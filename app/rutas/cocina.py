"""Vista de cocina: la cola, iniciar un item, marcarlo listo.

Esta ruta no decide nada: llama a reglas.py o consultas.py y elige que
mostrar. Si la operacion se rechaza, atiende la excepcion con un mensaje,
nunca con un error 500.
"""

from flask import Blueprint, flash, redirect, render_template, url_for

from .. import consultas, reglas
from ..db import get_db

bp = Blueprint("cocina", __name__, url_prefix="/cocina")


@bp.route("/")
def cola():
    db = get_db()
    return render_template("cocina/cola.html", grupos=consultas.cola_cocina(db))


@bp.route("/items/<int:item_id>/iniciar", methods=["POST"])
def iniciar(item_id):
    db = get_db()
    try:
        reglas.iniciar_item(db, item_id)
    except reglas.TransicionInvalida as e:
        flash(str(e), "error")
    return redirect(url_for("cocina.cola"))


@bp.route("/items/<int:item_id>/listo", methods=["POST"])
def listo(item_id):
    db = get_db()
    try:
        reglas.marcar_listo(db, item_id)
    except reglas.TransicionInvalida as e:
        flash(str(e), "error")
    return redirect(url_for("cocina.cola"))


@bp.route("/items/<int:item_id>/cancelar", methods=["POST"])
def cancelar(item_id):
    db = get_db()
    try:
        reglas.cancelar_item(db, item_id)
    except reglas.TransicionInvalida as e:
        flash(str(e), "error")
    return redirect(url_for("cocina.cola"))
