#!/bin/bash
set -euo pipefail
framework_root="$(cd -- "$(dirname -- "$0")" && pwd)"
if [ "$#" -eq 0 ]; then exec /bin/bash "$framework_root/INICIO Y CONFIGURACION DE FRAMEWORK.command"; fi
exec /bin/bash "$framework_root/INICIO Y CONFIGURACION DE FRAMEWORK.command" --edit "$@"
