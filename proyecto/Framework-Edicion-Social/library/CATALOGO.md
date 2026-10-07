# Catálogo maestro de recursos

Generado desde `library/catalog.json` · 17 recursos · actualización 2026-09-25.

Este índice es para consulta humana. `catalog.json` es la fuente de verdad y los proyectos conservan una copia local de cada recurso utilizado.

## Resumen

| Tipo | Cantidad |
| --- | ---: |
| `bgm` | 1 |
| `icon` | 4 |
| `sfx` | 12 |

## Recursos

| ID | Tipo | Nombre | Descripción | Política | Usos | Archivo |
| --- | --- | --- | --- | --- | ---: | --- |
| `BGM-TECH-0001` | `bgm` | Pulso tecnológico 114 BPM | Cama instrumental tecnológica discreta, circular y sin voz para explicaciones de IA, procesos o productos digitales. | `limited` | 1 | [`music/tech_pulse_114bpm_8bars.wav`](music/tech_pulse_114bpm_8bars.wav) |
| `ICON-AUDIO-0001` | `icon` | Escucha con audífonos | Audífonos lineales para indicar escucha, audio inmersivo, podcast o recomendación de utilizar auriculares. | `unlimited` | 1 | [`icons/headphones.svg`](icons/headphones.svg) |
| `ICON-AUDIO-0002` | `icon` | Ondas y resonancia | Ondas lineales para representar sonido, frecuencia, resonancia, transmisión o propagación alrededor de una idea. | `unlimited` | 1 | [`icons/waves.svg`](icons/waves.svg) |
| `ICON-FOCUS-0001` | `icon` | Atención interior | Ojo lineal para representar cerrar los ojos, concentración, observación o enfoque interior sin implicar evidencia clínica. | `unlimited` | 1 | [`icons/eye.svg`](icons/eye.svg) |
| `ICON-WELL-0001` | `icon` | Respiración guiada | Icono lineal de respiración para acompañar instrucciones de inhalar, exhalar, pausar o regular el ritmo. | `unlimited` | 1 | [`icons/breath.svg`](icons/breath.svg) |
| `SFX-EMPHASIS-0001` | `sfx` | Acento grave suave | Acento breve de mayor peso para una afirmación, cifra o conclusión importante sin convertirse en golpe agresivo. | `rotate` | 2 | [`sfx/05_low_accent.wav`](sfx/05_low_accent.wav) |
| `SFX-ENTRY-0001` | `sfx` | Entrada aérea suave | Entrada aérea histórica, retirada del uso automático porque su brillo y presencia resultaron fuertes para el oído. | `do_not_reuse` | 2 | [`sfx/01_airy_in.wav`](sfx/01_airy_in.wav) |
| `SFX-ENTRY-0002` | `sfx` | Entrada aterciopelada | Entrada cálida, redondeada y con poco brillo para revelar ideas o imágenes sin sobresalir sobre la voz. | `rotate` | 1 | [`sfx/candidates/entry_velvet_bloom_soft_v01.wav`](sfx/candidates/entry_velvet_bloom_soft_v01.wav) |
| `SFX-ENTRY-0003` | `sfx` | Elevación respirada cálida | Elevación lenta, respirada y extremadamente discreta para entradas contemplativas debajo de la narración. | `rotate` | 1 | [`sfx/candidates/entry_warm_breath_lift_soft_v01.wav`](sfx/candidates/entry_warm_breath_lift_soft_v01.wav) |
| `SFX-LOOP-0001` | `sfx` | Retorno de ciclo | Gesto sonoro de retorno para reforzar un bucle, repetición, reinicio o regreso visual al punto inicial. | `rotate` | 2 | [`sfx/07_loop_return.wav`](sfx/07_loop_return.wav) |
| `SFX-MOTION-0001` | `sfx` | Whoosh corto suave | Whoosh histórico, retirado del uso automático porque su brillo y ataque resultaron fuertes para el oído. | `do_not_reuse` | 2 | [`sfx/02_soft_whoosh.wav`](sfx/02_soft_whoosh.wav) |
| `SFX-MOTION-0002` | `sfx` | Barrido de tela | Barrido mate y redondeado, parecido al roce de una tela, para acompañar desplazamientos sin un whoosh brillante. | `do_not_reuse` | 0 | [`sfx/candidates/motion_fabric_swish_soft_v01.wav`](sfx/candidates/motion_fabric_swish_soft_v01.wav) |
| `SFX-MOTION-0003` | `sfx` | Deslizamiento cálido | Deslizamiento corto, oscuro y discreto para cambios de bloque que deben sentirse sin llamar la atención. | `rotate` | 1 | [`sfx/candidates/motion_warm_slide_soft_v01.wav`](sfx/candidates/motion_warm_slide_soft_v01.wav) |
| `SFX-RESOLVE-0001` | `sfx` | Resolución cálida | Cola sonora cálida para cerrar una idea, revelar una solución o acompañar un CTA con espacio suficiente. | `rotate` | 2 | [`sfx/08_resolve.wav`](sfx/08_resolve.wav) |
| `SFX-SEQUENCE-0001` | `sfx` | Secuencia de tres pasos | Frase sonora de tres eventos para acompañar diagramas, listas o procesos visuales exactamente de tres pasos. | `rotate` | 2 | [`sfx/06_sequence.wav`](sfx/06_sequence.wav) |
| `SFX-UI-0001` | `sfx` | Tick de interfaz | Tick extremadamente breve para un nodo, marca, selección o detalle puntual sincronizado a una aparición visual. | `rotate` | 2 | [`sfx/03_ui_tick.wav`](sfx/03_ui_tick.wav) |
| `SFX-UI-0002` | `sfx` | Pop suave | Pop corto y redondeado para la aparición de una palabra clave, icono o elemento visual pequeño. | `rotate` | 2 | [`sfx/04_soft_pop.wav`](sfx/04_soft_pop.wav) |

## Regla de consulta

Antes de generar, buscar por intención, etiquetas, `best_for` y restricciones. Reutilizar solo cuando coincida el significado; una semejanza visual no basta para marcas, datos o evidencia.

Regenerar este archivo y la galería mediante:

```bash
python3 scripts/build_asset_catalog.py
```
