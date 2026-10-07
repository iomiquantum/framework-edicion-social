# Fuentes consultadas para el asistente · 2026-10-06

- [Codex CLI](https://learn.chatgpt.com/docs/codex/cli), [comandos](https://learn.chatgpt.com/docs/developer-commands) y [proyectos](https://learn.chatgpt.com/docs/projects): instalación, acceso y directorio de trabajo. La entrega prepara una instrucción para un chat nuevo; no envía mensajes ni inicia sesión automáticamente.
- [HyperFrames CLI](https://hyperframes.app/docs/5-packages/cli): doctor, browser ensure, check, render y transcripción. El doctor se decide por su payload, no solo por código de salida. La prueba de producción se ejecuta en el equipo de destino.
- [Node releases](https://nodejs.org/dist/index.json): consulta de última estable y LTS; instalador aislado con SHASUMS256.txt de la misma versión.
- [Python](https://www.python.org/downloads/) y [Python en Windows](https://docs.python.org/3/using/windows.html): disponibilidad y mecanismos de instalación. El arranque mínimo no depende de Node ni de un entorno virtual previo.
- [uv: instalación de Python](https://docs.astral.sh/uv/guides/install-python/) y [opciones del instalador](https://docs.astral.sh/uv/reference/installer/): runtime dentro de la entrega, sin cambiar el PATH global. Sus builds de Python son de Astral python-build-standalone.
- [FFmpeg](https://www.ffmpeg.org/download.html), [Gyan](https://www.gyan.dev/ffmpeg/builds/), [Homebrew ffmpeg-full](https://formulae.brew.sh/formula/ffmpeg-full) y [winget install](https://learn.microsoft.com/en-us/windows/package-manager/winget/install): distribución y filtros; la presencia del ejecutable no demuestra que incluya zscale/tonemap/loudnorm.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/transcribe.py): carga local con `local_files_only` para evitar descargas implícitas al editar. El modelo se instala en un paso autorizado aparte.
- [PyPI ai-edge-litert 2.2.0](https://pypi.org/pypi/ai-edge-litert/2.2.0/json): disponibilidad de wheels Windows x64/Mac arm64 para Python 3.12. Disponibilidad no equivale a ejecución ni calibración en el equipo.

La consulta real del asistente está registrada en `versiones-consultadas-asistente.json`. Las versiones futuras se vuelven a consultar: no se presenta este recibo como garantía permanente. Audio conserva versiones calibradas de la copia. La última versión publicada de ai-edge-litert observada es distinta de la versión calibrada; no se cambia por ese hecho.

Límites: se probó un smoke con HyperFrames 0.8.102 instalado previamente, no se ejecutó aquí 0.8.138 ni los instaladores de destino. No se usaron sitios de terceros como autoridad para instrucciones de Codex.
