# Musicalización por código y evaluación perceptual asistida

Incorporado el 2026-10-01 por petición expresa: ampliar la revisión con herramientas que reciben audio real y permitir que Codex implemente música/SFX sin abrir interfaces. Complementa [dirección y prosodia](AUDIO_DIRECCION_Y_PROSODIA.md) y [QA de mezcla](AUDIO_MEZCLA_CONTEXTO_QA.md). Mantiene flujo1 y los guards/aprobaciones existentes; no activa limpieza especializada de voz ni adopta canciones nuevas globalmente.

## Entrada única para Codex

Desde la raíz del proyecto, usar `Framework-Edicion-Social/scripts/audio_multimedia`. Puede ejecutarse desde otro directorio mediante ruta absoluta; los archivos de cada plan se resuelven respecto del JSON del plan. No necesita navegador, Studio, servidor, reproductor o sesión de otro chat.

```bash
Framework-Edicion-Social/scripts/audio_multimedia doctor
Framework-Edicion-Social/scripts/audio_multimedia catalog --type music --role impulso
Framework-Edicion-Social/scripts/audio_multimedia catalog --type sfx --approved-only
Framework-Edicion-Social/scripts/audio_multimedia prosody --voice VOZ_NATIVA.wav --transcript PALABRAS_EXISTENTES.json --direction DIRECCION.json --out QA_PROSODIA
Framework-Edicion-Social/scripts/audio_multimedia mix --plan PLAN_AUDIO.json --out AUDIO_v1 --review
Framework-Edicion-Social/scripts/audio_multimedia review --voice AUDIO_v1/voz.wav --mix EXPORT_EXACTO.m4a --music AUDIO_v1/musica.wav --sfx AUDIO_v1/efectos.wav --out QA_AUDIO
```

Codex prepara el plan y lee los informes; el usuario no necesita redactar JSON ni abrir el HTML. El comparador es un recurso opcional para evaluar preferencias. `catalog --include-history` permite inspeccionar antecedentes; no habilita SFX rechazados. Música y SFX se devuelven separados; candidatos y aprobaciones conservan su alcance original.

El lanzador usa el entorno aislado `~/.cache/codex-audio-perceptual/2026-10-01/venv`. No modifica Python global ni entornos de otros videos. `AUDIO_MULTIMEDIA_PYTHON` permite indicar otro ejecutable; el revisor exige las versiones/modelo calibrados. Si el entorno falta o cambia, reparar/recalibrar antes de presentar resultados como válidos. No instalar ni cargar modelos grandes en cada edición.

## Secuencia de trabajo

1. Reutilizar voz nativa seleccionada, transcript, marcadores y recursos verificados. Leer intención/objetivo/público y localizar hook, contraste, explicación, aplicación y pregunta. La transcripción suministra contexto, no certifica cómo suena la interpretación.
2. Consultar prosodia existente por hash. `prosody` puede ejecutar el perfil acústico ya disponible: intensidad/F0 estimado/ritmo/pausas, con palabras temporizadas existentes. No repite ASR. Su `direction` contiene `sections` con `start_s`, `end_s` y texto/intención; transcript es una lista de palabras con `start`/`end`. Comparar dentro de la misma voz; no inferir emoción desde números.
3. Elegir función y arreglo mediante el catálogo y escribir el plan por frases. En15–30s, una o dos músicas según mensaje, sin cuota. En largos, cambios por argumento. Justificar cada SFX; conservar descansos. La voz gobierna tanto retiradas como recuperaciones.
4. Ejecutar `mix --review` en una carpeta nueva de versión. Devuelve rutas JSON para que Codex continúe. Produce mezcla48k estéreo WAV FLOAT/AAC256k, voz/música/SFX separados, plan congelado, curva secundaria y recibo. La voz admite solo ganancia constante explícita; no normalizar cada variante por separado ni tratar voz automáticamente.
5. Leer candidatos temporales de revisión y cruzarlos con las frases/prosodia. Comparar nivel, ubicación, carácter o arreglo. No cambiar faders para maximizar E-STOI ni reducir toda la música hasta que el detector deje de verla. Valores locales son hipótesis, no presets universales.
6. Integrar derivados versionados en el editable y verificar el export audiovisual exacto. Usar stems y ganancias congeladas con `data-volume=1` cuando corresponda. Si se incorpora una mezcla completa, impedir duplicar la voz o SFX que ya contiene. Respetar la política de canales/timing del motor y volver a comprobar el audio extraído delMP4; pasar un AAC previo no aprueba el audio de otro hash.
7. Documentar decisiones y controles afectados. Estado `MEZCLA_TECNICA_CANDIDATA`/`EVALUACION_ASISTIDA_PARCIAL`; `LISTA_PARA_ESCUCHA` cuando el QA aplicable exacto esté completo. Escucha humana, naturalidad, carácter, fatiga, percepción de SFX y dispositivo permanecen `por confirmar` si no hay evidencia.

## Plan de mezcla v1

Ejemplo ejecutado: [plan-piloto-01.json](research/escucha-perceptual-2026-10-01/headless/plan-piloto-01.json). Es una prueba con fuentes reales del banco; adaptar rutas, hashes, tiempos y dirección a cada nuevo video. No heredar sus valores como decisión estética.

Campos raíz: `schema: "audio-multimedia/v1"`, `id`, `voice`, listas `music`/`sfx`, `music_bus`, `hook_window_s` y `notes`. Opciones desconocidas bloquean mezcla.

| Campo | Uso |
| --- | --- |
| `voice.file`, `sha256`, `gain_db` | Fuente nativa y ganancia constante compartida. Rechaza voz16k derivada de ASR. Mono se duplica aL/R unity; estéreo se conserva. |
| `file`, `sha256`, `license`, `credit`, `reason` de cada clip | Archivo local congelado, procedencia y vínculo con el mensaje. Se verifica hash antes de mezclar. |
| `start_s`, `duration_s`, `source_start_s` | Ubicación en el montaje y fragmento musical/SFX. No hay loops ni recortes implícitos si la fuente no alcanza. |
| `level_mode: "source"` | Conserva nivel del archivo antes de aplicar curva. |
| `level_mode: "voice_relative"` | Normaliza cama a referenciaRMS de voz activa y SFX a contexto cercano, antes de aplicar dB negativos. Es una referencia de calibración, no volumen final recomendado. |
| `gain_db_points: [[segundo,dB],…]` | Curva interpolada en segundos **absolutos del montaje**, no del clip. Puntos crecientes y únicos. `gain_db` constante es alternativa. |
| `fade_in_s`, `fade_out_s` | Bordes sinusoidales; dos clips superpuestos pueden formar crossfade. Duraciones explícitas≤media longitud del clip. |
| `pan`, `width`, `reverse` | Pan−1…1, anchura mid/side0…2, inversión temporal opcional. Verificar mono/cola tras cambios. |
| `hook`, `tail_protect_fraction` enSFX | Identifica evento inicial. Protección de cola después de65ms contra actividad vocal; fracción0…1. No equivale a audibilidad aprobada. |
| `music_bus.highpass_hz`, `lowpass_hz` | Filtrado de la música; no de la voz. |
| `carve_fraction`, `carve_band_hz` | Retirada de una banda de música durante actividad vocal;0…0,8. No estima emoción ni detecta instrumento. |
| `duck_max_db`, `duck_lookahead_s`, `duck_release_s` | Protección descendente de sílabas suaves después de la curva editorial. No eleva música automáticamente en pausas. |
| `speech_margin_db`, `cap_max_db` | Reducción secundaria por relación350–5000Hz, con ventana/suavizado. Aproximación acústica; no certificado de masking ni preset universal. |

Guards: fuentes/hash; clips dentro de voz; SFX no silencioso en hook; dos identidades fuente distintas para20–30s; SFX explícitamente rechazados; finitud; clipping; suma de stems; acuerdoAAC/PCM≥0,999; true peakAAC≤−1,5dBTP. Un intento fallido se conserva; corregir plan y usar nueva carpeta, sin atenuar la voz a escondidas. La CLI no implementa todos los efectos de HyperFrames: compresión/reverb/delay u otro grafo necesita el motor real y su QA. No presentar este mezclador de stems como equivalente a un grafo no soportado.

## Qué se reutiliza y qué se vuelve a revisar

`review` guarda resultados inmutables por hash de fuentes, configuración, script, versiones, modelo/etiquetas y calibración. Comprueba los sellos/evidencias antes de reutilizar. `mix` reutiliza solo la misma receta/fuentes/versión y outputs intactos; una receta distinta en la misma carpeta bloquea escritura. `prosody` reutiliza fuente/transcript/dirección/perfil/FFmpeg y sello.

Cambiar solo interpretación editorial no justifica nuevo ASR/restauración ni volver a descargar modelos. Cambiar audio/export/configuración invalida la evaluación correspondiente. Cambiar versión de herramientas exige comprobar alcance/calibración. El catálogo no convierte candidatos en aprobados. Mantener recibos, decisiones por frase y bitácora/changelog.

En la aceptación local17casos: revisión nueva53s3,19s→reutilizada0,64s;158,798s7,66s→0,69s. Incluyen arranque de Python; una ejecución por condición en este Mac, sin velocidad/equivalencia general demostradas. [Evidencia](research/escucha-perceptual-2026-10-01/headless/v2/aceptacion.json).

## Capacidades calibradas y límites

| Herramienta | Decisión local |
| --- | --- |
| STOI/E-STOI0.4.1 | Uso limitado a estimar conservación del habla frente a voz común y a interferencia musical. Tres controles de ese alcance pasaron; sensibilidad global a SFX breves falló. No es porcentaje de palabras niMOS. |
| YAMNet/LiteRT2.2.0 | Clasificación de audio real:5controles de habla/música/silencio pasaron. Activaciones no son probabilidades humanas, volumen ideal o audibilidad de efectos. |
| Qwen2.5Omni7B4bit/MLX | Experimental: omitió cama suave y efectos en controles; no autoriza faders, claridad humana ni cierre creativo. Puerto con adaptadores documentados; sin equivalencia numérica al backend oficial afirmada. |
| Gemma4E2B4bit/MLX | Descartado **en esta configuración** por inventar habla en música sola/silencio. Pesos nuevos retirados del cache tras conservar hash/recibo; reconstrucción versionada disponible. |

Los detectores reciben ondas; las descripciones de modelos generativos no se aceptan por sonar convincentes. Calibrar capacidades antes de usarlas: controles ciegos de voz, música, silencio, balance, música excesiva, SFX excesivos, ausencia de voz y distorsión. Conservar fallo/umbral original; reducir alcance de una herramienta cuando falle, no cambiar el criterio para aprobarla. Estos controles no son un corpus subjetivo ni certifican generalización a cualquier voz/música.

No usar ViSQOL entre voz seca y mezcla con música para decidir carácter: penalizaría diferencias intencionales. Puede investigarse para comparar codec de la **misma** mezcla. DNSMOS no fue instalado como juez de musicalización: su ámbito de comunicaciones/ruido no demuestra adecuación editorial de música intencional. [pystoi](https://github.com/mpariente/pystoi), [YAMNet oficial](https://www.tensorflow.org/hub/tutorials/yamnet), [ViSQOL](https://github.com/google/visqol), [DNS Challenge](https://github.com/microsoft/DNS-Challenge/tree/master/DNSMOS).

Resultado y fallos reales: [INFORME.md](research/escucha-perceptual-2026-10-01/INFORME.md). El sistema prepara decisiones de mezcla mejor sustentadas; no acredita oído humano, atención de audiencia ni que no exista otra mejora posible.
