# Scripts operativos de la serie

## QA post-render de entregas MP4

`qa_post_render.py` genera evidencia técnica reproducible para uno o más MP4 finales locales. Es una etapa posterior al render: **no renderiza, no publica, no modifica la entrada y no marca un video como aprobado**.

Por cada MP4 ejecuta:

1. `ffprobe` completo de formato, streams, capítulos y programas.
2. Decodificación completa de video y audio con `ffmpeg -xerror`.
3. Medición EBU R128 (`I`, `LRA` y `true peak`) cuando existe audio.
4. SHA-256 antes y después del análisis, más comparación de tamaño, mtime e inode.
5. Extracción de seis fotogramas en posiciones `1/7` a `6/7` de la duración.
6. Hoja de contacto 3×2.
7. `evidence.json` + `EVIDENCE.md` por video y `summary.json` + `SUMMARY.md` por lote.

Requisitos: Python 3, `ffmpeg` y `ffprobe` en `PATH`.

### Un video

```bash
python3 scripts/qa_post_render.py \
  VIDEO-14/editable-hyperframes-video-14/renders/VIDEO-14-FINAL.mp4 \
  --output-dir VIDEO-14/qa/post-render-2026-09-26
```

### Varios videos, máximo dos en paralelo

```bash
python3 scripts/qa_post_render.py \
  VIDEO-14/editable-hyperframes-video-14/renders/VIDEO-14-FINAL.mp4 \
  VIDEO-15/editable-hyperframes-video-15/renders/VIDEO-15-FINAL.mp4 \
  --output-dir 00-INGESTA/qa-post-render-14-15 \
  --jobs 2
```

El directorio indicado debe ser nuevo. El script se niega a sobrescribir evidencia existente y elimina entradas duplicadas del mismo comando. Devuelve `0` solo si todos los MP4 pasan metadatos, decodificación, loudness cuando aplica, seis fotogramas, hoja de contacto e integridad de entrada; devuelve `1` si alguna comprobación falla y `2` ante un error de uso o preflight.

Un resultado `PASS` es exclusivamente técnico. La reproducción completa, sincronía, color, encuadre, textos, contenido y aprobación final continúan siendo decisiones humanas. En HLG/PQ, la hoja de contacto conserva la señal decodificada sin pretender simular una pantalla HDR certificada.

Para ver todas las opciones:

```bash
python3 scripts/qa_post_render.py --help
```
