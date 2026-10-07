param(
  [ValidateSet('doctor','verify','list','nuevo','plan','preview','check','preflight','render')][string]$Accion='list',
  [ValidateRange(1,9999)][int]$Video=31,
  [ValidatePattern('^T(0[1-9]|[12][0-9]|30)$')][string]$Plantilla='T01',
  [ValidateSet('pc-a-gtx1660ti','pc-b-uhd620')][string]$Perfil,
  [switch]$AprobarRender
)
$ErrorActionPreference='Stop'
$Arguments=@($Accion,'--video',"$Video",'--template',$Plantilla)
if ($Perfil) { $Arguments += @('--profile',$Perfil) }
if ($AprobarRender) { $Arguments += '--approve-render' }
& (Join-Path $PSScriptRoot 'tools/bootstrap.ps1') -EditArgs $Arguments
exit $LASTEXITCODE
