# Social Essentials Original · v1.0

Ocho efectos cortos para edición educativa/tecnológica en español. Todos se sintetizan desde cero mediante osciladores, ruido y envolventes en `generate_sfx.py`; no contienen muestras, música ni grabaciones de terceros. Son mono, WAV PCM de 24 bits a 48 kHz, compatibles con mezcla estéreo sin problemas de fase. Los nombres son estables para reutilizarlos en plantillas.

## Selección y niveles

| Archivo | Duración | Pico del archivo | Uso propuesto |
|---|---:|---:|---|
| `01_airy_in.wav` | 0,44 s | −12 dBFS | Entrada ligera de un diagrama o concepto |
| `02_soft_whoosh.wav` | 0,30 s | −12 dBFS | Desplazamiento gráfico o cambio de bloque |
| `03_ui_tick.wav` | 0,085 s | −10 dBFS | Un nodo, marcador o detalle puntual |
| `04_soft_pop.wav` | 0,16 s | −10 dBFS | Aparición de una palabra o elemento clave |
| `05_low_accent.wav` | 0,34 s | −12 dBFS | Énfasis importante, cálido y breve |
| `06_sequence.wav` | 0,50 s | −14 dBFS | Tres pasos de una secuencia visual |
| `07_loop_return.wav` | 0,48 s | −14 dBFS | Retorno al inicio o repetición conceptual |
| `08_resolve.wav` | 0,84 s | −15 dBFS | Cierre de una idea con espacio en la voz |

Los picos de esta tabla corresponden al archivo, no al nivel final de mezcla ni a LUFS. `manifest.json` incluye duración, pico y RMS de cada archivo. La mezcla definitiva debe medirse de nuevo porque voz, música y efectos se suman.

## Regla editorial inicial

Para una primera versión de un video de un minuto, empezar con 5–8 eventos sonoros distribuidos en cambios de significado. Una variante de mayor densidad puede llegar a 22 eventos si cada cue está localizado, no compite con la voz y supera una auditoría en altavoz de teléfono. Ambos presupuestos son hipótesis editoriales, no reglas oficiales de las plataformas ni promesas de retención. Reutilizar una misma familia sonora da continuidad.

Colocar el sonido contra la aparición o movimiento que explica; ajustar a fotograma y escuchar el resultado. El pico de los whooshes llega después de su inicio: adelantar aproximadamente media duración si se quiere que coincida con un corte. Los cues melódicos `06` y `07` funcionan mejor cuando el gráfico reproduce sus tres pasos; sus tiempos están definidos en el generador.

El perfil V2 histórico llegó a usar `data-volume` de 1,05–1,75. Esa práctica ya no es el punto de partida del framework: puede volver agresivo un efecto brillante aunque no exista clipping. Comenzar normalmente entre `0.35` y `0.50`, comparar dentro de la mezcla y no superar `1.0` sin una escucha específica. Medir la suma final, bajar cualquier cue que tape consonantes y evitar limitación audible.

`01_airy_in.wav` y `02_soft_whoosh.wav` se conservan por reproducibilidad histórica, pero fueron rechazados explícitamente por exceso de intensidad y brillo. No deben seleccionarse automáticamente en proyectos nuevos.

## Pack suave revisado

El subdirectorio `candidates/` contiene cuatro alternativas con filtros de dos o tres polos, ataques redondeados, picos entre −22 y −24 dBFS y menor energía aguda. La decisión explícita vive en `candidates/review.json`:

| ID | Archivo | Función | Decisión |
| --- | --- | --- | --- |
| `SFX-ENTRY-0002` | `entry_velvet_bloom_soft_v01.wav` | Entrada cálida y aterciopelada | Aprobado |
| `SFX-ENTRY-0003` | `entry_warm_breath_lift_soft_v01.wav` | Entrada respirada y contemplativa | Aprobado |
| `SFX-MOTION-0002` | `motion_fabric_swish_soft_v01.wav` | Barrido mate tipo tela | Rechazado; no reutilizar |
| `SFX-MOTION-0003` | `motion_warm_slide_soft_v01.wav` | Deslizamiento corto y oscuro | Aprobado |

Regenerar únicamente este grupo mediante `python3 generate_soft_candidates.py`. Su manifiesto independiente evita alterar el pack histórico y `review.json` conserva la decisión aunque se regeneren los WAV.

La aprobación requiere dos escuchas: auriculares/monitores para detectar aspereza y altavoz de teléfono a volumen normal para confirmar que whooshes, ticks, pops y resolves realmente se perciben. Si un efecto solo se oye al buscarlo, puede subirse dentro del margen técnico; si llama más la atención que la frase, debe bajarse o retirarse. Priorizar siempre la comprensión de la voz. Como objetivo de trabajo, la mezcla puede rondar −16 LUFS integrada y un techo de −1 dBTP, sujeto a medición del render final; no se presenta como requisito de publicación.

## Separación de grupos

- `voiceover`: referencia principal; no se sacrifica para hacer sitio a un efecto.
- `music`: cama independiente, con carve dinámico contra la voz cuando compitan en la misma banda. El perfil V2 usa `strength: 0.8` como punto de partida.
- `sfx`: cues puntuales con su propio `data-volume`; editar por evento, no elevando todo el bus indiscriminadamente.

La separación permite cambiar música, SFX o tratamiento de voz sin rehacer el montaje visual. Un render final aplana los grupos, pero el editable debe conservarlos.

## Cuándo NO usar

- No poner un efecto por palabra, subtítulo, zoom o corte de respiración.
- No encadenar los ocho por tenerlos disponibles; elegir los que refuercen la narración.
- Evitar `03`/`04` repetidos en pasajes solemnes o donde la voz ya sea rápida.
- Evitar `06`/`07`/`08` sobre una música cuya tonalidad choque con sus notas.
- Evitar `05` debajo de golpes graves de la música; comprobar audibilidad en teléfono.
- Evitar un sonido de cierre si el siguiente fragmento continúa inmediatamente la explicación.
- No etiquetar este pack como tendencia viral. Es vocabulario sonoro original y reutilizable, pendiente de evaluación editorial y de resultados reales.

## Procedencia, derechos y reproducción

Creado para este framework el 23 de septiembre de 2026 mediante síntesis procedural original asistida por IA. No se ha usado una biblioteca externa, voz clonada, grabación o muestra protegida. No se ha entrenado ningún modelo de audio para generar estos archivos: los construye el código matemático incluido.

En la medida en que existan derechos sobre este código y los archivos generados, se ofrecen bajo **CC0 1.0 Universal**, permitiendo uso, modificación y distribución, incluso comercial, sin atribución. Esta declaración no afirma que una creación puramente procedural o asistida por IA tenga necesariamente protección autoral. Texto de la dedicación: <https://creativecommons.org/publicdomain/zero/1.0/>.

Regenerar con `python3 generate_sfx.py` desde esta carpeta. Usa únicamente la biblioteca estándar de Python. La semilla fija mantiene los resultados reproducibles. La generación reemplaza únicamente estos ocho WAV y su manifiesto dentro de esta carpeta; duplicar y versionar antes de cambiar parámetros. Los archivos originales tienen margen de pico y desvanecimientos de borde; revisar otra vez el techo de la mezcla al exportar.
