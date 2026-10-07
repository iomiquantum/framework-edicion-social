# Flujo1, flujo2 y flujo3

Preparados el2026-09-30. Los perfiles son instrucciones operativas versionadas sobre el framework existente, no tres motores ni un editor automático nuevo. El flujo1 es la referencia actual y sigue predeterminado. Los perfiles2/3 están listos para piloto; todavía no hay ahorro ni equivalencia audiovisual demostrados por ellos.

| Selección | Alcance | Organización |
|---|---|---|
| Flujo1, versión1.0.0 | Edición personalizada actual | Procedimiento vigente; en el piloto se agregan mediciones |
| Flujo2, versión0.1.0 | Misma intención y cobertura de calidad | Consolidación previa, controles dirigidos, reutilización verificada, procesos independientes simultáneos e índice único de evidencia |
| Flujo3, versión0.1.0 | Edición esencial, más estandarizada | Organización del2; plantilla elegible, captions contextuales estables y motion probado; menos diseño/recurso a medida |

Leer siempre [QA_COMUN.md](QA_COMUN.md), además de las reglas aplicables y delJSON del perfil. La selección se registra, nunca se infiere de que una tarea vaya lenta. Pedir «edita este lote con flujo2» elige ese perfil para el lote; una instrucción específica del usuario prevalece sobre la asignación experimental. Sin elección ni piloto, usar flujo1.

## Arranque de una ejecución

Desde la raíz del proyecto, registrar una carpeta nueva de mediciones, sin copiar ni sobrescribir el editable:

```bash
python3 Framework-Edicion-Social/scripts/workflow_run.py init --video VIDEO-26 --flow 2 --trial LOTE-26-30 --out Serie-IA-Negocios-10-Videos/VIDEO-26/workflow-runs/flujo2-01
python3 Framework-Edicion-Social/scripts/medir_fases_edicion.py start --run Serie-IA-Negocios-10-Videos/VIDEO-26/workflow-runs/flujo2-01 --phase assembly --kind work
```

Al cambiar de fase, detener el reloj y abrir el siguiente. No dejarlo abierto durante ausencia/espera:

```bash
python3 Framework-Edicion-Social/scripts/medir_fases_edicion.py stop --run Serie-IA-Negocios-10-Videos/VIDEO-26/workflow-runs/flujo2-01
python3 Framework-Edicion-Social/scripts/medir_fases_edicion.py start --run Serie-IA-Negocios-10-Videos/VIDEO-26/workflow-runs/flujo2-01 --phase qa_pre_render --kind work
```

Registrar `user_wait` al esperar respuesta; `experiment_audit` para la revisión adicional del piloto. `command` cubre el intervalo de un proceso durante el que no hay trabajo del editor; los tiempos internos de subprocess se registran también con medir_proceso, pero no se suman otra vez al reloj por fases. El reloj por fases es una atribución operativa explícita, no prueba de atención continua ni tokens. Los huecos quedan sin medir. Ingesta usa ejecución de lote separada, nunca se cobra completa cinco veces.

Para la ingesta compartida el temporizador admite una carpeta independiente, sin workflow_run de video: `medir_fases_edicion.py start --run RUTA_EXPERIMENTO/ingesta-lote --phase intake --kind work`, después stop y summary. Guardar ese resumen una vez y enlazarlo en el informe del lote y en los cinco índices individuales; no sumarlo cinco veces.

## Secuencia del flujo2

1. Revisar recibo del lote y documentos cambiados. Confirmar tomas, plantilla/contrato y disponibilidad contextual de recursos. Resolver ambigüedades temprano, con ASR dirigido si hace falta; no repetir masterASR.
2. Definir antes del montaje titulares semánticos, captions, función de la imagen y SFX/música contra voz propia. Mantener variación por video. No copiar ganancias, perfil de ruido ni composición del anterior por ahorro.
3. Montar por capas. Lint temprano cuando sea útil. Revisar estados afectados durante correcciones; reservar check integral para el candidato estable, sin duplicar lint que ya incluye check.
4. Completar las tres pasadas sobre esa versión. Reutilizar únicamente evidencia intacta de dependencias equivalentes, con puente escrito de alcance; un cambio desconocido obliga revisión integral. La tercera pasada conserva cobertura de toda la pieza.
5. Obtener aprobación y renderizar por wrapper. Checks ligeros obligatorios se mantienen antes de captura; no se cachea autorización humana ni se omite el guard.
6. Verificar el MP4 exacto y completar los recibos habituales. Generar un índice de tiempos/evidencias; vincularlo a bitácora/changelog sin copiar nuevamente grandes logs. Auditoría sombra del piloto, separada y visible, antes de entrega.

## Alcance del flujo3

Aplicar la organización del2. Usar plantilla aprobada compatible y motion ya probado; reducir exploración y diseño a medida, con voz, captions y SFX contextualizados. Preferir un apoyo breve cuando ayude; no generar por cuota ni montar un recurso genérico por disponibilidad. Evitar por defecto nuevosdiagramas,3D, complejas transiciones o muchos recursos diferentes. Los requisitos específicos del contenido o del usuario prevalecen.

Si faltan recursos pertinentes y son necesarios, generar/resolver lo necesario o registrar escalamiento a2. Avisar motivo/impacto, conservar el run anterior y abrir otro con el nuevo perfil; no exceder un límite explícito ni cambiar silenciosamente el perfil. No confundir menos personalización con equivalencia creativa del1.

## Reutilización de QA: elegibilidad, no aprobación

`change_impact.py` calcula cambios declarados; no descubre modificaciones. `cache_key.py` conserva su comportamiento actual y no registra por sí solo motor/binarios/configuración. La capa nueva `qa_reuse_context.py` complementa esos instrumentos sin modificarlos.

Crear un spec explícito con `scope_id`, `coverage_note` y `groups` exactos: source,transcription,cut_plan,visual_style,visual_assets,audio_assets,mix,engine. Cada grupo contiene rutas a archivos existentes, relativas al spec. En engine incluir configuración, versiones reales, argumentos de captura/render, scripts/generadores, fuentes tipográficas o sus referencias, binarios/manifiestos verificados y el perfil; separar medios visuales y sonoros. Un manifiesto declarado no demuestra que un binario coincida: comprobar y guardar sus hashes reales. No introducir carpetas deQA/logs que cambian dentro del conjunto creativo.

```bash
python3 Framework-Edicion-Social/scripts/qa_reuse_context.py snapshot --spec context-spec.json --out context-v1.json
python3 Framework-Edicion-Social/scripts/qa_reuse_context.py compare --before context-v1.json --after context-v2.json --current-spec context-spec.json --out impact-v2.json
```

El snapshot debe congelarse junto a la evidencia. `compare` comprueba integridad y archivos actuales; sin inventario actual falla cerrado. Solo sugiere ámbitos candidatos a reutilización; todavía hay que verificar informeQA PASS real, cobertura, hashes del informe/contexto y pendientes humanos. Nunca heredar aprobación de otro artefacto ni QA delMP4 para un export nuevo. Si no se puede probar el conjunto completo de dependencias, repetir el control afectado o integral. El helper depende de que el inventario sea completo; no es un descubridor de todos los recursosHTML.

Estilo incluye HTML/CSS y rótulos visibles: su cambio invalida revisión semántica. Un activo visual nuevo invalida también captions, por posibles cambios de fondo/contraste/protección. Solo el audio puede quedar candidato si sus dependencias permanecen intactas. Si el index contiene parámetros de audio, incluirlo también en mix; su hash cambiado obliga comprobar ese ámbito hasta tener una extracción de parámetros verificada.

## Registro y cierre

Registrar cada check, corrección, render, fallo, recurso generado/sinuso o escalamiento con evidencia, sin inventar ausencia por falta de eventos:

```bash
python3 Framework-Edicion-Social/scripts/workflow_run.py event --run RUTA_RUN --kind full_check --note "Candidato estable, revisión integral" --evidence RUTA_CHECK_JSON
python3 Framework-Edicion-Social/scripts/workflow_run.py report --run RUTA_RUN --out RUTA_RUN/resumen-v1.json --evidence RUTA_ENTREGA_JSON --evidence RUTA_QA_JSON
```

Registrar `candidate_ready` cuando exista el candidato revisable concreto y `local_delivery_completed` cuando termine entrega/QA, ambos con `--evidence` obligatorio. El informe conserva el primer timestamp de esos hitos; no los reconstruye desde tiempos retrospectivos ni los convierte en aprobaciones.

El informe calcula tiempos/cuenta eventos registrados y enlaza archivos porhash; no aprueba ni redacta automáticamente decisiones de bitácora. Reutilizar el índice en los documentos habituales evita duplicar datos; conservar petición, cambios, motivo, validación, resultado, aprendizaje y pendientes. No rellenar con ceros fases desconocidas para satisfacer el schema anterior.

Cada run conserva copias de perfil y QA común. El informe histórico valida esas copias y señala cambios de reglas vigentes; permite reconstruir el registro anterior sin reinterpretar su autorización. Si cambian reglas durante trabajo nuevo, crear un run versionado antes de registrar más eventos. Alterar las copias congeladas bloquea el informe.

## Retorno al flujo1

Seleccionar1en una ejecución nueva; no borrar ni modificar la experimental. Los scripts previos y las entregas21–25 se conservan. La referencia de documentación/código anterior a esta integración vive en `baseline/2026-09-30/manifest.json`. Versionar cualquier nueva política; ningún perfil se promueve automáticamente al terminar cinco videos.


## Identidad visual y perfiles — aclaración2026-09-30

En1/2/3 aplicar [FIDELIDAD_Y_DIVERSIDAD_PLANTILLAS.md](../FIDELIDAD_Y_DIVERSIDAD_PLANTILLAS.md) y QA_COMUNv0.1.2. «Menos diseño a medida» en3 no significa borrar el lenguaje visual de la plantilla ni cambiar solo paleta/tipografía. Priorizar módulos probados propios de esa familia y documentar referencia aprobada/encuadre/recursos y control `conforme_para_montaje` antes de composición completa, sin comparación obligatoria de vecinos en `QA_FIDELIDAD_PLANTILLA.md`. Mantener snapshots/runs anteriores; no alterar baseline para fingir que esta aclaración era histórica.
