"""Portable entry for the framework's existing assisted audio implementation."""
import subprocess, sys
from pathlib import Path
import runtime_setup as rt
py=rt.local_python()
if not py.is_file():raise SystemExit('Falta preparar audio en INICIO Y CONFIGURACION DE FRAMEWORK.')
script=rt.ROOT/'proyecto/Framework-Edicion-Social/scripts/audio_multimedia.py'
raise SystemExit(subprocess.call([str(py),str(script),*sys.argv[1:]],env=rt.environment()))
