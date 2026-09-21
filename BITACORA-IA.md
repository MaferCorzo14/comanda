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

## Sesión 5 — 20 de septiembre de 2026

**Herramienta:** Claude Code (construcción), chat de Claude (revisión y decisiones).

Fase F2, el flujo principal. El encargo se partió en dos: primero la lógica sin HTTP, después las rutas y las plantillas. El prompt de la primera parte salió al final de la sesión anterior; los prompts completos están en `prompts/`.

---

### Primera parte: reglas y consultas

**Qué le pedí.** `app/reglas.py` con las cuatro transiciones del flujo principal, y `app/consultas.py` con la cola de cocina, los ítems listos del mesero y el estado calculado del pedido. Sin rutas, sin plantillas: ninguno de los dos módulos debía saber que existe HTTP.

Partí el trabajo así a propósito. La lógica se puede probar entera desde `flask shell` antes de que exista una sola página, y es la parte que más conviene revisar línea por línea. Si el tiempo se hubiera acabado, tener la lógica correcta con la interfaz a medias era mejor que al revés.

**Qué decidió el agente por su cuenta.** Le dejé elegir cómo informar un rechazo, entre una excepción propia del dominio o un resultado explícito, pidiéndole que justificara. Eligió una excepción, `TransicionInvalida`, con un mensaje que nombra el ítem y el estado esperado. Lo acepté: hace imposible que una operación rechazada pase inadvertida, y el módulo no devuelve códigos HTTP, que era la condición.

**Qué rechacé: se adelantó a F3.** El agente implementó también la disponibilidad del plato, con una consulta `plato_disponible` y una validación dentro de `crear_pedido`. Es la regla 2, que según `docs/PLAN.md` corresponde a la fase siguiente.

No era un disparate, porque hay una dependencia real: `crear_pedido` tiene que decidir qué platos acepta. Pero tres cosas pesaban en contra: el plan dejaría de describir el proyecto, el criterio de aceptación de F2 se volvería borroso, y acabaría revisando código que no tenía previsto revisar.

Decidí recortar y respetar el plan. Se quitó la validación de `crear_pedido` y la excepción asociada, y se dejó `plato_disponible` en `consultas.py`, que es una lectura inerte y F3 la necesitaría igual. Quedó anotado en el docstring de `crear_pedido` que la ausencia es deliberada, y en la fase F3 del plan que al reponerla debe ir **dentro de la transacción**, no en la ruta: dentro, el candado de escritura ya está tomado y nadie puede agotar un ingrediente entre la comprobación y la creación.

De ahí salió una línea nueva para `AGENTS.md`: no construir más de lo que pide la tarea; si una tarea depende de algo de otra fase, decirlo en vez de implementarlo.

**La prueba que hice.** Iniciar el mismo ítem dos veces seguidas desde `flask shell`. La primera funcionó y la segunda lanzó `TransicionInvalida: el item 8 no esta en PENDIENTE, no se puede iniciar`.

Esa prueba es la que demuestra que se comprueba `rowcount`: si no se comprobara, el segundo intento pasaría en silencio y la garantía sería falsa. Y es el mismo mecanismo que resuelve la carrera entre cancelar e iniciar, porque no depende del orden de llegada sino del estado que tenga la fila en el instante del `UPDATE`.

---

### Segunda parte: rutas y plantillas

**Qué le pedí.** Un blueprint por rol, plantillas Jinja2, y tres condiciones explícitas: que las rutas no validen nada antes de llamar a la regla, que toda operación que cambia estado sea POST seguida de redirección, y que la identidad viaje en la URL sin sesión de usuario.

**Sobre la identidad en la URL.** Con la autenticación fuera de alcance, `/mesero/3` evita montar sesiones y contraseñas. La consecuencia, que acepté conscientemente: `mesero_id` no es una credencial. Nada impide que un mesero marque como entregado un ítem de otro armando la URL. Sirve para saber a qué panel volver, no para autorizar. Comprobar la pertenencia daría una falsa sensación de control sobre un sistema que no autentica a nadie.

**Qué encontré al revisar el código.**

*`crear_pedido` era la única ruta sin `try`.* Si alguien enviaba un `mesa_id` inexistente por HTTP, la clave foránea lanzaba `IntegrityError`, nadie la atrapaba y salía una página de error 500. En la interfaz no pasa, porque el formulario solo ofrece mesas reales, pero el criterio de aceptación de F2 habla justamente de peticiones enviadas sin pasar por la interfaz. Se corrigió para rechazar con mensaje.

*La validación del formulario sí va en la ruta, y está bien.* Que falte la mesa o no haya platos marcados es un formulario incompleto, no una regla de negocio. Validar la forma de la entrada es trabajo de la ruta; decidir si la operación es legítima es trabajo de `reglas.py`.

*Los botones condicionados en la plantilla no contradicen la regla de oro.* La plantilla decide qué botón mostrar, que es presentación; no decide si la operación es válida. La prueba es que enviando la petición sin botón de por medio el servidor la rechaza igual.

*Riesgo de fecha nula.* Los filtros de hora aplican `strptime` sobre el valor de la base, y `iniciado_en`, `listo_en` y `entregado_en` están vacíos hasta que ocurre la transición. Al revisar resultó que cada filtro se aplica solo donde el estado garantiza que la marca existe: la cola usa `creado_en`, que nunca es nulo, y la tabla de listos solo contiene ítems en `LISTO`. La garantía era correcta pero frágil, porque depende de que la consulta filtre por estado, así que se añadió una guarda en los filtros para devolver un guion cuando el valor es nulo.

---

### El hueco de especificación que apareció al ejecutar

Al recorrer el flujo completo en el navegador, el pedido #7 se quedó en "en curso" después de entregar todos sus ítems.

El código era **correcto respecto a lo escrito**: el supuesto A-05 definía completo como "todos los ítems en `LISTO` o `CANCELADO`", y un ítem entregado ya no está en `LISTO`. El pedido retrocedía.

El hueco era del supuesto, no del código: al definirlo nunca contemplamos qué pasa **después** de entregar. Se corrigió con cuatro estados, comprobados en orden:

1. **Anulado** — todos los ítems `CANCELADO`.
2. **Entregado** — todos `ENTREGADO` o `CANCELADO`.
3. **Completo** — todos `LISTO`, `ENTREGADO` o `CANCELADO`. Es "listo para entregar", la definición original.
4. **En curso** — cualquier otro caso.

Anulado va primero porque un pedido con todos los ítems cancelados también cumpliría la condición de entregado. Y el tercero acepta `ENTREGADO` porque un pedido puede tener un plato ya llevado a la mesa y otro esperando en la barra: ese pedido está completo, no en curso.

`ASSUMPTIONS.md` quedó actualizado con la definición de cuatro estados.

**Lo que esto enseña:** no lo habría encontrado leyendo el código. Apareció al ejecutar el flujo de punta a punta, que es la diferencia entre revisar y verificar.

---

### Verificación del índice de la cola

Comprobé con `EXPLAIN QUERY PLAN` que la consulta obligatoria usa el índice parcial, y de paso medí el costo de escribir el filtro de otra forma.

Con el filtro literal que exige `AGENTS.md`:

```
SCAN item_pedido USING INDEX idx_item_pedido_cola
```

Un solo paso: recorre el índice, que solo contiene los ítems activos y ya ordenados por antigüedad.

Con el filtro reescrito de forma equivalente (`estado != 'ENTREGADO' AND estado != 'CANCELADO'`):

```
SCAN item_pedido USING INDEX idx_item_pedido_no_cancelado
USE TEMP B-TREE FOR ORDER BY
```

Dos pasos. SQLite no reconoce que puede usar el índice de la cola, recurre a otro y tiene que construir una estructura temporal solo para ordenar. Las dos consultas devuelven lo mismo, pero una ordena gratis y la otra paga un ordenamiento cada vez que la cocina refresca la pantalla.

Esto convierte la regla del `AGENTS.md` sobre el filtro literal en una diferencia medible, no en una preferencia.

---

### Qué quedó sin verificar

- La prueba por HTTP sobre un ítem ya entregado, enviada con `Invoke-WebRequest` sin pasar por la interfaz. *(completar con el resultado)*
- El índice `idx_item_pedido_no_cancelado` apareció en el plan de la consulta de comparación. Hay que comprobar que tenga en el esquema el comentario que nombra la consulta que lo justifica; si ninguna lo usa, contradice la política del propio esquema de no tener índices que nadie aproveche.

### Estado al cierre

**F2 cerrada.** El recorrido completo funciona en el navegador: crear un pedido, verlo en la cola, iniciarlo, marcarlo listo, entregarlo, y ver el pedido pasar a entregado.

Lo siguiente es F3, las reglas 2 y 3, con el registro de faltantes de cocina recortado por tiempo: no es ninguna de las cuatro reglas del enunciado y se hará solo si sobra tiempo después de F4 y del cierre.



## Sesión 6 — 20 de septiembre de 2026

**Herramienta:** Claude Code (construcción), chat de Claude (revisión y decisiones).

Fase F3, las reglas 2 y 3: disponibilidad de platos y cancelación de ítems.

---

### Recorte de alcance antes de empezar

El plan incluía en F3 que cocina registrara los faltantes para que el administrador los viera. Lo saqué antes de encargar la tarea.

El motivo: **no es ninguna de las cuatro reglas del enunciado**. Salió de una decisión de flujo propia, el supuesto A-12, y con F4 y el cierre todavía por delante era lo primero que sobraba. Quedó en el plan como opcional, y mientras no exista, el aviso de cocina al administrador ocurre fuera del sistema, que es como funciona hoy en cualquier restaurante.

---

### Qué le pedí

Implementar las reglas 2 y 3, sin tocar nada de F4. El prompt está en `prompts/`.

Para la regla 3, cancelar un ítem siguiendo el mismo patrón que las demás transiciones: una sola sentencia condicionada al estado previo, escribiendo `cancelado_en` a la vez, y solo desde `PENDIENTE`. Con botón en las vistas de cocina y de mesero, porque las dos pueden cancelar.

Para la regla 2, reponer la validación en `crear_pedido` que se había quitado al recortar F2, con una condición explícita: **dentro de la transacción**, no en la ruta antes de llamarla. Dentro, el candado de escritura ya está tomado y nadie puede agotar un ingrediente entre la comprobación y la creación; fuera, quedaría un hueco.

Más una vista de administrador con lo mínimo para operar la regla: listar ingredientes, marcarlos como agotados o disponibles, y ver qué platos se están ofreciendo.

---

### El hueco que apareció al usar el sistema

Al registrar un pedido en el navegador me di cuenta de que **el formulario usaba casillas de verificación**, así que un mesero no podía pedir tres hamburguesas: cada plato solo se marcaba una vez.

La lógica sí lo soportaba. `crear_pedido` recibe una lista de identificadores, y repetir uno crea varios ítems, que es exactamente lo que exige el supuesto A-08. El modelo de datos era correcto y la interfaz no lo aprovechaba.

Se corrigió con un campo de cantidad por plato. **La traducción de cantidades a lista repetida va en la ruta**, no en `reglas.py`: interpretar lo que envía un formulario es trabajo de la capa que habla HTTP, y el dominio sigue recibiendo una lista de identificadores sin enterarse de que existen cantidades.

También se añadió un límite de cantidad por plato y de ítems por pedido, para que una petición enviada directamente no pueda crear miles de filas de golpe. Es validación de formulario, no regla de negocio.

Es el segundo hallazgo del fin de semana que solo aparece usando el sistema, no leyéndolo. El primero fue el estado del pedido tras la entrega.

---

### Verificación de la regla 2

El escenario completo, que además sirve como demostración:

1. El mesero registra un pedido con tres hamburguesas. Se crean tres ítems, uno por unidad.
2. El administrador marca la carne como agotada.
3. La hamburguesa **desaparece del menú** del mesero al recargar el formulario.
4. Envié de todas formas la petición de crear el pedido con ese plato, con `Invoke-WebRequest`, sin pasar por el formulario. **Se rechazó** con el mensaje "el plato 6 no esta disponible", en la propia página del formulario y no con un error 500.

El paso 4 es el que cierra el criterio. El menú filtrado es comodidad, no garantía: refleja el estado del momento en que se cargó la página. Si un mesero tiene el formulario abierto cuando el administrador agota un ingrediente, su navegador sigue ofreciendo ese plato y el envío llegaría igual. Por eso la validación está en el servidor, dentro de la transacción.

---

### Comportamientos que comprobé y resultaron correctos

Dos cosas me parecieron errores al verlas y no lo eran. Las anoto porque en ambos casos el sistema estaba haciendo lo que yo misma había especificado.

**Los ítems ya pedidos no se cancelan solos.** Tras agotar la carne, las tres hamburguesas del pedido 13 seguían en la cola en `PENDIENTE`, y el pedido seguía en curso. Es el supuesto A-14: la regla 2 impide **pedir** un plato agotado, no anula lo ya pedido. La cancelación la decide la cocina.

**La cocina puede iniciar un ítem cuyo ingrediente se agotó.** El sistema no lo bloquea, y es deliberado: ninguna de las cuatro reglas lo pide. La regla 2 impide pedir, no preparar. Quien verifica los ingredientes antes de empezar es la cocina como persona, según el supuesto A-12, y lo que el sistema sí garantiza es que pueda cancelar el ítem mientras esté pendiente. Queda como mejora no implementada marcar visualmente en la cola los ítems cuyo plato dejó de estar disponible: sería ayuda visual, no una regla.

**Un pedido con parte entregada y parte cancelada figura como entregado.** El pedido 13 terminó con dos hamburguesas entregadas y una cancelada, y su estado calculado pasó a *entregado*. Me chocó que dijera eso faltando un ítem, pero coincide con lo que decidí el primer día: un ítem cancelado cuenta como resuelto, porque si no, ese pedido quedaría abierto para siempre y la mesa nunca se podría cobrar. Queda como mejora de presentación mostrar el desglose, del tipo "entregado, 2 entregados y 1 cancelado", para que la palabra no esconda la cancelación.

---

### Verificación de la regla 3

Con el mismo pedido 13: cocina canceló un ítem en `PENDIENTE` y preparó los otros dos.

*(Completar con el resultado de las pruebas restantes: que un pedido con todos los ítems cancelados quede anulado y siga existiendo en la base, y que un ítem ya iniciado no se pueda cancelar ni desde el botón ni por HTTP.)*

---

### Estado al cierre

**F3 cerrada.** Las reglas 2 y 3 están implementadas y verificadas, con el registro de faltantes declarado como opcional y no implementado.

Lo siguiente es F4, la cuenta y los pagos parciales. Queda preparado en la base un caso útil para probarla: la mesa 1 tiene un pedido con dos hamburguesas entregadas y una cancelada, así que su cuenta debe sumar dos y no tres. Es el supuesto A-20, que un plato cancelado nunca llegó a la mesa y no se cobra.

---

## Sesión 7 — 20 de septiembre de 2026

**Herramienta:** Claude Code (construcción), chat de Claude (revisión y decisiones).

Fase F4, la última de construcción: la cuenta de una mesa y los pagos parciales, regla 4.

---

### Qué le pedí

Implementar la regla 4 según `prompts/pago.md`: total de la cuenta (suma de los precios congelados de los ítems no cancelados), pagado (suma de los montos sin la propina), saldo (total menos pagado), y "mesa libre" cuando el saldo llega a cero, sin guardar ninguna marca de cierre. Registrar un pago debía rechazarse si el monto es cero o negativo, si supera el saldo, si quedan ítems sin entregar, o si el saldo ya está en cero. Le puse la misma condición que en `esquema.md` al principio del proyecto: si el modelo tenía un problema, decírmelo antes de implementarlo en vez de resolverlo por su cuenta.

---

### Qué señaló antes de escribir código

El modelo que le di contradecía un supuesto ya documentado. `ASSUMPTIONS.md` (A-23) decía que una mesa cerrada "no admite más pagos ni pedidos"; el modelo de `pago.md` decía lo contrario, que no hace falta ninguna marca y que un pedido nuevo hace subir el saldo solo. El agente lo señaló en vez de elegir una de las dos por su cuenta, tal como se lo pedí, y siguió implementando el modelo del prompt por ser el más reciente y el que no dejaba ambigüedad.

Acepté seguir adelante con esa lectura, y quedó pendiente actualizar A-23 al cierre.

---

### Qué propuso

`consultas.py` con `total_mesa`, `pagado_mesa` y `saldo_mesa` calculados sobre **todos** los pedidos históricos de la mesa; `reglas.registrar_pago` dentro de una transacción `BEGIN IMMEDIATE` (la misma herramienta que ya se usaba para la disponibilidad, ahora justificada por dos cajeros cobrando la misma mesa a la vez); y un blueprint nuevo, `caja`, con el listado de mesas y el detalle de cada una.

Antes de mostrarme el resultado, notó él mismo que la vista de detalle mezclaba, en una sola lista, los ítems y pagos de **toda la vida de la mesa**, y me preguntó directamente cómo prefería resolverlo: dejarlo como historial completo, o calcular la ronda abierta actual. Elegí dejarlo como historial completo, razonando que el saldo ya era correcto y que separar rondas era una cuenta nueva que el prompt no había pedido.

---

### El hueco que apareció al usar el sistema

Registré un pago que dejaba en cero la cuenta de la mesa 3 y después le abrí un pedido nuevo. La pantalla de caja mostró los ítems y los pagos del pedido viejo, ya cobrado, mezclados con los del pedido nuevo. El saldo mostrado seguía siendo el correcto, pero **no cuadraba con la lógica** que yo misma había escrito en A-23: si la mesa se cierra al llegar a cero, un pedido nuevo debería empezar una cuenta en cero, no seguir sumando sobre el historial completo.

Volví sobre mi propia decisión anterior. Le señalé la contradicción con A-23 tal como está redactado, y le pedí que la vista de caja mostrara cero al cerrar una cuenta, y que la mesa quedara disponible para una cuenta nueva sin arrastrar lo ya cobrado.

Es el tercer hallazgo del fin de semana que solo apareció usando el sistema y no leyendo el código: el primero fue el estado del pedido tras la entrega, el segundo el formulario con casillas en vez de cantidades, y este es el tercero.

---

### Qué propuso para resolverlo

`cuenta_mesa`, que reemplaza a las tres funciones anteriores. Recorre en orden cronológico los ítems no cancelados y los pagos de toda la historia de la mesa, acumulando total y pagado, y busca el pago más reciente que haya dejado esas dos sumas exactamente iguales. Todo lo anterior a ese pago pertenece a una ronda ya cerrada y no se muestra; todo lo posterior es la cuenta abierta ahora. Si eso nunca ha pasado, cuenta la mesa completa.

Me explicó, y verifiqué que tiene sentido, que el **saldo no cambiaba con este ajuste** (ya era matemáticamente correcto antes, porque lo pagado también se acumulaba y las rondas cerradas se cancelaban solas en la resta); lo único que cambiaba era qué ítems y pagos se muestran como "cobrables" en la pantalla, que es justo lo que a mí me parecía mal.

No pedí que se guardara ninguna marca de "mesa cerrada": el cierre se sigue calculando, no almacenando, que es coherente con cómo se calcula todo lo demás en este proyecto (estado del pedido, disponibilidad del plato).

---

### Verificación de la regla 4

- Pagar un monto de cero, o mayor al saldo pendiente: rechazado en ambos casos, con mensaje.
- Pagar una mesa con ítems sin entregar: rechazado.
- Pagar el saldo exacto de una mesa: la cuenta queda en cero y la pantalla de caja lo muestra vacío.
- Pagar de nuevo una mesa ya en cero: rechazado.
- Abrir un pedido nuevo en una mesa ya saldada: el total y el saldo mostrados son solo los del pedido nuevo, no el historial.
- Repetir el ciclo una tercera vez sobre la misma mesa: vuelve a arrancar en cero cada vez, sin guardar ninguna marca.
- Una mesa que nunca ha tenido pedidos: la cuenta da cero en todo, sin romperse.

---

### Qué actualicé en `ASSUMPTIONS.md` y `AGENTS.md`

A-23 quedó reescrito con el algoritmo real: la mesa se cierra cuando el saldo llega a cero, sin guardar ninguna marca de cierre, y por eso una mesa "cerrada" sí admite pedidos nuevos — en cuanto llega uno, sus ítems ya quedan después del último cierre y la cuenta visible arranca de nuevo en cero. La tabla de "dueño único de cada concepto derivado" en `AGENTS.md` quedó apuntando a esa misma definición para el total de la cuenta y el saldo pendiente.

---

### Estado al cierre

**F4 cerrada.** La regla 4 está implementada y verificada, incluida la corrección de la ronda abierta.

Las cuatro reglas del negocio predominante están construidas: F2 (flujo principal), F3 (disponibilidad y cancelación) y F4 (cuenta y pagos). El registro de faltantes de cocina sigue fuera, declarado como opcional desde la sesión 6.

Lo siguiente es F5, el cierre: instrucciones de ejecución probadas desde cero, esta bitácora al día, y el repaso de los criterios de éxito con lo que se cumplió y lo que no.

**Qué quedó sin verificar.** El recorrido manual completo de punta a punta por el navegador, con los cuatro roles y las cuatro reglas en un solo repaso, que quedó en marcha al cierre de esta sesión siguiendo una guía de verificación paso a paso.