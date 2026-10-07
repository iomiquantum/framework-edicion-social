# Dirección de audio a partir de la voz real

Regla permanente solicitada por el usuario durante VIDEO23, 2026-09-30. Aplicar antes de elegir música/SFX en cada nueva edición y cuando cambie materialmente la voz o su montaje. Reutilizar transcripción y rangos del lote; analizar solo la voz seleccionada. Conservar análisis anteriores y ligar resultados a hashes de voz, transcript y dirección.

## Escuchar, medir y decidir

1. Leer palabras reales y marcadores; identificar hook, contrastes, explicación, conclusión y preguntas como información interna. No mostrar estos nombres en pantalla. Escuchar voz original/limpia cuando sea posible. No afirmar escucha si no la hubo.
2. Perfilar intensidad y cambios de nivel dentro del mismo hablante, tono estimado y variación de entonación, pausas, velocidad por frase, cambios de ritmo y transiciones. Distinguir silencio original de pausa creada por montaje. `scripts/perfilar_voz.py` reutiliza tiempos de palabras y produce curvas y medidas por tramo; requiere el numpy del Python ya incluido en Codex. Guarda parámetros y límites. Un estimador F0 puede fallar por armónicos/octavas; no reemplaza escucha.
3. Contrastar esos datos con la interpretación editorial de las palabras: preferencia, pregunta, explicación, énfasis o cierre. Registrar interpretación como inferencia cuando no esté validada auditivamente. No deducir emociones, personalidad, intención psicológica o lo que percibirá el público únicamente desde pitch/RMS. Los valores absolutos de un desconocido no prueban un defecto vocal.
4. Elegir función y carácter del audio: textura frente a acento tonal, ataque/cola, duración, energía y relación con cambios de idea. La voz manda. No llenar cada pausa ni cada palabra. Una voz que baja ritmo no obliga a música triste; una subida de pitch no obliga a un impacto. Mantener descansos y categorías perceptualmente contrastadas cuando se requieren efectos distintos.
5. Si un SFX no se percibe, comprobar primero pista/timing/gain real y reproducción. Comparar subir nivel, mover a un espacio vocal o sustituir carácter; no sustituir por defecto ni subir sin medir picos/enmascaramiento. Preferir el ajuste que se reconoce sin perturbar fonemas. Guardar alternativa y motivo de la decisión. Ganancias congeladas en derivados WAV con `data-volume=1` reducen dependencias de rutas de reproducción; esto no prueba por sí solo un bug del reproductor ni aprueba un recurso nuevo globalmente.

## Hook y QA obligatorios

- **Todo hook inicial debe llevar al menos un SFX integrado con el hook**, con función editorial, sincronía y presencia verificables. La voz sola no cumple esta instrucción. Elegir ventana del hook por el contenido real; no imponer un sonido agresivo ni tapar palabras. Registrar evento/identidad/hash/nivel/ventana.
- En20–30s, mínimo dos identidades de SFX distintas; variantes normalizadas del mismo original siguen siendo una identidad. Registrar por separado identidad y eventos. Biblioteca aprobada/rotación siguen vigentes.
- Medir cada efecto contra la voz contemporánea: nivel de evento, pico, pausa/actividad vocal, tiempo de mayor energía y sensibilidad en banda limitada. Examinar mezcla completa y margen de true peak. `scripts/revisar_presencia_sfx.py` comprueba coincidencia HTML/plan/hashes, hook con evento, identidades fuente distintas, mezcla estática y riesgos de nivel. Los avisos de posible enmascaramiento requieren decisión contextual, no una fórmula universal de volumen ideal.
- El diagnóstico350–5000Hz es una aproximación de sensibilidad, **no una escucha ni prueba real de teléfono**. Los presets de alerta (-25dBFS de pico, -15dB relativo) orientan revisión; no certifican audibilidad ni inteligibilidad. En una pausa, un efecto puede superar al fondo residual sin superar la voz hablada.
- Verificar SFX solo y **dentro de voz/mix**, en reproducción real y luego en MP4 final; no declarar «audible aprobado» solo porque hay dos archivos o un check verde. Conservar muestra corta de revisión cuando facilite localizar el efecto. Si no hay escucha humana, mantenerla por confirmar y continuar trabajo técnico autorizado.
- El guard está limitado a voz raíz explícita y SFX estáticos. Rechaza grafos anidados de audio, buses, FX/automatización/rate/fades no soportados para evitar medir una mezcla seca distinta. Para esos casos se necesita el grafo real/export y su QA; no se permite presentar el guard estático como evidencia suficiente.
- VIDEO23 integra el guard en `media-runtime.mjs` antes del render junto al guard de texto visible. Toda siguiente edición debe incluir una comprobación equivalente de hook/identidades/presencia/mix en su entrada de render. Ausencia de hook o vínculos inválidos detiene captura. Repetir QA afectado cuando cambie timing/gain/carácter; no repetir ASR o limpieza intactos.

## Caso23

V2 usaba entrada aterciopelada y deslizamiento cálido: categorías distintas, ambas texturas suaves. El usuario no percibió el segundo. Se midió97.24% de energía del deslizamiento por debajo800Hz; esto y la voz superpuesta permiten sospechar enmascaramiento, no probar percepción. Se conservó alternativa con+4dB (mix-15.97LUFS/-1.48dBTP). Se eligió pop tonal redondeado en pausa17.433–17.593s antes de «Viralidad…»: RMS del fondo de voz-45.95dBFS, pico SFX-16.01dBFS. Mantiene las entradas0.1s y12.633s; hook con efecto, tres eventos/dos identidades. Mix seleccionado-15.95LUFS/-1.48dBTP, voz intacta. El ritmo medido se reduce en la conclusión frente al hook; pregunta final tiene pitch mediano estimado superior, con límites del estimador. Interpretación editorial ligada al texto, no emoción certificada. Escucha nueva y aprobación final por confirmar.


## Aprendizaje de export23 — dominio de canales y timing

El MP4final confirmó que una referencia FFmpeg que negocia mono→estéreo implícitamente puede reducir3.01dB la contribución SFX frente a duplicaciónunity del motor/WebAudio. No corregir el montaje por esa diferencia de diagnóstico. El helper ahora duplica explícitamente pistasmono en L/R y compara voz/SFX en el mismo dominio plegado; registra por separado pico fuente y métrica de suma. La referencia del motor0.8.99 usa inicios redondeados al milisegundo:0.333ms de diferencia altera correlación de un tono corto aunque el timing editorial sea equivalente. Validar estas políticas contra cada motor/export antes de generalizarlas. Caso23: acuerdoAAC/reference>0.999 por cada evento, fullmix0.999400; se conserva diagnóstico anterior. Los niveles previos documentados no se borran: su dominio aislado no equivale a relación efectiva del mix estéreo.

## Aprendizaje de export24 — AAC, duración y true peak

Comparar el audio exportado con la referencia del **proceso completo del motor**, además de la mezclaPCM. HyperFrames0.8.99 cuenta paquetesAAC, ajusta duración al número de frames, puede recodificar y limita el true peak del AAC a≤−1dBFS con margen objetivo−1.5dBFS. La compresiónAAC puede elevar picos respecto delPCM: no asumir volumen idéntico ni culpar al efecto por una diferencia global. Comprobar niveles finales, relación voz/SFX, cambios de canales/timing y equivalencia de la cadena. Preservar discrepancias antes de resolverlas; no relajar umbrales para convertir un fallo enPASS.

Caso24: referenciaPCM−16.08LUFS/−1.46dBTP; AAC tras ajuste de duración alcanza−0.6dBTP y activa reducción global−0.900dB/recodificación. Exportfinal−17.0LUFS/−1.2dBTP. Reproducción local de preparaciónPCM16, mezcla, AAC, trim y corrección coincide muestra por muestra con export, incluidos tres eventos/dos fuentes; diagnóstico inicial retenido. No se alteró ni rerenderizó el MP4 aprobado. Ese−0.900dB corresponde a esta salida; no usarlo como preset. Evidencia: VIDEO24/editable-hyperframes-video-24/qa/final-audio-v1/{engine-parity-verified.json,reproduction-recipe.json}. Igualdad técnica no certifica escucha/naturalidad/audibilidad móvil.


## Musicalización por contexto en piezas de 15–30 segundos

Criterio confirmado por el usuario en la investigación de música del 2026-09-30: una música o dos según duración y contexto, sin cuota ni cambios por cronómetro. Una pista puede cubrir varias ideas con arreglo, ganancia, entradas, retiradas y efectos. Una segunda requiere un cambio de intención reconocible y espacio para asentarse. La voz conduce todo el diseño sonoro; conservar claridad en palabras relevantes, finales suaves y entradas después de pausas.

Elegir función y carácter antes del recurso, después escribir automatización editorial por frases. No adoptar un volumen constante porque la media global parezca segura. Ducking o reducción dinámica pueden ayudar como segunda capa; no subir música automáticamente en cada silencio. Revisar transiciones y colas de SFX dentro de la mezcla y el export exactos.

Biblioteca por función, procedencia, licencia y feedback específico: [CATALOGO_EDITORIAL.md](library/music/CATALOGO_EDITORIAL.md), [catalogo-editorial.json](library/music/catalogo-editorial.json). Neon tiene dirección/inicio favorables reportados en C, con bajadas solicitadas; D es una prueba sin aprobación auditiva. Conservar primera tanda descartada, versiones y fuentes. Las dos referencias aportadas son evidencia de investigación; no fuentes de música reutilizable. [Análisis y límites](research/musica-bajo-voz-2026-09-30/ANALISIS_REFERENCIAS_SONORAS.md).


## Aprendizaje25 — carácter, banda y ventana real

Calibrar cada acento contra la voz de su propia ventana y revisar tanto RMS plegado a estéreo como banda350–5000Hz; no aplicar un piso universal de pico del efecto. En una frase suave, forzar pico fuente≥−18dBFS dejó una relación aproximada−1.9dB contra voz. Se retiró ese piso y se conservó techo de seguridad; la resolución contextual quedó−11dB deRMS efectivo, con pico fuente−22.36dBFS. Los números son particulares de este recurso y esta frase, no presets.

En el hook25, mover un golpe grave al comienzo de la voz produjo−18.6dB deRMS relativo y−27.7dB en banda de habla: advertencia de posible enmascaramiento. Cambiar a entrada más amplia y calibrar su ventana dio−11dB global/−11.50dB de banda. Pop del ahorro−12.44/−10.74dB; resolución−11/−8.21dB. Elegir aumento de nivel, ubicación o carácter según evidencia semántica y espectral; conservar comparaciones.

La medición evalúa presencia, contraste y riesgo; no demuestra escucha, timbre natural ni audibilidad en móvil. Confirmar la cadena delAAC exacto y sus cambios globales antes de atribuir una diferencia alSFX. No cambiar la voz ya procesada ni activar restauración especializada sin la solicitud vigente. Evidencia25: editable/qa/{sfx-calibration.json,sfx-presence-v3.*,sfx-presence-v4.*}; futuras referencias deben ligarse alMP4 y su hash.
