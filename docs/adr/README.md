# Decisiones de arquitectura

Registro de las decisiones importantes del proyecto. Cada una explica el contexto en que se tomó, qué se decidió, qué alternativas se descartaron y con qué consecuencias.

Las decisiones no se editan una vez aceptadas. Si una deja de ser válida, se escribe una nueva que la reemplace y la anterior se marca como superada, para que quede el rastro de cómo evolucionó el proyecto.

| # | Decisión | Estado | Fecha |
|---|---|---|---|
| [001](ADR-001-herramienta-de-ia.md) | Herramienta de IA | Aceptada | 18/09/2026 |
| [002](ADR-002-lenguaje-y-framework.md) | Lenguaje y framework web | Aceptada | 18/09/2026 |
| [003](ADR-003-persistencia.md) | Persistencia y control de concurrencia | Aceptada | 18/09/2026 |

## Formato

Cada decisión sigue la misma estructura:

```markdown
# ADR-NNN. Título

**Estado:** propuesta | aceptada | superada por ADR-NNN
**Fecha:** DD de mes de AAAA

## Contexto
Qué situación obliga a decidir. Las restricciones reales, no las deseables.

## Decisión
Qué se eligió y por qué.

## Alternativas descartadas
Cada opción considerada, con el motivo concreto del descarte.

## Consecuencias
Lo que se gana y lo que se acepta perder.
```