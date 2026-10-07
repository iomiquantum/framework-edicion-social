# Política editorial y gobernanza

## Orden de prioridad

1. Veracidad, seguridad, derechos y fidelidad a lo dicho.
2. Comprensión de voz, captions y recursos visuales.
3. Requisitos vigentes de la plataforma.
4. Coherencia con identidad, tema y audiencia.
5. Aprendizajes propios comparables.
6. Recomendaciones oficiales con sus limitaciones.
7. Tendencias externas como hipótesis, nunca como garantía.

## Estados

```text
candidate → testing → adopted
           ↘ rejected
adopted → needs_review → adopted | deprecated
trend vencida → expired
```

`adopted` significa útil dentro del alcance declarado. No significa verdad universal.

La automatización puede crear observaciones, candidatos, propuestas y avisos de revisión. No puede promover por sí sola una hipótesis creativa a `adopted`. Esa transición requiere resultados propios documentados o aprobación editorial explícita.

La automatización tampoco puede convertir un render técnicamente válido en aprobación del usuario, reutilizar la aprobación de un hash distinto ni crear derivados de plataforma antes del bloqueo explícito del máster.

El motor de aprendizaje tampoco puede ampliar por sí solo el alcance de una señal, revocar una decisión humana mediante una medición automática, convertir similitud en calidad ni declarar una plantilla ganadora universal. Su salida es una recomendación contextual pendiente de revisión humana.

## Precedencia de aprendizaje

Cuando dos señales entren en conflicto se aplica este orden:

1. seguridad, legalidad, fidelidad y hard gates;
2. instrucción explícita vigente para el trabajo actual;
3. aprobación humana ligada al hash y alcance exactos;
4. contrato versionado de serie o creador;
5. rendimiento comparable revisado;
6. señal externa o tendencia experimental.

Una evidencia de nivel inferior no puede revocar otra superior. Toda corrección o revocación conserva el evento anterior, exige autoridad compatible y produce un nuevo snapshot; nunca reescribe el historial.

## Evidencia

- Nivel A: cambio oficial verificable o resultados propios repetidos y comparables.
- Nivel B: señal agregada de plataforma con filtros documentados o muestra reproducible.
- Nivel C: observación aislada, fuente secundaria o inferencia editorial.

Toda afirmación verificable necesita URL, fecha de consulta, alcance y limitaciones. Si no hay acceso o muestra suficiente, se registra `unknown` o `insufficient_evidence`; nunca se completa con una suposición.

Una revisión de rendimiento solo puede elevar evidencia cuando declara plataforma, ventana de medición, distribución, audiencia, cohorte y confusores. Likes, vistas o retención sin ese contexto producen observaciones, no reglas automáticas.

## Ventanas operativas iniciales

Estas ventanas son política interna configurable, no hechos científicos:

| Tipo | Revalidar | Al vencer |
| --- | ---: | --- |
| Audio, meme o reto | 72 h | Suspender recomendación |
| Hook, montaje o formato emergente | 14 días | Revisar |
| Recomendación de plataforma | 30 días | Consultar fuente vigente |
| Interfaz o zona segura | 30 días y antes de exportar | Verificar en destino |
| Regla validada localmente | 90 días | Revisar datos recientes |
| Principio editorial | 180 días | Revisar si existe contradicción |

`review_due_at` solicita revisión. `expires_at` impide seleccionar automáticamente una señal temporal vencida.

## Experimentación

- Cambiar una familia principal de variables por comparación.
- Declarar hipótesis, baseline, variante, métrica primaria y métrica de protección.
- Comparar dentro de la misma plataforma, objetivo, tema, duración y tipo de distribución.
- Separar orgánico de pagado.
- Guardar la definición y el denominador de cada métrica.
- No usar vistas brutas como árbitro universal.
- Evaluar inicialmente a 24 h, 72 h y 7 días.
- Sin analítica suficiente, el estado es `awaiting_data`.

Una regla local puede proponerse tras un resultado consistente en al menos tres pares comparables sin deteriorar la métrica de protección. Este umbral ordena el trabajo; no sustituye un análisis de variabilidad.

La experimentación creativa mantiene un portafolio de familias. Puede variar estructura, formato, estilo, ritmo o transiciones, pero una comparación interpretable declara el eje principal que cambia. Una familia puede quedar respaldada para un contexto sin desplazar a otras apropiadas para mensajes diferentes.

## Límites creativos permanentes

- No inventar cifras, logos, interfaces, citas o evidencia.
- No usar recursos con procedencia o licencia desconocida.
- No cubrir ojos, boca, rostros ni sujetos esenciales con texto, gráficos o velos, incluyendo personas y objetos principales de imágenes generadas o de apoyo.
- No usar iconos o SVG cuya relación con la frase activa no sea inmediata e inequívoca.
- No resolver cambios de sujeto con fundidos prolongados que mezclen dos rostros o vuelvan confusa la lectura.
- No convertir estimulación en saturación: cada corte, zoom, gráfico y sonido debe responder al significado.
- No adoptar una tendencia incompatible con el guion, la marca o el objetivo.
- No degradar claridad para imitar un formato viral.
