"""Pagina inicial: enlaces a la cocina y a cada mesero."""

from flask import Blueprint, render_template

from .. import consultas
from ..db import get_db

bp = Blueprint("principal", __name__)


@bp.route("/")
def index():
    db = get_db()
    return render_template("principal.html", meseros=consultas.meseros(db))
