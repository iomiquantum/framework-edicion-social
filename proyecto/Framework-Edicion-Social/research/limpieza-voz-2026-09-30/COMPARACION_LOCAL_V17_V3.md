# Comparación local de limpieza: VIDEO17

2026-09-30. Petición: aún se percibe fondo leve y el usuario autoriza probar las otras opciones para afinar la elección. Estado: **pruebas locales terminadas; preferencia y naturalidad por confirmar**. El editable y su entrega v2 se conservan. No se declara aislada perfectamente la voz ni se atribuye el fondo a un ventilador concreto.

## Qué se probó realmente

Cuatro motores/modelos nuevos sobre los cinco contextos PCM48k ya extraídos del original: [ClearerVoice Studio](https://github.com/modelscope/ClearerVoice-Studio) con MossFormer2_SE_48K y FRCRN_SE_16K; [Resemble Enhance](https://github.com/resemble-ai/resemble-enhance), **solo su submódulo denoiser oficial**, sin vocoder/restauración ni DeepSpeed de entrenamiento; [RNNoise](https://github.com/xiph/rnnoise), modelo oficial compilado localmente mediante C/clang. Comparación contra original, afftdn18 y DeepFilterNet3 ya probados. Los cuatro se aplican directamente al original, sin encadenar denoisers.

Fuentes GitHub fijadas por commit, archivos de modelos verificados por SHA esperado de LFS/upstream, env Python3.11 aislado y dependencias congeladas. Recibos en `noise-benchmark-v3/{*-source-provenance,model-provenance,rnnoise-model-provenance}.json`, `environment-lock.txt`, `run_neural.py`, `run_rnnoise.py` y logs. Se distingue licencia del código de una evaluación general de términos de modelos/datasets. No instalación global. Adobe requiere sesión de usuario; **no probado ni audio subido**. El ejemplo de Claude con Adobe sigue por confirmar.

## Comparación comparable

Procesar con contexto y4800samples de cola añadida antes de cortar. Downmix explícito(L+R)/2 para cada motor y la referencia; todas las audiciones duplican ese mono enL/R. FRCRN trabaja a16k nativos y después se remuestrea a48k: no recupera ancho de banda. Resemble44,1k nativos→48k. MossFormer/RN48k nativos. RN produce retraso medido959–960samples; compensar960samples/20ms en los cinco contextos. Los demás arrojan0samples en tres ventanas por contexto. Recibo `alignment-and-cuts.json`.

Todos los A/B tienen1.331.200samples/27,733333s y−22LUFS±0,01 por **ganancia constante**, sin nuevo compresor, limitador, puerta niSFX. El primer intento de normalización detectó la diferencia de medir el estéreo original frente al mono duplicado; se corrigió midiendo la referencia común real antes de la ganancia. A/B finales medidos, no inferidos. El primer arranque de MossFormer obtuvo numpyarray y un assertion del wrapper que esperaba dict; logs preservados, wrapper corregido y ensayo completado. No se modificó el código/modelo de terceros para conseguir salida.

## Resultados y límites

| Herramienta | Cambio de RMS frente a v2 en las cinco colas de150ms (dB) | Inferencia local de cinco contextos |
|---|---|---|
| Original | +17.63, +17.65, +15.25, +17.63, +17.35 | antecedente |
| FFmpeg afftdn18 actual | +0.00, +0.00, +0.00, +0.00, +0.00 | antecedente |
| DeepFilterNet3 anterior | +3.96, +4.07, +0.91, +5.40, +1.55 | antecedente |
| ClearerVoice MossFormer2 48K | +9.72, -3.27, +8.43, +13.17, +7.68 | 5.331s |
| ClearerVoice FRCRN 16K | +11.81, +10.90, +8.74, +14.09, +7.73 | 45.161s |
| Resemble denoiser 44,1K | -10.29, -15.07, -21.45, +4.14, -24.32 | 9.113s |
| RNNoise 48K | -28.10, -29.05, -33.73, -29.36, -28.13 | 2.068s |


Valores negativos: menos energía en ese tramo frente a la limpieza actual a igual loudness. **Solo cinco colas quietas de150ms; no SNR durante voz ni evaluación perceptual**. RNNoise es la primera propuesta para escucha por la reducción consistente en esas cinco muestras. Resemble reduce cuatro de cinco; ClearerVoice no supera consistentemente v2 aquí. No establecer ganador universal ni preset común a otros ruidos/grabaciones. El usuario todavía debe revisar fondo durante voz, consonantes, respiraciones, timbre, bombeo/sonido metálico.

Los tiempos suman solo inferencia de cinco contextos que contienen44s de fuente, más padding; excluyen instalación, descarga, carga de modelos, lectura/escritura y remuestreo. Corrida local CPU; no benchmark controlado ni proyección universal. ASR local large-v3 sobre cada nueva audición27,73s recupera **81/81 palabras iguales**, no certifica naturalidad. Se reutiliza la ingesta y los cinco contextos; no se reanaliza/transcribe el master completo.

## Material de revisión y QA

Comparador: `http://localhost:3038/qa/noise-benchmark-v3/review/index.html`, siete opciones al mismo reloj, tramos/repetición y referencias originales. Dos señales de diferencia alineada, sin amplificación adicional, para inspeccionar cambios; contienen componentes vocales filtrados y ruido, no constituyen prueba automática de palabras perdidas. QA UI: las siete opciones cargan27,733333s, cambio pausado19,60s preservado, cambio durante reproducción confirmado; diferencia audio/video medida<80ms en esa observación, sin errores/warnings capturados. Dos diferencias cargadas y rangos HTTP206/1024bytes verificados. `UI-verification.json`, captura `review/comparador-voz.jpg`.

Pruebas dentro del montaje: `VIDEO-17-PRUEBA-RNNOISE-v1.mp4` y `VIDEO-17-PRUEBA-RESEMBLE-v1.mp4`. Loudness−15,23LUFS ambas; truepeak−1,77/−1,79dBTP, respectivamente. Imagen codificada **idéntica en832paquetes yPTS/DTS/duración** a v2/v1; se reutilizaQAvisual completo de esa imagen. AudioAAC48kstereo192k,1080×1920,30fps,27,733s,SDRBT709. Decode completo sin errores y0lag en cuatro ventanas AAC. Guard de texto y comprobación equivalenteSFX dentro de la entrada remux: cuatro eventos/timings/gains/hashes, dos identidades, hook integrado, sin automatización/nested audio. Niveles/masking por evento registrados; audibilidad humana pendiente. Mezcla desde PCM nativo, sin reconstruirSFX mediante sustracciónAAC.

Hashes y recetas: `audition-verification.json`, `metadata-verification.json`, `audition-commands.json`, `audition-sfx-guard.json`, `audition-visible-text-guard.json`, `ASR-verification.json`, `comparison-metrics.json`, `difference-signals.json`. RN SHA b525ec94898f009e74a1478b668c30604de200acd98d8d6db62147409d1634b6; Resemble SHA b358d3b1cf2f29a8194029a5bf69fd65aa26b4ddd740f9e4417b8cfdd9ccd0e6. ElSHA de v2 y16v4 aprobado siguen intactos, verificados en esta corrida. Ningún material se publica ni reemplaza automáticamente la entrega actual. Gates humanos de selección de pista/toma y aprobación continúan pendientes bajo la excepción provisional autorizada; no se fuerzan aPASS.

## Aprendizaje para siguientes ediciones

Conservar entornos/modelos congelados y fuente/cache; probar el mismo audio antes de adoptar herramientas. Para una mejora exclusiva de audio, remux de imagen existente y prueba de identidad permite reutilizarQAvisual, manteniendo QA nuevo de sonido/sincronía. Primero original+actual+uno o dos candidatos y ampliar si hace falta: evita repetir todas las instalaciones/descargas. Normalizar **la señal real con el mismo número de canales**, no una referencia estéreo distinta. Volver a medir delay por motor/toma. Mantener originales y estado perceptual por confirmar.

Pendiente: escucha y elección del usuario, Adobe con sesión disponible si se incluye, ensayos representativos de ruido variable/ladridos/carros/bocinas/voces superpuestas. Este video no contiene un benchmark etiquetado de esos casos.
