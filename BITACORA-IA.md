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