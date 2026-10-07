# Cama tecnológica original

`tech_pulse_114bpm_8bars.wav` es una textura/pulso instrumental discreta de 8 compases en 4/4 a 114 BPM, unos 16,842 segundos. Estéreo, WAV PCM 48 kHz/24-bit, pico −18 dBFS. La medición EBU R128 con FFmpeg da −32,3 LUFS integrados, rango de 1,8 LU y pico verdadero de −18,0 dBTP. Incluye un pad suspendido, bajo suave, notas espaciadas y ruido percusivo tenue. Centro tonal de mi mayor, compatible con la familia melódica del pack de efectos. No es una canción ni un audio identificado como tendencia.

## Uso bajo voz

Repetir el archivo a su duración exacta, sin silencios entre copias. La síntesis circular conserva las colas en el inicio y las fases continuas del pad; no recortar arbitrariamente para construir el loop. Para un minuto bastan cuatro repeticiones y recorte al final. Aplicar un fundido de entrada de 150–300 ms y salida de 500–900 ms sobre la secuencia completa, no sobre cada repetición.

Como punto inicial, aplicar −6 dB de ganancia al archivo y ducking adicional de 4–7 dB cuando habla el presentador, ataque de 15–35 ms y recuperación de 180–350 ms. Son parámetros de partida editorial, no valores universales: escuchar a bajo volumen y ajustar para que todas las palabras se entiendan. Evitar que la recuperación del ducking haga subir la música en cada pausa de respiración. Con voz continua, una ganancia estable muy baja puede resultar más natural.

No añadir esta cama si el original ya contiene música, si compite con la emoción del guion o si los efectos melódicos de otro pack chocan con su tonalidad. No compensar una voz poco clara subiendo su volumen sin corregir antes ruido y equilibrio. Comprobar el nivel integrado y el pico verdadero de la mezcla final.

## Procedencia y reproducción

Generada el 23 de septiembre de 2026 desde cero con `generate_bed.py`, usando únicamente la biblioteca estándar de Python: osciladores, ruido y envolventes. No contiene muestras, grabaciones ni material musical externo. Se ofrece bajo CC0 1.0 Universal en la medida en que existan derechos, con la misma declaración de procedencia del pack `../sfx/README.md`. Texto: <https://creativecommons.org/publicdomain/zero/1.0/>.

Regenerar mediante `python3 generate_bed.py`. El script reemplaza este WAV y su manifiesto dentro de esta carpeta. `manifest.json` registra formato, duración, pico, RMS y diferencia de muestras en el punto de repetición. La aprobación estética final depende de la escucha con la voz del proyecto.

## Candidatos descargados para comparar bajo voz

La investigación del2026-09-30 añade tres pistas oficiales con CC BY4.0 en [candidates/2026-09-30](candidates/2026-09-30/README.md). Mantienen estado `candidate`: licencia, archivos y decode verificados; escucha, adecuación y adopción por confirmar. Requieren atribución e indicación de cambios. La cama original y sus instrucciones anteriores se conservan.

[Investigación y recomendaciones](../../research/musica-bajo-voz-2026-09-30/INFORME.md). [Banco de comparaciones](../../research/musica-bajo-voz-2026-09-30/banco.html).


## Biblioteca por función y feedback — 2026-09-30

Se añade un [catálogo editorial](CATALOGO_EDITORIAL.md) y un [visor de escucha](../../research/musica-bajo-voz-2026-09-30/biblioteca.html) con música y ocho SFX originales. Tres candidatos musicales actuales: Neon/No Melody (dirección de C valorada por el usuario, mezcla pendiente), Resonance/alternativa y Sarsaparilla (nuevos, sin escucha). Los antecedentes y extractos descartados se conservan aparte en el visor, sin mover ni borrar archivos. Créditos, hashes y licencias enlazados en cada ficha.

Criterio vigente para piezas de 15–30 s: una música o dos según argumento y contexto, sin cuota automática; selección por función y mezcla por frase. Los parámetros históricos anteriores son puntos de partida, no sustituyen este trabajo ni aprueban una relación de volumen para cada palabra. Ninguna música de los videos de referencia se adopta en la biblioteca.
