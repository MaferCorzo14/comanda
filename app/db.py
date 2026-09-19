"""Conexion a la base de datos SQLite.

Solo configuracion de la conexion: ninguna regla de negocio vive aqui.
"""

import sqlite3
from contextlib import contextmanager

import click
from flask import current_app, g


def get_db():
    """Devuelve la conexion de esta peticion, abriendola si hace falta.

    Una conexion por peticion, no una global compartida: `check_same_thread`
    vale True por omision en el modulo sqlite3, asi que una conexion no se
    puede reusar desde un hilo distinto al que la creo (ver ADR-003). `g`
    vive solo durante la peticion actual, asi que guardar la conexion ahi
    hace que cada peticion tenga la suya.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            # None pone la conexion en autocommit puro: ninguna sentencia
            # abre transaccion por su cuenta. El modo por omision del
            # modulo solo abre transaccion antes de INSERT/UPDATE/DELETE/
            # REPLACE y deja un SELECT sin proteger (ver ADR-003), asi que
            # se apaga ese comportamiento implicito en vez de confiar en
            # el para las operaciones que necesitan varias sentencias.
            isolation_level=None,
        )
        # Filas accesibles por nombre de columna (fila["estado"]) en vez
        # de por posicion (fila[2]), para que el codigo que las lee sea
        # legible.
        g.db.row_factory = sqlite3.Row

        # SQLite trae las claves foraneas desactivadas por omision y el
        # ajuste es por conexion: sin esto, las FOREIGN KEY de esquema.sql
        # quedan escritas pero sin efecto. Va antes de cualquier
        # transaccion porque este pragma no tiene efecto dentro de una.
        g.db.execute("PRAGMA foreign_keys = ON")

        # El modo WAL queda grabado en el archivo la primera vez que se
        # activa, pero se pide en cada conexion para que una base creada
        # o copiada sin haberlo activado antes tambien quede en WAL.
        g.db.execute("PRAGMA journal_mode = WAL")

    return g.db


def close_db(e=None):
    """Cierra la conexion de esta peticion, si se llego a abrir.

    Registrada con `teardown_appcontext`, Flask la llama al final de cada
    peticion (incluso si hubo una excepcion, recibida en `e`), para que
    ninguna conexion quede abierta mas alla de su peticion.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


@contextmanager
def transaccion(db):
    """Abre una transaccion explicita para operaciones de varias sentencias.

    Con `isolation_level=None` ninguna sentencia abre transaccion por su
    cuenta (ver `get_db`), asi que una operacion como registrar un pago
    -leer el total y el saldo, y solo entonces insertar el pago- necesita
    un BEGIN explicito para que las dos sentencias se ejecuten como una
    unidad. Se usa BEGIN IMMEDIATE en vez de BEGIN a secas para tomar el
    candado de escritura desde la lectura inicial: con BEGIN a secas, otra
    conexion podria registrar un pago entre nuestra lectura del saldo y
    nuestra escritura, y la suma de pagos terminaria superando el total.
    """
    db.execute("BEGIN IMMEDIATE")
    try:
        yield db
    except BaseException:
        db.rollback()
        raise
    else:
        db.commit()


def init_db():
    """Crea las tablas y carga los datos semilla en la base configurada."""
    db = get_db()
    with current_app.open_resource("esquema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    with current_app.open_resource("semilla.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Comando `flask init-db`: crea la base desde cero con sus datos semilla."""
    init_db()
    click.echo("Base de datos inicializada.")


def init_app(app):
    """Conecta este modulo con la aplicacion Flask.

    Se llama una vez desde la fabrica de la aplicacion (`create_app`),
    todavia no escrita, para registrar el cierre de conexion al final de
    cada peticion y el comando `flask init-db`.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
