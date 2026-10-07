# Índice de evidencia original

Raíz: `/Users/iomijhondavid/Documents/Codex/Edicion de Videos`. Resolver rutas siguientes desde ella. Si se mueve o faltan archivos, localizar por recibos y declarar datos no verificables; no reinstalar automáticamente. Modelos/entornos/medios grandes quedan donde están, sin duplicarlos en la skill.

- `Framework-Edicion-Social/AUDIO_LIMPIEZA_VOZ.md`: procedimiento y evolución; alcance actual por solicitud.
- `Framework-Edicion-Social/research/limpieza-voz-2026-09-30/INFORME.md`: investigación inicial de repositorios/Adobe.
- Misma carpeta, `COMPARACION_LOCAL_V17_V3.md`: siete opciones reales, resultados/tiempos y límites; `REVISION_A_SOLICITUD.md`: alcance actual e investigación adicional.
- `Serie-IA-Negocios-10-Videos/VIDEO-17/qa/noise-revision-v2/`: afftdn18/DF3; binario/modelo, `prepare_comparison.py`, `remux_candidates.py`, parámetros/comandos/ASR/QA. El remux histórico cambiaba el editable: leerlo, no rerun sin adaptar.
- `Serie-IA-Negocios-10-Videos/VIDEO-17/qa/noise-benchmark-v3/`: `run_neural.py`, `run_rnnoise.py`, `assemble_compare.py`, `check_words.py`, `remux_audition.py`; Python3.11/lock, fuentes/commits/modelos y librería. Proveniencia: `*-source-provenance.json`, `model-provenance.json`, `rnnoise-model-provenance.json`, `rnnoise/binary-provenance.json`.

En `qa/noise-benchmark-v3/`:

| Evidencia | Recibo |
|---|---|
| Contextos/hashes/modelrates/tiempos | `{clear_moss48,clear_frcrn16,resemble_denoise,rnnoise}/events.json` |
| Delay/cortes exactos | `alignment-and-cuts.json` |
| SieteA/B/LUFS/hashes/tails | `comparison-metrics.json` |
| 81palabras en4variantes | `ASR-verification.json` |
| Diferencias de señal/alcance | `difference-signals.json` |
| Export/hash/decode/paquetes | `audition-verification.json`, `metadata-verification.json`, `audition-commands.json` |
| SFX/hook/dosidentidades/niveles | `audition-sfx-guard.json` |
| Guardtexto | `audition-visible-text-guard.json` |
| UI/captura | `review/index.html`, `UI-verification.json`, `review/comparador-voz.jpg` |
| Cierre | `finalization.json` |

Estado: editable17v2 conafftdn18 intacto; v1 y pruebasDF3/RN/Resemble conservadas. RecomendaciónRN no es aprobación ni cambio deeditable. RN28.10–33.73dB menosRMS frente av2 en5colas150ms a igual loudness; noSNR durante voz ni naturalidad escuchada. Cuatro variantes recuperan81palabras, sin certificar timbre/consonantes. DosMP4 audición conservan832paquetesvideo/4SFX/2identidades;AAC0lag en4ventanas. Adobe no probado ni audio subido; gates humanos no forzados. 16v4 aprobado no se modificó. Nueva política no revierte limpiezas anteriores sin petición.
