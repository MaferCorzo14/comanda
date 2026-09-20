# Rrutas y plantillas (F2, segunda parte)
 
Lee `AGENTS.md`, `docs/PLAN.md`, `app/reglas.py` y `app/consultas.py` antes de empezar.
 
**Tarea:** escribe las rutas y las plantillas del flujo principal. Nada de la fase F3 ni F4: sin cancelación, sin gestión de ingredientes, sin caja.
 
## Identidad y roles
 
No hay autenticación. **El rol y la identidad van en la URL**, sin sesión de usuario:
 
- `/` — página inicial con enlaces a cocina y a cada mesero.
- `/cocina` — la cola.
- `/mesero/<mesero_id>` — las mesas y los ítems listos de ese mesero.
Así no hace falta ni inicio de sesión ni almacenamiento de sesión para identificar a nadie.
 
## Rutas
 
Organízalas en blueprints, uno por rol, en `app/rutas/`.
 
**Mesero:**
- Ver sus pedidos y los ítems en `LISTO` que debe llevar.
- Un formulario para crear un pedido: elegir mesa y marcar platos.
- Marcar un ítem como entregado.
**Cocina:**
- Ver la cola, agrupada por pedido y ordenada por antigüedad.
- Iniciar un ítem.
- Marcar un ítem como listo.
## Cómo se escriben las rutas
 
**Las rutas no deciden nada.** No validan estados, no escriben SQL, no comprueban si una transición es posible. Reciben la petición, llaman a `reglas.py` o `consultas.py`, y eligen qué mostrar.
 
**No comprobar el estado antes de llamar a la regla.** Si una ruta hiciera "si el ítem está en PENDIENTE, entonces iniciarlo", la regla viviría en la ruta. Llama directamente a la operación y atiende el rechazo.
 
**Atender el rechazo.** Captura la excepción de transición inválida de `reglas.py` y muestra un mensaje claro al usuario. Nunca debe salir una página de error del servidor por una operación legítimamente rechazada.
 
**Toda operación que cambia estado es POST, seguida de una redirección.** Nunca se cambia estado con un GET, y tras el POST se redirige para que recargar la página no repita la operación.
 
## Plantillas
 
Una plantilla base con el encabezado y los estilos, y una por vista. Estilos sencillos, escritos a mano, en un solo archivo. Sin framework de CSS, sin JavaScript, sin dependencias externas.
 
**La cola de cocina se refresca sola cada pocos segundos**, con la forma más simple que exista en HTML y sin JavaScript.
 
**Las horas se muestran en hora local.** La base guarda UTC y Colombia está en UTC−5: mostrar el valor crudo haría que la cocina viera horas que no coinciden con su reloj. Resuélvelo en la capa de presentación, con un filtro de plantilla, no cambiando lo que se guarda.
 
Cada ítem de la cola debe mostrar a qué mesa y pedido pertenece, el plato, y hace cuánto está esperando.
 
## Restricciones
 
- Solo Flask y Jinja2. Nada nuevo en `requirements.txt` salvo lo imprescindible, y si agregas algo, dime por qué.
- Si necesitas configurar algo más en `create_app()`, dilo y explica para qué.
## Al terminar
 
Dime:
 
1. Qué decisiones tomaste que no estaban en esta instrucción.
2. Los pasos exactos para recorrer el flujo completo en el navegador: crear un pedido, verlo en la cola, iniciarlo, marcarlo listo y entregarlo.
3. Cómo enviar una transición inválida directamente por HTTP, sin usar la interfaz, para comprobar que se rechaza.
---
 
## Cómo revisar lo que devuelva
 
| Revisar | Qué buscar |
|---|---|
| SQL en rutas | No debe haber ni un `SELECT` ni un `UPDATE` en `app/rutas/` |
| Validación en rutas | Ningún `if` que compruebe estados antes de llamar a la regla |
| Métodos | Las operaciones que cambian estado son `POST`. Si alguna es `GET`, está mal |
| Redirección | Tras cada `POST` hay un `redirect`, no un `render_template` directo |
| Rechazo | La excepción se captura y produce un mensaje, no un error 500 |
| Plantillas | No hay consultas ni cálculos dentro del HTML |
| Dependencias | `requirements.txt` sigue teniendo solo lo necesario |
| Horas | Se muestran en hora local, no en UTC |