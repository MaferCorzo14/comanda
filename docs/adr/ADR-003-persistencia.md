# ADR-003. Persistencia y control de concurrencia

**Estado:** aceptada
**Fecha:** 18 de septiembre de 2026

## Contexto

El sistema reemplaza la comanda en papel, así que el estado de pedidos, ítems y pagos tiene que sobrevivir a un reinicio. Además debe poder levantarse desde cero en otra máquina sin instalar ni configurar servicios adicionales.

Las reglas de negocio se validan en el servidor, dentro de una transacción. Dos de ellas pueden romperse por concurrencia, y esa es la restricción que decide esta elección:

- **Cancelación.** Si un mesero cancela un ítem en el mismo instante en que la cocina lo inicia, solo una de las dos operaciones puede prosperar.
- **Pagos.** Si dos pagos se registran a la vez sobre la misma cuenta, la suma no puede superar el total.

La carga esperada es la de un restaurante con una cocina y unos pocos meseros: muchas lecturas, porque la cola se consulta con recarga periódica, y pocas escrituras.

## Decisión

**SQLite, accedido con el módulo `sqlite3` de la librería estándar de Python, con SQL escrito a mano y sin ORM.** La base de datos se abre en modo WAL.

Las transiciones de estado se aplican como **una sola sentencia condicionada al estado previo**, no como una lectura seguida de una escritura:

```sql
UPDATE item_pedido
   SET estado = 'CANCELADO', cancelado_en = ?
 WHERE id = ? AND estado = 'PENDIENTE';
```

Si la sentencia afecta cero filas, la operación se rechaza porque alguien cambió el estado antes. Esto hace la operación idempotente y elimina el intervalo entre comprobar y actuar, que es donde se cuela la carrera.

## Alternativas descartadas

**PostgreSQL.** Es lo esperable en un sistema en producción y aporta tipos y control de concurrencia más ricos. Se descartó porque exige instalar un servidor, crear usuario, contraseña y base de datos, y repetir todo eso en cada máquina donde se ejecute el sistema. Para la carga real de un restaurante no aporta nada que SQLite no cubra. La decisión se revertiría si el sistema tuviera que atender varias sedes o varios servidores de aplicación a la vez.

**MySQL o MariaDB.** Mismos costos de instalación y configuración que PostgreSQL, sin ventaja adicional para este caso.

**SQLAlchemy u otro ORM.** Reduciría la cantidad de SQL escrito a mano. Se descartó porque oculta precisamente la parte más delicada del sistema: la consulta de la cola de cocina, con su orden y su agrupación, es el corazón del problema que se está resolviendo, y conviene tenerla a la vista y poder ajustarla. Además, el comportamiento de un ORM frente a transacciones y sesiones es una capa más de reglas propias que aprender.

**Archivos JSON o CSV.** Descartado de entrada: sin transacciones no hay forma de garantizar las reglas de cancelación y de pagos.

## Consecuencias

**A favor:**
- `sqlite3` forma parte de la librería estándar de Python, así que no hay driver que instalar ni configurar.
- La base de datos es un archivo: se copia, se respalda y se reinicia sin herramientas externas.
- En modo WAL, los lectores no bloquean al escritor ni el escritor a los lectores, lo cual encaja con una cola que se consulta constantemente mientras se registran pedidos.

**En contra, y asumido:**
- SQLite admite **un solo escritor a la vez**: las escrituras se serializan. Para esta carga es irrelevante, y de hecho simplifica las garantías de concurrencia.
- El modo WAL requiere que todos los procesos estén en la misma máquina, porque se apoya en memoria compartida y no funciona sobre sistemas de archivos en red.
- Sin ORM hay más SQL que escribir y revisar.

**Hallazgo verificado sobre transacciones.** Según la documentación oficial del módulo `sqlite3`, en su comportamiento por omisión (`LEGACY_TRANSACTION_CONTROL` con `isolation_level` en `DEFERRED`) la transacción se abre implícitamente **solo antes de un INSERT, UPDATE, DELETE o REPLACE**. Un `SELECT` queda fuera. Por eso un patrón de leer el estado y después escribirlo **no queda protegido por omisión**, y de ahí viene la decisión de usar una única sentencia condicionada. Donde una operación necesite varias sentencias, como registrar un pago comprobando el saldo, la transacción se abre de forma explícita en lugar de confiar en el comportamiento implícito.

**Nota sobre hilos.** El parámetro `check_same_thread` del módulo vale `True` por omisión, de modo que una conexión no puede usarse desde un hilo distinto al que la creó. La aplicación abre una conexión por petición en lugar de compartir una global.

## Referencias

- [Módulo `sqlite3` de Python, documentación oficial](https://docs.python.org/3/library/sqlite3.html)
- [SQLite, Write-Ahead Logging](https://www.sqlite.org/wal.html)