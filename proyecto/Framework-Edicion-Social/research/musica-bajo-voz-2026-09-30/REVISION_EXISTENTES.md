# Revisión de videos existentes para decidir música

Fecha local: 2026-09-30. Muestra de 26 renders y sus editables; dos fotogramas por render. Sonoridad del programa completo. No atribuir estas cifras a voz o BGM aisladas. Escucha y revisión completa de movimiento por confirmar.

| Pieza | Duración del MP4 | LUFS del programa | Capas de música declaradas | Archivo muestreado |
| --- | ---: | ---: | ---: | --- |
| VIDEO-01 | 21.40 s | -16.39 | 1 | `Serie-IA-Negocios-10-Videos/VIDEO-01/VIDEO-01_REVISION_v2.mp4` |
| VIDEO-02 | 18.33 s | -16.90 | 1 | `Serie-IA-Negocios-10-Videos/VIDEO-02/VIDEO-02_REVISION_v3.mp4` |
| VIDEO-03 | 20.30 s | -16.91 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-03/VIDEO-03_REVISION_v3.mp4` |
| VIDEO-04 | 18.83 s | -16.70 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-04/VIDEO-04_REVISION_v2.mp4` |
| VIDEO-05 | 19.53 s | -17.05 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-05/VIDEO-05_REVISION_v2.mp4` |
| VIDEO-06 | 19.60 s | -16.92 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-06/VIDEO-06_REVISION_v3.mp4` |
| VIDEO-07 | 18.70 s | -16.92 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-07/VIDEO-07_REVISION_v3.mp4` |
| VIDEO-08 | 18.90 s | -16.87 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-08/VIDEO-08_REVISION_v3.mp4` |
| VIDEO-09 | 20.20 s | -17.04 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-09/VIDEO-09_REVISION_v7.mp4` |
| VIDEO-10 | 21.30 s | -16.63 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-10/VIDEO-10_REVISION_v3.mp4` |
| VIDEO-11 | 29.10 s | -16.59 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-11/editable-hyperframes-video-11/renders/VIDEO-11-FINAL.mp4` |
| VIDEO-12 | 19.70 s | -16.34 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-12/editable-hyperframes-video-12/renders/VIDEO-12-FINAL.mp4` |
| VIDEO-13 | 19.50 s | -16.82 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-13/editable-hyperframes-video-13/renders/VIDEO-13-FINAL.mp4` |
| VIDEO-14 | 23.30 s | -16.47 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-14/editable-hyperframes-video-14/renders/VIDEO-14-FINAL.mp4` |
| VIDEO-15 | 21.10 s | -16.53 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-15/editable-hyperframes-video-15/renders/VIDEO-15-FINAL.mp4` |
| VIDEO-16 | 28.50 s | -15.31 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-16/VIDEO-16-PARA-APROBACION-v4.mp4` |
| VIDEO-21 | 21.63 s | -16.19 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-21/editable-hyperframes-video-21/renders/VIDEO-21-ENTREGA-HLG-v2.mp4` |
| VIDEO-22 | 25.27 s | -16.00 | 0 | `Serie-IA-Negocios-10-Videos/VIDEO-22/entrega/VIDEO-22-ENTREGA-HLG-v2-audio-conservado.mp4` |
| MIGUEL-PILOTO | 14.47 s | -16.37 | 0 | `Miguel-Reel-Piloto/outputs/MIGUEL_REEL_PILOTO_FASE2.mp4` |
| MIGUEL-V2 | 60.00 s | -15.80 | 4 | `Miguel-Reel-Piloto/outputs/MIGUEL_REEL_COMPLETO_PRO_V2.mp4` |
| WELLNESS | 33.07 s | -17.33 | 1 | `WhatsApp-Reel-Prueba-Fuego/outputs/PRUEBA_FUEGO_IMMERSIVE_WELLNESS_V1.mp4` |
| EXPLAINER-V1 | 53.00 s | -15.93 | 0 | `NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado/renders/video-delivery.mp4` |
| EXPLAINER-V2 | 52.96 s | -14.13 | 0 | `NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado-v2/renders/video-v2-delivery.mp4` |
| MUSE-06 | 19.60 s | -16.92 | 0 | `PRUEBAS-MUSE/VIDEO-06-VARIANTE-01/VIDEO-06_REVISION_v3.mp4` |
| MUSE-12 | 20.83 s | -15.74 | 0 | `PRUEBAS-MUSE/VIDEO-12-EDICION-01/VIDEO-12_MUSE_V4.mp4` |
| MUSE-14 | 21.03 s | -16.54 | 0 | `PRUEBAS-MUSE/VIDEO-14-EDICION-01/VIDEO-14_MUSE_V1.mp4` |

La presencia de una capa no garantiza su audibilidad, y su ausencia no descarta música ya incorporada a una fuente. Las ganancias lineales de los editables no permiten comparar volúmenes sin medir las fuentes.

Los hashes de los 26 MP4 se conservaron y volvieron a comprobar al cierre, sin cambios en esa muestra. Los 52 fotogramas se inspeccionaron en tres láminas; la conversión HDR para estas capturas sirve para examinar estructura y no certifica color de entrega. El primer intento usó un FFmpeg sin zscale; se recuperaron únicamente las capturas fallidas con FFmpeg full 9.0.2, sin repetir transcripción, ingesta ni mediciones.

## Láminas inspeccionadas

- [Serie 01 a 10](evidencia/contacto-01-10.jpg)
- [Serie 11 a 22](evidencia/contacto-11-22.jpg)
- [Otras familias](evidencia/contacto-otras-familias.jpg)

## Evidencia reproducible

- `evidencia/inventario-renders.json`: 107 archivos, incluyendo dos referencias externas y versiones históricas.
- `evidencia/revision-existentes.json`: selección exacta, hashes, streams y pistas de timeline.
- `evidencia/*-timeline.json`: HyperFrames 0.8.99, operación de lectura; no se actualizaron pins de proyectos.
- `evidencia/*-probe.json` y `*-loudness.log`: metadatos y mediciones de programa completo.
- `evidencia/audiciones.json`: fragmento, hashes, ganancias y mediciones de las comparaciones.
- `evidencia/validacion.json`: archivos, enlaces, decodificación de muestras y preservación verificados.

## Selección de recursos

Se investigaron también Cipher y Floating Cities de Incompetech y Discovery de Scott Buckley. No se descargaron: el hook insistente declarado para Cipher y la instrumentación dramática de Discovery añaden competencia musical; Floating Cities se describe como escena atmosférica sin diálogo. Estos motivos son criterios editoriales de preselección, no juicios derivados de una escucha.

Fuentes: [Cipher](https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1100844), [Floating Cities](https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1600018), [Discovery](https://www.scottbuckley.com.au/library/discovery/).
