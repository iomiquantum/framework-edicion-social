# Plan de medición — plantillas 01–10

Fecha: **2026-09-25**  
Objetivo: aprender qué combinaciones de ángulo, estructura y sistema visual conectan mejor, sin atribuir causalidad a una sola publicación.

## Unidad de análisis

Cada registro corresponde a un archivo publicado específico, identificado por:

- `video_id`
- `template_id`
- plataforma y cuenta
- ruta y SHA-256 del archivo publicado
- fecha y hora con zona horaria
- duración
- tema y promesa del hook
- CTA
- estado orgánico o pagado
- seguidores de la cuenta al publicar
- cualquier cambio respecto al máster

## Ventanas

- 24 horas: respuesta inicial.
- 72 horas: distribución temprana.
- 7 días: comportamiento acumulado comparable.
- 28 días: solo para piezas que sigan recibiendo distribución.

Las ventanas se calculan desde la hora real de publicación. No se mezclarán datos capturados en edades distintas.

## Métricas

### Atracción

- alcance o impresiones
- reproducciones
- `viewed vs swiped away` cuando exista
- retención a 1–3 segundos cuando la plataforma la exponga

### Permanencia

- tiempo medio visto
- porcentaje medio reproducido
- retención por segundo
- finalización
- repeticiones o loops, si están disponibles
- caídas y picos con inspección del contenido correspondiente

### Valor y difusión

- compartidos por 1.000 reproducciones
- guardados por 1.000 reproducciones
- comentarios por 1.000 reproducciones
- likes por 1.000 reproducciones
- seguidores o visitas al perfil atribuibles cuando la plataforma los muestre

### Calidad cualitativa

Los comentarios se codifican sin datos personales en categorías:

- identificación personal
- aprendizaje o utilidad
- debate o desacuerdo argumentado
- pregunta concreta
- intención de probar
- mención espontánea de estilo o claridad
- reacción vacía o spam

## Hipótesis y métrica principal

| Plantilla | Hipótesis dominante | Métrica primaria | Métricas secundarias |
|---|---|---|---|
| T01 Editorial impreso | autoridad y profundidad | guardados / 1.000 | tiempo medio, comentarios de aprendizaje |
| T02 Internet nativo | interrupción y relevancia | eligió ver / swipe | retención inicial, comentarios |
| T03 Minidocumental humano | confianza y reflexión | porcentaje medio visto | comentarios personales, finalización |
| T04 Sistema claro | utilidad y decisión | guardados / 1.000 | finalización, preguntas concretas |
| T05 Cómic pop | entretenimiento accesible | compartidos / 1.000 | retención, comentarios |
| T06 Confesión cruda | identificación | comentarios personales / 1.000 | porcentaje visto, compartidos |
| T07 Caso abierto | verificación | guardados / 1.000 | revisiones, preguntas concretas |
| T08 Duelo de ideas | toma de posición | comentarios argumentados / 1.000 | compartidos, finalización |
| T09 Manifiesto de autor | identidad y aspiración | compartidos / 1.000 | seguidores, finalización |
| T10 Reto de autor | acción y competencia | respuestas o intentos / 1.000 | guardados, comentarios |

## Comparabilidad

- Comparar solo dentro de la misma plataforma y cuenta.
- Separar orgánico de pagado.
- Priorizar videos con tema, duración, nivel de familiaridad y hora de publicación similares.
- No comparar conteos brutos cuando el alcance difiere; usar tasas.
- Registrar cambios de hook, CTA, audio, duración y publicación.
- Una plantilla necesita varias aplicaciones independientes antes de considerarse consistente.
- Para atribución más fuerte, reutilizar el mismo contenido con una sola familia de cambios y pruebas A/B o Trial Reels cuando estén disponibles.

## Decisiones permitidas

- `explorar`: evidencia insuficiente, continuar probando.
- `señal_favorable`: mejora repetida en la métrica principal dentro de comparaciones válidas.
- `contextual`: funciona solo para ciertos temas, públicos o plataformas.
- `fatiga`: el rendimiento cae después de repeticiones comparables.
- `no_concluyente`: datos incompatibles o muestra pequeña.
- `retirar`: problemas editoriales, técnicos o respuesta repetidamente adversa.

No se usará `ganadora` hasta contar con varias publicaciones comparables y revisión humana.

## Registro mínimo por publicación

```markdown
- Video:
- Plantilla:
- Plataforma/cuenta:
- Archivo y SHA-256:
- Publicado:
- Ventana observada:
- Alcance/reproducciones:
- Eligió ver o retención inicial:
- Tiempo medio / porcentaje reproducido:
- Finalización:
- Compartidos por 1.000:
- Guardados por 1.000:
- Comentarios por 1.000:
- Seguimientos atribuibles:
- Categorías de comentarios:
- Cambios frente al máster:
- Interpretación:
- Limitaciones:
- Próxima prueba:
```
