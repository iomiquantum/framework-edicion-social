# Memoria y documentación del proyecto

Este proyecto mantiene una bitácora maestra en `BITACORA_CURSO_EDICION.md`.

Después de cualquier cambio material en videos, editables, estilos, plantillas, recursos, reglas, scripts, renders o estructura del framework:

1. Actualizar la fecha de “Última actualización” de la bitácora.
2. Añadir una entrada cronológica en “Registro de nuevas entradas”.
3. Registrar la petición, el punto de partida, los cambios, el motivo, los archivos afectados, la validación, el resultado, el aprendizaje y lo pendiente.
4. Actualizar también el changelog especializado de la carpeta afectada cuando exista.
5. No afirmar que algo fue aprobado, escuchado, visto, probado, publicado o medido si no existe evidencia.
6. Marcar como `por confirmar` cualquier recuerdo o dato que no pueda verificarse.
7. Conservar las versiones anteriores; no reescribir la historia para que parezca que la última decisión siempre fue la original.

Las consultas, inspecciones y explicaciones que no cambien el proyecto no requieren una nueva entrada, salvo que el usuario pida registrarlas como parte del curso.

## Inicio permanente de cada nueva edición

Por instrucción explícita del usuario, al recibir un nuevo video hay que aplicar los aprendizajes y reglas vigentes sin pedirle que los repita. Antes de montar, revisar instrucciones aplicables, bitácora reciente, documentación del framework, plantilla aprobada, dirección creativa y QA; guardar un recibo de inicio en VIDEO-NN con los documentos y hashes consultados, decisiones y pendientes reales. Incluir audio y supresión de ruido cuando corresponda, captions, protección de rostro/gestos, texto semántico y pertinencia de imágenes.

Reutilizar ingesta, transcripción, marcadores y recursos ya verificados; no repetir el análisis del lote por cada video. Buscar una mejora concreta de calidad o flujo, medir tiempos de comandos/retrabajo cuando sea posible y documentar el resultado sin atribuir ahorros ni rendimiento que no se hayan medido. Verificar las reglas en el editable y en la salida exacta, conservar versiones anteriores y actualizar bitácora/changelog tras cambios materiales. Esta instrucción no equivale a aprobación de un video nuevo ni permite afirmar escucha o revisión humana sin evidencia.


## Dirección de audio y hook — regla permanente VIDEO23, 2026-09-30

Aplicar `Framework-Edicion-Social/AUDIO_DIRECCION_Y_PROSODIA.md` (ruta desde raíz del proyecto). Antes de elegir música/SFX, analizar voz real por intensidad/contrastes, pitch/entonación estimados, pausas, ritmo y cambios por frase; ligar interpretación a palabras/contexto y separar inferencia de escucha. Reutilizar ASR y voz intactos. Comparar aumento de nivel, ubicación o carácter cuando un efecto no se perciba. **Todo hook inicial lleva SFX integrado y debe comprobarse en QA**, además del mínimo dos identidades distintas para20–30s. Registrar niveles contra voz, picos/masking y reproducción real; ausencia de hook/vínculos inválidos bloquea render mediante verificación equivalente a `scripts/revisar_presencia_sfx.py`. Medición no certifica audibilidad ni emociones; mantener escucha por confirmar si falta.
