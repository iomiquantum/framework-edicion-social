# Ingesta maestra de grabaciones por lote

## Decisión operativa

Cada archivo maestro se inspecciona y transcribe **una sola vez**. No se vuelve a recorrer el mismo MOV por cada video. La ingesta produce un mapa de tomas y proxies de trabajo; los renders finales continúan leyendo los rangos exactos del original.

```text
MOV original inmutable
  → selección de pista de audio por escucha
  → transcripción única con tiempos por palabra
  → detección de marcadores
  → revisión de take-map.json
  → proxies independientes por toma aprobada
  → edición paralela por VIDEO-NN
  → render final desde el MOV original
```

## Artefactos

- `00-INGESTA/source-manifest.json`: identidad, hash y datos técnicos de cada maestro.
- `00-INGESTA/<lote>.recording-preflight.json`: inspección técnica inicial de solo lectura.
- `00-INGESTA/<lote>.transcript.json`: transcripción única del maestro.
- `00-INGESTA/take-map-XX-YY.json`: marcadores, decisiones y rangos fuente.
- `VIDEO-NN/source/<take-id>-proxy.mp4`: archivo liviano solo para previsualización/edición.
- `VIDEO-NN/source/<take-id>-source-range.json`: vínculo exacto entre proxy y MOV original.
- `VIDEO-NN/cut-plan.json`: refinamiento de fonemas, pausas y empalmes dentro de la toma seleccionada.

## Secuencia obligatoria

1. Conservar y hashear el MOV original.
2. Ejecutar `check_recording_preflight.py`; un hard fail técnico bloquea transcripción y proxies, mientras un warning queda documentado para revisión.
3. Ejecutar `preflight_project.py --stage ingest --deep`; corregir cualquier error de identidad, hash, recurso o estilo antes de iniciar procesos pesados.
4. Escuchar muestras de cada pista de audio y fijar `audio_stream_selection`/`audio_stream_index`; nunca elegir por posición sin escuchar.
5. Transcribir el archivo completo una sola vez en español con tiempos por palabra. Especificar idioma/modelo; no utilizar un modelo `.en`.
6. Ejecutar `scripts/build_take_map.py`.
7. Revisar todos los marcadores detectados. Resolver tomas abiertas, decisiones huérfanas, correcciones parciales, marcadores desconocidos y múltiples aprobaciones. En una corrección `MARCADOR. Corregir, corregir. Última frase.`, escuchar ambas versiones, delimitar la frase anterior completa y la repetición nueva, registrar los rangos en el `take-map` y cambiar su estado a `resolved`; la puntuación automática no basta. Solo entonces cambiar `qa.human_review_completed` a `true`.
8. Ejecutar `scripts/build_take_proxies.py`. Los proxies eliminan la necesidad de que cada tarea vuelva a inspeccionar el maestro.
9. Ejecutar `preflight_project.py --stage edit` para confirmar que cada video solicitado tiene toma, proxy y rango original válidos.
10. Inicializar `production-board.json` y reclamar cada `VIDEO-NN` antes de asignarlo: una tarea puede escribir `VIDEO-02`, otra `VIDEO-03`, etc. El framework y `00-INGESTA` permanecen de solo lectura durante esas ediciones.
11. Limitar procesos pesados simultáneos con el tablero: transcripciones y renders se encolan; el trabajo creativo puede avanzar en paralelo. Como regla inicial, no ejecutar más de dos codificaciones pesadas a la vez en el mismo equipo.
12. En el render final, usar `original_source + source_in_s + source_out_s`; el proxy nunca sustituye la fuente de cámara.

## Comandos de referencia

```bash
python3 Framework-Edicion-Social/scripts/check_recording_preflight.py \
  --source "00-INGESTA/LOTE-VIDEOS-01-05-ORIGINAL.MOV" \
  --out "00-INGESTA/lote-01-05.recording-preflight.json"

npx hyperframes transcribe \
  "00-INGESTA/LOTE-VIDEOS-01-05-ORIGINAL.MOV" \
  --model small --language es

python3 Framework-Edicion-Social/scripts/build_take_map.py \
  --transcript "00-INGESTA/lote-01-05.transcript.json" \
  --source "00-INGESTA/LOTE-VIDEOS-01-05-ORIGINAL.MOV" \
  --source-id SOURCE-VIDEOS-01-05 \
  --project-id serie-ia-negocios-10-videos \
  --source-sha256 '<hash verificado>' \
  --fps 30 --audio-stream-index 1 \
  --language es --engine hyperframes \
  --out "00-INGESTA/take-map-01-05.json"

python3 Framework-Edicion-Social/scripts/build_take_proxies.py \
  --take-map "00-INGESTA/take-map-01-05.json" \
  --project .
```

## Control de calidad

La detección automática propone rangos, pero no aprueba por inferencia. Un proxy solo se crea cuando:

- el marcador de inicio pertenece inequívocamente a `VIDEO-NN / TAKE-NN`;
- existe una decisión `approved` inequívoca;
- toda corrección parcial tiene `target_range` y `replacement_range` verificados por escucha, estado `resolved` y una decisión equivalente en `cut-plan.json`;
- la pista de audio fue escuchada y seleccionada;
- `take-map.json` fue revisado;
- el rango no invade el marcador siguiente;
- el proxy conserva referencia y hash del original;
- el proxy contiene video y audio, su duración coincide con el rango esperado y su propio hash queda registrado;
- una escritura interrumpida no se presenta como proxy válido: primero se genera un archivo parcial, se verifica y solo entonces se promueve al nombre final.

Si existen varias tomas aprobadas, se generan todas o se selecciona una tras comparar interpretación, foco, exposición y audio. Nunca se elige silenciosamente la última.

## Avance provisional autorizado — 2026-09-30

El usuario autoriza continuar ante ausencia de escucha directa, usando transcripción y señal sin inventar revisión humana. Se registra selección técnica provisional y `human_review_completed: false`. La edición provisional usa rangos trazables y un recibo `ingest-provisional-XX-YY.json`; no se genera `ingest-ready` ni se declara aprobación auditiva. La regla histórica de escucha sigue rigiendo las afirmaciones de escucha y la entrega verificada.
