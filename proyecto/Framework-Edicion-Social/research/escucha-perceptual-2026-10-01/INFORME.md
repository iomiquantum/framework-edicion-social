# Revisión perceptual asistida y operación por código

Fecha: 2026-10-01. Petición: avanzar desde mediciones técnicas hacia herramientas que reciban audio real, probarlas antes de pedir revisión humana y permitir que Codex use el sistema en los demás videos sin abrir interfaces.

## Resultado práctico

Quedó una entrada por código: [audio_multimedia](../../scripts/audio_multimedia), con `doctor`, `catalog`, `prosody`, `mix --review` y `review`. Mezcla nativa, automatización por frases, fades/pan/anchura, filtrado/carve de música, ducking descendente, protección de colaSFX, export/stems y revisión acotada. Codex prepara planes con contexto y lee JSON; el HTML es opcional. [Método y contrato](../../AUDIO_EVALUACION_PERCEPTUAL_ASISTIDA.md).

La revisión recibió las11mezclas previas,2referencias y5controles de voz completa; además8controles de calibración. STOI/E-STOI recorrió444ventanas de4s con salto2s de las mezclas previas; las dos candidatas nuevas tienen103ventanas adicionales. YAMNet procesó26señales iniciales y luego las2candidatas. No son26mezclas ni547audiciones humanas.

Se añadieron candidatas completas53s/158,798s con curvas de música por idea y hookSFX+2,5dB. Se conservanC y todos los bancos previos. Se verificó la voz común escrita, la suma de stems,AAC48k estéreo, margen de picos y mono. El piloto21,375s demuestra mezcla/revisión totalmente por código; no reemplazaVIDEO-01 ni constituye aprobación de su dirección.

## Herramientas instaladas y probadas

Entorno aisladoPython3.11.15 en `~/.cache/codex-audio-perceptual/2026-10-01/venv`; [lock completo](evidencia/requirements-lock.txt). No modificamos los entornos de otras ediciones. Las inferencias son locales; los audios no se enviaron a proveedores externos.

| Herramienta | Prueba y decisión |
| --- | --- |
| pystoi0.4.1 | Sensibilidad a interferencia musical, pérdida de voz y referencia seca. Admitido en ese alcance, excluido como auditor global deSFX. |
| GoogleYAMNetfloat32,4.1MB/LiteRT2.2.0CPU2threads |5controles predefinidos pasaron; detector básico de habla/música/silencio. ModeloSHA2564d8b4a…584faf. No decide faders. |
| Qwen2.5Omni7B4bit/MLX0.32.3 |8controles ciegos con audio real. Describe voz/música evidentes pero omite cama suave y efectos; no admitido para decisiones de volumen. |
| Gemma4E2B4bit/MLX-VLM0.7.4 |8controles e inspección adicional de3prompts/embeddings. Inventó habla en silencio/música sola; descartado en esta configuración. |

Se consultaron repositorios/documentación primarios: [pystoi](https://github.com/mpariente/pystoi), [QwenOmni](https://github.com/QwenLM/Qwen2.5-Omni), [puertoMLXOmni](https://github.com/giangndm/mlx-lm-omni), [MLX-VLM](https://github.com/Blaizzy/mlx-vlm), [Gemma/audio](https://ai.google.dev/gemma/docs/capabilities/audio?hl=en), [YAMNet](https://www.tensorflow.org/hub/tutorials/yamnet). Los modelos/puertos no tienen una capacidad creativa demostrada por haber descargado sus pesos.

Recibos fijan revisionesHF:Qwen`cc80234b9ea0dc4461ad15a4c45e76d85b703b03`;Gemma`238767527555cb75a05732a84dff5d6ba0dd6809`. Pesos seguros/checksums y documentos de licencia guardados. Los pesosGemma nuevos se retiraron del cache después del descarte, con hash confirmado y descarga reproducible; no se borraron audios del usuario. Qwen permanece disponible como experimento; la rutina no lo carga.

Se investigaron [ViSQOL](https://github.com/google/visqol) y [DNSMOS](https://github.com/microsoft/DNS-Challenge/tree/master/DNSMOS). No se instalaron como jueces de carácter musical: sus ámbitos no validan ese uso. Una futura comparaciónPCM/AAC de la misma mezcla es un problema distinto de elegir música sobre una voz.

## Calibración antes de revisar muestras

Controles12s, nombres opacos, misma ganancia común, fuentes conocidas y recetas/hash en [manifest](calibracion/manifest.json). Verdad de control significa componentes/condiciones conocidos; no preferencia, emoción ni resultado subjetivo.

| Condición | E-STOI |
| --- | ---: |
| Voz sola |1,0000|
| Balance construido |0,9822|
| Música excesiva |0,4940|
| SFX breves excesivos |0,9576|
| Sin voz |−0,0226|
| Voz recortada/distorsionada |0,6815|

La diferencia balance/SFX0,0246 no alcanza el criterio predefinido0,05. Se conserva el fallo y se excluye esa capacidad; no se rebajó el umbral. E-STOI no es porcentaje ni probabilidad y puede ser negativo. [Validación](calibracion/validacion-indices.json), [intento inicial](antes/indices-calibracion-global-sfx/validacion-indices.json).

YAMNet pasó habla sola, música sola, silencio, ausencia de voz y aumento de activación musical ante música excesiva. Umbrales guardados antes de inferencia. [Criterios](calibracion/criterios-yamnet.json), [resultado](calibracion/validacion-yamnet.json). No se validó percepción deSFX, emoción, atención, instrumento exacto ni volumen ideal. Clasificación no es escucha humana.

Qwen llamó clara a voz con música excesiva y no reconoció cama suave/SFX excesivos. Gemma marcó habla en los8casos, incluso silencio. Se verificó que las ondas llegaron y que sus embeddings diferían; el problema no se resolvió interpretando respuestas fluidas como fiables. [Qwen](modelo/calibracion.json), [Gemma](modelo/gemma-calibracion.json), [inspecciónGemma](modelo/gemma-inspeccion-pipeline.json). Ninguno es revisor automático de faders.

## Hallazgos útiles y cambios

Los11E-STOIglobales0,9859–0,9991 indican alta conservación estimada del habla en estas muestras. No prueban que los fondos entretengan, se perciban o tengan suficiente contraste. No se eligió una canción ganadora por esa cifra.

Las ventanas deC más débiles estuvieron18–22s en53s y58–62/120–124s en2:39. Se cruzaron con frases reales: entrada/criterios, conversación/ventaja y no acumular otro curso. Allí se probaron retiradas de música3dB. En otras frases de avance/aplicación se probó +1,5…+2,5dB; preguntas finales se retiran. Se conserva el tramo sin música83,31–93,4s. El hook existente recibe+2,5dB, con vínculo/hash y duración de su evento original; no se añadieron efectos por cantidad.

Son hipótesis editoriales; el clasificador no recomendó esos dB. Referencias tienen activación musical media mayor que nuestras mezclas, pero cambian voces, escenas y material. No permiten calcular cuánto subir el fader ni copiar su nivel global.

| Candidata | AACLUFS | AACdBTP | E-STOIC→nueva | Ventanas |
| --- | ---: | ---: | --- | ---: |
|53s|−18,01|−5,74|0,9932→0,9924|25|
|158,798s|−18,01|−5,95|0,9941→0,9944|78|

El índice no mejora en todos los momentos; eso no basta para preferir o rechazar una versión. Voz reconstruida desde archivos escritos: error≤2,80e−8;AAC/PCMmono≥0,9999876; diferenciaRMSmono≤0,002dB. [Recetas](comparaciones/manifest.json), [QA](comparaciones/qa.json). Hook audibilidad/naturalidad por confirmar.

[Comparador opcional](index.html):C/nueva/voz/música/SFX en el mismo punto, momentos de revisión y descargas. La implementación y análisis se ejecutan sin ese comparador.

## Aceptación del flujo por código

[17casos](headless/v2/aceptacion.json):doctor, consulta de catálogo, mezcla21,375s+revisión, reutilización, prosodia con transcript existente, revisión/cache de las2candidatas, rechazo de hash alterado, falta de hook, identidades repetidas, cue fuera de rango, parámetro desconocido, recurso explícitamente rechazado y protección de una versión existente.

| Ejecución en esteMac | Nueva | Cache verificado |
| --- | ---: | ---: |
| Mix21,375s +review, proceso completo |3,72s|0,67s|
| Review53s |3,19s|0,64s|
| Review158,798s |7,66s|0,69s|
| Perfil21,375s |0,73s|0,59s|

Una ejecución por condición, incluyendo arranque del intérprete. Son resultados locales, no promesa de velocidad/equivalencia en otros videos/máquinas. Primer intentoCLI conservado en [antes/cli-v1](antes/cli-v1/aceptacion.json); revisión posterior añadió separación de tipos en catálogo y bloqueo deSFXrechazados. No se oculta trabajo previo/reintentos.

## Incidencias y límites pendientes

CompatibilidadQwen: ruta local/embedding legacy, transposiciónConv1d y atención por bloques según encoder oficial. Se registró carga de1609parámetros usados, ninguno faltante/ignorado; no equivalencia numérica de backends. Salidas iniciales sin máscara conservadas. [Incidencias](evidencia/incidencias.json), [carga](modelo/carga.json).

Reserva de disco frenóGemma después de completar pesos. Se terminó solo metadata pequeña bajo reserva explícita; los pesos fallidos se retiraron tras verificación. El sistema no descarga nuevos modelos pesados por defecto. La rapidez rutinaria deriva del detector pequeño, conservación de resultados y análisis por cambio, no de omitirQA.

El cierre es técnico con percepción asistida **parcial**. Falta evidencia de naturalidad/timbre, adecuación musical/interpretación, SFXpercibidos, fatiga y experiencia en dispositivo real. No se declaró escucha de este agente, aprobación estética, eficacia en audiencia o imposibilidad de más mejoras. No se modificó ningúnMP4/editable/voz original, no se publicó y no se promovieron candidatos a recursos aprobados.
