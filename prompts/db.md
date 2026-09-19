# Conexión a la base de datos

Lee `AGENTS.md`, `ADR-003` y `app/esquema.sql` antes de empezar.

**Tarea:** escribe `app/db.py`. Solo ese archivo. No escribas rutas, ni plantillas, ni lógica de negocio todavía.

**Qué debe hacer:**

1. **Abrir una conexión por petición**, no una global compartida. El módulo `sqlite3` impide por omisión usar una conexión desde un hilo distinto al que la creó. Usa el patrón de Flask con `g` y `teardown_appcontext` para que la conexión se cierre al terminar cada petición.

2. **Activar las claves foráneas en cada conexión**, con `PRAGMA foreign_keys = ON`. SQLite las tiene desactivadas por omisión y el ajuste es por conexión, así que sin esto las `FOREIGN KEY` del esquema no se aplican. Ejecútalo inmediatamente después de conectar, antes de cualquier transacción, porque este pragma no tiene efecto dentro de una.

3. **Poner la base de datos en modo WAL** con `PRAGMA journal_mode = WAL`.

4. **Devolver filas accesibles por nombre de columna**, no por posición, para que el código sea legible.

5. **Una función de inicialización** que cree la base ejecutando `esquema.sql` y luego `semilla.sql`. Debe poder invocarse desde la línea de comandos, por ejemplo como un comando de Flask, para que el README pueda indicar un solo paso para preparar la base desde cero.

6. **Una forma explícita de abrir una transacción** para las operaciones que necesitan varias sentencias, como registrar un pago comprobando el saldo. No confíes en el comportamiento implícito del módulo: por omisión solo abre transacción antes de INSERT, UPDATE, DELETE o REPLACE, así que un SELECT seguido de un UPDATE quedaría sin proteger.

**Restricciones:**

- Solo librería estándar y Flask. No agregues dependencias.
- Nada de lógica de negocio en este archivo: aquí solo va la conexión y su configuración.
- Comenta cada pragma explicando por qué está, no qué hace.

**Al terminar**, dime cómo verificar desde la terminal que las claves foráneas quedaron activas y que la base está en modo WAL.

---

## Qué verificar antes de seguir

Esto es el hito: la base de datos existe y funciona.

1. **Crear la base desde cero** con el comando de inicialización. Debe generarse el archivo `.db` y aparecer también `.db-wal`, que es señal de que el modo WAL quedó activo.

2. **Comprobar los dos pragmas** abriendo la base con el cliente de SQLite:

   ```sql
   PRAGMA foreign_keys;   -- debe devolver 1
   PRAGMA journal_mode;   -- debe devolver wal
   ```

3. **Probar que las claves foráneas rechazan de verdad.** Insertar un ítem con un `pedido_id` que no existe: debe fallar. Si lo acepta, el pragma no se está aplicando.

4. **Probar la consulta de la cola** contra los datos semilla, y verificar con `EXPLAIN QUERY PLAN` que usa el índice parcial.
