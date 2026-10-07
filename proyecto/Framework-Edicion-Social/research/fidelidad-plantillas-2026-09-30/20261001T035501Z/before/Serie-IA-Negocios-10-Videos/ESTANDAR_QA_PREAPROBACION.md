# Estándar QA antes de pedir aprobación

Vigente desde: 2026-09-26.

Este gate aplica a todos los videos de la serie. Su objetivo es que el usuario reciba una propuesta que ya se vea bien, se oiga bien y cumpla el lenguaje definido, no una primera inspección disfrazada de entrega.

## Pasada 1 — Visual y editorial

Reproducir o inspeccionar toda la pieza, incluidos inicios, cierres y transiciones.

- Cada texto aporta significado directo a la frase. Se eliminan rótulos de relleno, referencias internas y adornos que no comuniquen.
- Titulares y captions usan el ancho seguro disponible, tienen peso suficiente y se leen en pantalla de teléfono sin ampliar.
- Cabeza, ojos y boca quedan libres; captions a la altura del pecho/corazón salvo una justificación documentada.
- No hay desbordes, solapes, saltos de jerarquía, huérfanas o líneas demasiado pequeñas.
- Cuando existe espacio libre útil, los módulos se distribuyen verticalmente en vez de apilarse junto al borde superior. Como referencia, se conservan 24–32 px entre cajas independientes y se revisan también colas, bordes y líneas decorativas.
- Las líneas, rieles y bordes decorativos quedan fuera del área tipográfica; nunca atraviesan letras ni reducen su legibilidad.
- Los captions construidos con varios nodos (`span`, `b` o palabras resaltadas) usan separación CSS explícita; se comprueba que ninguna pareja de palabras aparezca concatenada.
- Los recursos visuales representan lo que se está diciendo; no son decoración genérica.
- Los recursos de apoyo a pantalla completa se usan como acentos breves. Como referencia, duran 1,5–2,5 s y regresan al presentador antes de perder autoridad o atención. Una permanencia mayor se justifica en el QA.
- La identidad del video es coherente internamente y distinguible de los videos adyacentes. Se compara al menos con el anterior y el siguiente cuando existan.
- Se inspeccionan fotogramas del hook, cada cambio de escena, captions largos y cierre.

## Pasada 2 — Audio y ritmo

Revisar de inicio a fin la voz, los empalmes y la mezcla.

- Ejecutar detección de silencios. Toda pausa mayor a 1,25 s se recorta o se justifica como decisión narrativa.
- No quedan colas mudas ni captions sostenidos sobre audio inexistente.
- No se inventa voz ni se presenta como pronunciada una frase que no está en la fuente.
- Cada corte mantiene respiración natural y no trunca sílabas o terminaciones.
- La voz conserva prioridad y continuidad de nivel.
- Los SFX coinciden con cambios semánticos o visuales. Para una pieza de 20–30 s se usa como referencia 3–5 acentos funcionales, sin convertir cada palabra en efecto.
- Los SFX deben resultar perceptibles en la mezcla de revisión y mantenerse aproximadamente 8–14 dB por debajo de la voz contemporánea como punto de partida; cualquier excepción se documenta.
- Si no hubo escucha humana demostrable, el estado se marca `por confirmar` aunque las mediciones automáticas pasen.

### Ruido de fondo y restauración de voz · solo a solicitud, 2026-09-30

Solo cuando el usuario pida explícitamente revisar la voz/el audio o eliminar ruido de fondo, aplicar `../Framework-Edicion-Social/AUDIO_LIMPIEZA_VOZ.md` y la skill `revisar-limpiar-voz` en `/Users/iomijhondavid/.codex/skills/revisar-limpiar-voz/SKILL.md`. Una edición normal, render o QA habitual no activa diagnóstico especializado, nuevas limpiezas, pruebas de motores ni bypass/A-B obligatorios. Dentro de la revisión solicitada, sugerir tratamientos adicionales si se detectan eses molestas, golpes de aire, clics, eco u otros defectos; no aplicarlos automáticamente. Conservar original, recetas, hashes y QA del audio que sí se cambie. Esta instrucción sustituye el alcance general previo; no revierte medios ya procesados ni las reglas habituales de mezcla, ritmo, SFX y sincronía. Los puntos siguientes aplican dentro de esa solicitud, no en cada edición.

- Diagnosticar cada toma desde la voz y sus pausas: piso de ruido, sonidos ajenos, clipping y cambios de ambiente. No asumir que toda respiración o energía grave es ruido.
- Si un ruido de fondo perjudica la voz, preparar una reducción conservadora en un derivado separado, conservar la voz sin procesar y registrar herramienta, parámetros y hash. Una pista ya limpia puede conservarse sin reducción.
- Comparar original y candidata sobre el mismo fragmento y al mismo nivel; verificar consonantes, respiraciones, timbre y artefactos por escucha. Las mediciones son evidencia técnica y no sustituyen esa escucha.
- Medir cualquier latencia del procesador y compensarla antes del montaje; comprobar duración y sincronía con labios después de la limpieza. Gate, EQ y compresión no equivalen a supresión de ruido.
- Ninguna supresión autoriza inventar fonemas ni recrear la voz. Si la comparación humana está pendiente, mantenerla como `por confirmar` y no afirmar que el audio fue escuchado.

## Pasada 3 — Integración final

Revisar otra vez la pieza completa después de todas las correcciones.

- Ejecutar `hyperframes lint`, `hyperframes check` con muestras de transición y snapshots.
- Revisar el arranque, cada transición, el fotograma inmediatamente anterior y posterior a cada corte y el cierre.
- Comprobar captions contra la voz y verificar que no aparezcan durante silencios indebidos.
- Revisar una hoja de contacto o capturas equivalentes y una reproducción a tamaño móvil.
- Registrar en el QA del video qué se verificó, con evidencia y pendientes reales.

Solo después de que las tres pasadas estén documentadas puede solicitarse aprobación. La aprobación del usuario habilita el render de entrega; no corrige retrospectivamente fallos que debieron detectarse antes.
