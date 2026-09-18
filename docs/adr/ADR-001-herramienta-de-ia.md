# ADR-001. Herramienta de IA

**Estado:** aceptada
**Fecha:** 18 de septiembre de 2026

## Contexto

El enunciado exige usar IA para construir el sistema y declarar cómo se usó. También advierte que conviene tener dos vías desde el primer día, una agéntica y un chat de respaldo, para que un tope de cuota a mitad de semana no cueste la entrega.

El criterio de selección no es qué herramienta escribe mejor código, sino cuál me permite **entender y sostener lo que entrega**. El enunciado es explícito en que un defecto del código generado es un defecto mío y en que cualquier línea puede ser objeto de pregunta.

## Decisión

**Claude Code como herramienta agéntica de construcción, y el chat de Claude como respaldo.**

El reparto de trabajo entre las dos es deliberado:

- **El chat** se usó para la etapa de análisis: aterrizar el propósito, detectar los vacíos del enunciado, decidir el alcance y redactar los documentos de especificación. Es una conversación de ida y vuelta donde yo decido y la herramienta cuestiona.
- **Claude Code** se usa para construir sobre esa especificación ya cerrada. Trabaja directamente sobre los archivos del repositorio y lee el `AGENTS.md`, que es el formato abierto pensado para dar contexto a agentes de programación.

El orden importa: primero la especificación, después el código. El agente construye contra reglas escritas, no contra una descripción improvisada en cada sesión.

## Alternativas descartadas

**GitHub Copilot con verificación de estudiante.** Gratuito con el correo institucional y bien integrado en el editor. Se descartó como herramienta principal porque su modo más usado es el autocompletado, que produce código línea a línea sin una visión del conjunto; para un proyecto donde las reglas de negocio se cruzan entre archivos, prefiero un agente que lea el repositorio completo y el `AGENTS.md`. Queda registrado como segunda opción real, ver la sección de consecuencias.

**Antigravity.** Es la opción agéntica más completa sin pagar, en versión preliminar. Se descartó porque no la he usado antes: aprender la herramienta y el proyecto a la vez, con 57 horas de plazo, agrega un riesgo que no compensa.

**Codex.** Incluido en la cuenta gratuita de ChatGPT, con acceso pensado para uso ocasional. Se descartó porque ese uso ocasional no encaja con una semana de construcción continua.

**Escribir todo a mano.** Descartado por el enunciado, que exige usar IA.

## Consecuencias

**A favor:**
- Continuidad entre el análisis y la construcción: el agente que construye recibe la especificación que se produjo en el chat, sin traducción de por medio.
- Claude Code trabaja sobre los archivos del repositorio, así que las correcciones al `AGENTS.md` tienen efecto inmediato en la siguiente sesión.

**En contra, y este es el riesgo principal:**

**Las dos vías comparten cuenta.** Claude Code y el chat de Claude se descuentan del mismo límite de uso. Si se agota, ambas se caen a la vez, que es justo lo que la advertencia del enunciado busca evitar. Dos superficies del mismo proveedor no son dos vías independientes.

**Mitigación:** activar GitHub Copilot con la verificación de estudiante y dejarlo disponible sin usarlo. No requiere tiempo de aprendizaje para un uso de emergencia, y con el correo institucional la activación es inmediata.

**Otras consecuencias asumidas:**
- Las condiciones de los planes gratuitos y de pago cambian con frecuencia; lo verificado aquí corresponde a la fecha de esta decisión.
- Delegar la construcción a un agente exige leer todo lo que produce. El tiempo que ahorra escribiendo se gasta revisando, y esa revisión no es opcional: es la que me permite responder en la defensa.

## Cómo se declara el uso

Cada sesión de trabajo queda registrada en `BITACORA-IA.md`: qué se pidió, qué propuso el agente, qué se aceptó o rechazó y por qué, y qué quedó sin verificar.

## Referencias

- [AGENTS.md, formato abierto para dar contexto a agentes de programación](https://agents.md/)