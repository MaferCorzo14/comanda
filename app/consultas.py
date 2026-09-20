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
               pl.nombre AS plato_nombre, m.nombre AS mesa_nombre
          FROM item_pedido ip
          JOIN plato pl ON pl.id = ip.plato_id
          JOIN pedido p ON p.id = ip.pedido_id
          JOIN mesa m ON m.id = p.mesa_id
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

    # La clave se llama "items_pedido" y no "items": en una plantilla,
    # grupo.items resolveria al metodo dict.items en vez de a la lista,
    # porque Jinja busca primero un atributo con ese nombre.
    return [
        {"pedido_id": pedido_id, "items_pedido": items_por_pedido[pedido_id]}
        for pedido_id in orden_pedidos
    ]


def items_listos_de_mesero(db, mesero_id):
    """Garantiza: los items en LISTO de los pedidos que le pertenecen a
    este mesero, del mas antiguo al mas reciente en pasar a LISTO."""
    return db.execute(
        """
        SELECT ip.id, ip.pedido_id, ip.estado, ip.listo_en, ip.nota,
               pl.nombre AS plato_nombre, m.nombre AS mesa_nombre
          FROM item_pedido ip
          JOIN pedido p ON p.id = ip.pedido_id
          JOIN plato pl ON pl.id = ip.plato_id
          JOIN mesa m ON m.id = p.mesa_id
         WHERE p.mesero_id = ? AND ip.estado = 'LISTO'
         ORDER BY ip.listo_en
        """,
        (mesero_id,),
    ).fetchall()


def mesas(db):
    """Garantiza: todas las mesas, para elegirlas en el formulario de pedido."""
    return db.execute("SELECT id, nombre FROM mesa ORDER BY id").fetchall()


def meseros(db):
    """Garantiza: todos los meseros, para los enlaces de la pagina inicial."""
    return db.execute("SELECT id, nombre FROM mesero ORDER BY id").fetchall()


def mesero_por_id(db, mesero_id):
    """Garantiza: los datos de un mesero, o None si ese id no existe."""
    return db.execute(
        "SELECT id, nombre FROM mesero WHERE id = ?", (mesero_id,)
    ).fetchone()


def platos(db):
    """Garantiza: todos los platos del menu. No filtra por disponibilidad:
    la regla 2 todavia no esta implementada (queda para F3)."""
    return db.execute("SELECT id, nombre, precio FROM plato ORDER BY nombre").fetchall()


def pedidos_de_mesero(db, mesero_id):
    """Garantiza: los pedidos de este mesero con su estado ya calculado,
    del mas reciente al mas antiguo."""
    filas = db.execute(
        """
        SELECT p.id, p.creado_en, m.nombre AS mesa_nombre
          FROM pedido p
          JOIN mesa m ON m.id = p.mesa_id
         WHERE p.mesero_id = ?
         ORDER BY p.creado_en DESC
        """,
        (mesero_id,),
    ).fetchall()
    return [
        {
            "id": fila["id"],
            "creado_en": fila["creado_en"],
            "mesa_nombre": fila["mesa_nombre"],
            "estado": estado_pedido(db, fila["id"]),
        }
        for fila in filas
    ]


def estado_pedido(db, pedido_id):
    """Garantiza: ANULADO, ENTREGADO, COMPLETO o EN_CURSO, calculado a
    partir de los estados de sus items en este instante y comprobado en
    ese orden (del mas especifico al mas general); la tabla pedido no
    tiene ni necesita una columna de estado."""
    filas = db.execute(
        "SELECT estado FROM item_pedido WHERE pedido_id = ?", (pedido_id,)
    ).fetchall()
    estados = {fila["estado"] for fila in filas}

    if estados <= {"CANCELADO"}:
        return "ANULADO"
    if estados <= {"ENTREGADO", "CANCELADO"}:
        return "ENTREGADO"
    if estados <= {"LISTO", "ENTREGADO", "CANCELADO"}:
        return "COMPLETO"
    return "EN_CURSO"
