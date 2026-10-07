# Banco de plantillas sociales

## Ubicación y estados

El registro maestro vive en `Framework-Edicion-Social/template-bank/registry.json`. Cada proyecto conserva un `template-candidate.json` con la configuración utilizada. El registro separa cuatro namespaces para que una aprobación no cambie silenciosamente otro estado:

| Namespace | Campo | Estados | Qué responde |
| --- | --- | --- | --- |
| Artefacto fuente | `artifact_approval.status` | `not_applicable`, `pending_review`, `pending_receipt`, `approved`, `changes_requested`, `rejected` | ¿El render exacto está aprobado y ligado a un recibo verificable? |
| Reutilización | `template_reuse.status` | `not_applicable`, `pending`, `series_default`, `creator_default`, `retired` | ¿Existe autorización independiente para reutilizar la plantilla y con qué alcance? |
| Madurez de familia | `status` | `planned`, `candidate`, `testing`, `validated`, `retired` | ¿En qué etapa editorial se encuentra la familia? |
| Rendimiento | `performance.status` | `no_data`, `awaiting_data`, `inconclusive`, `context_supported`, `context_opposed`, `expired` | ¿Qué evidencia comparable existe después de publicar? |

`artifact_approval: approved` exige un recibo existente del video exacto. `template_reuse: series_default|creator_default` exige su propia base y referencia de autorización; nunca se deriva del recibo del artefacto ni de una métrica de rendimiento. `validated` describe madurez de la familia, no autorización universal de uso.

Nada entra al banco como default por haber renderizado correctamente ni porque un video completo haya sido aprobado: primero se separa la aprobación del archivo de la autorización para reutilizar la plantilla. Después se prueba dentro de contextos comparables. No existe una ganadora universal; varias familias pueden quedar simultáneamente respaldadas para mensajes, audiencias u objetivos diferentes.

Cada candidato aprobado se registra por hash en `golden-master-registry.json`. Si cambia el archivo o sus metadatos, se crea una nueva versión y se repite su revisión; nunca se sobrescribe silenciosamente la referencia.

## Cinco familias iniciales

1. **T01 Editorial Loop** — hook contrario, ciclo/proceso y pregunta directa. Candidata creada con VIDEO-01.
2. **T02 Clean Authority** — cámara dominante, datos mínimos y ritmo sobrio para credibilidad.
3. **T03 Split Evidence** — presentador + evidencia/captura, útil para demostraciones y comparativas.
4. **T04 Kinetic Checklist** — pasos, listas y palabras cinéticas para contenido práctico.
5. **T05 Human Minimal** — casi sin B-roll, gestos y subtítulos muy cuidados para temas personales.

Las cinco comparten contratos técnicos —9:16, zonas seguras, una pista de captions, voz prioritaria— pero no la misma silueta visual.

## Variación y linaje

Cada familia registra plantilla padre, hipótesis del cambio, videos derivados y dimensiones controladas. Las exploraciones deben producir diferencias estructurales reales, no simples recolores:

- estructura narrativa;
- formato visual dominante;
- estilo y dirección artística;
- ritmo y distribución de descansos;
- transiciones y lenguaje de cámara;
- tratamiento sonoro.

El contrato de serie clasifica cada dimensión como `locked`, `bounded`, `rotating` o `free`. Lo fijo conserva calidad e identidad; lo rotativo crea diversidad; lo libre responde al contenido actual. La similitud alerta sobre repetición, pero nunca decide si un video es bueno.

## Protocolo de prueba

- Rotar familias, no solo paletas.
- Comparar piezas de tema, duración y fuerza de hook semejantes.
- Acumular al menos 3 publicaciones por familia antes de sacar conclusiones; 5–10 es preferible.
- Registrar por plataforma: retención a 3 s, tiempo medio visto, porcentaje completado, replays, compartidos, guardados, comentarios y conversión/CTA.
- Completar `performance-review.json` con ventana, distribución, audiencia, cohorte y confusores; ninguna métrica promueve automáticamente una regla o plantilla.
- No declarar ganador por vistas brutas: usar principalmente retención normalizada, finalización y acciones de alta intención.
- Revisar cada 10–15 publicaciones; promover contextualmente, iterar o retirar.

## Qué guardar siempre

- Proyecto editable limpio.
- Captura de portada y contact sheet.
- Tokens de color/tipografía/zonas seguras.
- Mapa de escenas y capas.
- Reglas de audio y SFX.
- Variables reemplazables.
- Historial de métricas y versión de plantilla.
- Blueprint creativo, decisión de estilo, perfil de plataforma y SHA-256 del golden master.
