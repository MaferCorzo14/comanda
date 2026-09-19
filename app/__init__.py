"""Fabrica de la aplicacion Flask.

Sin rutas, sin plantillas, sin logica de negocio: solo la construccion y
configuracion de la app.
"""

import os

from flask import Flask

from . import db


def create_app():
    # instance_relative_config=True hace que app.instance_path apunte a
    # una carpeta instance/ pensada para archivos que dependen del
    # despliegue y no van a control de versiones, como la base sqlite.
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "comanda.sqlite"),
    )

    # Flask no crea instance/ por su cuenta, y sin ella el comando de
    # inicializacion falla al intentar abrir el archivo de la base ahi.
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    return app
