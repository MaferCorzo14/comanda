# Prompt para Claude Code — esquema de datos

Copia todo lo que está entre las dos líneas de guiones.

---

Lee primero `AGENTS.md` y `ASSUMPTIONS.md`. Son la fuente de verdad de este proyecto; si algo de lo que te pido aquí los contradice, detente y dímelo en vez de elegir por tu cuenta.

**Tarea:** escribe `app/esquema.sql` y `app/semilla.sql`. No escribas código Python todavía, ni rutas, ni plantillas.

**Entidades:** mesa, pedido, ítem de pedido, plato, estado de preparación, mesero, ingrediente, la relación entre plato e ingrediente, pago y reporte de faltante.

**Lo que el esquema debe garantizar por sí solo**, sin depender de código de aplicación:

1. Un ítem solo puede tener uno de los estados válidos del ciclo definido en AGENTS.md. Cualquier otro valor debe ser rechazado por la base de datos.
2. Un ítem no puede existir sin su pedido, ni un pedido sin su mesa, ni un pago sin su mesa.
3. Cada ítem conserva el precio con el que fue pedido, independiente de cambios posteriores en el plato.
4. Cada transición de estado deja registrada su marca de tiempo.
5. Un pago no puede tener monto cero ni negativo. La propina, si existe, se guarda aparte del monto.
6. Un mismo ingrediente no puede aparecer dos veces en la receta del mismo plato.

**Lo que el esquema NO debe tener.** Estos valores se calculan con una consulta, así que no existe columna para ellos y no hay forma de escribir un valor que contradiga a los datos:

- Estado del pedido.
- Disponibilidad de un plato.
- Total de la cuenta de una mesa.
- Saldo pendiente de una mesa.

Si crees que alguno de estos debería guardarse, no lo agregues: dímelo y explica por qué.

**Consultas que el esquema debe soportar con eficiencia:**

- La cola de cocina: ítems pendientes y en preparación, agrupados por pedido, ordenados estrictamente por antigüedad del ítem.
- Los ítems listos de los pedidos de un mesero.
- El total y el saldo de la cuenta de una mesa.

Agrega los índices que hagan falta para eso, y explica en un comentario qué consulta justifica cada índice. No agregues índices que ninguna consulta use.

**Convenciones:**

- Nombres de tablas y columnas en español, en minúsculas y con guion bajo.
- Los montos se guardan como enteros, en pesos sin decimales. No uses coma flotante para dinero.
- Las marcas de tiempo en formato ISO 8601 y en UTC.
- Comenta cada tabla con una línea que diga qué representa en el negocio.

**Sobre las claves foráneas:** escríbelas en el esquema, pero ten presente que SQLite no las aplica salvo que la conexión ejecute `PRAGMA foreign_keys = ON`. Deja un comentario en el archivo recordándolo. La activación se hará después en `db.py`; no la implementes ahora.

**`semilla.sql`:** datos mínimos para poder probar el sistema y ver la cola funcionando. Al menos dos mesas, dos meseros, seis platos, los ingredientes necesarios y un caso donde un ingrediente esté agotado para que su plato deje de ofrecerse.

**Al terminar**, antes de que yo revise, explícame en pocas líneas:

- Qué restricción implementa cada una de las cuatro reglas de negocio, y cuál de ellas no se puede expresar en el esquema y necesitará lógica en la aplicación.
- Qué decisiones tomaste que no estaban especificadas aquí.
- Qué dudas te quedaron.
