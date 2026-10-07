# Cinco pruebas de musicalización por contexto

Petición: probar la dirección sonora en tres voces cortas de20–30s y dos piezas largas existentes, sin dar veredicto final sobre canciones. Cambiar nivel como una mezcla editorial, incluir música y efectos, documentar el proceso y dejar audiciones completas. Una o dos músicas en cortos según duración y contexto, sin obligación de cambiar por cronómetro.

## Punto de partida y selección

C tenía dirección/inicio favorables según el usuario, con bajadas solicitadas. La primera tanda calmada fue rechazada y la tanda reciente se percibió con sonidos fuertes; no se declaró rechazo definitivo de sus canciones completas. Las dos referencias sirven para estudiar entradas, retiros, cambios de intención y acentos; ninguna música extraída se reutiliza.

Se localizaron voces nativas existentes. Para01 se usa el corte vigente21,375s, no el antiguo voice-master28,893s. Para14 el máster anterior a música/SFX del editable vigente, no el final con efectos integrados. La pieza52,93s es la voz genérica Kokoro seleccionada en el explainer; se conserva sin usar la alternativa de clon con error documentado. La pieza158,798s es la guía HeyGen de V05 que une01–15; es voz artificial, no clon del usuario. El recuerdo de1/2min era aproximado: se conservan sus duraciones reales. También se localizó radio-cut humano130,892s en V03, sin modificarlo ni presentarlo como la guía más reciente.

Inventario/hashes/formatos: fuentes/inventario.json. Las tres fuentes humanas están a48k; Kokoro fue creado originalmente a24k y el máster localizado a48k; la guía HeyGen está a44,1k. Remuestrear a48k no recupera información ausente. Mono se duplica unity en L/R para comparar en el mismo dominio; no se usa PCM16k de reconocimiento para mezcla. La cola01 tiene1ms de silencio de alineación y11 tiene16,1875ms: diferencias entre duración de audio y contenedor, sin mover palabras ni cortes.

## Voz antes de música

Se reutilizan transcripciones/metadata y tiempos del montaje.01 usa captions actuales porque el transcript-final correspondía a una versión anterior.11/14 usan ASR existente;14 contiene errores escritos y una frontera fusionada entre mejor/pregunta: se toma contexto corregido del guion/cut-plan, se conserva ASR y se trata como aproximación. Largos: líneas reales de metadataKokoro y366 palabras de guíaV05. No nueva ASR ni nueva voz.

Praat autocorrelación75–400Hz/20ms, RMS50ms y umbral de baja energía relativo al propio audio. Cada fuente tiene perfil global, por frases, ritmo descriptivo y pausas en evidencia/prosodia-*.json. F0 puede errar por octavas; pausas de baja energía incluyen respiración/residuo. Métricas no prueban emoción, defecto vocal, intención psicológica ni recepción de la audiencia. Lectura del texto/contexto es inferencia editorial. No se activó restauración especializada ni se aplicaron nueva EQ/compresión/denoise sobre voz.

| Voz | F0 mediano estimado | Rango central estimado | Contraste central de energía activa |
| --- | ---: | ---: | ---: |
| La IA y el retrabajo | 129.3Hz | 7.17st | 15.24dB |
| Contenido propio | 154.4Hz | 10.56st | 15.39dB |
| Escuchar al cliente | 148.6Hz | 8.44st | 16.18dB |
| Retrabajo acelerado | 169.5Hz | 8.23st | 11.5dB |
| De atención a ventas | 115.9Hz | 6.92st | 15.43dB |

## Diseño y procesamiento

Cada plan escribe función por tramo antes de elegir archivo. Una pista puede desaparecer, volver más discreta o dejar una frase desnuda. Las tres pruebas cortas usan una pista cada una; el largo53s cambia de mecanismo a aplicación con dos; el largo2:39 usa cuatro recursos y tres funciones (contraste/mecanismo, conversación/evidencia, acción), repetidos y transformados entre actos. Ninguna selección está aprobada globalmente.

Nuevas fuentes oficiales: Backbay Lounge, Clean Soul y Cipher de Kevin MacLeod. Se obtiene filename/ISRC del catálogo público oficial pieces.json y el enlace de la página real; Cipher usa Cipher2.mp3. Se congelan originales, HTML y licenciaCC BY4.0 actual, créditos y hashes. HeyGen search devolvió UNAUTHORIZED; se continuó por fuentes públicas, sin enviar voces ni cambiar conexión. Biblioteca principal conserva seis candidatos musicales, ochoSFX y cuatro antecedentes, con feedback específico; no limpia la historia.

Voz: ganancia constante por pieza para aproximar−18LUFS estéreo con techo fuente−3,2dBTP. Mezcla y control tienen exactamente el mismo aporte de voz; no se aplana su dinámica. Música: highpass70Hz/lowpass9kHz y resta de60% de banda400–4000Hz en el derivado, sin alterar originales. Este carve deja espacio y es una elección provisional; no se afirma que el timbre sea óptimo sin escucha.

V1 contiene automatización editorial en dB por frases y SFX. V2 añade protección secundaria solo descendente: lecturaRMS50ms, anticipación aproximada100ms, recuperación suavizada; nunca devuelve la música por encima del plan en cada silencio. Ajusta frases/sílabas suaves y evalúa la banda350–5000Hz. Objetivo orientativo de margen14dB: curvas suavizadas y energía residual no garantizan cumplimiento por cada50ms, inteligibilidad ni percepción. Se mantienen todas las curvas, incluidas ventanas de posible competencia. No hay fórmula universal de volumen ideal.

SFX: biblioteca originalCC0, mínimo dos identidades por corto y un acento en todos los hooks. Cada evento tiene función, fuente/hash, ataque/cola, calibración contra voz local y techo de pico; no se usan impactos por cada palabra. En pausas, el SFX puede superar el residual de voz: una relación positiva no es por sí misma enmascaramiento. Se revisa contexto hablado cercano y reproducción nativa. Efectos conservan su identidad aunque cambie nivel.

Suma48kfloat, archivoWAVPCM24 y AAC256kbps estéreo. Se estima true peak a4× antes de escribir; se mide AAC real y existe corrección global compartida con control si el codec supera−1,5dBTP. En estas cinco mezclas no fue necesaria correcciónAAC. V1 permanece junto a V2 y las fuentes originales. Cada procesamiento queda en scripts y plan-mezcla.json, sin gráficos de audio ocultos dependientes del preview.

## Dirección por pieza y tramos exactos

### La IA y el retrabajo · 21.375s

Pulso de mecanismo que desaparece en el veredicto. Retorno más discreto para sistema y retirada en la pregunta. Una pista; contraste mediante arreglo/nivel.

| Tramo musical | Fuente/offset | Función |
| --- | --- | --- |
| 0.000–11.350s | neon desde45.000s | Repetición; baja antes de las colas suaves. |
| 13.350–21.375s | neon desde70.000s | Sistema sin celebrar; pregunta queda al frente. |

Curvas de ganancia absolutas en plan-mezcla.json; protección secundaria y relación medida en evidencia/relacion-01.json.

| SFX | Tiempo | Decisión |
| --- | ---: | --- |
| 04_soft_pop.wav | 0.025s | Hook: acento corto antes de la entrada vocal. |
| 02_soft_whoosh.wav | 6.050s | Entrada del bucle; transición dentro de pausa. |
| 03_ui_tick.wav | 8.420s | Una corrección del proceso, no cada palabra. |
| 07_loop_return.wav | 9.850s | Último retorno del bucle en pausa; cola protegida. |
| 08_resolve.wav | 13.130s | Salir del bucle y presentar sistema. |

### Contenido propio · 29.1s

Un único groove contenido. Más impulso durante la enumeración; retirada antes de originalidad. El remate pensado/generado tiene espacio.

| Tramo musical | Fuente/offset | Función |
| --- | --- | --- |
| 0.000–13.750s | cipher desde27.000s | Cantidad/velocidad; crecimiento limitado, no aceleración artificial. |
| 16.700–26.050s | cipher desde59.000s | Vuelve detrás de lo propio, desaparece para el último contraste. |

Curvas de ganancia absolutas en plan-mezcla.json; protección secundaria y relación medida en evidencia/relacion-11.json.

| SFX | Tiempo | Decisión |
| --- | ---: | --- |
| 01_airy_in.wav | 0.025s | Hook con entrada suave, sin impacto grave. |
| 03_ui_tick.wav | 8.530s | Preparar enumeración en pausa. |
| 05_low_accent.wav | 13.600s | El giro de cantidad a originalidad, con retirada musical. |
| 04_soft_pop.wav | 20.730s | Pregunta en pausa medida, suave. |

### Escuchar al cliente · 23.26s

Una música de conversación con movimiento suave. Baja durante las necesidades del cliente y se retira en escuchar mejor. Pregunta final casi desnuda.

| Tramo musical | Fuente/offset | Función |
| --- | --- | --- |
| 0.000–13.520s | backbay desde38.000s | Movimiento humano; se abre espacio para qué preocupa/quiere/no entiende. |
| 18.300–23.260s | backbay desde56.300s | Cola tenue durante pregunta; no subir en cada pausa. |

Curvas de ganancia absolutas en plan-mezcla.json; protección secundaria y relación medida en evidencia/relacion-14.json.

| SFX | Tiempo | Decisión |
| --- | ---: | --- |
| 04_soft_pop.wav | 0.030s | Hook: pregunta implícita sobre el prompt. |
| 02_soft_whoosh.wav | 6.370s | Pasar de herramienta a conversación real. |
| 03_ui_tick.wav | 13.500s | Inicio de la tesis escuchar mejor; único punto de puntuación. |

### Retrabajo acelerado · 52.93s

Dos temas: mecanismo en el bucle, groove práctico al explicar flujo y acción. Retirada en la tesis, contraste por sentido; la pregunta final respira.

| Tramo musical | Fuente/offset | Función |
| --- | --- | --- |
| 0.000–16.270s | neon desde45.000s | El bucle tiene movimiento; se evita un golpe en cada verbo. |
| 18.980–32.800s | backbay desde38.000s | Sistema con espacio en la lista de requisitos. |
| 35.060–52.930s | backbay desde60.000s | Aplicación; retirada al diseñar primero el sistema y en cierre. |

Curvas de ganancia absolutas en plan-mezcla.json; protección secundaria y relación medida en evidencia/relacion-largo-53.json.

| SFX | Tiempo | Decisión |
| --- | ---: | --- |
| 01_airy_in.wav | 0.025s | Hook: apertura con aire. |
| 03_ui_tick.wav | 4.830s | Comienza el bucle en pausa. |
| 07_loop_return.wav | 10.960s | Bucle: un retorno, no cuatro impactos. |
| 08_resolve.wav | 19.010s | Del bucle al flujo definido. |
| 05_low_accent.wav | 33.040s | Tesis retrabajo acelerado, precedida de pausa. |
| 04_soft_pop.wav | 34.910s | Prueba práctica. |
| 03_ui_tick.wav | 47.570s | Pregunta final sin crescendo. |

### De atención a ventas · 158.798s

Cuatro recursos, tres funciones: contraste/mecanismo (Cipher y Neon), conversación/evidencia (Clean Soul), acción (Backbay). Los temas se transforman; no ocho canciones para ocho actos.

| Tramo musical | Fuente/offset | Función |
| --- | --- | --- |
| 0.000–24.400s | cipher desde27.000s | Abrir problema, sin tono épico ni golpes para cada negación. |
| 24.160–58.950s | clean desde31.000s | Cambio a persona/evidencia; textura ligera sin drone continuo. |
| 58.980–83.300s | backbay desde38.000s | Conocimiento propio y activo reutilizable; pequeño avance, sin triunfo. |
| 93.310–120.770s | neon desde70.000s | Advertencia: pulso de mecanismo, nunca drama intenso. |
| 120.800–145.960s | backbay desde70.000s | Acción concreta; retirada en una sola y medir antes de automatizar. |
| 146.200–158.798s | clean desde69.000s | Pregunta: leve soporte, cola controlada. |

Curvas de ganancia absolutas en plan-mezcla.json; protección secundaria y relación medida en evidencia/relacion-largo-159.json.

| SFX | Tiempo | Decisión |
| --- | ---: | --- |
| 04_soft_pop.wav | 0.025s | Hook: atención/ventas. |
| 03_ui_tick.wav | 13.120s | Contenido genérico, cambia el argumento. |
| 02_soft_whoosh.wav | 24.200s | De herramienta a cliente. |
| 03_ui_tick.wav | 37.060s | Entrada de evidencia. |
| 08_resolve.wav | 58.940s | Conocimiento del negocio. |
| 05_low_accent.wav | 83.320s | Criterio al frente; música retirada. |
| 07_loop_return.wav | 93.270s | Advertencia sobre procesos. |
| 02_soft_whoosh.wav | 120.800s | De riesgo a aplicación. |
| 04_soft_pop.wav | 142.220s | Una sola: acento en pausa, sin música. |
| 03_ui_tick.wav | 145.980s | Regreso a la pregunta correcta. |

## Validación y resultado

45 archivos de las cinco piezas verificados por hash, formatos, decode completo y energía no nula. Fuentes intactas; suma de stems y voz a ganancia constante verificadas. AAC/PCM correlación mínima0.999803; es equivalencia técnica, no aprobación estética. No se certifica escucha ni atención/retención de audiencia.

| Mezcla final AAC | Duración | LUFS estéreo | True peak | Identidades/eventosSFX |
| --- | ---: | ---: | ---: | ---: |
| La IA y el retrabajo | 21.375s | -18.06 | -3.21dBTP | 5/5 |
| Contenido propio | 29.100s | -18.31 | -2.99dBTP | 4/4 |
| Escuchar al cliente | 23.260s | -19.01 | -3.21dBTP | 3/3 |
| Retrabajo acelerado | 52.930s | -18.01 | -6.11dBTP | 6/7 |
| De atención a ventas | 158.798s | -18.01 | -5.97dBTP | 6/10 |

La relación de banda en ventanas activas con voz350–5000Hz por encima−40dBFS se resume en validacion-entrega.json, conservando también datos de energía menor. Ese recorte describe habla suficientemente energética para comparar; no borra las curvas ni convierte residuos en palabras. P95relativoV2: aproximadamente−16,0/−23,4/−22,2/−19,3/−23,3dB en01/11/14/53/159. Valores más bajos no demuestran mejor mezcla; sirven para localizar una revisión.

Reproducción nativa en banco: los cinco AAC cargaron con duración correcta, errornull y reproducción activa. Comprobados salto11,695s/control de voz conservando≈11,93s; largo83,449s y cambios música/efectos conservando≈83,47/83,49s. La UI pausa otras pruebas al reproducir una y ofrece descarga. Evidencia UI separada de percepción. No se escuchó directamente por el agente; claridad, timbre, naturalidad y preferencia humana siguen por confirmar.

Incidencia real: primera ejecución detuvo el guard por tolerancia de2muestras para voz/contenedor. Se comprobó1ms/16,1875ms de cola, se añadió silencio terminal explícito con tope50ms y se repitió. Script previo/diagnóstico conservados. Aprendizaje previo aplicado: seek antes de entrada/recorte explícito antes de fades; comprobarRMS no nulo además de decode para no entregar previews silenciosos.

## Reproducir y continuar

Scripts, orden: preparar_fuentes.py → perfilar_voces.py (entornoPraat) → crear_plan.py → mezclar.py → crear_banco.py → verificar_entrega.py → integrar_biblioteca.py. FFmpegfull9.0.2; entornoDSP privado scipy/NumPy/soundfile; entornoPraat separado. No se modifican dependencias de otros editables. El servidor8868 ya existente sirve este banco con rangos. El usuario puede usar index.html local o localhost; el banco no requiere Internet para reproducir.

Para afinar, registrar pieza/segundo/qué compite o qué emoción busca. Primero carácter/ubicación/nivel de música/SFX; mantener voz intacta salvo nueva petición. No elegir según rapidez ni según el mayor número de efectos. Pendiente: escucha humana completa, ajustes tras feedback, decisión de repertorio y adopción en el editable que se solicite. Ningún video original reemplazado, ningún contenido publicado, ningún resultado de audiencia medido.

Fuentes verificadas: [catálogo oficial](https://incompetech.com/music/royalty-free/pieces.json), [licencias del compositor](https://incompetech.com/music/royalty-free/licenses/), [CC BY4.0](https://creativecommons.org/licenses/by/4.0/), [Neon](https://www.scottbuckley.com.au/library/neon/). Créditos completos y cambios en CREDITOS.md; derechos de las referencias no se trasladan a esta biblioteca.
