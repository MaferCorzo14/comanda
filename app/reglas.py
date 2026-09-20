"""Reglas de negocio: las operaciones que cambian el estado del sistema.

Cada funcion recibe una conexion ya abierta y valores ya extraidos; no
sabe que existe HTTP, y una operacion rechazada se anuncia lanzando una
excepcion de dominio, nunca con un codigo de estado.
"""

from .db import transaccion


class ErrorDeRegla(Exception):
    """Raiz comun de todo rechazo de una regla de negocio."""


class TransicionInvalida(ErrorDeRegla):
    """El item no estaba en el estado previo que la transicion exige."""


def crear_pedido(db, mesa_id, mesero_id, platos_ids):
    """Garantiza: crea el pedido y un item por cada plato pedido, con el
    precio de ese momento ya congelado.

    Nota: en F2 no valida disponibilidad del plato. Esa comprobación es la
    regla 2 y entra en F3, dentro de esta misma transacción."""
    with transaccion(db) as tx:
        pedido_id = tx.execute(
            "INSERT INTO pedido (mesa_id, mesero_id) VALUES (?, ?)",
            (mesa_id, mesero_id),
        ).lastrowid

        for plato_id in platos_ids:
            precio = tx.execute(
                "SELECT precio FROM plato WHERE id = ?", (plato_id,)
            ).fetchone()["precio"]
            tx.execute(
                """
                INSERT INTO item_pedido (pedido_id, plato_id, precio_congelado)
                VALUES (?, ?, ?)
                """,
                (pedido_id, plato_id, precio),
            )

    return pedido_id


def iniciar_item(db, item_id):
    """Garantiza: solo pasa a EN_PREPARACION un item que estaba PENDIENTE,
    y en la misma sentencia deja registrado iniciado_en."""
    cursor = db.execute(
        """
        UPDATE item_pedido
           SET estado = 'EN_PREPARACION',
               iniciado_en = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
         WHERE id = ? AND estado = 'PENDIENTE'
        """,
        (item_id,),
    )
    if cursor.rowcount == 0:
        raise TransicionInvalida(
            f"el item {item_id} no esta en PENDIENTE, no se puede iniciar"
        )


def marcar_listo(db, item_id):
    """Garantiza: solo pasa a LISTO un item que estaba EN_PREPARACION, y
    en la misma sentencia deja registrado listo_en."""
    cursor = db.execute(
        """
        UPDATE item_pedido
           SET estado = 'LISTO',
               listo_en = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
         WHERE id = ? AND estado = 'EN_PREPARACION'
        """,
        (item_id,),
    )
    if cursor.rowcount == 0:
        raise TransicionInvalida(
            f"el item {item_id} no esta en EN_PREPARACION, no se puede marcar listo"
        )


def marcar_entregado(db, item_id):
    """Garantiza: solo pasa a ENTREGADO un item que estaba LISTO, y en la
    misma sentencia deja registrado entregado_en."""
    cursor = db.execute(
        """
        UPDATE item_pedido
           SET estado = 'ENTREGADO',
               entregado_en = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
         WHERE id = ? AND estado = 'LISTO'
        """,
        (item_id,),
    )
    if cursor.rowcount == 0:
        raise TransicionInvalida(
            f"el item {item_id} no esta en LISTO, no se puede marcar entregado"
        )
