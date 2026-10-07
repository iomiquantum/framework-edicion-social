# Análisis de voz y dirección sonora

Fecha: 2026-09-30. Petición: analizar contraste, énfasis, entonación, pausas, ritmo, interpretación y proyección para elegir música y efectos. Estado: mediciones descriptivas y propuestas editoriales; percepción y eficacia por confirmar.

**VIDEO-13 tiene variación de tono e intensidad. Sus pausas internas son especialmente regulares.** Esa regularidad es una hipótesis concreta para revisar la sensación plana que reportó el usuario. El procesado no muestra una pérdida clara del contraste de intensidad frente al mismo origen.

Se midió la voz declarada en 18 editables: VIDEO-01–16,21 y 22 de la instantánea de investigación. Se mapearon por frases 11,13,14 y 21. No equivale a 18 escuchas humanas completas ni a revisar todas las versiones históricas. En 14 el activo del editable tiene un nivel diferente al render normalizado; las audiciones aisladas igualan el volumen para reducir ese confusor.

## Hallazgos en VIDEO-13

- **Entonación:** mediana estimada de 153 Hz; rango central 116–193 Hz, equivalente a 8,73 semitonos. El inicio y la revaloración «Esa información puede valer más que cien prompts» tienen medianas más altas que varios tramos vecinos. Hay movimiento de tono.
- **Intensidad:** rango central de 14,64 dB entre ventanas sonoras. La pregunta final tiene aproximadamente 2,3 dB menos de energía mediana que el bloque de «cien prompts». Esto describe una diferencia; no determina si la pregunta se percibe cercana o débil.
- **Pausas:** siete intervalos internos de energía baja de 0,35–0,44 s; mediana 0,42 s y variación relativa 7,5 %. En 11 esa variación es 58,1 %, en 14 es 49,4 % y en 21 es 26,0 %, con el mismo método. La regularidad puede contribuir a una cadencia predecible; no demuestra la causa ni convierte una pausa irregular en mejor.
- **Procesado:** el mismo origen con los mismos cortes conserva 8,73 semitonos de rango central y 14,45 dB de contraste de energía; el editable tiene 8,73 y 14,64. No aparece una reducción material del contraste en estas medidas.
- **Revisión de la hipótesis preliminar:** la diferencia de ganancia calculada antes en ventanas sin alinear era variable. Tras compensar 21,38 ms entre previews, el 80 % central de las diferencias queda entre−0,39 y+0,42 dB a igual LUFS; correlación de waveform 0,935. La variación preliminar no prueba compresión. Ambas evidencias se conservan.

La percepción reportada por el usuario sigue siendo válida. Las curvas no prueban interés: también cuenta **qué palabra recibe énfasis, dónde cambia la intención y cuánto espacio recibe la idea principal**. Los tiempos de ASR disponibles incluyen duraciones de palabras inverosímiles; se reutilizaron los captions como referencia de frases, sin fingir precisión por palabra ni repetir la transcripción.

## Interpretación y acompañamiento por pieza

Estas lecturas se basan en mensaje, estructura y curvas. Son propuestas a contrastar escuchando el video; no emociones detectadas ni rasgos de personalidad.

| Pieza | Intención y evidencia | Acompañamiento que conviene evaluar |
| --- | --- | --- |
| 11 | Critica contenido genérico, enumera facilidad de producir y cambia al valor de una idea propia. La enumeración eleva la mediana de tono; las pausas tienen duraciones diversas. | Pulso contenido durante la acumulación; espacio al giro de valor. Un acento puede acompañar «algo propio que decir» con el recurso visual. |
| 13 | Afirmación firme, contraste marketing/cliente, llamadas y objeciones, revaloración y pregunta. Posible proyección: criterio que invita a reflexionar. | Notas cortas y pulso ligero durante la explicación; despejar remate y pregunta. Evaluar contraste de pausas antes de otra cama. La tanda ambiental presentada quedó rechazada. |
| 14 | Propone conversación y escucha. Las pausas grandes entre bloques rondan 0,6–0,7 s. Posible proyección: curiosidad y cercanía. | Ritmo ligero con espacio. Sonido de conversación/libreta donde la imagen lo justifique; margen para la invitación final. |
| 21 | Advierte sobre promesas de control, explica atención/confianza y cierra con un límite ético. Varias entradas altas descienden al cierre del bloque. | Voz y acentos en cambios del argumento; base neutra poco densa si aporta continuidad. Dar peso a entender/manipular. |

Para 13 propongo este recorrido: apertura con presencia; explicación con avance suave; remate con espacio; pregunta con aire. La música acompaña la progresión y los efectos marcan una revelación o cambio visible. La coincidencia con una palabra exacta necesita validación de su acento real. No se aplicó ningún cambio al video.

## Ficha de voz para orientar la edición

| Dimensión | Información a registrar | Decisión que puede orientar |
| --- | --- | --- |
| Entonación | Subidas, bajadas y repetición de contornos por idea. | Sostener, retirar o resolver el fondo. |
| Énfasis | Tono, intensidad y duración ligados a la palabra relevante; escucha del acento real. | Aparición visual o acento sonoro que merece coincidir con ella. |
| Pausas | Respiración, cierre de idea, anticipación, pregunta y silencios del montaje. | Preservar pensamiento y expectativa; variar espacio cuando ayude al sentido. |
| Ritmo | Velocidad por bloques, duración de grupos y contraste de cadencias. | Densidad del pulso y cantidad de eventos musicales. |
| Intensidad | Crecimientos, descenso final y comparación con el mismo origen. | Ganancia, automatización y ducking que conserven el gesto vocal. |
| Timbre y dicción | Color, resonancia, consonantes, respiraciones y naturalidad frente al origen. | Limpieza/EQ conservadora ante un problema demostrado; instrumentos con espacio para la voz. |
| Interpretación y proyección | Intención del guion frente a firmeza, duda, ironía, curiosidad, cercanía o urgencia percibidas. | Carácter del sonido, silencio o SFX. Registrar lectura, confianza y contexto. |
| Contexto | Voz aislada y luego rostro, gesto, captions y música en el video. | Confirmar que el conjunto comunica la misma intención. |

Crear un mapa de intención por frases antes de escoger audio. Comparar acompañamiento con voz sola en el mismo montaje. Cambiar interpretación, edición, mezcla y música simultáneamente impediría saber qué funcionó. Una frecuencia, BPM o puntuación automática no representa toda la interpretación.

## Método y límites

Se reconstruyeron los tramos declarados en cada HTML con posición, media-start y ganancia, excluyendo BGM y SFX independientes. Se guardaron rutas y hashes. El análisis usa mono 16 kHz, Praat 6.1.38 mediante Parselmouth 0.4.7, autocorrelación sin filtrar 60–500 Hz cada 10 ms y sensibilidad 75–450 Hz. Discrepancias mayores de un semitono: 1,1–3,4 % en frames comparables. Hay saltos candidatos a error y consonantes sin F0; cada punto no se presenta como entonación cierta.

Praat recomienda hoy autocorrelación filtrada para entonación; la versión embebida utilizada ofrece el método anterior. Las estimaciones necesitan revisión antes de corregir palabras concretas. [Praat, elección del método](https://praat.org/manual/how_to_choose_a_pitch_analysis_method.html). [Parselmouth, implementación](https://parselmouth.readthedocs.io/en/stable/).

Energía en ventanas 50 ms y salto 10 ms. Los intervalos bajos usan umbral relativo p90 menos 22 dB, con sensibilidad 18/26 dB, y duración mínima 150 ms. Pueden incluir consonantes, respiración o cortes: no es VAD validado. Los cues son tiempos de visualización de captions; sus palabras por minuto son aproximaciones editoriales, no velocidad silábica exacta. No se midió dicción, timbre percibido, salud vocal o emoción mediante un clasificador.

Un estudio de 2024 grabó ocho oradores en dos estilos y obtuvo valoraciones de 21 oyentes: encontró asociaciones entre variación de duraciones y carisma percibido. Estudió presentaciones comerciales en inglés; no establece la pausa ideal de nuestros reels. [Niebuhr y Taghva](https://www.isca-archive.org/interspeech_2024/niebuhr24_interspeech.html). Otro estudio de 51 discursos y 50 oyentes encontró relaciones más fuertes para variación/distribución que para nivel medio, con diferencias por grupo: subir toda la voz no equivale a mejorar interpretación. [Niebuhr y Skarnitzl, 2021](https://www.isca-archive.org/tai_2021/niebuhr21_tai.html).

El [visor por frases](voz.html) contiene cuatro voces y el origen de 13 con los mismos cortes. Audiciones finales mono 48 kHz/PCM 24, todas a −22 LUFS ±0,1 mediante **ganancia constante**: sin EQ, nueva compresión, denoise, música o cambio de velocidad. Ese nivel sirve exclusivamente a esta comparación. Las primeras pruebas 16k se conservan como antecedente técnico y no se usan para juicio de timbre.

No hubo escucha del agente ni medición de audiencia. Naturalidad, énfasis palabra a palabra y proyección final: **por confirmar**. [Datos y hashes](evidencia/prosodia/analisis.json), [alineación](evidencia/prosodia/alineacion-origen-procesada.json), [script reproducible](scripts/analizar_prosodia.py).

## Medidas de las 18 piezas

Rangos centrales p10–p90. «Pausa» significa intervalo interno de energía baja ≥150 ms. Intensidad en unidades digitales, no presión sonora ni volumen percibido. Esta tabla no es un ranking de calidad.

| Pieza | F0 mediana Hz | Rango tono st | Rango intensidad dB | Pausa mediana s | Intervalos internos |
| --- | ---: | ---: | ---: | ---: | ---: |
| VIDEO-01 | 129.7 | 7.79 | 14.65 | 0.35 | 11 |
| VIDEO-02 | 141.3 | 8.69 | 13.28 | 0.36 | 8 |
| VIDEO-03 | 134.7 | 9.83 | 13.93 | 0.35 | 9 |
| VIDEO-04 | 132.7 | 8.26 | 12.48 | 0.36 | 7 |
| VIDEO-05 | 131.7 | 9.84 | 13.71 | 0.39 | 7 |
| VIDEO-06 | 132.1 | 11.08 | 13.28 | 0.34 | 6 |
| VIDEO-07 | 137.5 | 11.01 | 12.52 | 0.33 | 6 |
| VIDEO-08 | 142.6 | 11.00 | 13.23 | 0.32 | 8 |
| VIDEO-09 | 142.9 | 11.99 | 13.36 | 0.33 | 7 |
| VIDEO-10 | 135.1 | 9.43 | 14.06 | 0.34 | 9 |
| VIDEO-11 | 154.6 | 11.08 | 14.23 | 0.41 | 14 |
| VIDEO-12 | 155.8 | 9.75 | 14.97 | 0.25 | 8 |
| VIDEO-13 | 153.1 | 8.73 | 14.64 | 0.42 | 7 |
| VIDEO-14 | 149.4 | 8.69 | 14.61 | 0.63 | 7 |
| VIDEO-15 | 150.4 | 10.84 | 15.79 | 0.52 | 5 |
| VIDEO-16 | 138.0 | 9.03 | 15.00 | 0.38 | 11 |
| VIDEO-21 | 133.7 | 8.79 | 15.46 | 0.58 | 5 |
| VIDEO-22 | 138.5 | 9.47 | 14.40 | 0.58 | 6 |
