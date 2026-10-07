# Revisión especializada de voz solo a solicitud

2026-09-30. El usuario confirma conservar lo ya realizado y limita la revisión/limpieza avanzada a su petición explícita. Esta decisión sustituye el alcance general previo, sin modificar voces/render/aprobaciones existentes.

La edición ordinaria conserva su mezcla, ritmo, SFX, sincronía, loudness/picos y QA habituales. No requiere instalar motores, medir ruido de cada toma, comparar denoisers ni documentar bypass automáticamente. «Revisa la voz/el audio», «elimina el ruido» o una invocación explícita activan la skill sobre el material indicado, sin extender autorización al próximo video. Un hallazgo incidental del QA puede motivar una sugerencia, sin iniciar procesamiento.

Skill personal: [revisar-limpiar-voz](</Users/iomijhondavid/.codex/skills/revisar-limpiar-voz/SKILL.md>), con `allow_implicit_invocation: false`. Investigación adicional: [diagnóstico y sugerencias](</Users/iomijhondavid/.codex/skills/revisar-limpiar-voz/references/diagnostico.md>). Recetas y evidencia enlazadas desde la skill; modelos/medios grandes permanecen en VIDEO17. Documentación de la comparación existente: [siete opciones reales](COMPARACION_LOCAL_V17_V3.md).

En una revisión solicitada, si aparecen sibilancias (“s”), golpes de aire (“p”/“b”), clics de boca, eco, dureza/retumbo, problemas de dinámica, clipping o empalmes, registrar frase/tiempo/evidencia y sugerir de-esser, de-plosive, de-click, de-reverb, EQ u otro tratamiento pertinente. No aplicar todos por defecto ni ampliar una eliminación de fondo a esas correcciones sin solicitud. Respiraciones/fonemas/timbre se preservan; denoiser no equivale a de-esser. Ninguna de esas restauraciones adicionales se ejecutó en VIDEO17.

Fuentes investigadas/consultadas2026-09-30: [Adobe Audition: de-esser y dinámica](https://helpx.adobe.com/ph_en/audition/desktop/effects-reference/amplitude-compression-effects.html), [iZotope: limpieza de voz](https://www.izotope.com/community/blog/how-to-clean-up-voice-recordings-video-podcasts). Estas guías describen tratamientos; no demuestran defecto en una nueva toma ni disponibilidad local de esas herramientas.

RNNoise fue primera recomendación técnica por pausas de17, no aprobado ni fijado para otros videos. Editable17v2/afftdn18 y todas las audiciones quedan intactos. Adobe pendiente de acceso/prueba; noaudio subido. Un helperRN48k reutilizable y su validación sintética no son una nueva audición de voz ni aprobación de calidad.

Historial: snapshots completos de los nueve puntos de activación anteriores en `skill-a-solicitud/before/`; preferencias incluyen `previous_versions` y evidencia anterior junto a la nueva decisión. Bitácora/changelogs registran la transición, sin presentar la última decisión como original.
