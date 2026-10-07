# Framework inteligente de edición social

Núcleo reutilizable para convertir un video fuente en una edición vertical verificable, adaptable a plataforma, tema, audiencia y objetivo. El sistema no persigue modas a ciegas: conecta cada decisión con una fuente, una hipótesis o un aprendizaje propio.

Versión operativa actual: **1.6.3**.

## Modelo de conocimiento

```text
fuente → señal observada → hipótesis → experimento → aprendizaje local → regla aplicable → render
```

Estas etapas nunca se mezclan:

- `platform_change`: cambio confirmado por una plataforma.
- `observed_pattern`: patrón reciente que todavía no demuestra eficacia.
- `experiment`: adaptación concreta que se probará en nuestra audiencia.
- `validated_local_rule`: aprendizaje repetido dentro de un alcance documentado.
- `principle`: regla estable de oficio, seguridad o fidelidad.

Una tendencia con muchas vistas no es automáticamente una regla. Una recomendación para anuncios no demuestra rendimiento orgánico. Una comparación entre dos publicaciones en días distintos no se presenta como experimento aleatorio.

## Ciclo por video

1. Ejecutar el preflight técnico de la grabación antes de iniciar procesos pesados.
2. Ingestar cada maestro una sola vez: hash, selección de audio por escucha, transcripción completa, mapa de tomas y proxies por `VIDEO-NN`.
3. Reclamar el video en el tablero de producción; nunca existen dos propietarios de escritura para el mismo `VIDEO-NN`.
4. Ejecutar el preflight del proyecto y bloquear activos rechazados, faltantes o alterados antes de editar.
5. Crear brief y `creative-blueprint.json`: mensaje, hook, beats, arco emocional, descansos, zonas faciales y presupuestos de motion/SFX.
6. Consultar el índice semántico y compilar hasta tres recetas contextuales; reutilizar antes de generar, permitir abstención cuando falte evidencia y registrar en `creative-attribution.json` la opción que una persona elija realmente.
7. Consultar reglas vigentes y puntuar estilos de forma explicable. Si ninguno supera el umbral, el selector se abstiene.
8. Congelar reglas, estilo y recursos en decisiones y locks versionados.
9. Calcular la clave de caché y el mapa de dependencias antes de montar o rehacer una capa.
10. Editar por capas: montaje, color, voz, captions, evidencia, diagramas, imágenes, motion, música y SFX.
11. Crear variantes solo con cuerpo compartido bloqueado y una familia de cambios declarada.
12. Renderizar desde los rangos exactos del original, nunca desde el proxy de edición.
13. Construir la consola de revisión con todos sus insumos ligados por hash; transformar feedback en cambios por tiempo, capa y elemento, y revisar primero previews parciales.
14. Completar el scorecard de QA con evidencia; cualquier hard fail bloquea la entrega.
15. Obtener aprobación explícita y crear un recibo ligado al SHA-256, rol y alcance del archivo exacto; distinguir cuándo decidió la persona de cuándo se registró retrospectivamente la evidencia.
16. Conservar el mezzanine editorial HDR cuando exista y derivar un máster social SDR BT.709 trazable; no confundirlos ni reutilizar el mismo hash.
17. Registrar el máster aprobado como golden master inmutable y producir únicamente el máster de Instagram Reels por defecto.
18. Reutilizar ese mismo MP4 en TikTok y Shorts cuando sea compatible; crear otro render solo ante una diferencia material documentada. Ejecutar preview real por plataforma, aunque varias superficies compartan el mismo hash.
19. Registrar en el manifiesto la versión de reglas, perfiles y fecha límite de investigación.
20. Extraer el fingerprint con QA técnica ligada al mismo SHA-256, revisar el contrato de serie y actualizar el ledger de variedad sin convertir similitud en una nota de calidad.
21. Registrar publicaciones y métricas con evidencia local ligada por hash, atribución creativa explícita y ventanas comparables; el motor propone aprendizajes no causales y una persona decide si se promueven.

## Velocidad con calidad profesional

La optimización principal no consiste en omitir análisis ni controles: consiste en trabajar en paralelo, reutilizar antes de generar, mantener capas independientes y revisar por delta.

- El guion provisional permite preparar recursos mientras se graba.
- La toma aprobada y su transcripción son la fuente de verdad final.
- La biblioteca se consulta antes de generar imágenes, iconos, música o SFX.
- El índice agrupa copias binarias exactas por SHA-256, ordena por metadatos semánticos y avisa fatiga sin bloquear un recurso pertinente.
- El compilador combina módulos creativos y estima esfuerzo antes de montar; nunca selecciona ni promueve una receta por sí solo.
- La primera revisión usa previews, hojas de contacto y renders cortos.
- Los cambios se describen por tiempo, capa y elemento, conservando lo ya aprobado.
- La consola vuelve a verificar hashes de render, manifiesto, blueprint, dependencias y cambios antes de mostrar o escribir una revisión.
- El montaje de voz usa un `cut-plan.json` no destructivo: entrada ligada al primer fonema, pausas clasificadas por función y continuidad gestual verificada.
- Un `take-map.json` compartido impide que cada tarea vuelva a transcribir o recorrer el maestro y registra correcciones parciales con `MARCADOR. Corregir, corregir. Última frase.` para sustituir solo el último enunciado después de verificarlo por escucha.
- Cada tarea edita su propio `VIDEO-NN`; las transcripciones y codificaciones pesadas se limitan inicialmente a dos procesos simultáneos.
- El tablero atómico bloquea colisiones de escritura y sobrecarga de procesos pesados.
- El mapa de dependencias invalida únicamente las capas afectadas por cada cambio; la clave de caché evita reutilizar resultados obsoletos.
- El render completo de máxima calidad se reserva para la entrega.

El contrato completo vive en [FLUJO_PRODUCCION_RAPIDA.md](FLUJO_PRODUCCION_RAPIDA.md).
La matriz de módulos, gates, estados y artefactos vive en [MATRIZ_PRODUCCION_PRO.md](MATRIZ_PRODUCCION_PRO.md).
Para delegar la preparación de recursos a otro chat del mismo proyecto, usar [PROMPT_PREPRODUCCION_RECURSOS.md](PROMPT_PREPRODUCCION_RECURSOS.md).
Para entregar las grabaciones y ejecutar selección, edición y render del lote, usar [PROMPT_INGESTA_Y_EDICION.md](PROMPT_INGESTA_Y_EDICION.md).
Para asignar después un solo `VIDEO-NN` a una tarea paralela sin reanalizar el maestro, usar [PROMPT_EDICION_INDIVIDUAL.md](PROMPT_EDICION_INDIVIDUAL.md).
Para producir versiones específicas después de aprobar el máster, usar [PROMPT_DERIVADOS_PLATAFORMA.md](PROMPT_DERIVADOS_PLATAFORMA.md).
La ingesta única y la creación de proxies se especifican en [INGESTA_MAESTRA.md](INGESTA_MAESTRA.md).
La entrega profesional se rige por [QA_PROFESIONAL.md](QA_PROFESIONAL.md).
Los subtítulos de las próximas ediciones se eligen por contexto con [SUBTITULOS_CONTEXTO_Y_LECTURA.md](SUBTITULOS_CONTEXTO_Y_LECTURA.md), [catálogo de formatos](captions/catalog.json) y [decisión por video](templates/caption-decision.json). Estilo y ubicación se separan; presets de tamaño/CPS no son requisitos oficiales ni rendimiento probado. La auditoría de18 exportaciones vive en [INFORME.md](research/subtitulos-2026-09-30/INFORME.md).
La memoria verificable y su política de promoción viven en [MOTOR_APRENDIZAJE.md](MOTOR_APRENDIZAJE.md).
La secuencia operativa de estas optimizaciones para el lote vive en [OPERACION_OPTIMIZACION.md](OPERACION_OPTIMIZACION.md).
Las mejoras siguientes, separadas por dependencia y evidencia disponible, viven en [ROADMAP_OPTIMIZACION.md](ROADMAP_OPTIMIZACION.md).

## Aprendizaje de preferencias

El framework distingue cinco estados que nunca deben confundirse:

- `qa_status`: el archivo funciona y supera controles técnicos.
- `editorial_status`: la pieza respeta guion, fuentes y reglas editoriales.
- `user_approval_status`: existe o no una aprobación explícita del usuario.
- `reuse_status`: el elemento puede reutilizarse y dentro de qué alcance.
- `performance_status`: existen o no resultados de publicación que respalden la decisión.

Solo una aprobación explícita alimenta gustos. Una instrucción global como “siempre” puede aplicarse inmediatamente dentro del alcance indicado. Una preferencia inferida necesita confirmación en al menos dos proyectos distintos. El perfil vigente vive en `profiles/creative_preferences.json`; cada decisión de revisión usa `templates/review-decision.json` y cada producción registra tiempo y retrabajo con `templates/production-metrics.json`.

## Motor de aprendizaje y portafolio creativo

El motor separa evidencia técnica, aprobación creativa, preferencias y rendimiento. Sus salidas son recomendaciones no vinculantes: no escribe registros de reglas, no amplía alcance y no promueve plantillas automáticamente. Cada evidencia conserva contexto, familia de plantilla, eje de variación y evento al que sustituye.

La memoria de serie divide decisiones en `locked`, `bounded`, `rotating` y `free`. El piloto aprobado es una referencia, no una ley. Dos videos aprobados distintos pueden proponer un default estable; desde tres aprobaciones se solicita una recalibración humana. Las dimensiones creativas continúan rotando y la similitud solo alerta sobre repetición: nunca aprueba, rechaza ni puntúa calidad.

El banco mantiene varias familias con linaje. Estructura narrativa, formato visual, estilo, ritmo y transiciones se exploran de forma controlada para crear plantillas realmente distintas. El selector elige por adecuación a contenido, audiencia, objetivo y plataforma; no existe una plantilla ganadora universal.

El registro de plantillas separa cuatro estados independientes: aprobación del artefacto fuente, autorización de reutilización, madurez de la familia y evidencia de rendimiento. Así, VIDEO-01 puede estar aprobado sin convertir `T01-editorial-loop` en default. El registro y sus invariantes se validan con `schemas/template-bank-registry.schema.json`; para un artefacto decidido, el validador también vuelve a comprobar el sello, el hash y el archivo actual del recibo.

Comandos principales:

```bash
python3 scripts/learning_engine.py validate --event evento.json
python3 scripts/learning_engine.py recommend --store eventos.jsonl --output recomendacion.json
python3 scripts/series_memory.py fingerprint --editable PROYECTO --out fingerprint.json
python3 scripts/series_memory.py check --contract series-contract.json --fingerprint fingerprint.json --ledger series-variety-ledger.json
```

La gobernanza completa está en [MOTOR_APRENDIZAJE.md](MOTOR_APRENDIZAJE.md).

## Biblioteca maestra

`library/catalog.json` es el catálogo global del framework: mantiene ID estable, nombre humano, descripción semántica, usos recomendados, restricciones, procedencia, hash e historial de reutilización. `library/CATALOGO.md` y `library/catalogo.html` se generan desde esa misma fuente para evitar listas divergentes.

Antes de generar:

1. Buscar candidatos existentes.
2. Reutilizar solo cuando el significado coincida.
3. Derivar una variante si basta cambiar color, encuadre o formato.
4. Generar desde cero solo cuando no exista un candidato correcto.
5. Copiar el recurso elegido al proyecto para mantener el render autocontenido.

`scripts/asset_intelligence.py` construye un índice desde catálogo, manifests, asset locks, manifiestos de `media-use` y carpetas explícitas. Solo un SHA-256 idéntico prueba duplicación exacta. La búsqueda usa descripción, etiquetas, intención y contraindicaciones declaradas; no calcula similitud visual perceptual. Activos rechazados, obsoletos o `do_not_reuse` quedan fuera, mientras los cooldowns permanecen como avisos no bloqueantes. El historial registra únicamente recursos que realmente llegaron a un artefacto aprobado.

## Recetas creativas contextuales

`creative-recipes/catalog.json` contiene 18 módulos iniciales: tres por cada eje de hook, estructura, sistema visual, motion, sonido y CTA. `scripts/compose_recipe.py` valida el blueprint, memoria de serie e índice completos y propone como máximo tres combinaciones compatibles y deliberadamente distintas. Cada opción explica ajuste, confianza, cobertura de activos, fatiga y esfuerzo.

El orden es solo una prioridad de revisión para ese blueprint. La selección requiere una persona; una receta puede abstenerse y nunca se convierte automáticamente en ganadora universal. Cuando combina familias, conserva una familia primaria determinista y las contribuyentes por separado para evitar atribuir dos veces el mismo rendimiento.

## Consola de revisión por delta

`scripts/build_review_packet.py` produce `review-packet.json` y `review.html` desde el MP4 y todos los insumos materiales ligados por hash. La consola muestra beats, comparación, capas, impacto y previews parciales; recibe cambios estructurados como `inicio + fin + capa + elemento + instrucción`. Una decisión visible en la consola no sustituye `approval-receipt.json` ni autoriza entrega.

## Motor de estilos

El análisis decide primero qué debe comunicar cada beat y dónde existe espacio visual; después `scripts/score_style.py` puntúa los presets de `styles/catalog.json`. La selección exige un umbral absoluto y margen frente al segundo candidato; una abstención es preferible a imponer un look débil. El estilo es intercambiable por capas: puede cambiar paleta, tipografía, placas, transiciones y motion sin reconstruir montaje, voz, captions, activos aprobados ni zonas seguras. Si una variante cambia significado, orden, cortes o claims, exige una nueva revisión editorial.

El catálogo inicial contiene Tech Editorial Gold, Tech Editorial Color e Immersive Wellness. Todos continúan en `testing` hasta reunir resultados comparables en publicaciones reales.

## Máster editorial, máster social y derivados por plataforma

Cuando el material se conserva en HDR, `MASTER-PROFILE-EDITORIAL-HDR-001` define un mezzanine HEVC/ProRes de 10 bits para revisión y archivo. No se declara automáticamente listo para publicación. Después de aprobar su hash exacto, se genera un archivo distinto bajo `MASTER-PROFILE-SOCIAL-SDR-001`: 1080 × 1920, 9:16, 30 fps, H.264/AAC 48 kHz y BT.709. Ese segundo archivo cumple la función de máster social vertical neutral.

`scripts/check_master_profile.py` comprueba metadatos, loudness y linaje aprobado, pero nunca sustituye la revisión visual de la conversión HDR→SDR. Solo después del bloqueo de toma, cortes, voz, significado y activos se genera el máster de Instagram Reels. Ese MP4 se reutiliza en TikTok y Shorts cuando sea compatible. Los perfiles de `platforms/catalog.json` habilitan un delta únicamente si existe una diferencia material documentada; no pueden reabrir contenido aprobado. Las zonas numéricas son márgenes internos conservadores y siempre requieren preview real. El contrato completo vive en [platforms/README.md](platforms/README.md).

`scripts/build_publish_package.py` vuelve a verificar máster SDR, recibos SDR/HDR, reporte de perfil, catálogo y content lock antes de preparar derivados y briefs. El comando es de solo lectura salvo `--write`, materializa el paquete completo mediante staging y sellos finales, no sube nada y mantiene pendientes los gates de render, control técnico, preview real, correspondencia semántica y aprobación humana de publicación. `--force` solo puede reemplazar otro paquete válido y nunca una carpeta arbitraria.

## Métricas verificables por cohortes

`scripts/performance_cohorts.py` no acepta una fila de métricas aislada como evidencia. Cada observación debe resolver un registro de publicación hacia un paquete válido, el target correcto, un MP4 real inspeccionado con `ffprobe`, un control de entrega `ready`, evidencia local de publicación y captura, y un `creative-attribution.json` que seleccione una propuesta real del plan. Normaliza ventanas bilaterales de 24 h, 72 h y 7 días, tasas con denominador, confusores y ocho dimensiones creativas. El N efectivo conjunto es la intersección de publicaciones que contienen todas las métricas nucleares, no el menor conteo marginal ni el número de filas.

Las cohortes separan también cuenta, idioma, tema, campaña, periodo y moneda. Un confusor material limita la fuerza de la evidencia, y solo tiempos de producción con evidencia marcada `verified` entran en comparaciones; los autodeclarados se conservan sin mezclarlos. Los reportes se recomputan antes de consumirse, son descriptivos y no causales, exigen interpretación humana y nunca escriben reglas ni promociones automáticas.

Los hashes prueban integridad y linaje de los artefactos locales; no autentican por sí solos la identidad de una persona, una cuenta ni la exhaustividad de los datos remotos. Esa limitación permanece explícita en cada evidencia.

## Operación recurrente

- Radar diario: detecta cambios y señales; permanece silencioso cuando no hay novedades materiales.
- Informe semanal: consolida evidencia, caducidades y hasta tres decisiones accionables.
- Revisión previa a cada exportación: comprueba interfaz y zona segura reales de la plataforma.
- Revisión posterior: compara resultados propios dentro de contextos equivalentes.

Las instrucciones completas viven en [OPERACION_RADAR.md](OPERACION_RADAR.md). La gobernanza vive en [POLITICA_EDITORIAL.md](POLITICA_EDITORIAL.md).

## Directorios

- `config/`: cadencias, ventanas y prioridades operativas.
- `profiles/`: contexto predeterminado y futuros perfiles por cuenta.
- `profiles/creative_preferences.json`: preferencias explícitas y política contra sobreajuste.
- `platforms/`: perfil del máster neutral y perfiles derivados versionados por superficie.
- `sources/`: catálogo de fuentes con alcance y limitaciones.
- `rules/`: registro versionado de principios, requisitos e hipótesis.
- `research/observations/`: señales normalizadas, incluso cuando el resultado es “sin cambios relevantes”.
- `research/reports/`: informes semanales legibles.
- `experiments/`: pruebas, resultados y limitaciones.
- `decisions/`: snapshots seleccionados para proyectos.
- `library/`: recursos reutilizables con procedencia, incluidos SFX y música.
- `feedback/`: eventos atómicos de aprobación o corrección; nunca sustituye métricas de rendimiento.
- `learning/`: política conservadora para evaluar evidencia y producir recomendaciones no vinculantes.
- `creative-recipes/`: gramática modular y compatibilidades para propuestas contextuales.
- `template-bank/`: familias candidatas con aprobación del artefacto, reutilización, madurez y rendimiento separados.
- `master-profiles/`: contratos separados del mezzanine editorial HDR y el máster social SDR.
- `styles/`: catálogo, contrato de sustitución y presets visuales/motion reutilizables.
- `schemas/`: contratos de datos.
- `templates/`: formatos de brief, decisión e informe.
- `templates/cut-plan.json`: selección, arranque, pausas y empalmes de voz trazables antes del montaje.
- `templates/take-map.json`: mapa compartido de marcadores, decisiones y rangos del original.
- `templates/asset-lock.json`: snapshot inmutable de los recursos realmente autorizados para la edición.
- `templates/asset-index.json` y `templates/asset-usage-history.json`: búsqueda, deduplicación exacta, procedencia y fatiga no bloqueante.
- `templates/qa-scorecard.json`: gates técnicos y revisión editorial con evidencia por render.
- `templates/creative-blueprint.json`: estrategia, beats, emoción, descansos, face-safe y presupuestos.
- `templates/style-decision.json`: ranking reproducible o abstención documentada.
- `templates/production-board.json`: propiedad exclusiva y capacidad de tareas pesadas.
- `templates/dependency-map.json`: grafo para cambios por delta y caché segura.
- `templates/variant-plan.json`: variantes con cuerpo compartido bloqueado.
- `templates/golden-master-registry.json`: referencias aprobadas por hash y metadatos.
- `templates/approval-receipt.json`: aprobación explícita ligada al archivo y alcance exactos.
- `templates/review-packet.json`: revisión reproducible, impacto por capas y previews parciales.
- `templates/creative-recipe-plan.json`: hasta tres combinaciones modulares pendientes de selección humana.
- `templates/creative-attribution.json`: selección humana exacta de receta, familia primaria, contribuyentes y seis módulos, ligada al plan por hash.
- `templates/series-contract.json` y `templates/series-variety-ledger.json`: ADN de serie, familias, linaje y control de variedad.
- `templates/platform-master.json` y `templates/platform-adaptation.json`: gate del máster y derivados.
- `templates/content-lock-evidence.json` y `templates/publish-package.json`: inventario sellado y paquete multicanal sin publicación automática.
- `templates/recording-preflight.json` y `templates/performance-review.json`: entrada técnica y aprendizaje posterior contextual.
- `templates/publication-registry.json`, `templates/performance-observation.json`, `templates/performance-store.json` y `templates/performance-cohort-report.json`: linaje local de publicación, evidencia de métricas y análisis no causal.
- `templates/production-metrics.json`: eficiencia separada entre medición verificada y autodeclarada.
- `FLUJO_PRODUCCION_RAPIDA.md`: carriles paralelos, revisión por capas, aprendizaje y presupuesto de renders.
- `INGESTA_MAESTRA.md`: transcripción única, revisión humana de marcadores y proxies por video.
- `QA_PROFESIONAL.md`: contrato verificable que bloquea la entrega ante defectos críticos.
- `OPERACION_OPTIMIZACION.md`: carriles, gates y orden de uso para el lote completo.

## Toolchain de referencia

- Skills oficiales instaladas: `hyperframes` y `media-use`.
- Versión fijada para la composición, validación y render del ciclo actual: HyperFrames `0.8.75`.
- `media-use` resuelve y congela recursos locales; todo logo, imagen, audio o LUT debe conservar procedencia en el manifiesto del proyecto.
- El editable mantiene voz, música y SFX separados. El MP4 final aplana las capas, pero nunca reemplaza el proyecto fuente ni un render anterior validado.
- Las actualizaciones de herramienta requieren una nueva validación antes de cambiar la versión fijada de un proyecto en curso.
- `scripts/preflight_project.py` valida estilos, originales, hashes, manifiestos y elegibilidad de activos antes de editar o renderizar.
- `scripts/check_recording_preflight.py` inspecciona grabaciones con `ffprobe` antes de transcribir.
- `scripts/production_board.py` protege ownership y capacidad; `change_impact.py` y `cache_key.py` gobiernan el retrabajo.
- `scripts/score_style.py` selecciona o se abstiene; `golden_master.py` registra y compara referencias sin renderizarlas.
- `scripts/approval_receipt.py` prepara, sella y verifica aprobaciones por hash, incluidas decisiones retrospectivas con `created_at`, `decided_at` y `recorded_at` separados; sin `--write` no modifica archivos. SHA-256 protege integridad, no identidad criptográfica.
- `scripts/check_master_profile.py` valida el rol técnico y el linaje HDR→SDR sin transcodificar.
- `scripts/learning_engine.py` ingesta evidencia y genera recomendaciones contextuales pendientes de revisión humana.
- `scripts/series_memory.py` extrae fingerprints, exige QA técnica verificable ligada al mismo artefacto para aprender defaults estables, y gobierna familias y variedad sin puntuar calidad.
- `scripts/plan_platform_derivatives.py` prepara deltas y `check_platform_delivery.py` valida cada archivo de destino.
- `scripts/asset_intelligence.py` crea y consulta el índice semántico con duplicación exacta, exclusiones y cooldowns explicados.
- `scripts/compose_recipe.py` propone recetas modulares contextuales con abstención y atribución familiar inequívoca.
- `scripts/build_review_packet.py` convierte un render y feedback estructurado en una consola y previews por delta.
- `scripts/build_publish_package.py` prepara un paquete multicanal únicamente desde evidencia SDR/HDR y content lock revalidados.
- `scripts/performance_cohorts.py` verifica linaje local, MP4, evidencia, atribución creativa y reportes recomputables antes de generar cohortes descriptivas.
- `scripts/validate_framework.py` comprueba los contratos del núcleo; una validación fallida impide declarar vigente una nueva versión.

## Regla para nuevos proyectos

Cada proyecto debe enlazar este núcleo, no copiarlo. Los valores específicos —por ejemplo, escala de zoom, volumen de música o densidad de captions— son presets del estilo o hipótesis del video; no reglas universales.

## Dirección de imágenes confirmada — 2026-09-30

[IMAGENES_CONTEXTO_REALISMO.md](IMAGENES_CONTEXTO_REALISMO.md): selección por frase real, generación contextual preferida ante recursos inadecuados, fotografía natural y QA de plausibilidad/integración. Preferencia `PREF-IMAGE-CONTEXT-REALISM-001` y regla `CONTEXTUAL_REALISTIC_IMAGE_REPLACEMENT`.


## Selección versionada de flujo de edición

Flujo1actual sigue predeterminado. Por petición «con flujo2» o «con flujo3», aplicar [GUIA de perfiles](workflow-profiles/GUIA.md), su perfilJSON y [QA común](workflow-profiles/QA_COMUN.md), conservando las reglas vigentes. Estos perfiles son experimentales;2organiza/reutiliza trabajo comprobado,3simplifica alcance creativo sin omitir controles requeridos. La preparación delpiloto1deoctubre vive en [PRUEBA26–30](workflow-profiles/experiments/2026-10-01-lote26-30/PRUEBA.md). Registrar run/versiones/tiempos y separar espera humana/auditoríaextra. Procedimiento anterior conservado como referencia1; esta selección cambia organización/alcance declarado, no autorización, ingesta, fidelidad, QA ni aprobación.


## Fidelidad y diversidad visual — 2026-09-30

Aplicar [FIDELIDAD_Y_DIVERSIDAD_PLANTILLAS.md](FIDELIDAD_Y_DIVERSIDAD_PLANTILLAS.md) a nuevos videos/lotes. La identidad incluye estructura, composición, recursos gráficos, encuadre y movimiento, además de color/tipografía. Consultar original y vecinos; completar `VIDEO-NN/QA_FIDELIDAD_PLANTILLA.md` desde [la plantilla de revisión](templates/template-fidelity-review.md), antes del render y sobre el MP4 exacto. El check técnico no acredita esta revisión editorial. Conservar minimalismo cuando sea propio del estilo y evitar huecos/crops accidentales o gráficos sin función.
