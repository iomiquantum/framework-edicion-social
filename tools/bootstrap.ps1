param([switch]$OpenCodex, [string[]]$EditArgs)
$ErrorActionPreference = 'Stop'
$KitRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONUTF8='1'; $env:PYTHONDONTWRITEBYTECODE='1'
$env:UV_UNMANAGED_INSTALL=Join-Path $KitRoot 'runtime/uv'
$env:UV_PYTHON_INSTALL_DIR=Join-Path $KitRoot 'runtime/python'
$env:UV_CACHE_DIR=Join-Path $KitRoot 'runtime/uv-cache'
try {
$ProgressFolder=Join-Path $KitRoot 'MI-PROGRESO'
New-Item -ItemType Directory -Path $ProgressFolder -Force | Out-Null
Start-Transcript -Path (Join-Path $ProgressFolder 'inicio-windows.log') -Append | Out-Null
$PythonPath=$null
$Candidates=@()
foreach ($Name in @('python','python3')) {
  $Found=Get-Command $Name -ErrorAction SilentlyContinue
  if ($Found -and $Found.Source -notlike '*WindowsApps*') { $Candidates += $Found.Source }
}
$Candidates += @(Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA 'Programs/Python/Python*/python.exe') -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -ExpandProperty FullName)
foreach ($Candidate in $Candidates) {
  & $Candidate -c 'import sys; sys.exit(sys.version_info < (3,11))' 2>$null
  if ($LASTEXITCODE -eq 0) { $PythonPath=$Candidate; break }
}
$Uv=Join-Path $env:UV_UNMANAGED_INSTALL 'uv.exe'
if (-not $PythonPath -and (Test-Path -LiteralPath $Uv)) {
  $FoundPython= & $Uv python find --managed-python --no-python-downloads 3 2>$null
  if ($LASTEXITCODE -eq 0) { $PythonPath=($FoundPython | Out-String).Trim() }
}
if (-not $PythonPath) {
  if (-not $OpenCodex -and -not $EditArgs) { try { Start-Process (Join-Path $KitRoot 'INICIO.html') } catch {} }
  Write-Host 'INICIO Y CONFIGURACION DE FRAMEWORK'
  Write-Host 'Falta Python 3.11 o superior. Se propone instalar uv y Python estable dentro de esta carpeta.'
  Write-Host 'Fuentes: https://astral.sh/uv/install.ps1 y Astral python-build-standalone. No se cambia el PATH global.'
  $Answer=Read-Host 'Autorizas descargar e instalar estos recursos? Escribe SI'
  if ($Answer -ne 'SI') { Write-Host 'Cancelado. Puedes instalar Python desde python.org/downloads y volver a abrir este archivo.'; exit 0 }
  $Downloads=Join-Path $KitRoot 'runtime/downloads'
  New-Item -ItemType Directory -Path $Downloads -Force | Out-Null
  $Installer=Join-Path $Downloads 'uv-install.ps1'
  Invoke-WebRequest -UseBasicParsing -Uri 'https://astral.sh/uv/install.ps1' -OutFile $Installer
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Installer
  if ($LASTEXITCODE -ne 0) { throw 'No se pudo instalar uv.' }
  & $Uv python install 3
  if ($LASTEXITCODE -ne 0) { throw 'No se pudo instalar Python. Revisa la conexion.' }
  $PythonPath=(& $Uv python find --managed-python --no-python-downloads 3 | Out-String).Trim()
}
Set-Location -LiteralPath $KitRoot
if ($EditArgs) { & $PythonPath (Join-Path $PSScriptRoot 'asistente.py') --edit @EditArgs }
elseif ($OpenCodex) { & $PythonPath (Join-Path $PSScriptRoot 'asistente.py') --codex }
else { & $PythonPath (Join-Path $PSScriptRoot 'asistente.py') }
if ($LASTEXITCODE -ne 0) { throw 'El asistente termino con error. Lee el mensaje anterior.' }

} catch {
  Write-Host ('No se pudo terminar el inicio: ' + $_.Exception.Message)
  Write-Host 'Abre INICIO.html. Conserva MI-PROGRESO para retomar y pedir ayuda.'
  try { $_.Exception.Message | Out-File -FilePath (Join-Path $KitRoot 'MI-PROGRESO/error-inicio.txt') -Encoding utf8 } catch {}
  try { Start-Process (Join-Path $KitRoot 'INICIO.html') } catch {}
  exit 1
} finally { try { Stop-Transcript | Out-Null } catch {} }
