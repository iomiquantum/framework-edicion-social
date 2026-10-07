# Informe del piloto de edición: lote 26–30

**Borrador. Falta cerrar QA exacto de VIDEO27 y VIDEO29v2. No constituye el informe final.**

## Qué se probó

Se editaron cinco piezas nuevas del mismo master con un reparto congelado antes del montaje: dos con flujo 1, dos con flujo 2 y una con flujo 3. Todos los trabajadores recibieron la selección explícita de GPT‑6.1 Sol con razonamiento Medio; el runtime del modelo no se verificó independientemente ni expuso aquí costos o tokens por video.

| Par | Flujo 1 | Flujo 2 | Criterio previo |
| --- | --- | --- | --- |
| A | VIDEO26, 28,267 s | VIDEO28, 24,700 s | Complejidad simple a moderada y recursos previos disponibles |
| B | VIDEO27, 22,033 s | VIDEO29, 23,967 s | Cuatro tramos y familias centradas en captions, ritmo y recapitulación |

VIDEO30, de 15,900 s, se asignó a flujo 3 por compatibilidad con T30: texto, voz/onda, símbolo contextual y recapitulación mediante módulos existentes. Su alcance esencial no equivale al diseño personalizado de flujo 1. La identidad de la plantilla siguió siendo obligatoria.

La ingesta compartida inicial ocupó **767,083 s (12 min 47,083 s)** y se cuenta una sola vez. Ya existían 52 archivos de preproducción: su costo histórico es desconocido y queda fuera de esta producción. Se midió y documentó la revisión/adaptación nueva, incluida una imagen contextual nueva para VIDEO26 con 25,957 s de generación.

## Tiempos observados por fase

Valores en segundos. Cada cifra es un intervalo registrado de reloj de pared. Las fases incluyen trabajo, coordinación y procesos según sus notas; no son tiempos puros de atención o CPU. Los motores medidos dentro de estos intervalos se muestran aparte y no se suman otra vez. Los intervalos todavía abiertos quedan excluidos.

| Video | Flujo | Semántica | Recursos | Montaje | QA previo | Fase render | QA posterior | Correcciones | Documentación | Coordinación |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 26 | 1 | 577.5 | 256.1 | 412.0 | 273.2 | 261.4 | 137.5 | No medido | No medido | No medido |
| 27 | 1 | 364.0 | 322.4 | 151.7 | 144.2 | 538.3 | No medido | No medido | No medido | No medido |
| 28 | 2 | 262.0 | 253.1 | 262.2 | 519.8 | 490.2 | 147.1 | No medido | 23.3 | No medido |
| 29 | 2 | 270.4 | 547.3 | 526.1 | 213.3 | 200.9 | 143.4 | 92.9 | No medido | No medido |
| 30 | 3 | 318.7 | 506.2 | 240.6 | 1002.2 | 353.2 | 259.4 | 43.2 | 202.2 | 30.7 |

La preparación semántica de VIDEO30 incluye una reparación compartida de alineación para 26/28/30. No existe un reloj exclusivo de esa reparación: no se atribuye íntegramente a flujo 3 ni se inventa una resta. Recursos de 30 incluyen maqueta y primera autoría; montaje incluye checks/correcciones. Recursos de 29 incluyen implementación y coordinación del cierre de 26. Estas mezclas limitan la comparación por fase.

La auditoría experimental se registra en su propia ejecución y se informa aparte. Los solapes entre agentes impiden sumar los cinco tiempos como duración total del lote. Los huecos y el tramo inicial anterior al reloj permanecen sin medir.

## Motor, controles técnicos y revisión completa

| Video / versión | Render de motor | Controles técnicos posteriores | Fase completa de QA posterior |
| --- | ---: | --- | --- |
| 26 v1 | 231,8 s | Helper 4,101 s; extracción de fronteras 4,026 s; paridad ligada a recibo | 137,461 s: incluye revisión visual, documentación y coordinación |
| 27 v1 | 129,8 s reportados por responsable | Pendiente cierre exacto | Pendiente |
| 28 v1 | 193,384 s | Paridad 2,175 s; recibos de export y 42 frames | 147,063 s de fase registrada |
| 29 v1 | 171,6 s | Helper 2,830 s; paridad 1,170 s; fronteras 2,121 s | 143,369 s de revisión y cierre |
| 29 v2 | Pendiente | Pendiente | Pendiente |
| 30 v1 | 125,453 s | Helper 2,467 s; paridad 0,897 s; frames 12,992 s | Documentada en reloj, incluye revisión/cierre |
| 30 v2 | 130,619 s | Helper 4,495 s; paridad 1,222 s; frames 10,990 s | 122,693 s de fase, además de documentación separada |

En VIDEO29 la corrección de transición v2 ocupó 92,9 s reportados por root; se verificó con controles dirigidos, sin duplicar el check integral del candidato por un retraso localizado del cuerpo gráfico. Las cifras finales deben verificarse contra el reloj y recibo v2.

## Calidad y correcciones del piloto

Se conservaron las familias originales: T26 lectura fácil; T27 captions protagonistas; T28 onda y círculos de audio guía; T29 comparación, recuerdo circular y recapitulación; T30 cuatro accesos semánticos. Los SVG de preproducción con paletas discordantes se preservaron y se adaptaron recursos nuevos para cada familia. Reutilizar un archivo intacto no garantiza que encaje con voz o diseño.

La sombra independiente detectó dos fallas de acabado después de la revisión local del candidato: fondo negro breve alrededor del presentador en VIDEO30v1, y gráficos cruzando el rostro durante la entrada de paneles en VIDEO29v1. Ambas exigieron nuevas versiones finales; no se dejó una advertencia como sustituto de una corrección posible. También detectó antes del render de 28 un acento y posibles solapes de captions de 10 ms, corregidos y comprobados en fronteras exactas.

VIDEO30v2 conserva un fondo navy persistente: la revisión de 24 frames críticos confirmó que desapareció el flash, con 14 dependencias del candidato intactas y únicamente index.html cambiado. El MP4 nuevo recibió su propio control técnico y paridad AAC completa. VIDEO29v2 retrasa tarjetas, círculo y cuerpo de cierre hasta que el fondo sea opaco; su revisión exacta está pendiente en este borrador.

Todos los MP4 nuevos se verifican mediante sus propias rutas, hashes, metadatos, decodificación, niveles y fotogramas. La paridad técnica de audio y los eventos SFX no prueban audibilidad subjetiva ni escucha humana.

## Integridad de la medición

Dos eventos tempranos de VIDEO28 apuntaban a index.html y QA_FIDELIDAD_PLANTILLA.md todavía mutables. Al cambiar estos archivos, el helper de reporte rechazó sus hashes. Se preservaron los eventos y hashes históricos; no se reparó la historia para aparentar un PASS. El índice manual de artefactos finales estables se separa de este fallo metodológico. La validez del MP4 se sostiene en sus recibos y hash exacto, sin convertir el reporte automático en aprobado.

El costo de errores de comandos, checks repetidos, smokes fallidos visualmente, correcciones y segundos renders forma parte de la ejecución real. Cuando un comando carece de cronómetro propio se registra el hecho y su duración queda sin medir; no se rellena con cero. Un render que termina con exit 0 puede requerir retrabajo por un defecto visual.

## Aprendizajes operativos y decisión

1. Conservar un fondo explícito y persistente en la raíz de la composición HDR. Apagar titulares y módulos al salir mediante estados deterministas; el fondo no debe depender de una animación que deje negro el lienzo.
2. En entradas de placas completas, mostrar el cuerpo gráfico después de que el fondo oculte el presentador. Proteger el rostro también en los frames de transición.
3. Registrar eventos contra copias inmutables o versiones cerradas, no contra documentos de trabajo que se actualizarán.
4. Usar un smoke representativo con captions, hueco, transición de escena y retorno. El check del DOM y un frame central no detectan todas las diferencias del export HDR.
5. Tras un cambio localizado, revisar las dependencias actuales y estados afectados; verificar siempre el MP4 nuevo. No repetir un check completo sin una razón nueva.

**La decisión de velocidad permanece pendiente en este borrador.** Cinco observaciones con dos pares aproximados y un alcance esencial distinto no permiten una conclusión causal sobre ahorro. Flujo 1 sigue predeterminado; flujos 2/3 permanecen experimentales.

## Límites de entrega

La ejecución está autorizada para renders locales autónomos. No se infiere aprobación editorial humana, publicación, escucha, naturalidad, reproducción continua, revisión en dispositivo físico o certificación de Instagram/Facebook/TikTok. La ingesta sigue siendo provisional: falta escucha y la claqueta de 27 ausente se adjudicó por contexto, sin inventarla. El término del hook de 26 fue adjudicado contextualmente en el derivado editorial; su confirmación auditiva sigue pendiente.

El informe final debe enlazar los cinco MP4 definitivos, los cinco QA exactos, la asignación congelada, los relojes, auditorías y el índice manual estable.
