"""Vista de caja: la cuenta de cada mesa y el registro de pagos
parciales (regla 4).

Esta ruta no decide nada: llama a reglas.py o consultas.py y elige que
mostrar. Si la operacion se rechaza, atiende la excepcion con un
mensaje, nunca con un error 500.
"""

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .. import consultas, reglas
from ..db import get_db

bp = Blueprint("caja", __name__, url_prefix="/caja")


@bp.route("/")
def mesas():
    db = get_db()
    return render_template("caja/mesas.html", mesas=consultas.mesas_con_cuenta(db))


@bp.route("/mesas/<int:mesa_id>")
def detalle(mesa_id):
    db = get_db()
    mesa = consultas.mesa_por_id(db, mesa_id)
    if mesa is None:
        abort(404)

    cuenta = consultas.cuenta_mesa(db, mesa_id)
    return render_template(
        "caja/detalle.html",
        mesa=mesa,
        items=cuenta["items"],
        pagos=cuenta["pagos"],
        total=cuenta["total"],
        pagado=cuenta["pagado"],
        saldo=cuenta["saldo"],
    )


@bp.route("/mesas/<int:mesa_id>/pagos", methods=["POST"])
def registrar_pago(mesa_id):
    db = get_db()
    if consultas.mesa_por_id(db, mesa_id) is None:
        abort(404)

    monto = request.form.get("monto", type=int)
    propina = request.form.get("propina", type=int) or 0
    medio = request.form.get("medio")
    pagador = request.form.get("pagador") or None

    # Que falte el monto o el medio es un formulario incompleto, no una
    # regla de negocio: se corta aqui, sin llamar a reglas.registrar_pago.
    if monto is None or not medio:
        flash("Ingresa un monto y un medio de pago validos.", "error")
        return redirect(url_for("caja.detalle", mesa_id=mesa_id))

    try:
        reglas.registrar_pago(
            db, mesa_id=mesa_id, monto=monto, medio=medio, propina=propina, pagador=pagador
        )
    except reglas.PagoInvalido as e:
        flash(str(e), "error")

    return redirect(url_for("caja.detalle", mesa_id=mesa_id))
