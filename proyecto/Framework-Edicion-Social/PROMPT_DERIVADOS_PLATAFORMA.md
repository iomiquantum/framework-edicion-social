# Prompt para crear derivados después de aprobar el máster

Usar este prompt únicamente cuando el usuario haya aprobado explícitamente el video principal.

```text
Prepara la entrega social desde el máster aprobado de VIDEO-NN, sin reeditar el contenido desde cero ni generar variantes redundantes.

Lee completamente:

- Framework-Edicion-Social/README.md
- Framework-Edicion-Social/MATRIZ_PRODUCCION_PRO.md
- Framework-Edicion-Social/platforms/README.md
- Framework-Edicion-Social/QA_PROFESIONAL.md
- Framework-Edicion-Social/MOTOR_APRENDIZAJE.md
- Framework-Edicion-Social/OPERACION_OPTIMIZACION.md
- Framework-Edicion-Social/platforms/catalog.json
- VIDEO-NN/platform-master.json

Primero valida el recibo de aprobación del mezzanine editorial exacto. Si es HDR, confirma que el máster social SDR es un archivo distinto, cumple `MASTER-PROFILE-SOCIAL-SDR-001`, conserva linaje al hash aprobado y superó revisión visual de color. Una fuente HLG/PQ no puede renderizarse como SDR solo con una bandera o cambio de etiquetas: crea primero un intermedio BT.709 mediante una transformación de color gestionada, verifica su metadata y compara fotogramas equivalentes de piel, blancos, ropa y fondo. Después valida que platform-master.json tenga aprobación explícita y crea `content-lock-evidence.json` con inventario real de proyecto, cut-plan, mezcla y activos. Ejecuta `build_publish_package.py` primero en dry-run; debe volver a comprobar ambos recibos, reporte SDR, catálogo y content lock. Si queda bloqueado, no renderices ni modifiques el máster. Un paquete materializado debe conservar los sellos finales de package, adaptación y briefs.

Genera primero únicamente el máster de Instagram Reels. Evalúa ese mismo MP4 en TikTok y YouTube Shorts. Si encuadre, safe zones, subtítulos, CTA, duración y especificaciones son compatibles, reutiliza exactamente ese archivo y adapta fuera del video título, copy, hashtags, portada y metadata. No hagas copias ni renders adicionales solo para cambiar el nombre.

Una variante adicional requiere documentar antes una diferencia material: duración o aspecto distintos, reencuadre/safe zone incompatible, CTA exclusivo dentro del video, restricción técnica o experimento creativo aprobado. Para cada variante justificada, conserva toma, cortes, voz, significado y activos aprobados; cambia únicamente el delta necesario mediante el mismo proyecto HyperFrames.

Antes del render final genera una preview por perfil y una hoja de contacto independiente con al menos 12 momentos distribuidos entre hook, desarrollo, B-roll, transiciones, talking head y CTA. Revisa que captions persistentes estén debajo del mentón o en espacio negativo y que ninguna tarjeta cubra cabello, cabeza, ojos o boca. No transfieras la revisión de una variante a otra.

Renderiza un archivo independiente por perfil siguiendo el paquete. Ejecuta check_platform_delivery.py y después realiza una preview real de la superficie/dispositivo. La revisión visual debe referenciar el SHA-256 exacto del render. Si cambia el archivo, repite la revisión. Si el usuario rechaza una versión, archívala sin borrarla, invalida expresamente su manifiesto y genera una revisión nueva; no la vuelvas a presentar como vigente. El paquete solo prepara derivados: `human_publication_approval` permanece pendiente y no se publica automáticamente.

Entrega el máster universal, su check técnico y una revisión por superficie ligada al mismo hash. Entrega otro MP4 solamente si existe una diferencia material, acompañada por su justificación, check, hash y resumen del delta. No publiques.
```

Comando de paquete, después de completar los artefactos reales:

```bash
python3 Framework-Edicion-Social/scripts/build_publish_package.py \
  --master-manifest VIDEO-NN/platform-master.json \
  --master-media VIDEO-NN/social-master.mp4 \
  --approval-receipt VIDEO-NN/social-master-approval.json \
  --source-approval-receipt VIDEO-NN/editorial-master-approval.json \
  --master-profile-report VIDEO-NN/social-master-profile-report.json \
  --content-lock-evidence VIDEO-NN/content-lock-evidence.json \
  --out-dir VIDEO-NN/publish
```

Sin `--write` solo valida y muestra el plan. Después de revisar la salida, repetir con `--write`. No usar `--force` salvo que se haya confirmado qué paquete previo válido se reemplazará; el comando rechaza carpetas arbitrarias, symlinks y destinos que solapen los insumos.

Comando de planificación de bajo nivel:

```bash
python3 Framework-Edicion-Social/scripts/plan_platform_derivatives.py \
  --master VIDEO-NN/platform-master.json \
  --out VIDEO-NN/platform-adaptation.json \
  --output-dir VIDEO-NN/deliveries
```

Sin `--target` se preparan Reels, TikTok y Shorts. La salida lista variables de layout para HyperFrames y permanece en `blocked` hasta que el máster cumpla los gates.


## Subtítulos por contexto — 2026-09-30

Aplicar `SUBTITULOS_CONTEXTO_Y_LECTURA.md` y `captions/catalog.json`. Registrar estilo y ubicación por separado en `VIDEO-NN/caption-decision.json` usando la plantilla del framework; preservar voz y sincronía. Revisar dos líneas reales, tamaño móvil, lectura sin audio, rostro/gestos y caja completa frente a UI de cada destino. No imponer palabras sueltas, coordenadas o CPS universales. Mantener preview pendiente cuando no exista evidencia real; no certificar plataforma por un check local ni reanalizar el maestro.
