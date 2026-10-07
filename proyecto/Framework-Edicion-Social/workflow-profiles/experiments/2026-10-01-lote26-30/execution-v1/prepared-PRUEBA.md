# Piloto del 1 de octubre de2026: lote26–30

Estado: preparado, todavía no ejecutado. El usuario autorizó crear perfiles2/3 y prepararlos para mañana. No hay una automatización programada. El inicio será en la sesión de edición del lote.

## Por qué combinar material nuevo y conocido

Usar26–30para medir producción real. Ya hay52archivos de preproducción: inventariados con hashes en initial-inventory.json, sin editables/renders en ese inventario. Su pertinencia se decide contra voz real; disponibilidad no significa aprobación ni ahorro demostrado.

Usar el25terminado solo para regresión de herramientas: selección, integridad, conservación, registro y rechazo de reuso obsoleto. No reeditar cinco videos anteriores ni atribuir su mayor velocidad a un perfil: ya conocemos tomas, correcciones, recursos y solución. Las pruebas de herramientas pueden pasar hoy sin demostrar velocidad ni calidad de nuevas ediciones.

## Reparto y comparación

Propuesta operativa: dosF1, dosF2 y unF3. Primero ingesta compartida, duración, número/ambigüedad de cortes, complejidad narrativa, necesidades visuales y recursos disponibles. Registrar estas variables antes de editar. Elegir un video compatible conF3; agrupar los cuatro restantes en dos pares comparablesF1/F2 y alternar orden de producción para no hacer siempre primeroF1. Congelar asignación/criterio en un archivo nuevo assignment-v1.json y enlazarlo desde el cierre; no adaptar el reparto después de ver los tiempos.

El plan.json conserva asignacionesnullhasta ese momento. Si el usuario pide un perfil para todo el lote, prevalece y se registra un nuevo plan; no presentar ese lote como la comparaciónmixta prevista. Si no hay contenido apto paraF3, declarar incompatibilidad y ajustar antes de montar; no forzar una edición deficiente.

Dos pares no eliminan diferencias de contenido/modelo/caché/carga ni demuestran superioridad causal. Registrar modelo/esfuerzo reales si están disponibles, motor, configuración, colas/carga y recursos nuevos frente a preexistentes. No fabricar contadores que la herramienta no expone. F3 cambia alcance creativo y tendrá una evaluación propia de acabado esencial.

## Medición sin esconder el coste del piloto

- Ingesta del lote una sola vez, separada del tiempo individual.
- Relojes de fases para decisiones/preparación/ensamblaje/correcciones/QA/render/documentación/coordinación. Una fase por ejecución; los solapes de procesos van en medir_proceso, no se suman al reloj otra vez.
- Espera humana separada. Huecos sin registrar quedan sin medir; no se convierten en trabajo ni ahorro.
- Candidato estable y entrega registrados con timestamps reales; nunca medir desde una aprobación retrospectiva como si fuera el inicio.
- Contar checks completos, dirigidos, correcciones, renders/fallos y recursos generados sin uso, con motivo/evidencia.
- EnF2/F3 realizar auditoría adicional con cobertura del procedimiento actual sobre el mismo candidato, medida `experiment_audit`. Mostrar tiempo operativo observado y total delpiloto conauditoría/esperas/huecos. La sombra verifica defectos, no reconstruye la velocidad de montaje deF1.

La prueba podría tardar más que una ediciónnormal por su auditoríaextra. El reporte debe mostrarlo. Usar evaluation-template.json como referencia de filas, no como resultados ni schema de métricas verificadas completo.

## Decisión al cerrar

Verificar cumplimiento de QA común, defectos que escaparon al candidato, aprobación editorial específica y completitud de medición. F2evalúa conservación del alcance y reducción de trabajo repetido; F3evalúa utilidad/aceptación de un alcance más sencillo. Las observaciones iniciales sirven para ajustar, no para prometer porcentajes ni promover defaults. Si los tiempos no mejoran, registrar dónde; si faltan mediciones, mantener conclusiónpendiente.

Fallo de integridad/reuso/QAobliga controles requeridos y corrección; registrar el coste y volver aF1cuando corresponda, conrun separado. Mantener perfiles experimentales después de este primer lote hasta revisar resultados. No autorizar publicación ni sustituir archivos21–25.

## Inicio mañana

Leer [GUIA.md](../../GUIA.md), [QA_COMUN.md](../../QA_COMUN.md) y plan.json. Confirmar fuente/ingesta, asignación y perfil antes de crear cada workflow-run. Mantener las reglas vigentes de aprobación/render. Esta preparación no inicia grabación, ingesta ni edición de26–30.
