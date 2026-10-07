# Reglas operativas de la serie

## Gate obligatorio de ingesta por lote

Antes de editar cualquier `VIDEO-NN` perteneciente a un archivo grabado por lote:

1. Identificar el rango completo del lote, por ejemplo `16–20`.
2. Ejecutar una sola vez la ingesta maestra completa: preflight técnico, selección de pista por escucha, transcripción única, revisión de todos los marcadores y correcciones, proxies y rangos fuente.
3. Ejecutar:

   ```bash
   python3 scripts/validar_lote_listo.py --desde 16 --hasta 20 --write-lock
   ```

4. No comenzar la edición individual si el comando falla o si no existe el recibo `00-INGESTA/ingest-ready-16-20.json` ligado al hash actual del take-map.
5. Un fallo de ingesta se corrige una sola vez en `00-INGESTA`; está prohibido recorrer o transcribir el maestro completo desde una tarea individual.
6. La tarea individual solo puede usar el proxy y `VIDEO-NN/source/*-source-range.json` para localizar la toma. El render final debe conservar el vínculo con el original.

La existencia de un `candidate_range` aproximado no sustituye este gate. Deben estar resueltas por escucha todas las correcciones y `qa.human_review_completed` debe ser `true`.

## Gate obligatorio antes de pedir aprobación

Ningún video puede presentarse al usuario como “listo para revisar” sin completar y documentar las tres pasadas de `ESTANDAR_QA_PREAPROBACION.md`:

1. Revisión visual/editorial completa.
2. Revisión de audio y ritmo completa.
3. Revisión integral final de principio a fin.

Además:

- Toda pausa detectada mayor a 1,25 s debe revisarse y justificarse o recortarse; no se permiten colas mudas accidentales.
- Todo texto debe ser semántico, legible en móvil, aprovechar el ancho seguro y respetar rostro/cabeza. No se aceptan etiquetas decorativas sin función narrativa.
- Los rótulos visibles de plantillas describen el contenido de la voz real, nunca la estructura narrativa. No mostrar «la pregunta», «el contraste», «el ejemplo», «la idea», «tu experiencia», hook o cierre como nombres de etapas. Una numeración solo se conserva como navegación temática útil; los nombres técnicos de beats quedan en archivos y notas internas. Revisar todos los rótulos y avisos siguientes antes de renderizar.
- Si queda espacio vertical útil, distribuir los módulos con respiración visible en lugar de pegarlos al borde superior; como referencia, mantener 24–32 px entre cajas independientes.
- Las líneas y rieles decorativos nunca atraviesan letras ni compiten con el área tipográfica; deben quedar debajo o fuera del bloque de texto con separación visible.
- En captions con varios nodos o estilos, usar separación CSS explícita y comprobar que ninguna palabra quede concatenada con la siguiente.
- Los recursos de apoyo a pantalla completa se usan como acentos breves. Como referencia, se mantienen 1,5–2,5 s y luego se regresa al presentador para conservar autoridad y atención; cualquier permanencia mayor debe justificarse por la narración.
- Videos consecutivos no deben compartir sin intención la misma combinación dominante de composición, cajas, sombras y tipografía.
- Los SFX deben acompañar hitos semánticos y ser perceptibles en la mezcla, sin tapar la voz. Como punto de partida para piezas de 20–30 s se buscan 3–5 acentos distintos por función, no por palabra.
- Si no existe evidencia de escucha humana, se registra `por confirmar`; nunca se afirma que el video fue escuchado.
- Un `hyperframes check` aprobado no reemplaza estas tres pasadas ni una inspección estética.

## Limpieza de voz en VIDEO-16–20 y próximas ediciones

Por instrucción explícita del usuario el 2026-09-30, aplicar `../Framework-Edicion-Social/AUDIO_LIMPIEZA_VOZ.md`: revisar voz aislada antes de mezclar, suprimir ruido ajeno cuando exista, conservar original y comparar A/B sin perder timbre, fonemas ni respiración. Registrar bypass si no hace falta. Conservar parámetros/hashes y verificar latencia/sincronía; ninguna métrica sustituye evidencia de escucha.

## Control temprano de transcripción

Inmediatamente después del ASR compartido y antes de crear mapas o captions, ejecutar `scripts/validar_transcripcion_ingesta.py --transcript RUTA --duration SEGUNDOS --desde NN --hasta NN`, conservar informe y hash de la transcripción. Un `fail` obliga a resolver los hallazgos en ingesta, mediante reparación dirigida o adjudicación humana documentada; no sirve para montar ni alinear captions finales. `pass` o `warn` tampoco sustituyen selección por escucha ni el recibo de `validar_lote_listo.py`. El control nunca aprueba una toma.

## Excepción autorizada — avance sin escucha directa — 2026-09-30

El usuario indicó: «Correcto no debes bloquearte debes buscar soluciones y seguir». Para este lote y las próximas tareas con la misma limitación, se permite transcripción, análisis y montaje provisional basados en evidencia automática aunque falte escucha humana. Esta excepción sustituye la prohibición de iniciar trabajo útil únicamente por `pending_listen` o `qa.human_review_completed: false`.

- Mantener `human_review_completed: false` y registrar escucha/naturalidad como `por confirmar`. No falsear el gate estricto ni su recibo.
- Registrar pista, hashes, transcripción, rangos, marcadores y correcciones con evidencia; un mapa ambiguo se afina antes de usar su tramo.
- Guardar un recibo distinto `ingest-provisional-XX-YY.json` que declare límites y no autorice publicación ni entrega aprobada.
- Revisar ruido, empalmes y captions con ASR/señal/inspección visual; separar pruebas técnicas de juicio auditivo.
- Continuar con el editable y preview, conservar el original y solicitar revisión humana solo sobre un resultado concreto si todavía es necesaria.

La exigencia histórica de escucha no se borra: sigue vigente para afirmar escucha realizada o declarar una entrega auditivamente verificada.

## Guiones y grabación — prioridad confirmada 2026-09-30

Los guiones son referencias de estructura y preparación de recursos. Los marcadores de grabación determinan tomas, repeticiones y correcciones; la voz real de la toma seleccionada determina montaje y subtítulos, incluidas improvisaciones. No inventar marcadores ni completar palabras ausentes con el guion. Un guion nuevo se contrasta con la ingesta compartida existente, sin repetir el análisis del maestro por video.

### Gate de texto visible obligatorio — corrección21/22, 2026-09-30

Antes de toda captura de render, ejecutar `Framework-Edicion-Social/scripts/validar_texto_visible.py --project RUTA_EDITABLE --report RUTA_QA_NUEVA.json`. Un resultado `fail` detiene el render: corregir las etiquetas, no omitir el comando ni desactivar el guard. Los wrappers `media-runtime.mjs` de21/22 lo ejecutan automáticamente y fallan si no pueden comprobarlo. Las siguientes ediciones deben incorporar el mismo gate en su entrada de render; no invocar el render por fuera del wrapper para eludirlo.

El informe recorre HTML/subcomposiciones activas y conserva hashes e inventario del texto. Bloquea etiquetas conocidas de producción, incluidas formas numeradas y «SIGUE: UN EJEMPLO». No inspecciona IDs ni nombres de archivos; los captions de voz se distinguen de la navegación editorial. Esta lista no cubre toda forma posible de estructura narrativa: sigue siendo obligatorio leer e inspeccionar visualmente cada rótulo, titular y aviso de contenido. La plantilla define el diseño; no autoriza mostrar el nombre de sus beats.

## Imágenes según contexto — instrucción global 2026-09-30

Aplicar `../Framework-Edicion-Social/IMAGENES_CONTEXTO_REALISMO.md`. Inspeccionar cada recurso contra la frase real; si no encaja o resulta genérico, preferir generar una imagen específica con acabado fotográfico natural, distinta por su escena y microacción. Banco como alternativa pertinente. Verificar manos/anatomía/miradas, luz/perspectiva, objetos/pantallas y encuadre real. Registrar prompt/fuente/hashes; no prometer indetectabilidad/exclusividad ni presentar generación como caso real. La regla global no aprueba por sí sola una imagen o render.
