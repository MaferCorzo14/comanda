# Reglas y consultas (F2, primera parte)

Lee `AGENTS.md`, `docs/PLAN.md`, `app/esquema.sql` y `app/db.py` antes de empezar.

**Tarea:** escribe `app/reglas.py` y `app/consultas.py`. Nada de rutas, plantillas ni HTML: estos dos módulos no deben saber que existe HTTP.

## `reglas.py` — operaciones que cambian estado

Cuatro operaciones, las del flujo principal:

- Crear un pedido para una mesa, a nombre de un mesero, con una lista de platos.
- Iniciar la preparación de un ítem.
- Marcar un ítem como listo.
- Marcar un ítem como entregado.

La cancelación no va en esta tarea: corresponde a la fase F3.

**Cómo se escribe cada transición.** Una sola sentencia `UPDATE` condicionada al estado previo, que escriba el nuevo estado y su marca de tiempo a la vez. Si afecta cero filas, la operación se rechaza: alguien cambió el estado antes. Nunca leer el estado y después escribirlo en otra sentencia.

**Crear un pedido necesita varias sentencias**, así que va dentro de una transacción explícita con el ayudante de `db.py`. El precio de cada ítem se congela en el momento de crearlo: el ítem guarda el precio que tenía el plato entonces, no una referencia al plato.

**Cómo se informa un rechazo.** Decide entre lanzar una excepción propia del dominio o devolver un resultado explícito, y aplica la misma forma en las cuatro operaciones. Explícame cuál elegiste y por qué. Lo que no quiero es que una operación rechazada pase inadvertida ni que el módulo devuelva códigos de estado HTTP.

## `consultas.py` — lecturas, sin efectos

Tres consultas:

**Cola de cocina.** Ítems en `PENDIENTE` o `EN_PREPARACION`, agrupados por pedido, ordenados estrictamente por antigüedad del ítem. Excluye los pedidos anulados. El filtro se escribe literalmente como `estado IN ('PENDIENTE', 'EN_PREPARACION')`, porque es la condición del índice parcial y SQLite no lo usaría con una forma equivalente distinta.

**Ítems listos de un mesero.** Los ítems en `LISTO` de los pedidos que le pertenecen, para que sepa qué llevar a la mesa.

**Estado de un pedido.** Calculado a partir de sus ítems, nunca leído de una columna: *completo* cuando todos están en `LISTO` o `CANCELADO`, *anulado* cuando todos están `CANCELADO`, y en curso en cualquier otro caso.

## Restricciones

- Solo librería estándar y Flask.
- SQL escrito a mano, sin ORM.
- Parámetros con marcadores de posición, nunca concatenando cadenas.
- Cada función lleva una línea que dice qué garantiza, no qué hace.

## Al terminar

Dime:

1. Qué decisiones tomaste que no estaban en esta instrucción.
2. Cómo probar cada operación desde `flask shell`, incluidos los casos que deben ser rechazados.
3. Qué dudas te quedaron.

---

## Cómo revisar lo que devuelva

| Revisar | Qué buscar |
|---|---|
| Transiciones | Cada una es **un solo** `UPDATE` con `WHERE ... AND estado = '<previo>'`. Si ves un `SELECT` seguido de un `UPDATE`, está mal |
| Marcas de tiempo | La fecha se escribe en la **misma** sentencia que el cambio de estado, no después |
| Rechazo | Se comprueba `rowcount` y cero filas produce un rechazo visible, no un silencio |
| Precio | Se congela al crear el ítem. Si alguna consulta saca el precio de `plato` para cobrar, está mal |
| Crear pedido | Va dentro de la transacción explícita de `db.py`, no suelto |
| Filtro de la cola | Dice literalmente `estado IN ('PENDIENTE', 'EN_PREPARACION')` |
| Estado del pedido | Se calcula en la consulta. Si aparece una columna `estado` en `pedido`, está mal |
| Capas | Ninguno de los dos archivos importa nada de Flask salvo lo necesario para la conexión. Sin `request`, sin `redirect`, sin códigos HTTP |
| Separación | `consultas.py` no tiene ningún `INSERT`, `UPDATE` ni `DELETE` |

La prueba que más importa hacer tú misma, en `flask shell`: **iniciar un ítem dos veces seguidas**. La primera debe funcionar y la segunda debe rechazarse. Si la segunda pasa en silencio, el `rowcount` no se está comprobando y la garantía no existe.