from flask import Flask, request, redirect, url_for
import os
import psycopg2

app = Flask(__name__)


def obtener_conexion():
    return psycopg2.connect(os.environ["DATABASE_URL"])


@app.route("/")
def inicio():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # ==========================================
        # CONSULTAR ÓRDENES DE TRABAJO
        # ==========================================

        cursor.execute("""
            SELECT
                ot.id_ot,
                ot.id_pqr,
                ot.tipo_servicio,
                ot.descripcion,
                ot.direccion,
                ot.prioridad,
                ot.estado,
                t.nombre
            FROM ordenes_trabajo ot
            LEFT JOIN tecnicos t
                ON ot.id_tecnico = t.id_tecnico
            ORDER BY ot.id_ot DESC
        """)

        ordenes = cursor.fetchall()

        filas_ordenes = ""

        for ot in ordenes:
            tecnico = ot[7] if ot[7] is not None else "Sin asignar"
            estado = ot[6] if ot[6] is not None else "Sin estado"

            filas_ordenes += f"""
            <tr>
                <td>{ot[0]}</td>
                <td>{ot[1]}</td>
                <td>{ot[2]}</td>
                <td>{ot[3]}</td>
                <td>{ot[4]}</td>
                <td>{ot[5]}</td>
                <td>{estado}</td>
                <td>{tecnico}</td>
            </tr>
            """

        # ==========================================
        # CONSULTAR TÉCNICOS
        # ==========================================

        cursor.execute("""
            SELECT
                id_tecnico,
                nombre,
                telefono,
                especialidad,
                estado
            FROM tecnicos
            ORDER BY id_tecnico
        """)

        tecnicos = cursor.fetchall()

        filas_tecnicos = ""

        for tecnico in tecnicos:
            filas_tecnicos += f"""
            <tr>
                <td>{tecnico[0]}</td>
                <td>{tecnico[1]}</td>
                <td>{tecnico[2]}</td>
                <td>{tecnico[3]}</td>
                <td>{tecnico[4]}</td>
            </tr>
            """

        cursor.close()
        conexion.close()

        return f"""
        <!DOCTYPE html>

        <html lang="es">

        <head>
            <meta charset="UTF-8">
            <title>AquaSucre OT</title>
        </head>

        <body>

            <h1>AquaSucre</h1>

            <h2>Gestión de Órdenes de Trabajo</h2>

            <p>
                Plataforma para la gestión y seguimiento
                de órdenes de trabajo.
            </p>

            <hr>

            <h2>Órdenes de Trabajo</h2>

            <table border="1" cellpadding="8">

                <tr>
                    <th>OT</th>
                    <th>PQR</th>
                    <th>Servicio</th>
                    <th>Descripción</th>
                    <th>Dirección</th>
                    <th>Prioridad</th>
                    <th>Estado</th>
                    <th>Técnico</th>
                </tr>

                {filas_ordenes}

            </table>

            <br>
            <hr>

            <h2>Técnicos registrados</h2>

            <table border="1" cellpadding="8">

                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Teléfono</th>
                    <th>Especialidad</th>
                    <th>Estado</th>
                </tr>

                {filas_tecnicos}

            </table>

            <br>

            <strong>AquaSucre OT - Versión 1.2</strong>

        </body>

        </html>
        """

    except Exception as error:

        return f"""
        <h1>AquaSucre OT</h1>

        <h2>Error conectando con la base de datos</h2>

        <p>{error}</p>
 
        """


@app.route("/asignar/<int:id_ot>")
def asignar(id_ot):

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Consultar la OT seleccionada
        cursor.execute("""
            SELECT
                id_ot,
                id_pqr,
                tipo_servicio,
                descripcion,
                direccion,
                prioridad,
                estado
            FROM ordenes_trabajo
            WHERE id_ot = %s
        """, (id_ot,))

        ot = cursor.fetchone()

        # Consultar técnicos activos
        cursor.execute("""
            SELECT
                id_tecnico,
                nombre,
                especialidad
            FROM tecnicos
            WHERE UPPER(estado) = 'ACTIVO'
            ORDER BY nombre
        """)

        tecnicos = cursor.fetchall()

        cursor.close()
        conexion.close()

        if ot is None:
            return "<h2>Orden de trabajo no encontrada</h2>", 404

        opciones = ""

        for tecnico in tecnicos:
            opciones += f"""
                <option value="{tecnico[0]}">
                    {tecnico[1]} - {tecnico[2]}
                </option>
            """

        return f"""
        <!DOCTYPE html>

        <html lang="es">

        <head>
            <meta charset="UTF-8">
            <title>Asignar OT - AquaSucre</title>
        </head>

        <body>

            <h1>AquaSucre</h1>

            <h2>Asignar Orden de Trabajo</h2>

            <hr>

            <h3>OT #{ot[0]}</h3>

            <p><strong>PQR:</strong> {ot[1]}</p>

            <p><strong>Servicio:</strong> {ot[2]}</p>

            <p><strong>Descripción:</strong> {ot[3]}</p>

            <p><strong>Dirección:</strong> {ot[4]}</p>

            <p><strong>Prioridad:</strong> {ot[5]}</p>

            <p><strong>Estado:</strong> {ot[6]}</p>

            <hr>

            <h3>Seleccionar técnico</h3>

            <form method="POST"
                  action="/confirmar-asignacion/{ot[0]}">

                <select name="id_tecnico" required>

                    <option value="">
                        -- Seleccione un técnico --
                    </option>

                    {opciones}

                </select>

                <br><br>

                <button type="submit">
                    Confirmar asignación
                </button>

            </form>

            <br>

            <a href="/">
                Volver al Gestor de OT
            </a>

        </body>

        </html>
        """

    except Exception as error:

        return f"""
            <h2>Error consultando la orden de trabajo</h2>
            <p>{error}</p>
        """

@app.route("/confirmar-asignacion/<int:id_ot>", methods=["POST"])
def confirmar_asignacion(id_ot):

    conexion = None
    cursor = None

    try:
        id_tecnico = request.form.get("id_tecnico")

        if not id_tecnico:
            return "<h2>Debe seleccionar un técnico.</h2>", 400

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Verificar que el técnico exista y esté activo
        cursor.execute("""
            SELECT id_tecnico
            FROM tecnicos
            WHERE id_tecnico = %s
              AND UPPER(estado) = 'ACTIVO'
        """, (id_tecnico,))

        tecnico = cursor.fetchone()

        if tecnico is None:
            return "<h2>El técnico seleccionado no existe o no está activo.</h2>", 400

        # Asignar técnico a la orden de trabajo
        cursor.execute("""
            UPDATE ordenes_trabajo
            SET
                id_tecnico = %s,
                estado = 'ASIGNADA',
                fecha_asignacion = CURRENT_TIMESTAMP
            WHERE id_ot = %s
        """, (id_tecnico, id_ot))

        if cursor.rowcount == 0:
            conexion.rollback()
            return "<h2>Orden de trabajo no encontrada.</h2>", 404

        conexion.commit()

        return redirect(url_for("inicio"))

    except Exception as error:

        if conexion:
            conexion.rollback()

        return f"""
            <h1>AquaSucre OT</h1>
            <h2>Error realizando la asignación</h2>
            <p>{error}</p>
        """, 500

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()
            
if __name__ == "__main__":
    app.run()
