from flask import Flask
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
                id_ot,
                id_pqr,
                tipo_servicio,
                descripcion,
                direccion,
                prioridad,
                estado,
                id_tecnico
            FROM ordenes_trabajo
            ORDER BY id_ot DESC
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


if __name__ == "__main__":
    app.run()
