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

## Revisión y limpieza de voz — únicamente a solicitud, 2026-09-30

Solo cuando el usuario pida explícitamente revisar la voz/el audio o eliminar ruido de fondo, aplicar `../Framework-Edicion-Social/AUDIO_LIMPIEZA_VOZ.md` y la skill `revisar-limpiar-voz` en `/Users/iomijhondavid/.codex/skills/revisar-limpiar-voz/SKILL.md`. Una edición normal, render o QA habitual no activa diagnóstico especializado, nuevas limpiezas, pruebas de motores ni bypass/A-B obligatorios. Dentro de la revisión solicitada, sugerir tratamientos adicionales si se detectan eses molestas, golpes de aire, clics, eco u otros defectos; no aplicarlos automáticamente. Conservar original, recetas, hashes y QA del audio que sí se cambie. Esta instrucción sustituye el alcance general previo; no revierte medios ya procesados ni las reglas habituales de mezcla, ritmo, SFX y sincronía.

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


## Subtítulos según contexto — próximas ediciones — 2026-09-30

Aplicar `../Framework-Edicion-Social/SUBTITULOS_CONTEXTO_Y_LECTURA.md` y `captions/catalog.json`; documentar la elección con `templates/caption-decision.json` dentro de cada VIDEO-NN. Estilo y ubicación son decisiones independientes. Conservar frase fiel, una o dos líneas reales, posición predecible, lectura móvil/sin sonido y énfasis selectivo. Proteger rostro, manos y acción; revisar toda la caja con UI real de Instagram, Facebook y TikTok cuando se declaren listos esos destinos. Sin preview, mantener destino pendiente y continuar candidato editorial local sin certificarlo. Los valores de fuente/CPS son presets revisables, no hard fails automáticos. Reutilizar ASR/timing compartidos; este cambio no autoriza modificar exportaciones ya aprobadas.

## SFX distintos e integración del apoyo — 2026-09-30

En videos de20–30s usar como mínimo dos sonidos de efecto distintos, perceptibles y con función editorial. Repetir un único archivo en varios momentos no cumple este mínimo. La referencia de3–5eventos sigue vigente: distinguir número de eventos de identidades sonoras. Respetar biblioteca aprobada, rotación/cooldown y voz real; ajustar por contexto sin saturar ni tapar palabras. Comprobar mezcla, picos y audibilidad; una medida no prueba escucha humana.

Aplicar el apartado de formato de `../Framework-Edicion-Social/IMAGENES_CONTEXTO_REALISMO.md`: apoyo en la caja exacta del presentador o vertical a pantalla completa, según qué comunique mejor en cada video. Evitar portrait estrecho montado por defecto dentro de cuadro ancho; generar con geometría destino antes de maquetar.


## Dirección de audio y hook — regla permanente VIDEO23, 2026-09-30

Aplicar `Framework-Edicion-Social/AUDIO_DIRECCION_Y_PROSODIA.md` (ruta desde raíz del proyecto). Antes de elegir música/SFX, analizar voz real por intensidad/contrastes, pitch/entonación estimados, pausas, ritmo y cambios por frase; ligar interpretación a palabras/contexto y separar inferencia de escucha. Reutilizar ASR y voz intactos. Comparar aumento de nivel, ubicación o carácter cuando un efecto no se perciba. **Todo hook inicial lleva SFX integrado y debe comprobarse en QA**, además del mínimo dos identidades distintas para20–30s. Registrar niveles contra voz, picos/masking y reproducción real; ausencia de hook/vínculos inválidos bloquea render mediante verificación equivalente a `scripts/revisar_presencia_sfx.py`. Medición no certifica audibilidad ni emociones; mantener escucha por confirmar si falta.

## Solicitud acotada al lote16–20 — RNNoise — 2026-09-30

El usuario autorizó expresamente RNNoise para los videos16–20 del mismo original. Consultar `00-INGESTA/voice-cleanup-request-16-20-rnnoise.json`; aplicar ese único motor a voz original48k con contexto antes de cortes y conservar versiones. Esto no modifica la activación a solicitud fuera de este lote ni autoriza otros procesos de restauración.

Para la entrega16/18/19 autorizó agentes en paralelo con render local revisable, sin nuevas consultas. Repartir responsables por video; preparación y QA independientes pueden solaparse, procesos pesados respetan `production-board.json` y propiedad exclusiva. Usar cachés y medir tiempos/cola; no convertir pruebas incomparables en un porcentaje de ahorro.
