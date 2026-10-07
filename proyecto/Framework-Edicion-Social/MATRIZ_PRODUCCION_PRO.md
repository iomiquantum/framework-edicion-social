# Matriz operativa de producción profesional

Esta matriz convierte el framework en una cadena verificable. La edición rápida no depende de recordar instrucciones: cada etapa produce un artefacto, tiene un responsable y bloquea únicamente lo que realmente quedó inválido.

## Núcleo 1.4 — ocho módulos de producción

| # | Módulo | Artefacto principal | Qué evita | Gate de salida |
| ---: | --- | --- | --- | --- |
| 1 | Preflight de grabación | `recording-preflight.json` | Transcribir material sin audio, resolución útil o metadatos mínimos | Sin hard fail técnico |
| 2 | Blueprint creativo | `creative-blueprint.json` | Añadir imágenes, zooms, motion o SFX sin función narrativa | Cada beat tiene intención, trazabilidad, descanso y presupuesto |
| 3 | Selección explicable de estilo | `style-decision.json` | Elegir un look por intuición o forzarlo cuando no encaja | Umbral y margen superados, o abstención válida |
| 4 | Tablero de producción | `production-board.json` | Dos tareas escribiendo el mismo `VIDEO-NN` o demasiados renders simultáneos | Un propietario por video y capacidad heavy disponible |
| 5 | Impacto y caché | `dependency-map.json`, `cache-manifest.json` | Rehacer todo por un cambio local o reutilizar resultados obsoletos | Solo se invalidan dependencias transitivas; hashes coinciden |
| 6 | Variantes controladas | `variant-plan.json` | Comparar piezas donde cambiaron demasiadas variables | Cuerpo compartido bloqueado y una familia de cambios declarada |
| 7 | Golden master | `golden-master-registry.json` | Sobrescribir una versión aprobada o heredar su aprobación a otro archivo | Hash y metadatos del aprobado coinciden |
| 8 | Derivados y aprendizaje | `platform-master.json`, `platform-adaptation.json`, `performance-review.json` | Reeditar por red o convertir métricas incomparables en reglas | Máster aprobado/bloqueado, preview real y revisión humana del rendimiento |

## Extensión 1.5 — aprendizaje sin congelar creatividad

| # | Módulo | Artefacto principal | Qué evita | Gate de salida |
| ---: | --- | --- | --- | --- |
| 9 | Aprobación atómica | `approval-receipt.json` | Aplicar una aprobación a otra versión, capa, plantilla o derivado | Hash, tamaño, rol, alcance y evidencia explícita coinciden |
| 10 | Doble máster | perfiles `editorial_mezzanine` y `social_delivery_master` | Publicar HDR impredecible o destruir el original al convertir | HDR preservado; SDR BT.709 distinto, trazable y revisado |
| 11 | Memoria de serie | `series-contract.json`, fingerprint y variety ledger | Copiar ciegamente el piloto o perder identidad entre episodios | `locked`, `bounded`, `rotating` y `free` comprobados; similitud no puntúa calidad |
| 12 | Motor y portafolio | eventos de evidencia + reporte de recomendación | Sobreajustar por una aprobación o elegir una plantilla universal | Recomendación contextual, no vinculante y pendiente de revisión humana |

## Extensión 1.6 — optimización conectada y verificable

| # | Módulo | Artefacto principal | Qué evita | Gate de salida |
| ---: | --- | --- | --- | --- |
| 13 | Índice semántico y antifatiga | `asset-index.json`, `asset-usage-history.json` | Regenerar recursos existentes, reutilizar rechazados o confundir ranking textual con similitud visual | Hash/procedencia válidos, contraindicaciones respetadas y cooldown solo consultivo |
| 14 | Compilador de recetas | catálogo modular + `creative-recipe-plan.json` + `creative-attribution.json` | Repetir una plantilla completa, decorar sin contexto o atribuir rendimiento a una receta no elegida | Hasta tres opciones compatibles; selección humana exacta ligada al plan por hash |
| 15 | Consola de revisión | `review-packet.json`, `review.html` | Reinterpretar feedback o rehacer capas aprobadas | Insumos hash-bound, cambios estructurados, impacto calculado y recibo de aprobación separado |
| 16 | Paquete multicanal | `content-lock-evidence.json`, `publish-package.json` | Publicar desde HDR, un máster distinto, rutas manipuladas o un proyecto alterado | SDR/HDR/recibos/perfil/lock revalidados; paquete sellado y gates de destino pendientes |
| 17 | Registro y cohortes | registro, evidencia, store y reporte de cohortes | Aprender de capturas huérfanas, atribución inventada, filas duplicadas o comparaciones incompatibles | MP4 real, linaje/evidencia local, ventana válida, N de intersección y revisión humana no causal |

## Flujo completo

```text
grabación
  → preflight técnico
  → ingesta única + take-map + proxies
  → propietario exclusivo de VIDEO-NN
  → transcripción/toma aprobada
  → blueprint creativo
  → consulta semántica + recetas contextuales
  → selección humana + atribución creativa ligada al plan
  → estilo seleccionado o abstención
  → asset-lock + dependency-map + cache key
  → montaje por capas
  → consola de revisión + cambios por delta + previews parciales
  → QA + revisión humana
  → recibo de aprobación ligado al hash
  → mezzanine editorial HDR aprobado, cuando corresponda
  → máster social SDR BT.709 derivado y revisado
  → golden master inmutable
  → content lock sellado + máster Instagram universal
  → preview real por plataforma sobre el mismo hash
  → variante adicional solo si existe diferencia material
  → publicación
  → registro con evidencia local + ventanas de rendimiento + cohortes contextuales
  → fingerprint + memoria de serie + variedad
  → recomendación del motor
  → revisión humana de hipótesis, default o familia de plantilla
```

## Estados que no se pueden confundir

| Estado | Pregunta que responde | No demuestra |
| --- | --- | --- |
| `qa_status` | ¿El archivo supera controles técnicos y editoriales del render exacto? | Que guste o que vaya a rendir bien |
| `user_approval_status` | ¿El usuario aprobó explícitamente esta versión? | Que otra variante también esté aprobada |
| `content_lock` | ¿Toma, cortes, voz, significado y activos están congelados? | Que la UI de cada plataforma esté revisada |
| `platform_delivery_status` | ¿El derivado supera exportación y preview real para su destino? | Que tenga mejor rendimiento |
| `performance_status` | ¿Existen datos comparables posteriores a publicación? | Causalidad automática |
| `reuse_status` | ¿Puede reutilizarse este recurso o receta y con qué alcance? | Que deba usarse en todos los videos |

## Regla de cambios por delta

Antes de modificar, expresar la solicitud como `tiempo + capa + elemento + cambio` y ejecutar `change_impact.py`. La salida lista capas y artefactos invalidados.

| Cambio solicitado | Se conserva | Se invalida normalmente | Render de revisión |
| --- | --- | --- | --- |
| Color o tipografía | toma, cortes, voz, timing de captions, assets | lookdev, composición y controles de contraste | segmento afectado; final completo al entregar |
| Imagen o icono | montaje y mezcla | asset-lock, lookdev, escena y límites vecinos | escena afectada |
| Zoom o transición | guion, voz, assets | cámara/motion del rango y continuidad adyacente | tramo + handles |
| Música o SFX | capas visuales | mezcla y controles de inteligibilidad/picos | audio del tramo; escucha final completa |
| Corrección de una palabra de caption | montaje y voz | caption y QA de sincronía/legibilidad | tramo afectado |
| Cambio de toma, cortes o significado | recursos todavía pertinentes | narrativa y todas sus dependencias | nueva aprobación del máster |
| Adaptación de plataforma | contenido bloqueado del máster + diferencia material documentada | layout, saltos de captions, CTA equivalente, exportación | derivado completo + preview real; sin diferencia se reutiliza el máster Instagram |

El MP4 de entrega se codifica completo porque aplana las capas. Eso no significa reconstruir todo: el cálculo de impacto, el proyecto por capas y la caché conservan el trabajo no afectado.

## Concurrencia segura

1. `production-board.json` se crea una vez en la raíz del lote.
2. Una tarea reclama `VIDEO-NN` antes de escribir y lo libera al terminar.
3. Un reclamo repetido por el mismo owner es idempotente; otro owner recibe conflicto.
4. Transcripción, codificación y render cuentan como carga `heavy`.
5. El límite inicial es dos heavy jobs por equipo; se ajusta solo con medición real.
6. Framework, originales e ingesta compartida permanecen de solo lectura para tareas individuales.

Ejemplo:

```bash
python3 Framework-Edicion-Social/scripts/production_board.py \
  --board Serie/production-board.json init \
  --project-id serie --max-heavy-jobs 2

python3 Framework-Edicion-Social/scripts/production_board.py \
  --board Serie/production-board.json claim \
  --video VIDEO-01 --owner tarea-video-01 --workload heavy
```

## Artefactos mínimos por video

```text
VIDEO-NN/
├── source/                         # proxy + rango exacto del original
├── recording-preflight.json        # o referencia al preflight del lote
├── cut-plan.json
├── creative-blueprint.json
├── creative-recipe-plan.json
├── creative-attribution.json       # solo después de elegir una propuesta real
├── style-decision.json
├── asset-lock.json
├── dependency-map.json
├── cache-manifest.json
├── variant-plan.json               # solo si existe una prueba controlada
├── editable-hyperframes-*/
├── qa/
├── review/
│   ├── review-packet.json
│   └── review.html
├── platform-master.json
├── approval-receipt.json           # ligado al SHA-256 y al alcance aprobados
├── series-conformance.json         # identidad y variedad
├── platform-adaptation.json        # solo después de aprobar el máster
├── content-lock-evidence.json       # inventario sellado antes del paquete
├── publish/                         # derivados y briefs; nunca subida automática
├── golden-master-registry.json
└── performance-review.json         # después de publicar y medir
```

La memoria compartida usa una única ruta canónica:

```text
SERIE/series-memory/
├── series-contract.json
├── series-variety-ledger.json
└── fingerprints/
    └── VIDEO-NN.json               # descripción; no nota de calidad
```

El lote mantiene además dos almacenes compartidos que no se copian por video:

```text
SERIE/asset-intelligence/
├── asset-index.json
└── usage-history.json

SERIE/performance/
├── publication-registry.json
├── performance-store.json
└── reports/
```

Cada captura de métricas vive como evidencia local dentro del video o de `performance/` y se referencia por ruta + SHA. Los hashes prueban integridad local, no autenticidad remota. Los tiempos de producción autodeclarados se conservan, pero solo los marcados `verified` con evidencia participan en comparaciones.

El contrato conserva identidad, rangos y familias de plantilla; el ledger registra snapshots inmutables para detectar deriva o monotonía sin reemplazar la revisión creativa. `series-conformance.json` permanece dentro del video porque describe la comparación puntual de ese candidato contra la memoria compartida.

## Máster y perfiles por plataforma

El formato de producción base es `PLATFORM-MASTER-VERTICAL-001`: 1080 × 1920, 9:16, 30 fps, MP4/H.264, AAC-LC 48 kHz y BT.709. El máster de publicación por defecto es Instagram Reels y se reutiliza sin otro render en TikTok y Shorts cuando encuadre, safe zones, CTA, duración y especificaciones sean compatibles. Cuando la edición se conserva en HDR existe antes un mezzanine editorial separado; su aprobación se registra por hash y la conversión SDR se valida como un derivado distinto.

Después de la aprobación explícita:

- Instagram Reels: reflujo para controles laterales/inferiores y CTA del contexto de Instagram.
- TikTok: reflujo para columna derecha y bloque inferior; captions especialmente conservadores.
- YouTube Shorts: elegibilidad de orientación/duración, codificación y reflujo para controles de Shorts.

Las coordenadas del catálogo son márgenes internos conservadores, no especificaciones oficiales. Siempre se comprueba la vista previa real y esa revisión queda ligada al SHA-256 exacto. Distintas plataformas pueden compartir el mismo hash; solo una diferencia material documentada habilita otro render.

## Definición de terminado

Un video está listo cuando:

- proviene de una toma aprobada y un rango verificable del original;
- blueprint, estilo, activos y montaje conservan trazabilidad;
- no existe conflicto de propietario ni resultado de caché obsoleto;
- el QA del hash exacto no tiene hard fails ni revisiones pendientes;
- el usuario aprobó explícitamente ese máster;
- el golden master fue registrado sin sobrescribir otro;
- si existe un destino concreto, su derivado pasó preview y QA propios;
- cualquier aprendizaje posterior conserva contexto y revisión humana.
