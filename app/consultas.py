"""Consultas de solo lectura.

Sin efectos, sin escrituras y sin saber que existe HTTP: cada funcion
recibe una conexion ya abierta y devuelve datos.
"""


def plato_disponible(db, plato_id):
    """Garantiza: True solo si el plato tiene receta y todos sus
    ingredientes estan disponibles en este instante; nunca lee una
    columna de disponibilidad de plato, porque no existe."""
    fila = db.execute(
        """
        SELECT 1
          FROM plato p
         WHERE p.id = ?
           AND EXISTS (
                 SELECT 1 FROM plato_ingrediente pi WHERE pi.plato_id = p.id
               )
           AND NOT EXISTS (
                 SELECT 1
                   FROM plato_ingrediente pi
                   JOIN ingrediente i ON i.id = pi.ingrediente_id
                  WHERE pi.plato_id = p.id AND i.disponible = 0
               )
        """,
        (plato_id,),
    ).fetchone()
    return fila is not None


def cola_cocina(db):
    """Garantiza: los items PENDIENTE o EN_PREPARACION, agrupados por
    pedido y ordenados estrictamente por antiguedad del item; un pedido
    anulado nunca aparece, porque un pedido con todos sus items en
    CANCELADO no puede tener ninguno en estos dos estados."""
    filas = db.execute(
        """
        SELECT ip.id, ip.pedido_id, ip.estado, ip.creado_en, ip.nota,
               pl.nombre AS plato_nombre
          FROM item_pedido ip
          JOIN plato pl ON pl.id = ip.plato_id
         WHERE ip.estado IN ('PENDIENTE', 'EN_PREPARACION')
         ORDER BY ip.creado_en
        """
    ).fetchall()

    items_por_pedido = {}
    orden_pedidos = []
    for fila in filas:
        pedido_id = fila["pedido_id"]
        if pedido_id not in items_por_pedido:
            items_por_pedido[pedido_id] = []
            orden_pedidos.append(pedido_id)
        items_por_pedido[pedido_id].append(fila)

    return [
        {"pedido_id": pedido_id, "items": items_por_pedido[pedido_id]}
        for pedido_id in orden_pedidos
    ]


def items_listos_de_mesero(db, mesero_id):
    """Garantiza: los items en LISTO de los pedidos que le pertenecen a
    este mesero, del mas antiguo al mas reciente en pasar a LISTO."""
    return db.execute(
        """
        SELECT ip.id, ip.pedido_id, ip.estado, ip.listo_en, ip.nota,
               pl.nombre AS plato_nombre, p.mesa_id
          FROM item_pedido ip
          JOIN pedido p ON p.id = ip.pedido_id
          JOIN plato pl ON pl.id = ip.plato_id
         WHERE p.mesero_id = ? AND ip.estado = 'LISTO'
         ORDER BY ip.listo_en
        """,
        (mesero_id,),
    ).fetchall()


def estado_pedido(db, pedido_id):
    """Garantiza: COMPLETO, ANULADO o EN_CURSO, calculado a partir de los
    estados de sus items en este instante; la tabla pedido no tiene ni
    necesita una columna de estado."""
    filas = db.execute(
        "SELECT estado FROM item_pedido WHERE pedido_id = ?", (pedido_id,)
    ).fetchall()
    estados = {fila["estado"] for fila in filas}

    if estados <= {"CANCELADO"}:
        return "ANULADO"
    if estados <= {"LISTO", "CANCELADO"}:
        return "COMPLETO"
    return "EN_CURSO"
