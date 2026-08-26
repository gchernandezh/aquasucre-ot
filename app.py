from flask import Flask

app = Flask(__name__)


@app.route("/")
def inicio():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AquaSucre OT</title>
    </head>

    <body>
        <h1>AquaSucre</h1>
        <h2>Gestión de Órdenes de Trabajo</h2>

        <p>Plataforma para la gestión y seguimiento
        de órdenes de trabajo.</p>

        <hr>

        <h3>AquaSucre OT - Versión 1.0</h3>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
