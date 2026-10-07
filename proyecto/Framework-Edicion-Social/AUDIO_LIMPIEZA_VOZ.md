# Limpieza de voz y supresión de ruido — a solicitud

## Alcance vigente — cambio explícito del usuario, 2026-09-30

Solo cuando el usuario pida explícitamente revisar la voz/el audio o eliminar ruido de fondo, aplicar `AUDIO_LIMPIEZA_VOZ.md` y la skill `revisar-limpiar-voz` en `/Users/iomijhondavid/.codex/skills/revisar-limpiar-voz/SKILL.md`. Una edición normal, render o QA habitual no activa diagnóstico especializado, nuevas limpiezas, pruebas de motores ni bypass/A-B obligatorios. Dentro de la revisión solicitada, sugerir tratamientos adicionales si se detectan eses molestas, golpes de aire, clics, eco u otros defectos; no aplicarlos automáticamente. Conservar original, recetas, hashes y QA del audio que sí se cambie. Esta instrucción sustituye el alcance general previo; no revierte medios ya procesados ni las reglas habituales de mezcla, ritmo, SFX y sincronía.

## Antecedente de alcance inicial, sustituido

> Vigente desde 2026-09-30 por petición explícita del usuario. Aplicar al trabajo actual de VIDEO-16 a VIDEO-20 y a las próximas ediciones, incluido VIDEO-21 en adelante. No modificar retroactivamente videos ya aprobados sin solicitud. El alcance inicial 21–25 se amplía aquí por la instrucción explícita del usuario en el chat 16–20; se conserva ese antecedente en la bitácora.

Este párrafo documenta la instrucción anterior; no activa limpieza automática. Las versiones previas completas se conservan en `research/limpieza-voz-2026-09-30/skill-a-solicitud/before/`.

## Procedimiento cuando se solicite la revisión o limpieza

1. Revisar la voz aislada antes de música, SFX, compresión o normalización. Clasificar ruido continuo, zumbido, golpes, viento, sonidos externos, reverberación y posibles voces secundarias. Respiración y gesto vocal del presentador no se eliminan por defecto.
2. Guardar el original y trabajar en una copia local de la pista seleccionada, preferentemente WAV 48 kHz; el WAV 16 kHz de transcripción no es fuente de mezcla.
3. Si no hay ruido molesto, conservar la voz y registrar bypass justificado. Si existe, probar primero un fragmento representativo con voz, pausa, consonantes y finales de frase, aplicando reducción conservadora.
4. Comparar original y candidato con niveles perceptuales equivalentes. Revisar inteligibilidad, timbre, respiraciones, consonantes, bombeo, sonido metálico y cantidad de ruido residual. Escuchar también lo retirado cuando la herramienta lo permita: si contiene voz reconocible, reducir intensidad o cambiar método.
5. Seleccionar el candidato que reduzca ruido conservando interpretación. No aplicar una puerta dura como sustituto de supresión: el ruido durante la voz requiere otro tratamiento. No prometer aislamiento perfecto de voces superpuestas ni eliminar ambiente narrativamente pertinente sin criterio.
6. Procesar la toma útil con contexto en los bordes; después aplicar los cortes. Evitar reiniciar algoritmos adaptativos en cada palabra. Registrar y compensar latencia, verificar duración y sincronía labial al inicio, medio y final.
7. Mezclar, normalizar y medir loudness/true peak después de la limpieza. Volver a revisar la voz dentro de la mezcla y en las tres pasadas finales.
8. Registrar herramienta, versión, modelo/hash cuando exista, parámetros, rangos, hashes original/procesado, tiempo y decisión. Sin escucha verificable: `por confirmar`; no marcar fidelidad ni mejora como aprobadas.

## Herramientas y escalado

- FFmpeg `afftdn`: instalado y verificable localmente; candidato inicial para reducción espectral moderada. Parámetros se ajustan a la grabación, no preset universal.
- FFmpeg `arnndn`: filtro instalado, requiere modelo compatible. No disponible para uso efectivo hasta congelar y validar un modelo.
- DeepFilterNet: candidato para supresión neuronal de ruido en voz a 48 kHz. No instalado en el Python/PATH inspeccionados; compatibilidad, rendimiento y calidad en esta voz por verificar. Evaluar si el filtro inicial no resuelve el problema.

Fuentes consultadas 2026-09-30: [FFmpeg](https://ffmpeg.org/ffmpeg-filters.html#afftdn), [DeepFilterNet oficial](https://github.com/Rikorose/DeepFilterNet). Estas fuentes describen capacidad, no demuestran cuál suena mejor en este lote.

## Evidencia inicial 21–25

Existe un piloto exploratorio 15–30 s de la pista AAC: original y `afftdn=nr=6:nf=-50:tn=1`, WAV PCM 24-bit, 48 kHz. Ambos conservan duración. `analysis-21-25/audio-denoise-pilot/pilot-evidence.json` conserva parámetros, tiempos y hashes. No se ha seleccionado para la edición; presencia de ruido y mejora auditiva por confirmar. No sustituye selección de pista ni gate de ingesta.

## Ruido reportado por el usuario — 2026-09-30, VIDEO16

Un nivel de ruido técnicamente bajo no justifica mantener bypass cuando el usuario escucha un fondo molesto. Registrar su reporte, sin asumir que la fuente física propuesta quedó confirmada; preparar reducción conservadora con A/B, contexto y latencia medida. No llamar «voz preservada» o «ruido eliminado» por correlación/nivel solamente: el nuevo candidato requiere escucha de fidelidad. VIDEO16v3 redujo elRMS de tres pausas5–7dB; elventilador concreto y la naturalidad delcandidato siguen por confirmar.

Para cambios exclusivos de audio, conservar imagen codificada mediante remux y verificar hash de paquetes yPTS/DTS/duración contra elMP4 revisado. Reutilizar QAvisual solo si coinciden; medir audio nuevo y sincronía. Mantener versiones anteriores y receta reproducible. Esta optimización no autoriza omitir pruebas de sonido ni publicar.

## Aprendizaje VIDEO23 — perfil de ruido propio, 2026-09-30

El preset heredado afftdn nr6/nf-50/tn1 redujo.02dB una pausa y el ajuste nr8/nf-45/tn0 redujo.31dB en esa misma muestra. Se preparó una tercera prueba con perfil espectral tomado de una pausa de la propia toma, sin voz ASR, conservando original/ensayos. FFmpeg8.1.2: anteponer.6s del ambiente, muestrear sn start.05/sn stop.55 en afftdn, retirar el preroll y medir/compensar después la latencia25ms. Este tratamiento nr8/nf-45/tn0 redujo7.39–8dB en tres muestras y conservó nivel/correlación vocal próximos en cinco tramos; no prueba timbre, fonemas ni mejora perceptual. Escucha por confirmar.

Si una prueba no reduce el ruido medido, perfilar una pausa realmente pertinente es un candidato antes de aumentar agresividad o instalar otro motor. No adoptar estos rangos/parámetros como universal: elegir ambiente sin voz/sonidos narrativos, procesar con contexto, comparar A/B igualado y verificar latencia en cada toma. Receta/evidencia: Serie-IA-Negocios-10-Videos/VIDEO-23/editable-hyperframes-video-23/prepare-audio-v3.py y qa/media-v3/.

## Cantidad y audibilidad de efectos — revisión VIDEO23, 2026-09-30

Para20–30s, mínimo dos identidades de SFX distintas con función editorial; tres instancias de un mismo archivo siguen siendo un solo sonido. Mantener referencia3–5eventos, biblioteca aprobada/rotación, voz dominante y escucha contextual. Medir nivel contra voz contemporánea y picos de mezcla. Si el usuario percibe un solo efecto, revisar identidad y nivel, sin asumir que existir en HTML basta. En23 se sustituyó un acento repetido por Deslizamiento cálido en9.5s y se ajustaron niveles bajo voz; medición no certifica percepción ni naturalidad.


## Dirección de audio y hook — regla permanente VIDEO23, 2026-09-30

Aplicar `Framework-Edicion-Social/AUDIO_DIRECCION_Y_PROSODIA.md` (ruta desde raíz del proyecto). Antes de elegir música/SFX, analizar voz real por intensidad/contrastes, pitch/entonación estimados, pausas, ritmo y cambios por frase; ligar interpretación a palabras/contexto y separar inferencia de escucha. Reutilizar ASR y voz intactos. Comparar aumento de nivel, ubicación o carácter cuando un efecto no se perciba. **Todo hook inicial lleva SFX integrado y debe comprobarse en QA**, además del mínimo dos identidades distintas para20–30s. Registrar niveles contra voz, picos/masking y reproducción real; ausencia de hook/vínculos inválidos bloquea render mediante verificación equivalente a `scripts/revisar_presencia_sfx.py`. Medición no certifica audibilidad ni emociones; mantener escucha por confirmar si falta.


## Comparación VIDEO17: motor local neural verificado, 2026-09-30

Ante reporte de ruido persistente se comparó perfil propioafftdn18 yDeepFilterNet3. **Disponibilidad actual verificada:** binario oficialDeepFilterNet0.5.6AppleSilicon y modeloDF3ONNX en `Serie-IA-Negocios-10-Videos/VIDEO-17/qa/noise-revision-v2/`; versiones/hashes/proveniencia y comandos registrados. El antecedente «no instalado» describe la inspección inicial; no se instaló globalmente ni enPython. Ejecución localnativa funciona.

afftdn18 reduce11.16–12.72dB adicionales en cinco colas150ms normalizadas respecto av1;DF3reduce7.54–10.24dB. ASR recupera81palabras iguales yAAC0lag en cuatro ventanas. Ninguna medida certifica naturalidad, voz aislada perfecta o superioridad con ruido variable. Editable17 eligió provisionalmenteafftdn18 para fondo aparentemente constante; se conservaMP4DF3 para escucha. nr18/nf-55/tn0/gs12 y24dBDF3 son pruebas de esa toma, no defaults del lote.

Próximas pruebas de ruido variable pueden incluir [ClearerVoice Studio](https://github.com/modelscope/ClearerVoice-Studio), [Resemble Enhance denoise_only](https://github.com/resemble-ai/resemble-enhance) o [Adobe Enhance Speech](https://helpx.adobe.com/premiere/desktop/add-audio-effects/adjust-volume-and-levels/enhance-speech.html). Evaluar cada uno con el mismo original, niveles comparables y escuchar fonemas/respiraciones/timbre; no encadenarlos por defecto. Ninguno se probó localmente en17 salvoDeepFilterNet/FFmpeg, ni se subió audio aAdobe. Informe detallado: `research/limpieza-voz-2026-09-30/INFORME.md`. Ruidos específicos de perros/carros/bocinas y uso deAdobe del ejemploClaude permanecen por confirmar.

## Pruebas ampliadas VIDEO17 — 2026-09-30

Se ejecutaron ahora localmente **ClearerVoiceMossFormer2_SE_48K, FRCRN_SE_16K, Resemble denoiser44,1k yRNNoise48k**; el párrafo previo «no probados» conserva la etapa anterior. Entorno y modelos fijados en VIDEO17/qa/noise-benchmark-v3, sin instalación global. Resemble probado solo en supresión; no vocoder/restauración. Adobe aún no probado, sesión pendiente. Reporte: [comparación local](research/limpieza-voz-2026-09-30/COMPARACION_LOCAL_V17_V3.md).

Mismos cinco contextos originales, corte posterior y compensaciónRN960samples/20ms verificada. SieteA/B con monoL/R explícito y ganancia constante−22LUFS; medir la señal real con igual distribución de canales antes de fijar ganancia. FRCRN16k→48k no recupera ancho de banda. RN reduce28,10–33,73dB adicionales en cinco colas150ms respecto av2 a igualloudness; candidatos y fidelidad humana por confirmar. ASR81palabras iguales no prueba timbre/consonantes. Editablev2 conservado mientras se elige; dosMP4 audición no son aprobación ni nuevo default. No encadenar denoisers por defecto.

Reutilizar fuentes/contextos/entornos/modelos conSHA conocido; repetir únicamente procesos afectados por nueva señal. Remux para cambios soloaudio si se prueba identidad completa de imagen y timestamps; conservarguardtexto/hook/SFX y medir audio exacto. Tiempos locales de inferencia excluyen descarga/setup/carga: no tratarlos como tiempo total ni rendimiento garantizado. Señal de diferencia alineada sirve para revisar componentes cambiados, no demuestra pérdida de palabras por sí sola. Elección debe incluir escucha del ruido **durante voz**, fonemas, respiraciones y mezcla final.
