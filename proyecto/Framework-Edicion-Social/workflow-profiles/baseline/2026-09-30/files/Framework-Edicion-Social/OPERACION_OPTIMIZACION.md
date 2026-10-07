# Operación acelerada para un lote de 30 videos

Este contrato conecta las optimizaciones del framework sin convertirlas en atajos de calidad. La meta no es producir 30 videos iguales: es evitar que cada video vuelva a pagar el costo de descubrir, verificar y reconstruir lo que ya existe.

## Principio operativo

```text
analizar una vez
  → proponer con contexto
  → editar por capas
  → revisar por delta
  → aprobar el hash exacto
  → reutilizar máster de Instagram; derivar solo ante diferencia material
  → aprender solo de publicaciones y métricas con evidencia ligada
```

Son operaciones independientes:

- buscar un activo no lo aprueba;
- proponer una receta no la selecciona;
- mostrar una decisión en la consola no crea una aprobación;
- construir un paquete no publica nada;
- observar una métrica no demuestra causalidad ni promueve una regla.

## Carriles paralelos

| Carril | Trabajo | Carga | Puede avanzar mientras |
| --- | --- | --- | --- |
| Ingesta compartida | hash, audio, transcripción, marcadores, `take-map` y proxies | pesada | se preparan recursos de otros videos |
| Inteligencia de activos | índice, duplicados exactos, búsquedas y cooldowns | ligera | otro video renderiza |
| Dirección creativa | blueprint y hasta tres recetas contextuales | ligera | se termina el video anterior |
| Edición | montaje, capas, motion, mezcla y captions de un `VIDEO-NN` | media/pesada | otras tareas trabajan en carpetas distintas |
| Revisión | paquete hash-bound, cambios y previews parciales | ligera/media | se prepara el siguiente blueprint |
| Entrega | SDR, máster universal de Instagram y variantes materialmente justificadas | pesada | solo después de aprobación exacta |
| Aprendizaje | uso real, producción y métricas de publicación | ligera | nunca bloquea editar el siguiente video |

Solo un propietario puede escribir un `VIDEO-NN`. Transcripción, transcodificación y render comparten el límite inicial de dos procesos pesados simultáneos.

## Ciclo del lote

### 1. Preparar el lote una sola vez

1. Ejecutar preflight sobre cada maestro.
2. Transcribir y revisar marcadores una sola vez.
3. Crear un proxy y rango exacto por video.
4. Inicializar el tablero de producción.
5. Construir el índice semántico desde catálogo, manifests, locks y manifiestos de `media-use`.

El índice deduplica únicamente cuando el SHA-256 coincide. El ranking semántico usa texto declarado; no debe presentarse como similitud visual perceptual.

### 2. Preparar cada video antes del montaje

1. Reclamar `VIDEO-NN` en el tablero.
2. Usar la toma aprobada y su transcripción como fuente final de verdad.
3. Completar `creative-blueprint.json`.
4. Consultar activos por intención y tipo.
5. Compilar de una a tres recetas de seis módulos: hook, estructura, sistema visual, motion, sonido y CTA.
6. Elegir humanamente una propuesta o solicitar otra; una abstención del compilador es válida.
7. Si se elige una propuesta, registrar `creative-attribution.json` contra el plan exacto: opción, receta, familia primaria, contribuyentes y seis módulos.
8. Congelar estilo, activos y dependencias antes de construir escenas.

La penalización por fatiga solo cambia el orden de revisión. Nunca convierte una opción en mala, bloquea un activo pertinente ni sustituye el criterio editorial.

### 3. Editar y revisar por delta

1. Mantener montaje, voz, captions, gráficos, imágenes, motion, música y SFX en capas separadas.
2. Renderizar una primera versión con manifiesto ligado al archivo.
3. Crear `review-packet.json` y `review.html` desde render, manifiesto, blueprint y mapa de dependencias congelados por hash.
4. Registrar cada solicitud como `inicio + fin + capa + elemento + instrucción`.
5. Calcular impacto transitivo y conservar las capas no afectadas.
6. Renderizar previews cortos con handles para las correcciones.
7. Hacer un render completo únicamente cuando el candidato vaya a QA final o entrega.

Un MP4 final siempre se codifica completo porque aplana las capas. Eso no obliga a reconstruir las capas no afectadas ni a revisar repetidamente todo el maestro original.

### 4. Aprobar y preparar publicación

1. Completar QA técnico y editorial del hash candidato.
2. Crear el recibo de aprobación del artefacto exacto.
3. Conservar el mezzanine editorial HDR cuando corresponda.
4. Derivar y revisar un máster social SDR BT.709 distinto.
5. Aprobar por separado el hash del SDR.
6. Construir por defecto únicamente el máster de Instagram Reels desde ese SDR.
7. Verificar el mismo archivo en TikTok y Shorts; si es compatible, reutilizar su hash. Renderizar otra variante solo cuando una diferencia material quede registrada y después verificarla por separado.

El paquete contiene planes, manifests, briefs, portadas/copy previstos y linaje. No sube archivos ni inventa que un destino está listo. Si falla el recibo, el perfil, el content lock, un hash o un gate de destino, se detiene.

### 5. Aprender sin contaminar la memoria

Después de una aprobación:

- registrar solo los activos que realmente sobrevivieron al render aprobado;
- guardar tiempos, rondas, previews, renders y causas de retrabajo;
- actualizar fingerprint y ledger sin promocionar una plantilla;
- conservar recomendaciones como propuestas pendientes de revisión.

Después de una publicación real:

- registrar el paquete y derivado local exactos, su control de entrega, una referencia de la publicación y evidencia local ligada por hash;
- ligar cada captura de métricas a su propio archivo de evidencia y a la receta que una persona seleccionó realmente;
- capturar ventanas cercanas a 24 h, 72 h y 7 días;
- normalizar tasas con denominadores explícitos;
- comparar solo plataforma, superficie, perfil, cuenta, idioma, tema, campaña, periodo, moneda, audiencia, duración y ventana compatibles;
- exigir tamaño efectivo por métrica y la intersección real de publicaciones con todas las métricas nucleares;
- reportar confusores y variación creativa antes de interpretar resultados.

El reporte de cohortes es descriptivo y no causal. No puede escribir reglas, elegir un ganador universal ni aprobar una promoción. SHA-256 comprueba la integridad local del archivo de evidencia, no autentica la plataforma, la cuenta o la persona; esa limitación nunca se oculta.

## Estructura recomendada

```text
SERIE/
├── production-board.json
├── asset-intelligence/
│   ├── asset-index.json
│   └── usage-history.json
├── performance/
│   ├── publication-registry.json
│   ├── performance-store.json
│   └── reports/
└── VIDEO-NN/
    ├── creative-blueprint.json
    ├── creative-recipe-plan.json
    ├── creative-attribution.json
    ├── asset-lock.json
    ├── dependency-map.json
    ├── production-metrics.json
    ├── metrics-24h.json           # solo tras una captura real
    ├── review/
    │   ├── review-packet.json
    │   └── review.html
    ├── qa/
    ├── approval-receipt.json
    ├── platform-master.json
    └── publish/
```

La estructura es una convención; ningún archivo vacío satisface un gate. Cada artefacto debe validar contra su schema y, cuando corresponda, volver a comprobar el archivo y hash que declara.

## Comandos de operación

Cada comando ofrece `--help`; las rutas siguientes muestran la relación entre artefactos y deben sustituirse por las del `VIDEO-NN` real.

### Buscar recursos

```bash
python3 Framework-Edicion-Social/scripts/asset_intelligence.py query \
  --project-root Serie-IA-Negocios-10-Videos \
  --index asset-intelligence/asset-index.json \
  --intent "concepto exacto del beat" \
  --type image \
  --current-video-sequence 3 \
  --as-of 2026-09-25 \
  --limit 5
```

Al reconstruir el índice, repetir `--manifest` por cada manifiesto gobernado y proporcionar `--usage-history`. La salida se escribe solo en la ruta explícita de `--out`.

### Proponer recetas

```bash
python3 Framework-Edicion-Social/scripts/compose_recipe.py \
  --blueprint Serie-IA-Negocios-10-Videos/VIDEO-NN/creative-blueprint.json \
  --series-contract Serie-IA-Negocios-10-Videos/series-memory/series-contract.json \
  --series-memory Serie-IA-Negocios-10-Videos/series-memory/series-variety-ledger.json \
  --asset-index Serie-IA-Negocios-10-Videos/asset-intelligence/asset-index.json \
  --count 3 \
  --out Serie-IA-Negocios-10-Videos/VIDEO-NN/creative-recipe-plan.json
```

### Crear la consola de revisión

```bash
python3 Framework-Edicion-Social/scripts/build_review_packet.py \
  --project-root Serie-IA-Negocios-10-Videos/VIDEO-NN \
  --project-id SERIE-IA-NEGOCIOS \
  --video-id VIDEO-NN \
  --render VIDEO-NN_REVISION_v1.mp4 \
  --manifest manifest-render.json \
  --dependency-map dependency-map.json \
  --blueprint creative-blueprint.json \
  --out review \
  --write
```

Cuando haya feedback estructurado, añadir `--changes changes.json`. Si existe una versión anterior, añadir `--previous-render`. Cambiar un insumo después de construir el paquete invalida su verificación.

### Preparar derivados

```bash
python3 Framework-Edicion-Social/scripts/build_publish_package.py \
  --master-manifest Serie-IA-Negocios-10-Videos/VIDEO-NN/platform-master.json \
  --master-media Serie-IA-Negocios-10-Videos/VIDEO-NN/social-master.mp4 \
  --approval-receipt Serie-IA-Negocios-10-Videos/VIDEO-NN/social-master-approval.json \
  --source-approval-receipt Serie-IA-Negocios-10-Videos/VIDEO-NN/editorial-master-approval.json \
  --master-profile-report Serie-IA-Negocios-10-Videos/VIDEO-NN/social-master-profile-report.json \
  --content-lock-evidence Serie-IA-Negocios-10-Videos/VIDEO-NN/content-lock-evidence.json \
  --out-dir Serie-IA-Negocios-10-Videos/VIDEO-NN/publish
```

La primera ejecución es dry-run. Solo después de revisar una salida no bloqueada se repite con `--write`. Este paso construye el paquete local; nunca sube ni publica.

### Ingerir y reportar rendimiento

```bash
python3 Framework-Edicion-Social/scripts/performance_cohorts.py ingest \
  --project-root Serie-IA-Negocios-10-Videos \
  --publication-registry performance/publication-registry.json \
  --store performance/performance-store.json \
  --input performance/captura-24h.json \
  --write

python3 Framework-Edicion-Social/scripts/performance_cohorts.py report \
  --project-root Serie-IA-Negocios-10-Videos \
  --publication-registry performance/publication-registry.json \
  --store performance/performance-store.json \
  --production-metrics VIDEO-NN/production-metrics.json \
  --out performance/reports/cohort-report.json \
  --write
```

El `--input` no es una fila libre: debe contener referencias con ruta y SHA a `creative-attribution.json` y a la evidencia de esa captura de métricas. La ingesta falla si no puede volver a leer esos mismos bytes, resolver el plan/receta seleccionados, inspeccionar el MP4 con `ffprobe` y comprobar paquete, perfil y delivery-check. El registro de publicación conserva también evidencia local y referencia de origen. Un reporte se escribe sin sobrescribir otro ID, vuelve a calcular sus cohortes antes de consumirse y no autoriza una decisión editorial.

`production-metrics.json` puede conservar tiempos `self_reported`, pero solo registros `verified` con evidencia ligada entran en comparaciones de eficiencia.

### Verificar el núcleo

```bash
python3 -m unittest discover -s Framework-Edicion-Social/scripts/tests -p 'test_*.py' -v
python3 Framework-Edicion-Social/scripts/validate_framework.py
```

## Presupuesto de renders

| Momento | Salida | Propósito |
| --- | --- | --- |
| Montaje | preview de baja/mediana resolución | revisar estructura y ritmo |
| Cambio localizado | tramo afectado con handles | verificar el delta |
| Bloqueo editorial | render completo de revisión | validar continuidad global |
| QA final | render completo de máxima calidad | aprobar el hash exacto |
| Plataforma | encode completo por destino | validar códec, layout y UI real |

## Gates que nunca se omiten

- toma y rango fuente verificables;
- rostro, voz, captions y sujetos principales protegidos;
- relevancia semántica y procedencia de activos;
- dependencias y caché ligadas a hashes actuales;
- hard gates de QA en `pass`;
- aprobación explícita del archivo exacto;
- SDR distinto y trazable antes del paquete social;
- publicación registrada, MP4 inspeccionado y evidencia local antes de métricas;
- revisión humana antes de promover cualquier aprendizaje.

## Cadencia recomendada para los 30 videos

- Mientras se corrige el video actual, preparar blueprint, búsquedas y recetas del siguiente.
- Al aprobar un video, actualizar uso real, memoria y métricas de producción antes de liberar su owner.
- Cada cinco videos, revisar tiempos, retrabajo, consultas de activos y diversidad de recetas.
- Cada diez videos, recalibrar familias y rangos con revisión humana; no cambiar silenciosamente defaults.
- Revisar rendimiento de redes solo cuando existan publicaciones comparables suficientes.

Así el ahorro crece con el lote: el análisis y la evidencia se reutilizan, mientras la estructura y el lenguaje creativo continúan variando según el mensaje.

## Mejora continua desde el lote 21–25

Aplicar [MEJORA_FLUJO_21_25.md](MEJORA_FLUJO_21_25.md): medir por fase, comprobar primero transiciones críticas en segmentos del pipeline final, revisar por delta y registrar causa del retrabajo después de cada video. El ahorro debe demostrarse con tiempos comparables; las tres pasadas y los gates del candidato exacto siguen obligatorios.

## Control temprano y mejora desde el lote 16–20

Aplicar [MEJORA_FLUJO_16_20.md](MEJORA_FLUJO_16_20.md) junto al ciclo de mejora 21–25: validar salud del ASR antes de mapas/captions, preparar revisión compacta de tomas y dudas, reutilizar análisis por hash, revisar cambios locales primero y medir por fase. Los pilotos de limpieza son condicionales; la regla de voz cubre el lote16–20 y próximas ediciones. Cada cierre de video añade defecto/causa/prevención; cada cinco videos compara datos equivalentes. No convertir tiempos de recuperación ASR en ahorro global ni sustituir las tres pasadas finales.

## Mejora continua vigente — 2026-09-30

Aplicar `MEJORA_CONTINUA.md` al iniciar el lote y cerrar cada video. Incluye prioridades medidas, registro automático de comandos y prevención de rutas/entradas duplicadas. La excepción provisional vigente en AGENTS de serie sustituye el requisito histórico de detener todo montaje por falta de escucha: mantener sus límites y recibo provisional. Las instrucciones anteriores se conservan como antecedente y no permiten inventar aprobación.
