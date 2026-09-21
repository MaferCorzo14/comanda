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


def items_pendientes_de_mesero(db, mesero_id):
    """Garantiza: los items en PENDIENTE de los pedidos de este mesero,
    del mas antiguo al mas reciente, para que los pueda cancelar."""
    return db.execute(
        """
        SELECT ip.id, ip.pedido_id, ip.estado, ip.creado_en, ip.nota,
               pl.nombre AS plato_nombre, m.nombre AS mesa_nombre
          FROM item_pedido ip
          JOIN pedido p ON p.id = ip.pedido_id
          JOIN plato pl ON pl.id = ip.plato_id
          JOIN mesa m ON m.id = p.mesa_id
         WHERE p.mesero_id = ? AND ip.estado = 'PENDIENTE'
         ORDER BY ip.creado_en
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


def platos_disponibles(db):
    """Garantiza: solo los platos que se ofrecen ahora mismo: con receta
    registrada y todos sus ingredientes disponibles (regla 2). Es la
    misma condicion que plato_disponible, en una sola consulta para
    listar el menu en vez de comprobar plato por plato."""
    return db.execute(
        """
        SELECT p.id, p.nombre, p.precio
          FROM plato p
         WHERE EXISTS (
                 SELECT 1 FROM plato_ingrediente pi WHERE pi.plato_id = p.id
               )
           AND NOT EXISTS (
                 SELECT 1
                   FROM plato_ingrediente pi
                   JOIN ingrediente i ON i.id = pi.ingrediente_id
                  WHERE pi.plato_id = p.id AND i.disponible = 0
               )
         ORDER BY p.nombre
        """
    ).fetchall()


def platos_con_disponibilidad(db):
    """Garantiza: todos los platos del menu, cada uno con un indicador
    de si se esta ofreciendo ahora mismo, para que el administrador vea
    el efecto de marcar un ingrediente agotado."""
    return db.execute(
        """
        SELECT p.id, p.nombre, p.precio,
               CASE
                 WHEN EXISTS (SELECT 1 FROM plato_ingrediente pi WHERE pi.plato_id = p.id)
                  AND NOT EXISTS (
                        SELECT 1
                          FROM plato_ingrediente pi
                          JOIN ingrediente i ON i.id = pi.ingrediente_id
                         WHERE pi.plato_id = p.id AND i.disponible = 0
                      )
                 THEN 1 ELSE 0
               END AS disponible
          FROM plato p
         ORDER BY p.nombre
        """
    ).fetchall()


def ingredientes(db):
    """Garantiza: todos los ingredientes con su disponibilidad actual."""
    return db.execute(
        "SELECT id, nombre, disponible FROM ingrediente ORDER BY nombre"
    ).fetchall()


def ingrediente_por_id(db, ingrediente_id):
    """Garantiza: los datos de un ingrediente, o None si ese id no existe."""
    return db.execute(
        "SELECT id, nombre, disponible FROM ingrediente WHERE id = ?",
        (ingrediente_id,),
    ).fetchone()


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


def mesa_por_id(db, mesa_id):
    """Garantiza: los datos de una mesa, o None si ese id no existe."""
    return db.execute("SELECT id, nombre FROM mesa WHERE id = ?", (mesa_id,)).fetchone()


def _historia_completa_mesa(db, mesa_id):
    """Trae, cada uno por su lado, todos los items no cancelados y todos
    los pagos de la mesa desde que existe, ordenados por fecha. Uso
    interno de cuenta_mesa."""
    items = db.execute(
        """
        SELECT ip.id, ip.pedido_id, ip.estado, ip.precio_congelado, ip.creado_en,
               pl.nombre AS plato_nombre
          FROM item_pedido ip
          JOIN pedido p ON p.id = ip.pedido_id
          JOIN plato pl ON pl.id = ip.plato_id
         WHERE p.mesa_id = ? AND ip.estado != 'CANCELADO'
         ORDER BY ip.creado_en
        """,
        (mesa_id,),
    ).fetchall()
    pagos = db.execute(
        """
        SELECT id, monto, propina, medio, pagador, creado_en
          FROM pago
         WHERE mesa_id = ?
         ORDER BY creado_en
        """,
        (mesa_id,),
    ).fetchall()
    return items, pagos


def _inicio_ronda_actual(items, pagos):
    """Encuentra la marca de tiempo del pago mas reciente que dejo el
    saldo de la mesa exactamente en cero (A-23: la mesa se cierra ahi).
    Devuelve None si eso nunca ha pasado. Recorre items y pagos juntos,
    ordenados por fecha, acumulando el total y lo pagado; cada vez que un
    pago iguala esas dos sumas, ese es un cierre. El ultimo cierre
    encontrado es donde empieza la ronda que sigue abierta ahora."""
    eventos = [(fila["creado_en"], fila["precio_congelado"], 0) for fila in items]
    eventos += [(fila["creado_en"], 0, fila["monto"]) for fila in pagos]
    eventos.sort(key=lambda evento: evento[0])

    total_acumulado = 0
    pagado_acumulado = 0
    ultimo_cierre = None
    for creado_en, monto_item, monto_pago in eventos:
        total_acumulado += monto_item
        pagado_acumulado += monto_pago
        if monto_pago > 0 and total_acumulado == pagado_acumulado:
            ultimo_cierre = creado_en
    return ultimo_cierre


def cuenta_mesa(db, mesa_id):
    """Garantiza: los items cobrables, los pagos, el total, lo pagado y
    el saldo de la ronda que sigue abierta en esta mesa ahora mismo.

    Una ronda anterior que ya dejo el saldo en cero (A-23: la mesa se
    cierra ahi) no se cuenta: en cuanto un pedido nuevo llega a una mesa
    libre, sus items cobrables, su total y lo pagado empiezan otra vez
    en cero, sin que haya que guardar ninguna marca de cierre."""
    items, pagos = _historia_completa_mesa(db, mesa_id)
    inicio = _inicio_ronda_actual(items, pagos)

    items_ronda = [i for i in items if inicio is None or i["creado_en"] > inicio]
    pagos_ronda = [p for p in pagos if inicio is None or p["creado_en"] > inicio]

    total = sum(i["precio_congelado"] for i in items_ronda)
    pagado = sum(p["monto"] for p in pagos_ronda)

    return {
        "items": items_ronda,
        "pagos": pagos_ronda,
        "total": total,
        "pagado": pagado,
        "saldo": total - pagado,
    }


def saldo_mesa(db, mesa_id):
    """Garantiza: el saldo pendiente de la ronda abierta en esta mesa."""
    return cuenta_mesa(db, mesa_id)["saldo"]


def mesas_con_cuenta(db):
    """Garantiza: todas las mesas con el total, lo pagado y el saldo de
    su ronda abierta, para verlas de un vistazo."""
    resultado = []
    for fila in db.execute("SELECT id, nombre FROM mesa ORDER BY id").fetchall():
        cuenta = cuenta_mesa(db, fila["id"])
        resultado.append(
            {
                "id": fila["id"],
                "nombre": fila["nombre"],
                "total": cuenta["total"],
                "pagado": cuenta["pagado"],
                "saldo": cuenta["saldo"],
            }
        )
    return resultado


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
