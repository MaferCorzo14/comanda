# comanda
Gestión de pedidos y cola de cocina para restaurantes. 

Un restaurante que toma los pedidos en papel tiene dos problemas: la cocina no sabe en qué orden preparar y los meseros no saben qué está listo. Comanda reemplaza la nota de papel por un registro compartido, con una cola ordenada por antigüedad para la cocina y una vista de lo que está listo para el mesero.

## Qué hace

- **Pedidos por mesa.** El mesero registra el pedido y queda asignado a él. Una mesa puede tener varios pedidos.
- **Estados por ítem.** Cada plato del pedido avanza por su cuenta: pendiente, en preparación, listo, entregado. El pedido está completo cuando todos sus ítems lo están.
- **Menú vivo.** Un plato cuyo ingrediente se agota deja de ofrecerse automáticamente.
- **Cancelación con límite.** Un ítem se puede cancelar solo mientras la cocina no lo haya empezado.
- **Cuenta por mesa con pagos parciales.** Varios pagos de monto libre hasta cubrir el total.

## Alcance

Incluye persistencia de datos, una interfaz web para operar el sistema, las cuatro reglas de negocio y las consultas que resumen el estado.

Queda fuera: autenticación avanzada, pagos reales, despliegue en producción, integraciones externas, impuestos y descuentos.

## Roles

| Rol | Qué hace |
|---|---|
| Administrador | Platos y disponibilidad de ingredientes |
| Cocina | Recetas, cola de preparación, inicio y fin de cada ítem |
| Mesero | Registra pedidos y entrega lo que está listo |
| Caja | Registra los pagos parciales de una mesa |

## Reglas de negocio

1. Cada ítem avanza por sus propios estados. El pedido está completo cuando todos sus ítems están listos o cancelados.
2. Un plato sin ingredientes disponibles no se puede pedir y deja de ofrecerse.
3. Un ítem se puede cancelar solo si la cocina todavía no lo empezó.
4. La cuenta de una mesa puede dividirse entre varios pagos parciales.

Las cuatro se validan en el servidor, dentro de una transacción. La interfaz nunca decide.

## Cómo ejecutarlo

Pendiente. Se completa cuando se defina el stack (ADR-002 y ADR-003) y exista el primer flujo funcionando.

## Criterios de éxito

Obligatorios:

| Criterio | Medida | Umbral |
|---|---|---|
| Las cuatro reglas se cumplen | Un escenario por regla, aceptando lo válido y rechazando lo inválido | 4 de 4 |
| No se cancela un ítem empezado | Cancelaciones exitosas de ítems que no están pendientes | 0 |
| No se pide un plato sin ingredientes | Ítems creados con un plato no disponible | 0 |
| Los pagos no superan el total | Cuentas con pagos por encima del total, sin contar propina | 0 |
| La cola es correcta | Resultado con datos de prueba conocidos frente al esperado | Coincidencia exacta |
| Nada se pierde | Datos tras reiniciar el servidor | Sin pérdida |
| El README funciona | Levantar el proyecto en otra máquina siguiendo solo estas instrucciones | Sin pasos adicionales |

Deseables, sujetos al tiempo disponible:

| Criterio | Medida | Umbral |
|---|---|---|
| El mesero ve lo listo rápido | Segundos entre listo y su aparición en la vista del mesero | 5 s o menos |
| Registro de faltantes | Reportes de cocina visibles para el administrador | Funcionando |
| Propina | Registrada aparte del monto del pago | Funcionando |
| Pruebas automatizadas | Reglas cubiertas por pruebas | Al menos las 4 reglas |

Los criterios no cumplidos se reportan como tales al cierre, con el motivo.

## Documentación

| Archivo | Contenido |
|---|---|
| [AGENTS.md](AGENTS.md) | Contexto e instrucciones para el agente de IA |
| [ASSUMPTIONS.md](ASSUMPTIONS.md) | Lo que el enunciado no define y se resolvió aquí |
| [BITACORA-IA.md](BITACORA-IA.md) | Registro por sesión de trabajo con la IA |
| [docs/adr/](docs/adr/) | Decisiones de arquitectura |

## Contexto

Proyecto desarrollado como prueba técnica individual de la asignatura Herramientas de Empleabilidad en Ingeniería de Sistemas, Universidad Francisco de Paula Santander, septiembre de 2026. El enunciado se entregó deliberadamente incompleto; los vacíos resueltos están documentados en [ASSUMPTIONS.md](ASSUMPTIONS.md).

## Ejecución

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run
```

### Reiniciar la base de datos

`init-db` crea la base; no la reinicia. Si ya existe, el comando falla en
lugar de sobrescribirla. Para empezar de cero, borra el archivo primero:

```powershell
Remove-Item instance\comanda.sqlite
flask --app app init-db
```
