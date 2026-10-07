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

Por instrucción explícita del usuario, al recibir un nuevo video hay que aplicar los aprendizajes y reglas vigentes sin pedirle que los repita. Antes de montar, revisar instrucciones aplicables, bitácora reciente, documentación del framework, plantilla aprobada, dirección creativa y QA; guardar un recibo de inicio en VIDEO-NN con los documentos y hashes consultados, decisiones y pendientes reales. Incluir mezcla y QA habitual de audio, captions, protección de rostro/gestos, texto semántico y pertinencia de imágenes. La revisión especializada y supresión de ruido se activan únicamente por solicitud explícita del usuario, según el apartado siguiente.

Reutilizar ingesta, transcripción, marcadores y recursos ya verificados; no repetir el análisis del lote por cada video. Buscar una mejora concreta de calidad o flujo, medir tiempos de comandos/retrabajo cuando sea posible y documentar el resultado sin atribuir ahorros ni rendimiento que no se hayan medido. Verificar las reglas en el editable y en la salida exacta, conservar versiones anteriores y actualizar bitácora/changelog tras cambios materiales. Esta instrucción no equivale a aprobación de un video nuevo ni permite afirmar escucha o revisión humana sin evidencia.


## Dirección de audio y hook — regla permanente VIDEO23, 2026-09-30

Aplicar `Framework-Edicion-Social/AUDIO_DIRECCION_Y_PROSODIA.md` (ruta desde raíz del proyecto). Antes de elegir música/SFX, analizar voz real por intensidad/contrastes, pitch/entonación estimados, pausas, ritmo y cambios por frase; ligar interpretación a palabras/contexto y separar inferencia de escucha. Reutilizar ASR y voz intactos. Comparar aumento de nivel, ubicación o carácter cuando un efecto no se perciba. **Todo hook inicial lleva SFX integrado y debe comprobarse en QA**, además del mínimo dos identidades distintas para20–30s. Registrar niveles contra voz, picos/masking y reproducción real; ausencia de hook/vínculos inválidos bloquea render mediante verificación equivalente a `scripts/revisar_presencia_sfx.py`. Medición no certifica audibilidad ni emociones; mantener escucha por confirmar si falta.


## Revisión y limpieza especializada de voz — solo a solicitud, 2026-09-30

Solo cuando el usuario pida explícitamente revisar la voz/el audio o eliminar ruido de fondo, aplicar `Framework-Edicion-Social/AUDIO_LIMPIEZA_VOZ.md` y la skill `revisar-limpiar-voz` en `/Users/iomijhondavid/.codex/skills/revisar-limpiar-voz/SKILL.md`. Una edición normal, render o QA habitual no activa diagnóstico especializado, nuevas limpiezas, pruebas de motores ni bypass/A-B obligatorios. Dentro de la revisión solicitada, sugerir tratamientos adicionales si se detectan eses molestas, golpes de aire, clics, eco u otros defectos; no aplicarlos automáticamente. Conservar original, recetas, hashes y QA del audio que sí se cambie. Esta instrucción sustituye el alcance general previo; no revierte medios ya procesados ni las reglas habituales de mezcla, ritmo, SFX y sincronía.
La petición específica puede expresarse en lenguaje natural (por ejemplo, «revisa el audio del17» o «quita el ruido de fondo»); entonces leer/invocar la skill indicada. Su política evita selección implícita por tareas generales. Fuera de esa solicitud, un hallazgo incidental del QA puede comunicarse como sugerencia, sin activar ensayos ni modificar la voz automáticamente.


## Perfiles de edición1/2/3 — piloto preparado el2026-09-30

Consultar `Framework-Edicion-Social/workflow-profiles/GUIA.md`, `catalog.json`, `QA_COMUN.md` y elJSON del perfil elegido. Sin petición explícita ni asignación experimental registrada, conservar flujo1predeterminado. Flujo2optimiza organización/reutilización verificada con igual intención creativa; flujo3reduce personalización con los mismos controles requeridos. Ambos son experimentales, sin rapidez/equivalencia demostradas. Registrar selección/versiones y reloj de fases antes de editar; las tres pasadas, guards, aprobación yQA de cadaMP4 siguen vigentes. Preservar versiones y volver a1en un runnuevo si hacefalta; no promoverdefaults automáticamente. Plan del1deoctubre en `Framework-Edicion-Social/workflow-profiles/experiments/2026-10-01-lote26-30/PRUEBA.md`; asignar perfiles tras ingesta yantes del montaje. Una elección concreta del usuario prevalece sobre el reparto piloto.
