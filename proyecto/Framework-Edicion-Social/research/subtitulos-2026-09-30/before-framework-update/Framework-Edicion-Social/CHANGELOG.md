# Changelog

## VIDEO-21 provisional y lote compartido21–25 — 2026-09-30

- Ingesta reparada por50 ventanas:5 tomas,17 marcadores y6 correcciones provisionales; cinco proxies HLG con decode/hash verificados. No existe recibo estricto ni escucha ficticia.
- Candidato21 de21,633 s: T21 Ruta de foco, captions14, apoyo1,9 s, tres acentos y voz48k con denoise suave, A/B y25 ms compensados.
- Corregidos fallos reales de dependencia x265, títulos persistentes, cobertura del encabezado y captions; archivos anteriores conservados. Runtime privado auténtico216; ninguna atribución a otro chat ni cambios globales realizados por esta tarea.
- Check52 muestras PASS; MP4v2 decode/hash/mezcla PASS y72 fotogramas reales inspeccionados. Naturalidad y aprobación pendientes. Métricas separan todos los intentos y no afirman ahorro global.
- Regla confirmada: guiones referenciales; marcadores seleccionan y voz real gobierna montaje/subtítulos. Mejora operativa, QA_REVISION, manifest y métricas actualizados.

## Mejora continua y medición aplicada — 2026-09-30

- MEJORA_CONTINUA.md fija prioridades con evidencia, revisión por delta y cierre por video/cinco; los documentos16/21/OPERACION aplican excepción provisional vigente.
- Medidor medir_proceso.py conserva intentos/logs/hash/exit code y distingue suma de comandos/solapes; cinco pruebas PASS. Usado en lint/check16, sin sustituir métricas completas, QA ni aprobación.
- VIDEO-16 provisional: SDR gestionado, voz48k, captionsDTW y montaje; rutas/entrada duplicada corregidas antes de render. Check estricto PASS9,678s; QA audiovisual completo aún pendiente.
- FFmpegfull9.0.2 añade zscale; dependencia x265 alteró binario8 y se restauró enlace a librería preservada. Versión y decode corto del8 PASS. No se afirma aceleración.

## Paquete de escucha y benchmark acotado — 2026-09-30

- Paquete ingesta16–20: cinco candidatos +tres dudas originales,223,07s/64,97MB; ocho decode/probe/hashes verificados, HEVCMain10HLG720×1280/AAC48k. Escucha/selección humana pendientes; no es edición final.
- Recuento confirmado:24bloques retenidos, corrige el resumen previo de25. Se conserva su antecedente en la bitácora; propuesta/outputs sin omisiones.
- Captura agrupada vs6seeks sobreVIDEO15: PNG/PTS equivalentes, tres pares, mediana1,765→0,977s/44,64% menos únicamente en esa fase/muestra. ScriptQA estable intacto; otros perfiles y adopción por confirmar.
- Tres muestras reales de candidato16 inspeccionadas para geometría, sin afirmar colorSDR/QA audiovisual completo. Reserva16 pasa a ligera al terminar procesos.

## Ingesta 16–20 y prevención de retrabajo — 2026-09-30

- Nuevo control temprano de salud ASR (`Serie-IA-Negocios-10-Videos/scripts/validar_transcripcion_ingesta.py`), nueve pruebas PASS e integración en AGENTS, README de ingesta y operación. No aprueba tomas ni sustituye escucha.
- Se documentan recuperación compartida acotada (30,039 s sumados de procesos), mapa de25 bloques candidatos/150,95 s y reutilización del análisis por hash. ASR original y recuperación fallan aún los controles; se preservan evidencias y pendientes.
- `MEJORA_FLUJO_16_20.md` conecta control temprano, revisión compacta, previews locales, medición por fase y prevención tras cada video; ahorro global por confirmar.
- Se amplía explícitamente la regla de limpieza de voz a VIDEO-16–20 y próximas ediciones, conservando el antecedente21–25. Diagnóstico y A/B conservador del16 no seleccionados; original intacto.
- Prompt de trabajo21–25 creado en la serie; se conserva separación de carpetas, propietario y reservas de carga pesada.

## Revisión previa y persistencia de audio — 2026-09-30

- Se registra muestreo visual compartido del lote, control de hashes VIDEO-21 y detección técnica de pausas, conservando pendientes escucha y selección.
- La instrucción de limpieza de voz se incorpora al perfil confirmado, AGENTS de la serie y prompt individual para que alcance las próximas ediciones. No se declara procesado ni aprobado el audio final.

## Limpieza de voz — 2026-09-30

- Se añade `AUDIO_LIMPIEZA_VOZ.md` y se integra en QA y prompt de ingesta/edición por solicitud del usuario.
- Se genera piloto A/B local 48 kHz con FFmpeg afftdn; duración preservada, calidad auditiva y selección pendientes. DeepFilterNet queda candidato sin instalación ni adopción.

## Mejora de flujo 21–25 — 2026-09-30

- Se revisan métricas de VIDEO-13 y VIDEO-15 y se añade `MEJORA_FLUJO_21_25.md` con prioridades, evidencia, procedimiento y mediciones pendientes.
- Se incorpora el ciclo de mejora por video a `OPERACION_OPTIMIZACION.md`; no se cambian renderizadores, reglas de aprobación ni scripts de QA.
- La ingesta 21–25 registra fuente, probe, hash y preflight; la escucha y el gate siguen pendientes.

## Radar semanal — 2026-W40 — 2026-09-28

- Se consolida el período 2026-09-22 a 2026-09-28 en `research/reports/2026-W40.md` con tres cambios oficiales de YouTube ya registrados, ausencia de patrones virales demostrables y limitaciones explícitas para Ecuador/LATAM.
- Se mantienen las reglas vigentes: ninguna fuente contradice el máster universal de Instagram ni justifica derivados automáticos por plataforma.
- Se proponen, sin activarlos ni incorporarlos al registro de experimentos, una prueba de Shorts Series y una comparación nativa de hasta tres hooks. Ambas requieren disponibilidad de cuenta y decisión humana.
- La observación diaria del 2026-09-28 queda como `no_material_change`; no se modifican perfiles, reglas, renders ni archivos audiovisuales.

## 1.7.1 — 2026-09-27

- Se traslada la investigación de mercado al proyecto hermano `Investigacion-Mercado-Meta`, por petición del usuario; se mantienen enlaces de compatibilidad y datos históricos.
- La referencia a los 30 videos pasa a ser opcional y no condiciona la investigación. La arquitectura, costos y pruebas se documentan en la bitácora del proyecto nuevo.
- No se modifica el scheduler instalado ni el radar técnico de edición. Las decisiones originales de 1.7.0 se conservan como historial.

## 1.7.0 — 2026-09-27

- Se incorpora `research/market-intelligence/`, un radar Meta-first para estudiar Instagram y Facebook en español alrededor de IA, marketing, ventas y emprendimiento.
- Se define una rotación auditable de 19 mercados latinoamericanos, con prioridad operativa para Ecuador, México, Colombia, Argentina, Chile y Perú sin excluir Centroamérica, Caribe y mercados pequeños.
- El contexto editorial se deriva de los títulos y beats de los 30 videos; no se infiere que una pieza fue publicada o rindió bien.
- Se separan métricas propias autorizadas, señales públicas de competidores, anuncios y limitaciones de acceso.
- Se añaden contratos de cuenta, observación y corrida, controles de tokens, prompt nocturno, plantillas y validación estática.
- La arquitectura recomienda Astra para diseño y auditoría, Luna en esfuerzo bajo para la rutina nocturna y Sol para síntesis semanal cuando exista muestra suficiente.
- Se añade la skill local `investigador-mercado-meta`; TikTok y Shorts quedan previstos pero desactivados en la primera fase.
- Tras inspeccionar la única marca conectada en Metricool, se excluye del radar por no corresponder al proyecto de IA, marketing y ventas; la automatización no la consultará.

## 1.6.3 — 2026-09-25

- Instagram Reels se convierte en el máster social universal por defecto. El mismo MP4 se reutiliza en TikTok y YouTube Shorts cuando encuadre, safe zones, captions, CTA, duración y especificaciones sean compatibles.
- Se adopta `RENDER_VARIANTS_ONLY_FOR_MATERIAL_DIFFERENCE`: otro render exige una diferencia material documentada —duración/aspecto, reencuadre o safe zone incompatible, CTA exclusivo, restricción técnica o experimento creativo aprobado—. Copy, hashtags, portada, metadata, renombrado y decoración menor no justifican un render.
- `plan_platform_derivatives.py` deja de proponer tres salidas automáticamente: sin `--target` planifica solo Instagram. TikTok y Shorts permanecen disponibles mediante selección explícita después de justificar el delta.
- La preview sigue siendo necesaria por superficie, pero varias plataformas pueden referenciar exactamente el mismo SHA-256 universal sin copiar ni re-encodear el archivo.

## 1.6.2 — 2026-09-25

- Se invalida la primera generación de derivados de VIDEO-01 después del rechazo explícito del usuario: presentaba piel lavada por interpretar HLG directamente como SDR y elementos tipográficos que invadían rostro, cabello o cabeza. Los MP4 y checks anteriores se conservaron en `deliveries/rejected-2026-09-25-v1/` y su manifiesto registra el rechazo; no se reescribió la historia.
- El flujo social de VIDEO-01 usa ahora un intermedio SDR BT.709 creado mediante transformación gestionada antes de entrar al navegador. Se prohíbe considerar una bandera `--sdr` o un simple cambio de etiquetas como conversión HDR→SDR.
- El gate visual exige una hoja de contacto independiente por derivado, captions persistentes debajo del mentón o en espacio negativo y revisión explícita de piel, blancos, ropa, cabello, cabeza, ojos y boca. Una variante no hereda la inspección visual de otra.
- Se generaron tres revisiones nuevas de VIDEO-01; cada una pasó preflight técnico y doce fotogramas representativos fueron inspeccionados. Permanecen pendientes la vista previa dentro de cada aplicación y la aprobación humana del usuario.

## 1.6.1 — 2026-09-25

- El protocolo de claqueta pasa a `compact_v2` y añade `MARCADOR. Corregir, corregir. Última frase.` para rehacer el último enunciado sin repetir toda la toma.
- La corrección mantiene abierta la toma, exige repetir la frase completa y sigue requiriendo un marcador final de aprobación o descarte.
- `build_take_map.py` detecta la nueva orden, conserva el rango continuo para el proxy y registra por corrección el objetivo anterior y el reemplazo nuevo como pendientes de escucha.
- El preflight bloquea una edición cuando una corrección parcial sigue sin resolver o aparece fuera de una toma; el inicio de la frase anterior no se decide únicamente mediante puntuación ASR.
- `take-map.json` y `cut-plan.json` incorporan diagnóstico y decisiones de reemplazo no destructivas; se mantienen compatibles los mapas históricos `compact_v1`.
- Se añadieron pruebas para detección, continuidad de la toma y correcciones huérfanas.
- La prueba del registro vigente de plantillas se sincroniza con sus diez entradas actuales; la expectativa anterior todavía indicaba cinco.

## 1.6.0 — 2026-09-25

- VIDEO-06–10 corrigen una mezcla SFX técnicamente presente pero perceptualmente ausente: cada pieza pasa de dos eventos al 20 % a cuatro acentos semánticos en hook, concepto, apoyo y CTA, calibrados según el nivel real del archivo fuente y siempre subordinados a la voz.
- La preferencia de sonido deja explícito que una ganancia porcentual fija no garantiza audibilidad; el gate debe comprobar presencia en el MP4 final y conservar picos prudentes.
- La ingesta admite claquetas `video N toma N` sin la palabra `inicio`, con menor confianza y advertencia explícita; se añadieron pruebas de regresión y se preserva la revisión humana como requisito cuando falta identidad inequívoca.
- El QA de captions incorpora un gate de límites: cues adyacentes no pueden dejar dos frases legibles al mismo tiempo y se exige muestrear el MP4 real en transiciones críticas. El hallazgo surgió al revisar VIDEO-08 dentro del lote 06–10 y se corrigió en los cinco editables antes de su entrega.
- El preflight visual previo al render completo se vuelve explícito y bloqueante: la hoja de contacto debe proteger cabeza, cabello, rostro, manos y sujeto principal, y verificar que placas, fondos, resaltados y contenedores cubran íntegramente su texto. Cuando haya espacio, se prioriza reencuadrar la toma antes que reducir por rutina la jerarquía tipográfica.
- El mismo gate separa texto editorial de metadatos de producción: timecodes de trabajo, nombres de beats, números de escena, instrucciones de animación y notas de composición no pueden aparecer dentro del área renderizable.
- VIDEO-01 aplica por primera vez los tres perfiles activos desde una sola composición parametrizada: Instagram Reels prioriza aire y lectura editorial, TikTok compacta y alinea a la izquierda, y YouTube Shorts adopta una composición centrada con continuidad `EP. 01`. Los tres derivados conservan toma, cortes, voz, mensaje y activos; pasaron preflight técnico, mientras la vista previa real por plataforma y la aprobación exacta siguen pendientes.
- El ciclo de render se actualiza a HyperFrames 0.8.77 y deja salidas SDR BT.709 H.264/AAC a 1080×1920, 30 fps y −14.3 LUFS, con manifiesto y hashes por derivado.
- Se añade una guía de SFX basada en evidencia: firma inicial compacta y sincronizada, efectos ligados a eventos semánticos, voz prioritaria y ausencia de sobreestimulación. VIDEO-03–05 adoptan una segunda capa breve en el hook y mantienen sus acentos de transición y cierre.
- La preferencia visual de la serie incorpora placas de contraste detrás de los títulos iniciales, con color variable por familia, escala grande y protección del rostro.
- El radar del 25 de septiembre registra Shorts Series y la recomendación de publicaciones dentro del feed de Shorts como cambios oficiales de plataforma. Se conservan como experimentos opcionales —serie para un subconjunto coherente y post de apoyo como superficie separada— cuando la cuenta tenga acceso; no alteran másteres, reglas ni renders y no usan métricas generales de microdramas como prueba de rendimiento para IA.
- El lote VIDEO-03–05 convierte tres familias planificadas en candidatas editables y distintas: mapa de conocimiento propio, diagnóstico de caos de procesos y contraste criterio/delegación. Todas permanecen pendientes de aprobación y de datos de red; no se declara ganadora ninguna.
- La práctica de producción normaliza la voz antes del render completo y revisa loudness del MP4 final; VIDEO-03 demostró que omitir este gate genera retrabajo aun cuando la imagen ya es válida.
- La medición separa tiempo creativo de render y marca la contención de recursos: no se usa un render concurrente como benchmark de velocidad.
- Se incorpora una consola de revisión reproducible: MP4, manifiesto, dependencias, blueprint, cambios y decisión quedan ligados por SHA-256; el feedback se expresa por rango, capa, elemento e instrucción y genera previews parciales sin sustituir el recibo de aprobación.
- Se crea un índice semántico de activos que descubre catálogo, manifests, locks y `media-use`, agrupa solo duplicados binarios exactos, respeta contraindicaciones y exclusiones, y aplica cooldowns no bloqueantes. La serie cuenta con un snapshot de 139 activos, 237 registros de origen y 11 grupos exactos.
- Se añade una gramática ejecutable de 18 módulos y un compilador que propone hasta tres recetas contextuales con cobertura, esfuerzo, compatibilidad, fatiga y abstención. `creative-attribution.json` liga la selección humana a una propuesta real, con familia primaria y contribuyentes para no duplicar crédito.
- Se implementa un paquete multicanal fail-closed desde un SDR aprobado, con replay del perfil, linaje HDR, recibos, catálogo, content lock, gates por destino, staging completo y sellos de package/adaptación/briefs; no publica ni hereda aprobación a derivados.
- Se implementan registro de publicaciones con evidencia local, inspección real de MP4, observaciones normalizadas, ventanas bilaterales, N efectivo por métrica e intersección, ocho dimensiones creativas y cohortes descriptivas comparables por cuenta/idioma/tema/campaña/periodo/moneda. Eficiencia verificada y rendimiento creativo permanecen separados.
- Se endurecen rutas, symlinks, hashes, lectura desde los mismos bytes, IDs reproducibles, locks/CAS, no-clobber, revalidación semántica, escritura explícita y pruebas adversariales en los cinco módulos. SHA-256 se documenta como integridad local, no como autenticación humana o remota.
- Se integra la ola en el validador, los prompts de producción, la matriz, el flujo, el motor de aprendizaje y una guía operativa para el lote; se registra la preferencia explícita de optimizar los 30 videos sin bajar calidad ni congelar creatividad.
- Se planifica la ola 1.7: orquestador de cierre atómico, controlador del lote, tablero de eficiencia, regresión audiovisual y preproducción adaptativa.

## 1.5.0 — 2026-09-25

- VIDEO-02 añade una salvaguarda de composición HDR: la transparencia de video se valida en el render final; cuando el compositor no preserva alfa, se usa un precompuesto HLG corto que modifica solo el fondo mediante matte invertido y mantiene intacto al sujeto.
- Se incorpora loudness previo al render como gate de preflight para cada toma nueva; una cámara o toma distinta no hereda por supuesto la ganancia de voz del video anterior.
- Se incorpora un motor de aprendizaje basado en evidencia, alcance mínimo, precedencia, revocación y revisión humana; sus recomendaciones no escriben reglas ni promueven plantillas automáticamente.
- Se separan evidencia técnica, aprobación creativa, preferencia, repetición y rendimiento; las métricas sin cohorte o comparación no pueden presentarse como señal direccional.
- Se añade memoria de serie con fingerprint reproducible, contrato `locked`/`bounded`/`rotating`/`free`, ledger inmutable, linaje de familias y alertas de variedad que nunca puntúan ni bloquean calidad; un re-check idempotente excluye el mismo fingerprint para no generar falsas alertas de similitud.
- La promoción de defaults estables exige videos distintos aprobados y QA técnica `pass` ligada al mismo SHA-256 del artefacto; una instrucción explícita conserva una vía separada y no finge evidencia repetida.
- Se crea un recibo de aprobación ligado a hash, tamaño, rol, perfil, alcance y referencia humana; soporta registro retrospectivo mediante tiempos separados de creación, decisión y registro.
- Se endurecen sellado y escritura atómica, referencias estructuradas, rechazo de `NaN`/infinito, rutas seguras, locks multiproceso y validación de evidencia. SHA-256 garantiza integridad, no autenticidad o no repudio.
- Se separan el mezzanine editorial HDR y el máster social SDR BT.709. El segundo requiere un HDR aprobado, otro hash, conversión trazable y revisión visual humana.
- El banco de plantillas obtiene schema e invariantes propios. Aprobación del video, autorización de reutilización, madurez de familia y rendimiento usan estados independientes; el validador vuelve a comprobar el sello y el artefacto del recibo, y T01 permanece candidata aunque VIDEO-01 esté aprobado.
- Se establece un portafolio contextual y una gramática modular de `hook + estructura + sistema visual + motion + sonido + CTA`; ninguna plantilla puede declararse ganadora universal.
- Se actualizan prompts, matriz, QA, política, flujo, roadmap y validador integral para aplicar los contratos 1.5.0 y priorizar revisión por timecode, índice semántico de activos, recetas creativas, paquete multicanal y métricas por cohortes.

## 1.4.1 — 2026-09-25

- Se endurece el gate de protección de sujetos: aplica a la persona en cámara y también a rostros y elementos principales de imágenes generadas, B-roll y cutaways.
- Se exige ubicar texto y gráficos únicamente después de inspeccionar el espacio negativo real del fotograma.
- Se incorpora verificación explícita de relevancia para iconos y SVG; los recursos ambiguos o decorativos quedan fuera del montaje.
- Se bloquean transiciones con dobles exposiciones prolongadas entre rostros y se añade revisión representativa del inicio, desarrollo, transición crítica y cierre antes del render completo.
- Se registra esta decisión como preferencia global confirmada a partir de la revisión explícita de VIDEO-02.

## 1.4.0 — 2026-09-25

- Se incorpora una matriz profesional de ocho módulos con artefactos y gates verificables desde grabación hasta aprendizaje posterior.
- Se añade preflight técnico de grabaciones mediante `ffprobe`, con rotación, resolución, FPS/VFR, códecs, audio y metadatos de color.
- Se crea `creative-blueprint.json` para estrategia, hook, beats, arco emocional, protección facial, descansos y presupuestos de motion/SFX con trazabilidad.
- Se añade selección determinista de estilo con ranking explicable, umbral absoluto, margen mínimo y abstención válida.
- Se introduce un tablero atómico de producción: un owner por `VIDEO-NN`, límite configurable de heavy jobs, bloqueo entre procesos y escrituras atómicas.
- Se incorporan grafo de dependencias, cálculo transitivo de impacto y claves de caché SHA-256 para evitar tanto retrabajo innecesario como reutilización obsoleta.
- Se formalizan variantes controladas con cuerpo compartido bloqueado y una sola familia de cambios por experimento.
- Se añade un registro de golden masters que compara hash y metadatos sin renderizar ni sobrescribir aprobados.
- Se crean cuatro perfiles: máster vertical neutral, Instagram Reels, TikTok y YouTube Shorts; las restricciones oficiales quedan separadas de defaults y safe zones internas.
- Los derivados por plataforma permanecen bloqueados hasta aprobación explícita, content lock completo y hashes; reutilizan el mismo proyecto y cambian únicamente layout, captions, CTA equivalente y exportación.
- Se añade preflight por plataforma con `ffprobe` y revisión visual humana ligada al SHA-256 exacto del archivo.
- Se incorpora `performance-review.json`, que exige contexto y prohíbe por contrato la promoción automática de reglas.
- El validador integral incorpora todos los contratos nuevos, invariantes de catálogo y endurecimientos de QA, fechas, symlinks, hashes y pesos numéricos.
- La versión de HyperFrames del ciclo actual se alinea a `0.8.75`.

## 1.3.0 — 2026-09-25

- Se adopta la ingesta maestra de una sola pasada: selección de audio por escucha, transcripción única, detección de marcadores y revisión humana de `take-map.json`.
- Se crean proxies independientes por `VIDEO-NN` para habilitar edición paralela sin volver a recorrer cada MOV; el render final mantiene los rangos exactos del original.
- Se incorporan `build_take_map.py`, `build_take_proxies.py`, sus pruebas y el contrato [INGESTA_MAESTRA.md](INGESTA_MAESTRA.md).
- Se añade un prompt de edición individual que obliga a reutilizar `take-map`, proxy y rango fuente, y limita cada tarea a su propia carpeta `VIDEO-NN`.
- Se añade un preflight de proyecto que verifica originales, hashes, estilos autocontenidos, recursos locales y bloqueo de activos rechazados o inelegibles.
- El preflight detecta copias binarias exactas de SFX rechazados aunque estén renombradas; los históricos quedan fuera de árboles activos en cuarentena recuperable.
- Se introduce `asset-lock.json` para congelar el catálogo efectivo de cada producción.
- Los tres presets de estilo pasan a vivir dentro del framework con versión y hash de paquete verificables.
- Se incorpora un scorecard profesional con 26 hard gates, 16 criterios editoriales, evidencia por render y bloqueo obligatorio ante cualquier hard fail.
- Se formaliza un máximo inicial de dos trabajos pesados simultáneos en el mismo equipo; el montaje creativo continúa en carpetas exclusivas por video.

## 1.2.1 — 2026-09-25

- Se adopta la regla `SPEECH_LED_CADENCE_EDITING`: la entrada predeterminada queda cuatro fotogramas antes del primer fonema a 30 fps, con margen adaptable según respiración y gesto.
- Se clasifican silencios, respiraciones y pausas semánticas antes de comprimirlas para evitar tanto tiempos muertos como una cadencia artificial.
- Se definen colas de voz, microfundidos, continuidad gestual, excepciones expresivas y QA de cada empalme.
- Se incorpora `templates/cut-plan.json` para congelar cortes de forma no destructiva y permitir cambios posteriores de estilo sin rehacer la selección.
- Se documenta la ingesta local de archivos grandes y la convención para lotes que contienen varios `VIDEO-NN`.

## 1.2.0 — 2026-09-25

- Se define un flujo de producción rápida que prepara recursos mientras se graba y trata la toma aprobada como fuente definitiva.
- Se separan QA técnico, aprobación editorial, aprobación explícita del usuario, reutilización y rendimiento para evitar aprender gustos por inferencia.
- Se crea un perfil versionado de preferencias confirmadas y una política de promoción que exige contexto y repetición cuando la instrucción no es global.
- Se incorpora un catálogo maestro con IDs estables, descripciones semánticas, hashes, procedencia, usos recomendados y políticas de rotación.
- Se añade una galería local buscable y un índice Markdown generados desde el mismo catálogo.
- Se formaliza la revisión por delta: tiempo, capa, elemento y cambio solicitado.
- Se limita el gasto de render mediante previews, clips de tramos críticos y un render final completo después del bloqueo editorial.
- Se añaden plantillas para decisiones de revisión y estado del video, junto con eventos de feedback atómicos.
- Se incorpora una plantilla de métricas para medir tiempo por etapa, reutilización, rondas, renders y causas de retrabajo.
- Se retiran del uso automático `SFX-ENTRY-0001` y `SFX-MOTION-0001` por feedback explícito sobre intensidad y brillo.
- Se añaden cuatro candidatos SFX de bajo brillo y ataque redondeado, pendientes de aprobación, y se reduce la ganancia inicial recomendada a 0,35–0,50.
- Tras la revisión explícita se aprueban `SFX-ENTRY-0002`, `SFX-ENTRY-0003` y `SFX-MOTION-0003`; `SFX-MOTION-0002` queda rechazado y fuera del uso automático.

## 1.1.0 — 2026-09-23

- Se añade un motor de selección y sustitución de estilos por capas.
- Se centralizan tres presets iniciales en `styles/catalog.json`.
- Se incorpora `STYLE_003_IMMERSIVE_WELLNESS` con parámetros visuales y de movimiento verificables.
- Se define qué recursos pueden reutilizarse al pedir otro estilo y qué cambios requieren nueva revisión editorial.
- Se inicia `library/icons/` con cuatro SVG semánticos wellness, manifiesto y hashes.

## 1.0.0 — 2026-09-23

- Se crea el núcleo global separado del piloto.
- Se separan cambios de plataforma, patrones observados, experimentos y reglas locales.
- Se establece una automatización única a las 09:00 America/Guayaquil: radar diario y, los lunes, informe semanal dentro del mismo ciclo.
- Se añade catálogo inicial de fuentes oficiales.
- Se crean registros versionados de reglas y experimentos.
- Se incorpora la biblioteca original Social Essentials y su cama musical.

## 2026-09-30 — auditoría concreta VIDEO-21

Hashes del lote/candidato y referencias locales revalidados; T21 aprobado confirmado en registro. Comparación20/22 limitada a planes sin editables. Fuente científica, auditoría de requisitos y paquete MP4/A/B añadidos; frame.md distingue pendientes iniciales de QA ya ejecutado. Final/escucha siguen pendientes; no se renderiza por repetir auditoría.

## 2026-09-30 — Prevenciones del cierre provisional16

- MEJORA_CONTINUA añade congelación de evidencia antes de repartir QA y selector de motion inequívoco antes de muestreo denso.
- Cambio de hashHTML exige comprobar dependencia de audio; no repetir WAV/ASR si fuente y schedule son equivalentes con evidencia.
- Prompt21–25 alinea excepción de preview sin escucha con medidas por comando; versión anterior preservada.
- VIDEO16 recoge42tiempos/43capturas/34assertions, referenciaaudio y Studio como evidencia distinta del MP4/escucha/aprobación. No ahorro global medido ni cambio a la capturaQA estable.

## 2026-09-30 — VIDEO21 entrega local por delegación explícita

- Render delivery30fps HLG21,633s autorizado según criterio, sin afirmar escucha/aprobación visual realizada por el usuario ni publicación.
- Composición idéntica al candidato revisado; decode/integridad/metadatos/mezclaPASS.94frames del MP4−2/−1/0/+1/+2 y lectura inspeccionados; cuatro hojas.
- Render148,407s, QA5,229s, extracción3,535s; no equivalen al tiempo total. Mejora QA local añade frames inmediatamente adyacentes a cortes y corrige nombre por defecto.
- ENTREGA/AUTORIZACION/AUDITORIA_ENTREGA y métricas/manifest/QAs/bitácora actualizados. Humanflagsfalse; ingesta provisional reusable21–25 conservada.

## 2026-09-30 — Prevención de captions congelados en export HDR

- Caso16CLI0.8.98: Studio/check pasan, MP4 último cue constante. Diagnóstico estático de máscara visibility y smoke real4,8s respaldan GSAPopacity del wrapper como mitigación.
- Regla añadida a mejora continua, QA profesional y prompt individual: smoke real tras autorización, tres cues+gap y QA de todos los captions/cola en MP4. Generador16 actualizado; previos aprobados intactos.
- ColorHDR/tonemap ySDR se verifican por destino; sin corrección manual de paleta ni aprobación retrospectiva del V1.


## 2026-09-30 — VIDEO22 y muestreo visual experimental sin tiempos copiados

- Nuevo scripts/qa_visual_boundaries.py: límites de HTML y captions.json (incluye legacyGSAP),±2/±1, lectura y resumen1s; extracción agrupada y evidencia ligadas a SHA/fps/argv. Mantieneqa_post_render.py estable sin cambios.
- Preserva carpetas previas, rechazaVFR/start distinto de0 y valida número deframes. Expresión balanceada evita límite de profundidad deFFmpeg;200PTS exactos en600frames de prueba. Pasó parsing de14cues21 y16cues22 y límites del apoyo22.
- Piloto22 encontró mismo síntomaHDR de16; se corrigió opacity del contenido de cada cue sin modificar dependencias ni videos anteriores. Dos pilotos49,443s/43,698s, check final30,502s. No son tiempos totales ni ahorro probado.
- Limpieza de ruido conservaA/B y latencia medida. Retocar geometría o documentación no justifica repetirASR/voz. CierreQA22 se registra al completarse.

## 2026-09-30 — Cierre VIDEO16 y medición por destino

- Entrega principalSDR y másterHDRv2 pasan decode yQA visual acotado; V1 rechazado conservado. Authorizationbinding y manifiesto ligan fuentes/evidencias/output exactos, sin afirmar escucha humana.
- Registro real:36,632sSDR drawElement/GPU/1worker y392,358sHDR screenshot/GPU/2workers; perfiles distintos, sin benchmark equivalente. Smoke real previo, extracción agrupada y reutilización dePCM exacto evitan repetir trabajo sin saltarse diferencias entre variantes.
- Descripción de límites de extracciónSDR corregida; evidencia histórica inmutable aclarada por errata. Mejora continua documenta alcance y siguientes tareas sin cambiar aprobados anteriores.


## 2026-09-30 — Corrección de audio22 conservando la imagen verificada

- Se comprobó equivalencia del HTML visual ignorando solo tagsaudio y data-hf-id editoriales, hashes de medios/subcomposiciones y hash del stream de video antes/después de remux. Nueva mezcla recibe decode/loudness/integridaddel candidato exacto; no se reutiliza un scorecard con otro nombre.
- RotaciónSFX-ENTRY-0003, tres entradas11dB y cierre13,06dB bajo voz; final−16LUFS/−1,7dBTP. Remux1,664s frente a189,630s de captura inicial; configuraciones/tareas distintas, no benchmark de ahorro global.
- Dos pilotos y seis checks preservados. Scorecard semánticamente válido sin firma ficticia. Preview usa variables oficiales HYPERFRAMES_FFMPEG_PATH/FFPROBE_PATH y FFmpegfull conlibzimg; render mantiene backend aislado.

## 2026-09-30 — Ruido de fondo16: revisiónv3

- Reporte auditivo del usuario reabre bypass; ventilador como origen tentativo, sin confirmación física.
- afftdn local/perfil de pausa, contexto48k,25ms compensados; ruido−5–7dB en tres pausas, cambios mínimos de voz medidos. A/B, señalretirada y parámetros/hashes conservados.
- CopiasSDR/HDRv3:−15,1LUFS/TP−1,7; decode/lag/clipPASS. Imagen ytimingcodificados iguales aV2: remux, sin rerendergráfico niASR. Entregasprevias intactas.
- QA nuevo pendiente de escucha/naturalidad; no atribuye aprobación, supresiónperfecta ni origen confirmado. Regla de limpieza incorpora escucha reportada como motivo para revisar bypass.


## 2026-09-30 — Rótulos temáticos y estructura interna

- Corrección humana22: rótulos de beats visibles pasaron inadvertidos pese a la regla existente de no mostrar metadatos. Se reemplazaron por significado del contenido en escenas/generador y avisos.
- QA_PROFESIONAL y AGENTS de serie concretan ejemplos en español y exigen leer todos los rótulos/avisos; numeración permitida como navegación temática, no nombre de escena.
- No basta contraste/layout:22 pasa120muestras y44/44contrastes, además de inspección visual de cinco estados y comparación exacta del alcance. Renders anteriores conservados y marcados históricos; el editable corregido requiere nueva captura de imagen para MP4.
- Optimización acotada: reutilizar voz, corte, medios y timings inalterados por hashes; no repetir ASR ni mezcla para una corrección textual. Una imagen modificada impide reutilizar/remuxear el stream gráfico antiguo como si estuviese corregido.21 revisado en paralelo por solicitud explícita del usuario; resultado se añade al cerrar.


## 2026-09-30 — Gate obligatorio de texto visible y aprobación22

- Usuario aprueba22 y solicita documentar regla sin omisiones. Causa identificada: se interpretaron nombres de estructura como navegación válida pese a la prohibición existente; el check técnico no evalúa esa intención.
- Nuevo `scripts/validar_texto_visible.py`: recorre HTML activo/subcomposiciones, registra hashes e inventario, bloquea etiquetas conocidas con numeración/anticipación, falla ante referencias ausentes. Excluye notas técnicas, script/style/captions y capas inline display:none.
- Cinco pruebas de regresión PASS: rechaza etiqueta numerada/aviso y texto anidado; acepta rótulos contextuales y separa captions/IDs/notas ocultas; falla cerrado ante fuente activa ausente. No pretende demostrar semántica universal.
- Wrapper22 ejecuta gate antes de render, aborta ante fallo y conserva informe único. Wrapper21 lo incorpora después de su render en curso. AGENTS/QA obligan usar el gate y revisar visualmente todo el texto; futuras ediciones deben conectar la misma entrada, sin saltarse wrapper.
- Aprobación22 ligada a hashes del HTML corregido; exportación local en curso. Escucha humana no declarada por esa aprobación.21v2 exportado yQA técnico/modelo visual PASS, cierre especializado en curso.


## 2026-09-30 — Cierre paralelo21: rótulos contextuales

- Agente solicitado por usuario: sustituyó tres rótulos visibles y fuente generadora21; títulos, cortes, captions y recursos conservados. Nueva entregaHLGv2, previa preservada.
- Check0.8.99:131muestras17/17contrastes;115framesdelnuevoMP4, cuatro hojas; decode/integridad/loudnessPASS. Render148,263s; QA5,711s; muestreo3,854s. AACcodificadoidénticoalv1.
- Guard de texto conectado enwrapper21; revisiónsemántica/manualdelmodelo siguenecesaria, escucha humana porconfirmar. CLIactualizado0.8.99trasprobevalidado; no actualizaciónglobal niASRrepetido. Bitácora y docs especializados registran revisión previa que omitió estehallazgo.

## 2026-09-30 — Imagen tecnológica contextual y regla permanente
+
+- Nueva fotografía ilustrativa asesora/cliente/portátiles sustituye taller en candidato v4; dos segundos, captions exteriores y retorno conservados. Prompt/origen/hashes y visualización inspectada guardados; foto previa intacta.
+- Preferencia PREF-IMAGE-CONTEXT-REALISM-001 y regla CONTEXTUAL_REALISTIC_IMAGE_REPLACEMENT adoptadas por instrucción global: inspeccionar significado real, preferir generación específica ante recursos inadecuados, banco alternativo, fotografía natural y QA de plausibilidad/integración.
+- CandidatoCLI0.8.99 tras bump0.8.98, check61,874sPASS/300motion/11contrastes; cinco snapshots8,196s inspeccionados. Audio limpio v3 reutilizado; «Ok mejoro» acredita mejora reportada, no escucha completa ni aprobación visual.
+- MP4v4 no exportado en solicitud de generar imagen; anteriores preservados. No promesa de indetectabilidad/exclusividad ni promoción global de asset. Documentos/prompt/AGENTS, changelogs y bitácora actualizados con versiones previas.
+

## 2026-09-30 — Cierre entrega22 con guard aplicado

- Aprobación de editable ligado a hashes; gatepre-renderPASS y entregaHLG204,500s. QAdecode/integridad/metadatos/loudnessPASS3,877s;161frames delnuevoMP4 inspeccionados en seis hojas. Rótulos contextuales comprobados, previosconservados.
- ExtracciónHLG requirióbackendfull9 conzscale: intento fallido8(0,179s) conservado y reintento3,567s correcto; diagnóstico no altera export ni audio. PerfilHDRcompliant conaviso bitrate6,35Mbps vs12referencia; audición humana sigueporconfirmar.
- Regla fallida documentada sin reescribir historia; guardconocido más lectura visualtodo texto sonobligatorios. NoASRrepetido ni QAvisualantigua trasladada a imagen nueva.


## 2026-09-30 — VIDEO22: microacción de compra frente a metáfora abstracta

- Feedbackhumano rechaza mano/pasos por falta de contexto. Se aplica regla globalIMAGENES_CONTEXTO_REALISMO: escena generada específica de pago de auriculares como ilustración de comprar, sin afirmar caso/producto real. Caso22 añadido a regla existente; recurso previo conservado.
- Fuente/generador/ledger alineados; root solo cambia src/alt. Cinco estados del apoyo y161frames de nuevoMP4 inspeccionados. Check0.8.99PASS120/44, upgradedesde0.8.98validado. Render201,232s, QA3,842s, muestreo3,465s.
- Audiooriginal fuente/hash/timing intactos, pero AAC delrenderer nuevo varió; se copia AACv1sinencode sobre imagenv2. Identidad de ambosstreams demostrada yQA del remux final3,797s. Preservar audio codificado evita cambios no pedidos en una revisión solo visual; no transcribir ni limpiar de nuevo. Sin atribuir ahorro globalcontrolado.
- Recursos/documentación/recibos y versiones históricas preservados; aprobación específica de imagen nueva y escucha humana porconfirmar, sin publicación.
