# Mejora continua del flujo — lote 21–25

Fecha: 2026-09-30 · America/Guayaquil
Estado: procedimiento aplicado a la preparación; mejoras de render por verificar en VIDEO-21.

## Evidencia y prioridades

| Hallazgo verificable | Acción | Cómo comprobar la mejora |
| --- | --- | --- |
| VIDEO-13: render 1.233,02 s; captura HDR por capas 1.204,4 s, aproximadamente 97,7 % del render. | Antes de un render completo, inspeccionar segmentos de las transiciones críticas usando el mismo pipeline HDR de entrega. Medir una muestra corta antes de elegir configuración. | Registrar tiempo, fps efectivos y resultado visual; comparar configuraciones sobre el mismo segmento. No extrapolar como tiempo final garantizado. |
| VIDEO-15: renders de revisión de 380,68 s y 162,39 s rechazados; fallos de retorno al presentador y rótulo persistente. | Verificar salida de B-roll, fondo, rótulos y captions a ambos lados de cada límite; t−2 y t+2 fotogramas, además del estado exacto. | Guardar imágenes del MP4 de prueba; confirmar que no quedan capas anteriores. El preview SDR no valida el comportamiento HDR. |
| VIDEO-13: seis corridas Whisper y gate de lote aún sin cerrar durante la edición histórica. | Una ingesta compartida 21–25 con transcripción completa y take-map; análisis dirigido solo si quedan dudas locales. | Gate `validar_lote_listo.py --desde 21 --hasta 25 --write-lock`; contador separado de transcripción completa y consultas locales. |
| VIDEO-13: 86.788.277 B de PNG en una carpeta de 120.555.649 B. | Hoja de contacto compacta para primera inspección; capturas a resolución completa solo para texto, rostro y defectos. Conservar toda la evidencia histórica. | Medir bytes nuevos de QA y número de capturas; no reducir muestreo de escenas breves ni transiciones críticas. |
| QA post-render abre seis procesos para seis capturas, más decodificación y loudness separados. | Candidato de mejora: probar extracción agrupada o captura durante decodificación sobre un archivo existente, sin modificar aún el script estable. | Comparar timestamps reales, seis imágenes, integridad y tiempo contra el script actual. Adoptar únicamente tras equivalencia; ahorro por confirmar. |

Fuentes: `Serie-IA-Negocios-10-Videos/VIDEO-13/METRICAS_PRODUCCION.md`, `VIDEO-15/METRICAS_PRODUCCION.md`, `00-INGESTA/METRICAS_INGESTA_11_15.md` y `scripts/qa_post_render.py`.

## Ejecución del lote

1. Leer reglas y preferencias una vez al inicio; guardar referencias y decisiones comunes. Después leer solo documentos cambiados y requisitos específicos del video. Una lectura truncada no demuestra lectura completa.
2. Cerrar ingesta antes de declararla aprobada; la excepción provisional de AGENTS vigente2026-09-30 permite avanzar con montaje/preview y recibo distinto sin escucha, resolviendo antes cada tramo ambiguo. No declarar selección por escucha ni revisión humana sin evidencia. Pista 1 AAC decodificable; pista 2 sin decodificador local: comparación A/B por confirmar.
3. Reutilizar biblioteca y módulos por pertinencia semántica, conservando variedad. No clonar la composición del 21 en los siguientes.
4. Cerrar cortes de voz antes de sincronizar captions; revisar empalmes y pausas superiores a 1,25 s.
5. Revisar montaje y composición con proxy; validar color y transiciones críticas en el pipeline de entrega desde el original.
6. Ejecutar check completo tras cambios estructurales; correcciones locales se verifican primero en su rango y dependencias. Antes de entrega repetir el gate completo del candidato exacto.
7. Un render revisable completo tras resolver fallos locales; completar las tres pasadas visual, audio/ritmo e integral, con evidencia honesta.
8. Mantener máximo dos procesos pesados simultáneos; no atribuir mejora a paralelismo sin distinguir pared y CPU.

## Registro por video y cierre de ciclo

Medir tiempo por fase: preparación, ingesta compartida, montaje, medios, check, render, QA y documentación. Separar espera externa, trabajo del agente y procesos superpuestos. Registrar renders completos y parciales, reintentos y causa del retrabajo, recursos nuevos/reutilizados y bytes de evidencia. Tokens, costo y consumo eléctrico quedan `no disponible` si no hay contador verificable.

Tras cada video registrar: defecto encontrado, causa, corrección, evidencia y prevención reutilizable. Cambiar reglas operativas solo dentro del alcance autorizado; no promover automáticamente gustos, plantillas ni supuestos de rendimiento. Al terminar 21–25 comparar datos medidos y conservar prácticas que reduzcan tiempo sin perder QA.

## Estado inicial

El original 21–25 dura 495,0117 s; HEVC HLG BT.2020, vertical 1080×1920, aproximadamente 30 fps, AAC 48 kHz. Preflight de grabación: 14 pass, 0 fail. Preflight de proyecto en ingesta: pass_with_warnings por selección auditiva pendiente. Fuente registrada por SHA-256; original intacto. Transcripción, take-map revisado, proxies, recibo de ingesta, edición y QA del 21 todavía pendientes. Ningún ahorro del lote se declara medido todavía.

## Actualización del procedimiento — 2026-09-30

Usar `MEJORA_CONTINUA.md` y `scripts/medir_proceso.py` para comandos nuevos medibles. La excepción de AGENTS vigente gobierna el avance provisional; los pendientes/estado inicial de arriba son históricos y no sustituyen el estado actual del tablero ni autorizan aprobación ficticia.

## Resultado observado en VIDEO-21 — 2026-09-30

Ingesta provisional compartida completa: transcripción reparada por50 ventanas de voz,5 tomas/17 marcadores y6 correcciones trazables; mapas/proxies21–25 reutilizables, sin escucha humana ni recibo estricto ficticio. Guiones como referencias; marcadores y voz real tienen prioridad.

El render corregido30fps/quality looks tardó139,808 s; el proceso también tuvo153,668 s fallidos por dependencia,146,738 s de draft rechazado y33,292 s de piloto6fps. No confundir último render con costo total ni declarar ahorro porcentual. Cinco proxies:26,175 s/65,2 MB. QA post-render3,439 s; extracción72frames en un decode2,041 s. Es un ensayo local; no reemplaza el script QA estable ni demuestra equivalencia/rendimiento global.

Prevenciones aplicables: probar ffmpeg y ffprobe antes de trabajo pesado; usar runtime aislado reproducible y coordinar cambios globales de dependencias. Cada subcomposición debe limitar selectores a su raíz y definir salida de hijos. Proteger encabezado/rostro mediante límites físicos de medios, además de z-order. Probar persistencia de capas en el pipeline HLG real antes del render completo; un piloto6fps sirve para persistencias, no para QA de cortes30fps. Tras exportar inspeccionar ±2 frames de cada transición/caption más estados de lectura. Preview/check no sustituyen MP4 real.

Denoise conservador con original+A/B, latencia medida/compensada y métricas de mezcla; naturalidad queda por confirmar si no se ha escuchado. Candidato21 documentado en `VIDEO-21/QA_REVISION.md` y `METRICAS_PRODUCCION.*`;22–25 preparados, no editados.

## Cierre VIDEO21 por delegación — 2026-09-30

Delivery148,407s frente al candidato139,808s; configuración/calidad diferentes, no es comparación controlada de rendimiento. QA del delivery5,229s;94frames agrupados3,535s. Capturas agrupadas añaden±1 para verificar los frames inmediatamente adyacentes exigidos por QA, además de±2. La autorización del usuario para decidir render se registra sin convertirla en prueba de escucha; no se repiten ASR/ingesta ni cambios estéticos sin un defecto.


## Aplicación VIDEO22 — 2026-09-30

Reutilizó rangos/transcripción/proxy, sin recorrer ni transcribir otra vez el original. MantieneT22 distinto deT21: orientación por cinco etapas y aviso del siguienteestado; T23seráPausa sensorial según registro, todavía no editado.

Se corrigieron dos errores de duracionesFFmpeg (`0.008`, `0.12` requieren cero inicial), raíces sin dimensiones, SFXde0,84s declarado1,2s, y acento demasiado alto frente a voz suave. Reanudaciones consultaron éxito previo yprobe de medios para conservarprocesamiento válido. No se contabilizan reintentos como inexistentes.

Captions del pilotoHLG quedaron congelados pese alcheck; corrección poropacity de contenido y salida explícita, validada ensegundo piloto. Leer prevención concurrente16 enMEJORA_CONTINUA antes de próximas ediciones; Studio/checknoacreditanHDR. Nuevohelper experimental deriva límites de la pieza actual y usa expresiónbalanceada: un muestreo grande con suma lineal deeq() falló, prueba de200PTS exactos pasó. Mantener capturaQA estable; agrupada es evidencia adicional. No promover ahorro por comparar distinto número deframes/pipelines.

Checksmedidos106,352s en5intentos (uno falló1,006s); pilotos93,141s en2intentos. Preparaciónmedios9,539s sumados en49eventos (incluye consultas/reuso y2errores), sin imputar coste de ingesta compartida como cero. Edición/agente/documentación no quedan incluidas en esos comandos. Render completo aún en curso al registrar esta entrada.


## Cierre técnico VIDEO22 y prevención siguiente

Una captura completa30fps189,630s; render de revisión actualv2 usa esa misma imagen, probada por identidad del stream codificado. Corrección de rotación/ganancias de audio en1,664s (más intento fallido0,639s), nuevo QA de3,562s. La imagen no se recapturó porque se demostró que solo cambiaron tags/scheduleaudio y atributos del editor; no aplicar este atajo si cambia una fuente visual, timing, CSS, motion, color o geometría.

Antes del montaje siguiente comprobar licencia/elegibilidad/cooldown y mantener ledger desde el generador. Parsear loudnorm con JSONDecoder.raw_decode para admitir progreso posterior; usar módulos disponibles/stdlib en vez de asumirNumPy. Las variables de binariosCLI0.8.98 son HYPERFRAMES_FFMPEG_PATH y HYPERFRAMES_FFPROBE_PATH. Registrar diferencias sin tocar dependencias globales ni videos aprobados.

Mediciones por comando enVIDEO22/METRICAS_PRODUCCION.*. No incluyen tiempo total del agente y no permiten afirmar ahorro global frente a21. Candidato25,266667s,161frames inspeccionados,−16LUFS/−1,7dBTP; escucha humana y aprobación de entrega22 por confirmar. Ingesta se reutilizó íntegra;0 nuevas transcripciones del maestro.
