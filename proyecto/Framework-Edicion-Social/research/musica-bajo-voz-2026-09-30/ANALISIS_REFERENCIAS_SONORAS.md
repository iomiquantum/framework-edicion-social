# Dos referencias para dirigir y mezclar el sonido

Fecha: 2026-09-30. Fuente: dos grabaciones de pantalla aportadas por el usuario. Petición: estudiar a fondo cambios de fondos, efectos, subidas/bajadas y su relación con lo que se dice; llevar nuestros videos al nivel de acabado que muestran las referencias. El usuario escuchó C, valoró su dirección y el inicio, y pidió bajar música por momentos. Esto **no equivale a aprobación final de la mezcla ni de una música para toda la biblioteca**.

**La lección aplicable es diseñar estados sonoros según el argumento y mezclar dentro de cada estado.** Las referencias alternan acompañamiento presente, explicación con voz por delante, acentos de transición, retirada del fondo y regreso. La música recibe atención por momentos; la voz recupera prioridad cuando cambia el sentido o se pide una acción.

Se revisaron imágenes, transcripción y curvas de las dos mezclas completas. Se estimaron voz y acompañamiento localmente para comparar niveles. **No hubo escucha del agente.** El usuario sí reporta escucha de C y variedad de efectos/músicas en la segunda referencia. Las familias tímbricas exactas, canciones, SFX concretos y valores originales de fader siguen por confirmar. La interpretación editorial se sostiene en las palabras y los cambios visuales; no en una emoción detectada automáticamente.

## Qué se puede demostrar y qué no

Los MP4 duran69,556 y66,336 s. Son capturas móviles de Instagram, con interfaz y actividad del teléfono. En la primera se abre la descripción durante parte del video; eso pertenece a la captura, no al montaje del creador. Los extremos pueden incluir reproducción en bucle. En la segunda hay una cola final sin diálogo. No se cuentan esas circunstancias como decisiones creativas del reel original.

Se extrajo el audio sin cambiar la ganancia. ASR local Whisperlarge-v3 ayuda a dividir el mensaje; no reemplaza escucha y tiene errores, por ejemploHamilton frente aJamilton visible en pantalla, o una frase dudosa sobre repetir formatos. Los tiempos son aproximados de frase. La posición del audio respecto al video se corrige+27,891 ms en referencia1 y+15,374 ms en referencia2.

Demucshtdemucs separa estimaciones de voces, percusión, bajo y otros componentes. Se revirtió una ganancia común y se guardaronFLOATWAV **sin normalizar cada stem por separado**, para no inventar diferencias de volumen. El acompañamiento estimado agrupa música, SFX y posibles residuos vocales. Una subida puede venir de un efecto, instrumentación, interpretación de la pista o automatización; **no demuestra que el editor subió un fader**. La reconstrucción cercana al audio de entrada prueba consistencia de la suma, no pureza de las fuentes. La voz rotulada como robot en referencia1 necesita cautela especial.

Los niveles siguientes son medianas RMS sobre ventanas100ms, no posiciones de un control de volumen, dB de reducción aplicados ni sonoridad percibida. Sirven para ubicar contraste. [Curvas y datos](referencias-usuario/ref-02/perfil-mezcla.json).

## Referencia2: relato de tres pasos y cambio de intención

Cuenta visible: herasmedia. El video presenta un caso de crecimiento, tres pasos y una clase privada a cambio de comentarVIRAL. Las cifras de seguidores son afirmaciones del contenido; esta investigación no las valida ni atribuye el resultado a la edición.

| Tramo del archivo | Mensaje / imagen | Comportamiento medido y lectura editorial | Aplicación a nuestro formato |
| --- | --- | --- | --- |
| 0–8,2 s | Resultado, perfil superpuesto y promesa de tres cosas | Fondo bajo la mayor parte del tiempo y acentos breves. Eventos rápidos alrededor2,5 y7,5 s. No se puede llamar a todos «música alta»: el contexto visual ayuda a distinguir un acento puntual de una cama. | Hook con entrada reconocible, voz clara y un acento relacionado con la promesa, sin llenar todas las palabras. |
| 8,2–18,5 s | «Uno», marca, nicho y sector; exterior y autos | La relación mediana acompañamiento/voz durante habla pasa aproximadamente a−15 dB. Números y títulos delimitan una nueva unidad. | Cambiar estado sonoro cuando empieza la explicación, con una cama que pueda sostener varias frases. |
| 18,5–33,8 s | «Dos», interior de casa, problema y ejemplosPOV/cámara/entrevista | El título tiene una transición; en explicación/ejemplos el acompañamiento queda aproximadamente8–9 dB bajo voz, bastante más presente que en el bloque anterior. Hay sucesos rápidos adicionales. | Usar un carácter o arreglo nuevo ligado al paso; distinguir música de soporte y sonidos de demostración. No copiar ese margen a una voz con otro timbre/nivel. |
| 33,8–39,7 s | Otro interlocutor, piscina, «truquito» y cesión de palabra | El acompañamiento vuelve a unos20 dB bajo voz. La escena prepara lo que viene en vez de mantener la energía del bloque anterior. | El puente puede bajar densidad/volumen para producir expectativa, antes de un regreso. |
| 39,7–44,1 s | «Tres», método y explicación | Acercamiento fuerte entre acompañamiento y voz: mediana cercana a−3 dB durante el título y−7 dB durante la explicación. Esto incluye acentos y posible fuga del separador. | Una entrada musical marcada puede anunciar el paso principal; después debe ceder a sus palabras. No usar estas cifras como receta. |
| 44,1–48,1 s | «Espera», «¿vas a contar eso aquí?», valor del contenido; imagen en blanco y negro | El acompañamiento mediano cae de≈−24 a≈−42 dBFS entre bloques; la voz permanece alrededor−16/−18 dBFS. Cambia sobre todo lo que rodea la conversación. | Para distinguir una interrupción o pregunta, retirar el fondo puede aportar más contraste que añadir otro impacto. |
| 48,1–57,1 s | Oferta de clase privada | Hay una reentrada/acento alrededor49 s; el acompañamiento mediano vuelve a≈−30 dBFS. Después decrece mientras se explica la oferta. | Regresar con intención al pasar de expectativa a solución; mantener claridad en condiciones e instrucciones. |
| 57,1–62,2 s | Qué hacer: comentarVIRAL | El acompañamiento queda unos20 dB bajo voz. La acción se repite con alternancia de interlocutores y menos protagonismo del fondo. | Despejar la acción o pregunta final. La mezcla debe facilitar que se recuerde qué hacer. |

### Dónde está el acabado que buscas

La voz tiene una tarea distinta en cada tramo: anunciar, explicar, dar ejemplos, despertar curiosidad, interrumpir y pedir una acción. La música y los acentos cambian al servicio de esas tareas. También cambian plano, entorno, texto y color. La combinación crea jerarquía; no podemos atribuir toda la atención exclusivamente al audio.

La variedad musical que señalas conviene traducir en **roles**: impulso en la promesa, continuidad en explicación, variación en ejemplos, expectativa en el puente, entrada marcada en el método, retirada en la interrupción y soporte contenido en la oferta. No se identifican nombres ni número exacto de canciones desde el archivo mezclado. Un cambio puede ser otra canción, otro tramo/arreglo de la misma o una capa añadida. La distinción queda registrada como pendiente, no se sustituye por un conteo inventado.

Los efectos funcionan como puntuación, sincronía y relación material con lo mostrado. Hay títulos grandes, cambio de escenario, perfil/cifras y demostración de formatos. En el análisis se marcan candidatos de ataque rápido próximos a2,5/7,5/19,6/39,5/49,0 s, entre otros; **no todos los ataques detectados se certifican como SFX**. La identificación precisa de whoosh, click, impacto, riser, frenada o efecto cómico necesita escucha. Para nuestro montaje sí podemos diseñar esas familias deliberadamente y registrar su función.

El blanco y negro coincide con un cambio de conversación y una retirada fuerte del acompañamiento. Es una relación audiovisual comprobable. Su intención puede leerse como pausa/interrupción dramática por el texto; no se presenta como una emoción del público medida.

## Referencia1: selección de momentos de podcast

Cuenta visible: jamiltongo. Se alternan interlocutores, identidad del invitado, situaciones sobre robots, recursos gráficos y cierre de marca/canal. Es un montaje promocional de fragmentos, con más discontinuidad temática que VIDEO-13.

| Tramo aproximado | Evidencia y comportamiento | Qué extraer para nuestro trabajo |
| --- | --- | --- |
| 1,7–5,7 s | Portero y automatización; acompañamiento muy bajo frente a voz | Una afirmación inicial puede ganar presencia con entrada puntual y luego espacio. |
| 5,7–9,3 s | Presentación e identidad; acompañamiento más presente | La tarjeta/presentación admite un gesto sonoro distinto del desarrollo. |
| 9,3–27,3 s | Identidad, nombre del robot y remate; fondo más contenido y eventos breves | Mantener continuidad entre frases, reservar contraste para reacciones y remates. |
| 27,3–31,4 s | Cuenta deAmazon y cifras en pantalla; energía no vocal concentrada cerca del cambio | Un contador o revelación puede recibir un acento propio, sin que toda la cama tenga que subir. |
| 31,4–42,7 s | Aseo, teleoperación y conversaciones privadas; la relación baja hasta≈−19 dB en el último bloque | Reducir protagonismo sonoro cuando importa comprender una condición o implicación del argumento. |
| 42,7–48,2 s | Respuesta rotulada «Brayan Robot» | Un cambio de voz/personaje necesita espacio propio; el separador puede confundir ese timbre con acompañamiento. |
| ≈51–55,1 s | Relato del hermano/cigarrillos, recuadro pequeño y blanco y negro; acompañamiento muy retirado | La sustracción también es un recurso. No hace falta un efecto en cada palabra para distinguir una historia. |
| ≈55,2–60,6 s | Regreso del acompañamiento antes del final del remate y el robot para el hijo | Recuperar una cama/capa puede marcar salida de una pausa dramática. |
| 60,6–67,6 s | Marca y canal, sin diálogo sostenido | La música puede tomar el primer plano cuando la voz deja de conducir. En una pregunta de VIDEO-13 la prioridad es diferente. |

Ambas referencias usan la caída del acompañamiento cerca de un giro de conversación, con tratamiento visual distinto. La segunda articula pasos de una explicación; la primera salta entre momentos de un podcast. **Para nuestro contenido deIA/negocio, la segunda es una referencia más próxima de progresión explicativa; de la primera tomamos acentos, remates y contraste.** Esta es una selección editorial por formato, no un ranking de calidad o rendimiento.

## Cinco decisiones independientes de mezcla

1. **Selección/arreglo:** elegir instrumentación, pulso, densidad y frase musical adecuados a la función. Un fondo puede tapar por actividad/registro aunque su nivel global sea bajo. No buscar únicamente «música paraIA».
2. **Cambio de estado:** decidir si la siguiente idea conserva cama, cambia arreglo/pista, recibe transición o queda sin fondo. Los cambios deben tener un motivo reconocible en el texto o la imagen.
3. **Automatización editorial:** escribir subidas/bajadas por grupos de palabras e intención. Preparar la bajada antes de la frase importante, mantenerla hasta que termina y recuperar con una transición suave cuando tenga sentido.
4. **Protección local de la voz:** usar ducking o reducción dinámica de bandas como segunda capa si la relación lo pide. Un detector que sube música cada vez que la voz baja puede devolverla durante una consonante, una palabra suave o una pausa del pensamiento. No subir en todos los huecos.
5. **Efectos y cola:** ubicar acento/ataque respecto al gesto, texto y fonemas; medir el evento completo y su cola. Una cola que cruza la próxima frase también ocupa espacio. Ganancia, ubicación y carácter se comparan antes de sustituir un sonido que no se percibe.

No añadimos compresión/EQ a una voz para fabricar interés sin un problema técnico demostrado. Tampoco basta con aumentar el volumen general. Se preserva la interpretación y se modifica primero la relación con el acompañamiento que el usuario señaló.

## Aplicación preparada: C frente a D en VIDEO-13

C ya alterna entrada, explicación con pulso y remate/pregunta despejados. Lo que le faltaba era **mezcla dentro de la explicación**: tenía ganancia constante, salvo los fundidos de entrada y retirada. La media global de música18 dB bajo voz activa no describe todas las palabras.

Con stems propios exactos —sin incertidumbre del separador— hay ventanas para revisar en4,6–4,8/6,3–6,8/8,2–9,8/10,2–12,4 s. Son100ms de energía y pueden contener consonantes o finales de palabra; no se certifica enmascaramiento con ese filtro. El feedback humano confirma que hay momentos donde pide bajar el fondo.

**D es una primera automatización por frases**, conservando los primeros4,05 s de C y toda su voz/efectos:

| Momento | Movimiento de la cama respecto a C | Función propuesta |
| --- | --- | --- |
| 0–4,05 s | Igual | Conservar el inicio que gustó. |
| 4,05–5,1 s | Baja suavemente4 dB y recupera parte | Ceder hacia el final de la primera explicación, sin saltos por sílaba. |
| 5,3–6,8 s | Hasta6 dB menos | Dar espacio al contraste sobre no conocer al cliente. |
| ≈7 s | Recuperación parcial, aún bajo C | Conectar el apoyo visual y la siguiente idea. |
| 7,3–10,1 s | Baja4,5–6 dB | Mantener pulso con espacio para llamadas y sus finales suaves. |
| 10,6–13,4 s | Alrededor5,5 dB menos; conserva retirada final | Facilitar la lista y preparar el cambio de valor. |
| 13,4–19,5 s | Igual: música fuera | Frase clave y pregunta con aire. |

Estos movimientos no se copian de los faders de las referencias: son una prueba específica para nuestra voz, argumento y música. Se interpolan en dB a escala de frases, con el fundido original aplicado además; no persiguen cada pico de waveform. D conserva C, la imagen por paquetes y la contribución de voz/SFX salvo cuantización24bits. MP4D−16,99LUFS/−2,22dBTP; AAC/PCM correlación0,999994. **Escucha y elección de D pendientes**. [Comparar C y D](http://127.0.0.1:8868/research/musica-bajo-voz-2026-09-30/practica.html).

Cambiar canciones no se fija como cuota. Para una pieza de20 s usamos su mapa de ideas; para una pieza de60 s, pasos como los de referencia2 ofrecen más oportunidades de cambios de carácter. La biblioteca debe poder buscarse por función —impulso, explicación, curiosidad, transición, remate, pregunta— y densidad, con licencia/procedencia y aprobación registradas. Las músicas extraídas aquí son estimaciones para análisis, no candidatos licenciados de nuestra biblioteca.

## Un flujo para llegar a ese acabado

Crear mapa de frases e intención → asignar estado sonoro a cada bloque → seleccionar fuentes compatibles/licenciadas → diseñar entradas, cambios y retiros → mezclar por frase contra voz real → ajustar SFX y colas → escuchar dentro del video y en teléfono → validar el export exacto.

En cada bloque registrar: texto, propósito, fondo/capa, motivo de cambio, entrada/salida, puntos de ganancia y efectos. Escuchar especialmente primera consonante, final suave de frase, palabra clave y primera palabra después de una pausa. Comparar el mismo tramo con voz sola y a ganancia vocal idéntica. Si falla claridad, revisar nivel, densidad/registro, ubicación y cola; no cambiar simultáneamente todas las variables.

El resultado buscado es que el sonido ayude a seguir el argumento y sentir sus cambios. Comprensión, naturalidad, atención y eficacia real necesitan validación con personas; cifras deviews o seguidores de una referencia no prueban que su música cause rendimiento.

## Evidencia y pendientes

Originales por hash, probe, WAVmezcla, ASR/logs, estimaciones sin rescale,27 bloques, curvas y capturas en `referencias-usuario/ref-01/` y `ref-02/`. Entorno de análisis aislado reutilizaTorch existente; no se alteran entornos de otras ediciones. Fuente metodológica: [Demucs, documentación oficial](https://github.com/facebookresearch/demucs), entrenamiento en música y limitaciones de separación aplican. [Datos referencia1](referencias-usuario/ref-01/perfil-mezcla.json), [datos referencia2](referencias-usuario/ref-02/perfil-mezcla.json), [QA conjunto](referencias-usuario/validacion.json), [automatizaciónD](evidencia/practica-v2/manifest.json).

Pendientes: identificación auditiva exacta de fondos/efectos, marcas finas de cambio de canción y forma de cada transición; escuchaC/D y posterior adopción en editable/export. No se conoce el proyecto/stems originales ni se declara aprobación global de recursos o mejora de retención. Se preservan C, la tanda rechazada y todos los antecedentes.

## Criterio confirmado para nuestras piezas cortas

El usuario precisa que trabajamos con videos de **15–30 segundos**: pueden llevar una sola música o dos según duración y contexto. La cantidad no es una cuota ni cambia automáticamente a cierto segundo. Una música puede sostener varios estados con arreglo, ganancia, retiros y efectos. Una segunda se justifica cuando aporta un cambio de intención reconocible y tiene espacio para asentarse; comprobar voz y transición completa.

Biblioteca por función en [biblioteca.html](biblioteca.html), con recursos locales, licencia, créditos, estado de prueba y feedback específico. Se conservan las muestras descartadas como antecedentes, sin devolverlas a la selección activa. Neon tiene feedback favorable de la dirección de C; no aprobación global. Resonance/mezcla alternativa y Sarsaparilla son candidatos nuevos por descripciones del compositor, pendientes de escuchar con voz.
