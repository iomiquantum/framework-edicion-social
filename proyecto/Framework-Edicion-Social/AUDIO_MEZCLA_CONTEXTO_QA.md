# Mezcla por contexto y cierre técnico para escucha

Protocolo incorporado el2026-09-30 a petición del usuario durante pruebas de musicalización. Complementa AUDIO_DIRECCION_Y_PROSODIA.md. No activa restauración de voz ni aprueba música/SFX nuevos globalmente. Valores de las muestras son decisiones provisionales ligadas a fuentes concretas, no presets universales.

## Una relación por momento

Analizar la voz nativa del montaje vigente y reutilizar palabras/tiempos. Identificar afirmación, contraste, explicación, lista, pausa y pregunta a partir de texto/contexto. Estimar intensidad, F0, pausas y ritmo dentro del mismo hablante; no inferir emoción o defecto solo por números. Elegir función musical antes de canción. En15–30s, una o dos según mensaje, sin cuota. En largos, cambiar cuando cambia el argumento y conservar temas cuando aportan continuidad.

Escribir la automatización editorial por frases y grupos de palabras: bajar antes de la idea importante, mantener espacio hasta su final y volver solo cuando el relato lo permite. Retirada, cambio de arreglo, selección de otro tramo, transición o un acento son alternativas distintas. La protección automática es secundaria y descendente; no elevar música en cada hueco.

Trabajar timbre/densidad y bandas sobre la música cuando compite; conservar voz intacta salvo petición distinta. Distinguir un volumen bajo de un arreglo poco compatible. Usar efectos con función y ataque/cola elegidos, revisar cuánto invaden la próxima entrada vocal. Mayor cantidad de efectos no demuestra mejor acabado. Mantener hook con SFX y mínimo dos identidades para20–30s según regla vigente.

## Comparaciones que sirven

Cuando el carácter no esté elegido, preparar alternativas completas con hipótesis diferentes: pulso/precisión, textura cálida/fluida, contraste/densidad editorial u otras justificadas. Mismo guion, tiempos, aporte vocal y nivel de voz; mantener un control y la versión anterior. No normalizar cada mezcla por separado de forma que cambie la voz y parezca que una alternativa gana por volumen.

Versionar plan, fuentes, ganancias, filtros, inicios/offsets, fades, automatización y eventosSFX. Poder escuchar mezcla, voz, música y efectos en el mismo momento. Registrar feedback por pieza/versión/segundo y distinguir aprobación del tramo, de la mezcla y del recurso global.

## Verificar el proceso y el archivo exactos

1. **Fuentes y montaje:** hashes, procedencia/licencia, versión actual, audio nativo; no usar ASR16k para mezclar. Declarar mono/estéreo y su matriz; duplicaciónmono unity y downmix normalizado no son equivalentes de nivel. Diferencias de cola requieren diagnóstico; no mover fonemas para coincidir con un contenedor.
2. **Plan previo a export:** fuentes válidas, hook integrado, identidades reales y ventanas dentro del archivo. No llamar identidad nueva a un cambio de ganancia del mismo SFX. Ausencia de hook o binding inválido detiene export.
3. **Señal y automatización:** finitud, energía no nula, fades en el tiempo correcto. Cortar/seek antes de aplicar filtros de tiempo. Media de energía es no negativa: un residual negativo minúsculo por precisión requiere evidencia y clamp limitado antes de sqrt; negativos sustanciales/NaN no se ocultan. Guardar incidencias y el intento anterior.
4. **Relación local:** medir música/SFX contra voz contemporánea y su contexto, incluidas colas, primeras palabras y finales suaves. Mantener curvas completas; separar banda de habla de residuos/pausas. Relaciones positivas durante silencio no prueban masking. Umbrales orientan revisión; no certifican audibilidad/inteligibilidad.
5. **Mezcla real:** suma de stems, invariancia de voz compartida, WAV/codec/duración/canales, decode completo y energía. Correlación contra referencia del proceso íntegro, no contra mezcla seca si el motor procesó buses/fades. True peak delAAC exacto; si hay ajuste, guardarlo y verificar la salida nueva.
6. **Portabilidad técnica:** downmixmono, cancelación/RMS y, si hay duda concreta, simulación de canal limitado. No etiquetar simulación como escucha en teléfono ni equivalencia con su altavoz.
7. **Reconocimiento opcional:** cuando ayude a investigar competencia o pérdida de mensaje en un export nuevo, comparar ASR de mezcla y control con mismo motor/configuración, sin prompt del guion. Mantener resultados fallidos. Repeticiones con tiempos nulos o discrepancias grandes necesitan contraste de señal y bloques originales/control, no bajar música hasta complacer un reconocedor. Fronteras comunes preexistentes y comparación contra el guion permiten separar contexto del modelo de una posible omisión; ASR sigue siendo un proxy.
8. **Reproducción nativa:** verificar el archivo final, avance de tiempo, ausencia de error, seek, comparación conservando posición y rutas de descarga. La reproducción por herramienta no equivale a escucha perceptual ni aprobación.

No repetir ASR del lote, restauración intacta, renders anteriores o verificaciones ya pasadas sin cambios, fallos o una incertidumbre concreta. La investigación profunda de una nueva paleta puede justificar variantes/iteraciones; no convertirla en carga obligatoria para cada edición normal.

## Cierre honesto

Estado **LISTA_PARA_ESCUCHA** cuando los checks aplicables están completos, fuentes preservadas, incidencias resueltas, export/player exactos comprobados y ninguna incertidumbre técnica relevante queda sin decisión. Registrar cobertura y límites. No afirmar «no existe otra mejora posible» ni «escuchado profesionalmente» si no hay evidencia.

La siguiente decisión entonces requiere escucha: carácter, naturalidad, efecto percibido, jerarquía, fatiga y experiencia en el dispositivo real. Una mezcla técnicamente verificada sigue siendo candidata hasta ese feedback. Tras una corrección, repetir únicamente la verificación afectada y preservar versiones.

Caso de origen: research/prueba-mezcla-voz-2026-09-30/variantes.html y PROCESO_VARIANTES.md. Tres tratamientos por voz53s/2:39, seis recursos musicales, ochoSFX originales candidatos, voz compartida, protección descendente y pruebas de export/mono/ASR/UI. Sin adopción de una canción ni eficacia de audiencia afirmada.


## Continuación2026-10-01 — ejecución por código

Usar [AUDIO_EVALUACION_PERCEPTUAL_ASISTIDA.md](AUDIO_EVALUACION_PERCEPTUAL_ASISTIDA.md) y laCLI [audio_multimedia](scripts/audio_multimedia) para implementar/evaluar musicalización sin abrir interfaz. El HTML es opcional para comparaciones estéticas. La revisión añadida recibe audio real, calibra por capacidad y conserva fallos: estimaciones de habla/música y detección básica aprobadas dentro de los controles locales; percepciónSFX/adecuación creativa no demostradas. Verificar decode/clock/montaje/export por código y mantener comprobación de dispositivo/aprobación como pendientes reales cuando falte evidencia. Una interfaz no es dependencia del mezclado/análisis. Reutilizar por hash y repetirQA afectado, sin nuevosASR/limpiezas/renders intactos.
