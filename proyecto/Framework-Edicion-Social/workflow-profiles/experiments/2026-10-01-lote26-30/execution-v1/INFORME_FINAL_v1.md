# Informe final del piloto de edición: lote 26–30

La producción experimental terminó con **cinco MP4 finales locales**, verificados por sus hashes y QA técnico y visual por muestras. Se corrigieron los defectos observados antes de cerrar las entregas. La escucha, reproducción continua, revisión en un dispositivo físico y aprobación editorial humana siguen pendientes. **Flujo 1 continúa predeterminado; flujo 2 y flujo 3 permanecen experimentales.** Este piloto no demuestra ahorro ni equivalencia causal de calidad.

## Reparto y condiciones

La [asignación v1](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/assignment-v1.json>) quedó congelada después de la ingesta y antes del montaje. Par A: VIDEO26 con flujo 1 (28,267 s) y VIDEO28 con flujo 2 (24,700 s), complejidad simple a moderada. Par B: VIDEO27 con flujo 1 (22,033 s) y VIDEO29 con flujo 2 (23,967 s), captions protagonistas frente a ritmo y recapitulación. El par A empezó primero; en B se inició 29 antes de 27. VIDEO30, flujo 3 (15,900 s), preservó los cuatro canales semánticos de T30 mediante módulos probados: texto, voz/onda, símbolo contextual y recapitulación.

Todos los trabajadores recibieron GPT‑6.1 Sol con razonamiento Medio. Root confirmó la configuración de los agentes; el runtime de root no se verificó independientemente. No hay costos ni tokens atribuibles por video. Los cinco proyectos usaron HyperFrames 0.8.100; la ingesta mantuvo ASR 0.8.99. Los videos históricos 21–25 no son controles causales de este piloto.

La ingesta inicial compartida tomó **767,083 s (12 min 47,083 s)** y se cuenta una sola vez. El inventario final volvió a calcular los hashes de los **52 archivos de preproducción: 52 sin cambios y ninguno ausente**, según [comparación final](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/preproduction-integrity-final-v1.json>). Su costo histórico es desconocido y queda excluido. La producción nueva adaptó los recursos discordantes conservando esos originales; generó una imagen contextual para 26 (25,957 s de herramienta) y un SFX local para 27 (0,021825 s de síntesis; 0,642127 s de herramienta). Estos procesos ya están contenidos en fases y no se suman otra vez.

## Entregas y calidad observada

| Video / versión | Archivo final | Evidencia | Frames revisados en esta versión |
| --- | --- | --- | ---: |
| 26 v3 | [MP4](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-26/entrega/VIDEO-26-ENTREGA-HLG-v3.mp4>) | [QA exacto](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-26/editable-hyperframes-video-26/qa/final-review-v3.json>) · [Sombra](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/shadow-VIDEO26-exact-v3/audit.json>) | 59 |
| 27 v2 | [MP4](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-27/entrega/VIDEO-27-ENTREGA-HLG-v2.mp4>) | [QA exacto](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-27/editable-hyperframes-video-27/qa/exact-export-review-v2.json>) · [Sombra](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/shadow-VIDEO27-exact-v2/audit.json>) | 60 |
| 28 v1 | [MP4](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-28/entrega/VIDEO-28-ENTREGA-HLG-v1.mp4>) | [QA exacto](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-28/editable-hyperframes-video-28/qa/local-delivery-receipt-v1.json>) · [Sombra](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/shadow-VIDEO28-exact-v1/audit.json>) | 42 |
| 29 v2 | [MP4](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-29/entrega/VIDEO-29-ENTREGA-HLG-v2.mp4>) | [QA exacto](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-29/editable-hyperframes-video-29/qa/final-review-v2.json>) · [Sombra](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/shadow-VIDEO29-exact-v2/audit.json>) | 58 |
| 30 v2 | [MP4](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-30/entrega/VIDEO-30-ENTREGA-HLG-v2.mp4>) | [QA exacto](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-30/editable-hyperframes-video-30/qa/QA_EXACTO_VIDEO30_v2.json>) · [Sombra](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/shadow-VIDEO30-exact-v2/audit.json>) | 24 |

En 30 v2 se revisaron 24 frames críticos y ocho cues directamente; se conservan 47 muestras de v1 y sus nueve cues para dependencias intactas, con el alcance documentado. En 29 v2 se conservan los 140 frames de v1 para entradas intactas, además de 58 muestras nuevas de todos los 15 cues y transiciones modificadas. En cada MP4 final se verificó audio AAC completo y tres ventanas SFX; esto acredita identidad técnica, no audibilidad subjetiva.

Se conservaron las reglas de composición y los rasgos gráficos de las plantillas: T26 jerarquía de lectura y tarjetas conectadas; T27 captions protagonistas, iconos de los formatos mencionados, onda y cierre; T28 guía visual de audio mediante onda y foco circular; T29 comparación y recapitulación circular; T30 cuatro accesos semánticos. Las imágenes acompañan el contexto de la voz y el retorno del presentador; captions y gráficos permanecen separados del rostro y los gestos en las muestras finales. El espacio negativo deliberado se conserva. No se impuso una cuota de imágenes o iconos ni una rejilla común que borrara la identidad.

## Tiempos por fase

Segundos de reloj de pared, agregados de intervalos cerrados de cada run. Incluyen tareas, coordinación y comandos según las notas; no son atención pura ni CPU. Los tiempos de motor incluidos se muestran después, **sin sumarlos de nuevo**. “No medido” no significa cero.

| Video | Flujo | Semántica | Recursos | Montaje | QA previo | Fase render | QA posterior | Correcciones | Documentación | Coordinación |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 26 | 1 | 577.5 | 256.1 | 412.0 | 273.2 | 573.1 | 305.1 | 519.3 | 178.2 | No medido |
| 27 | 1 | 364.0 | 322.4 | 151.7 | 144.2 | 954.6 | 443.1 | No medido | 21.9 | No medido |
| 28 | 2 | 262.0 | 253.1 | 262.2 | 519.8 | 490.2 | 147.1 | No medido | 23.3 | No medido |
| 29 | 2 | 270.4 | 547.3 | 526.1 | 213.3 | 437.3 | 256.6 | 92.9 | No medido | No medido |
| 30 | 3 | 318.7 | 506.2 | 240.6 | 1002.2 | 353.2 | 259.4 | 43.2 | 202.2 | 30.7 |

| Video | Intervalos operativos observados | Tramo entre inicio y cierre del run | Huecos sin medir |
| --- | ---: | ---: | ---: |
| 26 | 3094.6 | 5272.8 | 2178.2 |
| 27 | 2401.9 | 2402.7 | 0.8 |
| 28 | 1957.6 | 1971.6 | 14.0 |
| 29 | 2344.0 | 2524.7 | 180.7 |
| 30 | 2956.3 | 3163.9 | 207.6 |

Los cinco tramos se solapan y no se suman para obtener la duración del lote. Los huecos no se atribuyen a espera sin evidencia. La auditoría experimental tiene un reloj separado: 1036.737 s de intervalos registrados, según [resumen final](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/AUDIT_TIMING_FINAL_v1.json>). Incluye documentación y sombras; la preparación anterior al primer reloj y tareas entre intervalos permanecen sin medir. No se añade a la duración del lote como si fuera trabajo secuencial.

La semántica de 30 incluye una reparación compartida de alineación para 26/28/30 sin reloj exclusivo: no se carga íntegra a flujo 3 ni se inventa una resta. Recursos de 30 incluyen maqueta y primera autoría; montaje y QA previo incluyen checks y correcciones. Recursos de 29 incluyen coordinación del cierre de 26. QA posterior incluye revisión y documentación, no solo controles técnicos. Las correcciones de 27 quedaron dentro de fases render y QA posterior, sin intervalo exclusivo de reparación.

## Motor y controles técnicos

| Versión | Motor CLI mostrado | Pared de comando cuando medida | Controles técnicos posteriores |
| --- | ---: | ---: | --- |
| 26 v1 | 231,8 s | No separado aquí | Helper 4,101 s; frames 4,026 s; fase post completa 137,461 s |
| 26 v2 | 203,0 s | 205,168 s | Base visual conservada para v3 |
| 26 v3 | No nuevo render visual | 1,291 s, derivado AAC y paridad | Helper 2,950 s; 59 frames 1,620 s; identidad HEVC 0,152 s |
| 27 v1 rechazado | 129,779 s según recibo | No separado aquí | Fondo futuro amarillo; conservado y no entregado |
| 27 v2 | 126,640 s según recibo | No separado aquí | Paridad 2,150 s; 60 muestras y QA técnico exacto |
| 28 v1 | 193,384 s según responsable | No separado aquí | Paridad 2,175 s; 42 muestras; fase post 147,063 s |
| 29 v1 | 171,6 s | No separado aquí | Helper 2,830 s; paridad 1,170 s; frames 2,121 s; post 143,369 s |
| 29 v2 | 161,9 s | Incluida en fase render | Helper 2,153 s; paridad 1,208 s; frames 1,353 s; post 113,191 s |
| 30 v1 | 123,4 s | 125,453 s | Helper 2,467 s; paridad 0,897 s; frames 12,992 s |
| 30 v2 | 127,9 s | 130,619 s | Helper 4,495 s; paridad 1,222 s; frames 10,990 s; post 122,693 s |

Los cuatro segundos renders correctivos suman **619,440 s de motor mostrado**: 203,0 + 126,640 + 161,9 + 127,9. Es trabajo extra medido por correcciones, no duración de lote ni ahorro atribuible a un flujo. El log de 30 v2 aporta pipeline de 127,864 s con mayor precisión; la suma utiliza consistentemente el valor mostrado. Hubo nueve renders visuales completos en total y un derivado de audio; se conservaron los primeros renders que terminaron técnicamente pero fallaron visualmente.

En 26 se cambió el hook ENTRY0002 por ENTRY0003 tras comprobar que 25 ya usaba ENTRY0002 y no cumplía el cooldown. El registro global estaba desactualizado. V3 reutilizó el HEVC de v2 y cambió únicamente AAC: hashes de bitstream, todos los PTS/DTS y metadatos coinciden; guards del candidato final y paridad completa pasaron. No fue un tercer render visual. Este caso elimina un proceso de video innecesario mediante dependencias verificadas; no demuestra ahorro causal de flujo 1/2/3. La rotación real 24–30 quedó verificada por root, sin modificar los originales aprobados.

## Retrabajo, integridad y límites

La sombra detectó tres defectos menores escapados del QA local: flash de fondo negro en 30 v1, y cuerpo gráfico sobre el rostro durante entradas en 29 v1 y 26 v1. Todos se corrigieron y verificaron en nuevas salidas. El responsable de 27 detectó su fondo amarillo futuro durante el QA exacto de v1; v2 lo oculta hasta su estado. En 28 la sombra previa corrigió “qué” y cinco posibles solapes de captions de 10 ms antes del render final. No quedan defectos críticos o menores sin resolver en las muestras revisadas; esto no equivale a revisión humana continua de todos los frames.

Los smokes y checks repetidos se conservaron como costo real: 26 tuvo dos smokes de 39,9/41,1 s; 27 tres de 66,5/14,4/64,3 s; 29 uno de 48,5 s; 30 dos, el primero visualmente fallido. Los errores de comandos sin reloj dedicado permanecen sin duración estimada. 30 registró nueve checks completos y una llamada cancelada adicional. La distinción entre eventos registrados y llamadas reales impide tratar un cero como ausencia: 26 reporta históricamente full_render=3, aunque los procesos acreditan dos CLI visuales y un derivado AAC. El evento tardío del primer render de 26 conservó su hora real de registro, sin retrofechar.

Dos eventos tempranos de 28 apuntaban a index.html y QA_FIDELIDAD_PLANTILLA.md mutables: sus hashes cambiaron y el reporte automático rechazó la integridad. Se preservan eventos y hashes; el reporte automático de 28 no se declara PASS. La calidad del MP4 se sostiene separadamente en recibos, hash final y revisión exacta. En 26 se preservó el ledger histórico restaurando sus bytes y se adoptó asset-ledger-v3.json como versión activa, con recibo de adopción; no se reescribió el evento histórico. Los reportes automáticos de 26, 27, 29 y 30 no certifican QA editorial ni escucha. El [índice manual final](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/EVIDENCE_INDEX_FINAL_v1.json>) fija las evidencias finales estables y no repara el fallo histórico de 28.

La ingesta permanece provisional en lo humano: la claqueta ausente de 27 se adjudicó por contexto, y “su IA” en el hook de 26 requiere confirmación auditiva. No se inventaron marcadores ni se activó limpieza especializada de voz. No se certifican publicación, UI de plataformas, reproducción física o colorimetría.

## Decisión operativa

La organización de flujo 2 y el montaje esencial de flujo 3 resultaron viables con fidelidad y controles comunes. **Aún no se ha demostrado que sean más rápidos ni equivalentes en calidad.** Dos pares aproximados y un clip esencial difieren en duración, plantilla, autor, recursos, estado de caché, coordinación y retrabajo; este conjunto no permite porcentajes causales ni una clasificación fiable de rapidez.

Antes de otro piloto, estabilizar la receta compartida: fondo dentro del child, base explícita persistente para HDR, cuerpo gráfico después del fondo opaco y apagado determinista al salir. El smoke debe incluir captions, huecos, estados futuros y retorno, además de revisar transiciones. Registrar eventos contra copias inmutables. Tras un cambio localizado, comprobar dependencias y estados afectados y verificar el nuevo MP4, evitando duplicar checks completos sin una razón nueva.

Una subprueba posterior con la misma fuente y plantilla permitiría observar organización en condiciones más equivalentes; otro lote nuevo comprobaría su aplicación práctica. No se crea esa prueba ni se cambia el default con este informe.

Datos reutilizables: [CSV final](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/RESULTADOS_FINALES_v1.csv>), [JSON final](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/RESULTADOS_FINALES_v1.json>) e [índice de evidencias](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/execution-v1/EVIDENCE_INDEX_FINAL_v1.json>). Versiones, defectos y borradores anteriores permanecen conservados.
