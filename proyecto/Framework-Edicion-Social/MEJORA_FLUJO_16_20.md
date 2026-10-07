# Mejora del flujo comprobada en la ingesta 16–20

Fecha: 2026-09-30. Alcance: lote 16–20 y prácticas reutilizables en próximos lotes.

## Diagnóstico y medidas aplicadas

| Problema | Medida aplicada | Evidencia y límite |
| --- | --- | --- |
| ASR large-v3 repite una CTA hasta el final y pierde cobertura de videos. | Nuevo control temprano `validar_transcripcion_ingesta.py`, inmediatamente después del ASR y antes del mapa/captions. | Informe large-v3: FAIL, 17,55 % de palabras sin duración y bucle masivo. Nueve pruebas del control pasaron. No sustituye escucha. |
| Repetir todo el análisis desde cada VIDEO-NN. | Audio extraído una sola vez, recuperación compartida en nueve bloques con contexto cero y consultas locales a puentes ambiguos. | La recuperación suma 30.039 s de procesos registrados; restaura contenido semántico, pero aún falla por solapes/retrocesos y marcador 19 ausente. No es una comparación de calidad equivalente ni demuestra ahorro global. |
| Revisar intentos descartados al buscar la última frase. | Mapa único de 24 bloques candidatos para los cinco videos; historial de correcciones y ventanas de duda. | 150.95 s candidatos frente a 769,0517 s del original. Revisión humana pendiente; no son proxies aprobados. |
| Confundir legibilidad geométrica con fidelidad de color. | Hoja compartida de 28 muestras para encuadre; color HLG se verifica por separado. | `source-review/master-contact-sheet.jpg`; no contiene transformación SDR verificada. |
| Procesar ruido por defecto aunque la voz ya esté limpia. | Diagnóstico, piloto A/B con niveles equivalentes y latencia compensada; bypass condicional. | Diagnóstico técnico VIDEO-16 estima suelo ≈−66 dBFS y SNR ≈42 dB sobre análisis mono16k. Prueba afftdn suave: mejora del suelo ≈2,3–2,4 dB y latencia25ms. Resultado auditivo y banda superior a8kHz pendientes. Voz final siempre desde AAC48k original. |
| Dos chats escriben documentación y saturan cómputo. | Dueño único por video, máximo dos trabajos pesados, un proceso pesado por dueño; lock en escritura compartida. | `production-board.json` controla reservas, no inspecciona procesos reales. Liberar reserva pesada al esperar escucha. |

## Orden de trabajo reutilizable

1. Leer documentación común una vez; después cargar solo reglas cambiadas y requisitos particulares. Si una lectura queda truncada, completar únicamente la parte faltante.
2. Congelar hash del original y registrar pista/formatos. Reutilizar audio, contacto visual y manifiestos mientras sus hashes coincidan.
3. Ejecutar ASR compartido y control temprano. Ante FAIL, reparar en ingesta las ventanas afectadas o registrar adjudicación humana; conservar evidencia previa. Nunca emitir captions finales desde ASR fallido.
4. Preparar tomas candidatas y dudas en un único paquete. Confirmar pista, identidades, última corrección y fonemas de los empalmes. Cerrar el gate real antes de declarar ingesta aprobada. Según la excepción de AGENTS vigente2026-09-30, el montaje provisional puede avanzar con recibo distinto y escucha por confirmar; resolver cada tramo ambiguo antes de usarlo.
5. Cerrar voz/cortes antes de captions y diseño. Usar recursos existentes pertinentes y conservar variedad entre videos.
6. Probar primero las transiciones críticas con el mismo pipeline de entrega, incluyendo t−2/t/t+2 fotogramas del MP4. Una corrección local recibe un preview local con handles y revisión de sus dependencias.
7. Completar QA visual, audio/ritmo e integral del candidato completo. Un hash nuevo invalida aprobación anterior. Reutilizar un máster social compatible entre plataformas.
8. Tras cada video, anotar defecto, causa, corrección, prevención, tiempo de fase y número de renders. Al cerrar cada cinco videos, comparar fases equivalentes y adoptar únicamente mejoras con evidencia.

## Qué medir y cómo evitar cifras engañosas

Conservar comando, versión, hashes de entrada/salida, inicio/fin, segundos de proceso, resultado y causa de reintento. Separar espera humana, carga local y trabajo superpuesto; no sumar procesos paralelos como si fueran tiempo de pared. Tokens y costo no se estiman desde duración del render: requieren contador real. Contar por separado ASR completo, recuperación por bloques y consultas locales. Comparar el mismo tramo/pipeline/configuración antes de afirmar aceleración.

En este lote ya hay prevención y tiempos locales registrados; ahorro total de edición, calidad auditiva, gate de ingesta y edición final del16 siguen pendientes. No se cambia el modelo activo desde estos scripts ni se afirma haberlo verificado.

## Evidencia

- `00-INGESTA/analysis-16-20/auditor-reglas/`: validaciones ASR reales, hashes, tiempos y auditoría de reglas.
- `00-INGESTA/analysis-16-20/asr-recovery/metrics.json`: nueve corridas acotadas.
- `00-INGESTA/analysis-16-20/auditor-ingesta/PROPUESTA-MAPA-EDL-16-20-2026-09-30.json`: propuesta y dudas, con human_review_completed=false.
- `00-INGESTA/analysis-16-20/auditor-audio/`: diagnóstico y A/B no seleccionado.
- `00-INGESTA/analysis-16-20/director-visual/frame.md`: T16 Opt-Out, semántica y protección de cara/gestos.
- `MEJORA_FLUJO_21_25.md`: evidencia histórica de render y candidato de captura agrupada, sin adopción ficticia.

## Paquete compacto generado

`analysis-16-20/ingest-review-package/index.html` reúne cinco montajes candidatos y tres ventanas originales de duda. Incluye24botones para las24ventanas de contexto en el maestro. Los candidatos suman150,95s nominales; las ocho salidas suman223,066668s reales y64.973.604B. Se verificaron hashes, decode completo y HEVCMain10HLG720×1280/AAC48k estéreo; no son SDR ni editables finales. HEVCVideoToolbox funcionó en los ocho:81,508s sumados de encode y18,208s de decode. No se compara contra otro códec ni se atribuye ahorro total a estas cifras.

Recuento confirmado:24bloques retenidos, no25como indicaba el primer resumen del auditor. El historial conserva ese antecedente; la propuesta contiene cuatrobloques16 y cincobloques en cada17–20. La revisión auditiva de pista, identidades, correcciones y empalmes permanece pendiente. El paquete no firma aprobación.

## Experimento de extracción de QA

Se compararon seis seeks independientes contra un único decode/select en el MP4 VIDEO-15 de21,1s, HEVC/HLG, CFR30 y start0. Calibración aparte: seis PNG byte/pixel idénticos y PTS iguales comprobados en ticks de1/15360. Tres pares AB/BA/AB, sin showinfo en los tiempos medidos: mediana1,765364s frente a0,977326s; diferencia0,788039s (44,64%) exclusivamente para extraer seis imágenes de esa muestra. Los36PNG medidos coinciden dentro de cada par.

`auditor-reglas/capture-benchmark/result-v2.json` y `RESULTADO_BENCHMARK.md` conservan comandos, versiones, hashes, PTS y tiempos. La primera comparación decimal tuvo un falso desacuerdo de28µs: evidencia inicial preservada, reconstrucción en ticks corrige el diagnóstico sin repetir calibración. `qa_post_render.py` permanece intacto. Propuesta de captura agrupada condicionada aCFR/start0 y medición del mismo perfil: falta verificar archivos largos/VFR/otros códecs antes de adoptar un default. No extrapolar44,64% a render, escucha o QA completo.

## Actualización operativa — 2026-09-30

Aplicar `MEJORA_CONTINUA.md`: registro automático por comando, revisión por dependencia y cierres por video/cinco. El montaje16 ya usa el recibo provisional y la excepción autorizada; el estado histórico de bloqueo queda en entradas previas. Voz48k se diagnostica sin denoise innecesario; montaje/QA/aprobación siguen separados. El primer lint detectó rutas de subcomposiciones y entrada HDR duplicada; se corrigen en el generador antes de navegador/render. Ahorro global aún no medido.


## 2026-09-30 — Flujo16/18/19 con agentes: ejecución en curso

Usuario autorizó responsables de video en paralelo con direcciónvisual y auditoría reutilizables; recibo en `00-INGESTA/qa-parallel-16-18-19/request-and-roles.json`. Sesión ofrece4slots activos incluyendo raíz. Configdocumentada permite `agents.max_concurrent_threads_per_session` para futurascargas deconfig; efectoencurso no confirmado. `production-board.json` limita2heavyglobales; la reserva25deotrochat compartecapacidad.18/19intercalan heavy y liberan al trabajarHTML/light, conservando propiedadexclusiva.

16v5RNNoise reutilizó94s48koriginal (inferencia4,294s), check63,869s, ASR9,009s, remux0,483s, decode0,718s. Son fases distintas sin baselineequivalente. Informe parcial en `measured-phases-in-progress.json`. TrasfeedbackLdébil,16v6restaura palabraoriginalconcrossfade; ese defecto muestraque ASRexacto no reemplaza revisiónfonética y prueba final.

En18QAindependiente detectó ycorrigió captionssobremanos antesdelrenderfinal;19recibe ese aprendizaje antesdemontar. Nuevofotorecurso18contextualconservaarchivoanterior;19reutilizafotopertinente. Entregas18/19 e informefinal siguenencurso; no atribuir aceleración porcentual a este solapamiento.


## 2026-09-30 — Cierre paralelo16/18/19

Tresrenders16v6/18v1/19v1 completosconQA técnicos/independientesguardados, aprobaciónhumanapendiente. Informe `INFORME_PARALELO_16_18_19_2026_09_30.md`: repartoagentes,relevoQA,heavy/light, medicionesporfase yconfig. No se cambianlímites ni se afirmaahorro2vs3.18motionautomáticodesactivado explícito,192estadosvisualesMP4reales;19visual218másaudioindependiente. Palabrasdébiles16/19preservadasdeloriginal,sinotrodenoiser.
