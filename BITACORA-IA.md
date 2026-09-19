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

## Sesión 4 — 19 de septiembre de 2026

**Herramienta:** Claude Code (construcción), chat de Claude (revisión y decisiones).

Sesión dedicada a cerrar la fase F1: conexión a la base de datos, fábrica de la aplicación y verificación de que las garantías del esquema funcionan de verdad. En el camino se decidió y documentó la arquitectura.

---

### Conexión a la base de datos

**Qué le pedí.** Escribir `app/db.py`, solo ese archivo, sin rutas ni lógica de negocio. El prompt completo está en `prompts/db.md`. Las exigencias fueron seis: conexión por petición y no global, `PRAGMA foreign_keys = ON` en cada conexión, modo WAL, filas accesibles por nombre de columna, un comando que cree la base desde `esquema.sql` y `semilla.sql`, y una forma explícita de abrir transacción para operaciones de varias sentencias.

Cada una responde a un comportamiento por omisión que habría roto una garantía del esquema: SQLite trae las claves foráneas apagadas y el ajuste es por conexión; el módulo `sqlite3` impide usar una conexión desde otro hilo; y el módulo solo abre transacción implícita antes de INSERT, UPDATE, DELETE o REPLACE, nunca antes de un SELECT.

**Qué propuso.** Cumplió los seis puntos, y tomó por su cuenta dos decisiones que no estaban en mi instrucción:

*`isolation_level=None`.* En vez de convivir con el comportamiento implícito de transacciones del módulo, lo apaga del todo: ninguna sentencia abre transacción por su cuenta, y donde hace falta una se abre a mano. La acepté porque es más predecible que depender de cuándo el módulo decide abrirla.

*`BEGIN IMMEDIATE` en lugar de `BEGIN`.* Con `BEGIN` a secas SQLite empieza como transacción de lectura y solo toma el candado de escritura al llegar la primera escritura, lo cual deja un hueco entre leer el saldo de una cuenta y registrar el pago. `IMMEDIATE` toma el candado desde el principio. Es el detalle más fino del archivo y lo acepté por esa razón.

**Qué corregí.** Un comentario de `create_app()` afirmaba que `instance_relative_config=True` *hace que `app.instance_path` apunte a una carpeta `instance/`*. Según la documentación de Flask eso no es exacto: `instance_path` apunta ahí de todas formas, y lo que el parámetro cambia es que las rutas relativas al cargar archivos de configuración se resuelvan contra esa carpeta. Como la configuración se pasa con `from_mapping` y una ruta absoluta, el parámetro no está haciendo nada funcional. El código está bien; el comentario explicaba mal el motivo.

---

### Decisión de arquitectura

**Qué planteé.** Propuse revisar si convenía una arquitectura orientada a eventos con procesamiento asíncrono, en vez de la organización en capas que veníamos usando sin haberla documentado. La intuición venía del dominio: una cola de cocina se parece a una cola de mensajes.

**Qué salió de la discusión.** Primero, que estaba mezclando dos decisiones distintas: cómo se organiza el código por dentro, que son las capas, y cómo se procesan las operaciones, que es la parte síncrona o asíncrona. No son alternativas entre sí.

Segundo, y decisivo: el procesamiento asíncrono **debilitaría** la garantía principal del sistema en lugar de reforzarla. Entre publicar un evento y procesarlo pasa tiempo, y en ese intervalo el estado puede cambiar. Si un mesero publica "cancelar ítem" y un instante después la cocina publica "iniciar ítem", el resultado dependería del orden de procesamiento, y corregir esa inconsistencia exigiría transacciones compensatorias. Con procesamiento síncrono el problema no existe: una sola sentencia condicionada al estado previo lo resuelve.

Tercero, un argumento de operación: el mesero que cancela necesita saber en ese momento si procedió, porque tiene que decirle algo al cliente. Un "solicitud recibida" no sirve.

**Qué decidí.** Capas con procesamiento síncrono, documentado en `ADR-004` con el modelo orientado a eventos como alternativa descartada. `docs/PLAN.md` quedó remitiendo a ese ADR, y se añadieron diagramas en Mermaid: capas y ciclo de vida del ítem en el ADR-004, y el recorrido entre roles en la fase F2.

**Lo que sí se conserva del modelo de eventos.** El diseño ya incorpora la parte útil sin la infraestructura: cada transición es un evento con nombre dentro de una máquina de estados explícita, las marcas de tiempo por transición son el registro de esos eventos, y la cola de cocina es una cola real consultada por antigüedad. Lo que no se adopta es el procesamiento diferido.

---

### Fábrica de la aplicación

**Qué le pedí.** `app/__init__.py` con `create_app()` y `requirements.txt`, nada más. El prompt está en `prompts/create-app.md`.

**Las dos dudas que me dejó de la tarea anterior, y cómo las resolví.**

*¿Dónde vive el archivo de la base?* En `instance/`, al mismo nivel que el paquete `app/`, no dentro de él. La documentación de Flask define esa carpeta como el lugar para archivos que no van bajo control de versiones y dependen del despliegue, que es exactamente el caso. Añadí que `create_app()` debe crearla con `os.makedirs(..., exist_ok=True)`, porque Flask no la crea sola y sin ella `init-db` falla.

*¿Conviene agregar `PRAGMA busy_timeout`?* **No, y la premisa de la propuesta era incorrecta.** El agente argumentaba que un `BEGIN IMMEDIATE` que choca con otro escritor fallaría de inmediato con "database is locked". Al verificar en la documentación oficial del módulo `sqlite3` resultó que el parámetro `timeout` de `connect` **es** el tiempo de espera por bloqueo y vale **cinco segundos por omisión**. O sea que el comportamiento que proponía agregar ya estaba activo. Rechacé la propuesta con la cita y lo dejé como regla en `AGENTS.md`, para que no vuelva a proponerse en otra sesión.

Este caso es el más instructivo de la sesión: el agente no propuso algo incorrecto por descuido, sino porque desconocía un valor por omisión. Aceptarlo habría añadido configuración redundante que después habría que explicar.

**Lo que ninguno de los dos vio al principio.** El agente nombró el archivo `comanda.sqlite`, pero el `.gitignore` solo cubría `*.db`, `*.db-wal` y `*.db-shm`. La extensión `.sqlite` no coincidía con ninguna regla, así que la base se habría subido al repositorio. Se agregaron `instance/` y las variantes de `.sqlite`.

---

### Verificación de la fase F1

Ejecutadas desde `flask shell`, con la base creada por `flask init-db`:

| Comprobación | Resultado |
|---|---|
| `flask init-db` crea la base en `instance/` | Correcto |
| `PRAGMA foreign_keys` devuelve 1 | Correcto |
| `PRAGMA journal_mode` devuelve `wal` | Correcto |
| Insertar un ítem con `pedido_id` inexistente lanza `IntegrityError` | Correcto |
| El `CHECK` de cancelación rechaza un ítem cancelado con `iniciado_en` | Correcto |
| `EXPLAIN QUERY PLAN` sobre la cola usa el índice parcial | Correcto |
| Los datos semilla salen en orden de antigüedad | Correcto |

La cuarta es la que de verdad cierra el criterio: que el pragma esté puesto y que las claves foráneas rechacen son cosas distintas, y solo el insert fallido demuestra la segunda.

**Sobre el archivo `.db-wal`.** El agente señaló, correctamente, que ese archivo solo existe mientras hay una conexión abierta: al cerrarse la última, SQLite hace un punto de control y lo elimina. La prueba permanente de que el modo quedó activo es que `PRAGMA journal_mode` devuelva `wal`, no que el archivo esté en disco.

---

### Decisión sobre reinicializar la base

`flask init-db` ejecutado dos veces falla con `table mesa already exists`, porque `init_db()` no borra nada antes.

El agente recomendó documentarlo en el README en vez de añadir `DROP TABLE IF EXISTS`, argumentando el riesgo de borrar datos reales por accidente.

**Acepté la conclusión pero no ese argumento.** En este proyecto no hay datos reales que proteger: la base se genera desde `semilla.sql`, el despliegue está fuera de alcance y el archivo no va al repositorio. La razón válida es otra: el comando falla de forma ruidosa y con un mensaje claro, y un comando que no puede destruir nada por accidente es preferible a uno que sí. Reiniciar queda como una acción deliberada y separada.

Quedó como supuesto A-34 y documentado en el README con el comando de reinicio.

---

### Ejecución del proyecto

El README quedó con los pasos verificados desde cero:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run
```

Y el reinicio de la base como paso aparte, borrando `instance/comanda.sqlite` antes de volver a inicializar.

---

### Estado al cierre

**La fase F1 queda cerrada.** La base de datos existe, se crea con un comando, y sus garantías están verificadas y no solo revisadas.

**Lo siguiente es F2**, el flujo principal: `reglas.py` con las transiciones de estado, `consultas.py` con la cola de cocina y la vista del mesero, y las rutas y plantillas por rol. Es la fase que decide el proyecto, porque sin un recorrido completo de punta a punta no hay sistema que mostrar.

**Qué queda sin verificar.** Nada de F1. De lo que viene, todo.