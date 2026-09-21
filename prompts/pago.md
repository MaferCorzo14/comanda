# Cuenta y pagos parciales (F4)
 
Lee `AGENTS.md`, `docs/PLAN.md`, `app/reglas.py`, `app/consultas.py` y `app/db.py` antes de empezar.
 
**Tarea:** implementar la regla 4, la cuenta de una mesa con pagos parciales. Es la última fase de construcción.
 
## El modelo
 
Nada de esto se guarda en columnas. Todo se calcula:
 
- **Total de la cuenta de una mesa:** suma de los precios congelados de los ítems **no cancelados** de todos sus pedidos. Un ítem cancelado nunca llegó a la mesa y no se cobra.
- **Pagado:** suma de los montos de los pagos de esa mesa, **sin contar la propina**.
- **Saldo:** total menos pagado.
- **Mesa libre:** saldo en cero. No hace falta ninguna marca: si no se debe nada, la mesa está libre, y si después entra un pedido nuevo el saldo vuelve a subir solo.
Si crees que este modelo tiene un problema, dímelo antes de implementarlo en lugar de resolverlo por tu cuenta.
 
## Registrar un pago
 
Los datos: quién pagó (texto libre, los clientes no están registrados), el medio (efectivo o tarjeta), el monto, la propina opcional y la fecha.
 
**Esta operación necesita transacción explícita**, con el ayudante de `db.py`. Son varias sentencias: hay que consultar el saldo actual y solo entonces insertar el pago. Es el caso para el que existe `BEGIN IMMEDIATE`: sin él, dos cajeros registrando pagos a la vez podrían pasarse del total entre la lectura y la escritura.
 
Se rechaza, con el mismo estilo de excepción que el resto del dominio, si:
 
- El monto es cero o negativo.
- El monto supera el saldo pendiente en ese instante.
- Quedan ítems no cancelados sin entregar en la mesa. Solo se cobra lo que ya se sirvió.
- El saldo ya está en cero.
**La propina va en su propia columna, separada del monto.** Si se sumara al monto, rompería la regla de que los pagos no superan el total.
 
## Vista de caja
 
Un blueprint nuevo, `caja`:
 
- Listar las mesas con su total, lo pagado y el saldo, para ver de un vistazo cuáles deben.
- Ver el detalle de una mesa: sus ítems cobrables con el precio congelado, los pagos ya registrados, y el saldo.
- Un formulario para registrar un pago.
Añade el enlace en la página inicial.
 
## Restricciones
 
- Los montos son enteros, en pesos sin decimales. Nada de coma flotante.
- Las rutas no deciden: llaman y atienden el rechazo.
- POST con redirección para registrar el pago.
- Nada nuevo en `requirements.txt`.
## Al terminar
 
Dime qué decisiones tomaste fuera de esta instrucción y cómo probar cada rechazo.