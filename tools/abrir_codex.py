"""Launch only the already installed local Codex CLI, without implicit installation."""
import json, subprocess, sys
from pathlib import Path
import runtime_setup as rt

def main():
    package=rt.ROOT/'runtime/codex/node_modules/@openai/codex'
    metadata=package/'package.json'
    if not metadata.is_file():raise SystemExit('Usa tu app Codex o prepara Codex CLI con el asistente. No está instalado en esta entrega.')
    entry=json.loads(metadata.read_text(encoding='utf-8'))['bin'];entry=entry['codex'] if isinstance(entry,dict) else entry
    file=(package/entry).resolve()
    if not file.is_relative_to(package.resolve()) or not file.is_file():raise SystemExit('Instalación de Codex inválida.')
    node=rt.binary('node')
    if not node:raise SystemExit('Falta Node. Vuelve al asistente.')
    print('Codex se abrirá en proyecto/. Inicia sesión si lo solicita y pega ABRIR_EN_CODEX.txt del lote.')
    raise SystemExit(subprocess.call([node,str(file),'--cd',str(rt.ROOT/'proyecto')],env=rt.environment()))
if __name__=='__main__':main()
