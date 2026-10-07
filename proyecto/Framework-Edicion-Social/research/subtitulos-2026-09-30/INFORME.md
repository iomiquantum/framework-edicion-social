# Investigación y auditoría de subtítulos — 2026-09-30

## Encargo y conclusión

El usuario pidió investigar ubicación y estilos de subtítulos para Instagram/Facebook Reels y TikTok, pensando también en quienes ven sin audio; amplió la revisión a exportaciones previas para fijar reglas de las próximas ediciones.

Conviene dar mayor presencia a la lectura y diseñar su ubicación desde el encuadre. No hay fundamento para imponer el centro geométrico ni palabras sueltas a todas las piezas. Se adopta un proceso común de cobertura, legibilidad y verificación, con cuatro estilos y tres ubicaciones contextuales. Los valores de tamaño/CPS son presets internos revisables.

## Muestra y método

- 18 videos distintos: 01–16, 21 y 22; la elección exacta de archivo y su SHA-256 están en `export-audit.json`.
- Tres estados seleccionados por video, 54 fotogramas decodificados del MP4 y 18 hojas de contacto inspeccionadas visualmente por el modelo. No fue reproducción completa, escucha ni revisión humana.
- 189 cues extraídos de editables actuales: texto, tiempos, CPS y CSS base/overrides. No se acredita igualdad entre cada editable actual y el origen histórico del export sin recibo. El01 exige considerar su override Instagram; no confundir CSS base con geometría final.
- Conversión de HDR a una vista SDR para observar composición cuando corresponde; no certificación de color HDR.
- Exportaciones verificadas por hash antes/después y conservadas intactas. El16v4 tiene aprobación editorial explícita previa; esta auditoría no revoca esa aprobación ni certifica la interfaz de todos sus destinos. El22 se congeló según su puntero vigente al inicio; otra tarea puede generar versiones posteriores.
- No se abrió ninguna interfaz real de publicación. “Riesgo de UI” es inferencia basada en perfiles internos y guía primaria, no evidencia de un botón tapando texto en pantalla.

## Qué aprendemos de las familias

01 tiene una adaptación de plataforma con caption más alto que su CSS base, pero fuente pequeña. 02–10 muestran repetidamente bandas inferiores con letras relativamente pequeñas frente a titulares grandes; no conviene perpetuar esa jerarquía. 11–15 elevan el texto y aumentan su presencia, con14 como referente útil de tamaño, no como default aprobado de todo el catálogo. El12 ilustra que un CPS razonable no evita que aparezcan tres líneas.

16 ofrece separación editorial limpia; la placa original del carril está en x108/y1592/w864/h132 y puede entrar en el espacio usado por interfaces inferiores. Una mejora futura requiere redistribuir el carril y el encuadre, preservando rostro/manos. 21–22 tienen letra más grande, pero una segunda línea aumenta la altura real de caja: comprobar solo su coordenada superior no basta.

Las fronteras tipográficas observadas en09/10 (“seguir?¿Alguien” y “resuelto.¿Qué”) refuerzan el control ya existente de espacios entre nodos y puntuación en el MP4. Se documenta el aprendizaje sin editar esos archivos.

## Inventario revisado

Máximo CPS y conteo sobre20 corresponden al editable inspeccionado, con espacios/puntuación. Son avisos para revisión, no fallos automáticos ni métricas de comprensión. Pulsar el video abre su hoja de tres muestras.

| Video | Cues | Máx. CPS | Sobre20 | Observación en las muestras |
| --- | ---: | ---: | ---: | --- |
| [VIDEO-01](VIDEO-01/contact-sheet.png) | 12 | 22.1 | 3 | Derivado Instagram con override de plataforma: texto sobre pecho/parte baja. No atribuir bottom255 o fuente49 del CSS base al MP4: override43 y zona variable. Frase con énfasis útil; relativamente pequeña a tamaño móvil. |
| [VIDEO-02](VIDEO-02/contact-sheet.png) | 10 | 23.0 | 1 | Frase y acento legibles en la muestra, pero letra pequeña y franja muy baja; alto titular compite con lectura. Riesgo de UI inferido, sin captura real de plataforma. |
| [VIDEO-03](VIDEO-03/contact-sheet.png) | 8 | 20.9 | 1 | Bloques completos y contraste; ubicación baja y fuente48 del editable. Revisar ancho derecho y carga del titular en siguientes plantillas. |
| [VIDEO-04](VIDEO-04/contact-sheet.png) | 7 | 22.0 | 1 | Diagrama y caption simultáneos requieren repartir lectura. Franja baja de tamaño48; no repetir esta posición como default. |
| [VIDEO-05](VIDEO-05/contact-sheet.png) | 8 | 23.6 | 2 | Énfasis semántico existente es reutilizable; fuente48 y caja inferior deben ganar presencia móvil y espacio útil. |
| [VIDEO-06](VIDEO-06/contact-sheet.png) | 10 | 20.4 | 1 | Fuente45 y banda baja; la jerarquía favorece mucho el titular. Mantener cobertura y redistribuir peso tipográfico en futuras ediciones. |
| [VIDEO-07](VIDEO-07/contact-sheet.png) | 10 | 19.1 | 0 | Frases relativamente concisas y palabras destacadas útiles. La banda pequeña/baja sigue siendo una referencia débil para UI móvil. |
| [VIDEO-08](VIDEO-08/contact-sheet.png) | 10 | 21.2 | 2 | Frase completa con acento útil; tamaño45 y ubicación baja frente al gran titular. Mejorar jerarquía de lectura. |
| [VIDEO-09](VIDEO-09/contact-sheet.png) | 11 | 19.8 | 0 | Captions bajos. En la muestra se observa unión de frontera de pregunta “seguir?¿Alguien”; comprobar separación entre nodos y puntuación en QA futuro. |
| [VIDEO-10](VIDEO-10/contact-sheet.png) | 11 | 23.4 | 2 | Franja baja con letra45. Se observa frontera “resuelto.¿Qué”; incorporar separación tipográfica explícita y revisión del texto ya renderizado. |
| [VIDEO-11](VIDEO-11/contact-sheet.png) | 10 | 18.9 | 0 | Referencia más fuerte: letra52/peso alto y caption elevado sobre pecho/espacio libre. El ancho casi completo requiere contrastar con UI derecha. |
| [VIDEO-12](VIDEO-12/contact-sheet.png) | 7 | 19.8 | 0 | Mejor tamaño/posición que familias anteriores, pero la muestra de 7,2s muestra tres líneas. El CPS por sí solo no detecta ese problema. |
| [VIDEO-13](VIDEO-13/contact-sheet.png) | 7 | 22.0 | 1 | Letra52–58 con énfasis visible; captions cerca del pecho. Revisar competencia con diagrama y extremo derecho de la caja. |
| [VIDEO-14](VIDEO-14/contact-sheet.png) | 10 | 22.6 | 2 | Letra60–64 y lectura más presente: buen referente visual. Titulares/quotes adicionales deben limitarse según carga y UI. |
| [VIDEO-15](VIDEO-15/contact-sheet.png) | 6 | 22.3 | 1 | Buena presencia y contraste con letra54–60; caption elevado. Conservar lectura clara y comprobar caja completa/UI por destino. |
| [VIDEO-16](VIDEO-16/contact-sheet.png) | 22 | 24.6 | 10 | v4 editorialmente aprobado: carril limpio, separado de rostro/gestos, pero placa y1592–1724 está muy abajo. Mejorar diseño del carril en videos futuros; no mover texto ciegamente sobre las manos. UI real no certificada aquí. |
| [VIDEO-21](VIDEO-21/contact-sheet.png) | 14 | 22.8 | 2 | Letra58 y carril elevado; buena base. Top1400 y alto de dos líneas pueden acercarse a interfaz inferior; cara está alta en esta toma: reflujo antes de subir indiscriminadamente. |
| [VIDEO-22](VIDEO-22/contact-sheet.png) | 16 | 26.5 | 2 | Archivo congelado en esta auditoría, no promesa de última versión permanente. Letra62 y top1380: presencia clara, pero revisar altura de dos líneas e interfaz inferior. Primer cue de0,49s merece reagruparse en futuras decisiones. |

31 de189 cues superan20 CPS en esta extracción. Diez están en16, donde hay22 bloques cortos; es un candidato a revisar agrupación en siguientes ediciones, sin concluir que todo cue rápido es ilegible. La revisión móvil, el contexto y la sincronía deciden.

![Comparación de seis exportaciones](COMPARACION_6_EXPORTACIONES.png)

## Investigación actual y diferencias de alcance

La especificación TikTok consultada está actualizada a junio2026. La revisión académica CHI2026 reúne36 trabajos de2015–2025; se verificó su resumen primario. El experimento de2024 sobre ausencia de audio incluye168 participantes y material inglés: apoya reducir esfuerzo de lectura, pero no compara nuestros formatos ni promete retención.

El PDF primario CHI2024 está archivado con hash. Analiza300 TikToks recogidos enabril2023 y nueve entrevistas:83,3% de la muestra usó bloques de pocas líneas que se reemplazaban, mientras5% usó una o pocas palabras rápidas. Eso describe esa muestra histórica, no prevalencia actual ni eficacia. Consistencia y tiempo para leer guían nuestra adaptación.

La disponibilidad actual de resaltados/dinámica en CapCut muestra opciones de producción; no demuestra que un estilo sea la tendencia dominante ni el más eficaz. No se hizo muestreo representativo del feed2026 ni estudio de nuestra audiencia. Se catalogan formatos contemporáneos disponibles sin atribuirles superioridad por moda.

La referencia de lectura Netflix y la guía Meta corresponden a entregas profesionales y anuncios, respectivamente. El35% inferior de la guía Meta no se aplica como requisito orgánico universal. No trasladar los5–10 words/sec de overlays publicitarios deTikTok a captions fieles de voz. Las páginas actuales deMeta Ads Guide con login no se pudieron comprobar directamente; se conserva esta limitación.

## Fuentes primarias consultadas

Consulta local:2026-09-30. “Fecha no verificada” no equivale a publicación reciente. Notas estructuradas, alcance y acceso: `source-notes.json`.

| ID | Fuente | Fecha de publicación/actualización | Límite |
| --- | --- | --- | --- |
| CAP_TIKTOK_SAFE_ZONE_2026 | [TikTok for Business](https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads) | June 2026 | Guía de anuncios; no fija un y universal para subtítulos orgánicos. Preview no específico del dispositivo. |
| CAP_META_REELS_ADS_GUIDE | [Meta, documento de autor alojado por organizador de evento](https://d3m889aznlr23d.cloudfront.net/img/events/458925814/assets/e042d2be.reels_ads_guide1.pdf) | Fecha de edición no declarada; estudios citados 2021–2023 | No certifica interfaz orgánica de 2026. Ads Guide actual bloqueada por login. No trasladar CTR/CPA a efecto causal de captions. |
| CAP_SOUND_OFF_PLOS2024 | [Autores / University of East Anglia / PLOS ONE](https://ueaeprints.uea.ac.uk/id/eprint/96946/) | 2024-10-07 | No compara nuestros tamaños, posición ni Reels españoles; no estima porcentaje de usuarios actuales sin sonido. |
| CAP_TIKTOK_ACCESSIBILITY_CHI2024 | [McDonnell y coautores / ACM CHI / Makeability Lab](https://makeabilitylab.cs.washington.edu/media/publications/McDonnell_CaptionItInAnAccessibleWayThatIsAlsoEnjoyableCharacterizingUserDrivenCaptioningPracticesOnTiktok_CHI2024.pdf) | CHI 2024, May 11–16; TikToks collected April 2023 | Muestra situada; no tendencia de frecuencia en 2026 ni prueba causal de retención. |
| CAP_SOCIAL_REVIEW_CHI2026 | [Nguyen y coautores / ACM CHI / SInC Lab](https://sinc-lab.com/publications/2026-04-13-nguyen2026like) | 2026-04-13 | Se verificó resumen primario; no atribuir al artículo una posición o tipografía ganadora. |
| CAP_NETFLIX_SPANISH_READING | [Netflix Partner Help Center](https://partnerhelp.netflixstudios.com/hc/en-us/articles/217349997-Spanish-Latin-America-Spain-Timed-Text-Style-Guide) | Fecha de edición no verificada | Especificación Netflix, no requisito de redes ni permiso para omitir palabras de nuestra voz. |
| CAP_W3C_SEMANTIC_COVERAGE | [W3C WAI](https://www.w3.org/WAI/media/av/captions/) | Fecha de edición no verificada | Aplicar principios no acredita conformidad integral WCAG del video. |
| CAP_W3C_CONTRAST | [W3C WAI](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | WCAG 2.2, página consultada en 2026 | Escala física del teléfono y fondo variable deben revisarse; px fuente no implica texto grande WCAG. |
| CAP_TIKTOK_CREATIVE_GUIDE | [TikTok for Business](https://ads.tiktok.com/resources/help/article/creative-best-practices?lang=en) | June 2025 | Los 5–10 words/sec del texto publicitario no se adoptan como velocidad de lectura de subtítulos de voz. |
| CAP_CAPCUT_AVAILABLE_FORMATS | [CapCut](https://www.capcut.com/resource/types-of-captions) | Fecha de edición no verificada | La oferta de una herramienta no mide moda, preferencia ni eficacia independiente. |

## Aplicación y optimización

El protocolo operativo es `../../SUBTITULOS_CONTEXTO_Y_LECTURA.md`; el catálogo separa estilo de ubicación. La elección se documenta con `templates/caption-decision.json`, sin imponer una plantilla única ni fingir un selector automático.

Se reutilizan transcripción/timing y la memoria de este muestreo. Cada nuevo video conserva su QA propio: cue más largo/rápido, dos líneas reales, rostro/gestos y destino. No repetir la inspección de todos los exports ni el maestro completo por cada edición. Un cambio solo de color no exige rehacer alineación; un reflujo de caja sí exige revisar wrapping, colisiones y MP4 nuevo.

Los previews parciales permiten corregir antes del render largo. Su ahorro total todavía no se midió. La comparación sin sonido, el review a tamaño móvil y el preview real por plataforma deben registrarse con alcance y evidencia; la hoja de contacto no los sustituye.

## Pendiente y límites

Por confirmar: preferencia del público de la cuenta, rendimiento por formato, test de usuarios en móvil y previews reales deInstagram/Facebook/TikTok con descripción/CTA. Estos pendientes no impiden definir y usar los criterios editoriales en nuevos candidatos locales. Sin evidencia de destino no declarar una entrega certificada para esa plataforma. No se solicitaron publicación ni reedición de archivos aprobados.
