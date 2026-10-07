# Del perfil de voz a decisiones de edición

Fecha: 2026-09-30. Petición: explicar qué permite hacer en la práctica el análisis de voz y convertirlo en comparaciones de música y efectos. Estado: pruebas de investigación; elección y escucha humana **por confirmar**.

El análisis sirve para decidir **función, momento, carácter y nivel del sonido**. En VIDEO-13 la voz presenta cambios de tono e intensidad, pero las siete pausas internas medidas son bastante regulares. Eso orienta una prueba de contraste entre bloques. No demuestra la causa de la sensación plana reportada ni produce una frecuencia musical ideal.

## Una aplicación concreta a VIDEO-13

| Momento aproximado | Mensaje y lectura editorial | Decisión que probamos | Qué buscamos comprobar |
| --- | --- | --- | --- |
| 0–2,09 s | «La IA no conoce a tu cliente»: afirmación que cuestiona una premisa | Pop breve de entrada; apertura sin cama | Si la aparición se reconoce sin competir con la afirmación |
| 2,09–6,99 s | Contraste entre saber marketing y conocer al cliente | Entrada de un pulso/arpegio sin melodía principal | Si aporta avance conservando claridad de las palabras |
| 6,99–13,39 s | Llamadas, objeciones y razones: evidencia concreta | Continuidad de la cama y un tick al aparecer el apoyo visual | Si ayuda a seguir el argumento sin convertir cada elemento en un efecto |
| 13,39–16,34 s | Información del cliente frente a «cien prompts» | Música retirada y acento grave breve en el cambio de idea | Si la ausencia de cama y el acento distinguen la frase clave |
| 16,34–19,50 s | Pregunta al espectador | Voz despejada, sin resolución musical | Si la pregunta conserva espacio para responder |

La intención de cada tramo se interpreta desde las palabras y el montaje; no se infiere una emoción de la frecuencia fundamental. El valor tiene una mediana de tono estimada mayor que la pregunta, que además presenta menor energía mediana: por eso probamos despejarla antes de decidir subir música o efectos. Los tiempos de frases proceden de captions, no de una alineación fonética exacta.

## Comparaciones preparadas

[Abrir la prueba](http://127.0.0.1:8868/research/musica-bajo-voz-2026-09-30/practica.html).

- **A — Referencia de voz sola:** control, no propuesta de entrega final. Permite reconocer lo que aportan los sonidos.
- **B — Voz y efectos:** tres eventos: pop0,025 s, tick6,99 s y acento13,34 s. Sus fuentes son tres identidades originales distintas.
- **C — Los mismos efectos y pulso:** suma música únicamente de2,09 a13,39 s, con fundidos de0,30 y0,70 s. La retirada ocurre antes de la frase clave, no al final del archivo.

Las tres versiones conservan los585 fotogramas originales1080×1920/30fps, su HEVC10bit/HLG y los mismos paquetes de video por hash. Solo se sustituye el audio en copias aisladas. La voz procede de la audición48k/PCM24, duplicada explícitamente en L/R con+2 dB fijos comunes. No se modifica su entonación, duración, pausas, EQ, compresión o supresión de ruido. Las mezclas PCM conservan la misma contribución vocal; los tres AAC se codifican independientemente.

El pulso procede de **Neon, No Melody**, de Scott Buckley: la fuente oficial lo describe con arpegios y sintetizadores. Su licencia declarada es CC BY4.0 con atribución. Se conserva descarga completa, página oficial, SHA-256 y crédito en `library/music/candidates/2026-09-30-prueba-ritmica/`. Es una nueva candidata, no una pista aprobada. Tiene carácter electrónico retro y también pads, por lo que puede no encajar con la voz. Extracto45,00–56,30 s; no se reutiliza la tanda rechazada como si hubiera sido aceptada.

## La decisión después de comparar

Si **B** ya da suficiente jerarquía, podemos editar con acentos y descansos. Si **C** añade movimiento y conserva atención en las palabras, trasladaríamos al editable la música por bloques y su retirada. Si C distrae o su carácter no encaja, conservaríamos la estructura y cambiaríamos instrumentación/densidad; subir el volumen no es la respuesta automática.

Si B y C siguen planas, la siguiente prueba debe actuar sobre **ritmo e interpretación**: variar pausas entre ideas conservando respiraciones y sincronía, escoger otra toma disponible o dirigir una nueva grabación con palabras de apoyo, énfasis y contraste. Un ecualizador o compresor puede resolver un problema técnico concreto; por sí solo no crea una intención interpretativa. No se ha aplicado ningún cambio de ritmo en estas muestras.

La prueba evita variar todo a la vez: A→B aísla acentos; B→C aísla acompañamiento musical. Revisar entrada, frase clave y pregunta, además del video completo. La claridad, naturalidad y atención percibidas requieren escucha en el dispositivo habitual y teléfono; no se certifican con una cifra.

## Comprobaciones y límites

Tres MP4 decodificados completos. Sonoridad integrada−16,99/−16,99/−16,98 LUFS; true peak−2,14/−2,14/−2,22 dBTP. La música se calibra18 dB por debajo de la mediana RMS de voz activa del bloque, antes de los fundidos; esto no garantiza separación por palabra o banda. Los efectos tienen picos−17,96/−19,12/−19,96 dBFS. Pop/tick atacan sobre baja energía vocal; la cola del acento grave se superpone parcialmente a la siguiente frase, por lo que necesita escucha contextual.

El preflight comprueba fuentes por hash, evento durante el hook y tres identidades. No se usa el guard de mezcla estática de HyperFrames para certificar esta automatización: aquí se verifican los WAV y MP4 exportados. Si se adopta la decisión debe integrarse en el grafo real y validarse su salida exacta. El servidor local8868 soporta rangos HTTP para los saltos y convive con el banco anterior8866.

Evidencia: [manifest técnico](evidencia/practica-v1/manifest.json), [QA complementario](evidencia/practica-v1/validacion.json), [script de preparación](scripts/preparar_practica.py). No se declara escucha por el agente, mejora de retención, aprobación de nuevas músicas/SFX, edición del proyecto VIDEO-13 ni publicación. Las primeras muestras y el análisis anterior se conservan.

Fuente musical: [página oficial de Neon](https://www.scottbuckley.com.au/library/neon/). Crédito: 'Neon' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au. Cambios: extracto, ganancia y fundidos indicados arriba.


## Revisión posterior: C y mezcla por frases

El usuario escuchóC: valora dirección/inicio y pide bajadas de música por momentos. Se conservaC y se añadeD, con el comienzo común y automatización por frases. Dos referencias recibidas y analizadas; ver [análisis](ANALISIS_REFERENCIAS_SONORAS.md) y [reproductor](referencias.html). D queda pendiente de escucha, sin aprobación final de mezcla ni de biblioteca.
