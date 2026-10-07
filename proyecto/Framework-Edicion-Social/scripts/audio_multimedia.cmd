@echo off
setlocal
set "PYTHONUTF8=1"
"%~dp0..\..\..\runtime\audio\Scripts\python.exe" "%~dp0..\..\..\tools\audio.py" %*
endlocal
