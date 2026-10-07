---
name: revisar-limpiar-voz
description: Revisar ruido de fondo o limpiar una voz grabada únicamente por solicitud explícita del usuario. Preparar diagnóstico, comparación y QA con recetas verificadas; sugerir tratamientos adicionales si aparecen sibilancias, golpes de aire, clics o eco. No activar durante edición normal, QA rutinario, mezcla de música/SFX ni por la mera presencia de un video.
---

# Revisión y limpieza de voz a solicitud

La instrucción del usuario del 2026-09-30 limita este trabajo a una revisión de voz o eliminación de ruido expresamente solicitada. Disponer de modelos o detectar un valor de ruido no activa procesamiento. La invocación implícita está desactivada en `agents/openai.yaml`.

## Activación y alcance

- «Edita el video18», «renderiza», «aplica la plantilla», QA habitual: no activar la skill, instalar motores, comparar denoisers ni exigir bypass/A-B de limpieza.
- «Revisa el ruido/la voz/el audio», «se oye fondo, corrígelo», «elimina el ventilador», o `$revisar-limpiar-voz`: activar sobre el material indicado. Una consulta conceptual se contesta sin procesar medios.
- Revisión solicitada: diagnosticar y sugerir. Eliminación solicitada: preparar limpieza conservadora y resultado comparativo dentro del alcance autorizado. No heredar de un video autorización para los siguientes ni todo el lote.
- Durante esa revisión, eses fuertes, golpes de aire, clics o eco motivan una sugerencia específica. No añadir automáticamente de-esser, de-click, de-reverb, EQ correctiva o compresión extra a una solicitud limitada a ruido de fondo.
- Conservar montaje, captions, imagen y SFX salvo petición que también los abarque. No sustituir una versión aprobada por una audición experimental.

## Procedimiento

1. Localizar original, pista, rango útil, versiones y autorización. Reutilizar ingesta, transcripción y contextos; no reanalizar el master completo por cada revisión. Para cambiar/exportar una composición HyperFrames, aplicar su skill de entrada y reglas vigentes.
2. Partir de voz original a frecuencia nativa, en copia; el WAV16k de ASR no es fuente de mezcla. Separar reporte humano, medida e inferencia. Leer [diagnóstico](references/diagnostico.md) para decidir qué sugerir.
3. Leer [recetas](references/recetas.md), localizar motor/modelo por hash y elegir uno o dos candidatos justificados. Ampliar si hace falta o se pide comparación completa. Cada candidato parte del original; no encadenar motores por defecto.
4. Procesar con contexto antes de cortar; medir/compensar delay y conservar muestras exactas. Igualar A/B mediante ganancia constante y los mismos canales, sin compresión/puerta/SFX extra. No aumentar agresividad solo para obtener silencio absoluto.
5. Revisar fondo durante voz y pausas, fonemas, eses, respiraciones, timbre y artefactos. Preparar diferencia alineada cuando ayude. ASR/correlación/RMS no prueban fidelidad auditiva; sin escucha demostrable mantener `por confirmar`.
6. Si cambia un video, mezclar desde voz/SFX PCM nativos y comprobar el export exacto: duración, canales, loudness, true peak, decode y sincronía. Para cambio soloaudio, remux y verificar todos los paquetes de imagen/timestamps antes de reutilizar QAvisual. Mantener guards de texto/hook/SFX dentro de la entrada de render. No reconstruir efectos restando AAC.
7. Entregar A/B, receta/versiones/hashes, resultado técnico y límites. No convertir recomendación técnica en aprobación humana. Registrar cambios en bitácora/changelog cuando el proyecto lo exija.

## Recursos según necesidad

- [Diagnóstico](references/diagnostico.md): investigación de sibilancia y otros defectos; sugerencias, sin tratamiento automático.
- [Recetas](references/recetas.md): FFmpeg, DF3, ClearerVoice, Resemble y RNNoise; contextos, latencia, A/B y export.
- [Evidencia original](references/evidencia-proyecto.md): guías, fuentes, modelos, pruebas, scripts, recibos y estado de VIDEO17. Cargar solo lo pertinente al motor/tarea elegidos.
- `scripts/rnnoise_wav.py`: helper para contexto48k y archivo nuevo; exige librería/SHA y compensación explícitos. No mezcla, normaliza ni modifica editables.

Adobe es opción externa pendiente de acceso y prueba. No crear cuentas, pagar ni subir voz por una solicitud genérica de edición; usar autorización concreta al incluir un servicio externo. Reutilizar modelos/entornos disponibles antes de volver a instalar o descargar.
