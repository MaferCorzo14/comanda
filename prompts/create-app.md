# Fábrica de la aplicación
 
Lee `AGENTS.md` y `app/db.py` antes de empezar.
 
**Tarea:** escribe `app/__init__.py` con la fábrica `create_app()`, y `requirements.txt`. Nada más: sin rutas, sin plantillas, sin lógica de negocio.
 
**Qué debe hacer `create_app()`:**
 
1. Crear la aplicación con `instance_relative_config=True`.
2. Configurar `DATABASE` apuntando a `comanda.sqlite` dentro de `app.instance_path`. La documentación de Flask define la carpeta `instance/` como el lugar para archivos que no van bajo control de versiones y dependen del despliegue, que es justo el caso de esta base de datos.
3. Crear la carpeta de instancia si no existe. Flask no la crea sola, y sin ella el comando de inicialización falla.
4. Llamar a `init_app` de `app/db.py` para registrar el cierre de conexión y el comando `init-db`.
5. Devolver la aplicación.
**Resuelve estas dos decisiones ya evaluadas, no las cambies:**
 
- **No agregues `PRAGMA busy_timeout`.** Lo propusiste en la sesión anterior, pero el parámetro `timeout` de `sqlite3.connect` ya es el tiempo de espera por bloqueo y vale cinco segundos por omisión, según la documentación oficial del módulo. Un `BEGIN IMMEDIATE` que choca con otro escritor ya espera y reintenta; agregar el pragma sería redundante.
- **La base va en `instance/`**, no en la raíz del proyecto ni dentro de `app/`.
**`requirements.txt`:** solo lo necesario para ejecutar el proyecto. Fija las versiones que estés usando.
 
**Además, revisa una cosa del esquema:** `init_db()` ejecuta `esquema.sql` y `semilla.sql` sin borrar nada antes. Comprueba si ejecutar `flask init-db` dos veces seguidas funciona. Si falla o duplica los datos semilla, dime cuál de estas dos salidas prefieres y por qué, sin aplicarla todavía:
 
- Que `esquema.sql` empiece con `DROP TABLE IF EXISTS` de cada tabla, de modo que el comando sea repetible y siempre deje la base en un estado conocido.
- Dejarlo como está y documentar en el README que hay que borrar el archivo antes de volver a inicializar.
**Al terminar**, dame los comandos exactos, para PowerShell en Windows, que me permitan comprobar:
 
1. Que `flask init-db` crea la base en `instance/`.
2. Que `PRAGMA foreign_keys` devuelve 1 y `PRAGMA journal_mode` devuelve `wal`.
3. Que insertar un ítem con un `pedido_id` inexistente lanza `IntegrityError`.
4. Que la consulta de la cola usa el índice parcial, con `EXPLAIN QUERY PLAN`.
---