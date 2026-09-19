# BITACORA-IA.md

Una entrada por sesión de trabajo con la IA: qué se pidió, qué propuso, qué se aceptó o rechazó y por qué, y qué quedó sin verificar.

---

## Sesión 1 — 16 de septiembre de 2026

**Herramienta:** Claude (chat en el navegador).

**Qué le pedí.**
Contextualizar el proyecto sin escribir código ni archivos: entender y aterrizar el propósito. Le di el enunciado del Sistema E, las cuatro reglas de negocio, la consulta obligatoria y la restricción de alcance. Le puse como condición que preguntara todo lo que hiciera falta hasta que no quedara ambigüedad, y que no avanzara al estado del arte sin mi confirmación.

**Qué propuso.**
Una batería larga de preguntas agrupadas por bloques: roles y tareas, estados del ítem y del pedido, ingredientes y disponibilidad, cancelación, cuenta y pagos parciales, la consulta de la cola, y datos e interfaz. Junto con las preguntas, señaló los huecos del enunciado y propuso una tabla inicial de criterios de éxito con medida y umbral.

**Los huecos que identificó.**
- Qué significa "pedido completo" cuando hay ítems cancelados. Sin decidirlo, un pedido con una cancelación no podría cerrarse nunca.
- La relación entre mesa y pedido: la regla 1 habla de pedido y la regla 4 de mesa, y la cuenta es por mesa.
- Qué pasa con los ítems ya pedidos cuando un ingrediente se agota, ya que la regla 2 impide pedir pero no dice nada de lo pedido.
- Las carreras de concurrencia: cancelar mientras la cocina inicia, y dos pagos simultáneos sobre la misma cuenta.
- Que las reglas deben garantizarse en la persistencia y no solo en la interfaz.

**Qué quedó sin verificar al cierre de la sesión.**
Todas las respuestas a esas preguntas. La sesión terminó con el cuestionario planteado, sin decisiones tomadas.

---

## Sesión 2 — 17 de septiembre de 2026

**Herramienta:** Claude (chat en el navegador).

**Qué le pedí.**
Responder el cuestionario de la sesión anterior, cerrar las ambigüedades que quedaran y producir la primera evidencia de los entregables: README.md, AGENTS.md, ASSUMPTIONS.md y esta bitácora. A mitad de la sesión le compartí el documento oficial de la prueba técnica, que hasta ese momento no tenía.

**Qué acepté.**
- Ingredientes como booleano en vez de inventario con cantidades (A-02).
- Un ítem por unidad, para poder cumplir la regla 1 tal como está escrita (A-08).
- Que el estado del pedido, la disponibilidad del plato y el saldo de la cuenta se calculen y no se guarden, cada uno con un único lugar donde se deriva.
- Que un pedido con todos sus ítems cancelados no se borre, en contra de mi idea inicial de eliminarlo del registro: sin eso se pierde la trazabilidad de las cancelaciones y de los tiempos (A-07).
- La regla de oro del proyecto: las reglas se validan en el servidor dentro de una transacción, y la interfaz nunca decide.

**Qué rechacé.**
- El menú por código QR para que el cliente pidiera directamente. Exigía identificar mesas sin autenticación y asignar meseros automáticamente, dos subsistemas que ninguna regla del enunciado pide y que no caben en el plazo (A-28).
- Agregar un estado de salida para ítems que ya están en preparación. Contradecía la regla 3 (A-13).
- Reordenar la cola de cocina por tiempo estimado de preparación. La idea fue mía, pero la consulta obligatoria pide antigüedad estricta; quedó registrada como mejora no implementada (A-26).
- Una tabla de idempotencia general. Las transiciones ya son idempotentes si se aplican con una actualización condicionada al estado previo, y el doble envío de un pago se cubre con una clave de unicidad. La tabla completa era infraestructura sin relación con las cuatro reglas.

**Dónde me corrigió y le di la razón.**
Propuse definir los criterios de éxito al final, según lo que alcanzara a construir. Señaló que así se terminan eligiendo los criterios que salieron bien, lo cual justifica en vez de medir. Quedaron fijados desde ahora, separados en obligatorios y deseables, para reportar al cierre los no cumplidos con su motivo.

También me corrigió dos imprecisiones de modelado: que la receta no es una entidad sino la relación muchos a muchos entre plato e ingrediente, y que volcar toda la conversación en el AGENTS.md sería un error, porque ese archivo es la instrucción para el agente y el razonamiento va en los supuestos y en los ADR.

**Qué quedó sin verificar.**
- El stack. Hay una recomendación preliminar (Go con librería estándar, SQLite y plantillas del servidor) pero las alternativas y sus contras no están documentadas todavía: son ADR-002 y ADR-003.
- La versión de Go instalada y las firmas concretas del enrutador de `net/http`, del driver de SQLite y de `embed`. Se verificarán contra la documentación oficial antes de escribir código, no de memoria.
- La afirmación de que SQLite serializa las escrituras y con eso resuelve la carrera entre cancelar e iniciar un ítem. Es del agente y debo comprobarla con una prueba.
- La elección de herramienta de IA para construir y su vía de respaldo: ADR-001.

---

## Sesión 3 — 18 de septiembre de 2026

**Herramienta:** Claude Code (construcción), chat de Claude (revisión y decisiones).

**Qué le pedí.** Escribir `app/esquema.sql` y `app/semilla.sql`, sin código Python todavía. El prompt completo está en `prompts/02-esquema.md`. Le di las garantías que el esquema debía cumplir, no el DDL: qué debía ser imposible, qué columnas no debían existir y qué consultas tenía que soportar con eficiencia.

**Qué propuso.** Un esquema completo con las entidades acordadas, restricciones `CHECK` sobre los estados, el precio congelado en `item_pedido`, una columna de marca de tiempo por transición y un índice parcial para la cola de cocina.

**Qué revisé.**

*Disponibilidad como `INTEGER`.* Habíamos acordado que la disponibilidad de un ingrediente era booleana, y el agente la declaró como `INTEGER`. Lo cuestioné pensando que era un error. Al verificar en la documentación oficial de SQLite resultó que el agente tenía razón: SQLite no tiene tipo booleano y los valores booleanos se guardan como enteros 0 y 1. Las palabras `TRUE` y `FALSE` se aceptan desde la versión 3.23.0, pero son solo otra forma de escribir 1 y 0. Acepté la declaración y añadí la comprobación de que llevara `CHECK (disponible IN (0, 1))`, para que no pueda guardarse cualquier otro entero.

*Para qué sirven las marcas de tiempo.* Pregunté si `iniciado_en`, `listo_en` y `cancelado_en` eran necesarias, dado que la columna `estado` ya tiene un `CHECK` con los valores válidos. La respuesta cambió el diseño: `estado` guarda solo el presente y se sobrescribe en cada transición, así que las marcas de tiempo son el único registro de por dónde pasó el ítem. De ahí salieron dos cosas: la cola necesita `creado_en` para ordenar por antigüedad, y `iniciado_en` permite detectar un ítem cancelado que ya había sido iniciado.

*Restricción añadida a partir de esa revisión.* Pedí agregar `CHECK (NOT (estado = 'CANCELADO' AND iniciado_en IS NOT NULL))`. Esto convierte parte de la regla 3 en una garantía del esquema: un ítem cancelado que tenga fecha de inicio es justamente lo que la regla prohíbe, y ahora esa fila no se puede guardar. No reemplaza la validación en la aplicación, que sigue haciéndose con el `UPDATE` condicionado al estado previo; es la red de seguridad por si ese código falla. Su límite: depende de que `iniciado_en` se escriba en la misma sentencia que el cambio a `EN_PREPARACION`, y eso quedó como regla en `AGENTS.md`.

*El índice parcial y su condición de uso.* El agente creó el índice de la cola sobre `creado_en` filtrando por los dos estados activos. Al revisarlo confirmé en la documentación oficial que SQLite solo usa un índice parcial cuando la condición de la consulta implica la del índice, y que su comprobación es limitada. En la práctica, la consulta debe repetir literalmente `estado IN ('PENDIENTE', 'EN_PREPARACION')`: escribirla de otra forma equivalente haría que la base de datos recorriera toda la tabla. Lo anoté como regla en `AGENTS.md`.

**Qué actualicé en `AGENTS.md`.** Tres líneas nuevas, todas nacidas de esta revisión:

- No eliminar ni relajar la restricción de cancelación. Si una operación la activa, el error está en el código.
- Al pasar un ítem a `EN_PREPARACION`, escribir `iniciado_en` en la misma sentencia `UPDATE`.
- La consulta de la cola filtra con `estado IN ('PENDIENTE', 'EN_PREPARACION')` de forma literal, porque es la condición del índice parcial.

**Qué quedó sin verificar.** El esquema está revisado, pero **no ejecutado**. Al cierre de esta sesión no he comprobado que:

- La base de datos se cree sin errores desde `esquema.sql` y `semilla.sql`.
- Las claves foráneas rechacen de verdad una fila huérfana, lo cual depende de activar `PRAGMA foreign_keys` en cada conexión.
- El `CHECK` de cancelación bloquee realmente la combinación prohibida.
- La consulta de la cola use el índice parcial, que se comprueba con `EXPLAIN QUERY PLAN`.

Las cuatro son el criterio de aceptación de la fase F1 y se verifican al escribir `app/db.py`.

