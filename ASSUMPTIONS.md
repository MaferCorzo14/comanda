# ASSUMPTIONS.md

Lo que el enunciado no define y se resolvió en este proyecto. Cada supuesto indica por qué se tomó esa salida.

## Entidades

**A-01. Ingrediente no esta en las entidades mínimas, pero se agrega.**
Se destaca Mesa, pedido, ítem de pedido, plato y estado de preparación. La regla 2 habla de ingredientes disponibles, así que sin esta entidad la regla no se puede implementar. 

**A-02. La disponibilidad de un ingrediente es un booleano, no una cantidad.**
No hay inventario con unidades ni descuento por receta. La regla dice "sin ingredientes disponibles", no "sin existencias suficientes". Un modelo de stock con cantidades habría traído reservas, devoluciones por cancelación y reposición.

**A-03. Un plato sin receta registrada no se ofrece.**
Evita vender algo cuya preparación cocina no ha definido.

## Estados y pedidos

**A-04. Los estados de un ítem son PENDIENTE, EN_PREPARACION, LISTO, ENTREGADO y CANCELADO.**
El enunciado no los enumera.

**A-05. El estado del pedido tiene cuatro valores: ANULADO, ENTREGADO, COMPLETO y EN_CURSO, comprobados en ese orden.**
ANULADO cuando todos los ítems están CANCELADO. ENTREGADO cuando todos están ENTREGADO o CANCELADO. COMPLETO cuando todos están LISTO, ENTREGADO o CANCELADO (listos para entregar, así no se hayan entregado todos aún). EN_CURSO en cualquier otro caso. Un ítem cancelado cuenta como resuelto en los tres primeros; si no, un pedido con una cancelación nunca podría cerrarse. El orden de las comprobaciones importa porque los conjuntos se anidan unos en otros: un pedido totalmente ENTREGADO también cumple la condición de COMPLETO, así que hay que comprobar primero la condición más específica para no reportarlo como algo menos preciso de lo que es.

**A-06. CANCELADO es terminal.**
No se permite reactivar un ítem cancelado, para que no exista la transición "cancelado y luego habilitado de nuevo".

**A-07. Un pedido con todos sus ítems cancelados queda anulado, pero no se borra.**
Se excluye de la cola y de la cuenta. Se conserva por trazabilidad de las cancelaciones y de los tiempos.

**A-08. Un ítem representa una unidad.**
Pedir tres hamburguesas crea tres ítems, porque la regla 1 exige que cada ítem avance por sus propios estados.

**A-09. A un pedido ya creado no se le agregan ítems.**
Una ronda nueva o una alternativa tras una cancelación es un pedido nuevo. Así la antigüedad de un pedido es estable y la cola no cambia de orden por añadidos.

**A-10. Una mesa puede tener varios pedidos, y cada pedido pertenece a un mesero.**
El enunciado no define la relación entre mesa y pedido. La cuenta se calcula por mesa, sumando todos sus pedidos.

**A-11. Los ítems admiten una nota de texto libre.**
Sin modificadores estructurados ni efecto sobre la receta.

## Ingredientes agotados

**A-12. Cocina verifica los ingredientes antes de iniciar un ítem.**
Si falta alguno, cancela el ítem mientras está PENDIENTE, lo cual respeta la regla 3, y registra el faltante para el administrador. Un ítem que ya pasó a EN_PREPARACION siempre se termina.

**A-13. Se descartó agregar un estado de salida para ítems en preparación.**
Habría contradicho la regla 3 del enunciado.

**A-14. Los ítems ya pedidos de un plato que queda sin ingredientes no se cancelan solos.**
La regla 2 impide *pedir*, no obliga a anular lo pedido. La cancelación la decide cocina.

**A-15. La alternativa que elija el cliente tras una cancelación va en un pedido nuevo.**
Consecuencia de A-09.

## Cuenta y pagos

**A-16. Los pagos parciales son por monto libre.**
Se registra quién pagó (texto libre), el medio (efectivo o tarjeta), el monto y la fecha. El monto libre cubre también la división en partes iguales, que es un caso particular.

**A-17. El saldo pendiente no se guarda: se calcula como total menos pagos.**
Guardarlo permitiría que se desincronizara de los pagos reales.

**A-18. El medio de pago es solo un dato.**
No hay pasarela ni validación de tarjetas; se excluye los pagos reales.

**A-19. Solo se aceptan pagos cuando todos los ítems no cancelados de la mesa están entregados.**

**A-20. Los ítems cancelados no se cobran.**
Un plato cancelado antes de prepararse nunca llegó a la mesa.

**A-21. El precio se congela en el ítem de pedido al momento de pedir.**
Un cambio posterior en el precio del plato no altera cuentas abiertas.

**A-22. La propina, si se registra, va en un campo aparte del monto.**
Si se sumara al monto, rompería la regla de que los pagos no superan el total.

**A-23. La mesa se cierra cuando el saldo llega a cero.** Una cuenta cerrada no admite más pagos ni pedidos.

**A-24. No hay impuestos ni descuentos.**

## Cola de cocina

**A-25. La cola muestra ítems PENDIENTE y EN_PREPARACION, agrupados por pedido.**
El negocio pide los pendientes agrupados, sin decir por qué criterio. Agrupar por pedido permite ver qué le falta a cada mesa; incluir los que están en preparación evita que cocina pierda de vista lo que ya empezó.

**A-26. El orden es estrictamente por antigüedad del ítem.**
En la práctica un plato largo que llegó antes puede retrasar a uno rápido posterior, pero la consulta obligatoria pide antigüedad y no se altera ese orden. Priorizar por tiempo estimado de preparación queda registrado como mejora posible, no implementada.

## Personas y datos

**A-27. No se guardan datos personales de los clientes.**
El nombre que acompaña a un pago es texto libre para identificar quién abonó, no un registro de cliente.

**A-28. El cliente no interactúa con el sistema.**
Se evaluó un menú por código QR y se descartó: exigiría identificar mesas sin autenticación y asignar meseros automáticamente, dos subsistemas que ninguna regla del enunciado pide.

**A-29. No hay autenticación: el rol se selecciona en la interfaz.**
Se excluye explícitamente la autenticación avanzada.

**A-30. Se registra la marca de tiempo de cada transición de estado.**
Necesario para la antigüedad de la cola y para medir tiempos.

**A-31. Un solo restaurante, una sola cocina, una sola cola.**

## Pendientes de decidir

- Stack, arquitectura y motor de persistencia: ADR-002 y ADR-003.
- Herramienta de IA: ADR-001.
- Idioma de los identificadores en el código.