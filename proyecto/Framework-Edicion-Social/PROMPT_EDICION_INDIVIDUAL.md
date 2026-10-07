# Prompt para editar un video ya separado por ingesta

Sustituir `VIDEO-NN` por el identificador real y pegar este bloque en una tarea nueva del mismo proyecto.

```text
Edita únicamente VIDEO-NN y trabaja con autonomía hasta entregar su primer MP4 revisable.

Lee y aplica completamente:

- Framework-Edicion-Social/README.md
- Framework-Edicion-Social/FIDELIDAD_Y_DIVERSIDAD_PLANTILLAS.md
- Framework-Edicion-Social/templates/template-fidelity-review.md
- Framework-Edicion-Social/FLUJO_PRODUCCION_RAPIDA.md
- Framework-Edicion-Social/MATRIZ_PRODUCCION_PRO.md
- Framework-Edicion-Social/QA_PROFESIONAL.md
- Framework-Edicion-Social/SUBTITULOS_CONTEXTO_Y_LECTURA.md
- Framework-Edicion-Social/captions/catalog.json
- Framework-Edicion-Social/templates/caption-decision.json
- Framework-Edicion-Social/IMAGENES_CONTEXTO_REALISMO.md
- Framework-Edicion-Social/MOTOR_APRENDIZAJE.md
- Framework-Edicion-Social/OPERACION_OPTIMIZACION.md
- Framework-Edicion-Social/profiles/creative_preferences.json
- Framework-Edicion-Social/library/catalog.json
- Serie-IA-Negocios-10-Videos/asset-lock.json
- Serie-IA-Negocios-10-Videos/asset-intelligence/asset-index.json
- Serie-IA-Negocios-10-Videos/asset-intelligence/usage-history.json
- Serie-IA-Negocios-10-Videos/VIDEO-NN/PLAN_RECURSOS.md
- Serie-IA-Negocios-10-Videos/VIDEO-NN/manifest.json

Antes de editar, ejecuta el preflight con --video VIDEO-NN --stage edit. Si falla, corrige solo el bloqueo del video solicitado o informa el bloqueo real; no vuelvas a transcribir ni recorras el MOV completo.

Reclama VIDEO-NN en el production-board con un owner estable antes de escribir. Si ya pertenece a otra tarea, no modifiques su carpeta. Respeta el límite de heavy jobs y libera el claim únicamente cuando hayas terminado o entregado un bloqueo real.

Usa el take-map compartido y VIDEO-NN/source/*-source-range.json como fuente de verdad. El proxy es para montaje y preview. El render de entrega debe leer el rango exacto del MOV original registrado en source-range.json.

Si la toma contiene `MARCADOR. Corregir, corregir. Última frase.`, exige que la corrección figure como `resolved` después de revisión por escucha. El montaje debe quitar la frase equivocada y la claqueta completas, conservar la repetición nueva y documentar los rangos y empalmes en `cut-plan.json`; la puntuación de la transcripción no decide el corte por sí sola.

Escribe únicamente dentro de Serie-IA-Negocios-10-Videos/VIDEO-NN. Trata Framework-Edicion-Social y 00-INGESTA como solo lectura. No modifiques carpetas de otros videos.

Compara la transcripción real con los recursos preparados; conserva lo pertinente, retira lo que ya no coincida y genera solo lo necesario por improvisaciones. Nunca uses activos rechazados, inelegibles o deprecados.

Para cada imagen, verifica acción, personas, entorno y significado contra la frase hablada. Si el recurso disponible no encaja o es genérico, prioriza generar otro específico con fotografía natural y detalles del contexto; usa el banco solo si hay una alternativa adecuada. No fuerces reutilización por ahorro. Audita manos, miradas, perspectiva, equipos/pantallas, piel/luz y encuadre dentro del video; evita clichés de IA y conserva prompt/fuente, versiones y hashes. No prometas exclusividad ni que nadie detectará generación.

Crea `creative-blueprint.json` desde la toma real. Consulta el índice con la intención de cada beat y compila `creative-recipe-plan.json` usando catálogo, contrato, ledger e índice completos. Revisa hasta tres opciones, cobertura, contraindicaciones, esfuerzo y fatiga. Solo si existe una selección humana explícita, crea `creative-attribution.json` ligado por hash al plan y copia exactamente opción, receta, familia primaria, contribuyentes y seis módulos; si no existe, conserva las propuestas pendientes o la abstención y no inventes atribución. El ranking no es similitud visual ni aprobación. Después ejecuta `score_style.py`. Consulta también el contrato de serie: conserva dimensiones `locked`, usa los rangos `bounded` y rota deliberadamente las dimensiones creativas. Si el selector se abstiene, conserva la abstención y resuelve el estilo editorialmente; no fuerces el preset con mayor puntuación ni copies la plantilla anterior. Congela recursos en `asset-lock.json`, copia `dependency-map.json` y genera una clave de caché antes del ensamblaje.

Antes de montar captions, copia caption-decision.json dentro de VIDEO-NN y decide por contexto frase estable, énfasis, resaltado progresivo o impacto puntual; elige aparte pecho/espacio negativo, carril seguro o integración en escena. Conserva voz completa, máximo dos líneas reales y posición predecible. Verifica lectura sin sonido, tamaño móvil, caja completa/gestos/UI y tiempos; CPS/tamaños son presets de revisión, no hard fails numéricos. Reutiliza transcripción/timing, sin volver a analizar el maestro. Si falta preview real de destino, mantenlo pending sin certificar plataforma ni impedir un candidato editorial local.

Monta por capas, protege rostro y captions, compacta silencios según su función, usa zooms/transiciones/SFX semánticos y conserva descansos visuales. Después del primer render crea `review/review-packet.json` y `review/review.html` ligados a render, manifest, dependency-map, blueprint y cambios. Convierte cada corrección en rango, capa, elemento e instrucción; calcula impacto y revisa primero previews parciales con handles. La consola no sustituye el recibo de aprobación.

Antes de entregar, ejecuta el preflight con --video VIDEO-NN --stage render --deep, completa el qa-scorecard del render exacto y corrige todo hard fail. Entrega MP4, editable, transcripción, cut-plan, plan de recetas, atribución creativa solo cuando esté respaldada por una selección humana, manifiestos, consola de revisión, scorecard y resumen breve de decisiones.

Si el proyecto conserva HDR, esta primera entrega es un mezzanine editorial para revisión. Prepara un recibo `pending` ligado a su hash, pero no infieras aprobación. Después de la aprobación explícita se deriva el máster social neutral SDR `PLATFORM-MASTER-VERTICAL-001`. No generes Reels, TikTok ni Shorts hasta que exista aprobación explícita, content lock completo y linaje HDR→SDR verificado. Después se usa `PROMPT_DERIVADOS_PLATAFORMA.md`.
```

Este prompt presupone que la ingesta maestra ya terminó. Si el preflight informa `TAKE_MAP_MISSING`, `AUDIO_STREAM_UNLOCKED`, `VIDEO_TAKE_UNSELECTED`, `EDITING_PROXY_MISSING` o `SOURCE_RANGE_MISSING`, la tarea debe detener la edición pesada: esos problemas se resuelven una sola vez en la ingesta compartida, no dentro de cada video.

## Limpieza especializada de voz — a solicitud

Solo cuando el usuario pida explícitamente revisar la voz/el audio o eliminar ruido de fondo, aplicar `AUDIO_LIMPIEZA_VOZ.md` y la skill `revisar-limpiar-voz` en `/Users/iomijhondavid/.codex/skills/revisar-limpiar-voz/SKILL.md`. Una edición normal, render o QA habitual no activa diagnóstico especializado, nuevas limpiezas, pruebas de motores ni bypass/A-B obligatorios. Dentro de la revisión solicitada, sugerir tratamientos adicionales si se detectan eses molestas, golpes de aire, clics, eco u otros defectos; no aplicarlos automáticamente. Conservar original, recetas, hashes y QA del audio que sí se cambie. Esta instrucción sustituye el alcance general previo; no revierte medios ya procesados ni las reglas habituales de mezcla, ritmo, SFX y sincronía. La pista16k deASR no es fuente de mezcla.

## Prevención verificada — captions anidados en export HDR (VIDEO-16, 2026-09-30)

CLI0.8.98 puede forzar visibility:visible!important a descendientes de una capa DOM, aunque el wrapper temporizado esté oculto. En16, las22cajas ocuparon el mismo lugar y quedó el último caption durante todo el MP4. Studio/check correctos no detectaron esa diferencia del compositorHDR.

- Mantener tiempos data-start/data-duration y añadir opacity:0 inicial al wrapper de cada cue, con GSAP determinista que lo activa al inicio y lo apaga al final. Opacity protege todo el subtree. No rebautizar display:flex como causa demostrada ni parchear dependencias instaladas.
- Después de autorización de render, validar primero un export corto del pipeline real con al menos tres cues distintos, un gap vacío y un corte. Luego comprobar todos los cues, pausas y cola en el MP4 exacto. No sustituirlo por screenshots deStudio.
- Smoke16 de4,8s/29,253s de comando: seis estados inspeccionados con cues correctos y lanevacía0/3,5333s. Check actualizado42tiempos/300muestrasPASS70,488s. El render largoV2 sigue sujeto aQA.
- Para color, comparar el destino correcto: HDRtonemapped no acredita paleta idéntica aSDR ni pantallaHDRcertificada. No compensar coloresCSS a ojo. Producir/revisar un derivadoSDR gestionado para reproducción compatible cuando corresponda.

Diagnóstico con código/hash: Serie-IA-Negocios-10-Videos/VIDEO-16/qa-supplements/2026-09-30-caption-render-diagnostic/. V1rechazada se preserva; no modificar videos anteriores aprobados sin solicitud.

## Inicio permanente — instrucción del usuario aplicada desde VIDEO23

Al recibir un video nuevo, aplicar sin recordatorio las reglas y aprendizajes vigentes. Revisar AGENTS aplicables, últimas entradas de bitácora, framework, plantilla aprobada, dirección creativa y tres pasadas QA. Guardar en VIDEO-NN un recibo de inicio con documentos/hashes, decisiones de audio, captions, imágenes y rótulos, reutilización de ingesta y mejora concreta de flujo/calidad. Medir comandos y retrabajo cuando sea posible; no inventar ahorros ni resultados. Verificar la aplicación en editable y salida exacta, conservar versiones y documentar el cambio. No inferir aprobación del nuevo video ni escucha humana.


## Dirección de audio y hook — regla permanente VIDEO23, 2026-09-30

Aplicar `Framework-Edicion-Social/AUDIO_DIRECCION_Y_PROSODIA.md` (ruta desde raíz del proyecto). Antes de elegir música/SFX, analizar voz real por intensidad/contrastes, pitch/entonación estimados, pausas, ritmo y cambios por frase; ligar interpretación a palabras/contexto y separar inferencia de escucha. Reutilizar ASR y voz intactos. Comparar aumento de nivel, ubicación o carácter cuando un efecto no se perciba. **Todo hook inicial lleva SFX integrado y debe comprobarse en QA**, además del mínimo dos identidades distintas para20–30s. Registrar niveles contra voz, picos/masking y reproducción real; ausencia de hook/vínculos inválidos bloquea render mediante verificación equivalente a `scripts/revisar_presencia_sfx.py`. Medición no certifica audibilidad ni emociones; mantener escucha por confirmar si falta.


## Selección versionada de flujo de edición

Flujo1actual sigue predeterminado. Por petición «con flujo2» o «con flujo3», aplicar [GUIA de perfiles](workflow-profiles/GUIA.md), su perfilJSON y [QA común](workflow-profiles/QA_COMUN.md), conservando las reglas vigentes. Estos perfiles son experimentales;2organiza/reutiliza trabajo comprobado,3simplifica alcance creativo sin omitir controles requeridos. La preparación delpiloto1deoctubre vive en [PRUEBA26–30](workflow-profiles/experiments/2026-10-01-lote26-30/PRUEBA.md). Registrar run/versiones/tiempos y separar espera humana/auditoríaextra. Procedimiento anterior conservado como referencia1; esta selección cambia organización/alcance declarado, no autorización, ingesta, fidelidad, QA ni aprobación.


### Regla vigente de identidad visual

En cada próximo video/lote, aplicar `FIDELIDAD_Y_DIVERSIDAD_PLANTILLAS.md` y documentar `VIDEO-NN/QA_FIDELIDAD_PLANTILLA.md`. Antes de composición completa, usar ficha/tablero aprobados como referencia y documentar mapa de voz, recursos, geometría y maqueta ligera `conforme_para_montaje`. Corregir desvíos antes de avanzar; no exigir comparación con vecinos ni cuota de diferencias. Preservar estructura/composición/recursos/movimiento distintivos; no reducir una familia a cambio de colores/letras. Revisar recorte/gestos/espacio inferior y funciones de iconos/SVG/imágenes/diagramas/elementos de interfaz. Comprobar conservación durante montaje y en QA del MP4 exacto; conservar aprobaciones previas.
