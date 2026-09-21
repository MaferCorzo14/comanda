# AGENTS.md

Contexto e instrucciones para agentes de IA que trabajen en este repositorio.
Los ADR mandan sobre este archivo; este archivo manda sobre cualquier costumbre general.

## Regla de oro

**Toda regla de negocio se valida en el servidor, dentro de una transacción de base de datos. La interfaz nunca decide.**

Comprobable así: cualquier operación prohibida por las reglas debe ser rechazada aunque se envíe directamente por HTTP, sin pasar por la interfaz. Si ocultar un botón es lo único que impide una operación inválida, la regla no está implementada.

## Qué es este sistema

Gestión de pedidos y cola de cocina para un restaurante con una sola cocina central.
Sustituye la comanda en papel: la cocina sabe qué preparar primero y el mesero sabe qué está listo.

Alcance: persistencia, interfaz web para operar, reglas del negocio predominante y la consulta de la cola.
Fuera de alcance: autenticación avanzada, pagos reales, despliegue en producción, integraciones externas, impuestos y descuentos.

## Roles

| Rol | Qué hace |
|---|---|
| Administrador | Gestiona platos (nombre, precio) y la disponibilidad de ingredientes (sí/no). Atiende los reportes de faltantes |
| Cocina | Define la receta de cada plato. Ve la cola. Inicia, termina o cancela ítems pendientes. Reporta faltantes |
| Mesero | Registra pedidos para una mesa y queda asignado a ese pedido. Ve los ítems listos. Marca entregado. Cancela ítems pendientes a petición del cliente |
| Caja | Registra pagos parciales de la cuenta de una mesa |

No hay autenticación: el rol se selecciona en la interfaz.

## Estados de un ítem

```
PENDIENTE -> EN_PREPARACION -> LISTO -> ENTREGADO
PENDIENTE -> CANCELADO
```

- CANCELADO es terminal. No existe transición de salida.
- Ninguna transición puede saltarse un paso ni retroceder.
- Cocina hace PENDIENTE -> EN_PREPARACION -> LISTO y puede cancelar ítems PENDIENTE.
- Mesero hace LISTO -> ENTREGADO y puede cancelar ítems PENDIENTE.

## Invariantes (las cuatro reglas del negocio predominante)

1. **Cada ítem avanza por sus propios estados.** El estado del pedido se calcula a partir de sus ítems, comprobado en este orden: *anulado* cuando todos están en CANCELADO; *entregado* cuando todos están en ENTREGADO o CANCELADO; *completo* cuando todos están en LISTO, ENTREGADO o CANCELADO; *en curso* en cualquier otro caso.
2. **Un plato sin ingredientes disponibles no se puede pedir y deja de ofrecerse.** Un plato se ofrece solo si tiene receta registrada y todos sus ingredientes están disponibles.
3. **Un ítem se puede cancelar solo si la cocina no lo empezó**, es decir, solo desde PENDIENTE. Cualquier otro intento se rechaza con error.
4. **La cuenta de una mesa admite varios pagos parciales.** La suma de los pagos, sin contar propina, nunca puede superar el total.

## Dueño único de cada concepto derivado

Cada uno de estos valores se calcula en **un solo lugar** y no se guarda duplicado en ninguna tabla.

| Concepto | Se deriva de |
|---|---|
| Estado del pedido | Los estados de sus ítems |
| Disponibilidad de un plato | Su receta y la disponibilidad de sus ingredientes |
| Total de la cuenta | Suma de los precios congelados de los ítems no cancelados de la ronda abierta de la mesa (ver A-23) |
| Saldo pendiente | Total menos la suma de los pagos de esa misma ronda |
| Antigüedad en la cola | Fecha de creación del ítem |
| Precio cobrado | El precio congelado en el ítem de pedido, nunca el precio actual del plato |

## Consultas obligatorias

- **Cola de cocina:** ítems en PENDIENTE y EN_PREPARACION, agrupados por pedido, ordenados **estrictamente** por antigüedad. Excluye pedidos anulados. Refresco cada pocos segundos.
- **Vista del mesero:** ítems en LISTO de los pedidos asignados a ese mesero.

## Reglas que el agente no debe romper

- No introducir un estado nuevo para salir de EN_PREPARACION. Si falta un ingrediente, la cancelación ocurre antes de iniciar.
- No guardar en columnas los valores derivados de la tabla anterior.
- No borrar pedidos ni ítems. Un pedido con todos los ítems cancelados se excluye de la cola y de la cuenta, pero permanece en la base de datos.
- No agregar ítems a un pedido ya creado. Una ronda o una alternativa es un pedido nuevo.
- No aceptar pagos si quedan ítems no cancelados sin entregar en la mesa.
- No inventar firmas de API ni de librerías. Verificar contra la documentación oficial antes de escribir.
- Registrar la marca de tiempo de cada transición de estado.
- La restricción `CHECK (NOT (estado = 'CANCELADO' AND iniciado_en IS NOT NULL))`
  de `item_pedido` no se elimina ni se relaja. Si una operación la activa, el
  error está en el código que intentó cancelar un ítem ya iniciado, no en la
  restricción. Corregir la operación, nunca el esquema.
- Al pasar un ítem a `EN_PREPARACION`, escribir `iniciado_en` en la misma
  sentencia UPDATE que el cambio de estado.
- No construir más de lo que pide la tarea. Si una tarea depende de algo
  de otra fase, decirlo y esperar, en vez de implementarlo por cuenta propia.
  El plan por fases existe para que cada entrega se revise completa.

## Stack

- Python 3 con Flask y plantillas Jinja2. Vistas renderizadas en el servidor, una por rol.
- SQLite con el módulo `sqlite3` de la librería estándar. Modo WAL.
- SQL escrito a mano. No usar ORM.
- Sin dependencias de frontend: nada de Node, npm ni frameworks de JavaScript.

Ver ADR-002 y ADR-003.

### Base de datos
 
- El archivo vive en `instance/comanda.sqlite`, la carpeta que Flask reserva
  para lo que depende del despliegue y no va a control de versiones.
  `create_app()` la crea con `os.makedirs(app.instance_path, exist_ok=True)`:
  Flask no la crea sola.
 
- **No agregar `PRAGMA busy_timeout`.** El parámetro `timeout` de
  `sqlite3.connect` ya es el tiempo de espera por bloqueo y vale cinco
  segundos por omisión. Un `BEGIN IMMEDIATE` que choca con otro escritor
  ya espera y reintenta; el pragma sería redundante. Verificado en la
  documentación oficial del módulo `sqlite3`.
 
- La conexión se abre con `isolation_level=None`, o sea en autocommit puro:
  ninguna sentencia abre transacción por su cuenta. No cambiar esto por el
  comportamiento implícito del módulo, que solo abre transacción antes de
  INSERT, UPDATE, DELETE o REPLACE y deja los SELECT sin proteger.
 
- Una operación de varias sentencias se abre con `BEGIN IMMEDIATE`, no con
  `BEGIN` a secas. `BEGIN` empieza como transacción de lectura y solo toma
  el candado de escritura al llegar la primera escritura, lo cual deja un
  hueco entre leer el saldo y registrar el pago.
 
- `init-db` crea, no reinicia. Si la base ya existe, el comando falla en vez
  de sobrescribirla. No agregar `DROP TABLE IF EXISTS` al esquema: reiniciar
  es una acción explícita, documentada en el README.

 
## Marcas de tiempo
 
### Fechas y horas
 
- Se guardan en UTC, en formato ISO 8601, con
  `strftime('%Y-%m-%dT%H:%M:%fZ', 'now')`.
 
- **No agregar `%S` a ese formato.** En SQLite, `%f` significa "fractional
  seconds: SS.SSS", o sea que ya incluye los segundos. Escribir `%S.%f`
  los duplicaría.
 
- El formato es fijo y con ceros delante a propósito: así ordenar como texto
  equivale a ordenar cronológicamente, que es de lo que depende el
  `ORDER BY creado_en` de la cola.
 
- Al mostrar una hora en una plantilla, convertirla a la zona local. La base
  guarda UTC y Colombia está en UTC−5: mostrar el valor crudo haría que la
  cocina viera horas que no coinciden con el reloj.


### Cómo se escriben las transiciones de estado

Siempre como una sola sentencia condicionada al estado previo, nunca leyendo y
luego escribiendo:

    UPDATE item_pedido SET estado = 'CANCELADO'
     WHERE id = ? AND estado = 'PENDIENTE';

Si afecta cero filas, la operación se rechaza. El módulo `sqlite3` no abre
transacción antes de un SELECT, así que leer y después escribir deja una
carrera abierta.

## Convenciones

- Idioma del código y los identificadores: nombres de dominio en español (plato, pedido, item_pedido, mesa, mesero, ingrediente), el resto del código en inglés.
- Mensajes de commit: explican **qué se decidió**, no qué archivo se tocó.
- Todo supuesto nuevo que el agente tenga que resolver por su cuenta se anota en `ASSUMPTIONS.md` en el mismo cambio.