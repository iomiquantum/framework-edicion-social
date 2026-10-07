# Prompt para entregar grabaciones y comenzar la edición

## Texto corto para pegar en otro chat del mismo proyecto

```text
Lee completamente y aplica:

- Framework-Edicion-Social/README.md
- Framework-Edicion-Social/FLUJO_PRODUCCION_RAPIDA.md
- Framework-Edicion-Social/MATRIZ_PRODUCCION_PRO.md
- Framework-Edicion-Social/INGESTA_MAESTRA.md
- Framework-Edicion-Social/QA_PROFESIONAL.md
- Framework-Edicion-Social/POLITICA_EDITORIAL.md
- Framework-Edicion-Social/MOTOR_APRENDIZAJE.md
- Framework-Edicion-Social/OPERACION_OPTIMIZACION.md
- Framework-Edicion-Social/profiles/creative_preferences.json
- Framework-Edicion-Social/library/catalog.json
- Framework-Edicion-Social/PROMPT_INGESTA_Y_EDICION.md

Los archivos adjuntos o las rutas locales indicadas contienen varios videos y tomas identificados mediante la claqueta verbal MARCADOR. Procesa todo el lote con autonomía, sin detenerte después del análisis y sin hacer preguntas salvo que exista un bloqueo real. Entrega un video final independiente por cada VIDEO aprobado.
```

## Contrato de ejecución

0. Ejecutar `check_recording_preflight.py` sobre cada maestro antes de transcribir. Un hard fail bloquea la ingesta de ese archivo; una advertencia queda documentada y no se convierte silenciosamente en aprobación.
1. Si el metraje está en una ruta local del proyecto, trabajar desde esa ruta y no duplicarlo ni volver a subirlo. Conservar cada original intacto y registrar ruta, datos técnicos y hash.
2. Antes de inspeccionar un maestro, buscar en `00-INGESTA/` su transcripción, `take-map.json` revisado y proxy de `VIDEO-NN`. Si existen y sus hashes coinciden, reutilizarlos: queda prohibido volver a transcribir o recorrer todo el maestro para ese video.
3. Si esos artefactos no existen, realizar una sola ingesta compartida del maestro: escuchar y fijar la pista de audio, transcribir una vez con tiempos por palabra, compilar todos los marcadores, revisar el mapa y crear proxies independientes por video.
4. Detectar los comandos:
   - `MARCADOR. Video N, toma N, inicio.`
   - `MARCADOR. Corregir, corregir. Última frase.`
   - `MARCADOR. Aprobada, aprobada.`
   - `MARCADOR. Descartar, descartar.`
   - `MARCADOR. Fin de sesión.`
5. Crear primero `cut-plan.json` a partir de `templates/cut-plan.json`, ligado al hash del original y de la transcripción. No montar antes de tener rangos verificables.
6. Conservar únicamente tomas con inicio y aprobación inequívocos. Una toma abierta, contradictoria o ambigua nunca se aprueba por inferencia.
7. Si una toma es ambigua, aislarla para revisión, continuar procesando el resto del lote y no bloquear los videos válidos.
7.1. Una corrección parcial no cierra ni descarta la toma. Escuchar la frase completa inmediatamente anterior y la repetición que empieza después del marcador; retirar la versión equivocada y todo el marcador, conservar la versión nueva y el contexto previo. Verificar por audio y significado los cuatro límites, registrar `target_range` y `replacement_range` en el `take-map`, cambiar la corrección a `resolved` y copiar la operación a `cut-plan.json`. No inferir el inicio del corte únicamente desde la puntuación del ASR. Si hay correcciones consecutivas, cada repetición verificada sustituye al intento inmediatamente anterior. La toma sigue necesitando un marcador final de aprobación.
8. Verificar por escucha los límites de los fonemas de la toma seleccionada; no volver a transcribir el archivo maestro si ya existe la transcripción compartida válida.
9. Ejecutar el preflight en etapa `edit`. Cualquier activo rechazado, faltante, alterado o de procedencia desconocida bloquea el montaje hasta corregirse.
10. Eliminar la claqueta y la espera posterior. Entrar de forma predeterminada 4 fotogramas antes del primer fonema; adaptar entre 2–6, o 6–12 cuando una mirada, respiración o gesto prepare la frase. Un segundo completo solo se conserva por intención expresiva documentada.
11. Clasificar cada espacio entre frases como silencio muerto, respiración natural, pausa entre ideas relacionadas, cambio de idea/énfasis o pausa dramática. Retirar dudas y esperas; comprimir sin eliminar la cadencia humana; conservar las pausas semánticas.
12. No cortar fonemas, sílabas finales, respiraciones emocionales ni gestos significativos. Usar microfundidos de voz de 10–33 ms y room tone compatible cuando haga falta; nunca ocultar un mal empalme solapando palabras.
13. Conservar normalmente 4–8 fotogramas tras el último fonema y 10–20 cuando deba terminar un gesto o reacción.
14. La toma aprobada y su transcripción sustituyen al guion provisional como fuente editorial.
15. Comparar el audio real con `Preproduccion-Recursos/VIDEO-NN/PLAN_RECURSOS.md` y su manifiesto cuando existan.
16. Retirar recursos que ya no correspondan, reutilizar primero lo aprobado y generar únicamente lo añadido durante la improvisación.
17. No utilizar activos con `user_approval_status: explicit_rejected`, `reuse_status: ineligible`, `reuse.policy: do_not_reuse` o `status: deprecated`.
18. Congelar los recursos elegidos en `asset-lock.json`; un cambio posterior de hash o estado obliga a repetir el preflight.
18.1 Crear `creative-blueprint.json` desde la toma aprobada y puntuar `styles/catalog.json` con `score_style.py`. Una abstención exige decisión editorial; no autoriza a forzar el estilo líder.
18.2 Crear `dependency-map.json` y la clave de caché de fuente, transcripción, cut-plan, estilo, activos y mezcla. Antes de rehacer trabajo, calcular el impacto transitivo del cambio.
18.3 Construir o refrescar una sola vez el índice semántico del lote. Consultarlo por beat y compilar hasta tres recetas contextuales desde blueprint, contrato, ledger e índice completos. La selección final es humana; cuando exista, guardarla en `creative-attribution.json` contra el plan exacto. Sin selección explícita, mantener propuestas pendientes o abstención. La fatiga y el orden de candidatos no son una nota de calidad.
19. Montar cada video por capas: fuente, cortes, cámara, corrección, voz, captions, evidencia, imágenes, iconos, motion, música y SFX.
20. Proteger ojos, boca, gestos y captions. Priorizar espacio negativo y usar cutaways completos únicamente cuando aporten significado.
21. Aplicar zooms, transiciones y SFX perceptibles pero semánticos. Los SFX aprobados parten de ganancia conservadora y nunca compiten con la voz.
22. Recalcular captions después de cerrar los cortes de voz. Revisar cada empalme con audio y también sin audio para detectar saltos gestuales.
23. Trabajar con previews y renders de segmento; reservar el render completo de calidad para después del bloqueo editorial interno.
23.1 Después de cada render revisable, generar `review-packet.json` y `review.html` con render, manifest, dependency-map, blueprint y cambios ligados por hash. Aplicar correcciones por rango/capa/elemento y volver a codificar el archivo completo solo para QA final o entrega.
24. Crear o reutilizar un `production-board.json`, reclamar cada `VIDEO-NN` con un único owner y limitar inicialmente a dos los procesos pesados simultáneos. El montaje creativo puede continuar en paralelo en carpetas exclusivas.
25. Renderizar la entrega desde los rangos exactos del MOV original; el proxy nunca es la fuente del master final.
26. Si la composición conserva HDR, producir primero un mezzanine editorial conforme a `MASTER-PROFILE-EDITORIAL-HDR-001`; no declararlo archivo social listo. El máster neutral de publicación se genera después de aprobar ese hash y debe cumplir `MASTER-PROFILE-SOCIAL-SDR-001`: 1080 × 1920, 30 fps, H.264/AAC 48 kHz y BT.709.
27. Ejecutar el preflight en etapa `render --deep` y completar un `qa-scorecard.json` para el archivo candidato exacto. Cualquier hard fail o hard gate requerido sin ejecutar bloquea la entrega.
28. Validar rostro, captions, sincronía, mezcla, picos, inicio, final, CTA, fuentes y archivo final. Reproducirlo completo con audífonos, altavoz y pantalla de teléfono.
29. Entregar por cada video:
   - MP4 final.
   - Proyecto editable por capas.
   - Transcripción utilizada.
   - `take-map`/rango fuente, `cut-plan`, `asset-lock`, manifiesto de recursos y manifiesto de render.
   - `creative-recipe-plan.json`, `creative-attribution.json` solo si hubo selección humana explícita y consola de revisión hash-bound.
   - Scorecard de QA con evidencia y firma editorial.
   - Recibo de aprobación `pending` preparado contra el hash exacto, sin inferir aprobación.
   - Fingerprint descriptivo y reporte de conformidad/variedad cuando el proyecto pertenezca a una serie.
   - `platform-master.json` en estado `pending`, sin derivados hasta la aprobación explícita.
   - Resumen breve de decisiones, recursos reutilizados y excepciones.
30. Actualizar las métricas de producción para medir tiempo, reutilización, rondas, renders y causas de retrabajo.
31. Tras la aprobación explícita, sellar el recibo del archivo exacto, registrar el golden master y actualizar el ledger de serie. La aprobación del video no promueve automáticamente su plantilla.
31.1 Registrar en `asset-usage-history.json` únicamente los recursos que sobrevivieron al artefacto aprobado; las asignaciones provisionales no cuentan como uso.
32. Si el aprobado es HDR, generar y revisar el máster social SDR ligado a ese recibo. Después aplicar `PROMPT_DERIVADOS_PLATAFORMA.md`; conservar contenido y producir Reels/TikTok/Shorts por delta mediante content lock y paquete verificable.
33. Registrar evidencia para el motor de aprendizaje. Las métricas solo se ingieren después de registrar paquete, target, MP4 real, delivery-check, evidencia local de publicación, atribución creativa y evidencia de la captura en una ventana válida. Los hashes prueban integridad local, no autenticidad remota. El motor solo recomienda; una persona decide defaults, familias y alcance.

## Regla de nombres

```text
Lote-AAAA-MM-DD/
├── VIDEO-01-tema/
├── VIDEO-02-tema/
├── VIDEO-03-tema/
└── RESUMEN-LOTE.md
```

El número `VIDEO-NN` proviene de la claqueta verbal y debe coincidir con los recursos provisionales. El número de toma solo identifica intentos de grabación y no cambia el conjunto semántico de recursos.

Para metraje local grande, colocar los originales en `00-INGESTA/`. Un lote puede dividirse por tamaño, por ejemplo:

```text
00-INGESTA/
├── LOTE-VIDEOS-01-05-ORIGINAL.MOV
└── LOTE-VIDEOS-06-10-ORIGINAL.MOV
```

Un mismo archivo puede producir varios videos. Nunca asumir que un archivo equivale a una sola salida.

## Limpieza de voz obligatoria

Antes de normalizar y mezclar, aplicar `AUDIO_LIMPIEZA_VOZ.md`: revisar ruido y sonidos ajenos, reducirlos cuando corresponda, comparar con el original y preservar la voz natural. Una prueba técnica no sustituye evidencia de escucha ni fidelidad.

## Guiones y grabación — prioridad confirmada 2026-09-30

Los guiones son referencias de estructura y preparación de recursos. Los marcadores de grabación determinan tomas, repeticiones y correcciones; la voz real de la toma seleccionada determina montaje y subtítulos, incluidas improvisaciones. No inventar marcadores ni completar palabras ausentes con el guion. Un guion nuevo se contrasta con la ingesta compartida existente, sin repetir el análisis del maestro por video.
