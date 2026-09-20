# Disponibilidad y cancelación (F3)
 
Lee `AGENTS.md`, `docs/PLAN.md`, `app/reglas.py` y `app/consultas.py` antes de empezar.
 
**Tarea:** implementar las reglas 2 y 3. No toques nada de F4: sin cuenta, sin pagos, sin caja.
 
El registro de faltantes de cocina queda **fuera de esta tarea**, aunque el plan lo mencione. Se hará solo si sobra tiempo al final.
 
## Regla 3 — cancelar un ítem
 
Una operación nueva en `reglas.py`: cancelar un ítem. Sigue exactamente el mismo patrón que las demás transiciones, una sola sentencia condicionada al estado previo, escribiendo `cancelado_en` en la misma sentencia que el cambio de estado. Solo procede desde `PENDIENTE`.
 
Pueden cancelar **tanto el mesero como la cocina**, así que hace falta el botón en las dos vistas, con sus rutas correspondientes en cada blueprint.
 
Recuerda que el esquema ya tiene la restricción que impide guardar un ítem cancelado con fecha de inicio. No la toques ni la relajes.
 
## Regla 2 — disponibilidad
 
**Repón la validación en `crear_pedido`.** Se quitó al recortar el alcance de F2 y ahora vuelve. Tiene que ocurrir **dentro de la transacción** de `crear_pedido`, no en la ruta antes de llamarla: dentro, el candado de escritura ya está tomado y nadie puede agotar un ingrediente entre la comprobación y la creación. Si se hiciera fuera, quedaría un hueco.
 
Usa `consultas.plato_disponible`, que ya está escrita. Un plato no disponible rechaza la creación del pedido completo con una excepción propia del dominio, igual que las transiciones inválidas.
 
**El menú del mesero solo ofrece platos disponibles.** El formulario de nuevo pedido debe listar únicamente los platos que tengan receta y todos sus ingredientes disponibles.
 
## Vista de administrador
 
Un blueprint nuevo, `administrador`, con lo mínimo para operar la regla 2:
 
- Listar los ingredientes con su disponibilidad.
- Marcar un ingrediente como agotado o como disponible.
- Listar los platos mostrando cuáles se están ofreciendo y cuáles no, para poder ver el efecto.
Añade el enlace en la página inicial.
 
## Restricciones
 
- Las rutas siguen sin decidir nada: llaman y atienden el rechazo.
- Las operaciones que cambian estado son POST con redirección.
- Nada nuevo en `requirements.txt`.
## Al terminar
 
Dime qué decisiones tomaste fuera de esta instrucción y cómo probar cada regla, incluidos los casos que deben rechazarse.
 
---
 
## Cómo revisar
 
| Revisar | Qué buscar |
|---|---|
| Cancelar | Un solo `UPDATE` con `AND estado = 'PENDIENTE'`, con `cancelado_en` en la misma sentencia |
| Disponibilidad | La comprobación está **dentro** de la transacción de `crear_pedido`, no en la ruta |
| Menú | El formulario del mesero filtra por disponibilidad |
| Rutas | Sin SQL, sin validaciones previas |
| Esquema | El `CHECK` de cancelación sigue intacto |