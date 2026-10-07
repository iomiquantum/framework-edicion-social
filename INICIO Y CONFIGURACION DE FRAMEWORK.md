# INICIO Y CONFIGURACION DE FRAMEWORK

**Entrada para alumnos:** `INICIO WINDOWS.cmd` o `INICIO MAC.command` abre la guía automáticamente. `INICIO.html` contiene el rescate si el navegador o el lanzador no abren. Los nombres largos de INICIO siguen funcionando.

[GUIASUPERDETALLADA.html](./GUIASUPERDETALLADA.html) contiene 15 pasos, casillas, notas y ayudas. [GUIA_GRABACION_MASTER.html](./GUIA_GRABACION_MASTER.html) explica visualmente qué leer, qué decir como marcador y cuándo pausar. Desde el asistente, el guardado queda en `MI-PROGRESO/` junto a la entrega; un HTML abierto directamente solo permite lectura y respaldo manual del navegador.

## Guardado del alumno

- `MI-PROGRESO/guia.json`: último paso, marcas y notas por sistema.
- `MI-PROGRESO/borrador-edicion.json`: cuestionario, paleta, plantillas, rutas y paso del asistente, sin duplicar masters.
- `MI-PROGRESO/guion-grabacion.json`: guion de práctica, números, ejemplo elegido y checklist de grabación.
- `MI-PROGRESO/ultimo-lote.json`: acceso al lote recién preparado, para evitar crearlo otra vez al reiniciar.
- `.anterior.json`: copia previa de cada documento. Se recupera con aviso si la actual está dañada; si ambas fallan, se detiene el guardado en vez de borrarlas.
- `MI-PROGRESO/copias/`: respaldos explícitos de la guía; se pueden recuperar desde un listado sin depender del selector de archivos del navegador.
- `MI-PROGRESO/acciones.jsonl` y `resultados/`: estado de acciones, diagnósticos, instalaciones y pruebas. Una acción interrumpida no cuenta como completada.

El estado se confirma tras escribir el archivo, con escritura atómica y control de revisión entre ventanas. Si falla la conexión o el disco, aparece el aviso y quedan cambios pendientes en la página; espera la confirmación o conserva un respaldo antes de cerrar. La sesión del asistente no autoriza descargas automáticamente y no se comparte entre computadoras. No copies `MI-PROGRESO` con datos del profesor a la entrega inicial de los alumnos.

Esta es la misma entrega ligera, ahora con asistente para **Windows y Mac**. Copia esta carpeta completa una sola vez. Su nombre histórico, `Entrega-Windows-v1`, no limita los sistemas compatibles. No necesitas los videos de trabajos anteriores.

## Abrir

- **Windows:** doble clic en `INICIO Y CONFIGURACION DE FRAMEWORK.cmd`.
- **Mac:** doble clic en `INICIO Y CONFIGURACION DE FRAMEWORK.command`. Si Finder no permite ejecutarlo, abre Terminal, escribe `bash `, arrastra este archivo a la terminal y pulsa Enter. No hace falta desactivar Gatekeeper ni cambiar una política global.
- **Desde Codex:** abre esta carpeta y pide: «Lee INICIO Y CONFIGURACION DE FRAMEWORK.md e inicia el asistente local. No instales nada sin mi autorización». Con Python ya instalado, el comando es `python3 tools/asistente.py` en Mac y `python tools/asistente.py` en Windows.

El inicio abre la guía en el navegador habitual; desde allí pulsa ABRIR ASISTENTE. Si no abre, usa el botón de `MI-PROGRESO/ABRIR GUIA.html`. Deja la terminal abierta mientras lo utilizas; Ctrl+C lo cierra. Necesitas una carpeta con permiso de escritura. Las rutas con espacios y tildes son válidas. Usa una copia local; evita que dos equipos escriban simultáneamente en la misma carpeta sincronizada.

Si falta Python, el inicio propone instalar uv de Astral y Python dentro de la entrega. Pide escribir **SI** antes de descargar. No modifica el PATH global. También puedes instalar Python manualmente desde [python.org](https://www.python.org/downloads/).

## Los seis pasos

1. **Equipo.** Lee CPU, RAM, gráfica y espacio libre. Revisa Python, Node, FFmpeg/ffprobe y filtros de audio/color, HyperFrames/Chrome, recursos, skills, ASR y audio asistido. Consulta las versiones disponibles. «Preparar instalación» muestra fuente, destino y cambios; «Autorizar e instalar» los ejecuta.
2. **Contexto.** Tema, audiencia, objetivo, publicación, tono, movimiento, CTA, marca, restricciones, guion y rutas a documentos.
3. **Colores.** Cinco propuestas locales según tema/tono, con historial de paletas elegidas en este asistente. Puedes cambiar los cuatro colores. Se comprueba contraste de tinta y papel. No se promete ausencia de semejanza visual con todos los videos históricos.
4. **Plantillas.** Las 30 propuestas con la paleta elegida, filtros y tablero ampliable; puedes ver también los originales. Las fotografías no se recolorean. Selecciona una o varias. Las vistas son estáticas y no son un nuevo video aprobado.
5. **Masters.** Pega las rutas completas, una por línea. No se copian ni se mueven. También puedes poner tus nuevas grabaciones en `entrada-masters/`. Elige cantidad de videos y duración orientativa. Un master puede servir para varios videos.
6. **Empezar.** Crea el lote y las carpetas, guarda contexto, paleta y referencias. Abre `proyecto/` en Codex y pega la instrucción generada. Codex continúa con ingesta, planificación, revisión de fidelidad y edición según las reglas vigentes.

Antes de indicar «todo listo», exige diagnóstico satisfactorio, prueba técnica de render con movimiento/audio en ese equipo y confirmación tuya de haber iniciado sesión en Codex. El diagnóstico puede terminar con pendientes: no se ocultan ni se consideran aprobados. Puedes preparar el contexto aunque aún falte instalar algo.

## Qué se instala y cómo se actualiza

- **Node:** última estable consultada en nodejs.org, ZIP/tar oficial y SHA-256; dentro de `runtime/node/`.
- **HyperFrames + GSAP:** versión estable actual de npm; dentro de `runtime/hyperframes/<versión>/`. Prepara Chrome con el comando oficial. Su caché puede quedar en la cuenta del usuario. Se fija la versión en cada nuevo lote, sin cambiar lotes existentes.
- **FFmpeg completo:** Windows usa winget y la distribución Gyan que enlaza FFmpeg; Mac usa Homebrew `ffmpeg-full`. El diálogo advierte que estas instalaciones pertenecen al equipo. Si falta winget/Homebrew, explica qué instalar y dónde; no los instala sin una autorización adicional del sistema/persona.
- **Audio:** uv y Python 3.12 compatible aislados; librerías con versiones que exige la calibración del framework. Comprueba si hay una versión nueva, pero no sustituye automáticamente las calibradas. Una actualización incompatible necesita recalibración. No se activa limpieza especializada de voz.
- **ASR:** faster-whisper con modelo small multilingüe descargado por separado, CPU int8 común a ambos sistemas. La transcripción necesita revisión; no se afirma equivalencia medida con el motor del Mac original.
- **Codex CLI opcional:** instalación local. La app existente también sirve. Para la CLI local abre `ABRIR CODEX.cmd` o `ABRIR CODEX.command`, que la inicia en `proyecto/`. Inicia sesión personalmente; no se incluyen sesiones, credenciales ni claves. La app se obtiene desde [la guía oficial](https://learn.chatgpt.com/docs/quickstart).

Las consultas de versiones solo solicitan metadatos públicos; el asistente no envía los masters ni los guiones. Si no hay conexión no afirma que una versión sea la última. El modo actual conserva versiones de audio calibradas por compatibilidad: «más nuevo» por sí solo no demuestra que todo siga funcionando.

## Las dos PC

| Equipo | Uso inicial | Ajuste |
| --- | --- | --- |
| A · i7 9.ª, 8 GB, GTX 1660 Ti 6 GB | Montaje y render principal | Un trabajo pesado; modo de memoria reducida; RAM 16 GB si es ampliable. NVENC no se activa sin prueba. |
| B · i7-8550U, 16 GB, UHD 620 | Preparación, revisión, transcripción u otro lote | Un trabajo pesado; no se supone la potencia gráfica de la GTX. |
| Mac | Edición independiente en esta entrega | Un render inicial; diagnóstico real del equipo. |

Ambas PC pueden avanzar con **lotes distintos**. No suman automáticamente CPU/GPU para renderizar un mismo video. Estas asignaciones son recomendaciones; no son benchmarks.

## Archivos y nombres

`proyecto/Lotes/<fecha-nombre>/` conserva CONTEXTO.json, MASTERS.json, GUION.md, ABRIR_EN_CODEX.txt y `00-INGESTA/` compartida. `proyecto/Nuevos-Videos/VIDEO-31/` y siguientes contienen la selección provisional, paleta, tablero, QA de fidelidad, editable y entregas.

Usa nombres como `MASTER-01-tema.mp4` y `GUION-01.md`. Un archivo ya referenciado debe conservar ruta/nombre. Al cambiar de computadora hay que llevar los masters de los trabajos activos y actualizar sus rutas. No necesitas llevar los anteriores. `runtime/` y `runtime.local.json` contienen instalaciones específicas de ese equipo: vuelve a configurar al cambiar de sistema; no copies cachés o entornos de Mac como si fueran Windows.

## Límites comprobados

El asistente prepara el entorno y el contexto. No decide por sí solo qué fragmentos del master usar ni crea un montaje aprobado: esa etapa la realiza Codex contigo. Se mantienen las revisiones de voz/contexto, rostro/gestos, captions, hook/SFX, mezcla, fidelidad, salida exacta y aprobación. No garantiza viralidad.

Consulta `evidencia/validacion-asistente.json` para distinguir pruebas realizadas y pendientes. La primera ejecución real en cada PC sigue siendo necesaria. No se instalaron programas globales ni se cambió el framework del Mac de origen para construir esta entrega.
