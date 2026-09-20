"""Fabrica de la aplicacion Flask."""

import os

from flask import Flask

from . import db, rutas


def create_app():
    # instance_relative_config=True hace que app.instance_path apunte a
    # una carpeta instance/ pensada para archivos que dependen del
    # despliegue y no van a control de versiones, como la base sqlite.
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "comanda.sqlite"),
        # flash() firma la cookie de sesion con esta clave; sin ella
        # lanza un error. No hay despliegue en el alcance del proyecto
        # (ADR-002), asi que un valor fijo de desarrollo basta.
        SECRET_KEY="dev",
    )

    # Flask no crea instance/ por su cuenta, y sin ella el comando de
    # inicializacion falla al intentar abrir el archivo de la base ahi.
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    rutas.init_app(app)

    return app
