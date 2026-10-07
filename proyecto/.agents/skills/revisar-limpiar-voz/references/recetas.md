# Recetas para revisión solicitada

Ejemplos verificados en VIDEO17 el2026-09-30; **no defaults del lote**. Leer [índice](evidencia-proyecto.md), verificar entradas/modelos/hashes y escribir en carpeta nueva. Scripts históricos escriben en sus carpetas originales y algunos modifican editables: no rerun allí. Adaptar a entradas actuales o usar el helper con salida nueva.

## Contexto, latencia y A/B

Partir de pista original seleccionada, frecuencia nativa, sin usar el WAV16k de ASR para mezclar. Procesar contexto antes/después y luego cortar. VIDEO17 usó cinco contextos/44s fuente y4800samples48k de padding final por contexto; no imponer esas duraciones a otra toma.

Downmix de prueba(L+R)/2 explícito y duplicaciónmonoL/R para todas las referencias. Revisar canales/fase antes si la fuente cambia. A/B−22LUFS con ganancia constante: medir la señal y distribución real de canales, ajustar diferencia de ganancia y medir archivo resultante, sin nuevo limiter/compresor/puerta/SFX. El nivel es de audición, no estándar de entrega; reducir objetivo común si falta margen de pico.

Medir delay en varias ventanas de voz y/o impulso según motor; compensar conservando muestras exactas y cola. Volver a comprobar trasAAC.

## FFmpeg afftdn con perfil propio

Ejemplo17v2: `afftdn=nr=18:nf=-55:tn=0:gs=12`. Anteponer1s de pausa pertinente de la misma grabación, muestrear perfil mediante `asendcmd` entre.1/.9s; retirar preroll y delay medido1200samples48k/25ms con `atrim`, después cortar. Perfil sin voz ni ambiente narrativo. Receta/recibos en `qa/noise-revision-v2/prepare_comparison.py`; intensidadnr18 no recomendada sin comparación.

## DeepFilterNet3 nativo48k

Binario oficialv0.5.6AppleSilicon yDF3ONNX fijados en revisiónv2. Receta17: `-m MODELO -D -a 24 -v -o CARPETA_NUEVA CONTEXTO_PADDED.wav`; límite24dB, compensación interna, sin postfilter solicitado. Añadir cola: elCLI compensa pero no rellena automáticamente la duración retirada. Medir/cortar después. Verificar sintaxis/versiones antes de adaptar otra release.

## ClearerVoice

Fuentes/checkpoints en `qa/noise-benchmark-v3/`; CPUtorch4threads. `ClearVoice(task='speech_enhancement',model_names=[...])` y llamada conarchivo/`online_write=False`. La versión fijada devuelve numpyarray para un archivo; wrapper aceptaarray/dict único y valida dimensiones. No asumir retorno de otra versión.

- `MossFormer2_SE_48K`:48k nativos, delay medido0.
- `FRCRN_SE_16K`:16k nativos→48k de comparación; no recupera ancho de banda. Delay medido0.

`run_neural.py`/`environment-lock.txt` conservan receta/dependencias; reutilizar checkpoints antes de descargar de nuevo.

## Resemble denoiser

Submódulo oficial `Denoiser(HParams())`, cargar claves`denoiser.` delcheckpoint retirando ese prefijo/`strict=True`; `inference(model,waveform48k,48000,'cpu')`. HParams44,1k/hop420/nfft2048 coincide conconfig congelada; remuestrear48k después. Evitar imports de entrenamientoDeepSpeed sin cambiar arquitectura/pesos. **No se probó vocoder/restauración completa**. Delay medido0.

## RNNoise48k

Fuente/modelo oficiales fijados; `librnnoise.dylib`C/clang. Estado por contexto, frames480samples/10ms, floatAPI×32768 alentrar/÷32768 alretorno; sin cuantizaciónPCM16 ni puerta añadida basada enVAD. Delay medido959–960samples, compensado960/20ms; verificar de nuevo si cambia librería/modelo/fuente.

Helper `scripts/rnnoise_wav.py`: requiereentrada48k,librería+SHA y compensación explícita. Produce contexto mono duplicadoL/R, duración exacta y recibo, sin normalizar/mezclar/cortar. Usar Python3.11 aislado existente con numpy/soundfile, salida nueva, después recortar. Sustituir rutas por las verificadas:

```text
PYTHON_ENTORNO scripts/rnnoise_wav.py --input CONTEXTO48K.wav --output SALIDA_NUEVA.wav --library LIBRERIA_VERIFICADA --expected-library-sha256 SHA_VERIFICADO --delay-samples 960
```

Hash esperado en `rnnoise/binary-provenance.json`; fuente/modelo/build en recibos relacionados. No copiar ese delay a otros motores; helper no decide naturalidad ni se activa en ediciones normales.

## Mezcla/export

Dos pasadasloudnorm17 aI−15/TP−1.8/LRA11 dieron mezcla−15.23LUFS/TP−1.77 y−1.79dBTP. Usar objetivo vigente del proyecto, no estándar externo universal. SFX desdePCM nativo congains/timings reales ymonoL/R explícito; nunca recrearlos restandoAAC. Remux`c:v copy` y probar todos los paquetes/PTS/DTS/duración antes de reutilizarQAvisual. Conservar guards de texto/hook/SFX enentrada yQA delaudio exacto. Otro hash deaudio no hereda aprobación. Adobe pendiente de acceso/autorización/prueba; no síntesis ni completar fonemas.
