"""Registro de blueprints y filtros de plantilla del flujo principal."""

from datetime import datetime, timedelta, timezone

from . import administrador, cocina, mesero, principal

# Colombia no observa horario de verano: UTC-5 fijo todo el anio, asi que
# no hace falta una base de datos de zonas horarias (evita depender de
# zoneinfo/tzdata, que en Windows no siempre trae los datos instalados).
_COLOMBIA = timezone(timedelta(hours=-5))


def _parsear_utc(valor):
    return datetime.strptime(valor, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def hora_local(valor):
    """Convierte una marca de tiempo UTC guardada en la base a hora de Colombia, para mostrarla."""
    return _parsear_utc(valor).astimezone(_COLOMBIA).strftime("%d/%m %H:%M")


def hace(valor):
    """Convierte una marca de tiempo UTC guardada en la base en un texto de tiempo transcurrido hasta ahora."""
    minutos = int((datetime.now(timezone.utc) - _parsear_utc(valor)).total_seconds() // 60)
    if minutos < 1:
        return "hace instantes"
    if minutos < 60:
        return f"hace {minutos} min"
    horas, minutos = divmod(minutos, 60)
    return f"hace {horas} h {minutos} min"


def init_app(app):
    """Conecta las rutas con la aplicacion: registra los blueprints del
    flujo principal y los filtros de plantilla para mostrar horas en
    hora local en vez de UTC."""
    app.register_blueprint(principal.bp)
    app.register_blueprint(cocina.bp)
    app.register_blueprint(mesero.bp)
    app.register_blueprint(administrador.bp)
    app.jinja_env.filters["hora_local"] = hora_local
    app.jinja_env.filters["hace"] = hace
