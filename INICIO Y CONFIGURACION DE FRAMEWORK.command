#!/bin/bash
set -euo pipefail
framework_root="$(cd -- "$(dirname -- "$0")" && pwd)"
framework_start_error() {
  framework_code=$?
  printf '\nNo se pudo terminar el inicio. Abre INICIO.html para ver cómo continuar.\n'
  /usr/bin/open "$framework_root/INICIO.html" || true
  if [ -t 0 ]; then read -r -p 'Pulsa Enter para cerrar: ' framework_reply; fi
  exit "$framework_code"
}
trap framework_start_error ERR
if [ "$#" -eq 0 ]; then
  mkdir -p "$framework_root/MI-PROGRESO"
  exec > >(/usr/bin/tee -a "$framework_root/MI-PROGRESO/inicio-mac.log") 2>&1
fi
export PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
export UV_UNMANAGED_INSTALL="$framework_root/runtime/uv"
export UV_PYTHON_INSTALL_DIR="$framework_root/runtime/python"
export UV_CACHE_DIR="$framework_root/runtime/uv-cache"
framework_python=""
for candidate in /opt/homebrew/bin/python3 /usr/local/bin/python3 "$(command -v python3 || true)"; do
  if [ -n "$candidate" ] && [ -x "$candidate" ] && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3,11))' 2>/dev/null; then
    framework_python="$candidate"; break
  fi
done
if [ -z "$framework_python" ] && [ -x "$UV_UNMANAGED_INSTALL/uv" ]; then
  framework_python="$("$UV_UNMANAGED_INSTALL/uv" python find --managed-python --no-python-downloads 3 2>/dev/null || true)"
fi
if [ -z "$framework_python" ]; then
  if [ "$#" -eq 0 ]; then /usr/bin/open "$framework_root/INICIO.html" || true; fi
  printf '\nINICIO Y CONFIGURACION DE FRAMEWORK\nFalta Python 3.11 o superior para abrir el asistente.\n'
  printf 'Se propone descargar uv desde https://astral.sh/uv/install.sh y Python estable de Astral python-build-standalone.\nTodo se guardará dentro de esta carpeta, sin modificar el PATH del sistema.\n'
  read -r -p '¿Autorizas descargar e instalar estos recursos? Escribe SI: ' framework_answer
  if [ "$framework_answer" != 'SI' ]; then printf 'Cancelado. También puedes instalar Python desde https://www.python.org/downloads/ y volver a abrir este archivo.\n'; exit 0; fi
  mkdir -p "$framework_root/runtime/downloads"
  /usr/bin/curl -fL --proto '=https' --tlsv1.2 https://astral.sh/uv/install.sh -o "$framework_root/runtime/downloads/uv-install.sh"
  /bin/sh "$framework_root/runtime/downloads/uv-install.sh"
  "$UV_UNMANAGED_INSTALL/uv" python install 3
  framework_python="$("$UV_UNMANAGED_INSTALL/uv" python find --managed-python --no-python-downloads 3)"
fi
cd "$framework_root"
"$framework_python" "$framework_root/tools/asistente.py" "$@"
