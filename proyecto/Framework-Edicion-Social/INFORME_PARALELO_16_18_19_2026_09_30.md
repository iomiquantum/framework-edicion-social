# Edición paralela16/18/19 — resultados y optimización

Fecha local:2026-09-30. Tres MP4 renderizados y verificados para revisión/aprobación final. La aprobación16v4 permanece vinculada a esa versión; no se transfiere al audio16v6. No hay publicación.

## Entregas

| Video | Versión | Duración | Cuadros30fps | Audio final medido | Resultado |
| --- | --- | --- | --- | --- | --- |
|16|v6|28,50s|855|−15,23LUFS / −1,79dBTP|RNNoise; «fácil» original restaurada; imagen idéntica a16v4 aprobado|
|18|v1|21,87s|656|−15,14LUFS / −1,23dBTP|T18Rótulo popular, foto contextual nueva,15cues/66palabras,3SFX/2identidades|
|19|v1|29,60s|888|−15,18LUFS / −1,80dBTP|T19PixelQuest, foto pertinente reutilizada,20cues,4SFX/3identidades; «persona» original preservada|

Todos:1080×1920, H264/SDRBT709, AAC48kestéreo. Paths/SHA y evidencia en `Serie-IA-Negocios-10-Videos/00-INGESTA/qa-parallel-16-18-19/delivery.json`.

## Reparto y cola

Raíz corrigió16, adoptó el RNNoise elegido en17 y coordinó documentación/entregas. Editor18 y editor19 escribieron exclusivamente sus montajes. Auditorreglas18 preparó checklist18/anexo19 y liberó plaza para editor19. Directorvisual18/19 preparó diseños/recursos y revisó los MP4. Al terminar18, su plaza se reutilizó para QAaudio19 independiente, mediante instrucciones compactas y archivos de evidencia.

Máximo observado:4agentes activos incluyendo raíz. El tablero limita2trabajos pesados globales;25deotrochat tenía una reserva.18/19cedieron cupos durante authoring ligero y los reclamaron para preparación/check/render. QA/dirección avanzó mientras se montaban otras piezas. No se reanalizó ni retranscribió el master completo.

## Tiempos medidos y límites

| Fase |16|18|19| Alcance |
| --- | --- | --- | --- | --- |
|RNNoise, motor|4,294s/94scontexto|3,771s/78scontexto|5,650s/120scontexto|Timer de inferencia del helper|
|RNNoise, comando|sin timer externo comparable|4,050s|5,919s|Incluye arranque/helper|
|Cortes originales aSDR|imagen reutilizada|4,971s|6,289s|Sólo selección individual|
|Exportación|remux de imagen aprobada|29,547s comando /26,0s pipeline|40,836s comando /37,1s pipeline|Wrapper/guards/pipeline son medidas diferentes|
|Revisión visual exacta|linajevisualv4 idéntico|211s|79s|Pared de revisión/herramientas/coordinación, noCPUbenchmark|
|Audio independiente19|—|—|218,947s|Revisión/herramientas PCM/AAC/hash, no escucha humana|

16v5:check63,869s incluyendo300muestras automáticas de movimiento.18final:21,881s,78estados de layout/11contrastes, módulo automático de movimiento **desactivado**; su revisión visual sí cubrió192estados reales del MP4. Estos checks no son comparables como prueba de aceleración equivalente.

18:una ejecuciónRNNoise, un render completo, dos lotes de snapshots, cuatrochecks; se corrigieron oclusión y geometría. Dos ASRindividuales emitieron7,173/7,033s de motor.19:smoke5,2s/6,6s de pipeline antes del render completo. Evidencia en `measured-phases-final.json`, `VIDEO-18/METRICAS_PRODUCCION.json` y `VIDEO-19/qa/final-v1/timings-and-optimization.json`.

No existe comparación controlada2vs3 con piezas/configuraciones equivalentes. Cola exacta, costo/tokens por agente y ahorro total no se midieron. Sumar procesos solapados no da la pared de edición.16es corrección de audio;18/19son montajes nuevos.

## Aprendizajes aplicados

1. Reutilizar ingesta/modeloRN/contextos48k. Afinar únicamente segmentos ambiguos con ASRindividual/señal; los timestamps estirados de recuperación no son cortes precisos.
2. Separar presentador/gestos y captions antes del check integral. Manos tapadas en18se corrigieron y el aprendizaje pasó a19antes de renderizar.
3. Verificar terminaciones débiles además de ASR.16«fácil» tenía transcripción correcta, pero usuario oyóLdefectuosa. Se conservó grabación original con transición local;19preservó«persona». Umbrales−40dB/12dB podían omitir colas débiles. Los guards no certifican fonemas. No se añadieron motores nuevos/de-esser.
4. Elegir imagen por contexto:18generó escena de aprendizaje práctico;19reutilizó imagen pertinente de automatización/respaldo humano. Recursos anteriores conservados.
5. Revisar cues, huecos, cortes y retornos en el MP4 exacto.19smoke comprobó tercer cue/hueco contra captions fantasma.18holdfinal247ms es lectura intencional.
6. Comprobar color directo antes de cambiarCSS: JPEGdeQA18 sugería diferencia, pero RGBdelMP4(5,128,132)≈CSS(6,127,132). Se evitó corregir/reexportar una imagen que estaba bien.
7. Revisar por dependencia y usar handoffs compactos. Audio nuevo permite reutilizar imagen cuando todos los packets/PTS/DTS/duración coinciden. Documentación/recibos nuevos no requieren encode audiovisual.

## Propuesta para dos o tres videos

Propuesta operativa basada en lo observado, aún sin benchmark:

| Paquete | Reparto | Uso |
| --- | --- | --- |
|2videos/4agentes totales|Coordinador,2editores,1director/QAcompartido|Solapar revisión y preparación|
|3videos/4agentes, como aquí|Raíz edita una y coordina,2editores,1director/QAcompartido; relevar plazas al cerrar fases|Coordinación y tercer montaje comparten responsable|
|3videos/6agentes, si configuración/runtime lo permite|Coordinador,3editores,1directorvisual,1QAaudio/captions compartido|Separar coordinación de montaje; medir el resultado|

Un editor por editable; revisores reciben hashes congelados y entregan hallazgos. Caches/recibos compartidos, documentación con lock. Cerrar cortes y geometría antes de comprobación integral; liberar cupo pesado durante trabajo ligero. No crear más agentes para repetir investigación o procesamiento ya validado.

## Configuración

`Serie-IA-Negocios-10-Videos/production-board.json` contiene `max_heavy_jobs:2`: política local editable, no capacidad máxima comprobada del equipo. No se cambió. Snapshot del host:AppleM4,10CPU,16GiBRAM; una lectura de memoria no prueba capacidad de renders simultáneos.

La [documentación oficial de Codex](https://learn.chatgpt.com/docs/config-file/config-reference) identifica `[agents].max_concurrent_threads_per_session` en `~/.codex/config.toml`, excluyendo el hilo principal. Valor8configura hasta8auxiliares; `max_threads` es alias antiguo. Esta sesión siguió ofreciendo4plazas totales; efecto de cambio sobre sesión iniciada no verificado.

Para comparar2vs3en siguientes lotes, registrar intervalos por etapa/esperas/reintentos/configuración y mantener cargas/calidad comparables. Separar concurrencia de preparación/revisión de comandosGPU/ASR/render. Un cupo pesado mayor puede probarse como experimento;3heavy no se probó aquí.

## Validación de entrega

16:855packets/PTS/DTS/duración idénticosv4/v5/v6, palabra original recuperada, voz fuera del parche igual, guards/metadata/decode/AACsyncPASS.18:192estados/15cues/4PNG360px.19:218estados/20cues/5PNG360px, más PCM/AAC/hashes/cierre revisados independientemente. Sin bloqueantes en muestras auditadas.

Scorecards18/19válidas sin errores de estructura; take/pista, escucha humana y destinos reales siguen pendientes. Las excepciones autorizadas permiten candidatos locales, sin convertirlos en aprobación de fuente/certificaciónIG/FB/TikTok. Aprobación y naturalidad definitivas corresponden a la revisión final del usuario.

## Contador de cierre del objetivo

El tracker del objetivo terminócon `timeUsedSeconds:3194` (53min14s) y `tokensUsed:1394606`, sin presupuestodetokens. Son contadores globales delobjetivo: incluyen conversación/herramientas/revisiones ysu historial, noCPU ni pared de edición aislada, factura o desgloseporagente. Esto añade una medida globalreal al cierre; no convierte el resultadoen comparacióncontrolada2vs3. Recibo `qa-parallel-16-18-19/goal-completion-usage.json`.
