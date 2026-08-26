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

        cursor.execute("""
            SELECT id_tecnico, nombre, telefono, especialidad, estado
            FROM tecnicos
            ORDER BY id_tecnico
        """)

        tecnicos = cursor.fetchall()

        cursor.close()
        conexion.close()

        filas = ""

        for tecnico in tecnicos:
            filas += f"""
            <tr>
                <td>{tecnico[0]}</td>
                <td>{tecnico[1]}</td>
                <td>{tecnico[2]}</td>
                <td>{tecnico[3]}</td>
                <td>{tecnico[4]}</td>
            </tr>
            """

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

            <h2>Técnicos registrados</h2>

            <table border="1" cellpadding="8">

                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Teléfono</th>
                    <th>Especialidad</th>
                    <th>Estado</th>
                </tr>

                {filas}

            </table>

            <br>

            <strong>AquaSucre OT - Versión 1.1</strong>

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
