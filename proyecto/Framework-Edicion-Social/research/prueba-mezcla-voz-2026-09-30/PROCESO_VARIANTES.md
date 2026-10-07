# Ampliación: seis tratamientos completos y sistema de comprobación

Fecha local:2026-09-30. El usuario pidió seguir mejorando técnicamente, probar varias canciones sobre las voces largas, más efectos/edición y subidas/bajadas como mezcla multimedia. Solicitó llegar al punto donde la siguiente decisión dependiera de su escucha. Este documento complementa PROCESO.md: conserva aquella tanda, no reescribe su resultado.

## Resultado preparado

Tres versiones completas de52,93s y tres de158,798s. A/Pulso y precisión, B/Cálida y fluida, C/Contraste editorial. Mismo audio de voz y nivel exactos en todas las versiones, sin restauración nueva ni edición de palabras/ritmo. Controles para mix/voz/música/SFX mantienen el momento. Primera prueba conservada para comparación. Tres cortos iniciales intactos.

Seis músicas existentes se probaron en contextos completos, no solo previews: Neon, Cipher, Backbay Lounge, Clean Soul, Resonance y Sarsaparilla. Las cuatro últimas selecciones de paleta se basan en función/argumento y procedencia verificada; los títulos no garantizan encaje. CréditosCC BY4.0, cambios y snapshots se conservan. OchoSFX originales nuevos,91eventos entre las seis alternativas, con semilla/receta/hash y dedicaciónCC0, candidatos sin adopción global. No se reutiliza audio de referencias ni se genera otra voz.

## Relación con las dos referencias

Se reutilizó su análisis de27bloques, contexto visual/textual y contrastes medidos, no se afirmó identificación de canciones/SFX o faders originales sin escucha. Aplicaciones concretas: una entrada en la promesa, cambio de carácter ligado a idea, puente con menos densidad, retirada marcada en tesis/criterio, reentrada de solución y pregunta despejada. Las referencias de≈66/69s no imponen cuota de canciones a cada pieza.

En53s, bucle→definición de flujo→tesis seca→prueba práctica→pregunta. En2:39, atención/ventas→cliente→evidencia→ventaja→criterio sin cama→riesgo→acción→pregunta. Cada variante cambia paleta y densidad, no la contribución de voz. C incluye anticipaciones y más acentos; B menos sonidos y más continuidad. Más eventos no se presentan como mayor calidad.

## Mezcla e iteración

Plan completo con tiempos/offsets/curvas: variantes-largas/plan.json. V1 por variante con automatización editorial y acentos; salida final añade protección local y de colas. Música más presente que primera tanda en ciertos tramos, con intervalos de silencio mantenidos. Fuente→highpass80/lowpass9,5k, filtro5,5k solo para arreglos densos/oscursos marcados, anchuraM/S0,86; carve dinámico400–4000Hz35% A/C y28%B, sobre música, ligado a actividad vocal suavizada. Parámetros provisionales de estos recursos, no presets globales.

Ganancia por puntos en dB anticipa palabras/listas/tesis. Segunda capa descendente para frases suaves y relación de banda350–5000Hz a250ms; objetivo10,5dB orientativo, con suavizado y límites. No devuelve música por encima del plan en cada silencio. SFX se calibran contra voz y contexto cercanos, con techo de pico fuente−18,5dBFS y protección de cola cuando vuelve el habla; algunos deC tienen paneo±0,10. Control de headroom reduce acompañamiento si es necesario y deja voz común. No se requirió esa corrección en las seis salidas.

Los originales no se filtran ni se reemplazan. WAV48kPCM24 y AAC256k, duración/canales comunes. Se conservan mezclasV1 y finales, stems y curvas. Primera ejecución de variantes detectó energía rodante ligeramente negativa por precisión antes de sqrt y guardó A/B finitas, deteniendo C porNaN. Se preservó esa tanda, se verificó mínimo≥−1e−12, se hizo clamp únicamente de residuo de precisión antes de sqrt, se añadió guard explícito y se repitieron las seis. Evidencia: incidencias-ampliacion.json y antes-correccion-media-cuadratica. No se convirtió un fallo enPASS relajando finitud.

## Verificación de archivos

42medios principales nuevos: hashes, decode completo,48k/estéreo/duración, finitud/energía no nula. Seis simulaciones adicionales de downmixmono, banda180–7200Hz/AAC128k; no constituyen escucha en teléfono. Reconstrucción de aporte de voz por resta de música/SFX≤2,4e−7; identidad de voz compartida comprobada. Cada uno de91eventos tiene binding/hash/presencia en elPCM, todas las entradas llevanSFX y hay múltiples identidades. AAC exacto contraPCM de proceso completo y sonoridad/true peak reales. Salidas y métricas en variantes-largas/validacion-entrega.json.

| Pieza/versión | Músicas distintas | Eventos/identidadesSFX | AAC LUFS | dBTP | CorrelaciónAAC/PCM | RMSmono frenteaestéreo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| largo-53/A | 2 | 12/7 | -18.01 | -5.84 | 0.999981 | -0.0056dB |
| largo-53/B | 2 | 9/7 | -18.01 | -5.92 | 0.999989 | -0.0026dB |
| largo-53/C | 4 | 16/8 | -18.02 | -5.85 | 0.999987 | -0.0013dB |
| largo-159/A | 4 | 17/7 | -18.01 | -5.90 | 0.999991 | -0.0027dB |
| largo-159/B | 3 | 11/7 | -18.01 | -5.93 | 0.999994 | -0.0014dB |
| largo-159/C | 5 | 26/8 | -18.01 | -5.85 | 0.999992 | -0.0013dB |

Relación medida por banda en ventanas con voz por encima−40dBFS: P95 música/voz≈−17,1/−22,1/−15,9dB para53A/B/C y−19,2/−20,8/−19,7dB para159A/B/C. Curvas completas conservan las ventanas suaves/pausas. Ese margen y el pico no prueban naturalidad, audibilidad móvil, inteligibilidad ni una emoción. No se usa una puntuación de calidad a partir de RMS.

## Reconocimiento: fallo contrastado, sin ocultarlo

Whisper.cpp large-v3 local, idiomaes,4threads, defaults y sin prompt con guion. Se decodificó elAAC final a16kmono SOLO para QA. Ocho lecturas completas (dos controles, seis mixes); no nuevoASR del lote, ninguna fuente16k mezclada.

Las tres variantes53s reconocen el texto del control y guion conWER0. En2:39, control≈0,82% contra guion; ASR completoA≈27,05%, B≈3,01%, C≈44,54%. A/C repiten frases, algunas con timestamps de duración0. Esto detuvo la conclusión de ese proxy y exigió diagnóstico; los archivos/results/logs se preservan en asr-qa. No se baja toda la música para obtener un porcentaje bonito.

Contraste de señal: entre83,70–93,20s las mezclasA/B y el control son exactamente iguales enPCM (diferencia máxima0); el reconocedor completoA repetía la frase durante ese tramo. El resto del aporte vocal también coincide por suma/resta de stems. Se revisaron las ocho fronteras narrativas preexistentesV05, comunes para control/A/B/C, sin dar guion al motor, en32lecturas independientes. Así se limita contexto del modelo, no se seleccionan solo fragmentos favorables.

| Guía2:39 por ocho actos | Errores contra guion366 palabras | Diferencia contra reconocimiento de control |
| --- | ---: | ---: |
| control | 3 (0.82%) | referencia |
| A | 3 (0.82%) | 0 (0.00%) |
| B | 1 (0.27%) | 2 (0.54%) |
| C | 3 (0.82%) | 0 (0.00%) |

A/C coinciden con reconocimiento del control por actos; B cambia dos palabras y queda más próxima al guion. Esto respalda un problema de contexto/repetición del reconocedor completo, no repetición física del audio ni supresión de esas frases en la mezcla. No demuestra escucha perfecta. Se conserva el resultado completo fallido junto al contraste, no se reemplaza retrospectivamente por el que salió mejor. No se alteró el guion/voz para resolver ese fallo del proxy.

## Reproducción y cierre

Navegador nativo: seis mixes con duración correcta/errornull; cambiosA/B/C conservan≈35,26s y121,15s. B53 inicialmente estaba en estado de seek1 y se comprobó luego estado4/tiempo5,18s; no se certifica avance a partir de una petición deplay solamente. Música/efectos deB53 reproducen y conservan≈5,2s. Comparación voz/primera mezcla de2:39 conserva≈83,46s. GUI pausa otras pruebas; controles/descargas y capítulos vinculados. validacion-ui.json conserva observaciones reales, distintas de audibilidad percibida.

Cierre **LISTA_PARA_ESCUCHA**: checks aplicables de fuente/plan/señal/mezcla/codec/mono/proxyASR/reproductor completos; incidencia numérica corregida, divergencia del reconocedor contrastada y ninguna pérdida física de voz detectada. No hay un problema técnico conocido que justifique seguir modificando estas seis mezclas a ciegas. No afirma agotamiento de toda mejora posible ni que el agente escuchó. Timbre, emoción, jerarquía, naturalidad, fatiga y percepción en altavoz real necesitan valoración del usuario.

## Sistema reutilizable

Nuevo protocoloFramework-Edicion-Social/AUDIO_MEZCLA_CONTEXTO_QA.md enlazado desdeAUDIO_DIRECCION_Y_PROSODIA.md. Integra relaciones por contexto, comparación completa con voz/nivel comunes, guard numérico/export, ASR opcional sin reingesta y cierre honesto. No convierte estas canciones/ganancias en reglas aprobadas ni activa limpieza especializada automáticamente.

Scripts: crear_variantes.py→mezclar_variantes.py→verificar_variantes.py; comprobar_reconocimiento.py y comprobar_asr_por_actos.py investigan el proxy; crear_banco_variantes.py crea el comparador. Solo repetir checks afectados por cambios/fallos/incertidumbre real. Modelos/entornos locales existentes, sin uploads de voces ni modificaciones de dependencias de otros proyectos. fuentes originales/primeros renders conservados.

Pendiente: escucha del usuario por versión/segundo y ajustes concretos; adopción de repertorio en editables solicitados. Ninguna aprobación global/publicación ni mejora de rendimiento de audiencia afirmada. Fuentes/licencias en CREDITOS_VARIANTES.md y manifiestos de biblioteca, mismas páginas oficiales verificadas antes de descarga.
