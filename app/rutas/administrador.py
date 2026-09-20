"""Vista de administrador: disponibilidad de ingredientes y su efecto en
el menu (regla 2).

Esta ruta no decide nada: llama a reglas.py o consultas.py y elige que
mostrar.
"""

from flask import Blueprint, abort, redirect, render_template, url_for

from .. import consultas, reglas
from ..db import get_db

bp = Blueprint("administrador", __name__, url_prefix="/administrador")


@bp.route("/")
def panel():
    db = get_db()
    return render_template(
        "administrador/panel.html",
        ingredientes=consultas.ingredientes(db),
        platos=consultas.platos_con_disponibilidad(db),
    )


@bp.route("/ingredientes/<int:ingrediente_id>/disponible", methods=["POST"])
def marcar_disponible(ingrediente_id):
    db = get_db()
    if consultas.ingrediente_por_id(db, ingrediente_id) is None:
        abort(404)
    reglas.marcar_ingrediente_disponible(db, ingrediente_id)
    return redirect(url_for("administrador.panel"))


@bp.route("/ingredientes/<int:ingrediente_id>/agotado", methods=["POST"])
def marcar_agotado(ingrediente_id):
    db = get_db()
    if consultas.ingrediente_por_id(db, ingrediente_id) is None:
        abort(404)
    reglas.marcar_ingrediente_agotado(db, ingrediente_id)
    return redirect(url_for("administrador.panel"))
