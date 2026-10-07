# Piloto real de publicación mediante Metricool MCP — v1

Fecha de registro: **1 de octubre de 2026**. Verificación final de horas: **recibo v2**; el recibo de programación v1 se conserva como historia. Marca: **Silent Run Ecuador**, ID `6177067`. Fecha objetivo: **2 de octubre de 2026**, zona `America/Guayaquil`.

## Autorización y estado comprobado

La petición inicial combinaba borradores y programación para mañana. El usuario aclaró **«Programadas para publicarse realmente mañana»**. Se prepararon borradores y después se activaron para publicación real. La autorización está conservada en el [recibo de programación](RECIBO_PROGRAMACION_v1.json).

La lectura MCP posterior confirma **11 casos y 17 destinos**: `draft=false`, `autoPublish=true` global y `instagramData.autoPublish=true` para todos los destinos Instagram seleccionados. Los 17 proveedores siguen **PENDING**. **No hay publicación real verificada todavía**, ni enlaces o horas reales de publicación. La desaparición futura de la cola no bastará como prueba de éxito.

El plan leído fue **Free**, una marca y 20 publicaciones mensuales, con 0 publicadas al iniciar. Si estos 17 destinos se publican y no hay otros posts, quedarían 3 publicaciones del cupo. Esto es una previsión; no certifica consumo futuro ni cobro. El borrador de control `3758769130611950882` permanece fuera de los 11 casos / 17 destinos.

## Casos y diferencia de horarios

| Caso | Formato / destinos | MCP / Calendario / Listado | Editor individual | Planner |
|---|---|---|---|---|
| P01 | Imagen cuadrada · IG + FB (2) | 09:00 | 16:00 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=572359031725834830) |
| P02 | Imagen vertical · IG + FB (2) | 09:10 | 16:10 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=2243109020537736501) |
| P03 | Carrusel / varias fotos · IG + FB (2) | 09:20 | 16:20 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=5060693824076268020) |
| P04 | Historia con imagen · IG + FB (2) | 09:30 | 16:30 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=6018955738659899342) |
| P05 | Historia con video · IG + FB (2) | 09:40 | 16:40 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=5229785277899230436) |
| P06 | Reel en feed · IG + Reel FB (2) | 09:50 | 16:50 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=1918079464526728961) |
| P07 | Video como post · Facebook (1) | 10:00 | 17:00 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=-2373599650573762156) |
| P08 | Imagen única · TikTok (1) | 10:10 | 17:10 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=4281328617706638093) |
| P09 | Carrusel de fotos · TikTok (1) | 10:20 | 17:20 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=-1208518555454452734) |
| P10 | Video · TikTok (1) | 10:30 | 17:30 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=1836079371515742936) |
| P11 | Short · YouTube (1) | 10:40 | 17:40 | [Abrir](https://app.metricool.com/planner/calendar?blogId=6177067&openWithPostUuid=3782030177655343356) |

Todos los casos tienen fecha 02/10/2026. La [verificación final v2](RECIBO_VERIFICACION_HORA_v2.json) confirma que **MCP, Calendario y Listado web coinciden en 09:00–10:40 America/Guayaquil**, con 11 casos / 17 destinos pendientes. El [DOM del Listado](evidencias/listado-final-dom.txt) y la [captura completa](evidencias/listado-programado-02-oct.jpg) muestran las 11 pruebas `Pendiente`; el borrador de control aparece aparte y no se suma al piloto.

**Solo el editor individual muestra 16:00–17:40**, también con selector `America/Guayaquil`: anomalía de visualización +7 horas cuya causa sigue **por confirmar**. No se atribuye a la cola completa ni se afirma que se haya corregido. La publicación real y su instante todavía no están comprobados. El recibo v1 conserva la observación anterior; v2 añade la comprobación de Calendario/Listado. El [CSV final v2](CASOS_PROGRAMADOS_v2.csv) separa los cuatro canales de hora y conserva los enlaces; el [CSV inicial v1](CASOS_PROGRAMADOS_v1.csv) queda como historia. Los UUID son identificadores de texto; evitar que una hoja de cálculo redondee sus dígitos.

## Archivos, evidencias y QA

- Seis tarjetas originales: una cuadrada 1080×1080, una vertical 1080×1350, carrusel de tres láminas 1080×1350 en orden 1/3–3/3 y una historia 1080×1920. Cada tarjeta tiene SVG, PNG y JPEG calidad 95: **18 archivos**, más [contacto visual](assets/contacto_tarjetas_prueba.png) y [manifest original](assets/manifest_tarjetas_prueba.json). El manifest copiado conserva las rutas de procedencia externas; el [inventario final local con hashes](INVENTARIO_CIERRE_v2.json) mapea todos los archivos copiados al proyecto. Los borradores gráficos anteriores no se copiaron a esta carpeta.
- Se reutilizó [VIDEO-18 v1 aprobado](</Users/iomijhondavid/Documents/Codex/Edicion de Videos/Serie-IA-Negocios-10-Videos/VIDEO-18/VIDEO-18-PARA-APROBACION-v1.mp4>): 1080×1920, 21,866667 s, H.264 High / yuv420p / SDR BT.709 y AAC estéreo 48 kHz según recibo. SHA-256 verificado antes y después: `7978d638f464ebccd8d68b1cd54e2c939cbc3a9e0acb5a800fd0307f6f2cb960`. Master, editable, voz, audio y artes estáticos aprobados no se escribieron ni se reemplazaron. No se hizo una escucha humana nueva.
- Se copiaron **18 evidencias** de las fases de borrador y programación. [Verificación UI](evidencias/verificacion-ui.json), [Reel programado](evidencias/P06-reel-programado.jpg), [historia de imagen](evidencias/P04-programado.jpg), [historia de video](evidencias/P05-programado.jpg), [carrusel](evidencias/P03-programado.jpg), [TikTok fotos](evidencias/P09-programado.jpg) y [Short](evidencias/P11-programado.jpg). Las capturas de borrador prueban la fase inicial; la activación final se acredita con el recibo MCP y capturas posteriores.
- QA del cierre: JSON/CSV legibles, 11 filas / 17 destinos, estados y enlaces iguales al recibo, rutas locales existentes, hashes de copia iguales a sus fuentes, PNG/JPEG RGB y dimensiones correctas, XML SVG válido. El recibo registra coincidencia de copies, cantidad y orden de medios y ausencia de errores de creación/activación. En P06, DOM del video: `readyState=4`, 1080×1920 y 21,866667 s; una preview cargada no acredita publicación ni reproducción audiovisual nueva.

## Restricciones observadas y aprendizajes

La [captura P04](evidencias/P04-programado.jpg) muestra avisos de Facebook e Instagram: **«Se ignorará el texto de la publicación»** al auto publicar historias. El mensaje visible de P04 está integrado en la imagen; el copy de P05 sirve como registro y no se convierte automáticamente en texto de la historia. Una encuesta o sticker dibujado tampoco crea interacción real.

Facebook varias fotos no equivale a un carrusel publicitario. El video individual de Instagram usa Reel; `showReelOnFeed=true` lo solicita también en feed. TikTok Stories no forman parte de los formatos admitidos por esta integración, según el recibo. Este piloto cubre los formatos disponibles en las cuentas conectadas, no todas las modalidades posibles de cada red.

La publicación debe comprobarse por destino, con estado real, enlace/ID de red e instante; aceptar una programación sin error solo demuestra que se creó la cola. Las previews son aproximaciones. La lectura final de Calendario/Listado coincide con MCP; la anomalía se limita al editor individual y no demuestra un desplazamiento del instante real de publicación.

## Seguimiento y pendientes

[Seguimiento verificado ACTIVE](RECIBO_SEGUIMIENTO_v1.json): **una revisión el 2 de octubre de 2026 a las 18:15, hora de Guayaquil**, ID `comprobar-piloto-metricool-de-todos-los-formatos`. Su propósito es comprobar resultados y horarios, **sin volver a publicar ni reprogramar**. El seguimiento existente se actualizó para leer el recibo v2 y reconocer la anomalía limitada al editor; continúa **ACTIVE**, con la misma única revisión, sin crear un segundo monitor. Su ejecución real sigue **por confirmar**. La revisión local requiere Mac encendido, app Codex abierta y proyecto accesible; la publicación programada en Metricool la ejecuta el servicio y no depende de que este Mac esté activo.

Pendientes: confirmar publicación y enlace/ID por cada uno de los 17 destinos, contrastar instante real frente a MCP/Calendario/Listado y explicar el desplazamiento de siete horas del editor individual, comprobar resultado final/orden/copy/audio y consumo real de cupo. No se declara éxito publicado ni rendimiento medido antes de esas evidencias.
