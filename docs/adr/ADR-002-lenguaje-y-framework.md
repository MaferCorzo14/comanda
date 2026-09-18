# ADR-002. Lenguaje y framework web

**Estado:** aceptada
**Fecha:** 18 de septiembre de 2026

## Contexto

El sistema necesita una interfaz para operarlo, con una vista distinta por rol: administrador, cocina, mesero y caja. La interfaz puede ser web o API.

Tres condiciones del proyecto acotan la elección:

1. **El plazo de entrega es de un fin de semana.** No hay margen para aprender una tecnología y construir con ella al mismo tiempo.
2. **El código lo produce un agente de IA, pero la responsabilidad es de quien entrega.** Cada línea debe poder leerse, verificarse y explicarse. Eso descarta cualquier stack donde el comportamiento dependa de capas que no se ven.
3. **El sistema debe poder levantarse desde cero en otra máquina**, sin instalar servicios ni configurar entornos complejos.

El criterio de selección no es la potencia del framework, sino cuánto del sistema queda bajo control directo de quien lo mantiene.

## Decisión

**Python 3 con Flask y plantillas Jinja2**, con vistas renderizadas en el servidor, una por rol.

Razones:

- Python es el lenguaje con el que ya se ha trabajado en desarrollo web, de modo que el código generado se puede revisar y corregir, no solo ejecutar.
- Flask expone las rutas como funciones con decoradores explícitos. No hay configuración automática ni comportamiento implícito: lo que está escrito en el archivo es todo lo que ocurre.
- Jinja2 viene incluido con Flask, así que la interfaz no requiere build de frontend, Node ni dependencias de JavaScript.
- Renderizar en el servidor evita construir dos aplicaciones separadas, una API y un cliente, dentro del plazo disponible.

## Alternativas descartadas

**Go con la librería estándar.** Compila a un binario único y su enrutador estándar es suficiente para este sistema. Se descartó porque no hay experiencia previa con el lenguaje: el tiempo de aprender la sintaxis competiría con el de revisar el código generado, y sin ese repaso no se puede responder por lo que se entrega. El interés en aprender Go no es un objetivo de este proyecto y puede atenderse después, reescribiendo el sistema sin plazo de por medio.

**Django.** Trae ORM, panel de administración y autenticación resueltos. Se descartó por eso mismo: buena parte del sistema no estaría escrita por el equipo, y ubicar dónde se aplica una regla de negocio dentro de su ORM es más difícil que señalar una consulta SQL. Su panel de administración resolvería la gestión de platos e ingredientes de una forma que no responde a ninguna decisión propia de diseño.

**FastAPI.** Genera documentación interactiva de la API de forma automática. Se descartó porque está orientado a API y no a vistas HTML: habría que incorporar el sistema de plantillas por separado, y su mecanismo de inyección de dependencias añade una capa más de comportamiento que entender.

**Java con Spring Boot.** Hay experiencia previa con el lenguaje, pero su funcionamiento se apoya en anotaciones y configuración automática. Es el stack donde resulta más difícil rastrear qué ocurre y por qué, y el más lento de poner en marcha desde cero.

## Consecuencias

**A favor:**
- Todo el código generado puede revisarse dentro del plazo.
- Poner en marcha el sistema se reduce a instalar dependencias y ejecutar un comando.
- Cada regla de negocio queda en una función localizable, no distribuida entre capas del framework.

**En contra, y asumido:**
- El servidor de desarrollo de Flask no es apto para producción. Es aceptable porque el despliegue no forma parte del alcance.
- Las vistas renderizadas en el servidor obligan a recargar la página: la cola de cocina se actualiza por recarga periódica, no en vivo.
- Sin un framework de estilos, la interfaz será funcional antes que vistosa.
- Al no usar ORM hay más SQL que escribir y revisar. Es un costo aceptado a cambio de que cada consulta sea visible y verificable.

## Referencias

- [Flask, documentación oficial](https://flask.palletsprojects.com/)
- [Jinja2, documentación oficial](https://jinja.palletsprojects.com/)