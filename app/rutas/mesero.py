"""Vista de mesero: sus pedidos, los items listos, crear un pedido y
marcar un item entregado.

Esta ruta no decide nada: llama a reglas.py o consultas.py y elige que
mostrar. Si la operacion se rechaza, atiende la excepcion con un mensaje,
nunca con un error 500.
"""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .. import consultas, reglas
from ..db import get_db

bp = Blueprint("mesero", __name__, url_prefix="/mesero")


@bp.route("/<int:mesero_id>")
def panel(mesero_id):
    db = get_db()
    mesero = consultas.mesero_por_id(db, mesero_id)
    if mesero is None:
        abort(404)
    return render_template(
        "mesero/panel.html",
        mesero_id=mesero_id,
        mesero_nombre=mesero["nombre"],
        pedidos=consultas.pedidos_de_mesero(db, mesero_id),
        listos=consultas.items_listos_de_mesero(db, mesero_id),
        pendientes=consultas.items_pendientes_de_mesero(db, mesero_id),
    )


@bp.route("/<int:mesero_id>/pedidos/nuevo")
def formulario_pedido(mesero_id):
    db = get_db()
    return render_template(
        "mesero/nuevo_pedido.html",
        mesero_id=mesero_id,
        mesas=consultas.mesas(db),
        # Solo platos disponibles (regla 2): con receta y todos sus
        # ingredientes en existencia ahora mismo.
        platos=consultas.platos_disponibles(db),
    )


@bp.route("/<int:mesero_id>/pedidos", methods=["POST"])
def crear_pedido(mesero_id):
    db = get_db()
    mesa_id = request.form.get("mesa_id", type=int)

    # El formulario manda una cantidad por plato disponible, no una lista
    # de identificadores marcados; esta traduccion es interpretacion de
    # la entrada del formulario, asi que va aqui y no en reglas.py, que
    # sigue sin enterarse de que existen cantidades.
    platos_ids = []
    for plato in consultas.platos_disponibles(db):
        cantidad = request.form.get(f"cantidad_{plato['id']}", type=int) or 0
        if not (0 <= cantidad <= 20):
            flash("Cada plato admite entre 0 y 20 unidades.", "error")
            return redirect(url_for("mesero.formulario_pedido", mesero_id=mesero_id))
        platos_ids.extend([plato["id"]] * cantidad)

    if len(platos_ids) > 50:
        flash("Un pedido admite hasta 50 items en total.", "error")
        return redirect(url_for("mesero.formulario_pedido", mesero_id=mesero_id))

    # Que falte la mesa o que todas las cantidades queden en cero es un
    # formulario incompleto, no una regla de negocio: se corta aqui, sin
    # llamar a reglas.crear_pedido.
    if mesa_id is None or not platos_ids:
        flash("Elige una mesa y al menos un plato.", "error")
        return redirect(url_for("mesero.formulario_pedido", mesero_id=mesero_id))

    try:
        reglas.crear_pedido(db, mesa_id=mesa_id, mesero_id=mesero_id, platos_ids=platos_ids)
    except reglas.PlatoNoDisponible as e:
        flash(str(e), "error")
        return redirect(url_for("mesero.formulario_pedido", mesero_id=mesero_id))

    return redirect(url_for("mesero.panel", mesero_id=mesero_id))


@bp.route("/<int:mesero_id>/items/<int:item_id>/entregado", methods=["POST"])
def entregar(mesero_id, item_id):
    db = get_db()
    try:
        reglas.marcar_entregado(db, item_id)
    except reglas.TransicionInvalida as e:
        flash(str(e), "error")
    return redirect(url_for("mesero.panel", mesero_id=mesero_id))


@bp.route("/<int:mesero_id>/items/<int:item_id>/cancelar", methods=["POST"])
def cancelar(mesero_id, item_id):
    db = get_db()
    try:
        reglas.cancelar_item(db, item_id)
    except reglas.TransicionInvalida as e:
        flash(str(e), "error")
    return redirect(url_for("mesero.panel", mesero_id=mesero_id))
