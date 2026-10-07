# Curso vivo y bitácora del sistema de edición de videos

Última actualización: 2026-10-06.
Estado: **documento vivo**  
Proyecto: `Edicion de Videos`

## Para qué existe este documento

Esta bitácora convierte el trabajo real del proyecto en un curso paso a paso. Registra qué se pidió, qué se construyó, por qué se cambió, qué resultado produjo y qué aprendimos. No sustituye los changelogs técnicos de cada carpeta: los conecta y los explica en orden.

Cuando se haga un cambio material en un video, plantilla, estilo, recurso o parte del framework, se añadirá una entrada nueva sin borrar las anteriores. Si un dato no puede demostrarse con los archivos del proyecto o con una indicación explícita del usuario, se marcará como **por confirmar**.

## Cómo pedir una actualización desde este chat

Se puede escribir cualquiera de estas frases:

- `Actualiza la bitácora con todo lo que hicimos desde la última entrada.`
- `Registra este cambio: [descripción y motivo].`
- `Convierte los cambios de hoy en una nueva lección del curso.`
- `Corrige la etapa [número] de la bitácora: [dato correcto].`

Antes de registrar, se revisarán los archivos modificados, los manifiestos, las validaciones y los changelogs especializados. El chat no debe usarse como única memoria del proyecto: este archivo es la memoria legible y permanente.

## Mapa general del aprendizaje

```text
referencias → análisis de estructura → primer bruto → transcripción
→ piloto corto → estilo visual → reel completo → segunda prueba
→ framework reutilizable → biblioteca y feedback → serie de 10 videos
→ ingesta única, QA, automatización y derivados por plataforma
→ revisión por delta, índice semántico, recetas modulares, paquete y cohortes
```

---

## Etapa 1 — Estudiar videos de referencia y extraer sus gramáticas

**Fecha reconstruida:** 2026-09-23  
**Objetivo:** dejar de editar solo por intuición y reconocer estructuras narrativas que pudieran reutilizarse.

### Qué se hizo

1. Se estudiaron seis referencias de video.
2. Cada referencia se convirtió en una ficha de “gramática”: estructura, función de cada tramo y patrón narrativo.
3. Se separó la estructura narrativa del estilo visual. Esto permitió pensar primero en cómo avanza la idea y después en colores, motion, música o efectos.

### Resultado

Se crearon seis documentos en `Estructuras Gramaticales de videos/`, desde `REF_001_GRAMATICA.md` hasta `REF_006_GRAMATICA.md`.

### Aprendizaje

Una referencia no debe copiarse como apariencia completa. Es más útil extraer su lógica —hook, contexto, desarrollo, demostración y cierre— y aplicarla a contenido propio.

### Evidencia disponible

- `Estructuras Gramaticales de videos/REF_001_GRAMATICA.md` a `REF_006_GRAMATICA.md`.
- Los videos originales de esas seis referencias no están actualmente en la carpeta del proyecto; su procedencia exacta queda **por confirmar**.

---

## Etapa 2 — Subir el primer video propio y analizarlo sin modificarlo

**Fecha:** 2026-09-23  
**Proyecto:** `Miguel-Reel-Piloto`  
**Fuente:** `input/RAW_001.mp4`

### Qué se hizo

1. Se conservó intacto el MP4 original y se verificó con SHA-256.
2. Se inspeccionaron resolución, duración, códecs y audio.
3. Se extrajo una copia de audio para análisis, sin recortar ni normalizar el original.
4. Se transcribió localmente en español con Whisper `large-v3`.
5. Se marcaron palabras dudosas en lugar de corregirlas por intuición.
6. Se comparó el contenido con las seis gramáticas y se propuso `REF_003 — AUTHORITY_PROCESS_BREAKDOWN`.
7. Se escogió el tramo 00:17.360–00:31.800 para el primer piloto.

### Por qué se hizo así

El análisis se separó de la edición para proteger el original, evitar inventar palabras y decidir el montaje desde el mensaje real.

### Resultado

Quedaron una transcripción completa, un plan estructurado, un registro de ejecución y una propuesta editorial. Todavía no se había renderizado nada.

### Aprendizaje

Antes de añadir efectos conviene fijar tres cosas: qué dice realmente la fuente, cuál es la unidad narrativa más fuerte y qué dudas necesitan escucha humana.

### Evidencia disponible

- `Miguel-Reel-Piloto/RESUMEN_PARA_CHATGPT.md`
- `Miguel-Reel-Piloto/logs/FASE1_EJECUCION.md`
- `Miguel-Reel-Piloto/transcripts/TRANSCRIPCION_REVISADA.md`
- `Miguel-Reel-Piloto/plans/plan_piloto.json`

---

## Etapa 3 — Construir el primer piloto corto

**Fecha:** 2026-09-23  
**Versión:** piloto FASE 2 / V1  
**Duración:** aproximadamente 14,44 s

### Qué se hizo

1. Se produjo una muestra vertical con el fragmento aprobado.
2. Se corrigió la imagen por tramos.
3. Se añadieron punch-ins discretos, captions y barra de progreso.
4. Se validaron layout, movimiento y contraste con HyperFrames.
5. Se evitó añadir música, datos o recursos externos que todavía no habían sido aprobados.

### Resultado

Se creó `Miguel-Reel-Piloto/outputs/MIGUEL_REEL_PILOTO_FASE2.mp4`.

### Aprendizaje

El primer corte sirvió para validar legibilidad y ritmo con pocas capas. La plantilla visual debía crecer después de demostrar que la base funcionaba.

---

## Etapa 4 — Convertir el piloto en una plantilla visual intercambiable

**Fecha:** 2026-09-23  
**Versión:** 0.2.0 / piloto visual V2  
**Estilo:** `STYLE_001_TECH_EDITORIAL_GOLD`

### Petición y cambio

Se pidió elevar el tratamiento visual sin reemplazar la primera versión. A partir de ahí:

1. Se creó el primer perfil de estilo intercambiable.
2. Se añadieron ilustraciones conceptuales para explicar el loop de IA y el loop musical.
3. Se construyó una biblioteca inicial de ocho iconos SVG.
4. Se sincronizaron overlays con conceptos verificados del guion.
5. Se protegieron ojos, boca y rostro.
6. Se usó el espacio negativo superior derecho en lugar de cubrir el torso con un panel grande.
7. No se representó visualmente la palabra dudosa `cue`.
8. Se limitaron los microzooms al 3 % para no degradar el primer plano.

### Resultado

Se conservó la V1 y se creó `MIGUEL_REEL_PILOTO_VISUAL_V2.mp4`, con manifiesto reproducible y controles visuales.

### Aprendizaje

Una plantilla útil no es un video rígido. Debe separar contenido, recursos, estilo, composición y render para poder cambiar la apariencia sin rehacer el razonamiento editorial.

---

## Etapa 5 — Pasar del piloto de 14 segundos al reel completo

**Fecha:** 2026-09-23  
**Versión:** 0.3.0 / reel completo profesional V1  
**Duración:** 60 s

### Qué se hizo

1. Se editó el minuto completo sin eliminar la muestra corta.
2. Se reorganizó el discurso para abrir con un hook real de la fuente.
3. Se crearon tres cutaways explicativos a pantalla completa.
4. La paleta se amplió de amarillo a carbón, blanco, cian, teal, coral, violeta y menta.
5. Se añadieron captions breves, punch-ins, tarjetas informativas y énfasis tipográficos.
6. Se integró música original y una biblioteca propia de SFX en capas editables.
7. Se corrigieron colisiones entre iconos, encabezados, rótulos y cutaways durante QA.
8. El proyecto se enlazó con un núcleo reutilizable: `Framework-Edicion-Social`.

### Resultado

Se creó `MIGUEL_REEL_COMPLETO_PRO_V1.mp4`, con manifiesto, medición de audio y hoja de contacto de 18 fotogramas.

### Aprendizaje

El paso de piloto a pieza completa obligó a convertir decisiones aisladas en reglas: protección facial, capas editables, recursos trazables y QA antes de entregar.

---

## Etapa 6 — Pedir efectos más visibles y mejorar el diseño sonoro

**Fecha:** 2026-09-23  
**Versión:** 0.4.0 / reel completo profesional V2

### Petición y cambio

La segunda versión hizo más perceptibles los cambios de cámara y amplió el lenguaje de transiciones y sonido:

1. Los microzooms pasaron a punch-ins y regresos visibles de 9–12 %.
2. Se protegieron ojos, boca, cabello y mentón mediante orígenes de transformación seguros.
3. Se añadieron cinco wipes direccionales sincronizados con cambios de idea.
4. Se amplió el diseño sonoro a 22 eventos SFX localizados.
5. Voz, música y SFX se mantuvieron en grupos separados.
6. Se añadió carve dinámico a la música para mejorar la inteligibilidad de la voz.
7. Se incorporaron logos oficiales de Claude y OpenAI, sin recrearlos con IA.
8. Se conservaron los cutaways conceptuales como sustituciones breves del talking head.

### Resultado

Se creó y validó `MIGUEL_REEL_COMPLETO_PRO_V2.mp4` sin reemplazar la V1.

### Aprendizaje

“Más efecto” no significa mover todo. Los efectos deben aparecer en cambios semánticos, proteger al hablante y conservar separación entre capas para poder corregirse después.

---

## Etapa 7 — Extraer un framework reutilizable del primer proyecto

**Fecha:** 2026-09-23  
**Framework:** versiones 1.0.0 y 1.1.0

### Qué se hizo

1. Se separó el núcleo global del reel de Miguel.
2. Se distinguieron fuentes, señales observadas, hipótesis, experimentos, aprendizajes locales y reglas estables.
3. Se creó un radar de cambios de plataformas y tendencias con registro diario y resumen semanal.
4. Se centralizaron tres presets de estilo.
5. Se creó un motor de selección y sustitución de estilos por capas.
6. Se añadió `STYLE_003_IMMERSIVE_WELLNESS`.
7. Se inició una biblioteca reutilizable de iconos, música y efectos.

### Aprendizaje

Una decisión que funcionó en un video no debe convertirse automáticamente en regla universal. Primero debe registrarse como hipótesis o aprendizaje local y conservar su contexto.

---

## Etapa 8 — Probar el framework en un video distinto

**Fecha:** 2026-09-23  
**Proyecto:** `WhatsApp-Reel-Prueba-Fuego`  
**Estilo:** `STYLE_003_IMMERSIVE_WELLNESS`

### Qué se hizo

1. Se creó un proyecto independiente para probar que el sistema no dependía del primer reel.
2. Se conservó el original y se corrigió su orientación.
3. Se generó un máster vertical CFR de 30 fps.
4. Se preservó una pausa experiencial central porque era parte de la historia.
5. Se definió una estética wellness con zooms suaves, ripple, iris y blur.
6. Se añadieron cuatro cutaways conceptuales, cuatro iconos SVG y una cama ambiental original.
7. Se mezclaron música y voz con carve dinámico.
8. Se usaron 14 instancias SFX y nueve movimientos de cámara.

### Resultado

Se creó `PRUEBA_FUEGO_IMMERSIVE_WELLNESS_V1.mp4` y se validaron render, audio, contraste y movimiento.

### Aprendizaje

El mismo framework pudo producir un resultado de carácter muy diferente. Eso confirmó que las reglas editoriales podían permanecer estables mientras el estilo visual y sonoro cambiaba.

---

## Etapa 9 — Registrar feedback, preferencias y recursos reutilizables

**Fecha:** 2026-09-25  
**Framework:** versión 1.2.0

### Peticiones y cambios acumulados

1. Se pidió un flujo más rápido que preparara recursos mientras se grababa.
2. Se separaron QA técnico, aprobación editorial, aprobación explícita del usuario, reutilización y rendimiento.
3. Se creó un perfil versionado de preferencias confirmadas.
4. Se creó un catálogo maestro con IDs, descripciones, hashes, procedencia y restricciones.
5. Se añadió una galería local y revisión por delta: tiempo, capa, elemento y cambio.
6. Se reservaron los renders completos para la entrega y se priorizaron previews y tramos críticos durante revisión.
7. Dos SFX iniciales se retiraron del uso automático después de feedback sobre intensidad y brillo.
8. Se generaron candidatos más suaves; tres fueron aprobados y uno quedó rechazado.

### Aprendizaje

Una corrección del usuario debe convertirse en dato trazable, no en una suposición general. “No usar este sonido aquí” y “no usar nunca sonidos así” tienen alcances distintos.

---

## Etapa 10 — Preparar una serie de diez videos antes del rodaje final

**Fecha:** 2026-09-25  
**Proyecto:** `Serie-IA-Negocios-10-Videos`

### Qué se hizo

1. Se prepararon planes de B-roll y recursos para `VIDEO-01` a `VIDEO-10`.
2. Se crearon 30 recursos visuales provisionales: overlays, fondos/cutaways e imágenes de B-roll.
3. Se reutilizaron recursos aprobados de la biblioteca con reglas de rotación para evitar monotonía.
4. No se inventaron logos, interfaces ni evidencia.
5. Todo el paquete quedó provisional hasta recibir y transcribir las tomas reales.
6. Se recibieron dos archivos maestros: videos 01–05 y videos 06–10.

### Aprendizaje

La preproducción puede adelantarse, pero el metraje y la transcripción finales deciden qué recursos siguen siendo válidos. Preparar no significa fijar prematuramente.

---

## Etapa 11 — Editar VIDEO-01 y convertirlo en candidato de plantilla

**Fecha:** 2026-09-25  
**Video:** `Serie-IA-Negocios-10-Videos/VIDEO-01`

### Qué se hizo

1. Se identificó `VIDEO-01-TAKE-02` como toma aprobada dentro del bruto.
2. Se trabajó con el rango fuente 42.067–70.960 s.
3. Se retiraron silencios reales con protección de 180 ms por lado.
4. Se aceleró la voz a 1,04× sin eliminar palabras.
5. Se añadieron seis escenas gráficas, subtítulos, reencuadres y CTA independiente.
6. Se reutilizaron B-roll de retrabajo, diagrama de ciclo y reloj de arena.
7. Se conservaron versiones de revisión V1 y V2.
8. La estructura `T01-editorial-loop` quedó como candidata de plantilla, todavía pendiente de aprobación humana y prueba en redes.

### Resultado

`VIDEO-01_REVISION_v2.mp4` quedó como revisión vigente, con editable, manifiesto y QA.

### Aprendizaje

Una plantilla no se declara “ganadora” solo porque técnicamente funciona. Debe aprobarse y después contrastarse con resultados reales antes de promoverse.

---

## Etapa 12 — Mejorar el montaje de voz y la ingesta de lotes

**Fecha:** 2026-09-25  
**Framework:** versiones 1.2.1 y 1.3.0

### Qué se cambió

1. La entrada predeterminada se fijó cuatro fotogramas antes del primer fonema a 30 fps, con adaptación por respiración y gesto.
2. Las pausas se clasificaron antes de comprimirlas: silencio inútil, respiración, pausa semántica o excepción expresiva.
3. Se creó `cut-plan.json` para congelar cortes sin destruir el original.
4. Se formalizó la ingesta maestra de una sola pasada: audio, transcripción, marcadores y revisión humana.
5. Se creó `take-map.json` para que varias ediciones reutilicen el mismo análisis.
6. Se añadieron proxies por `VIDEO-NN`; los renders finales siguen usando rangos exactos del original.
7. Se introdujeron `asset-lock.json`, preflight de proyecto y bloqueo de archivos rechazados aunque fueran renombrados.
8. Se creó un scorecard con hard gates y evidencia por render.
9. Se limitó inicialmente a dos la cantidad de procesos pesados simultáneos.

### Aprendizaje

La velocidad sostenible viene de no repetir transcripciones, análisis ni codificaciones. Los proxies aceleran la edición, pero nunca sustituyen al original en la entrega final.

---

## Etapa 13 — Convertir el framework en un sistema profesional verificable

**Fecha:** 2026-09-25  
**Framework:** versión 1.4.0

### Qué se añadió

1. Una matriz profesional de ocho módulos desde grabación hasta aprendizaje posterior.
2. Preflight técnico con resolución, rotación, FPS/VFR, códecs, audio y color.
3. Un `creative-blueprint.json` para hook, beats, emoción, descansos, rostro y presupuestos de motion/SFX.
4. Selección de estilo con ranking explicable y posibilidad válida de abstenerse.
5. Un tablero atómico: un propietario de escritura por video y límite de trabajos pesados.
6. Grafo de dependencias, impacto transitivo y caché por SHA-256.
7. Variantes controladas que cambian una sola familia de elementos.
8. Golden masters inmutables identificados por hash.
9. Un máster vertical neutral y derivados separados para Reels, TikTok y Shorts.
10. Preflight por plataforma y revisión visual ligada al hash exacto del render.
11. Revisión de rendimiento contextual, sin convertir resultados aislados en reglas automáticas.

### Aprendizaje

El framework dejó de ser solo una colección de estilos. Ahora describe estados, responsables, dependencias, gates de calidad, aprobaciones y aprendizaje controlado.

---

## Etapa 14 — Aprender sin congelar la creatividad

**Fecha:** 2026-09-25  
**Framework:** versión 1.5.0

### Qué se añadió

1. Un motor de aprendizaje que separa evidencia técnica, aprobación creativa, preferencia, repetición y rendimiento.
2. Recomendaciones no vinculantes: ningún proceso automático promueve reglas, amplía alcance ni corona una plantilla universal.
3. Recibos de aprobación ligados al SHA-256, tamaño, rol, perfil y alcance del archivo exacto, con tiempos distintos para creación, decisión y registro retrospectivo.
4. Perfiles separados para mezzanine editorial HDR y máster social SDR BT.709, con linaje, conversión y revisión visual obligatorios.
5. Memoria de serie con fingerprint, contrato, ledger y dimensiones `locked`, `bounded`, `rotating` y `free`.
6. QA técnica ligada al mismo SHA-256 de cada aprobación antes de contar evidencia para un default estable.
7. Un banco de plantillas validado que separa aprobación del artefacto, autorización de reutilización, madurez de familia y rendimiento.
8. Un roadmap hacia revisión por timecode, índice semántico de activos, recetas creativas modulares, paquete multicanal y métricas por cohortes.

### Aplicación real a VIDEO-01

`VIDEO-01_REVISION_v2.mp4` quedó aprobado como artefacto editorial exacto mediante `approval-receipt.json`. Su fingerprint conserva el recibo, el manifiesto de render y la QA técnica vinculados al SHA-256 `3caa435b4848a93295a366c06f203031a86bebb94c8f25f246c23b8399d269c4`. El contrato de serie lo usa como semilla descriptiva y el ledger registra una sola aprobación.

El motor no promovió ningún default: con un video solicita más evidencia para formato y velocidad, mantiene estructura y paleta como dimensiones rotativas y conserva `T01-editorial-loop` como candidata. La aprobación del video no aprobó la plantilla, sus activos ni derivados de plataforma.

### Aprendizaje

La memoria profesional debe acelerar decisiones repetidas sin falsificar certeza. Un video aprobado puede convertirse en referencia, pero solo evidencia distinta y verificable permite sugerir un default; la creatividad continúa variando por estructura, formato, estilo, ritmo, motion y sonido.

---

## Etapa 15 — Conectar la optimización para un lote de 30 videos

**Fecha:** 2026-09-25  
**Framework:** versión 1.6.0

### Qué se añadió

1. Una consola de revisión ligada por hash que convierte feedback en `inicio + fin + capa + elemento + instrucción`, calcula impacto y propone previews parciales sin sustituir el recibo de aprobación.
2. Un índice semántico de activos con deduplicación binaria exacta, procedencia, exclusiones y antifatiga consultiva; no afirma similitud visual perceptual.
3. Una gramática ejecutable de 18 módulos que combina hook, estructura, sistema visual, motion, sonido y CTA en hasta tres recetas contextuales, con abstención válida.
4. `creative-attribution.json` para registrar únicamente la receta elegida por una persona y evitar atribuir rendimiento a propuestas no utilizadas o duplicarlo en híbridos.
5. Un paquete multicanal desde el SDR aprobado, con replay de perfiles, linaje HDR, content lock, staging completo, sellos y gates independientes; construirlo no publica nada.
6. Un registro de publicación y métricas que inspecciona el MP4 real, liga evidencia local y ventanas de 24 h, 72 h y 7 días, calcula N de intersección y separa rendimiento creativo de eficiencia de producción verificada.
7. Una guía de operación para trabajar por carriles paralelos en 30 videos y un roadmap 1.7 con cierre atómico, controlador de lote, tablero, regresión audiovisual, preproducción adaptativa y futuros adaptadores externos.

### Aplicación real a la serie

El índice de la serie consolidó 139 activos canónicos desde 237 registros de origen y detectó 11 grupos de duplicados SHA-256. Nueve eventos representan recursos que sí sobrevivieron al VIDEO-01 aprobado; las asignaciones para videos posteriores no cuentan todavía como uso. No existe aún un paquete real ni una cohorte real: ambos permanecen bloqueados hasta disponer de SDR aprobado, publicación y evidencia métrica.

### Aprendizaje

La velocidad acumulativa proviene de analizar una vez, reutilizar con contexto, editar por capas, revisar por delta y aprender solo de evidencia ligada. Los hashes garantizan integridad local, pero no autentican por sí solos a una persona, una cuenta o los datos remotos; el framework conserva esa limitación en vez de fingir certeza.

---

## Estado actual del proyecto

### Completado

- Seis gramáticas de referencia documentadas.
- Piloto corto y dos versiones visuales del reel completo de Miguel.
- Segunda prueba con estilo wellness.
- Framework reutilizable hasta versión 1.6.0, con consola de revisión, índice de activos, recetas, paquete multicanal y cohortes fail-closed.
- Biblioteca de estilos, iconos, música y SFX con procedencia y estados.
- Preproducción de recursos para una serie de diez videos.
- Dos brutos maestros recibidos para esa serie.
- VIDEO-01 V2 aprobado por hash como mezzanine editorial HDR, con recibo, fingerprint, QA y memoria de serie.
- VIDEO-02 V3 y VIDEO-03–05 en versiones revisables con proyectos editables y familias creativas diferenciadas.
- Índice operativo de la serie con 139 activos canónicos, 237 registros de origen, 11 grupos duplicados exactos y nueve usos aprobados.

### En curso o por confirmar

- Aprobación humana de VIDEO-02 V3 y VIDEO-03–05.
- Edición de `VIDEO-06` a `VIDEO-10`; el framework queda preparado para ampliar el lote hasta 30 videos.
- Autorización de reutilización de `T01-editorial-loop`; por ahora solo es candidata.
- Aprobación humana de la plantilla candidata `T02-clean-authority`.
- Máster social SDR y derivados por plataforma de VIDEO-01, solo si se van a publicar.
- Resultados reales de publicación y aprendizaje de rendimiento.
- Implementación de la ola 1.7: cierre atómico, controlador del lote, tablero de eficiencia, regresión audiovisual y preproducción adaptativa.
- Procedencia exacta de los seis videos de referencia originales.

## Índice de registros especializados

- Evolución del framework: `Framework-Edicion-Social/CHANGELOG.md`
- Funcionamiento actual: `Framework-Edicion-Social/README.md`
- Primer piloto y reel completo: `Miguel-Reel-Piloto/CAMBIOS.md`
- Revisiones del primer piloto: `Miguel-Reel-Piloto/REVISIONES.md`
- Segunda prueba: `WhatsApp-Reel-Prueba-Fuego/CAMBIOS.md`
- Serie de diez videos: `Serie-IA-Negocios-10-Videos/RESUMEN_RECURSOS.md`
- VIDEO-01: `Serie-IA-Negocios-10-Videos/VIDEO-01/RESUMEN_VIDEO_01.md`
- VIDEO-02: `Serie-IA-Negocios-10-Videos/VIDEO-02/RESUMEN_VIDEO_02.md`
- VIDEO-03: `Serie-IA-Negocios-10-Videos/VIDEO-03/RESUMEN_VIDEO_03.md`
- VIDEO-04: `Serie-IA-Negocios-10-Videos/VIDEO-04/RESUMEN_VIDEO_04.md`
- VIDEO-05: `Serie-IA-Negocios-10-Videos/VIDEO-05/RESUMEN_VIDEO_05.md`
- Comparativo de producción 02–05: `Serie-IA-Negocios-10-Videos/REPORTE_PRODUCCION_VIDEO_02_A_05.md`
- Investigación de ángulos 06–10: `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/INVESTIGACION_ANGULOS_06_A_10.md`
- Plan de medición de plantillas 01–10: `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/PLAN_MEDICION_PLANTILLAS_01_A_10.md`
- Registro estructurado de plantillas: `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/REGISTRO_PLANTILLAS_01_A_10.json`
- Investigación de diversidad visual 11–20: `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/INVESTIGACION_DIVERSIDAD_VISUAL_11_A_20.md`
- Plan de medición 11–20: `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/PLAN_MEDICION_PLANTILLAS_11_A_20.md`
- Registro estructurado 11–20: `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/REGISTRO_PLANTILLAS_11_A_20.json`

---

## Registro de nuevas entradas

### 2026-09-27 — Se crea el agente de investigación Meta-first para Latinoamérica

- **Petición:** diseñar un agente recurrente de investigación de mercado que estudie en español a personas y cuentas sobre inteligencia artificial, marketing digital, ventas y emprendimiento en Latinoamérica; comenzar perfeccionando Instagram y Facebook, conservar después TikTok y Shorts, entender diferencias de lenguaje por país y controlar el consumo de la cuota semanal.
- **Punto de partida:** el framework ya tenía un radar diario de cambios oficiales de plataforma con foco inicial en Ecuador y tres superficies, pero no existía un universo de cuentas, esquema de publicaciones, rotación por país, capa dialectal ni comparación sistemática contra los 30 videos de la serie. Las observaciones previas declaraban muestra externa insuficiente.
- **Cambios:** se creó `Framework-Edicion-Social/research/market-intelligence/` con configuración Meta-first, 19 mercados en rotación, cuotas nocturnas, matriz de fuentes y límites, banco de consultas, contratos JSON, registro acumulativo de cuentas, estado incremental, plantillas diaria/semanal, prompt nocturno y validador. Se extrajo a `content-dna.json` el contexto verificable de los 30 títulos y sus cinco pilares. También se creó la skill local `.agents/skills/investigador-mercado-meta/` y se documentó el sistema dentro de `OPERACION_RADAR.md` y el changelog del framework.
- **Motivo:** un loop sostenible necesita memoria externa, evidencia, cuotas y condiciones de detención; una búsqueda abierta de “todo Instagram” no es verificable ni eficiente. La rotación permite ampliar el panel sin confundir una muestra con la totalidad y sin gastar Astra en tareas repetitivas.
- **Archivos afectados:** `.agents/skills/investigador-mercado-meta/`; `Framework-Edicion-Social/research/market-intelligence/`; `Framework-Edicion-Social/OPERACION_RADAR.md`; `Framework-Edicion-Social/CHANGELOG.md`; y esta bitácora.
- **Validación:** los JSON, CSV, pesos, 19 mercados, 30 títulos, canales activos y estructura de la skill pasaron los validadores locales. Una corrida piloto de búsqueda pública cubrió Ecuador, México, Colombia y Argentina: descubrió nueve cuentas candidatas, no logró verificar directamente perfiles dentro de Instagram y clasificó una sola publicación con evidencia C y sin métricas. No se afirma que Instagram o Facebook hayan sido scrapeados ni que exista una muestra completa.
- **Resultado:** queda una arquitectura reproducible y una automatización local activa a las 02:30 America/Guayaquil con GPT-6 Luna en esfuerzo bajo. Instagram y Facebook quedan activos; TikTok y YouTube Shorts, modelados pero desactivados. El piloto confirmó que la búsqueda web sirve para descubrir candidatos, pero no basta para comparar rendimiento de contenido.
- **Aprendizaje:** el valor del agente no está en acumular perfiles sin límite, sino en conservar procedencia, comparar señales compatibles, detectar recurrencia entre cuentas y países, y traducirla en experimentos que respeten la voz propia.
- **Pendiente:** conectar Metricool si se desean métricas fiables de cuentas propias; decidir más adelante un proveedor autorizado para ampliar competidores públicos; verificar directamente los nueve candidatos, completar la capa Facebook y ajustar falsos positivos y cuotas antes de activar TikTok y Shorts.

Las entradas nuevas se agregan debajo de esta línea, en orden cronológico.

### 2026-09-27 — Metricool se excluye del radar por falta de relación temática

- **Petición:** aclarar por qué se usaría Metricool si las cuentas conectadas no están relacionadas con la investigación de IA, marketing y ventas.
- **Punto de partida:** la conexión mostraba una sola marca, `Silent Run Ecuador`, con Instagram y Facebook; no había competidores configurados y su contenido no pertenecía al alcance del nuevo agente.
- **Cambios:** se marcó la conexión como `connected_out_of_scope`, se desactivó Metricool en `config/meta-first.json` y se corrigieron el prompt nocturno, la matriz de fuentes, el README y los changelogs para impedir que el loop consulte esa marca.
- **Motivo:** los datos de una cuenta no relacionada contaminarían la línea base y no ayudarían a descubrir ni comparar a creadores de IA, marketing o ventas.
- **Archivos afectados:** `research/market-intelligence/config/meta-first.json`, `context/metricool-profile.json`, `context/source-matrix.md`, `README.md`, `PROMPT_NOCTURNO.md`, los changelogs especializados y esta bitácora.
- **Validación:** Metricool confirmó una sola marca conectada y paneles de competidores vacíos. Las consultas exploratorias devolvieron cero publicaciones de Instagram y solo tres fotos antiguas de Facebook con señal prácticamente nula; esos datos no se incorporaron al universo ni a las observaciones del mercado.
- **Resultado:** Metricool permanece conectado en el producto, pero queda fuera del agente y no consume corridas nocturnas. El radar continúa con descubrimiento público hasta habilitar una fuente adecuada para competidores relevantes.
- **Aprendizaje:** una integración disponible no es automáticamente una fuente válida; primero debe superar el filtro de alcance temático y procedencia.
- **Pendiente:** seleccionar una fuente que permita descubrir o monitorear cuentas competidoras relevantes, o configurar manualmente una lista curada antes de volver a considerar Metricool.

### 2026-09-27 — El diseño de adquisición se prepara para continuar con Astra desde terminal

- **Petición:** confirmar si el primer análisis debía ejecutarse con Sol alto o Astra, y preparar una ruta y un prompt para abrir el trabajo desde terminal porque la ventana actual solo ofrece Sol.
- **Punto de partida:** el radar Meta-first ya existía y Metricool había quedado fuera de alcance. Todavía no se había decidido cómo combinar búsqueda pública, navegación autorizada, snapshots, Apify u otros proveedores para obtener evidencia sobre cuentas emergentes.
- **Cambios:** se creó `PROMPT_ASTRA_ARQUITECTURA_FUENTES.md` como relevo autocontenido. El documento obliga a leer el sistema existente, separa descubrimiento, navegación, métricas e historial, pide comparar esquemas gratuito, híbrido y escalable, define la necesidad de detectar cuentas observables de 30, 90 y 180 días y fija entregables dentro de la carpeta de inteligencia de mercado. El README pasó a recomendar Astra en esfuerzo alto para esta decisión fundacional.
- **Motivo:** el cambio de interfaz no debe perder el contexto ni provocar que una sesión nueva rediseñe desde cero, consulte Metricool por error, instale herramientas prematuramente o trate una fecha inferida como fecha real de creación.
- **Archivos afectados:** `Framework-Edicion-Social/research/market-intelligence/PROMPT_ASTRA_ARQUITECTURA_FUENTES.md`, `README.md`, `CHANGELOG.md` y esta bitácora.
- **Validación:** se comprobó localmente que Codex CLI acepta `-m/--model`, `-C/--cd` y sobreescrituras mediante `-c`; la configuración local contiene `model_reasoning_effort = "high"`. El prompt referencia rutas existentes y no incluye credenciales ni activa servicios externos.
- **Resultado:** existe un punto de entrada único para iniciar una sesión nueva con `gpt-6-astra` y conservar el estado verificable del proyecto. No se cambió el modelo de la conversación abierta, no se conectó Apify y no se gastó presupuesto externo.
- **Aprendizaje:** el modelo es solo una parte del relevo; la continuidad fiable exige un paquete de contexto, rutas de salida, límites de autoridad y reglas de evidencia explícitas.
- **Pendiente:** iniciar la sesión de terminal con Astra, ejecutar el diseño de adquisición y decidir después si el piloto gratuito necesita navegación autenticada o una integración de pago.

### 2026-09-25 — Se crea la bitácora maestra del curso

- **Petición:** documentar desde el inicio todo lo realizado y mantenerlo actualizado desde este chat.
- **Cambio:** se reconstruyó la secuencia del proyecto usando archivos, fechas, changelogs, manifiestos y resúmenes existentes.
- **Archivos:** `BITACORA_CURSO_EDICION.md` y `AGENTS.md`.
- **Decisión:** conservar los registros técnicos especializados y usar este documento como narración central.
- **Validación:** se contrastaron las etapas con los registros de Miguel, WhatsApp, la serie de diez videos y el changelog 1.0.0–1.4.0 del framework.
- **Pendiente:** el usuario puede corregir recuerdos o aportar pasos que no estén representados en los archivos actuales.

### 2026-09-25 — VIDEO-02 enseña protección de sujetos y relevancia visual

- **Petición:** corregir overlays que oscurecían el rostro, retirar un SVG sin relación clara con el discurso, acelerar una transición que mezclaba dos caras y convertir esas observaciones en aprendizaje permanente del framework.
- **Punto de partida:** `VIDEO-02_REVISION_v1.mp4` era técnicamente válido, pero el hook usaba un velo de cuadro completo, un icono ambiguo y un fundido lento hacia una imagen cuya placa cubría el rostro de la chica.
- **Cambio:** se retiraron el velo y el SVG, se reubicaron placas en zonas vacías verificadas, se protegieron sujetos de la toma principal y de imágenes generadas, y se cambió la transición por un corte limpio entre 4.22 y 4.30 s.
- **Motivo:** el rostro y el sujeto de primer plano son información esencial; ningún recurso decorativo debe competir con ellos ni aparecer si no explica la frase activa.
- **Archivos:** escenas editables de `VIDEO-02`, `VIDEO-02_REVISION_v2.mp4`, su manifiesto V2, perfil de preferencias, política editorial, QA profesional, scorecard, feedback, registro de plantillas y changelog del framework.
- **Validación:** HyperFrames 0.8.75 terminó con cero errores y cero avisos de layout o contraste; 23/23 comprobaciones de contraste pasaron; los fotogramas 4.16, 4.22, 4.30 y 4.42 s verificaron la transición; el MP4 conserva 1080×1920, 30 fps, HEVC Main 10, BT.2020 HLG, -16.8 LUFS y -1.4 dBTP. El framework 1.4.1 validó 54 JSON y 73 instancias de esquema.
- **Resultado:** revisión V2 completa y editable; V1 conservada. La plantilla T02 sigue como candidata hasta aprobación explícita del usuario.
- **Aprendizaje:** la revisión previa al render debe comprobar rostros, sujetos de primer plano, espacio negativo real, pertinencia semántica de cada icono/SVG y cambios limpios entre sujetos.
- **Pendiente:** revisión y aprobación explícita de VIDEO-02 V2; no se promueve T02 ni se avanza a otro video sin esa decisión.

### 2026-09-25 — Framework 1.5 aprende con evidencia sin volver rígida la edición

- **Petición:** optimizar continuamente el sistema, crear matrices y plantillas más rápidas sin perder calidad, estructura ni lógica, y probar variaciones reales de estructura, formato y estilo.
- **Punto de partida:** el framework 1.4.1 ya tenía QA, dependencias, caché, perfiles de plataforma y feedback, pero no existían contratos ejecutables para aprobación por archivo exacto, memoria de serie, promoción conservadora o separación formal entre aprobar un video y aprobar su plantilla.
- **Cambio:** se añadieron el motor de aprendizaje, recibos de aprobación, perfiles HDR/SDR, fingerprint y ledger de serie, portafolio de familias, schema del banco de plantillas y roadmap modular. Las auditorías adversariales endurecieron autoridad, revocación, concurrencia, cronología retrospectiva, rutas, hashes, QA ligada al artefacto y verificación real del recibo desde el validador.
- **Motivo:** acelerar el siguiente video mediante conocimiento reutilizable sin convertir una preferencia aislada, una métrica incompleta o una similitud visual en regla universal.
- **Archivos:** núcleo 1.5 de `Framework-Edicion-Social/`; recibo, decisión de revisión, conformidad y resumen de `VIDEO-01`; memoria compartida en `Serie-IA-Negocios-10-Videos/series-memory/`.
- **Validación:** 182 pruebas automatizadas pasaron; `validate_framework.py` reportó `OK v1.5.0` con 70 JSON, 89 instancias validadas, 22 reglas, 17 activos, 23 preferencias, 17 eventos de feedback, 2 familias y 5 plantillas del banco. El recibo real de VIDEO-01 verificó `approved_match`; su QA técnica se ligó al mismo hash y la conformidad de serie no produjo bloqueos ni se comparó consigo misma.
- **Resultado:** VIDEO-01 quedó como semilla aprobada del portafolio, no como plantilla universal. `T01-editorial-loop` conserva estado `candidate` y reutilización `pending`; el motor solicita un segundo video aprobado antes de proponer defaults estables y tres antes de recalibrar.
- **Aprendizaje:** aprobar un artefacto, autorizar una plantilla, demostrar rendimiento y fijar un default son cuatro decisiones distintas. La velocidad profesional viene de reutilizar evidencia y capas verificadas, no de omitir criterio creativo.
- **Pendiente:** producir el máster social SDR antes de publicar VIDEO-01, capturar datos comparables reales y construir la consola de revisión y el índice semántico de activos.

### 2026-09-25 — Se completa el lote VIDEO-02 a VIDEO-05 con cuatro familias medibles

- **Petición:** cerrar VIDEO-02 con las correcciones aprendidas y continuar de forma autónoma hasta entregar VIDEO-03, VIDEO-04 y VIDEO-05, midiendo tiempos y conservando variación creativa.
- **Punto de partida:** VIDEO-02 requería preservar color original, corregir la máscara alrededor del sujeto y reposacabezas, ampliar el título y evitar overlays o transiciones que taparan caras; VIDEO-03–05 todavía no tenían proyecto final.
- **Cambio:** VIDEO-02 quedó en V3; VIDEO-03–05 recibieron selección de toma, cortes protegidos, velocidad 1.04×, voz normalizada, sistema visual propio, B-roll con zonas seguras, SFX, captions y proyecto HyperFrames editable. Las familias T03–T05 pasaron de planificadas a candidatas del banco.
- **Motivo:** acelerar el lote reutilizando controles técnicos y componentes, pero variar estructura, metáfora y lenguaje visual para poder probar aceptación real sin convertir una sola plantilla en fórmula universal.
- **Archivos:** `VIDEO-02/VIDEO-02_REVISION_v3.mp4`, `VIDEO-03/VIDEO-03_REVISION_v2.mp4`, `VIDEO-04/VIDEO-04_REVISION_v1.mp4`, `VIDEO-05/VIDEO-05_REVISION_v1.mp4`, sus proyectos editables, manifiestos, resúmenes y `Serie-IA-Negocios-10-Videos/REPORTE_PRODUCCION_VIDEO_02_A_05.md`.
- **Validación:** todos los MP4 son 1080×1920, 30 fps, HEVC Main 10, BT.2020 HLG y AAC. Loudness final: VIDEO-02 −16.8, VIDEO-03 −16.4, VIDEO-04 −16.5 y VIDEO-05 −16.7 LUFS. Los renders finales se inspeccionaron en cuatro momentos representativos por video, con rostro, texto, color y transiciones aprobados técnicamente.
- **Resultado:** cuatro videos de revisión listos y cuatro proyectos editables; VIDEO-04 y VIDEO-05 llegaron al primer render completo sin correcciones visuales posteriores. El benchmark limpio de render HDR quedó en aproximadamente 10–11 minutos para piezas de 19–20 s.
- **Aprendizaje:** normalizar voz antes del render, inspeccionar espacios negativos y rostros en el MP4 real, no solapar codificaciones pesadas al medir rendimiento y separar siempre aprobación del artefacto, reutilización de plantilla y rendimiento de publicación.
- **Pendiente:** revisión humana de VIDEO-03–05, autorización explícita de las familias que convenga reutilizar y métricas comparables después de publicar.

### 2026-09-25 — Framework 1.6 conecta revisión, activos, recetas, publicación y cohortes

- **Petición:** implementar todas las optimizaciones útiles para acelerar un lote previsto de 30 videos, verificar profundamente que funcionen y dejar una siguiente ola planificada sin bajar la calidad profesional.
- **Punto de partida:** el framework 1.5 ya protegía aprobaciones, QA, memoria de serie y doble máster, pero revisión por timecode, búsqueda global de recursos, composición modular, empaquetado multicanal y métricas comparables seguían siendo piezas pendientes.
- **Cambio:** se construyeron cinco módulos ejecutables: consola de revisión por delta, índice semántico y antifatiga, compilador de 18 módulos creativos, paquete multicanal fail-closed y registro/cohortes con evidencia. Se añadió atribución creativa reproducible, inspección real del MP4, staging y sellos, escritura CAS/no-clobber, comparabilidad contextual y verificación semántica del reporte.
- **Motivo:** evitar que cada video vuelva a analizar el maestro, regenerar recursos, reinterpretar feedback o rehacer capas ya válidas; al mismo tiempo impedir que datos inventados, hashes copiados o una propuesta no elegida contaminen el aprendizaje.
- **Archivos:** `Framework-Edicion-Social/` versión 1.6.0, especialmente `OPERACION_OPTIMIZACION.md`, `ROADMAP_OPTIMIZACION.md`, `scripts/build_review_packet.py`, `scripts/asset_intelligence.py`, `scripts/compose_recipe.py`, `scripts/build_publish_package.py`, `scripts/performance_cohorts.py`, schemas/templates asociados y `Serie-IA-Negocios-10-Videos/asset-intelligence/`.
- **Validación:** 283/283 pruebas automatizadas pasaron. `validate_framework.py` reportó `OK v1.6.0` con 94 JSON, 107 instancias de esquema, 27 reglas, 18 módulos de receta y 26 hard gates/16 criterios editoriales. El snapshot real del índice validó 139 activos, 237 orígenes, 11 grupos duplicados exactos y nueve usos aprobados; además se normalizaron 11 fechas heredadas a RFC 3339.
- **Resultado:** el flujo de los videos siguientes puede preparar blueprint, recursos y recetas en paralelo; revisar cambios por capa; construir derivados solo desde un SDR aprobado; y aprender únicamente cuando existan publicación, evidencia y cohortes compatibles. No se creó ni fingió una publicación o cohorte real.
- **Aprendizaje:** automatizar bien significa también saber cuándo abstenerse. Un paquete local no es una publicación, un hash no autentica una cuenta, una métrica aislada no demuestra causalidad y una receta propuesta no merece crédito hasta que una persona la elija.
- **Pendiente:** aplicar el flujo a los siguientes videos, recoger mediciones reales de tiempo y aceptación, y ejecutar la ola 1.7 en el orden definido por el roadmap.

### 2026-09-25 — El radar detecta Shorts Series sin convertirlo en regla

- **Petición:** ejecutar el radar diario de edición social para detectar cambios oficiales o señales recientes aplicables al lote, con Ecuador como prioridad y LATAM como proxy, sin confundir novedad con causalidad.
- **Punto de partida:** la observación del 24 de septiembre ya registraba la edición conversacional, las pruebas A/B de hasta tres cortes y el cambio de Content ID para Shorts de 61 a 179 segundos.
- **Cambio:** se añadió una observación diaria separada y una fuente oficial para Shorts Series, que permite organizar Shorts en temporadas y episodios, incorporar miniaturas personalizadas y habilitar reproducción secuencial. El mismo anuncio confirma que YouTube empezará a recomendar publicaciones de comunidad dentro del feed de Shorts en web y móvil; se registró como superficie de apoyo independiente. La deduplicación excluyó los tres cambios ya documentados el día anterior.
- **Motivo:** un lote de 30 videos puede beneficiarse de una capa de publicación secuencial, pero solo si los episodios siguen siendo autónomos y la función está disponible en la cuenta; el anuncio no justifica rehacer montajes ni asumir mejoras de retención.
- **Archivos:** `Framework-Edicion-Social/research/observations/2026-09-25.json`, `Framework-Edicion-Social/sources/catalog.json`, `Framework-Edicion-Social/CHANGELOG.md` y `BITACORA_CURSO_EDICION.md`.
- **Validación:** fuente oficial de YouTube publicada el 23 de septiembre de 2026, contrastada con el resumen oficial en español LATAM; disponibilidad específica para Ecuador y la cuenta permanece **por confirmar**. No se encontró una muestra reciente suficiente de IA/tecnología en español y Ecuador para declarar un patrón viral. `validate_framework.py` reportó `OK v1.6.0` con 94 JSON, 107 instancias de esquema, 27 reglas, 15 fuentes y tres archivos de observación.
- **Resultado:** quedan documentadas dos pruebas futuras y reversibles: agrupar solo un subconjunto temáticamente coherente cuando aparezca Shorts Series, y acompañar un episodio con una publicación de contexto o encuesta sin mezclar sus métricas con la retención del Short. Los másteres permanecen intactos y no se promovieron reglas, plantillas ni cambios de render.
- **Aprendizaje:** una función de plataforma puede mejorar la arquitectura de distribución sin cambiar la edición fuente. Las cifras generales de microdramas no deben transferirse como evidencia al nicho de educación sobre IA.
- **Pendiente:** confirmar acceso real en la cuenta, definir el subconjunto y la línea base antes de ejecutar la prueba; registrar métricas locales antes de considerar cualquier recomendación estable.

### 2026-09-25 — VIDEO-01 produce tres perfiles visibles sin rehacer el montaje

- **Petición:** generar desde VIDEO-01 tres videos adicionales para Instagram Reels, TikTok y YouTube Shorts, con diferencias notables basadas en la investigación y conservando la calidad del video ya aprobado.
- **Punto de partida:** existía un mezzanine editorial HDR aprobado por hash, pero no un máster social SDR aprobado ni derivados reales de plataforma. El framework ya definía perfiles, zonas seguras internas y un contrato que impide heredar aprobación entre archivos.
- **Cambio:** el editable de VIDEO-01 pasó a una sola composición con variables de plataforma; se parametrizaron reflow, subtítulos, CTA y zonas seguras para tres salidas. Se renderizó un máster SDR y tres derivados, se normalizó el audio y se conservó sin cambios la toma, los cortes, la voz, el mensaje hablado y los activos aprobados.
- **Motivo:** mostrar diferencias genuinas entre superficies sin triplicar proyectos ni volver a editar el contenido base; así los cambios posteriores de estilo o plataforma se limitan a capas parametrizadas.
- **Archivos:** `VIDEO-01/social-master.mp4`, `VIDEO-01/deliveries/VIDEO-01-instagram-reels.mp4`, `VIDEO-01/deliveries/VIDEO-01-tiktok.mp4`, `VIDEO-01/deliveries/VIDEO-01-youtube-shorts.mp4`, sus preflights, QA visual, `platform-derivatives-manifest.json`, el editable HyperFrames, el resumen de VIDEO-01 y el changelog 1.6.0.
- **Validación:** HyperFrames 0.8.77 completó lint y check sin errores de ejecución o layout; permaneció un aviso de contraste ya documentado en un caption. Los tres MP4 pasaron el preflight técnico con 1080×1920, 30 fps, H.264 High, yuv420p, BT.709 y AAC-LC 48 kHz; midieron −14.3 LUFS y pico de −0.9 dBFS. Se inspeccionaron fotogramas representativos en 0.8, 12.3 y 18.8 s para las tres variantes y no se observó cobertura de ojos o boca.
- **Resultado:** tres candidatos de revisión claramente diferenciados: Instagram más aireado/editorial, TikTok más compacto/directo y Shorts más centrado/serial. Ninguno se declara publicado ni aprobado por el usuario.
- **Aprendizaje:** un único proyecto con variables permite diferencias perceptibles y coherentes por plataforma, reduce el retrabajo y conserva el content lock; la adaptación técnica no sustituye la revisión humana dentro de la interfaz real de cada red.
- **Pendiente:** que el usuario compare y elija; después, realizar la vista previa real ligada al hash del archivo seleccionado y registrar aprobación exacta antes de publicar.

### 2026-09-25 — Los hooks ganan fondo estable y una firma sonora contenida

- **Petición:** añadir fondos a los títulos iniciales de VIDEO-03, VIDEO-04 y VIDEO-05, y comprobar con evidencia si conviene usar más efectos sonoros para captar atención.
- **Punto de partida:** los hooks tenían buena jerarquía y color propio, pero el titular principal estaba directamente sobre la toma; cada video contaba con un solo acento sonoro.
- **Cambio:** cada titular recibió un panel oscuro, redondeado y seguro para el rostro, con borde y acento cromático propios; se añadió una firma de dos sonidos breves sincronizados con la entrada visual durante los primeros 600 ms. Se evitó poblar todo el video con sonidos decorativos.
- **Motivo:** la evidencia audiovisual favorece los puntos de sincronía para orientar atención y la congruencia semántica para memoria, mientras que una estimulación excesiva puede perjudicar el recuerdo. La voz debe seguir siendo la señal dominante.
- **Archivos:** escenas hook e índices editables de VIDEO-03–05; nuevos MP4 V3/V2/V2; `Framework-Edicion-Social/GUIA_SFX_ATENCION.md`, QA, preferencias, feedback y changelog.
- **Validación:** los tres proyectos pasaron HyperFrames con cero errores, cero avisos de layout y tres de tres comprobaciones de contraste temprano. Los hooks se inspeccionaron en fotogramas del MP4 real; mantienen rostros despejados, color original y lectura estable.
- **Resultado:** los inicios comparten una regla de legibilidad y una firma sonora reconocible, pero conservan verde/cian, naranja y magenta como identidades distintas.
- **Aprendizaje:** la mejor práctica no es “más sonidos”, sino uno o dos acentos con causa visible y relación semántica; los efectos adicionales se reservan para cambios de idea o CTA y deben evaluarse con pruebas A/B reales.
- **Pendiente:** medir retención inicial, finalización y replays tras publicar; comparar una variante control sin segundo acento antes de promover la mezcla a default universal.

### 2026-09-25 — Primera propuesta estructural para VIDEO-11

- **Petición:** reinterpretar las propuestas visuales como hojas horizontales con cuatro o cinco capturas representativas de la estructura completa del video: texto, posiciones, tipografías, placas, B-roll y cierre; no como imágenes conceptuales aisladas.
- **Punto de partida:** los videos anteriores compartían tarjetas oscuras redondeadas, acentos neón y diagramas tecnológicos. El usuario aportó cinco capturas de referencia para aclarar el tipo de comparación deseada.
- **Cambio:** se creó una primera lámina horizontal de cinco momentos para VIDEO-11 bajo la dirección `Editorial impreso`, con bloques rectos, fondo de papel, combinación de tipografía condensada, serif y monoespaciada, azul ultramar como acento, alternancia entre presentador, composición tipográfica y el B-roll existente de inundación de contenido.
- **Motivo:** probar una gramática visual realmente distinta sin alterar todavía ningún editable ni producir animación; la propuesta muestra cómo funcionaría el sistema durante todo el video y no solo una portada.
- **Archivos:** `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/OPCION-01_EDITORIAL-IMPRESO/propuesta-01.png`, su fuente SVG y cuatro recursos de apoyo dentro de `assets/`.
- **Validación:** la lámina se renderizó a 3200×1400 px y se inspeccionó visualmente; contiene cinco fotogramas 9:16, textos legibles, rostros despejados y ningún control de la aplicación Fotos. No se validó movimiento porque es una propuesta estática.
- **Resultado:** propuesta 01 lista para revisión visual. No se considera aprobada ni aplicada a VIDEO-11.
- **Aprendizaje:** una propuesta de estilo para una serie debe mostrar la gramática completa —hook, desarrollo, B-roll, remate y cierre— para poder evaluar jerarquía y continuidad, no únicamente color o una imagen central.
- **Pendiente:** la propuesta fue aprobada posteriormente por el usuario; conservarla como dirección disponible y compararla con las siguientes opciones antes de aplicarla al editable.

### 2026-09-25 — Se aprueba Editorial impreso y se crea Internet nativo

- **Petición:** aprobar la primera propuesta y producir una segunda opción apoyada en tendencias actuales de atención y retención.
- **Punto de partida:** `Editorial impreso` mostraba cinco momentos del VIDEO-11 y permanecía pendiente de decisión. La serie necesitaba una alternativa verdaderamente opuesta para comparar públicos y ritmos.
- **Cambio:** se registró la aprobación explícita de la propuesta 01 y se creó la propuesta 02 `Internet nativo / interrupción controlada`, con alto contraste negro–verde ácido, comentario inicial, tipografía de gran escala, multiplicación visual del feed, etiquetas repetidas, un cambio de patrón con rostro y texto, y un cierre de elección A/B.
- **Motivo:** la investigación oficial revisada señala el valor de comunicar temprano, usar texto que active lectura, introducir cambios de escena en giros narrativos, conservar personas reales y variar la creatividad para reducir fatiga. La mayor densidad se usa como sistema de atención y no como decoración constante.
- **Archivos:** `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/OPCION-02_INTERNET-NATIVO/propuesta-02.png`, su fuente SVG y los recursos locales en `assets/`; también se actualizó el estado histórico de la propuesta 01 en esta bitácora.
- **Validación:** la lámina se renderizó a 3200×1400 px, su SVG pasó validación XML y se inspeccionaron los cinco fotogramas para comprobar lectura, rostros, recortes y continuidad. No se afirma retención real porque todavía no existe publicación ni prueba A/B.
- **Resultado:** propuesta 01 aprobada como dirección visual; propuesta 02 lista para revisión, sin aprobación ni aplicación al editable.
- **Aprendizaje:** la estimulación visual debe marcar cambios de significado. Alternar rostro, tipografía, B-roll y participación puede renovar atención sin recurrir a un efecto por palabra.
- **Pendiente:** elegir, ajustar o rechazar la propuesta 02; después decidir si se produce una tercera dirección o se distribuyen las aprobadas entre VIDEO-11 y VIDEO-15.

### 2026-09-25 — Corrección visual y preflight bloqueante para Internet nativo

- **Petición:** conservar la propuesta 02, pero bajar el video de la primera captura para que el banner no cubra la cabeza y completar el cuadro verde detrás de `¿DÓNDE ESTÁS TÚ?` en la tercera; además, convertir estas revisiones en un control previo que evite retrabajo de render y estructura.
- **Punto de partida:** la primera versión de `Internet nativo` tenía la cabeza del presentador demasiado cerca del bloque superior y la franja verde de la tercera captura no alcanzaba el ancho completo del fotograma.
- **Cambio:** se reencuadró hacia abajo al presentador en la captura 01, siguiendo la separación usada en la captura 05; se amplió la franja verde de la captura 03 hasta cubrir íntegramente el cuadro; y el framework incorporó un preflight visual bloqueante que exige revisar sujeto, texto, placas, fondos y padding en una hoja de contacto antes del render completo.
- **Motivo:** resolver los conflictos de composición en una prueba estática cuesta menos que descubrirlos después de construir o renderizar el video, y protege tanto la legibilidad como la presencia del presentador.
- **Archivos:** `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/OPCION-02_INTERNET-NATIVO/propuesta-02.svg`, `propuesta-02.png`, `Framework-Edicion-Social/QA_PROFESIONAL.md`, `Framework-Edicion-Social/templates/qa-scorecard.json`, `Framework-Edicion-Social/CHANGELOG.md` y esta bitácora.
- **Validación:** se regeneró la lámina a 3200×1400 px y se inspeccionaron las cinco capturas. En la captura 01 el bloque titular termina antes de la cabeza y el presentador queda debajo; en la captura 03 la franja verde cubre el ancho del fotograma y contiene el texto completo. El SVG pasó validación XML, el PNG confirmó 3200×1400 px y `validate_framework.py` reportó `OK v1.6.0` con 94 JSON, 109 instancias de esquema, 27 reglas y 26 hard gates/16 criterios editoriales.
- **Resultado:** propuesta 02 corregida y lista para una nueva revisión; no se registra todavía como aprobada.
- **Aprendizaje:** el preflight debe revisar no solo safe zones genéricas, sino relaciones concretas entre cabeza y banners, además del ancho, padding y cierre visual de cada contenedor de texto.
- **Pendiente:** recibir la aprobación o nuevos ajustes de la propuesta 02 antes de convertirla en estructura animada o asignarla a uno de los videos 11–15.

### 2026-09-25 — Se aprueba Internet nativo y se crea Minidocumental humano

- **Petición:** aprobar la propuesta 02 corregida y crear una tercera alternativa visual con el mismo nivel de revisión previa.
- **Punto de partida:** `Editorial impreso` y `Internet nativo / interrupción controlada` ya estaban aprobadas como direcciones visuales diferentes; faltaba una alternativa para un público menos atraído por la alta estimulación y más sensible a claridad, criterio y presencia humana.
- **Cambio:** se registró la aprobación explícita de la propuesta 02 y se creó la propuesta 03 `Minidocumental humano / tensión progresiva`. La lámina muestra cinco momentos: promesa inmediata sobre el presentador, tensión tipográfica sin cifras inventadas, observación sobre el B-roll, regreso al rostro con el punto de vista central y cierre reflexivo que reactiva la pregunta inicial.
- **Motivo:** contrastar una tercera hipótesis de atención: menos ruido visual, mayor cercanía humana, curiosidad progresiva y una conclusión memorable. La dirección recoge recomendaciones oficiales actuales de comunicar valor desde los primeros segundos, usar texto para sostener el seguimiento, conservar los elementos importantes en zonas seguras y experimentar con estructuras diferentes; no se presenta como una garantía de retención.
- **Archivos:** `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/OPCION-03_MINIDOCUMENTAL-HUMANO/propuesta-03.svg`, `propuesta-03.png` y cuatro recursos locales dentro de `assets/`; esta bitácora registra además la aprobación de la propuesta 02.
- **Validación:** el SVG pasó validación XML y la lámina final confirmó 3200×1400 px. Se inspeccionaron los cinco fotogramas después del rasterizado: cabeza y rostro permanecen libres de banners, las placas contienen sus textos completos, el segundo titular del fotograma 04 se redujo antes de entregar para recuperar margen derecho y no se introdujeron métricas factuales no sustentadas.
- **Resultado:** propuestas 01 y 02 aprobadas; propuesta 03 lista para revisión, sin aprobación ni aplicación todavía al editable de VIDEO-11.
- **Aprendizaje:** la variedad útil no exige aumentar siempre la velocidad o la densidad. Una línea serena puede sostener atención mediante promesa, pregunta abierta, evidencia visual y regreso deliberado al rostro.
- **Pendiente:** aprobar, ajustar o rechazar la propuesta 03; después distribuir las direcciones elegidas entre VIDEO-11 y VIDEO-15 sin asumir cuál rendirá mejor hasta contar con datos comparables.

### 2026-09-25 — La pregunta final de la propuesta 03 queda fuera del retrato

- **Petición:** corregir únicamente la quinta captura porque parte de la pregunta entraba en el círculo del presentador y perdía legibilidad.
- **Punto de partida:** el bloque `¿Qué parte solo puedes decir tú?` estaba alineado a la izquierda y su segunda línea alcanzaba el área del retrato circular.
- **Cambio:** la pregunta se centró en un bloque independiente encima del retrato; el círculo se hizo ligeramente más pequeño y se bajó para crear una separación clara.
- **Motivo:** texto y sujeto deben conservar zonas exclusivas; una composición intencional no justifica una intersección que dificulte leer.
- **Archivos:** `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/OPCION-03_MINIDOCUMENTAL-HUMANO/propuesta-03.svg`, `propuesta-03.png` y esta bitácora.
- **Validación:** se regeneró la lámina a 3200×1400 px, el SVG pasó validación XML y la inspección visual confirmó que las dos líneas de la pregunta terminan antes del círculo, sin cubrir el rostro.
- **Resultado:** quinta captura corregida; la propuesta 03 continúa pendiente de aprobación.
- **Aprendizaje:** en cierres con retrato circular, reservar primero la huella completa del círculo y después componer el bloque de texto fuera de ese límite, incluyendo margen respirable.
- **Pendiente:** decisión del usuario sobre la propuesta 03.

### 2026-09-25 — Las notas de producción salen de todos los fotogramas

- **Petición:** retirar de la quinta captura de la propuesta 03 las leyendas `CIERRE / PREGUNTA ABIERTA` y `EL FINAL REACTIVA EL INICIO`, y evitar que notas equivalentes aparezcan en cualquier plantilla.
- **Punto de partida:** algunas etiquetas creadas para explicar la estructura de las láminas habían quedado dentro del área 9:16 y podían confundirse con texto que sí debía aparecer en el video.
- **Cambio:** se retiraron esas dos leyendas de la propuesta 03 y se auditaron las tres propuestas. También salieron de los fotogramas `00:00 · SIN INTRO`, `CAPÍTULO 01`, `OBSERVACIÓN 01`, `04 / 05`, `SATURACIÓN / 01`, `CAPTION`, `CIERRE / IDEA PROPIA`, `00:01 / FRASE CLAVE` y `PATTERN BREAK / 04`; cuando aportaban una idea al espectador se reemplazaron por lenguaje editorial como `CUANDO TODO AUMENTA`, `MIRA LO QUE PASA` o `RESULTADO`. El preflight del framework ahora bloquea metadatos de producción dentro del área renderizable.
- **Motivo:** una hoja de aprobación puede mostrar notas fuera de los fotogramas, pero el contenido dentro del marco vertical debe representar únicamente lo que verá la audiencia.
- **Archivos:** los SVG y PNG de `OPCION-01_EDITORIAL-IMPRESO`, `OPCION-02_INTERNET-NATIVO` y `OPCION-03_MINIDOCUMENTAL-HUMANO`; `Framework-Edicion-Social/QA_PROFESIONAL.md`, `templates/qa-scorecard.json`, `CHANGELOG.md` y esta bitácora.
- **Validación:** las tres láminas se regeneraron a 3200×1400 px, sus SVG pasaron validación XML y se inspeccionaron visualmente. Las notas de composición permanecen solo fuera de los cinco marcos 9:16; el texto interior es editorial o de participación para el espectador. `validate_framework.py` reportó `OK v1.6.0` con 94 JSON, 109 instancias de esquema, 27 reglas y 26 hard gates/16 criterios editoriales.
- **Resultado:** las tres propuestas quedan limpias de metadatos de producción dentro del video; sus direcciones visuales no cambiaron.
- **Aprendizaje:** distinguir siempre entre `texto de audiencia` y `metadato de producción`; la posición dentro o fuera del marco renderizable es parte del contrato, no un detalle de acabado.
- **Pendiente:** aplicar este gate a toda nueva propuesta y a los editables de VIDEO-11–15 antes del primer render completo.

### 2026-09-25 — El repertorio llega a cinco estructuras visuales

- **Petición:** crear las dos propuestas faltantes para completar un repertorio de cinco plantillas, conservando todas las observaciones acumuladas sobre protección del rostro, contenedores completos, legibilidad y ausencia de notas de producción dentro del video.
- **Punto de partida:** existían `Editorial impreso`, `Internet nativo / interrupción controlada` y `Minidocumental humano / tensión progresiva`. Hacían falta dos lenguajes claramente distintos para ampliar la comparación entre públicos.
- **Cambio:** se creó la propuesta 04 `Sistema claro / decisión visual`, orientada a un público analítico mediante problema, mecanismo, comparación, ventaja humana y filtro práctico. También se creó la propuesta 05 `Cómic pop / diálogo directo`, orientada a un público más expresivo mediante preguntas, globos, reacción, contraste y reto participativo. Cada dirección contiene cinco fotogramas verticales dentro de una sola lámina horizontal.
- **Motivo:** disponer de variedad real —editorial, nativa, documental, analítica y pop— permite probar hipótesis de conexión diferentes sin confundir un cambio de color con una estructura nueva.
- **Archivos:** `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/OPCION-04_SISTEMA-CLARO/` y `OPCION-05_COMIC-POP/`, con sus SVG, PNG y recursos locales; esta bitácora.
- **Validación:** ambas láminas se rasterizaron a 3200×1400 px, sus SVG pasaron validación XML y se inspeccionaron a resolución original. En la propuesta 04 se reemplazó antes de entregar un recorte parcial del presentador en el quinto fotograma por un cierre tipográfico limpio. En ambas, cabeza y rostro quedan libres, los textos permanecen dentro de sus contenedores y solo aparece lenguaje destinado al espectador dentro de los marcos 9:16; una búsqueda específica confirmó ausencia de timecodes, `pattern break`, `caption`, nombres numerados de capítulo/observación y otras notas prohibidas.
- **Resultado:** repertorio de cinco direcciones completo; propuestas 04 y 05 listas para revisión y todavía no aprobadas ni aplicadas a los editables de VIDEO-11–15.
- **Aprendizaje:** una familia de opciones es útil cuando cada una cambia la lógica de lectura y el público probable, no solo la paleta. El preflight estático sigue siendo el punto correcto para corregir recortes y jerarquías antes de producir movimiento.
- **Pendiente:** recibir aprobación o ajustes para las propuestas 04 y 05 y después decidir cómo distribuir las cinco direcciones entre VIDEO-11 y VIDEO-15.

### 2026-09-25 — Cinco hipótesis nuevas amplían públicos sin etiquetar personas

- **Petición:** investigar y crear cinco plantillas adicionales que cubran motivaciones, arquetipos, personalidades y enfoques de comunicación distintos, buscando mayor potencial de atención y difusión; archivar tanto el razonamiento como un sistema para medir resultados posteriores.
- **Punto de partida:** existían cinco direcciones visuales con diferencias de ritmo y lenguaje, pero no una segunda batería diseñada expresamente como hipótesis comparables de identificación, evidencia, debate, identidad y participación. Tampoco había un registro único para relacionar las diez plantillas con aprobación y métricas futuras.
- **Cambio:** se documentó la investigación y se crearon las propuestas 06 `Confesión cruda`, 07 `Caso abierto`, 08 `Duelo de ideas`, 09 `Manifiesto de autor` y 10 `Reto de autor`. Se añadió un plan de medición a 24 h, 72 h, 7 días y 28 días, y un registro JSON con ángulo, motivación, arquetipo usado como hipótesis, métrica principal y estado de aprobación de T01–T10.
- **Motivo:** ampliar la variedad mediante mecanismos psicológicos y narrativos realmente diferentes, sin usar estereotipos como diagnósticos ni presentar la PNL como ciencia predictiva. La evidencia consultada favorece hook temprano, historia auténtica, curiosidad, contraste, participación y experimentación; ninguna fuente permite garantizar viralidad.
- **Archivos:** `PROPUESTAS-ESTRUCTURA/INVESTIGACION_ANGULOS_06_A_10.md`, `PLAN_MEDICION_PLANTILLAS_01_A_10.md`, `REGISTRO_PLANTILLAS_01_A_10.json` y las carpetas `OPCION-06_CONFESION-CRUDA` a `OPCION-10_RETO-DE-AUTOR`, cada una con SVG, PNG y activos locales; esta bitácora.
- **Validación:** los cinco SVG pasaron validación XML y las cinco láminas se rasterizaron a 3200×1400 px. Se inspeccionaron los 25 fotogramas a resolución original y se corrigieron antes de entregar desbordes en titulares de las propuestas 07–10. Los rostros quedan libres, los contenedores están completos y el interior de los marcos solo contiene lenguaje destinado a la audiencia. El registro JSON pasó validación sintáctica.
- **Resultado:** cinco propuestas nuevas listas para revisión, investigación archivada y un protocolo preparado para incorporar resultados reales sin declarar ganadores prematuramente. Ninguna de las propuestas 06–10 se considera todavía aprobada ni publicada.
- **Aprendizaje:** llegar a públicos diversos no consiste en etiquetar a cada persona, sino en variar la promesa y la experiencia: identificación, certeza, contraste, identidad y participación. La viralidad se trata como resultado medible y no como propiedad garantizada del diseño.
- **Pendiente:** aprobar o ajustar las propuestas 06–10, asignarlas a videos concretos y registrar métricas comparables después de publicación; mantener T03 como `por confirmar` y T04–T05 como pendientes hasta que exista evidencia explícita de aprobación.

### 2026-09-25 — Lote VIDEO-06 a VIDEO-10: cinco familias, HDR preservado y captions sin cruces

- **Petición:** ejecutar de principio a fin `PROMPT_EDITAR_VIDEO_06_A_10.md`, entregar cinco MP4 de revisión y cinco proyectos HyperFrames editables, validar el material real y trabajar sin detenerse en decisiones intermedias.
- **Punto de partida:** existía un MOV HLG de 467,145 s con los cinco videos, planes y recursos preliminares, pero no había toma seleccionada para VIDEO-09, editables completos ni renders finales. El segundo stream de audio usa `apac` y no es decodificable por la herramienta disponible; el stream AAC estéreo sí lo es.
- **Cambio:** se transcribió el maestro una vez, se amplió el parser para claquetas sin la palabra `inicio`, se seleccionaron cinco tomas, se construyeron montajes de voz a 1,04× con protección aproximada de 180 ms, y se crearon cinco editables por capas con hooks y familias diferentes. Se renderizaron las revisiones HDR, se midieron los MP4, se extrajeron fotogramas reales y se corrigió un cruce de captions de 50 ms detectado en VIDEO-08, aplicando la misma prevención a los cinco proyectos y regenerando sus revisiones. VIDEO-09 recibió un postproceso de loudness con copia intacta del video.
- **Motivo:** entregar piezas profesionales, rápidas pero comprensibles, con color fuente preservado, variación creativa real y evidencia verificable. El defecto de captions demostró que un check general y cinco snapshots pueden no coincidir con un límite de transición de uno o dos cuadros.
- **Archivos:** `Serie-IA-Negocios-10-Videos/VIDEO-06` a `VIDEO-10`, sus editables `editable-hyperframes-video-XX/`, MP4 vigentes V2/V2/V2/V6/V2, `qa/`, resúmenes, métricas y manifiestos; `00-INGESTA/take-map-06-10.json`; `REPORTE_PRODUCCION_VIDEO_06_A_10.md`; memoria de serie; banco de plantillas; parser, tests, QA, preferencias, feedback y changelog de `Framework-Edicion-Social/`.
- **Validación:** los cinco proyectos pasaron lint/check de HyperFrames sin errores de runtime; los cinco MP4 decodificaron completos y son 1080×1920, 30 fps, HEVC Main 10, BT.2020/HLG y AAC 48 kHz. Midieron entre −16,63 y −16,96 LUFS, con picos entre −1,48 y −1,69 dBTP. Se inspeccionaron 25 fotogramas generales y cinco límites críticos de captions; el algoritmo confirmó cero solapes entre cues. El framework pasó 7/7 pruebas del parser y `validate_framework.py` reportó 94 JSON, 110 instancias de esquema y cero errores. Ante la observación de palidez en los PNG, la comparación con el original mostró coincidencia de piel y camiseta; el MP4 no añadió desaturación y conserva las etiquetas HDR.
- **Resultado:** quedan listos para revisión humana VIDEO-06 V2, VIDEO-07 V2, VIDEO-08 V2, VIDEO-09 V6 y VIDEO-10 V2, además de cinco proyectos editables, trazabilidad, hashes y familias candidatas. No se publicaron ni se declararon aprobados.
- **Aprendizaje:** los cruces breves de opacidad en captions deben revisarse justo en sus límites sobre el MP4 real; una hoja general puede omitirlos. Los PNG extraídos directamente de HLG no son una referencia suficiente de apariencia SDR, por lo que la fidelidad se comprueba contra el original y las etiquetas del archivo. El parser puede tolerar `video N toma N` sin `inicio`, pero debe bajar confianza y conservar la advertencia.
- **Pendiente:** escucha humana completa y aprobación creativa de los cinco artefactos exactos. VIDEO-09 mantiene una excepción documentada porque falta su claqueta inicial; la identidad se resolvió por secuencia, tema y marcador final, no por escucha humana. Ninguna familia se promueve ni se declara ganadora sin aprobación y métricas comparables.

### 2026-09-25 — Diez mundos visuales rompen la repetición de las plantillas

- **Petición:** crear diez propuestas adicionales, cada una completamente distinta de las demás y de las estructuras previas en percepción visual, evitando que la colección empezara a parecer una sucesión de cambios de color.
- **Punto de partida:** T01–T10 ya cubrían editorial impreso, Internet nativo, minidocumental, sistema analítico, cómic, confesión, investigación, debate, manifiesto y reto. La variedad estratégica era amplia, pero varias compartían tarjetas, placas y jerarquías tipográficas similares.
- **Cambio:** se construyeron T11 `Realidad deformada`, T12 `Prompt Playground`, T13 `Explorecore`, T14 `Texture Check`, T15 `Notes App Chic`, T16 `Opt-Out`, T17 `Drama Club`, T18 `Rótulo popular`, T19 `Pixel Quest` y T20 `Jardín de ideas`. Cada dirección cambia metáfora, material, tipografía, organización espacial, ritmo sugerido y mecanismo de participación. También se creó un generador reproducible, una investigación de diversidad, un plan de medición y un registro estructurado.
- **Motivo:** la diferenciación visual útil necesita cambiar la lógica de percepción, no únicamente la paleta. La investigación actual apunta simultáneamente hacia imperfección humana, mundos surrealistas, interfaces retro, tactilidad, calma, teatralidad, cultura cotidiana y participación; se usan como rutas creativas y no como garantías de rendimiento.
- **Archivos:** `PROPUESTAS-ESTRUCTURA/generar_propuestas_11_20.js`, las carpetas `OPCION-11_REALIDAD-DEFORMADA` a `OPCION-20_JARDIN-DE-IDEAS`, `INVESTIGACION_DIVERSIDAD_VISUAL_11_A_20.md`, `PLAN_MEDICION_PLANTILLAS_11_A_20.md`, `REGISTRO_PLANTILLAS_11_A_20.json` y esta bitácora.
- **Validación:** se renderizaron diez láminas de 3200×1400 px y se inspeccionaron los 50 fotogramas a resolución original. El primer preflight detectó desbordes tipográficos en las propuestas 11–20; se corrigieron tamaños y alineaciones, se regeneraron todas las fuentes y se repitió la inspección. Los rostros quedan libres, los textos permanecen dentro de sus marcos y no aparecen notas de producción dentro de las pantallas 9:16. Los SVG y JSON pasaron validación sintáctica.
- **Resultado:** diez sistemas visuales adicionales listos para revisión. T11–T20 permanecen pendientes de aprobación; todavía no se consideran aplicados, animados, publicados ni medidos.
- **Aprendizaje:** para controlar la fatiga creativa conviene registrar la silueta, la superficie, la tipografía, la geometría, el ritmo y el CTA de cada plantilla. Si dos direcciones coinciden en cuatro o más de esas dimensiones, deben replantearse antes de animar.
- **Pendiente:** recibir aprobación o correcciones de T11–T20, elegir qué mundos pasarán a los videos 11–15 y registrar resultados reales en las ventanas de 24 h, 72 h, 7 días y 28 días.

### 2026-09-25 — La segunda captura de Realidad deformada gana contraste

- **Petición:** corregir únicamente la segunda captura de la propuesta 11 porque las letras blancas no se distinguían bien; el usuario indicó que el resto estaba perfecto.
- **Punto de partida:** la frase `Una frase esperada se olvida.` aparecía en blanco directamente sobre una superficie rosa saturada, con contraste insuficiente en la vista general.
- **Cambio:** se añadió una placa oscura redondeada detrás de la frase y se reforzó ligeramente el peso de sus dos líneas, sin cambiar el texto, la composición de las otras cuatro capturas ni la dirección visual de la propuesta. La corrección quedó aplicada tanto en el SVG final como en el generador reutilizable.
- **Motivo:** asegurar legibilidad inmediata incluso en pantallas pequeñas, compresión de plataforma o brillo alto, sin perder la voz editorial de la plantilla.
- **Archivos:** `PROPUESTAS-ESTRUCTURA/generar_propuestas_11_20.js`, `OPCION-11_REALIDAD-DEFORMADA/propuesta-11.svg`, `OPCION-11_REALIDAD-DEFORMADA/propuesta-11.png` y esta bitácora.
- **Validación:** el SVG pasó validación XML, la lámina se regeneró a 3200×1400 px y se inspeccionó a resolución original. La placa contiene completamente ambas líneas, mantiene aire alrededor del texto y no invade los titulares ni las formas superior e inferior. Una búsqueda específica confirmó que no se introdujeron notas internas de producción.
- **Resultado:** propuesta 11 corregida en su segunda captura; las demás capturas se conservaron sin cambios. La aceptación final del ajuste queda pendiente de confirmación visual del usuario.
- **Aprendizaje:** el blanco no garantiza legibilidad sobre colores saturados; cuando la superficie varía o compite con el texto, un contenedor de alto contraste es más robusto que depender solo del peso tipográfico.
- **Pendiente:** recibir confirmación del ajuste de contraste antes de promover T11 a estado aprobado en el registro de plantillas.

### 2026-09-25 — VIDEO-06 a VIDEO-10 recuperan una capa SFX perceptible

- **Petición:** conservar los cinco videos, valorados por el usuario como excelentes, y corregir la única observación: los efectos de sonido no se percibían.
- **Punto de partida:** cada editable contenía solo dos SFX con `data-volume=".20"`. Los activos usados medían desde aproximadamente −10 hasta −24 dBFS de pico antes de esa reducción, por lo que varios terminaban entre unos −24 y −38 dBFS y quedaban ocultos por la voz.
- **Cambio:** cada video pasó a cuatro eventos sonoros breves y semánticos, alineados con la entrada, el cambio a concepto, el bloque de apoyo y el CTA. Se reutilizaron efectos aprobados de ataque suave y cálido; las ganancias quedaron entre 0,62 y 0,82 según el nivel de cada archivo. Se generaron VIDEO-06 V3, VIDEO-07 V3, VIDEO-08 V3, VIDEO-09 V7 y VIDEO-10 V3. No se cambió ninguna imagen, el montaje visual ni el tratamiento de color.
- **Motivo:** la presencia de un archivo de audio en el timeline no demuestra audibilidad. La mezcla debe calibrarse con el nivel real de la fuente y comprobarse en el MP4 final, manteniendo la voz como prioridad.
- **Archivos:** los cinco `index.html` dentro de `VIDEO-06` a `VIDEO-10`, los cinco MP4 nuevos, manifiestos de render, resúmenes, métricas, reporte del lote, script de auditoría, perfil de preferencias, registro de feedback, changelog del framework y esta bitácora.
- **Validación:** los cinco proyectos pasaron `hyperframes check` sin errores de runtime; los cinco MP4 decodificaron completos y conservan 1080×1920, 30 fps, HEVC Main 10, BT.2020/HLG y AAC estéreo a 48 kHz. La medición final quedó entre −16,63 y −17,04 LUFS, con picos entre −1,43 y −1,64 dBTP. VIDEO-09 recibió normalización posterior con copia intacta del video. Los cuatro SFX por pieza están declarados con IDs y tiempos distintos en los editables.
- **Resultado:** cinco revisiones nuevas listas para escuchar, con una firma de entrada y tres refuerzos narrativos perceptibles. Las versiones anteriores se conservaron y no se publicó ningún archivo.
- **Aprendizaje:** una ganancia fija —por ejemplo 20 % o incluso un rango recomendado— no funciona igual para fuentes con picos muy distintos. El gate correcto combina intención semántica, calibración por nivel de origen, prioridad de voz y verificación del render final.
- **Pendiente:** escucha del usuario sobre los cinco artefactos exactos; ajustar solo si algún acento resulta todavía bajo o demasiado presente.

### 2026-09-25 — La colección llega a treinta con una base de diseño inclusivo

- **Petición:** ampliar el repertorio de veinte a treinta plantillas antes de crear el Manual Maestro, considerando a personas con TDAH, autismo, dificultades de lectura y discapacidades visuales. El usuario también confirmó con `Excelente` la corrección anterior de T11.
- **Punto de partida:** existían treinta conceptos potenciales solo hasta T20; las reglas de accesibilidad estaban dispersas entre el preflight visual y decisiones puntuales. No existía una colección dedicada a necesidades de acceso ni un estándar transversal para todas las plantillas.
- **Cambio:** se investigaron WCAG 2.2, la guía cognitiva COGA de W3C, requisitos de descripción visual, barreras de baja visión y orientación de GOV.UK. Se evitó diseñar por diagnósticos rígidos y se construyeron T21 `Ruta de foco`, T22 `Camino predecible`, T23 `Pausa sensorial`, T24 `Contraste XL`, T25 `Forma + señal`, T26 `Lectura fácil`, T27 `Subtítulo primero`, T28 `Audio guía`, T29 `Ritmo y recuerdo` y T30 `Múltiples puertas`. También se creó un estándar común para T01–T30, un plan de medición, un registro estructurado y un generador reproducible. T11 pasó de pendiente a aprobada con evidencia explícita.
- **Motivo:** ampliar el acceso sin asumir que todas las personas con una misma condición comparten preferencias. La práctica elegida combina diseño universal para las treinta plantillas con propuestas especializadas por necesidad observable: enfoque, predictibilidad, baja estimulación, contraste, redundancia visual, lenguaje, subtítulos, descripción, memoria y multimodalidad.
- **Archivos:** `PROPUESTAS-ESTRUCTURA/generar_propuestas_21_30.js`; carpetas `OPCION-21_RUTA-DE-FOCO` a `OPCION-30_MULTIPLES-PUERTAS`; `INVESTIGACION_DISENO_INCLUSIVO_21_A_30.md`; `ESTANDAR_ACCESIBILIDAD_BASE_01_A_30.md`; `PLAN_MEDICION_PLANTILLAS_21_A_30.md`; `REGISTRO_PLANTILLAS_21_A_30.json`; actualización de `REGISTRO_PLANTILLAS_11_A_20.json`; y esta bitácora.
- **Validación:** el primer render reveló que Quick Look escalaba el lienzo horizontal y cortaba los últimos marcos; se corrigió la fuente a un lienzo cuadrado de trabajo y se regeneraron los PNG recortados. Los diez SVG pasaron validación XML, los dos registros modificados pasaron validación JSON y las diez imágenes miden 3200×1400 px. Se inspeccionaron las cincuenta pantallas a resolución original y como hoja de contacto: los textos permanecen dentro de sus contenedores, los rostros están libres, las señales de T25 no dependen solo del color y no aparecen timecodes ni notas internas de producción.
- **Resultado:** el proyecto contiene treinta carpetas de plantilla, treinta SVG y treinta PNG. T21–T30 quedan listas para revisión, todavía pendientes de aprobación, animación, publicación y prueba con participantes. T11 queda documentada como aprobada.
- **Aprendizaje:** accesibilidad no equivale a crear una estética separada “para un diagnóstico”. Lo más robusto es una base universal, variantes que resuelvan barreras específicas y pruebas con personas; las métricas de plataforma no permiten inferir neurodivergencia o discapacidad.
- **Pendiente:** recibir correcciones o aprobación de T21–T30 y después construir el Manual Maestro modular de T01–T30 con reglas de extensión para piezas de 15, 30 y 60 segundos.

### 2026-09-25 — Ficha técnica de dos referencias Santi Web (gramática motion-graphics sin presentador)

- **Petición:** analizar en profundidad dos videos de referencia de `Referencias Santi Web ` con la plantilla de 19 secciones (resumen, técnica, narrativa, guion, shot list, arte, tipografía, motion, ritmo, transiciones, audio, recursos, plantilla, parámetros, esenciales, comparación, fórmula, prompt y JSON), diferenciando dato verificado, estimación y no disponible, con timecodes.
- **Punto de partida:** dos grabaciones de pantalla de iPhone (134 MB y 113 MB) reproduciendo Instagram de @santitapias__; no son los másteres originales. No existía análisis previo de este autor.
- **Cambio:** se midieron specs con ffprobe (A: 74,662 s; B: 61,745 s; 1320×2868 HEVC 60 fps; voz −17,1/−16,9 dB RMS), se extrajeron 25 fotogramas, se transcribió con Whisper large-v3 (A: 237 palabras ≈197 ppm; B: 148 ≈150 ppm), se detectaron ~18 cambios de escena y se redactó `Referencias Santi Web /FICHA_TECNICA_SANTI_A_B.md` (19 secciones + JSON válido). Hallazgo clave: serie motion-graphics sin presentador (fondo papel cuadriculado, tarjetas negras, acento naranja, serif gigante + mono, beats 4–6 s, voz continua sin pausas).
- **Motivo:** dotar al equipo de una gramática reproducible para piezas originales con lenguaje similar, sin copiar marcas, personaje, textos ni audios del autor.
- **Archivos:** `Referencias Santi Web /FICHA_TECNICA_SANTI_A_B.md`, `_analisis/frames_A/`, `_analisis/frames_B/`, `_analisis/audio/trans_A.txt`, `trans_B.txt`; esta bitácora.
- **Validación:** 19/19 secciones presentes, JSON verificado por parseo, cada observación con timecode y marca [V]/[E]/[ND]; música y SFX declarados por confirmar por no haberse hecho escucha crítica.
- **Resultado:** ficha lista para usar como brief de producción de piezas originales.
- **Aprendizaje:** una grabación de pantalla impone un techo metodológico (specs = grabación, no máster); debe advertirse por escrito para no presentar fps/bitrate como decisiones del autor.
- **Pendiente:** escucha crítica de música/SFX y confirmación de 3 frases dudosas de la transcripción B; decidir si esta gramática se convierte en familia del framework.

### 2026-09-25 — Audio Santi verificado con análisis de señal propio (F0, stereo, transitorios)

- **Petición:** completar todo el análisis sin depender de escucha humana: instalar lo necesario y medir música, BPM, SFX y voz.
- **Punto de partida:** §11 de la ficha marcaba música y SFX por confirmar; el sistema no puede reproducir audio.
- **Cambio:** se montó `.venv` del proyecto con numpy/scipy y se escribió `/tmp/analisis_santi.py` (flujo espectral, autocorrelación de F0 y tempo, mid/side, dinámica). Resultados volcados en §10/§11/§16/§19 de la ficha: F0 mediana 151/152 Hz; A stereo (−21,3 dB) vs B mono (−43,8 dB); 30/31 transitorios con timecode (picos A 69,27 ×11,5 en CTA, B 50,20 ×14,8 en demo); pulso medido = tasa de habla (BPM musical declarado ND con honestidad).
- **Motivo:** cerrar la brecha de evidencia sin inventar timbres ni géneros.
- **Archivos:** `.venv/`, `Referencias Santi Web /FICHA_TECNICA_SANTI_A_B.md` (§10/§11/§16/§19), esta bitácora. Script reutilizable en `/tmp/analisis_santi.py` (no se commitea por ser prueba desechable).
- **Validación:** JSON re-parseado OK (18 claves); números procedentes del script, no de estimación.
- **Resultado:** ficha de audio completa salvo timbre de SFX y género musical, que exigen oído humano.
- **Aprendizaje:** un análisis de onsets sobre mezcla con voz continua detecta *dónde* hay acentos pero no *qué* suenan; el negativo (sin pulso musical separable) también es evidencia y debe registrarse.
- **Pendiente:** escucha humana solo para timbre/género; 3 frases dudosas de trans_B.

### 2026-09-25 — Correcciones T22/T30 y catálogo maestro navegable de las treinta plantillas

- **Petición:** corregir exclusivamente la captura 03 de T22 y las capturas 01 y 03 de T30, donde algunos textos salían de sus figuras; después comprobar que las treinta propuestas estuvieran documentadas y construir un HTML permanente para consultarlas ordenadamente con todas sus características.
- **Punto de partida:** existían treinta tableros, tres registros por lotes y documentos de investigación y medición, pero la información no estaba normalizada en una sola fuente. T22 y T30 necesitaban una corrección puntual antes de la aprobación condicionada del lote 21–30.
- **Cambio:** en T22-03, `TU EXPERIENCIA / CAMBIA EL MENSAJE` se recompuso como tres líneas centradas dentro del cuadro blanco. En T30-01 se incorporaron contenedores completos para el titular y el cierre, y se redistribuyeron los cuatro módulos; en T30-03 el titular, la onda y el resumen recibieron superficies propias. Se creó `generar_catalogo_01_30.js`, que valida los treinta artefactos y genera una fuente maestra JSON, una auditoría Markdown y un catálogo HTML local con orden T01–T30, buscador, filtros por colección, estados de aprobación, acceso al tablero completo y fichas desplegables de concepto, ángulo, motivación, lenguaje visual, estructura, extensión, accesibilidad, usos y métrica.
- **Motivo:** impedir que texto y contenedor se separen durante la construcción, y evitar que el concepto de una plantilla dependa de la memoria del chat. Una sola fuente normalizada permite extender piezas de 30–60 segundos sin deformar su lógica y regenerar el visor sin duplicar información manualmente.
- **Archivos:** `PROPUESTAS-ESTRUCTURA/generar_propuestas_21_30.js`; SVG y PNG de `OPCION-22_CAMINO-PREDECIBLE` y `OPCION-30_MULTIPLES-PUERTAS`; `REGISTRO_PLANTILLAS_21_A_30.json`; `generar_catalogo_01_30.js`; `CATALOGO_MAESTRO_01_A_30.json`; `AUDITORIA_DOCUMENTACION_01_A_30.md`; `CATALOGO-PLANTILLAS/index.html`; y esta bitácora.
- **Validación:** el generador de propuestas y el del catálogo pasaron comprobación sintáctica; los SVG corregidos pasaron `xmllint`; ambos PNG miden 3200×1400 px; la fuente maestra contiene 30 fichas y todos sus artefactos existen. Se revisó el HTML en navegador local en escritorio y 390×844 px: carga las treinta tarjetas, muestra diez al filtrar Diseño inclusivo, la búsqueda `audio` devuelve tres coincidencias, las fichas se expanden correctamente y no se registraron errores ni advertencias de consola. La inspección visual de T22 y T30 confirmó que los textos corregidos quedan dentro de sus figuras.
- **Resultado:** las correcciones están incorporadas y el proyecto dispone de una biblioteca navegable y una fuente maestra para mantener las treinta propuestas. Se conservaron los estados históricos según evidencia; T21–T30 siguen pendientes hasta que el usuario confirme visualmente estas correcciones.
- **Aprendizaje:** una biblioteca de plantillas útil necesita tres capas conectadas: tablero visual, contrato documental y visor operativo. La regla de extensión debe vivir junto al concepto para que aumentar la duración no convierta la plantilla en una secuencia genérica.
- **Pendiente:** recibir confirmación final de T22 y T30; después actualizar el estado de aprobación del lote que el usuario apruebe y comenzar la asignación de plantillas a nuevos guiones o videos de 30–60 segundos.

### 2026-09-25 — Las treinta plantillas quedan aprobadas y el catálogo aprende a buscar por intención

- **Petición:** registrar como aprobadas las treinta plantillas y permitir búsquedas útiles por necesidades como marketing, ventas, productos o una frase escrita libremente.
- **Punto de partida:** el catálogo filtraba por colección y coincidencia textual literal. Solo T01, T02 y T11 figuraban como aprobadas; el resto conservaba estados pendientes o por confirmar, aunque las correcciones finales de T22 y T30 ya habían sido entregadas.
- **Cambio:** se registró la aprobación explícita global de T01–T30 en los tres registros y en la fuente maestra. Cada plantilla recibió cinco temas de aplicación. El HTML incorporó búsqueda inteligente local con normalización de acentos, palabras vacías, sinónimos e intenciones para marketing, ventas, productos, IA, educación, storytelling, accesibilidad y servicios; ordena coincidencias por relevancia, admite frases como `quiero vender un producto`, ofrece accesos rápidos y muestra etiquetas temáticas en cada ficha.
- **Motivo:** el usuario no debería necesitar recordar el nombre de una plantilla. El sistema debe partir del objetivo comercial o comunicacional y recomendar direcciones visuales compatibles, sin enviar información a un servicio externo ni exigir una API.
- **Archivos:** `PROPUESTAS-ESTRUCTURA/generar_catalogo_01_30.js`; `CATALOGO-PLANTILLAS/index.html`; `CATALOGO_MAESTRO_01_A_30.json`; `AUDITORIA_DOCUMENTACION_01_A_30.md`; `REGISTRO_PLANTILLAS_01_A_10.json`; `REGISTRO_PLANTILLAS_11_A_20.json`; `REGISTRO_PLANTILLAS_21_A_30.json`; y esta bitácora.
- **Validación:** los cuatro JSON pasaron validación sintáctica; los tres registros contienen únicamente `approved` y la fuente maestra contiene treinta fichas aprobadas con cinco temas cada una. En navegador, `marketing` devolvió 11 recomendaciones, `quiero vender un producto` devolvió 14 y priorizó T07 por combinar ventas y productos, e `IA` devolvió únicamente T12 sin falsos positivos por coincidencias parciales. Se comprobó además el orden por relevancia, los accesos rápidos y la presentación visual del nuevo buscador.
- **Resultado:** las treinta plantillas quedan oficialmente aprobadas y el catálogo ya funciona como recomendador temático local para seleccionar una estructura desde el objetivo del próximo guion.
- **Aprendizaje:** para una colección pequeña y curada, una taxonomía explícita con sinónimos ofrece resultados transparentes, privados y mantenibles. Una IA externa solo será necesaria si más adelante se quiere interpretar briefs extensos, aprender de métricas publicadas o recomendar combinaciones entre plantillas.
- **Pendiente:** cuando se incorporen resultados reales de publicaciones, añadir al ranking una segunda capa de relevancia basada en desempeño comparable, sin confundir correlación con causalidad.

### 2026-09-25 — Auditoría independiente corrige cadencia, conteo y alcance de evidencia en Santi Web

- **Petición:** auditar de forma independiente los dos MP4 de `Referencias Santi Web ` y la ficha de Muse en dos pasadas, contrastar las transcripciones y convertir la gramática confirmada en reglas, blueprint HyperFrames, JSON y prompt de producción futura, sin editar videos ni proyectos existentes.
- **Punto de partida:** existía `FICHA_TECNICA_SANTI_A_B.md` con dos entradas previas en esta bitácora. La ficha contenía metadatos correctos y una lectura creativa útil, pero recomendaba 30 fps, decía haber extraído 25 fotogramas y mezclaba medidas de programa con atribuciones a voz, música o SFX.
- **Cambio:** se selló una primera pasada antes de abrir Muse; se midieron hashes, specs, LUFS, true peak, LRA, silencios, apertura mid/side, cambios visuales y cadencia interna; se generó una transcripción independiente con Whisper.cpp `ggml-base`; luego se auditó Muse afirmación por afirmación. Se creó `AUDITORIA_INDEPENDIENTE_2026-09-25/` con informe, fichas separadas, sistema reutilizable, blueprint HyperFrames, JSON y prompt. No se modificaron los videos, la ficha de Muse, los transcripts ni sus fotogramas.
- **Motivo:** separar evidencia de interpretación y evitar que un informe secundario se convirtiera en contrato de producción sin comprobar. La prioridad fue distinguir parámetros de la captura, parámetros probables del máster y recomendaciones nuevas.
- **Archivos:** `Referencias Santi Web /AUDITORIA_INDEPENDIENTE_2026-09-25/EVIDENCIA_PRIMERA_PASADA.md`; `AUDITORIA_INFORME_MUSE.md`; `FICHA_VIDEO_01.md`; `FICHA_VIDEO_02.md`; `SISTEMA_ESTILO_REUTILIZABLE.md`; `HYPERFRAMES_BLUEPRINT.md`; `style-system.json`; `PROMPT_PRODUCCION_FUTURA.md`; y esta bitácora.
- **Validación:** `ffprobe` confirmó A 74,662086 s y B 61,745329 s, ambas 1320×2868 HEVC Main/BT.709 con captura nominal de 60 fps; EBU R128 midió A −17,0 LUFS/−1,7 dBTP/2,1 LU y B −16,9 LUFS/−1,7 dBTP/3,9 LU. Tres ventanas por video mostraron ≈22,5–24 cambios reales/s, compatibles con una cadencia interna de 24 fps. Se contaron 27 fotogramas preexistentes (15 A, 12 B), no 25. La apertura side/mid de −21,3 dB en A y −43,8 dB en B fue reproducida independientemente. El JSON pasó parseo y los enlaces/archivos requeridos existen. No se hizo escucha humana.
- **Resultado:** la ficha de Muse recibió 72/100: sólida en metadatos, narrativa y sistema visual; parcial en temporalidad y reproducción; débil en atribución de audio. La especificación futura adopta 24 fps, separa macroescenas de eventos visuales, evita imponer “cero pausas” y trata música/SFX/F0 de voz como no verificados sin separación o escucha.
- **Aprendizaje:** una captura a 60 fps puede contener animación producida a otra cadencia; conviene medir cambios entre frames antes de recomendar el frame rate. Un detector de onsets prueba transitorios de mezcla, no la existencia ni el timbre de SFX. Las reglas de serie deben surgir de coincidencias entre piezas, no de rasgos exclusivos de una sola.
- **Pendiente:** escucha humana con auriculares; acceso a los másteres para confirmar 24 fps y exportación; verificación de fuentes/licencias; prueba HyperFrames de 10–15 s sólo cuando el usuario solicite producción. La auditoría no está marcada como aprobada ni publicada.

### 2026-09-25 — Una claqueta permite corregir solo la última frase sin repetir la toma

- **Petición:** añadir una orden verbal para que, cuando el locutor se equivoque únicamente en la última frase, pueda repetirla y continuar sin volver a grabar todo el video; la edición debe escuchar la versión nueva, retirar la anterior y conservar el contexto correcto.
- **Punto de partida:** el protocolo `compact_v1` solo distinguía inicio de toma, aprobación, descarte y fin de sesión. Un error corto obligaba a repetir la toma completa o a resolver manualmente un reinicio sin marcador estructurado.
- **Cambio:** el protocolo pasó a `compact_v2` con `MARCADOR. Corregir, corregir. Última frase.`. La toma permanece abierta; después de la orden se repite la frase completa desde su comienzo y se puede continuar. El parser registra la corrección sin cerrar la toma, guarda rangos de objetivo y reemplazo pendientes, detecta órdenes huérfanas y exige revisión por escucha. El preflight bloquea correcciones sin estado `resolved`; `cut-plan.json` recibió `phrase_corrections` para documentar el reemplazo no destructivo. También se actualizó a diez la expectativa de una prueba del banco de plantillas que había quedado desfasada frente al registro vigente.
- **Motivo:** permitir una grabación más fluida sin confiar ciegamente en la puntuación del reconocimiento de voz. El comienzo de una frase puede no coincidir con un signo automático; por eso el reemplazo se delimita por audio, significado, respiración y continuidad gestual.
- **Archivos:** `Framework-Edicion-Social/scripts/build_take_map.py`; `scripts/preflight_project.py`; pruebas de ambos módulos; schemas y plantillas de `take-map`/`cut-plan`; `FLUJO_PRODUCCION_RAPIDA.md`; `INGESTA_MAESTRA.md`; prompts de ingesta y edición individual; `README.md`; `rules/registry.json`; plantillas versionadas; `CHANGELOG.md`; y esta bitácora.
- **Validación:** las 286 pruebas automatizadas del framework pasaron. `validate_framework.py` reportó `OK v1.6.1` con 94 JSON, 112 instancias validadas, 28 reglas y diez entradas en el banco de plantillas. Las pruebas específicas confirmaron detección de la nueva orden, permanencia de la toma abierta, registro del reemplazo y diagnóstico de una corrección fuera de una toma. No se utilizó metraje real ni se escuchó una grabación con este marcador en esta actualización.
- **Resultado:** el framework puede recibir una corrección parcial inequívoca dentro de una toma y detener la edición si sus límites todavía no fueron verificados. Los mapas históricos `compact_v1` siguen siendo válidos.
- **Aprendizaje:** una orden de rodaje útil debe separar detección automática de decisión editorial. El marcador señala dónde ocurrió la corrección; la escucha determina exactamente qué frase sale y cuál entra.
- **Pendiente:** probar el protocolo con una grabación real, revisar la naturalidad del empalme y ajustar el vocabulario alternativo solo si la transcripción real confunde de forma recurrente la palabra `corregir`.

### 2026-09-25 — Próxima entrega prevista como un maestro con cinco videos

- **Petición:** registrar que la próxima entrega para edición será un solo archivo de video que contendrá cinco videos distintos.
- **Punto de partida:** el framework ya admite varios `VIDEO-NN` dentro de un mismo maestro y utiliza la claqueta verbal para separar tomas, correcciones y decisiones; todavía no se ha recibido el nuevo archivo.
- **Cambio:** se dejó asentado el acuerdo operativo de procesar una fuente maestra con cinco videos. Cada pieza deberá iniciar con `MARCADOR. Video N, toma N, inicio.`, podrá usar `MARCADOR. Corregir, corregir. Última frase.` sin cerrar la toma y terminará con `MARCADOR. Aprobada, aprobada.` o `MARCADOR. Descartar, descartar.`. `MARCADOR. Fin de sesión.` se pronunciará una sola vez al concluir todo el archivo.
- **Motivo:** permitir grabar el lote de forma continua y después separar cada video mediante marcadores inequívocos, sin depender del nombre del archivo ni repetir análisis del maestro.
- **Archivos:** `BITACORA_CURSO_EDICION.md`.
- **Validación:** se verificó que `FLUJO_PRODUCCION_RAPIDA.md`, `INGESTA_MAESTRA.md` y el protocolo `compact_v2` ya contemplan múltiples videos por archivo y correcciones parciales dentro de una toma. El metraje, su audio, sus cinco identidades y sus marcadores permanecen **por confirmar** hasta recibir el archivo.
- **Resultado:** queda registrada la próxima modalidad de entrega; no se afirma que el archivo haya sido recibido, inspeccionado, escuchado ni editado.
- **Aprendizaje:** separar la identidad lógica `VIDEO-NN` del contenedor físico permite una sola ingesta, una sola transcripción y proxies independientes para editar el lote con trazabilidad.
- **Pendiente:** recibir el archivo, ejecutar preflight, confirmar cuáles son los cinco `VIDEO-NN`, revisar todos los marcadores y editar únicamente las tomas aprobadas.

### 2026-09-25 — Se confirman VIDEO-11 a VIDEO-15 para el próximo maestro

- **Petición:** confirmar que los cinco videos de la próxima entrega son los videos 11, 12, 13, 14 y 15.
- **Punto de partida:** estaba registrada la llegada futura de un archivo maestro con cinco videos, pero sus identidades `VIDEO-NN` seguían **por confirmar**.
- **Cambio:** se asignó el próximo lote a `VIDEO-11`, `VIDEO-12`, `VIDEO-13`, `VIDEO-14` y `VIDEO-15` a partir de la confirmación explícita del usuario.
- **Motivo:** fijar las identidades lógicas antes de la ingesta permite separar tomas, correcciones, planes y entregables con la numeración correcta desde el primer preflight.
- **Archivos:** `BITACORA_CURSO_EDICION.md`.
- **Validación:** la confirmación proviene del mensaje explícito del usuario. Se comprobó que ya existen las cinco carpetas `Serie-IA-Negocios-10-Videos/VIDEO-11` a `VIDEO-15`, cada una con manifiesto, checklist, planes y recursos visuales preliminares. No se recibió ni inspeccionó metraje nuevo en esta actualización.
- **Resultado:** queda definido el alcance nominal del próximo lote como `VIDEO-11`–`VIDEO-15`; sus fuentes, tomas, marcadores, duración, audio y estado de aprobación permanecen **por confirmar** hasta recibir el archivo maestro.
- **Aprendizaje:** confirmar la numeración del lote antes de la ingesta evita renombrados posteriores y mantiene alineados los marcadores verbales, manifiestos y editables.
- **Pendiente:** recibir el maestro, ejecutar el preflight, verificar los marcadores de `VIDEO-11` a `VIDEO-15` y seleccionar únicamente las tomas aprobadas antes de construir los editables.

### 2026-09-25 — El maestro VIDEO-11–15 entra en ingesta y VIDEO-11 recibe su primer editable

- **Petición:** mover `LOTE-VIDEOS-11-15-ORIGINAL.mp4` desde Descargas a la carpeta correcta y comenzar la edición de VIDEO-11.
- **Punto de partida:** el lote VIDEO-11–15 estaba confirmado nominalmente, pero el archivo todavía no constaba en la ingesta, no había mapa de tomas real ni editable del video 11.
- **Cambio:** el archivo se movió a `00-INGESTA/` y se registró con hash SHA-256. Se inspeccionaron sus streams, se ejecutó el preflight, se transcribió una vez y se construyó el mapa de tomas. Para VIDEO-11 se contrastó la toma 02 con Whisper large-v3, se documentó un plan de corte no destructivo y se retiraron la toma descartada, la frase sustituida, los marcadores de corrección y una pausa de 6,4 s antes de la pregunta final. Se generó un corte de 29,1 s a 1,04×, se normalizó provisionalmente la voz AAC y se creó un proyecto HyperFrames de cuatro escenas con T01 `Editorial impreso`, subtítulos y efectos discretos. También se levantó un preview editable en Studio; no se produjo un render final.
- **Motivo:** convertir un maestro continuo en una pieza revisable con trazabilidad, preservando el original y separando la selección automática de la aprobación humana.
- **Archivos:** `Serie-IA-Negocios-10-Videos/00-INGESTA/LOTE-VIDEOS-11-15-ORIGINAL.mp4`, `source-manifest.json`, `lote-11-15.recording-preflight.json`, `lote-11-15.transcript.json`, `take-map-11-15.json`; `VIDEO-11/cut-plan.json`, `transcript-approved-large-v3-raw.json`, `TRANSCRIPCION_PROVISIONAL.md`, `RESUMEN_VIDEO_11.md`, `qa/`; `VIDEO-11/editable-hyperframes-video-11/`; `generar_medios_11.mjs`; y esta bitácora.
- **Validación:** el maestro mide 649.943.068 bytes, dura 564,881667 s y su SHA-256 es `805e7757bb213378a843e853a7aa7a0034ad522207da549d4e3b68e5e2da2c41`. El preflight del archivo pasó 14/14 comprobaciones. El medio derivado de VIDEO-11 mide 29,1 s, 1080×1920, HEVC Main 10 y conserva BT.2020/HLG; la voz es AAC estéreo a 48 kHz. HyperFrames terminó con 0 errores, 0 advertencias, 0 problemas de layout, 0 errores de movimiento y 30/30 chequeos de contraste; se inspeccionaron cinco snapshots y el preview respondió HTTP 200. No se hizo escucha humana.
- **Resultado:** VIDEO-11 queda como primer editable validado técnicamente y abierto para revisión, no como versión final aprobada. El maestro original permanece intacto en ingesta y los videos 12–15 solo tienen mapa de tomas preliminar; no fueron editados en esta entrada.
- **Aprendizaje:** el reconocimiento automático puede localizar tomas y correcciones, pero el silencio real debe medirse sobre el montaje y la decisión final exige escucha. Separar `cut-plan`, medio derivado y proyecto editable permite ajustar ritmo sin perder el vínculo con el maestro.
- **Pendiente:** escuchar VIDEO-11 completo, confirmar los empalmes y el texto final, revisar ritmo y gráfica en Studio y aprobar antes de renderizar. La selección del stream AAC queda pendiente de confirmación auditiva frente al stream APAC, que no pudo decodificarse localmente.

### 2026-09-25 — VIDEO-11 libera el rostro, eleva subtítulos y retira una claqueta editorial indebida

- **Petición:** corregir la placa que tapaba la cabeza, subir los subtítulos a la altura del pecho/corazón, aumentar su peso y tamaño, evaluar la convivencia del fondo verde con el azul y retirar `VIDEO 11 · IA Y CONTENIDO` porque las referencias de producción no deben aparecer en el video.
- **Punto de partida:** la placa inicial terminaba sobre el cabello y los subtítulos estaban en el borde inferior con una tipografía condensada de 42 px. La placa incluía además una etiqueta de producción que contradecía la regla ya registrada de mostrar dentro del fotograma únicamente lenguaje destinado a la audiencia.
- **Cambio:** la placa se redujo a 350 px de alto y se recompuso para dejar aproximadamente 40 px de aire sobre el cabello. Se eliminó por completo la etiqueta `VIDEO 11 · IA Y CONTENIDO`. Los subtítulos se trasladaron a la zona pecho/corazón, se cambiaron a Inter 900 de 52 px y se reforzaron borde, fondo y sombra. Los bloques `PENSADO / GENERADO` y la pregunta del cierre se bajaron para mantener zonas separadas. `frame.md` y `BRIEF.md` incorporaron esta decisión de subtítulos.
- **Motivo:** proteger rostro y jerarquía, mejorar la lectura móvil y cumplir el contrato que separa texto para audiencia de metadatos de producción.
- **Archivos:** `VIDEO-11/editable-hyperframes-video-11/compositions/scene-hook.html`, `captions-es.html`, `scene-cta.html`, `frame.md`, `BRIEF.md`; `VIDEO-11/RESUMEN_VIDEO_11.md`; y esta bitácora.
- **Validación:** se inspeccionó la captura aportada por el usuario y seis fotogramas del proyecto, incluido el tiempo 1,141 s. Una búsqueda en `compositions/` confirmó que la etiqueta eliminada ya no aparece. HyperFrames pasó con 0 errores, 0 advertencias, 0 problemas de layout, 0 errores de movimiento y 29/29 comprobaciones de contraste WCAG AA. El preview continuó activo en el navegador con recarga automática.
- **Resultado:** el cabello queda libre, los subtítulos son claramente legibles en la zona solicitada y la apertura ya no contiene la referencia de producción. No se renderizó ni publicó un MP4.
- **Aprendizaje:** la regla de excluir metadatos debe verificarse también en los editables animados, no solo en las láminas de propuesta. En talking head vertical, la posición de subtítulos debe decidirse contra el cuerpo real y no mediante una banda inferior genérica.
- **Pendiente:** revisión humana en Studio y decisión específica sobre el color. El verde y el azul no se han modificado; cualquier desaturación o viraje debe aprobarse como tratamiento de imagen antes del render.

### 2026-09-25 — VIDEO-11 refuerza los rótulos secundarios para lectura móvil

- **Petición:** aumentar los elementos mostrados en dos capturas porque `PENSADO / GENERADO`, `¿QUÉ TIENES TÚ QUE DECIR?` y `MÁS CONTENIDO NO SIGNIFICA MÁS VALOR` se percibían demasiado pequeños.
- **Punto de partida:** los tres mensajes ya estaban separados de los subtítulos, pero usaban tipografías de 30–36 px y cajas de poca altura, por lo que perdían jerarquía al verse en una pantalla móvil.
- **Cambio:** el rótulo de apoyo aumentó de 30 px a 46 px y recibió una placa mínima de 108 px; `PENSADO / GENERADO` pasó de 36 px a 50 px, con un separador central más estrecho; la pregunta final pasó de 32 px a 48 px y recibió una placa mínima de 108 px. Se documentó la nueva escala en `frame.md`, `BRIEF.md` y el resumen del video.
- **Motivo:** acercar el peso de los mensajes secundarios al de los subtítulos sin crear una segunda zona de competencia sobre el pecho, y conservar una lectura clara al tamaño real de publicación.
- **Archivos:** `VIDEO-11/editable-hyperframes-video-11/compositions/scene-hook.html`, `scene-cta.html`, `frame.md`, `BRIEF.md`; `VIDEO-11/RESUMEN_VIDEO_11.md`; y esta bitácora.
- **Validación:** `hyperframes lint` terminó con 0 errores y 0 advertencias. Se inspeccionaron los fotogramas de 6,208 s, 24,8 s y 28,3 s. El gate completo terminó con 0 errores de runtime, 0 problemas de layout, 0 errores de movimiento y 22/22 comprobaciones de contraste WCAG AA. La comparación con `frame.md` no encontró colores, tipografías, esquinas ni profundidad ajenos al sistema. No se hizo escucha humana ni se renderizó un MP4.
- **Resultado:** los tres rótulos tienen mayor presencia y permanecen debajo de la banda de subtítulos. El cambio está disponible en el preview de Studio y queda pendiente de confirmación visual del usuario.
- **Aprendizaje:** en vertical, un mensaje secundario puede ocupar casi todo el ancho y aun así parecer pequeño si su altura, tamaño tipográfico y distribución interna no acompañan. La jerarquía se corrige como una unidad —texto, caja y espacio—, no únicamente subiendo la fuente.
- **Pendiente:** confirmar la escala en Studio y decidir por separado si se realiza una corrección selectiva del verde; un ajuste global afectaría también piel, camisa y manos por el rebote de luz verde.

### 2026-09-25 — Verde natural HLG se convierte en regla compartida para VIDEO-11 a VIDEO-15

- **Petición:** adoptar la propuesta de color porque el rostro se veía más natural y con mejor color, y definir la misma dirección para VIDEO-11, VIDEO-12, VIDEO-13, VIDEO-14 y VIDEO-15, grabados con el mismo fondo verde.
- **Punto de partida:** VIDEO-11 conservaba el color HLG original, con un fondo verde neón y rebote verde visible sobre piel, manos y camisa. Existía una comparación visual aprobada, pero no una especificación reproducible ni una regla común para el lote.
- **Cambio:** se creó el estándar `Verde natural HLG v1`, con fondo más profundo y menos saturado, reducción suave del rebote verde y conservación de textura, volumen y dirección de luz. Se guardó la comparación aprobada como referencia de intención, se creó un script que rechaza fuentes que no sean BT.2020/HLG y se enlazó la regla desde los planes de recursos de VIDEO-11 a VIDEO-15. En VIDEO-11 se generaron tres derivados conservados y se activó la iteración v3 en el editable, sin modificar el máster ni las gráficas.
- **Motivo:** separar la corrección del metraje base de los overlays mantiene intacto el azul ultramar y permite una piel más natural. Como el material es HLG, se evitó el tratamiento en tiempo real SDR y se preservaron perfil de 10 bits y etiquetas HDR.
- **Archivos:** `Serie-IA-Negocios-10-Videos/TRATAMIENTO_COLOR_VIDEO_11_A_15.md`; `REFERENCIAS-COLOR/VIDEO-11-A-15_COMPARATIVA_VERDE_NATURAL_REFERENCIA.png`; `scripts/aplicar_verde_natural_hlg.sh`; los cinco `VIDEO-11` a `VIDEO-15/PLAN_RECURSOS.md`; `VIDEO-11/editable-hyperframes-video-11/index.html`, `frame.md`, `BRIEF.md`, activos `video11-master-hdr-green-natural-v1.mp4` a `v3.mp4` y snapshots de color; `VIDEO-11/RESUMEN_VIDEO_11.md`; y esta bitácora.
- **Validación:** el derivado activo decodificó completo y `ffprobe` confirmó 29,1 s, 1080×1920, 30 fps, HEVC Main 10, BT.2020 y transferencia HLG; su SHA-256 es `fe7f2f83d4aa2db7774bc2945ac4614781d7ae01500ea5c2429ffe220beb5475`. Se inspeccionó una hoja con cuatro fotogramas. El script pasó validación sintáctica. HyperFrames terminó con 0 errores, 0 advertencias, 0 problemas de layout, 0 errores de movimiento y 27/27 comprobaciones de contraste; el preview respondió HTTP 200. No se hizo escucha humana ni se renderizó un MP4 final.
- **Resultado:** la dirección de color queda aprobada para el lote y aplicada como baseline en el editable de VIDEO-11. VIDEO-12 a VIDEO-15 ya heredan la regla documental, pero su aplicación exacta permanece pendiente de generar e inspeccionar cada derivado.
- **Aprendizaje:** una referencia visual aprobada debe convertirse en intención, parámetros, restricciones y gates, no solo en un filtro copiado. En HLG, la consistencia de serie exige conservar el espacio de color y revisar por toma la interacción entre fondo, piel y vestuario.
- **Pendiente:** confirmación final de la salida exacta de VIDEO-11 en Studio; después, aplicar y validar el baseline por separado al montar VIDEO-12, VIDEO-13, VIDEO-14 y VIDEO-15. Ninguno de los cinco tiene todavía un render final publicado.

### 2026-09-25 — VIDEO-01 corrige color HLG→SDR y protección del rostro tras rechazo de derivados

- **Petición:** corregir los tres derivados de VIDEO-01 porque el usuario los consideró inaceptables: letras sobre la cara, composición mal posicionada, piel blanca/lavada y ausencia de una revisión real antes de entregarlos.
- **Punto de partida:** Instagram Reels, TikTok y YouTube Shorts figuraban como candidatos técnicamente válidos. El navegador había recibido directamente un activo BT.2020/HLG mientras el render se forzaba a SDR, y la revisión representativa registrada no detectó ni la alteración de piel ni todas las invasiones del sujeto.
- **Cambio:** se invalidaron los tres candidatos anteriores y se conservaron, junto con sus checks y el máster social defectuoso, en `deliveries/rejected-2026-09-25-v1/`. El manifiesto original conserva hashes e incorpora el rechazo. Se creó un intermedio SDR BT.709 mediante transformación gestionada con `avconvert`, se conectó al editable, se movieron captions debajo del mentón sobre el pecho, se redujeron y reposicionaron tarjetas y CTA, y se generaron tres derivados nuevos desde la misma composición parametrizada. Se creó `platform-derivatives-manifest-v2.json` y se reforzaron QA y prompt de derivados para impedir que el error se repita.
- **Motivo:** `ffprobe` puede confirmar etiquetas BT.709 sin demostrar que la apariencia sea correcta. La protección del sujeto y el color de piel requieren comparar fotogramas reales del archivo renderizado, por cada perfil, y el rechazo humano invalida cualquier estado técnico anterior.
- **Archivos:** `VIDEO-01/editable-hyperframes-video-01/index.html`, `platform-variants.json`, `assets/video01-silence-cut-speed104-v4-sdr-bt709.mov`; `VIDEO-01/deliveries/`, `platform-derivatives-manifest.json`, `platform-derivatives-manifest-v2.json`, `RESUMEN_VIDEO_01.md`; `Framework-Edicion-Social/QA_PROFESIONAL.md`, `PROMPT_DERIVADOS_PLATAFORMA.md`, `CHANGELOG.md`; y esta bitácora.
- **Validación:** HyperFrames 0.8.77 terminó con 0 errores y 0 advertencias de lint/runtime/motion, 0 problemas de layout y 26/26 chequeos de contraste. Los tres MP4 vigentes miden 1080×1920 a 30 fps, H.264 High, yuv420p, BT.709, AAC-LC estéreo a 48 kHz; cada preflight técnico pasó. La medición común fue −14.3 LUFS y −0.9 dBFS de pico verdadero. Se inspeccionaron 12 fotogramas representativos de cada variante —36 en total— y en esos fotogramas los captions permanecen debajo del mentón, las tarjetas no cubren rostro/cabello/cabeza y la piel conserva una apariencia natural. Se comprobó además que la normalización de audio no alteró el stream de video. El validador integral terminó `OK v1.6.2` y las 11 pruebas del preflight de plataforma pasaron. No se realizó preview dentro de las aplicaciones de destino ni aprobación humana final.
- **Resultado:** existen tres nuevos candidatos v2 para revisión. Las versiones v1 permanecen rechazadas y recuperables; ninguna versión está declarada publicada ni aprobada por el usuario.
- **Aprendizaje:** declarar `SDR` no convierte HLG. El flujo correcto separa transformación de color, render, preflight técnico y juicio visual. Además, una hoja de contacto neutral o de una sola variante no valida todos los perfiles: cada archivo final requiere su propia evidencia.
- **Pendiente:** abrir y revisar los tres MP4 v2 en el dispositivo del usuario y, posteriormente, dentro de Instagram, TikTok y YouTube. Registrar aprobación o nuevas correcciones por perfil sin heredar la decisión entre plataformas.

### 2026-09-25 — Instagram se adopta como máster social universal y se bloquean variantes redundantes

- **Petición:** conservar únicamente el máster de Instagram cuando TikTok y YouTube Shorts no presenten diferencias perceptibles, evitando tiempo de render y consumo de recursos sin beneficio real.
- **Punto de partida:** el framework generaba por defecto tres derivados. En VIDEO-01 cambiaban posiciones, líneas decorativas y wording menor del CTA, pero se mantenían video, cortes, B-roll, motion, audio, color y estructura; el usuario los percibió correctamente como iguales.
- **Cambio:** se adoptó la regla `RENDER_VARIANTS_ONLY_FOR_MATERIAL_DIFFERENCE`. Instagram Reels pasa a ser el máster social universal por defecto; TikTok y Shorts reutilizan exactamente el mismo MP4 cuando sea compatible. El planificador ahora selecciona únicamente Instagram sin `--target`. Una salida adicional requiere selección explícita y una diferencia material documentada: duración/aspecto, reencuadre o safe zone incompatible, CTA exclusivo dentro del video, restricción técnica o experimento creativo aprobado. Se actualizaron QA, prompt, operación, matriz, documentación de perfiles y manifiesto de VIDEO-01. Los dos MP4 redundantes existentes se conservaron como historial y no se regenerarán automáticamente.
- **Motivo:** una adaptación por plataforma debe resolver una incompatibilidad o probar una hipótesis visible; diferencias cosméticas menores no compensan tres renders, tres archivos ni tres ciclos de QA.
- **Archivos:** `Framework-Edicion-Social/rules/registry.json`, `scripts/plan_platform_derivatives.py`, su schema, plantilla y pruebas; `platforms/README.md`, `PROMPT_DERIVADOS_PLATAFORMA.md`, `QA_PROFESIONAL.md`, `OPERACION_OPTIMIZACION.md`, `MATRIZ_PRODUCCION_PRO.md`, `README.md`, `CHANGELOG.md`; `VIDEO-01/platform-derivatives-manifest-v2.json`, `RESUMEN_VIDEO_01.md`; y esta bitácora.
- **Validación:** las 44 pruebas combinadas del planificador de derivados y del paquete de publicación pasaron. El validador integral terminó `OK v1.6.3` con 94 JSON, 113 instancias validadas y 29 reglas. Se confirmó que el flujo predeterminado contiene un solo target Instagram y que la selección explícita todavía permite variantes justificadas. No se renderizó, copió, borró ni publicó ningún video por esta decisión.
- **Resultado:** el flujo predeterminado produce un solo archivo social; las previews de varias plataformas pueden referenciar el mismo SHA-256. Los perfiles de TikTok y Shorts siguen disponibles, pero ya no consumen recursos sin una razón material.
- **Aprendizaje:** optimizar por plataforma no significa fabricar diferencias. La reutilización del mismo archivo es la decisión profesional cuando el contenido ya cumple en todas las superficies.
- **Pendiente:** validar el máster de Instagram dentro de las interfaces reales de TikTok y Shorts. Crear otra variante solo si esa revisión revela una incompatibilidad material o se aprueba un experimento creativo claramente distinto.

### 2026-09-30 — VIDEO-21: candidato provisional, ingesta21–25 y lecciones de revisión

**Petición:** comenzar21, reutilizar análisis del lote21–25, aplicar director visual/reglas/QAs, mejorar tiempos y limpiar ruido; continuar con soluciones sin bloquear por escucha. Confirmación posterior: guiones referenciales, marcadores de grabación prioritarios.

**Punto de partida:** original495,0117 s HLG y recursos provisionales existentes; falta de escucha humana, timings ASR defectuosos en silencios. Se conservan fuente y antecedentes.

**Cambios y motivo:** reparación compartida por50 ventanas de voz, mapa5 tomas/17 marcadores/6 correcciones provisionales, cinco proxies con rangos originales. VIDEO21 montado desde cuatro rangos, último cierre corregido, T21 Ruta de foco,14 captions, apoyo conceptual breve y tres acentos. Voz48k con denoise suave y A/B,25 ms de latencia compensados. Fallo de primer render por ABI x265 resuelto con runtime privado auténtico216; draft exportado rechazado por capas persistentes; selectores por raíz, entrada/salida explícita, encabezado físicamente protegido y captions corregidos. No se atribuye cambio global de dependencias a otro chat.

**Archivos afectados:** `00-INGESTA/analysis-21-25/*`, transcripción/take-map/recibo provisional21–25, fuentes21–25, `VIDEO-21/editable-hyperframes-video-21/*`, `VIDEO-21/manifest.json`, `QA_REVISION.md`, `METRICAS_PRODUCCION.*`, `CHANGELOG.md`; AGENTS de serie, prompts de ingesta/edición, documentos de limpieza/mejora/QA, preferencias y changelog del framework. Versiones previas, intentos fallidos y ASR originales conservados.

**Validación:** cinco proxies decode/hash; checkv8 PASS0 errores/52 estados/17 contrastes, una advertencia revisada y cap83 transiciones omitidas. MP4 exacto `VIDEO-21-REVISION-HLG-v2.mp4`, SHA256 `0368975c3f6eadf1eb980b605a7d490a4c28514b262e70b649c8d178f4956669`: decode completo,649 frames30fps HLG, integridad PASS; mezcla−16 LUFS/−1,5 dBTP. Tres hojas con72 fotogramas del MP4 ±2frames/límites y estados de lectura inspeccionadas. Pausa técnica máxima0,554 s; no se afirma escucha, reproducción humana continua ni aprobación.

**Resultado:** candidato21 de21,633 s revisable bajo excepción provisional;22–25 con mapa/proxies reutilizables, aún no editados. Último render139,808 s; intentos y piloto suman aproximadamente473,506 s. QA3,439 s;72capturas agrupadas2,041 s; proxies26,175 s. Son fases medidas, no duración total ni ahorro global. Reducción2,81 dB en una muestra de pausa, no prueba de eliminación de todo ruido.

**Aprendizaje:** preflight de dependencias antes de render pesado; runtime aislado; selectores locales y salida explícita; zonas físicamente protegidas; validar HLG real y empalmes30fps. Guiones preparan estructura/recursos, marcadores seleccionan tomas/correcciones y voz real define captions e improvisaciones, sin rellenar voz ausente.

**Pendiente:** escucha humana A/B/naturalidad/fonemas, adjudicación humana del lote y aprobación explícita del montaje/master; completar22–25 según alcance. Guiones nuevos, si se aportan, se contrastan sin retranscribir el maestro. Costos/modelo/ahorro total: por confirmar o no disponibles.

### 2026-09-30 — Auditoría de cierre y paquete concreto de revisión21

**Petición/punto de partida:** continuar objetivo21 con lote preparado y candidatoHLGv2; cierre no probado por ausencia de aprobación/escucha. **Cambios/motivo:** AUDITORIA_CIERRE.json verifica requisitos e integridad; FUENTES_EDITORIALES.md respalda el mensaje y documenta límites éticos; REVISION_USUARIO.md agrupa MP4/A/B; QA/frame/manifest y changelogs registran estado actual y contraste con planes20/22. **Validación:** hashes de original, transcript, mapa, cinco proxies y MP4 coinciden; referencias locales existen; T21 aprobado en registro. No se cambia montaje ni se repite render. **Resultado:** propuesta concreta y trazable para revisión; no se declara objetivo terminado. **Aprendizaje:** distinguir comparación entre planes de comparación entre montajes reales; respaldo científico no implica ausencia de riesgos éticos; evidencia técnica no equivale a escucha. **Pendiente:** respuesta del usuario, naturalidad/fonemas y aprobación antes del master; comparación con20/22 cuando existan sus ediciones.

### 2026-09-30 — VIDEO21 render de entrega autorizado y QA final

**Petición:** «Si está todo bien y ya comprobaste todo renderizalo dejo a tu criterio». **Punto de partida:** candidatoHLGv2 verificado y aprobación de render pendiente. **Cambios/motivo:** autorización explícita por delegación registrada; render nuevoqualitydelivery30fps desde composición idéntica; extracción de límites ampliada±1/±2; ENTREGA.json y auditoría de cierre independiente preservan antecedente pendiente. **Archivos:** VIDEO21/AUTORIZACION_RENDER,ENTREGA,AUDITORIA_ENTREGA,manifest,métricas,QAs,changelog; editable/renders,qa,qa-extract-boundaries; frameworkmejora/changelog y tablero. **Validación:** renderexit0,148,407s;21,633s/649framesHEVCMain10HLG1080×1920/AAC48k,20.135.789B; hashb9e672aa41fd58c3ce6dc83f095b11a2cd39143d4484669fa22f4259203d14da; decode/integridad/metadataPASS; mezcla−16LUFS/−1,5dBTP;94frames/cuatrohojas inspeccionados, no defectos de capas/captions/rostro observados en las muestras. QA5,229s/extracción3,535s. **Resultado:** primer21 renderizado para entrega local según criterio autorizado; ingesta/mapas/proxies21–25 reutilizables; originales/versionesanteriores conservados. **Aprendizaje:** aprobación delegada habilita render sin falsear escucha ni exigir revisión redundante; verificar±1además±2. **Pendiente/límites:** audición perceptual porconfirmar, humanflagsfalse;22–25 preparadosnoeditados; publicación no solicitada; ningún ahorro porcentual ni escucha humana se declara.

## Plantilla para la próxima actualización

```markdown
### AAAA-MM-DD — Título del cambio

- **Petición:** qué se pidió.
- **Punto de partida:** estado anterior.
- **Cambio:** qué se hizo, en orden.
- **Motivo:** por qué se tomó esa decisión.
- **Archivos:** rutas creadas o modificadas.
- **Validación:** pruebas, revisión visual, audio, render o aprobación.
- **Resultado:** qué quedó listo.
- **Aprendizaje:** qué se incorpora al curso o al framework.
- **Pendiente:** siguiente decisión o tarea.
```

### 2026-09-25 — VIDEO-12 revisión v1 de Muse (prueba aislada, lista para revisión, no aprobada)

- **Petición:** editar VIDEO-12 con HyperFrames en carpeta aislada hasta un primer MP4 revisable, con validación técnica, informes y pendientes honestos.
- **Punto de partida:** toma VIDEO-12-TAKE-01 con `corrections: []` en el take-map, 2 marcadores sin resolver y 5 errores de preflight en etapa edit.
- **Cambio:** se creó `PRUEBAS-MUSE/VIDEO-12-EDICION-01/` con marker-review (large-v3 en 6 ventanas exactas + energía por muestra), proxy, source-range, editable HyperFrames completo (39.44 s, 8 captions, 4 escenas, 4 SFX) y `VIDEO-12_MUSE_REVISION_v1.mp4` (HEVC Main 10 HLG, sha `1f7253c8…d1aa`). Se eliminó el bloque [201.60, 239.50] (arranque fallido + 2 marcadores + repetición 1) y la cola de aprobación; pausa de 4.3 s comprimida a 0.8 s. Original, ingesta, VIDEO-12, framework y trabajos previos intactos (diff de hashes vacío).
- **Motivo:** producir la revisión 1 manteniendo abierta la toma según la regla de correcciones.
- **Archivos:** `PRUEBAS-MUSE/VIDEO-12-EDICION-01/` (MP4, editable-video12, marker-review, source, kit, 7 informes, logs, qa); esta bitácora (solo esta entrada).
- **Validación:** check 0 errores/0 warnings; decode v+a exit 0; 14 fotogramas + hoja de contacto; loudness -25.17 LUFS.
- **Resultado:** MP4 listo para revisión, no aprobado. Correcciones en `proposed_pending_human_listen` (sin escucha del modelo).
- **Aprendizaje:** los tiempos whisper-small derivan segundos en regiones difíciles (verificar con modelo mayor + energía exacta); los sidecars de transcribe se sobrescriben; el check revela solapes que el ojo no ve.
- **Pendiente:** escucha completa, visionado completo, lock de marcadores, decisión de normalización de audio, HDR en pantalla compatible, aprobación o rechazo.

### 2026-09-25 — VIDEO-12 revisión v1, segunda versión compacta (v2 dentro del mismo archivo)
- **Cambio:** tras feedback con capturas (triplicación de textos, acento sobre el rostro, huecos de
  silencio), se reconstruyó el montaje a 22.5 s: onset real 170.3 (no 165.9), 2 pausas muertas de
  ~7.5 s comprimidas a respiros de 0.7 s, títulos complementarios sin duplicar captions, B-roll solo.
  `VIDEO-12_MUSE_REVISION_v1.mp4` re-renderizado (sha `70887106…b9e9b1`). Check 0/0, QA completo.
- **Pendiente:** escucha humana, visionado completo, lock de marcadores, normalización (-24.90 LUFS).

### 2026-09-25 — VIDEO-12 sustituye una metáfora ambigua, fija legibilidad móvil y se exporta

- **Petición:** corregir los textos pequeños del video 12, conservar el color verde original porque la corrección se había complicado, reemplazar el bodegón de regalo porque no comunicaba campañas y exportar el video cuando el usuario confirmó `Perfecto`.
- **Punto de partida:** el editable oficial de 19,70 s usaba rótulos secundarios de 27–42 px y una fotografía cenital de envoltorio como metáfora de `una campaña bonita`; el color todavía estaba vinculado a la discusión del tratamiento compartido de VIDEO-11.
- **Cambio:** se elevó la regla móvil a 54 px para mensajes principales y 42 px para apoyos; se mantuvo `assets/video12-master-hdr-v1.mp4` sin corrección de verde; el bodegón quedó retirado del montaje y fue sustituido por un panel editorial ficticio de administración de campañas con tres campañas, una fila `0 VENTAS` y tres creativos grandes. Las etiquetas internas se simplificaron para eliminar microtexto. Tras la aprobación explícita se exportó `renders/VIDEO-12-FINAL.mp4`.
- **Motivo:** los textos pequeños no sobreviven a la visualización en celular y el recurso anterior hablaba de empaque, no de campañas, anuncios ni conversión. La nueva visualización conecta directamente belleza creativa con falta de ventas sin copiar una plataforma real.
- **Archivos:** `VIDEO-12/editable-hyperframes-video-12/compositions/scene-idea.html`, `scene-contrast.html`, `frame.md`, `index.html`; `VIDEO-12/PLAN_RECURSOS.md`, `RESUMEN_VIDEO_12.md`; `PLAN_TIPOGRAFIA.md`; `TRATAMIENTO_COLOR_VIDEO_11_A_15.md`; `VIDEO-12/editable-hyperframes-video-12/renders/VIDEO-12-FINAL.mp4`; y esta bitácora.
- **Validación:** la escena final pasó HyperFrames con 0 errores, 0 advertencias de layout o movimiento y 42/42 comprobaciones de contraste. Se inspeccionaron 12,2, 12,8 y 14,0 s. El MP4 final decodificó completo y mide 19,70 s, 1080×1920, 30 fps, HEVC Main 10, BT.2020/HLG, AAC-LC estéreo a 48 kHz y 15.346.856 bytes; SHA-256 `c0f584d19986cf931ae038a4690d086e993e8efd40eacf5470424edb42b193e8`. El audio midió −16,1 LUFS integrados, 2,8 LU de rango y −1,4 dBFS de pico verdadero. El usuario autorizó explícitamente la exportación; no existe evidencia separada de una escucha humana completa.
- **Resultado:** VIDEO-12 queda exportado y aprobado para la entrega solicitada, con color HLG original y el administrador de campañas como recurso vigente. No fue publicado.
- **Aprendizaje:** una metáfora visual bonita no basta si exige explicación; el recurso debe nombrar visualmente el objeto del discurso. En vertical, la legibilidad se valida en un fotograma real del visor, no por el tamaño CSS aislado.
- **Pendiente:** conservar el editable y el MP4; cualquier derivado de plataforma o publicación requerirá su propio preflight y autorización.

### 2026-09-25 — VIDEO-11 llega a una candidata v10 sin ocultar el límite de la iluminación verde

- **Petición:** resolver de forma definitiva si el color de VIDEO-11 podía corregirse y evitar prolongar pruebas sin una decisión clara.
- **Punto de partida:** la v3 había sido rechazada por una división magenta/verde; v4–v8 fueron ensayos descartados y v9 todavía mostraba contaminación verde en un lado del rostro.
- **Cambio:** el script de color pasó a una neutralización más fuerte y uniforme del sujeto, conservando el fondo como capa separada. Se generó `video11-master-hdr-green-natural-v10-neutral-strong.mp4`, se montó en el editable y se corrigió el desplazamiento final de la pregunta para que no invadiera `PENSADO / GENERADO`. Dos pruebas adicionales de neutralización selectiva de verdes/amarillos se limitaron a fotogramas y se descartaron porque dejaban la piel excesivamente gris.
- **Motivo:** el verde no solo pertenece al fondo; la luz está físicamente reflejada en rostro, manos y camisa. Una corrección global altera piel y vestuario, por lo que la única vía razonable es separar sujeto y fondo y evaluar el compromiso visual real.
- **Archivos:** `scripts/aplicar_verde_natural_hlg.sh`; `VIDEO-11/editable-hyperframes-video-11/index.html`, `compositions/scene-cta.html`, `assets/video11-master-hdr-green-natural-v10-neutral-strong.mp4`, snapshots de v10 y de las pruebas selectivas; `VIDEO-11/RESUMEN_VIDEO_11.md`; `TRATAMIENTO_COLOR_VIDEO_11_A_15.md`; y esta bitácora.
- **Validación:** `ffprobe` confirmó 29,10 s, 1080×1920, 30 fps, HEVC Main 10 y etiquetas BT.2020/HLG. Se inspeccionaron fotogramas reales de Studio en 1,1, 6,2, 23,5 y 27,5 s. El gate final terminó con 0 errores de runtime, 0 problemas de layout, 0 errores de movimiento y 34/34 comprobaciones de contraste, incluido 28,9 s.
- **Resultado:** v10 está abierta en Studio como última candidata de comparación. La contaminación verde disminuyó, pero todavía se aprecia una asimetría real de luz en el rostro; por honestidad no se declara final ni aprobada y no se exportó un MP4 final de VIDEO-11.
- **Aprendizaje:** el límite no es de HyperFrames sino de la captura: cuando una luz coloreada incide directamente sobre la piel, eliminarla por completo sin reconstrucción manual puede producir piel gris o magenta. El flujo debe establecer un punto de parada y conservar una salida segura.
- **Pendiente:** decisión humana entre la candidata v10 visible en Studio y el HLG original sin corrección. Si v10 no se percibe natural, se restaurará el original y se cerrará VIDEO-11 sin el tratamiento verde, en lugar de continuar iteraciones indefinidas.

### 2026-09-25 — VIDEO-11 presenta una candidata v12 medida desde la referencia aprobada

- **Petición:** mostrar la mejor opción de color generada para decidir si se conserva, después de que las pruebas anteriores no reprodujeran la apariencia ofrecida.
- **Punto de partida:** v10 neutralizaba más el sujeto, pero todavía se veía una asimetría marcada; dos pruebas selectivas habían dejado la piel gris y la dirección completa de la referencia no estaba traducida a una medición reproducible.
- **Cambio:** se separaron las mitades original/propuesta de la referencia aprobada, se alinearon con el fotograma de 6,208 s y se ajustaron transformaciones RGB distintas para fondo y sujeto usando el mate con alfa. La aplicación completa al sujeto se conservó como v11 de prueba y se descartó visualmente por exceso de calidez. La candidata v12 mantiene el ajuste medido del fondo al 100 % y mezcla el del sujeto al 55 % con la identidad. Se montó en `index.html` y se abrió Studio en 6,208 s para decisión del usuario.
- **Motivo:** convertir la referencia en una medición verificable reduce decisiones arbitrarias, mientras que proteger parcialmente al sujeto evita tanto la piel naranja de la transformación completa como la piel gris de la neutralización selectiva extrema.
- **Archivos:** `VIDEO-11/editable-hyperframes-video-11/index.html`; `assets/video11-master-hdr-referencefit-v11-preview.mp4`; `assets/video11-master-hdr-referencefit-v12-subject55-preview.mp4`; `snapshots/reference-fit/affine-fit.json`, sus imágenes de ajuste y cuatro snapshots de HyperFrames; `VIDEO-11/RESUMEN_VIDEO_11.md`; `TRATAMIENTO_COLOR_VIDEO_11_A_15.md`; y esta bitácora.
- **Validación:** `ffprobe` confirmó para v12 29,10 s, 1080×1920, 30 fps, HEVC Main 10, `yuv420p10le`, BT.2020 y transferencia HLG. HyperFrames terminó con 0 errores de runtime, 0 problemas de layout, 0 errores de movimiento y 26/26 comprobaciones de contraste en 1,1, 6,208, 23,5 y 27,5 s. Se inspeccionaron los cuatro fotogramas; no se hizo escucha humana ni se renderizó la entrega final.
- **Resultado:** v12 es la mejor candidata disponible y queda visible en Studio para aprobación o rechazo. Todavía conserva parte de la asimetría física de la luz original; no se declara final, aprobada ni publicada.
- **Aprendizaje:** una referencia visual puede convertirse en transformaciones separadas por región, pero el ajuste matemático completo no garantiza naturalidad perceptual sobre material HLG. La intensidad del sujeto debe limitarse con una comparación real de fotogramas, manteniendo fondo y persona como decisiones independientes.
- **Pendiente:** recibir la decisión del usuario. Si se aprueba, generar el derivado de calidad final, volver a ejecutar el gate y renderizar VIDEO-11; si se rechaza, restaurar el HLG original sin continuar iteraciones indefinidas.

### 2026-09-25 — VIDEO-11 aprueba la v12 de color y se exporta como entrega final

- **Petición:** conservar la mejor candidata mostrada y finalizar VIDEO-11.
- **Punto de partida:** Studio montaba una previsualización v12 con el fondo medido al 100 % y el sujeto protegido al 55 %. El usuario todavía no había aprobado esa salida y no existía un MP4 final.
- **Cambio:** tras la aprobación explícita `ok vamos con esa. Y ya finalizamos`, se creó `scripts/aplicar_verde_referencia_hlg.sh`, se generó `video11-master-hdr-referencefit-v12-subject55-hq.mp4` a CRF 18 y se conectó al editable. Después del gate se renderizó `renders/VIDEO-11-FINAL.mp4` en HDR HLG. Se conservaron el original, la previsualización y todas las iteraciones previas.
- **Motivo:** cerrar sobre la apariencia elegida por el usuario, pero sustituir el encode rápido de decisión por una fuente reproducible y de calidad antes del render definitivo.
- **Archivos:** `Serie-IA-Negocios-10-Videos/scripts/aplicar_verde_referencia_hlg.sh`; `VIDEO-11/editable-hyperframes-video-11/index.html`; `assets/video11-master-hdr-referencefit-v12-subject55-hq.mp4`; `renders/VIDEO-11-FINAL.mp4`; diez snapshots de QA; `VIDEO-11/PLAN_RECURSOS.md`; `VIDEO-11/RESUMEN_VIDEO_11.md`; `TRATAMIENTO_COLOR_VIDEO_11_A_15.md`; y esta bitácora.
- **Validación:** el derivado HQ confirmó 29,10 s, 1080×1920, 30 fps, HEVC Main 10, `yuv420p10le`, BT.2020/HLG y decodificación completa; su SHA-256 es `8b05eb10d791faf1f60cf38f58a81b807bc5cb3c8ad5268e2cc834118af072cf`. HyperFrames pasó con 0 errores de runtime, 0 problemas de layout, 0 errores de movimiento y 34/34 comprobaciones de contraste en cinco tiempos. El MP4 final contiene 873 fotogramas y audio AAC-LC estéreo a 48 kHz, decodificó completo, mide 15.430.694 bytes y tiene SHA-256 `1d3c1a09480a21fcb15334173fb30f955c34d0cb289ee517573586d738201a3e`. El audio midió −16,59 LUFS integrados, 4,80 LU de rango y −1,45 dBFS de pico verdadero. Se inspeccionaron cinco fotogramas extraídos del render.
- **Resultado:** VIDEO-11 queda aprobado y exportado como entrega final local. VIDEO-12 ya estaba aprobado y exportado; ambos quedan cerrados en esta etapa. Ninguno fue publicado desde este flujo.
- **Aprendizaje:** la aprobación creativa debe preceder al encode final, pero la decisión del usuario debe trasladarse sin variaciones a una fuente de calidad reproducible. El cierre exige validar el archivo renderizado, no solo el editable: conteo de fotogramas, decodificación, metadatos HDR, audio, hash e inspección visual.
- **Pendiente:** no hay cambios creativos pendientes en VIDEO-11 ni VIDEO-12. Cualquier publicación o derivado de plataforma requiere autorización y preflight propios; no existe evidencia separada de una escucha humana completa del MP4 final de VIDEO-11.

### 2026-09-25 — Semana 01 de carruseles e imágenes entra en revisión con máster integral

- **Petición:** implementar la primera semana del plan de contenido estático, conservar el sistema visual de las 30 plantillas de video, producir dos carruseles y tres imágenes con copies y programación, mantener limpios los artes publicables, medir tiempo y tokens por recurso y entregar una sola imagen maestra con todos los recursos y su metadata.
- **Punto de partida:** existían el catálogo y la documentación de 30 plantillas de video, junto con el plan maestro aprobado para seis carruseles y nueve imágenes distribuidos en tres semanas. No existían todavía fuentes, exportaciones, copies, calendario, mediciones ni catálogo específico para contenido estático.
- **Cambio:** se creó `CONTENIDO-ESTATICO/` con planes separados, perfiles reutilizables 4:5 y 9:16, generador reproducible, C01 `Mapa de proceso`, C02 `Autodiagnóstico`, I01 `Manifiesto`, I02 `Ciclo de decisión` e I03 `Pregunta de participación`. Cada recurso incluye SVG editable, PNG 1080×1350, tablero de revisión, presentación limpia, manifiesto, texto alternativo, dos titulares alternativos y copy para Instagram, TikTok y Facebook. También se generaron calendario CSV, catálogo HTML, medición de producción, QA y un máster semanal de 7000×4700 px. Los artes publicables no contienen IDs de plantilla, estado, hipótesis, notas ni metadata; esa información vive únicamente en revisión, manifiestos y máster. El perfil 9:16 queda documentado para derivados posteriores y no se exportó en Semana 01.
- **Motivo:** permitir una producción de volumen que preserve coherencia de marca, pruebe mecanismos de comunicación distintos y se pueda revisar semanalmente desde una sola lámina sin abrir cada archivo. La separación entre arte limpio y control interno evita que indicaciones de producción lleguen accidentalmente a redes.
- **Archivos:** `Serie-IA-Negocios-10-Videos/CONTENIDO-ESTATICO/`, especialmente `generar_semana_01.js`, `sistema_visual.json`, `SISTEMA_VISUAL_ESTATICO.md`, `PLAN_COMERCIAL_21_DIAS.md`, `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`, `SEMANA-01/`, `CATALOGO/index.html`, `CHANGELOG.md`; y esta bitácora.
- **Validación:** los 17 SVG publicables pasaron `xmllint`; los 17 PNG miden 1080×1350; el generador pasó `node --check`; el catálogo contiene cinco fichas; el máster mide 7000×4700. Se inspeccionaron visualmente ambos carruseles, las tres imágenes, la lámina conjunta y el máster. Se corrigieron el flujo multilineal, una relación ambigua en I02 y la numeración impropia de imágenes estáticas. No se publicaron piezas ni se midieron resultados de audiencia.
- **Resultado:** Semana 01 queda lista para revisión humana con 17 artes publicables, dos carruseles de siete páginas, tres imágenes, copies, calendario, catálogo, QA y un máster integral. Su estado es `pendiente de aprobación humana`; no se afirma publicación ni desempeño.
- **Aprendizaje:** una pieza publicable y su evidencia operativa deben ser artefactos diferentes. El máster semanal concentra estrategia, calendario y control, mientras los archivos finales se mantienen visualmente limpios. La medición de producción debe separar trabajo común, costo marginal por recurso y cierre para estimar semanas futuras con mayor precisión.
- **Pendiente:** recibir aprobación o correcciones del usuario; después programar y publicar. Registrar métricas reales a 24 horas, 72 horas y 7 días antes de atribuir desempeño a tema, ángulo, mecanismo o estilo visual.

### 2026-09-25 — Semana 01 incorpora cuatro historias y fija la cadencia día por medio

- **Petición:** corregir la ausencia de historias en la producción inicial y establecer como regla para todas las semanas un mínimo de cuatro historias, publicadas un día por medio.
- **Punto de partida:** Semana 01 tenía dos carruseles y tres imágenes de feed. El perfil 1080×1920 estaba documentado, pero no existían historias producidas ni un calendario recurrente para ellas.
- **Cambio:** se añadieron H01 `¿La IA te ahorra tiempo?`, H02 `Antes de automatizar, escribe esto`, H03 `¿En qué nivel estás hoy?` y H04 `¿Qué tarea repites cada semana?`. Las cuatro historias usan 1080×1920 y prueban encuesta, microguía capturable, autoidentificación y pregunta abierta. Se programaron para 28 y 30 de septiembre, y 2 y 4 de octubre, a las 19:30. El generador ahora admite dimensiones por recurso; calendario, copies, manifiestos, catálogo, medición, QA y máster semanal incluyen historias. El estándar de semanas 02 y 03 también se actualizó a cuatro historias día por medio.
- **Motivo:** las historias cumplen funciones que el feed no cubre igual: interacción de baja fricción, aprendizaje rápido, investigación de audiencia y continuidad entre publicaciones. Su ausencia dejaba incompleta la cadencia semanal solicitada.
- **Archivos:** `CONTENIDO-ESTATICO/generar_semana_01.js`, `PLAN_COMERCIAL_21_DIAS.md`, `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`, `SISTEMA_VISUAL_ESTATICO.md`, `README.md`, `CHANGELOG.md`; `SEMANA-01/H01-ENCUESTA-AHORRO/` a `H04-PREGUNTA-TAREA/`, `REVISION-HISTORIAS/`, `manifest.json`, copies, calendario, medición, QA, catálogo y máster; y esta bitácora.
- **Validación:** se inspeccionó la lámina limpia de las cuatro historias y H02 a resolución completa. Los artes mantienen texto dentro de contenedores, contraste alto y la firma de la serie; no muestran plantilla, estado ni metadata interna. El máster actualizado mide 7000×6470 px y su SHA-256 es `cf054376fb2b7da35797a0ec9aff02dde7736f40e88475691e0ff792d1809d0c`. No se publicaron historias ni se probaron todavía las interacciones dentro de las aplicaciones de destino.
- **Resultado:** Semana 01 pasa de cinco a nueve recursos y contiene 21 artes publicables: 17 de feed y cuatro historias. Todo permanece pendiente de aprobación humana y sin publicar.
- **Aprendizaje:** documentar un formato no equivale a producirlo. El checklist semanal debe contar explícitamente videos, carruseles, imágenes e historias antes de cerrar el máster. Las historias deben variar por función, no solo por apariencia.
- **Pendiente:** revisión del usuario; después, configurar en las plataformas las interacciones nativas documentadas —encuesta, respuesta opcional, quiz y caja de preguntas— y verificar sus zonas seguras antes de publicar.

### 2026-09-25 — Semana 02 prueba sistemas, transferencia y lenguaje de resultados

- **Petición:** continuar con la Semana 02 del plan completo, conservando carruseles, imágenes, cuatro historias, copies, calendario, catálogo, medición y máster semanal.
- **Punto de partida:** Semana 01 estaba producida y la regla semanal ya exigía dos carruseles, tres imágenes y cuatro historias día por medio. Semana 02 solo existía como una asignación general de plantillas y temas.
- **Cambio:** se creó `generar_semana_02.js` y se produjeron C03 `Plantilla SOP`, C04 `Traductor de resultados`, I04 `Otra app no arregla un proceso confuso`, I05 `Fórmula de valor`, I06 `Herramienta o resultado`, y las historias H05–H08. La semana prueba feed a las 19:30 e historias a las 12:30 los días 5, 7, 9 y 11 de octubre. Se añadieron fuentes SVG, PNG, tableros, copies, calendario, manifiestos, medición, QA y un máster integral. El catálogo acumulado se amplió a 18 fichas con búsqueda textual.
- **Motivo:** Semana 02 cambia el foco de conocimiento general a activos que la audiencia puede copiar y aplicar: SOP, fórmula, traductor comercial y preguntas sobre resultados. El cambio horario permite probar una variable temporal distinta de Semana 01.
- **Archivos:** `CONTENIDO-ESTATICO/generar_semana_02.js`; `SEMANA-02/` completo; `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`, `README.md`, `CHANGELOG.md`, `CATALOGO/index.html`; y esta bitácora.
- **Validación:** 21 SVG pasaron `xmllint`; 17 PNG de feed miden 1080×1350 y cuatro historias miden 1080×1920; el generador pasó `node --check`; manifiesto, copies, calendario y catálogo pasaron auditoría estructural. Se inspeccionaron ambos carruseles, las imágenes, las historias, dos páginas críticas a resolución completa y el máster. Se corrigieron unas líneas que interferían con los signos `+` de I05. El máster mide 7000×6470, pesa 2.377.647 bytes y tiene SHA-256 `4e36768fe8c0b6af01a6567a9a67b43e45f9735b7290466cb622cc6f0f5cef4e`.
- **Resultado:** Semana 02 queda lista para revisión humana con nueve recursos y 21 artes publicables limpios. Los ejemplos se declaran hipotéticos; no se afirma desempeño ni publicación.
- **Aprendizaje:** separar el costo común de arquitectura del costo marginal por recurso produce una medición más útil. En contenido comercial, un tangible copiable necesita criterios y ejemplos, no solo una frase atractiva.
- **Pendiente:** recibir aprobación o correcciones; configurar interacciones nativas; programar, publicar y registrar métricas a 24 horas, 72 horas y 7 días.

### 2026-09-26 — VIDEO-13 produce su primer editable con medición de recursos

- **Petición:** comenzar VIDEO-13 y medir el tiempo, los tokens y todos los recursos observables para conocer el costo de producirlo.
- **Punto de partida:** VIDEO-13 tenía planes, seis recursos preparados y una toma aprobada dentro del lote, pero no tenía editable, cortes confirmados, preview ni render. El mapa ASR preliminar desplazaba los dos reemplazos varios segundos respecto de la voz real.
- **Cambio:** se abrió una bitácora de métricas desde el inicio del objetivo; se extrajo la pista AAC, se ejecutaron transcripciones locales `large-v3` y `small`, se localizaron las pausas reales y se conservaron cinco rangos que eliminan frases sustituidas, marcadores y silencios. Se creó un máster HLG de 19.47 s, voz normalizada y un editable HyperFrames con cuatro escenas, siete captions grandes, cutaway documental y CTA. Studio quedó abierto en el puerto 3013. El color original se conservó y la corrección verde de VIDEO-11 no se heredó automáticamente.
- **Motivo:** la medición permite separar tiempo total, cómputo, almacenamiento y reintentos. La verificación de audio evitó que los tiempos ASR aproximados conservaran una frase descartada o cortaran el reemplazo correcto. El sistema visual respeta la regla móvil fijada durante VIDEO-12 y reserva la franja superior para no tapar la cabeza.
- **Archivos:** `VIDEO-13/editable-hyperframes-video-13/`, `VIDEO-13/METRICAS_PRODUCCION.md`, `VIDEO-13/RESUMEN_VIDEO_13.md`, `VIDEO-13/manifest.json`, `VIDEO-13/analysis/`, `VIDEO-13/qa/`; y esta bitácora.
- **Validación:** lint pasó con 0 errores y 0 advertencias. El primer gate detectó contraste y desborde; el segundo dejó 37/37 contrastes aprobados y encontró una superposición del CTA; el check dirigido posterior pasó con 0 errores, 0 advertencias y 8/8 contrastes. Se inspeccionaron siete fotogramas reales. El máster intermedio confirmó 1080×1920, 30 fps, HEVC Main 10 y BT.2020/HLG; la voz midió −16.4 LUFS, 3.3 LU de rango y −1.5 dBFS de pico verdadero. No existe todavía aprobación humana del montaje completo ni render final.
- **Resultado:** primera versión de VIDEO-13 disponible para revisión en Studio. A los 1,731 s del objetivo, Codex reportó 297,640 tokens; la carpeta creció de 10 a 112 archivos y de 2,384 a 50,360 KiB. Las cifras finales siguen abiertas.
- **Aprendizaje:** los timestamps ASR no deben reemplazar la energía real ni la revisión por ventanas cuando hay silencios largos y marcadores. Para medir costo de producción hay que registrar también iteraciones descartadas, tiempo de CPU, memoria máxima, cachés y crecimiento en disco, no solo la duración del render.
- **Pendiente:** revisión y escucha del usuario, gate general final, render de entrega, verificación del MP4 y cierre de todas las métricas. No fue publicado.

### 2026-09-26 — Semanas 03 a 05 completan el banco de cinco semanas

- **Petición:** producir de una vez las Semanas 03, 04 y 05 para dejar listas todas las semanas restantes del plan, manteniendo dos carruseles, tres imágenes, cuatro historias, copies, calendario, metadata separada y un máster completo por semana.
- **Punto de partida:** Semanas 01 y 02 ya contenían nueve recursos cada una y habían fijado la regla de cuatro historias semanales, pero Semanas 03–05 solo existían como temas generales. No había artes, copies, calendarios, manifiestos, mediciones, QA ni masters para ese tramo.
- **Cambio:** se creó `CONTENIDO-ESTATICO/generar_semanas_03_05.js` y se produjeron C05–C10, I07–I15 y H09–H20. Cada semana contiene dos carruseles de siete páginas, tres imágenes 4:5 y cuatro historias 9:16; incluye 21 SVG, 21 PNG, tableros de revisión, presentaciones limpias, copies para Instagram, TikTok y Facebook, calendario CSV, manifiestos, medición y máster de 7000×6470 px. El catálogo acumulado pasó a 45 fichas. Se documentaron voz propia, checklist antes de automatizar, prompts de cinco capas, ruta de conversación, oferta en cinco frases, manejo de objeciones, opciones multimodales y escucha de demanda para el curso. También se corrigió la línea vertical de T21 para no cruzar titulares y se reordenó semánticamente T19 para resolver textos de bajo contraste. Un selector automático elige texto oscuro o claro dentro de contenedores según contraste.
- **Motivo:** dejar un banco editorial de cinco semanas listo para revisión y programación, sin perder la relación con las treinta plantillas de video ni mezclar notas internas con material publicable. Las semanas nuevas amplían los mecanismos —comparación, checklist, misión, pausa, guion, quiz, encuesta y pregunta abierta— para aprender después de publicar qué combinación conecta mejor.
- **Archivos:** `CONTENIDO-ESTATICO/generar_semanas_03_05.js`; `SEMANA-03/`, `SEMANA-04/` y `SEMANA-05/` completos; `CATALOGO/index.html`; `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`; `README.md`; `sistema_visual.json`; `MEDICION_PRODUCCION_SEMANAS_03_A_05.md` y `.json`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** el generador pasó `node --check`; los 63 SVG publicables pasaron `xmllint`; los 51 PNG de feed miden 1080×1350 y las doce historias miden 1080×1920; los tres masters miden 7000×6470. Los manifiestos suman 27 recursos y 63 páginas. Cada semana contiene nueve bloques de copy para cada una de las tres plataformas y nueve filas de calendario. El catálogo muestra 45 fichas y sus 45 referencias de imagen existen. Se inspeccionaron las seis presentaciones limpias de carrusel, las seis láminas conjuntas de imágenes e historias y los tres masters finales. El escaneo no encontró estados, tokens, notas de revisión ni metadata de producción dentro de los SVG publicables.
- **Resultado:** el sistema acumulado queda en 45 recursos y 105 artes públicos: diez carruseles con 70 páginas, quince imágenes y veinte historias. Semanas 03–05 agregan 27 recursos y 63 artes, todos pendientes de aprobación humana y sin publicar. La medición de producción conserva un checkpoint compartido; no se inventó una atribución de tokens por pieza.
- **Aprendizaje:** cuando las paletas aprobadas no están ordenadas semánticamente como oscuro, claro y acento, copiar sus posiciones puede producir bajo contraste aunque los colores individuales sean correctos. Separar la paleta documental del tema funcional y calcular el color del texto dentro de cada contenedor evita ese fallo. En producción por lote, los costos individuales solo deben publicarse cuando existen checkpoints reales.
- **Pendiente:** recibir aprobación o correcciones; confirmar fecha y apertura de la convocatoria presencial en Quito; configurar interacciones nativas; programar y publicar; registrar métricas reales a 24 horas, 72 horas y 7 días antes de decidir qué mecanismos, horarios o estilos se repiten.

### 2026-09-26 — VIDEO-13 activa y supera el gate de movimiento antes de la aprobación

- **Petición:** mantener abierto el editor de VIDEO-13 mientras se mide y verifica la primera versión antes de exportarla.
- **Punto de partida:** el editable ya había pasado correcciones de contraste y solapamiento, pero el gate ampliado informó `motion.enabled: false` porque los sidecars estaban asociados a las subcomposiciones y no a la composición raíz.
- **Cambio:** se añadió `editable-hyperframes-video-13/index.motion.json` con quince aserciones sobre aparición, orden y permanencia en cuadro del presentador, las cuatro escenas y los captions. Se ejecutó primero un gate integral de 15 muestras más todas las transiciones y después una repetición específica con el sidecar raíz activo. Se actualizaron las métricas y el resumen especializado.
- **Motivo:** no declarar validado el movimiento cuando el propio reporte mostraba que esa sección de la prueba estaba desactivada; la evidencia debe corresponder al gate que se afirma haber superado.
- **Archivos:** `VIDEO-13/editable-hyperframes-video-13/index.motion.json`, cinco sidecars de subcomposición, `VIDEO-13/METRICAS_PRODUCCION.md`, `VIDEO-13/RESUMEN_VIDEO_13.md`; y esta bitácora.
- **Validación:** el gate integral terminó con 0 errores de runtime, 0 problemas de layout y 18/18 contrastes. La repetición con movimiento activo recorrió 300 muestras y terminó con 0 errores y 0 advertencias. El preview siguió respondiendo HTTP 200 en el puerto 3013. La advertencia de empaquetado sobre una imagen local de 2,2 MB es informativa y no afecta el preview ni el render local.
- **Resultado:** la primera versión queda técnicamente limpia para revisión humana, con el editor todavía abierto. A los 2.252 s del objetivo, Codex reportó 365.224 tokens; la carpeta VIDEO-13 contenía 159 archivos y 60.496 KiB. No se ha exportado un MP4 final.
- **Aprendizaje:** un comando exitoso no basta si una sección del reporte figura desactivada. Las pruebas de movimiento de un proyecto compuesto deben tener un sidecar asociado a la composición raíz o validarse de forma independiente y explícita.
- **Pendiente:** recibir aprobación o correcciones del usuario; después ejecutar el gate posterior al cambio, renderizar, verificar decodificación, metadatos, loudness, hash y fotogramas, y cerrar las métricas finales.

### 2026-09-26 — VIDEO-13 consolida costos provisionales en formato legible por máquina

- **Petición:** medir cuánto tarda, cuántos tokens consume y todos los recursos observables de la producción de VIDEO-13.
- **Punto de partida:** `METRICAS_PRODUCCION.md` reunía checkpoints y mediciones por comando, pero no tenía agregados de CPU, desglose de almacenamiento por extensión ni un artefacto JSON reutilizable.
- **Cambio:** se sumaron trece procesos aislados con medición exacta, se inventariaron los 159 archivos por tipo, se identificaron los cinco activos realmente referenciados por la composición y se creó `METRICAS_PRODUCCION.json` con sistema, almacenamiento, estructura del montaje, QA, incidencias y datos no disponibles.
- **Motivo:** distinguir el tiempo total de trabajo de la suma de procesos computacionales y separar los activos del montaje de los snapshots, cachés y archivos de evidencia que también consumen disco.
- **Archivos:** `VIDEO-13/METRICAS_PRODUCCION.json`, `VIDEO-13/METRICAS_PRODUCCION.md`, `VIDEO-13/RESUMEN_VIDEO_13.md`; y esta bitácora.
- **Validación:** el inventario contó 159 archivos y 61.612.397 bytes lógicos; `du` reportó 60.496 KiB asignados. Trece procesos exactos sumaron 419,55 s de pared y 468,36 segundos-CPU. Los cinco activos referenciados sumaron 14.095.495 bytes. A los 2.377 s del objetivo, el contador reportó 392.140 tokens.
- **Resultado:** existe un checkpoint reproducible y estructurado del costo previo a aprobación. No se presenta como cifra final porque faltan la decisión del usuario, cualquier corrección, el render y su QA.
- **Aprendizaje:** el tamaño del producto y el costo del proceso son distintos: en este checkpoint los PNG de QA ocupan más que el máster intermedio. Las razones por segundo de video son descriptivas y no deben convertirse en una tarifa lineal sin más muestras.
- **Pendiente:** revisión del usuario, render final y cierre de tiempo, tokens, almacenamiento, hash, decodificación, loudness y fotogramas del MP4.

### 2026-09-26 — VIDEO-13 se aprueba, se exporta y corrige el gate de ingesta para futuros lotes

- **Petición:** cerrar VIDEO-13 después de la aprobación explícita, explicar por qué tomó más tiempo y evitar que los próximos lotes vuelvan a recorrer el maestro completo por cada video.
- **Punto de partida:** la edición de VIDEO-13 estaba aprobada en Studio y técnicamente limpia, pero no existía MP4 final. La revisión del proceso comprobó además que el lote 11–15 había quedado con `qa.human_review_completed=false`, correcciones sin resolver y sin proxies ni rangos fuente por video; por eso el montaje de VIDEO-13 repitió parte del análisis que debía pertenecer exclusivamente a la ingesta maestra.
- **Cambio:** se renderizó `VIDEO-13-FINAL.mp4` con calidad de entrega HDR; se verificaron metadatos, decodificación, loudness, hash y seis fotogramas. Se añadió `VIDEO-13/QA_FINAL.md`, se cerraron manifiesto, resumen y métricas. Para impedir la repetición, se creó `Serie-IA-Negocios-10-Videos/AGENTS.md` y `scripts/validar_lote_listo.py`; el gate exige revisión humana completa, pista fijada por escucha, take-map resuelto, proxy, rango fuente y preflight profundo de todos los videos antes de emitir `ingest-ready-NN-NN.json`. Se actualizaron `00-INGESTA/README.md` y `PROMPT_INGESTA_MAESTRA.md` con la regla específica para 16–20.
- **Motivo:** separar correctamente tres costos: recorrer/transcribir el lote una sola vez, editar cada video desde rangos ya fijados y exportar la composición. El fondo verde no fue el cuello de botella de VIDEO-13; se conservó el HLG original. El render fue costoso por la composición HDR por capas, mientras la repetición de análisis ocurrió porque el gate de ingesta no se había cerrado.
- **Archivos:** `VIDEO-13/editable-hyperframes-video-13/renders/VIDEO-13-FINAL.mp4`; `VIDEO-13/QA_FINAL.md`; `VIDEO-13/qa/final-render/`; `VIDEO-13/manifest.json`; `VIDEO-13/METRICAS_PRODUCCION.md` y `.json`; `VIDEO-13/RESUMEN_VIDEO_13.md`; `Serie-IA-Negocios-10-Videos/AGENTS.md`; `scripts/validar_lote_listo.py`; `00-INGESTA/README.md`; `PROMPT_INGESTA_MAESTRA.md`; y esta bitácora.
- **Validación:** el render tardó 1.233,02 s de pared, usó 1.850,77 s de CPU de usuario, 117,18 s de CPU de sistema y 906.428.416 bytes RSS máximos. El MP4 decodificó completo y confirmó 19,50 s, 1080×1920, 30 fps, 585 fotogramas, HEVC Main 10, `yuv420p10le`, BT.2020/HLG y AAC-LC estéreo 48 kHz. Pesa 12.631.803 bytes, su SHA-256 es `6ee143441088f43eb6aa0c318b6bf0505e9c8d8f91f7eaa893bda2f30491893e` y el audio mide −16,5 LUFS, 3,8 LU y −1,6 dBFS. Se inspeccionaron seis fotogramas del render. El nuevo gate se probó contra 11–15: terminó con error, reportó siete códigos únicos y no escribió un recibo inválido.
- **Resultado:** VIDEO-13 queda aprobado y exportado como entrega final local, sin publicación. VIDEO-11, VIDEO-12 y VIDEO-13 tienen ahora MP4 finales comprobados; sus tamaños y hashes fueron verificados. El lote 16–20 no podrá iniciar edición individual hasta producir un recibo válido de ingesta completa.
- **Aprendizaje:** una regla escrita no protege el flujo si no existe un gate ejecutable. El lote largo no debe penalizar cinco veces: la ingesta comparte transcripción, escucha y rangos; cada edición consume solo su proxy. HDR no reduce resolución ni equivale al fondo verde, pero sí puede multiplicar el costo de captura y composición final. Para comparar, VIDEO-14 o un lote futuro puede grabarse en 4K/30 SDR sin perder resolución, midiendo la diferencia antes de convertirlo en estándar.
- **Pendiente:** no hay cambios pendientes en VIDEO-13. VIDEO-14 y VIDEO-15 siguen fuera de este cierre. Antes del lote 16–20 se debe completar la ingesta maestra y emitir `ingest-ready-16-20.json`. Cualquier publicación o derivado de plataforma requiere autorización y QA propios.

### 2026-09-26 — Aprobación conjunta y cierre de VIDEO-11, VIDEO-12 y VIDEO-13

- **Petición:** confirmar que los tres videos mostrados quedan aprobados y que esta etapa está lista.
- **Punto de partida:** los tres MP4 finales existían y habían sido verificados individualmente; los manifiestos de VIDEO-11 y VIDEO-12 todavía conservaban el estado histórico `provisional`, aunque sus resúmenes y la bitácora ya registraban aprobaciones anteriores.
- **Cambio:** se registró la evidencia explícita `Excelente aprobados los 3 videos quedamos listos.`; se actualizaron los manifiestos de VIDEO-11 y VIDEO-12 con toma aprobada, archivo final, duración, tamaño y hash; y se creó `APROBACION_VIDEOS_11_13.md` como recibo conjunto. VIDEO-13 ya tenía su manifiesto final cerrado.
- **Motivo:** alinear la metadata operativa con la decisión humana y evitar que un proceso posterior interprete como provisionales entregas que ya fueron aprobadas.
- **Archivos:** `VIDEO-11/manifest.json`, `VIDEO-12/manifest.json`, `APROBACION_VIDEOS_11_13.md`; y esta bitácora.
- **Validación:** los tres archivos finales existen y no están vacíos. Se verificaron sus duraciones, tamaños y SHA-256: VIDEO-11 29,10 s / 15.430.694 bytes / `1d3c1a…a3e`; VIDEO-12 19,70 s / 15.346.856 bytes / `c0f584d1…3e8`; VIDEO-13 19,50 s / 12.631.803 bytes / `6ee14344…93e`.
- **Resultado:** VIDEO-11, VIDEO-12 y VIDEO-13 quedan aprobados y cerrados como entregas finales locales. No fueron publicados desde este flujo.
- **Aprendizaje:** la aprobación debe reflejarse tanto en la conversación como en los manifiestos y en un recibo verificable; de lo contrario, el estado visual y el estado operativo pueden divergir.
- **Pendiente:** ninguno para estos tres videos. VIDEO-14 y VIDEO-15 pertenecen a la siguiente etapa; publicación o derivados requieren autorización separada.

### 2026-09-26 — Las 105 piezas estáticas explican ahora la promesa de la marca

- **Petición:** sustituir la firma aislada `NEGOCIO AUMENTADO` por una versión más visible y explicativa para que la audiencia entienda por qué está aprendiendo los temas del sistema. El texto acordado fue `NEGOCIO AUMENTADO / IA PARA CRECER Y VENDER`.
- **Punto de partida:** las cinco semanas ya contenían 45 recursos y 105 artes, pero la firma ocupaba una sola línea de 22 px y funcionaba como nombre sin explicar el objetivo comercial común.
- **Cambio:** la firma pasó a un lockup de dos líneas: marca de 25 px, descriptor de 18 px y línea cyan–magenta de 292 px. Se actualizaron `generar_semana_01.js`, `generar_semana_02.js` y `generar_semanas_03_05.js`, junto con el sistema visual, el plan y el catálogo. Se regeneraron las cinco semanas completas, sus fuentes, PNG, tableros y masters. Se añadieron mediciones separadas para esta actualización sin alterar las mediciones históricas de creación.
- **Motivo:** `NEGOCIO AUMENTADO` identifica el proyecto, pero no expresa por sí solo el beneficio. `IA PARA CRECER Y VENDER` conecta sistemas, automatización, contenido, diagnóstico y oferta con una finalidad reconocible sin afirmar que el crecimiento o las ventas estén garantizados o acelerados.
- **Archivos:** `CONTENIDO-ESTATICO/generar_semana_01.js`, `generar_semana_02.js`, `generar_semanas_03_05.js`, `sistema_visual.json`, `SISTEMA_VISUAL_ESTATICO.md`, `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`, `CATALOGO/index.html`, las carpetas `SEMANA-01/` a `SEMANA-05/`, sus cinco documentos QA, `MEDICION_ACTUALIZACION_FIRMA_2026-09-26.md` y `.json`, `CHANGELOG.md`; y esta bitácora.
- **Validación:** los tres generadores pasaron `node --check`; los 105 SVG pasaron `xmllint`; cada SVG público contiene exactamente una segunda línea visible `IA PARA CRECER Y VENDER`; los 105 PNG mantienen sus dimensiones correctas. Se inspeccionaron carruseles, imágenes e historias de las cinco semanas y los cinco masters. El lockup no cruza titulares, figuras, contenedores ni interacciones. El catálogo conserva 45 fichas y 45 referencias existentes. Los nuevos SHA-256 y pesos de los masters quedaron registrados en cada QA.
- **Resultado:** las cinco semanas comparten ahora una promesa descriptiva visible y consistente. El contenido publicable continúa limpio: no contiene estados, hipótesis, tokens ni notas internas. Todo permanece pendiente de aprobación humana y sin publicar.
- **Aprendizaje:** una marca puede ser memorable y aun así no explicar el beneficio. Un descriptor estable reduce esa ambigüedad sin obligar a reescribir cada titular; debe ser corto, honesto y legible cuando una página se comparte fuera de su carrusel.
- **Pendiente:** revisión del usuario. Después de aprobar el nuevo lockup podrán conservarse estas exportaciones para programación; las interacciones nativas y la publicación siguen pendientes.

### 2026-09-26 — El catálogo se convierte en centro editorial y simulador multiplataforma

- **Petición:** reunir planificación, copies, metadata, accesos a exportados, filtros, calendario, simulación del feed y los treinta videos en un solo HTML; permitir revisar Instagram, Facebook, TikTok y YouTube Shorts como plan completo, por semana o por día, alternando videos con carruseles e imágenes.
- **Punto de partida:** `CATALOGO/index.html` mostraba 45 fichas estáticas con búsqueda básica y filtros por formato. No incluía los treinta videos, copies copiables, accesos a carpetas, planificación conjunta, simulación por plataforma ni la sexta semana requerida por una cadencia de cinco videos semanales.
- **Cambio:** se creó `generar_catalogo_dashboard.js`, que construye `CATALOGO/catalog-data.json` y un panel autocontenido desde los manifiestos y calendarios existentes. El panel incorpora cuatro vistas —planificación, recursos, simulación y videos—; filtros por texto, semana, fecha y formato; selector de copy por plataforma; botones para copiar, abrir exportado, carpeta, lámina y manifiesto; fichas detalladas; y simulaciones específicas de Instagram, Facebook, TikTok y Shorts. VIDEO-01 a VIDEO-30 se distribuyen en seis semanas. Semanas 01–05 emparejan cada estático con un video posterior para producir un patrón descendente `video / estático`. Semana 06 reserva C11, C12, I16–I18 y H21–H24 como espacios pendientes, sin inventar artes ni copies. Se añadió un enlace local `CONTENIDO-ESTATICO/SERIE` para que miniaturas, MP4 y carpetas fuera de la raíz original del servidor puedan abrirse desde el catálogo. Los tres generadores estáticos regeneran ahora el panel avanzado.
- **Motivo:** el usuario necesita operar el sistema sin abrir archivos uno por uno y, sobre todo, anticipar la apariencia del contenido publicado. Separar la simulación por plataforma evita representar Shorts como si aceptara carruseles o imágenes. Reservar la sexta semana hace visible el faltante editorial que aparecería al repartir treinta videos a cinco por semana.
- **Archivos:** `CONTENIDO-ESTATICO/generar_catalogo_dashboard.js`; `CATALOGO/index.html`, `catalog-data.json` y `QA_DASHBOARD.md`; enlace `CONTENIDO-ESTATICO/SERIE`; `generar_semana_01.js`, `generar_semana_02.js`, `generar_semanas_03_05.js`; `README.md`, `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`, `CHANGELOG.md`; y esta bitácora.
- **Validación:** los cuatro scripts JavaScript pasaron `node --check`. El inventario generado contiene 75 recursos verificables, 30 videos, 20 historias generadas y seis semanas. Las rutas probadas de miniatura, MP4 y carpeta respondieron HTTP 200. Una auditoría confirmó en las seis semanas el patrón cronológico ascendente `estático / video`, que aparece como `video / estático` en el feed descendente. Se inspeccionaron en navegador la planificación, la biblioteca, Instagram completo, Instagram/Facebook/TikTok/Shorts para Semana 01, la vista diaria del 28 de septiembre y Semana 06. Instagram, Facebook y TikTok mostraron diez publicaciones y cuatro historias; Shorts mostró únicamente cinco videos; la vista diaria mostró dos publicaciones y una historia. Semana 06 mostró cinco espacios estáticos y cuatro historias como pendientes, sin fingir artes terminadas. Las miniaturas externas inicialmente no cargaban; se corrigieron y una segunda inspección confirmó su aparición. No se modificaron las 105 artes públicas.
- **Resultado:** existe un centro editorial navegable que muestra el plan conjunto, el estado real de los videos, los copies disponibles y el orden visual por plataforma. Semana 06 queda completa como estructura de planificación, pero sus nueve espacios editoriales continúan pendientes de producción. Nada fue publicado.
- **Aprendizaje:** una biblioteca de archivos no sustituye una vista de programación. Para evaluar la estética del perfil hay que ordenar por fecha y hora exactamente como lo hará la plataforma, y distinguir qué formatos existen en cada canal. La cadencia de treinta videos reveló una sexta semana que el banco estático original de cinco semanas no cubría.
- **Pendiente:** desarrollar y aprobar C11, C12, I16–I18 y H21–H24; confirmar horarios, copies y CTA de los videos; programar solo después del QA y registrar métricas reales a 24 horas, 72 horas y 7 días.

### 2026-09-26 — Semana 06 completa el horizonte editorial de seis semanas

- **Petición:** producir todo el contenido que faltaba para que las seis semanas quedaran completas, variando los temas para hablar de accesibilidad, creación, diferenciación, confianza, producto y resultados sin repetir el enfoque de las semanas anteriores.
- **Punto de partida:** Semanas 01–05 reunían 45 recursos estáticos y 105 artes públicos. El centro editorial distribuía treinta videos en seis semanas, pero Semana 06 todavía mostraba dos carruseles, tres imágenes y cuatro historias como espacios planificados sin diseño, copy ni archivos exportados.
- **Cambio:** se amplió `generar_semanas_03_05.js` para conservar compatibilidad histórica y producir también Semana 06. Se crearon C11 `Diseña contenido que funcione sin sonido`, C12 `Construye una ventaja que la IA no copie sola`, I16 `Crear será barato, elegir será valioso`, I17 `No vendas en cada publicación`, I18 `La pregunta antes de vender` y H21–H24. Los nueve recursos incluyen 21 SVG editables, 21 PNG publicables, tableros limpios y de revisión, copies para Instagram, TikTok y Facebook, calendario, manifiesto, medición, QA y un máster de 7000×6470 px. Se añadieron los temas T27 y T28 desde las paletas aprobadas, se actualizó el horizonte del sistema visual y el catálogo dejó de crear placeholders cuando existe un manifiesto real de Semana 06.
- **Motivo:** la cadencia de cinco videos semanales exige seis semanas para distribuir los treinta videos. Completar el mismo horizonte con dos carruseles, tres imágenes y cuatro historias por semana permite evaluar el feed intercalado sin huecos y amplía los ángulos editoriales más allá de herramientas o automatización.
- **Archivos:** `CONTENIDO-ESTATICO/generar_semanas_03_05.js`; `SEMANA-06/` completo; `generar_catalogo_dashboard.js`; `sistema_visual.json`; `README.md`; `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`; `CATALOGO/index.html`, `catalog-data.json` y `QA_DASHBOARD.md`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** ambos generadores pasaron `node --check`; los 21 SVG públicos de Semana 06 pasaron `xmllint`; los 17 PNG de feed miden 1080×1350 y las cuatro historias 1080×1920. Una auditoría confirmó nueve recursos, 21 páginas, nueve filas de calendario, 27 bloques de copy y cero términos internos prohibidos en los SVG públicos. Se inspeccionaron visualmente los dos carruseles, las tres imágenes, las cuatro historias y el máster. La primera inspección detectó elementos decorativos demasiado próximos a los titulares de C11 y C12; se desplazaron al pie y se regeneró antes del cierre. En navegador, la simulación de Semana 06 mostró diez celdas de feed, cuatro historias y cero artes pendientes. El catálogo final contabiliza 54 recursos estáticos, 30 videos, 84 recursos navegables y 126 artes públicos.
- **Resultado:** el horizonte editorial queda completo en seis semanas con doce carruseles, dieciocho imágenes y veinticuatro historias, además de treinta espacios de video. Semana 06 ya no tiene piezas por diseñar y sus artes publicables están separados de la metadata operativa. Los 54 recursos estáticos permanecen pendientes de aprobación humana; nada fue publicado ni medido en redes.
- **Aprendizaje:** una vista agregada puede descubrir faltantes que no aparecen al revisar carpetas por separado. También confirma que el QA visual debe ejecutarse después del render: una composición técnicamente válida puede conservar una interferencia decorativa que solo resulta evidente en la lámina completa. El generador debe preferir recursos reales y crear placeholders únicamente cuando no existe un manifiesto verificable.
- **Pendiente:** recibir aprobación o correcciones de Semana 06 y del conjunto estático; confirmar horarios, copies y CTA de los videos; configurar las interacciones nativas de historias; programar y publicar; y registrar métricas reales a 24 horas, 72 horas y 7 días antes de atribuir resultados a un estilo, tema o mecanismo.

### 2026-09-26 — VIDEO-14 y VIDEO-15 se corrigen, se renderizan y quedan listos para entrega

- **Petición:** corregir VIDEO-14 y VIDEO-15 sin otra ronda de preview, aplicar como reglas permanentes que ningún texto quede fuera, cortado o tapado, maximizar la tipografía para móvil cuando exista espacio, eliminar silencios extensos, conservar el rostro libre y asegurar efectos sonoros perceptibles pero subordinados a la voz; entregar directamente los renders finales después de revisarlos varias veces.
- **Punto de partida:** los previews anteriores habían pasado comprobaciones estructurales, pero la revisión del usuario reveló defectos que esos pases no habían evitado. VIDEO-14 mostraba tipografía fina, un rótulo lateral confuso, similitud visual con VIDEO-15 y pausas largas. VIDEO-15 conservaba un silencio de aproximadamente 5.2 s entre 00:18 y 00:23, otras dos pausas superiores al estándar, una cola muda y un cierre gráfico no pronunciado. No existían entregas finales válidas de ninguno.
- **Cambios:** se convirtió el estándar visual y auditivo en un gate obligatorio de tres pasadas y se documentó en `ESTANDAR_QA_PREAPROBACION.md` y `AGENTS.md`. VIDEO-14 se recortó a cinco rangos completos, quedó en 23.3 s y se rediseñó con Archivo Black/Inter 900, burbujas, waveform, avatar y paleta navy/cobalto/coral; se retiraron `FUERA DE LA PANTALLA`, League Gothic y las tarjetas mecánicas. VIDEO-15 se redujo a cuatro bloques, quedó en 21.1 s, eliminó el silencio reportado, dos pausas adicionales, la cola muda y la frase no pronunciada; se retimaron escenas, captions y cinco SFX. Ambos se exportaron en HDR HLG. La primera exportación de VIDEO-14 quedó baja de audio y se preservó como revisión; la entrega definitiva normaliza el audio sin recomprimir la imagen.
- **Motivo:** un check técnico no sustituye la revisión estética y narrativa. Las reglas acordadas deben funcionar como condiciones de salida y no depender de que el usuario vuelva a detectar textos pequeños, desbordes, oclusiones, silencios o efectos imperceptibles.
- **Archivos afectados:** `Serie-IA-Negocios-10-Videos/AGENTS.md`; `ESTANDAR_QA_PREAPROBACION.md`; `VIDEO-14/editable-hyperframes-video-14/`; `VIDEO-14/QA_DRAFT.md`; `VIDEO-14/QA_FINAL.md`; `VIDEO-14/METRICAS_PRODUCCION.md` y `.json`; `VIDEO-14/manifest.json`; `VIDEO-15/editable-hyperframes-video-15/`; `VIDEO-15/QA_FINAL.md`; `VIDEO-15/METRICAS_PRODUCCION.md` y `.json`; `VIDEO-15/manifest.json`; `scripts/qa_post_render.py`; las evidencias `00-INGESTA/qa-post-render-14-15-final-2026-09-26/` y `00-INGESTA/qa-post-render-14-final-audiofix-2026-09-26/`; y esta bitácora.
- **Validación:** los checks finales de HyperFrames pasaron runtime, layout y movimiento; VIDEO-14 obtuvo contraste 25/25 y VIDEO-15 terminó sin errores ni advertencias. Se inspeccionaron las hojas de contacto finales: rostro libre, textos grandes, cajas completas y sin desbordes observados. Los dos MP4 decodificaron completos. VIDEO-14 mide 23.300 s, 20,070,702 bytes, HEVC Main 10 BT.2020/HLG, −16.2 LUFS, LRA 3.4 LU, pico −1.4 dBFS y SHA-256 `084d116584731143071ab640bf6b457e23889362a6ae0e624e25dfc4dd38a84a`. VIDEO-15 mide 21.100 s, 12,474,393 bytes, HEVC Main 10 BT.2020/HLG, −16.5 LUFS, LRA 2.9 LU, pico −1.4 dBFS y SHA-256 `21b8a0814096bcd35e0768088957bf1324dbda63279c9a0b70a60f4911a17a13`; su silencio máximo medido es 0.549 s. El render de VIDEO-14 tardó 392.68 s y el de VIDEO-15 471.06 s; al correr en paralelo, la exportación estuvo dominada por los 471.06 s de VIDEO-15.
- **Resultado:** `VIDEO-14-FINAL.mp4` y `VIDEO-15-FINAL.mp4` quedan como entregas finales locales verificadas. La instrucción explícita del usuario autorizó el cierre directo sin otra aprobación intermedia. No se afirma escucha humana independiente de las reproducciones completas; queda `por confirmar`. Ningún archivo fue publicado.
- **Aprendizaje:** el gate de salida necesita tres capas separadas: geometría y legibilidad, audio y ritmo, e integración completa. El silencio debe medirse sobre el render, no solo sobre el proxy; los captions deben ocupar el espacio disponible sin invadir rostro ni safe zones; y un primer render que falla loudness debe conservarse como revisión, corregirse y someterse otra vez a QA antes de reemplazar la entrega.
- **Pendiente:** publicación, versiones específicas por plataforma o cualquier nueva transformación requieren autorización separada. Aplicar el mismo gate triple antes de presentar VIDEO-16 en adelante.

### 2026-09-26 — VIDEO-14 y VIDEO-15 se editan en paralelo desde la ingesta cerrada

- **Petición:** producir VIDEO-14 y VIDEO-15 en paralelo, conservar el estándar profesional definido para el lote y medir cuánto tarda cada fase hasta la exportación final.
- **Punto de partida:** el máster 11–15 ya existía, pero la ingesta compartida todavía necesitaba cerrar la escucha humana, fijar los rangos y emitir un recibo válido. VIDEO-14 y VIDEO-15 tenían planes y recursos preliminares, sin editables completos ni entregas finales.
- **Cambio:** se cerró el gate compartido de ingesta 11–15 y se montaron dos proyectos HyperFrames en paralelo. VIDEO-14 quedó en 33,90 s después de sustituir un primer corte de 21,47 s que truncaba terminaciones; utiliza cuatro escenas, un recurso de conversación, captions grandes al pecho y dos acentos SFX. VIDEO-15 quedó en 30,40 s después de retirar el `Sí` repetido entre dos tomas; utiliza cinco escenas, una máquina visual para explicar la automatización prematura, seis grupos de captions y tres acentos SFX. Ambos conservan el HLG BT.2020 original, sin aplicar automáticamente la corrección verde de VIDEO-11. Los previews quedaron activos en los puertos 3014 y 3015.
- **Motivo:** probar el flujo paralelo sin repetir el recorrido del máster, medir por separado preparación, ensamblaje, codificación, validación y render, y mantener las reglas ya aprobadas: cabeza libre, texto móvil grande, recursos semánticos y ninguna referencia interna visible.
- **Archivos:** `Serie-IA-Negocios-10-Videos/00-INGESTA/ingest-ready-11-15.json`; `VIDEO-14/editable-hyperframes-video-14/`, `VIDEO-14/QA_DRAFT.md`, `VIDEO-14/METRICAS_PRODUCCION.md` y `.json`, `VIDEO-14/qa/video14-final-snapshot-contact-sheet.png`; `VIDEO-15/editable-hyperframes-video-15/`, `VIDEO-15/METRICAS_PRODUCCION.md` y `.json`; los proxies y rangos fuente de VIDEO-14 y VIDEO-15; y esta bitácora.
- **Validación:** la ingesta terminó `pass`. VIDEO-14 confirmó por ASR 61 palabras y cinco frases completas; su máster de trabajo mide 33,901 s, 1080×1920, HEVC Main10 y BT.2020/HLG. Su check final pasó runtime, layout y movimiento, con contraste 33/33; se inspeccionaron cinco snapshots. VIDEO-15 confirmó 30,40 s, HEVC Main10 BT.2020/HLG; su check final pasó runtime, layout, movimiento y contraste sin errores ni advertencias, y su preview se reprodujo en vivo hasta 00:13. La aprobación del montaje completo y los MP4 de entrega todavía no existen.
- **Resultado:** los dos editables están listos simultáneamente para revisión humana en Studio. La preparación medida de VIDEO-14 fue 8 min 10 s, su ensamblaje y corrección 18 min 15 s y la validación final 1 min 27 s. VIDEO-15 acumuló 29 min 33 s desde el inicio del agente, incluyendo espera de revisión de ingesta; desde el lock de ingesta hasta el preview validado transcurrieron 13 min 02 s. Estas cifras no incluyen aún los renders finales.
- **Aprendizaje:** paralelizar preparación y diseño sí reduce tiempo de calendario, pero los límites de corte siguen necesitando una verificación lingüística: un corte técnicamente válido puede truncar una palabra o conservar un marcador descartado. Consumir rangos ya fijados evita volver a recorrer nueve minutos por video. Los renders HDR deben medirse aparte y no conviene atribuir sus tiempos a la edición creativa.
- **Pendiente:** recibir aprobación visual explícita de VIDEO-14 y VIDEO-15; después renderizar las dos entregas, verificarlas por decodificación completa, metadatos, loudness, hash y fotogramas, cerrar las métricas y actualizar manifiestos, resúmenes y QA final. No se ha publicado ninguno.

### 2026-09-26 — El QA post-render se automatiza sin convertir un pase técnico en aprobación

- **Petición:** acelerar el cierre de VIDEO-14, VIDEO-15 y lotes futuros con una comprobación reutilizable que acepte uno o más MP4 finales y reúna en una sola ejecución metadatos, decodificación completa, loudness, hash y evidencia visual.
- **Punto de partida:** esas comprobaciones ya se realizaban para entregas anteriores, pero mediante comandos y registros separados. Esto repetía preparación manual y hacía más difícil comparar tiempos entre videos sin omitir una etapa.
- **Cambio:** se creó `scripts/qa_post_render.py` con entrada múltiple, máximo seguro de dos archivos en paralelo, directorio de evidencia nuevo y rechazo de sobrescrituras. Por cada MP4 ejecuta `ffprobe`, decodificación completa con `ffmpeg -xerror`, medición EBU R128, SHA-256 antes y después, seis capturas uniformes y una hoja de contacto 3×2; después escribe `evidence.json`, `EVIDENCE.md`, `summary.json` y `SUMMARY.md`. El script conserva explícitamente `approval_status: not_evaluated`. Se documentó el uso y sus códigos de salida en `scripts/README.md`.
- **Motivo:** el QA técnico es repetible y puede automatizarse; la aprobación editorial, el color percibido y la revisión completa siguen requiriendo juicio humano. Separar ambos estados evita declarar aprobado un archivo únicamente porque decodifica.
- **Archivos:** `Serie-IA-Negocios-10-Videos/scripts/qa_post_render.py`, `scripts/README.md`, `scripts/qa-smoke-video-13/`; y esta bitácora.
- **Validación:** `python3 -m py_compile` y `--help` pasaron. La prueba sin modificar `VIDEO-13-FINAL.mp4` terminó `PASS` en 7,542 s: `ffprobe` 0,081 s, decodificación completa 2,160 s, EBU R128 0,178 s, seis fotogramas 4,506 s y hoja de contacto 0,547 s. Confirmó 19,5 s, 1080×1920, 30 fps, HEVC Main 10, HLG BT.2020, AAC 48 kHz estéreo, −16,5 LUFS, 3,8 LU y −1,6 dBFS. El SHA-256 anterior y posterior coincidió en `6ee143441088f43eb6aa0c318b6bf0505e9c8d8f91f7eaa893bda2f30491893e`; tamaño, mtime e inode tampoco cambiaron. La hoja de contacto contiene seis imágenes y se inspeccionó visualmente. Una segunda invocación sobre el mismo directorio fue rechazada con código 2, demostrando que no sobrescribe la evidencia.
- **Resultado:** existe una etapa de QA post-render única y medible que puede ejecutarse sobre VIDEO-14 y VIDEO-15 juntos después de su exportación. La prueba solo valida la automatización con VIDEO-13; no reabre ni cambia su aprobación previa.
- **Aprendizaje:** automatizar evidencia reduce trabajo repetido, pero un `PASS` técnico debe permanecer separado del visionado y de la decisión humana. Recalcular el hash al final y prohibir sobrescrituras hace el proceso auditable sin tocar la entrega.
- **Pendiente:** ejecutar el script sobre VIDEO-14 y VIDEO-15 cuando existan sus MP4 finales; revisar sus hojas de contacto y reproducciones completas; registrar aprobación o correcciones por separado. Ninguno se renderizó ni aprobó desde esta automatización.

### 2026-09-26 — Los 54 recursos estáticos se aprueban y el catálogo pasa a un visor visual

- **Petición:** registrar la aprobación conjunta de todas las imágenes, carruseles e historias; sincronizar la planificación y la documentación; y hacer que el HTML represente las piezas de forma fiel, mostrando solo la portada de cada carrusel en la biblioteca y permitiendo navegar sus páginas o abrir su lámina maestra.
- **Punto de partida:** las 126 artes públicas ya existían y estaban limpias, pero los 54 manifiestos estáticos y varias láminas de revisión conservaban estados pendientes. El catálogo priorizaba metadata y miniaturas recortadas; los carruseles no ofrecían una lectura clara de portada, páginas individuales y máster como tres niveles distintos.
- **Cambio:** se creó `registrar_aprobacion_contenido_estatico.js` y un recibo conjunto de aprobación en JSON y Markdown. Se sincronizaron los 54 manifiestos individuales, los seis manifiestos semanales, copies, QA, mediciones y sistema visual. Se actualizaron 72 láminas internas —54 tableros individuales, doce tableros conjuntos y seis másters semanales— sin insertar metadata en las 126 artes públicas. El generador del catálogo se rediseñó como biblioteca visual: respeta la proporción completa 4:5 o 9:16, muestra únicamente la portada de los doce carruseles, abre un detalle con siete miniaturas numeradas, permite seleccionar cada página y conserva un acceso directo a la lámina completa. La metadata, el copy y la programación viven dentro del detalle y no se superponen a las artes. También se ajustaron las simulaciones de Instagram, Facebook, TikTok y Shorts y se añadieron enlaces directos a biblioteca, feed, planificación y videos.
- **Motivo:** separar con claridad la pieza que verá la audiencia de la información operativa que necesita el equipo, facilitar la revisión sin abrir archivos uno por uno y evitar que el catálogo parezca un tablero técnico en lugar de una aproximación visual al contenido publicado.
- **Archivos:** `CONTENIDO-ESTATICO/registrar_aprobacion_contenido_estatico.js`; `APROBACION_CONTENIDO_ESTATICO.md` y `.json`; `generar_catalogo_dashboard.js`; `README.md`; `SISTEMA_VISUAL_ESTATICO.md`; `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`; `PLAN_COMERCIAL_21_DIAS.md`; `sistema_visual.json`; los manifiestos, copies, QA, mediciones, tableros y másters de `SEMANA-01/` a `SEMANA-06/`; `CATALOGO/index.html`, `catalog-data.json` y `QA_DASHBOARD.md`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** el inventario final contiene 84 recursos navegables: 54 estáticos y 30 videos. Los 54 estáticos figuran aprobados; existen 126 SVG públicos, doce carruseles con siete páginas cada uno y cero rutas enlazadas faltantes. Los scripts pasaron `node --check`, los SVG pasaron `xmllint` y el escaneo no encontró estados, tokens ni notas internas dentro de las artes públicas. En navegador se comprobó la apertura de C01 desde su portada, la selección de la miniatura 02 con actualización visible a `Página 2 de 7`, el acceso a la lámina completa y la ausencia de errores de consola.
- **Resultado:** los 54 recursos estáticos quedan aprobados localmente y documentados como conjunto; no fueron publicados. El catálogo queda abierto como visor visual y mantiene los estados reales de los videos: VIDEO-11, VIDEO-12 y VIDEO-13 están aprobados; no se afirma que los treinta videos estén terminados.
- **Aprendizaje:** una vista de perfil y una revisión de diseño cumplen funciones distintas. La primera debe conservar el ritmo y el recorte aproximado de la plataforma; el detalle debe mostrar el arte completo. En carruseles, portada, navegación por páginas y máster son capas complementarias. Las miniaturas numeradas resultaron una interacción más simple y verificable que controles laterales redundantes.
- **Pendiente:** confirmar horarios, copies y CTA antes de programar; configurar las interacciones nativas que correspondan; publicar únicamente con autorización; registrar métricas reales a 24 horas, 72 horas y 7 días; y terminar o aprobar los videos restantes según su estado real.

### 2026-09-26 — C01 prueba un lenguaje híbrido de fotografía realista e infografía

- **Petición:** explorar otras versiones de los carruseles incorporando caras y situaciones realistas para evitar que algunos fondos de color y composiciones SVG se perciban vacíos.
- **Punto de partida:** C01 estaba aprobado como carrusel completamente vectorial de siete páginas. Su jerarquía y recurso práctico funcionaban, pero no incluía personas ni un contexto cotidiano que facilitara identificación emocional.
- **Cambio:** se creó `C01-VARIANTE-FOTOGRAFICA` sin modificar la versión aprobada. Se generaron tres fotografías documentales de personas latinoamericanas en situaciones de caos operativo, revisión de una cotización y claridad posterior. Las páginas 01, 02, 03, 05 y 07 incorporan fotografía; las páginas 04 y 06 conservan el mapa y la plantilla vectoriales. Se mantuvieron copy, CTA, paleta, secuencia y jerarquía. También se creó un generador reproducible, siete SVG, siete PNG, una lámina horizontal y documentación de prompts e hipótesis.
- **Motivo:** probar una sola variable principal —el tratamiento visual— y comprobar si el realismo aporta identificación y densidad visual sin perjudicar la lectura ni convertir el carrusel en una colección decorativa de fotografías.
- **Archivos:** `CONTENIDO-ESTATICO/generar_c01_variante_fotografica.js`; `SEMANA-01/C01-VARIANTE-FOTOGRAFICA/` con `assets/`, `source/`, `exports/`, `review/`, `manifest.json` y `README.md`; `CONTENIDO-ESTATICO/README.md`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** el generador pasó `node --check`; se produjeron siete PNG de 1080×1350 y una lámina de 7800×1410. Se inspeccionó la secuencia completa: las caras no quedan cubiertas por los titulares, los textos permanecen dentro de sus contenedores, el mapa y la plantilla mantienen la máxima limpieza y las fotografías no contienen texto, logos ni notas internas visibles.
- **Resultado:** existe una variante fotográfica completa de C01 lista para revisión humana. Permanece pendiente de aprobación y no fue añadida todavía como alternativa pública en el catálogo ni publicada en redes.
- **Aprendizaje:** la fotografía funciona mejor cuando demuestra el problema o la transformación; los diagramas siguen siendo superiores para explicar pasos y entregar plantillas. El equilibrio útil no es reemplazar todos los vectores, sino alternar identificación emocional con claridad operativa.
- **Pendiente:** recibir aprobación o correcciones; si se aprueba, incorporar la alternativa al catálogo y definir qué otros carruseles se benefician de fotografía completa, recortes de personas o escenas de producto. Cualquier comparación de rendimiento requerirá controlar tema, horario y CTA.

### 2026-09-26 — VIDEO-14 gana respiración superior y corrige la separación tipográfica

- **Petición:** aprovechar el espacio disponible encima de la cabeza para bajar y separar los elementos superiores de VIDEO-14, impedir que vuelvan a verse amontonados y revisar dos palabras de subtítulos que aparecían pegadas.
- **Punto de partida:** `VIDEO-14-FINAL.mp4` existía como entrega local verificada, pero la captura enviada por el usuario mostraba dos burbujas del hook separadas por solo 4 px mientras quedaba espacio útil más abajo. Los captions mezclaban nodos de texto anónimos y etiquetas `<b>` dentro de un contenedor flex; el espacio escrito en HTML no garantizaba separación visual entre ambos nodos.
- **Cambios:** la primera burbuja se movió a `y=96–206`, la segunda a `y=262–396` y la onda a `y=438–542`, dejando separaciones reales de 56 px y 42 px entre módulos. Los diez captions se reestructuraron con nodos `<span>` explícitos y `column-gap:.22em`; se revisaron las siete fronteras donde cambia el color o peso. La regla de respiración superior de 24–32 px mínimos y la separación CSS obligatoria entre nodos de caption se añadieron a `AGENTS.md`, `ESTANDAR_QA_PREAPROBACION.md` y `frame.md`. El proyecto pasó de HyperFrames 0.8.78 a 0.8.79. La entrega anterior se conservó como revisión y se generó un nuevo render.
- **Motivo:** no basta con que las cajas no se solapen: si el cuadro ofrece espacio, la composición debe distribuirlo para construir jerarquía y descanso visual. Tampoco debe dependerse de espacios implícitos entre nodos flex para separar palabras.
- **Archivos afectados:** `Serie-IA-Negocios-10-Videos/AGENTS.md`; `ESTANDAR_QA_PREAPROBACION.md`; `VIDEO-14/editable-hyperframes-video-14/package.json`; `frame.md`; `compositions/scene-hook.html`; `compositions/captions-es.html`; `cut-plan.json`; `renders/VIDEO-14-FINAL.mp4`; `renders/revisions/VIDEO-14-FINAL-v2-before-spacing-fix.mp4`; `renders/revisions/VIDEO-14-FINAL-v3-spacingfix-audio-bajo.mp4`; `qa/final-spacing-pass/`; `VIDEO-14/QA_FINAL.md`; `METRICAS_PRODUCCION.md` y `.json`; `manifest.json`; evidencias `00-INGESTA/qa-post-render-14-spacingfix-2026-09-26/` y `qa-post-render-14-spacingfix-final-2026-09-26/`; y esta bitácora.
- **Validación:** lint pasó con 0 errores y 0 advertencias. `hyperframes check --strict` pasó runtime, layout y motion; contraste 29/29. Se inspeccionaron diez snapshots dirigidos que cubren todos los captions y la hoja final de seis fotogramas. El MP4 definitivo decodificó completo, conserva 23.300 s, 1080×1920, 30 fps, HEVC Main 10, `yuv420p10le` y BT.2020/HLG. Pesa 19,845,181 bytes, su SHA-256 es `76c87c7416646ec53f4f16dccdebd421069e046dc5fe6ab53c63a0ac4fca2840` y el audio mide −16.2 LUFS, LRA 3.4 LU y pico verdadero −1.5 dBFS. El render HDR tardó 308.42 s; su salida directa de −23.2 LUFS fue archivada y el ajuste final normalizó solo audio, copiando intacto el stream de video.
- **Resultado:** `VIDEO-14-FINAL.mp4` queda reemplazado por la revisión con respiración superior y separación tipográfica explícita. No se observaron textos fuera de caja, palabras concatenadas ni elementos cubriendo cabeza, ojos o boca. No fue publicado.
- **Aprendizaje:** los espacios en el HTML pueden desaparecer entre ítems flex; el gap debe ser una propiedad verificable. Para layout, la ausencia de colisión es apenas el mínimo: el QA también debe evaluar cómo se reparte el aire disponible. Un render nuevo debe volver a pasar loudness porque el mezclador puede reproducir el mismo nivel bajo aunque el cambio haya sido solamente visual.
- **Pendiente:** escucha humana independiente de la reproducción completa `por confirmar`; publicación o versiones por plataforma requieren autorización separada.

### 2026-09-26 — VIDEO-15 corrige el encabezado y devuelve antes la autoridad al presentador

- **Petición:** separar los elementos superiores de VIDEO-15, impedir que la línea amarilla atraviese las letras y reducir el tiempo del recurso de máquina para volver al rostro antes de perder atención y autoridad.
- **Punto de partida:** la entrega anterior medía 21.100 s y tenía SHA-256 `21b8a0814096bcd35e0768088957bf1324dbda63279c9a0b70a60f4911a17a13`. La captura del usuario mostraba el encabezado comprimido contra el borde y una regla amarilla sobre `LO QUE NO ENTIENDES`; la imagen de máquina permanecía hasta el cierre en lugar de funcionar como un acento breve.
- **Cambios:** la franja superior pasó de 276 a 330 px; la tarjeta inicial se bajó, amplió y redistribuyó, conservando tipografía móvil de 42–72 px y dejando la regla fuera del área tipográfica. Los encabezados de las escenas intermedias también se bajaron. El recurso de máquina se convirtió en un bloque de 1.85 s entre 12.652 y 14.502 s; después vuelve el presentador. Se añadió una máscara temporizada de 430 px para limpiar cualquier residuo de la escena anterior en la composición HDR. La regla de recursos a pantalla completa de 1.5–2.5 s y regreso al presentador, y la prohibición de líneas sobre letras, se incorporaron a `AGENTS.md` y `ESTANDAR_QA_PREAPROBACION.md`.
- **Motivo:** los recursos de apoyo deben reforzar una frase sin reemplazar durante demasiado tiempo a quien habla. La autoridad y la atención se recuperan al volver al rostro; las líneas decorativas solo funcionan si no reducen legibilidad.
- **Archivos afectados:** `VIDEO-15/editable-hyperframes-video-15/index.html`; `frame.md`; `compositions/scene-hook.html`, `scene-error.html`, `scene-inspect.html` y `scene-consequence.html`; `package.json`; `cut-plan.json`; `renders/VIDEO-15-FINAL.mp4`; `renders/revisions/VIDEO-15-FINAL-before-spacing-broll-fix.mp4`; `qa/video15-spacing-broll-fix/`; `VIDEO-15/QA_FINAL.md`; `METRICAS_PRODUCCION.md` y `.json`; `manifest.json`; `Serie-IA-Negocios-10-Videos/AGENTS.md`; `ESTANDAR_QA_PREAPROBACION.md`; y esta bitácora.
- **Validación:** `hyperframes lint` terminó con 0 errores y 0 advertencias. El check estricto final pasó runtime, layout y motion, y aprobó 27/27 contrastes en 1.2, 14.48, 14.62, 16.2 y 20.44 s. Dos renders HDR se rechazaron durante el control final: uno conservó la imagen demasiado tiempo y otro dejó un rótulo anterior visible en una zona transparente. Un render SDR de regresión confirmó la solución antes de la última entrega. El MP4 definitivo decodificó completo y confirmó 21.100 s, 1080×1920, 30 fps, HEVC Main 10, `yuv420p10le`, BT.2020/HLG y AAC-LC estéreo 48 kHz. Pesa 15,357,624 bytes, su SHA-256 es `b778b8bfdc79f88d651612f3a581c6661b32312edc287e51f477bfaf116a26f2` y el audio mide −16.4 LUFS, LRA 2.9 LU y pico verdadero −1.3 dBFS. La hoja dirigida muestra la máquina a 14.48 s y al presentador limpio a 14.62, 16.2 y 20.44 s.
- **Resultado:** `VIDEO-15-FINAL.mp4` queda reemplazado por la revisión corregida y verificada. El encabezado inicial tiene respiración, la línea amarilla no cruza letras, el recurso funciona como acento breve y el presentador conserva el cierre. La versión anterior permanece recuperable. No se publicó.
- **Aprendizaje:** la visibilidad correcta en Studio no garantiza por sí sola la composición HDR final; las zonas transparentes pueden exponer capas residuales y deben inspeccionarse directamente en el MP4. El QA útil compara fotogramas a ambos lados del corte, no solo una hoja uniforme. Un render fallido se rechaza y se documenta, aunque el comando termine con éxito.
- **Pendiente:** escucha humana independiente de la reproducción completa `por confirmar`; publicación o derivados por plataforma requieren autorización separada.

### 2026-09-26 — VIDEO-11 gana la selección narrativa para un explainer original inspirado en la gramática Santi Web

- **Petición:** revisar únicamente las narraciones de VIDEO-01 a VIDEO-15, escoger la que ofrezca mayor potencial para un motion-graphics explainer original con HyperFrames, documentar la comparación y detenerse antes de construir o renderizar.
- **Punto de partida:** los quince videos ya tenían fuentes de voz, másteres de cámara, transcripts, captions o evidencia ASR en estados distintos. También existían una auditoría independiente y un sistema reutilizable derivado de dos referencias Santi Web. No existía una comparación narrativa común de los quince audios ni un ganador para este nuevo proyecto.
- **Cambio:** se creó `ANALISIS-SELECCION-MOTION-GRAPHICS-2026-09-26/` sin modificar las carpetas VIDEO-01 a VIDEO-15. Se eligió una fuente de voz por candidato siguiendo la prioridad solicitada, se midieron duración y pausas, se calcularon SHA-256 del archivo y del PCM mono de 16 kHz, y se reutilizaron los transcripts existentes sin ejecutar ASR nuevo. Se puntuaron los quince audios con la matriz de 100 puntos, se documentó un top 3 y se recomendó VIDEO-11. Para el ganador se propusieron un corte principal 00:00.12–00:26.36, nueve escenas y un piloto conceptual de 13,96 s; la cola 00:26.36–00:29.00 quedó condicionada a escucha humana.
- **Motivo:** VIDEO-11 presenta la cadena causal más rica para motion graphics —inundación, facilidad, caída de valor, multiplicación, giro hacia lo propio y contraste pensado/generado— y es además la narración más larga del grupo. El análisis priorizó comprensión y capacidad visual por encima de la edición existente o de la calidad técnica aislada.
- **Archivos:** `ANALISIS-SELECCION-MOTION-GRAPHICS-2026-09-26/INFORME_SELECCION_AUDIO.md`, `EVIDENCIA_SELECCION.json`, `CHANGELOG.md` y esta bitácora.
- **Validación:** están presentes los quince candidatos. El JSON pasó `jq empty`; los ocho componentes de cada score suman su total declarado; los quince hashes PCM son diferentes y no se procesaron copias como candidatos separados. Se midieron silencios con `ffmpeg silencedetect` a −35 dB/0,25 s y loudness del top 3. No se renderizó video, no se creó un proyecto HyperFrames y no se afirma escucha humana en esta selección.
- **Resultado:** VIDEO-11 queda recomendado con 91/100, seguido por VIDEO-10 con 88 y VIDEO-14 con 87. La fuente propuesta es `VIDEO-11/editable-hyperframes-video-11/assets/video11-voice-normalized.m4a`. Ningún audio alcanza 45–90 s; el ganador mide 29,10 s y el segmento principal recomendado 26,24 s.
- **Aprendizaje:** para un explainer faceless, la mejor narración no es necesariamente la más polémica ni la de mayor nivel técnico: gana la que convierte cada frase en una operación visual distinta y contiene un giro de significado. Esta conclusión permanece como hipótesis de selección de un solo conjunto; no se promueve a regla permanente del framework.
- **Pendiente:** aprobación o cambio del audio ganador; escucha humana de `podemos/podremos` en 00:09.60–00:10.21 y de la recapitulación en 00:26.36–00:29.00; decidir si 45–90 s es requisito estricto. Sólo después corresponde enrutar el workflow de HyperFrames, crear un proyecto nuevo y producir un piloto de 10–15 s.

### 2026-09-26 — C01–C05 forman el primer lote fotográfico y una biblioteca reutilizable

- **Petición:** extender el lenguaje realista a todos los carruseles en bloques de cinco, documentar el contenido de cada página y conservar cada fotografía como recurso analizado para futuras ediciones. La audiencia prioritaria son emprendedores que empiezan con IA, ya la utilizan sin un sistema o necesitan asesoría.
- **Punto de partida:** C01 ya tenía una variante fotográfica con tres escenas; C02–C05 continuaban únicamente en sus versiones vectoriales aprobadas. No existía una biblioteca central de fotografías, un sistema transversal de realismo ni fichas que permitieran decidir cuándo reutilizar un activo.
- **Cambio:** se generaron doce fotografías nuevas y se centralizaron junto con las tres de C01 en `RECURSOS-FOTOGRAFICOS/`. Se crearon variantes híbridas de C02, C03, C04 y C05 sin modificar los originales. Cada carrusel recibió un ángulo visual distinto: autoevaluación, transferencia de conocimiento, conversación comercial y voz propia. Se documentaron quince activos con escena, función, audiencia, emoción, composición, prompt y páginas de uso. También se añadieron análisis página por página, manifiestos, un sistema fotográfico, un generador reproducible, una lámina horizontal por carrusel, una lámina conjunta, una hoja de recursos y un visor HTML para navegar el lote.
- **Motivo:** construir realismo y cercanía sin repetir la imagen genérica de una persona frente a una laptop, y evitar volver a generar fotografías que ya existen cuando una futura pieza necesita la misma emoción, contexto y espacio para texto.
- **Archivos:** `CONTENIDO-ESTATICO/generar_lote_fotografico_c01_c05.js`; `SISTEMA_FOTOGRAFICO.md`; `RECURSOS-FOTOGRAFICOS/`; `SEMANA-01/C01-VARIANTE-FOTOGRAFICA/` y `C02-VARIANTE-FOTOGRAFICA/`; `SEMANA-02/C03-VARIANTE-FOTOGRAFICA/` y `C04-VARIANTE-FOTOGRAFICA/`; `SEMANA-03/C05-VARIANTE-FOTOGRAFICA/`; `REVISION-LOTES/LOTE-01-C01-C05/`; `README.md`; `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** el generador pasó `node --check`; los SVG con fotografías incrustadas pasaron `xmllint --huge`; los 35 PNG miden 1080×1350. El inventario confirma cinco variantes, 23 páginas con fotografía, doce páginas limpias y quince recursos con identificadores únicos y archivos existentes. Se inspeccionaron los cinco másteres y la hoja de recursos. En navegador se abrieron C01–C05, cada carrusel mostró siete miniaturas, navegó hasta la página 7 y cargó todas sus imágenes; no se registraron errores de consola.
- **Resultado:** el primer lote de cinco carruseles está completo y listo para revisión humana. Los archivos públicos no muestran metadata ni notas internas. Las variantes permanecen pendientes de aprobación, no reemplazan los originales aprobados y no fueron publicadas.
- **Aprendizaje:** el realismo funciona cuando cada fotografía tiene una tarea narrativa concreta. La variedad útil proviene de negocios, edades, acciones y emociones diferentes, no solamente de cambiar el rostro. Las páginas que entregan una matriz o formulario suelen ganar claridad al permanecer limpias.
- **Pendiente:** recibir correcciones o aprobación de C01–C05. Después corresponde producir C06–C10, luego C11–C12; al terminar carruseles se continuará con publicaciones individuales y finalmente con historias. Cualquier medición de rendimiento requiere publicación y control de tema, CTA y horario.

### 2026-09-26 — Un laboratorio independiente reevalúa las 15 narraciones y prepara voz local

- **Petición:** continuar el nuevo explainer con voz genérica y una clonación autorizada de la voz del usuario; crear todo en carpetas nuevas, preservar los editables existentes, paralelizar selección, estilo, guion y dataset, y consultar únicamente la elección del guion antes de construir.
- **Punto de partida:** una selección anterior de la misma fecha había recomendado VIDEO-11 con 91/100 y permanecía pendiente de aprobación. Existían los quince editables y sus transcripciones, pero no un laboratorio local de voz, un corpus deduplicado ni guiones ampliados para esta ejecución.
- **Cambios:** se creó `NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/` sin escribir dentro de `VIDEO-01` a `VIDEO-15`. Dos auditorías paralelas aplicaron la matriz solicitada y una consolidación nueva recomendó VIDEO-01 con 92/100, seguido por VIDEO-06 con 91 y VIDEO-04 con 90. Se mantuvo explícitamente la selección histórica de VIDEO-11 como una conclusión previa con método y pesos distintos. Se sintetizó la gramática Santi Web sin copiar activos y se redactaron tres ampliaciones del guion ganador; una crítica independiente confirmó A como mejor base, pero corrigió la falsa equivalencia entre automatización y autonomía total. En `voice-lab/` se instalaron Kokoro ONNX y Chatterbox Multilingual en entornos Python 3.11 separados, se creó un corpus de 14 fuentes aceptadas y una en revisión, y se produjeron muestras técnicas genérica y clonada con procedencia.
- **Motivo:** separar la selección narrativa de las ediciones visuales existentes, convertir la voz en un componente reemplazable y permitir que el piloto use TTS genérico mientras se valida una clonación autorizada. La discrepancia VIDEO-11/VIDEO-01 se conserva como evidencia de que una puntuación depende de la rúbrica y no debe reescribir decisiones anteriores.
- **Archivos afectados:** `NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/selection/`; `script-development/`; `voice-lab/`; `CHANGELOG.md`; Homebrew `espeak-ng` 1.52.0; y esta bitácora. No se modificaron carpetas `VIDEO-*`.
- **Validación:** la auditoría cubre los quince videos y QA independiente confirmó existencia, rutas, duraciones, puntuaciones, top 3, ganador, diez escenas y piloto de 12 s; se incorporaron las siete dudas con timecode. El dataset localizó 15 fuentes, aceptó 14 con 302.898 s y separó VIDEO-14 para revisión; creó cuatro prompts de 19.5–29 s y un corpus de 307.798 s. Kokoro produjo un WAV mono de 4.373 s y Chatterbox cargó en Apple MPS y produjo uno de 7.120 s. Se midieron metadatos, loudness y picos, pero no se afirma escucha humana, similitud biométrica ni aprobación de las voces. No se renderizó video.
- **Resultado:** existe un laboratorio reproducible de selección, guion y voz. VIDEO-01 es el ganador de esta reevaluación y A `El bucle disfrazado` es la recomendación editorial actual. Todavía no existe `BRIEF.md`, storyboard definitivo, piloto ni MP4 porque el texto debe escogerse primero.
- **Aprendizaje:** la clonación zero-shot permite probar una identidad vocal sin entrenar pesos nuevos, pero no reemplaza la verificación humana de hablante, acento y naturalidad. También quedó demostrado que `MPS`, la ruta de `espeak-ng` y el watermarker deben probarse con generación real: una instalación exitosa no garantiza inferencia. Una selección nueva debe registrar por qué difiere de una selección previa, no ocultarla.
- **Pendiente:** elegir A, B o C; escuchar las dos muestras; confirmar que las 14 fuentes aceptadas pertenecen al usuario; decidir VIDEO-14; crear el proyecto `faceless-explainer` a 1080×1920/24 fps; construir y validar el piloto; y sólo después avanzar al video completo y al render final conforme a los gates de HyperFrames.

### 2026-09-26 — C06–C10 completan el segundo lote de carruseles fotográficos

- **Petición:** retomar en este chat la creación de carruseles que se había interrumpido y continuar desde el estado verificable del proyecto.
- **Punto de partida:** los doce carruseles vectoriales estaban aprobados. Las variantes fotográficas C01–C05 formaban un primer lote pendiente de revisión con quince recursos; la propia bitácora indicaba C06–C10 como siguiente bloque. No existían variantes fotográficas, fotografías ni visor del segundo lote.
- **Cambio:** se conservaron intactos los originales y se crearon variantes separadas de C06, C07, C08, C09 y C10. Se generaron quince fotografías nuevas mediante la herramienta integrada de generación de imágenes y se archivaron con prompts y funciones narrativas. Cada carrusel recibió un mundo visual distinto: decisión operativa antes de automatizar, especificación y evaluación de prompts, conversación sin presión, claridad de oferta y escucha de objeciones. El lote contiene 23 páginas con fotografía y doce páginas limpias. Se añadieron un generador reproducible, cinco análisis página por página, cinco manifiestos, cinco láminas horizontales, un máster conjunto, una hoja de recursos, un visor HTML y QA. La biblioteca pasó de quince a treinta activos.
- **Motivo:** continuar el experimento de realismo sin convertir cada página en un fondo decorativo. Las fotografías se asignaron a identificación, contexto o cierre; las matrices, estructuras y decisiones que deben leerse o copiarse permanecieron limpias.
- **Archivos:** `CONTENIDO-ESTATICO/generar_lote_fotografico_c06_c10.js`; `RECURSOS-FOTOGRAFICOS/C06/` a `C10/`, `BIBLIOTECA_RECURSOS.md`, `biblioteca_recursos.json` y `README.md`; `SEMANA-03/C06-VARIANTE-FOTOGRAFICA/`; `SEMANA-04/C07-VARIANTE-FOTOGRAFICA/` y `C08-VARIANTE-FOTOGRAFICA/`; `SEMANA-05/C09-VARIANTE-FOTOGRAFICA/` y `C10-VARIANTE-FOTOGRAFICA/`; `REVISION-LOTES/LOTE-02-C06-C10/`; `SISTEMA_FOTOGRAFICO.md`; `README.md`; `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** el generador pasó `node --check`; los 35 SVG pasaron `xmllint --huge`; los 35 PNG miden 1080×1350. Se inspeccionaron los cinco másteres y cinco páginas críticas a resolución completa. El máster conjunto mide 7800×7050 y tiene SHA-256 `9babcae8ccd886ed5b54e9d5f284488a8b6d7cd9527ffbb7011cca95b5051df4`. El visor contiene cinco secciones, 35 controles y cero rutas faltantes; respondió `HTTP 200`. La interacción gráfica quedó `por confirmar` porque el Mac estaba bloqueado, de modo que no se afirma prueba de clic ni consola.
- **Resultado:** existe un segundo lote completo con cinco variantes y quince recursos nuevos, listo para revisión humana. Las diez variantes C01–C10 siguen pendientes de aprobación, no sustituyen los originales y no fueron publicadas.
- **Aprendizaje:** la fotografía funciona mejor como prueba situacional que como relleno. En automatización debe mostrar responsabilidad y excepción; en prompts, preparación y evaluación; en ventas, escucha y decisión. Mantener limpia la página más utilitaria protege el valor práctico del carrusel.
- **Pendiente:** recibir correcciones o aprobación de C01–C10; después producir C11–C12. Al terminar los carruseles, continuar con publicaciones individuales y finalmente con historias. Medir desempeño requiere publicación y control de tema, CTA y horario.

### 2026-09-26 — C01 mide una ruta rápida para animar fotografías con FFmpeg

- **Petición:** probar una alternativa externa y abierta para animar el carrusel C01 y tres fotografías individuales ya creadas para los carruseles, con el objetivo de observar el costo de render frente al flujo habitual basado en composiciones HTML.
- **Punto de partida:** C01 tenía una variante fotográfica de siete páginas 1080×1350 y una biblioteca central con tres fotografías documentadas —caos operativo, cotización clara y claridad/acción—. No existía un pipeline reproducible para convertir esos activos en MP4 mediante FFmpeg ni mediciones de este caso.
- **Cambios:** se creó `CONTENIDO-ESTATICO/PRUEBAS-VIDEO-FFMPEG/C01-2026-09-26/`. El script genera un video 4:5 de 13,90 s con las siete páginas, zoom máximo de 2,5 % y fundidos de 0,25 s. También genera tres videos 9:16 de 6 s, uno por fotografía, con fondo desenfocado derivado del mismo activo y movimientos distintos: acercamiento al sujeto, paneo lateral y alejamiento. Se añadieron receta, README, reporte técnico, logs, metadatos `ffprobe`, hashes de fotogramas muestreados y láminas de contacto.
- **Motivo:** evaluar una ruta nativa de menor sobrecarga para movimientos sencillos, manteniendo HyperFrames para piezas que necesiten composición HTML, tipografía o motion graphics más complejos. El formato 4:5 protege el diseño original del carrusel; el 9:16 permite juzgar las fotografías como recursos de reel o historia sin recortar a los sujetos.
- **Archivos afectados:** `CONTENIDO-ESTATICO/PRUEBAS-VIDEO-FFMPEG/C01-2026-09-26/`; `CONTENIDO-ESTATICO/CHANGELOG.md`; y esta bitácora. Los PNG y SVG originales de C01 y las fotografías de la biblioteca no fueron modificados.
- **Validación:** FFmpeg 8.1.2 detectó y usó `h264_videotoolbox`. Los cuatro MP4 decodificaron completos sin errores reportados; `ffprobe` confirmó H.264, `yuv420p`, 30 fps, dimensiones previstas y BT.709. Tres muestras por video produjeron hashes distintos. Se inspeccionaron cuatro láminas de contacto y no se observó recorte de rostro ni pérdida de páginas. No se afirma reproducción humana continua, escucha, aprobación ni publicación.
- **Resultado:** el carrusel produjo 13,90 s en 22,40 s y pesa 12.113.635 B. Las tomas individuales produjeron 6 s en 2,27 s, 2,30 s y 2,25 s, con pesos entre 2.156.078 B y 3.033.510 B. Los cuatro renders permanecen pendientes de revisión del usuario y no contienen audio.
- **Aprendizaje:** FFmpeg puede producir una fotografía social animada más rápido que tiempo real cuando el tratamiento se limita a una imagen, un fondo derivado y una transformación. La secuencia completa cuesta más por el preescalado antitemblor, las siete fuentes y los fundidos. Estos datos no demuestran todavía que FFmpeg supere a HyperFrames porque falta renderizar una composición idéntica con ambos motores.
- **Pendiente:** revisar movimiento y ritmo en reproducción continua; decidir si el carrusel necesita versión 9:16; escoger intensidad de movimiento; definir música o silencio; y, si interesa un benchmark estricto, producir el mismo plano en HyperFrames y medirlo en el mismo equipo.

### 2026-09-26 — C11–C12 completan las variantes fotográficas de los doce carruseles

- **Petición:** terminar los dos carruseles que faltaban y continuar después con todas las historias.
- **Punto de partida:** los doce carruseles vectoriales estaban aprobados y C01–C10 ya tenían variantes fotográficas experimentales con treinta recursos. C11 y C12 conservaban únicamente sus versiones originales; la planificación indicaba completar ambos antes de pasar a otros formatos.
- **Cambio:** se conservaron intactos los originales y se crearon `C11-VARIANTE-FOTOGRAFICA` y `C12-VARIANTE-FOTOGRAFICA`. Se generaron seis fotografías nuevas mediante la herramienta integrada: revisión sin sonido, idea por bloques, prueba final de accesibilidad, contexto propio, proceso y criterio aprendidos, y confianza demostrable. El lote contiene once páginas fotográficas y tres limpias. Se añadieron un generador reproducible, manifiestos, análisis página por página, láminas horizontales, máster conjunto, hoja de recursos, visor y QA. La biblioteca pasó de treinta a 36 recursos y ahora cubre C01–C12.
- **Motivo:** cerrar la colección de carruseles con el mismo criterio narrativo de los dos lotes anteriores: usar fotografía para situar el problema y la acción, y conservar limpias las páginas donde la estructura necesita máxima legibilidad. La instrucción del usuario cambia el orden futuro y prioriza las 24 historias antes que las imágenes individuales.
- **Archivos:** `CONTENIDO-ESTATICO/generar_lote_fotografico_c11_c12.js`; `RECURSOS-FOTOGRAFICOS/C11/`, `C12/`, `BIBLIOTECA_RECURSOS.md`, `biblioteca_recursos.json` y `README.md`; `SEMANA-06/C11-VARIANTE-FOTOGRAFICA/` y `C12-VARIANTE-FOTOGRAFICA/`; `REVISION-LOTES/LOTE-03-C11-C12/`; `SISTEMA_FOTOGRAFICO.md`; `README.md`; `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** el generador pasó `node --check`; los 14 SVG pasaron `xmllint --huge`; los 14 PNG miden 1080×1350. Los 36 identificadores de biblioteca son únicos y sus archivos existen. Se inspeccionaron los dos másteres, la hoja de recursos y cuatro páginas críticas a resolución original. El máster conjunto mide 7800×2820 y tiene SHA-256 `9ea69921c227ea5a1637ef8fce943af2b9dd5a41695f09220a7e54656308dff3`. En navegador se abrió cada carrusel, se navegó hasta la página 7, ambas imágenes finales cargaron a 1080×1350 y no hubo errores ni advertencias de consola.
- **Resultado:** las doce variantes fotográficas de carrusel C01–C12 están completas. C11 y C12 quedan listas para revisión humana, con los originales aprobados intactos. Ninguna variante fue publicada ni medida.
- **Aprendizaje:** accesibilidad y diferenciación ganan credibilidad cuando se muestran como conductas concretas: probar en silencio, ordenar por significado, observar clientes, comparar prototipos y explicar límites. El cierre de una colección también debe registrar el cambio de prioridad del siguiente formato para no continuar por inercia con un orden que el usuario ya modificó.
- **Pendiente:** recibir correcciones o aprobación de las doce variantes de carrusel. El siguiente bloque solicitado es producir variantes fotográficas para H01–H24; las imágenes individuales quedan aplazadas. La configuración de encuestas, quiz y cajas nativas, la publicación y las métricas reales siguen pendientes.

### 2026-09-26 — H01–H24 completan la colección de historias fotográficas

- **Petición:** después de cerrar C11 y C12, continuar con todas las historias.
- **Punto de partida:** existían 24 historias originales aprobadas en 1080×1920 y una biblioteca de 36 fotografías creada para los doce carruseles. Ninguna historia tenía variante fotográfica. El sistema exigía buscar primero en la biblioteca antes de generar activos nuevos y las interacciones nativas seguían pendientes de configuración.
- **Cambio:** se crearon 24 variantes separadas, cuatro por semana, sin modificar los originales. Cada historia reutiliza un activo cuyo contexto coincide con su pregunta, checklist o quiz; se emplearon 20 fotografías únicas y se registraron 24 usos en la biblioteca. Se añadieron un generador reproducible, 24 manifiestos, 24 análisis, seis láminas semanales, un máster conjunto, un visor HTML y QA. El contraste se adapta automáticamente al color base del arte para conservar la lectura sobre fondos claros u oscuros.
- **Motivo:** producir todas las historias solicitadas sin convertir la biblioteca en una colección redundante. Reutilizar una escena ya documentada permite que carrusel e historia pertenezcan al mismo mundo visual y conserva trazabilidad entre tema, emoción y función.
- **Archivos:** `CONTENIDO-ESTATICO/generar_variantes_fotograficas_historias.js`; las 24 carpetas `SEMANA-*/H??-VARIANTE-FOTOGRAFICA/`; `REVISION-LOTES/LOTE-04-H01-H24/`; `RECURSOS-FOTOGRAFICOS/BIBLIOTECA_RECURSOS.md`, `biblioteca_recursos.json` y `README.md`; `SISTEMA_FOTOGRAFICO.md`; `README.md`; `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** el generador pasó `node --check`; los 24 SVG pasaron `xmllint --huge`; los 24 PNG miden 1080×1920; los 24 manifiestos conservan estado experimental pendiente y no publicado. Se inspeccionaron el máster general y las seis láminas semanales. El visor contiene seis secciones y 24 fichas sin rutas faltantes; en navegador las 24 imágenes cargaron con dimensiones naturales de 1080×1920 y no se registraron advertencias ni errores de consola. El máster mide 1510×4050 y tiene SHA-256 `ce24f1faa82372629800bfdc220dbdd4097b4e3b0d0afc3e476694b71499b69c`.
- **Resultado:** H01–H24 tienen variantes fotográficas completas y listas para revisión humana. Los originales aprobados permanecen intactos. No se afirma que las encuestas, quiz o cajas estén activas; nada fue publicado ni medido.
- **Aprendizaje:** una biblioteca fotográfica gana valor cuando registra usos derivados, no solamente archivos. La misma escena puede sostener un carrusel y una historia si la función narrativa coincide, mientras el velo cromático del diseño protege la legibilidad sin borrar el contexto humano.
- **Pendiente:** recibir correcciones o aprobación de las 24 historias fotográficas y de los doce carruseles fotográficos. Configurar interacciones nativas al programar. Las variantes de las 18 imágenes individuales quedan aplazadas hasta nueva indicación; publicación y métricas reales continúan pendientes.

### 2026-09-26 — El Guion A se convierte en un explainer HyperFrames completo

- **Petición:** después de aprobar el Guion A, continuar autónomamente con voz genérica y clonación autorizada, crear todo en carpetas nuevas, paralelizar las escenas y entregar el video completo sin modificar los editables VIDEO-01–VIDEO-15.
- **Punto de partida:** `NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/` ya contenía selección, tres guiones y un laboratorio local de voz. A `El bucle disfrazado` era la recomendación editorial, pero todavía no existían `BRIEF.md`, storyboard definitivo, piloto, proyecto renderizable ni master final.
- **Cambios:** se creó `videos/retrabajo-acelerado/` con workflow `faceless-explainer`, lienzo 1080×1920 a 24 fps y once subcomposiciones originales. Se redactaron brief, guion, storyboard, diseño y mapa de audio. Se generaron dos lecturas completas: Kokoro genérica y clon zero-shot Chatterbox autorizado. Whisper Large V3 comparó ambas; la voz genérica obtuvo WER 0 frente a 0.0066 del clon y fue masterizada y segmentada por escena. Se añadieron captions de 65 grupos, 21 cues de SFX, transiciones, tracks separados y un piloto de 11.147 s. Después del QA del piloto se ensambló el video completo, se corrigió la temporización del sello `Retrabajo acelerado`, se renderizó el master y se normalizó únicamente el audio del archivo de entrega.
- **Motivo:** convertir una tesis abstracta sobre automatización y retrabajo en un sistema visual comprensible. La ficha-semilla recurrente muestra el regreso, el bucle y el avance; la decisión de voz se basó en fidelidad textual medible y no en una similitud vocal no escuchada.
- **Archivos afectados:** `NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado/` con `BRIEF.md`, `SCRIPT.md`, `STORYBOARD.md`, `DESIGN.md`, `AUDIO_MAP.md`, `PRODUCTION_LOG.md`, `CHANGELOG.md`, `index.html`, `compositions/`, `assets/`, `scripts/`, `pilot-project/`, `qa/` y `renders/`; `NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/CHANGELOG.md`; y esta bitácora. Las carpetas VIDEO-01–VIDEO-15 no se modificaron.
- **Validación:** `npm run check` pasó con 0 errores en lint, runtime, layout y motion; quedaron advertencias no bloqueantes documentadas. Se capturaron e inspeccionaron once puntos medios, una hoja de contacto del MP4 y un frame adicional de la escena breve. `renders/video-delivery.mp4` decodificó completo y `ffprobe` confirmó H.264, 1080×1920, 24 fps, BT.709, AAC estéreo 48 kHz, 53.000 s y 8.569.927 bytes. El audio mide −15.93 LUFS integrado, LRA 1.20 LU y −3.31 dBTP. Su SHA-256 es `7d864c071debd8bbabf629606013a8c408faaece6b5410cbbd5a0f07874bf096`.
- **Resultado:** existe un explainer completo, original y editable basado en el Guion A, con master final y piloto conservado. La voz clonada también permanece como alternativa, pero no se usó porque el ASR detectó la alteración “diseña primeramente. Primero el sistema”. No se afirma escucha humana continua, similitud biométrica, aprobación audiovisual del usuario ni publicación.
- **Aprendizaje:** comparar las voces por fidelidad textual antes de animar evitó sincronizar once escenas con una lectura alterada. Dividir la voz por escena y construir subcomposiciones independientes permitió paralelizar sin perder editabilidad. Las escenas muy breves necesitan snapshots adicionales porque una hoja uniforme puede omitirlas; las advertencias automáticas deben distinguir errores reales de solapamientos intencionales documentados.
- **Pendiente:** revisión y escucha humana del master y del piloto; decidir si se desea una segunda versión con voz clonada corregida; aprobar o pedir cambios audiovisuales; y publicar o derivar versiones por plataforma solamente con autorización separada.

### 2026-09-27 — I01–I18 completan las variantes fotográficas de los posts individuales

- **Petición:** terminar las imágenes pendientes y decidir si los posts individuales debían repetir fotografías de carruseles o usar variación visual con los mismos conceptos, considerando que gran parte de la audiencia los descubre de forma aislada durante el scroll.
- **Punto de partida:** los 18 posts I01–I18 originales estaban aprobados. Existían doce carruseles y 24 historias con variantes fotográficas, además de una biblioteca de 36 recursos, pero ningún post individual tenía alternativa fotográfica.
- **Cambio:** se adoptó la regla `identidad constante + escena variable`. Se generaron 18 fotografías nuevas, una por post, con personas, oficios, iluminación y acciones diferentes. Cada fotografía se integró en una variante separada 1080×1350 que conserva firma, tipografía, paleta, estructura y tesis del original. Se añadieron un generador reproducible, 18 manifiestos, 18 análisis, seis láminas semanales, un máster, visor HTML y QA. La biblioteca pasó de 36 a 54 activos y archivó el prompt y la función de cada escena.
- **Motivo:** una repetición literal ayuda a reconocer una campaña, pero en el scroll reduce novedad y puede hacer que piezas distintas parezcan duplicadas. Mantener constantes los códigos de marca y variar la evidencia humana permite reconocimiento sin monotonía; cada post sigue entendible fuera del perfil.
- **Archivos afectados:** `CONTENIDO-ESTATICO/generar_variantes_fotograficas_imagenes.js`; las 18 carpetas `SEMANA-*/I??-VARIANTE-FOTOGRAFICA/`; `REVISION-LOTES/LOTE-05-I01-I18/`; `RECURSOS-FOTOGRAFICOS/I01/` a `I18/`, `BIBLIOTECA_RECURSOS.md`, `biblioteca_recursos.json` y `README.md`; `SISTEMA_FOTOGRAFICO.md`; `README.md`; `PLAN_CARRUSELES_IMAGENES_21_DIAS.md`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** el generador pasó `node --check`; los 18 SVG pasaron `xmllint --huge`; los 18 PNG miden 1080×1350; existen 18 recursos nuevos y 18 manifiestos con estado experimental pendiente y no publicado. La biblioteca JSON v5 contiene 54 identificadores únicos. Se inspeccionó el máster a resolución original y no se observaron titulares cortados, cajas fuera de lienzo ni pérdida de identidad. El máster mide 1140×3030 y tiene SHA-256 `69c381cea23fbacf6ed3003d67c0bc50c9ca2176a6d1299d950e28ad2186680c`.
- **Resultado:** los 18 posts individuales tienen variantes fotográficas completas. Con esto, todo el inventario estático —12 carruseles, 24 historias y 18 posts— cuenta con una alternativa fotográfica. Los originales aprobados siguen intactos y las variantes no están aprobadas ni publicadas.
- **Aprendizaje:** coherencia no significa duplicación. Para una serie distribuida en feed, la memoria de marca puede vivir en decisiones estables de diseño, mientras la fotografía cambia para ofrecer una nueva situación reconocible en cada aparición.
- **Pendiente:** revisión humana del lote I01–I18 y de las variantes fotográficas anteriores; después, seleccionar o corregir versiones antes de programar. Publicación y métricas reales continúan pendientes.

### 2026-09-27 — I12 elimina una interferencia entre adorno y titular

- **Petición:** revisar I12 porque una línea estaba montada sobre el texto y convertir la observación en una regla permanente que pudiera detectarse y corregirse durante futuras verificaciones.
- **Punto de partida:** el patrón T22 colocaba una barra horizontal en `y=235–253`; el primer titular de I12 comenzaba aproximadamente en `y=243`, por lo que ambos elementos se intersectaban en el original y en la variante fotográfica.
- **Cambio:** la barra se desplazó a `y=205–223`. Se regeneraron I12 original y I12-FOTO. El cambio se incorporó a `generar_semanas_03_05.js` para que futuras regeneraciones conserven la separación y a `generar_variantes_fotograficas_imagenes.js` como gate de salida. Se creó `verificar_solapamiento_adornos_texto.js` y se documentó la regla en los dos sistemas visuales y en el QA del lote.
- **Motivo:** una línea decorativa nunca debe competir con la legibilidad. Corregir solo el PNG habría dejado la causa activa en los generadores y permitido que el error regresara.
- **Archivos afectados:** `generar_semanas_03_05.js`; `generar_variantes_fotograficas_imagenes.js`; `verificar_solapamiento_adornos_texto.js`; `SEMANA-04/I12-SIGUIENTE-PASO/`; `SEMANA-04/I12-VARIANTE-FOTOGRAFICA/`; `REVISION-LOTES/LOTE-05-I01-I18/`; `SISTEMA_VISUAL_ESTATICO.md`; `SISTEMA_FOTOGRAFICO.md`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** los tres scripts pasaron `node --check`; el verificador recorrió 252 SVG fuente y terminó en `PASS`; los dos SVG de I12 pasaron `xmllint --huge`; ambos PNG miden 1080×1350. Se inspeccionó I12-FOTO a resolución original y se confirmó separación visible entre barra y titular. El original conserva estado aprobado; la variante conserva estado experimental pendiente y no publicado.
- **Resultado:** I12 ya no tiene la línea montada sobre el texto y el defecto queda cubierto por una comprobación automática reproducible más una regla de inspección visual.
- **Aprendizaje:** una observación de revisión debe corregir tres capas: el arte visible, la fuente que lo genera y el gate que impide reincidencia. La detección geométrica automática ayuda con barras rectas, pero curvas y formas irregulares todavía requieren inspección del render.
- **Pendiente:** aplicar la misma regla a cualquier nuevo generador de contenido estático y mantener revisión visual del PNG final. La variante I12 y el resto del lote continúan pendientes de aprobación humana; nada fue publicado.

### 2026-09-27 — C01 prueba movimiento interno con ComfyUI y LTX-Video

- **Petición:** aplicar ComfyUI/LTX-Video a las tres fotografías ya usadas en la prueba FFmpeg, conservar todo el aprendizaje en una carpeta transferible a MUSE SPARK CODE y mostrar una vista conjunta de las animaciones.
- **Punto de partida:** `PRUEBAS-VIDEO-FFMPEG/C01-2026-09-26/` ya demostraba acercamientos, paneos y alejamiento 2D rápidos, pero no existía una prueba local de movimiento generativo interno ni un runtime ComfyUI/LTX documentado. Las tres fuentes permanecían en la biblioteca fotográfica de C01.
- **Cambios:** se creó `CONTENIDO-ESTATICO/PRUEBAS-VIDEO-LTX/C01-2026-09-26/`. Se instaló ComfyUI 0.37.0 en un runtime aislado, se fijó su commit, se descargaron y verificaron LTX-Video 2B v0.9.5 y T5-XXL FP16, y se prepararon recortes 576×768 sin alterar las fuentes. El primer ensayo de C01-R01 usó la configuración oficial adaptada —20 pasos y fuerza 0,15—; produjo movimiento pero también deriva, por lo que se conservó como evidencia. Se amplió el cliente para parametrizar fuerza, pasos y variante, y se renderizó un lote corregido con fuerza 0,8, 16 pasos y semillas fijas. Se añadieron scripts de bootstrap, arranque y render, workflows API, logs, `framemd5`, láminas, un preview concatenado y documentación específica para MUSE SPARK CODE.
- **Motivo:** medir con evidencia si LTX puede aportar mirada, respiración, gestos y movimiento de luz que una transformación 2D no inventa, y convertir la prueba en una práctica acumulativa que otro agente pueda ejecutar y mejorar sin perder decisiones anteriores.
- **Archivos afectados:** `CONTENIDO-ESTATICO/PRUEBAS-VIDEO-LTX/C01-2026-09-26/` con `README.md`, `MUSE-SPARK-CODE-HANDOFF.md`, `BITACORA_EXPERIMENTOS.md`, `QA_RESULTADOS.md`, `bootstrap_macos.sh`, `start_comfy.sh`, `render_preserve.sh`, `run_comfy_ltx.py`, `inputs/`, `workflows/`, `logs/`, `qa/`, `renders/` y `runtime/`; `CONTENIDO-ESTATICO/CHANGELOG.md`; y esta bitácora. Las fotografías originales y los carruseles no se modificaron.
- **Validación:** el Mac de prueba fue un Apple M4 de 10 núcleos con 16 GB. Python 3.12.13 y PyTorch 2.14.0 confirmaron MPS disponible. Los hashes de los modelos coincidieron con los registrados. Los tres MP4 corregidos y el preview decodificaron completos; `ffprobe` confirmó H.264 `yuv420p`, 576×768, 49 fotogramas y 2,040 s por clip. Los scripts shell pasaron `bash -n` y el cliente pasó compilación Python. Se inspeccionaron láminas de ocho fotogramas; la reproducción humana continua queda `por confirmar`.
- **Resultado:** C01-R01, R02 y R03 generaron movimiento interno con mejor conservación a fuerza 0,8. Tardaron 800,996 s, 1.071,904 s y 622,120 s; el lote consumió 2.495,020 s para 6,12 s de salida. R01 conserva mejor teléfono, portátil y papeles; R02 mueve mirada y bolígrafo pero simplifica ligeramente la mano; R03 mantiene escena y cuerpo con movimiento facial/cabello discreto. El preview conjunto mide 6,125 s y tiene SHA-256 `a03994c63118bd0b56263fcd5162fa0412619e915aaec3f9dd2b8f43c5ce0c2a`. Nada fue aprobado ni publicado.
- **Aprendizaje:** en este nodo, elevar la fuerza de condicionamiento reduce el ruido aplicado al fotograma inicial y protege mejor la fuente. LTX 2B puede crear movimiento interno útil, pero en 16 GB presenta tiempos variables de 10:22 a 17:52 para solo 2,04 s y todavía puede deformar manos u objetos manipulados. La ruta práctica es híbrida: pocos candidatos generativos cortos y una terminación determinista para loop, texto, audio, branding y exportación social.
- **Pendiente:** reproducción y aprobación humanas; probar 12 pasos sobre una sola imagen; evaluar prompts que mantengan manos quietas; decidir si se crea un loop 9:16 de 5–6 s; incorporar audio y marca solo después de seleccionar una toma; y continuar registrando cada experimento en `BITACORA_EXPERIMENTOS.md` sin reescribir los anteriores.

### 2026-09-27 — El inventario estático recibe un auditor final reutilizable y medición de tokens

- **Petición:** crear un agente que, cuando todo el contenido esté listo, revise nuevamente texto, contexto, concordancia, ortografía, solapamientos y figuras tapadas; prepare un plan visual para revisión humana; corrija lo aprobado; conserve todas las reglas aprendidas; y mida el consumo de tokens por piezas, lotes, categorías y total.
- **Punto de partida:** existían 54 recursos originales aprobados y 54 variantes fotográficas pendientes. En artes esto equivale a 126 originales y 126 variantes: 252 SVG y 252 PNG. Había checks de estructura y una regla nueva para que las barras no atravesaran texto, pero no existía un agente final, un inventario de auditoría unificado, un tablero humano de hallazgos ni una medición comparable de tokens.
- **Cambios:** se creó el skill personal `$auditar-contenido-estatico` con scripts para inventario, dimensiones, XML, metadata visible, signos, textos alternativos, puntuación, solapamientos, extracción semántica, láminas de contacto, plan humano, tablero de hallazgos y medición. Se ejecutaron y conservaron cuatro ensayos de calibración antes de la auditoría vigente `20260927T054228Z`. Se revisaron 126 artes semánticamente únicos y doce láminas de contacto que cubren los 252 artes. Se añadieron `REGLAS_QA_APRENDIDAS.md`, documentación del agente y un índice histórico de auditorías.
- **Motivo:** convertir el cierre de contenido en un proceso reproducible y verificable. La revisión automática reduce omisiones, pero la intención, la naturalidad y la composición sobre rostros todavía requieren inspección del agente y decisión humana.
- **Archivos afectados:** `~/.codex/skills/auditar-contenido-estatico/`; `CONTENIDO-ESTATICO/AUDITOR_CONTENIDO_ESTATICO.md`; `REGLAS_QA_APRENDIDAS.md`; `AUDITORIA-CONTENIDO/`; `README.md`; `CHANGELOG.md`; y esta bitácora. Los generadores y artes publicables no fueron corregidos todavía porque la decisión humana sigue pendiente.
- **Validación:** el skill pasó `quick_validate.py`; sus tres scripts pasaron `node --check`; la auditoría inventarió 252 artes, 126 originales y 126 variantes. Los checks de XML, dimensiones y solapamiento de adornos no detectaron errores. Los checks nuevos detectaron 36 textos alternativos genéricos y 18 cierres con puntuación incompatible. Se inspeccionaron a resolución original el plan humano, el tablero de hallazgos y las piezas dudosas de cada semana. `get_goal` y los checkpoints dejaron medición directa por etapa y por semana.
- **Resultado:** la auditoría está en estado `human_review`. Registra siete grupos: dos de accesibilidad/puntuación, cuatro de oclusión visual y uno contextual sobre I09. El tablero identifica C03-FOTO p02, C04-FOTO p01, C05-FOTO p05, I07-FOTO, I11-FOTO, H21-FOTO, H23-FOTO y H24-FOTO para corrección visual. I09 queda `por confirmar`. Nada fue publicado y las variantes no fueron aprobadas.
- **Medición:** el total observado hasta documentación y validación es 473.744 tokens y 1.639 segundos del contador del goal. La construcción inicial del agente e inventario usó 249.957 tokens; el tramo reutilizable posterior usó 223.787. Dentro de ese tramo, la revisión semántica usó 51.927, la revisión visual 72.553, la preparación del plan/tablero 50.047 y la documentación/validación 49.260. La cifra por arte es un promedio, no atribución directa. Carruseles, posts e historias quedan contabilizados por volumen, pero la atribución directa de tokens por formato comienza en la próxima ejecución porque esta línea base se checkpointó por semana.
- **Aprendizaje:** medir consumo requiere fijar checkpoints antes de cada bloque; dividir un total al final no demuestra qué categoría lo produjo. Los falsos positivos del primer auditor también mostraron que tipo de pieza, texto fragmentado y relación original/variante deben normalizarse antes de juzgar el contenido. Un plan humano útil debe mostrar tanto el proceso como los hallazgos concretos.
- **Pendiente:** recibir la decisión humana sobre QA-001 a QA-007. Después se corregirán las fuentes autoritativas, se regenerarán solo los alcances afectados, se repetirá la auditoría completa y se añadirá el costo de correcciones, reauditoría y cierre. En la siguiente auditoría se registrarán checkpoints directos para carruseles, posts e historias además de los lotes semanales.

### 2026-09-27 — La medición de la auditoría recibe totales visibles y conciliación

- **Petición:** corregir `MEDICION_TOKENS.md` porque las tablas mostraban los tramos, pero no exhibían la suma totalizada al final.
- **Punto de partida:** el informe mostraba 490.062 tokens y 1.767 segundos en el encabezado, seis bloques y doce checkpoints, pero las tablas de bloques y detalle no contenían una fila total ni una operación de conciliación visible.
- **Cambios:** se actualizó `registrar_medicion.js` para calcular y mostrar `TOTAL GENERAL`, `TOTAL INVENTARIO` y `TOTAL MEDIDO`; formatear miles y decimales con convención española; totalizar el inventario dinámicamente; separar entrega, continuidad y medición en bloques legibles; y escribir ecuaciones de comprobación para el total general y la revisión visual. Se registró el propio ajuste en `ajuste_totalizacion_reporte`.
- **Motivo:** una medición auditable debe permitir comprobar el total sin hacer cálculos manuales ni confiar solamente en el encabezado. La regla queda en el generador para que las auditorías futuras hereden la corrección.
- **Archivos afectados:** `~/.codex/skills/auditar-contenido-estatico/scripts/registrar_medicion.js`; `CONTENIDO-ESTATICO/AUDITORIA-CONTENIDO/20260927T054228Z/MEDICION_TOKENS.md`; su fuente `medicion_tokens.json`; `CONTENIDO-ESTATICO/CHANGELOG.md`; y esta bitácora.
- **Validación:** `node --check` pasó; el informe se regeneró desde el JSON; `jq` confirmó que la suma de deltas equivale al total. Al checkpoint del ajuste, bloques y tramos suman 523.378 tokens y 1.993 segundos, iguales al contador registrado; las seis semanas visuales suman 72.553 tokens.
- **Resultado:** el informe expone las sumas en las tres tablas y una sección `Comprobación de sumas`. El costo reutilizable posterior a la construcción inicial queda en 273.421 tokens. La atribución directa por formato continúa `N/D` porque no se midió así en esta primera línea base.
- **Aprendizaje:** una tabla de costos no está completa solo por mostrar cada fila; necesita total, fórmula de conciliación y una distinción explícita entre cifras medidas y cifras no disponibles.
- **Pendiente:** recibir la decisión humana sobre QA-001 a QA-007, corregir las fuentes aprobadas, regenerar y reauditar. En futuras ejecuciones se crearán checkpoints separados por carruseles, posts e historias para obtener atribución directa por categoría.

### 2026-09-27 — Los ocho casos visuales se convierten en láminas ampliadas de decisión

- **Petición:** continuar el objetivo del auditor hasta disponer de un plan realmente revisable por una persona antes de corregir las fuentes.
- **Punto de partida:** el plan y el tablero enumeraban siete grupos de hallazgos, y `hallazgos.json` ya incluía recortes para ocho artes, pero la persona todavía debía abrir cada PNG por separado para comprobar las oclusiones.
- **Cambios:** se creó `generar_evidencia_humana.js`. El script valida rutas, existencia, dimensiones y límites de cada recorte; incrusta el PNG original; genera una miniatura completa con la zona marcada y un acercamiento grande; divide la evidencia en páginas de hasta tres casos; y produce un índice con las siete decisiones pendientes. El flujo del skill ahora exige estas láminas cuando haya `visual_evidence`.
- **Motivo:** una decisión humana sobre oclusiones necesita mostrar el contexto completo y el detalle simultáneamente. Una descripción textual sola es evidencia insuficiente para decidir si se mueve una figura, se cambia el encuadre o se conserva el diseño.
- **Archivos afectados:** `~/.codex/skills/auditar-contenido-estatico/SKILL.md`; `scripts/generar_evidencia_humana.js`; los nuevos `EVIDENCIA-HALLAZGOS-HUMANO-01.png` a `03.png`, sus SVG y su índice dentro de la auditoría vigente; `AUDITOR_CONTENIDO_ESTATICO.md`; `AUDITORIA-CONTENIDO/README.md`; `RESUMEN_AUTOMATICO.md`; `CHANGELOG.md`; y esta bitácora.
- **Validación:** el script pasó `node --check`; encontró ocho evidencias y generó tres PNG de 1800×2400. Se inspeccionaron las tres páginas a resolución original. La primera versión mostró dos choques entre rótulos, se corrigieron en la fuente y la página 1 se volvió a inspeccionar sin solapamientos.
- **Resultado:** QA-003 a QA-006 pueden evaluarse viendo arte completo y acercamiento; QA-001, QA-002 y QA-007 permanecen explicados en el tablero y en el índice. Las siete decisiones continúan pendientes y no se tocó ningún arte publicable.
- **Aprendizaje:** la evidencia de auditoría también debe pasar QA visual. Presentar contexto, delimitación y zoom en una misma tarjeta reduce ambigüedad y hace más fácil registrar una decisión reproducible.
- **Pendiente:** recibir decisiones explícitas para QA-001 a QA-007; luego corregir las fuentes autoritativas, regenerar los alcances, repetir todos los checks y realizar una segunda inspección visual.

### 2026-09-27 — Accesibilidad, puntuación e I09 reciben una comparación visual

- **Petición:** continuar avanzando hacia la corrección completa mientras la decisión humana de QA-001 a QA-007 sigue pendiente, sin alterar artes ni intención editorial antes de esa respuesta.
- **Punto de partida:** las tres láminas ampliadas cubrían QA-003 a QA-006, pero QA-001, QA-002 y QA-007 solo aparecían como resúmenes. Esto obligaba a abrir manifiestos y SVG para comprobar ejemplos concretos.
- **Cambios:** `hallazgos.json` incorporó `text_evidence` para C05, I07, H09 e I09. El generador de evidencia ahora crea una cuarta lámina con columnas `ACTUAL`, `OBSERVACIÓN` y `PROPUESTA / DECISIÓN`. El esquema y el skill documentan esta evidencia opcional y exigen comprobar que no quede texto truncado.
- **Motivo:** una persona debe poder verificar la mezcla de idiomas, los signos duplicados y la discrepancia comercial de I09 sin interpretar mensajes genéricos ni inspeccionar código.
- **Archivos afectados:** `hallazgos.json`; `EVIDENCIA-TEXTO-CONTEXTO-HUMANO-01.svg/.png`; `EVIDENCIA-HALLAZGOS-HUMANO.md`; `~/.codex/skills/auditar-contenido-estatico/scripts/generar_evidencia_humana.js`; `references/hallazgos-schema.md`; `SKILL.md`; documentación del auditor; changelog; y esta bitácora.
- **Validación:** `hallazgos.json` pasó parseo JSON; el script pasó `node --check`; el SVG pasó `xmllint --huge`; el PNG mide 1800×2400. La primera versión truncó la alternativa de I09; se amplió a cuatro líneas y se inspeccionó nuevamente a resolución original con la condición completa visible.
- **Resultado:** los siete grupos de hallazgos tienen ahora evidencia humana directa: cuatro láminas cubren ocho artes visuales y tres grupos de texto/contexto. No se modificó ningún generador de contenido ni arte publicable.
- **Aprendizaje:** los problemas de texto no deben presentarse solo como conteos. Un ejemplo real junto a su corrección permite validar la regla, mientras una afirmación comercial incierta debe presentarse como caminos condicionados y no como una corrección inventada.
- **Pendiente:** aprobación o rechazo por ID y confirmación de si I09 tiene realmente seis cupos y dos días. Después se corregirán las fuentes, se regenerarán los alcances y se repetirá la auditoría completa.

### 2026-09-27 — La revisión humana se convierte en un formulario HTML local

- **Petición:** reemplazar la respuesta manual sobre las láminas por un HTML donde la persona pueda aceptar el estado actual, autorizar la corrección o escribir una observación; al final debe generar la respuesta, confirmar el guardado y facilitar el regreso al chat.
- **Punto de partida:** existían cuatro láminas y un índice Markdown, pero las decisiones todavía tenían que redactarse a mano. Una página HTML estática no podía escribir archivos ni enviar mensajes al chat de forma verificable.
- **Cambios:** se creó `REVISION-HUMANA-INTERACTIVA/` con interfaz responsiva, navegación de siete QA, evidencia ampliable, tres decisiones, campo de observación, progreso y resumen final. Un servicio Node local sirve los activos y guarda atómicamente `RESPUESTA-HUMANA.json/.md`. La confirmación prepara un mensaje y un enlace de regreso a Codex; explica que el mensaje debe copiarse porque no existe integración de escritura directa desde el HTML.
- **Motivo:** convertir el plan humano en una superficie de trabajo real y reducir errores de transcripción, sin atribuir al usuario decisiones que no tomó ni afirmar envíos inexistentes.
- **Archivos afectados:** `AUDITORIA-CONTENIDO/20260927T054228Z/REVISION-HUMANA-INTERACTIVA/` con `index.html`, `styles.css`, `app.js`, `server.js`, `iniciar_revision.command` y `README.md`; documentación del auditor; `RESUMEN_AUTOMATICO.md`; el skill; changelog; y esta bitácora.
- **Validación:** ambos JavaScript pasaron `node --check`; `server.js --self-test` confirmó siete hallazgos y cuatro archivos de evidencia; las rutas HTML y API respondieron 200. En navegador se comprobó selección, borrador tras recarga, observación obligatoria, progreso 7/7 y resumen de siete filas. A 390×844 el documento mantuvo `clientWidth = scrollWidth = 390`; no hubo errores de consola. Se dejó la interfaz real en 0/7 y no existen archivos `RESPUESTA-HUMANA.*` de prueba.
- **Resultado:** la persona puede completar toda la revisión desde una página local y obtener un informe estructurado listo para que el agente lo ingiera. El servidor queda activo para esta sesión y también puede abrirse por doble clic.
- **Aprendizaje:** una interfaz local puede guardar evidencia sin exponerla a internet, pero no debe confundir `guardado en el computador` con `enviado al chat`. Separar ambas acciones mantiene trazabilidad y evita falsas aprobaciones.
- **Pendiente:** la persona debe completar y confirmar 7/7, volver al chat y avisar. El agente leerá la respuesta, actualizará `hallazgos.json`, corregirá solo las fuentes autorizadas, regenerará y ejecutará la reauditoría completa.

### 2026-09-27 — Las decisiones humanas corrigen las fuentes y cierran la auditoría completa

- **Petición:** leer `RESPUESTA-HUMANA.json` de la auditoría `20260927T054228Z` y aplicar todas las decisiones aprobadas.
- **Punto de partida:** el formulario contenía siete respuestas verificables: `approve_fix` para QA-001 a QA-005 y QA-007, y `custom_fix` para QA-006. La observación de QA-006 pidió subir la fotografía de H21 y usar espejo en H23/H24 para apartar los rostros. La auditoría original seguía en corrección, con 36 alt text genéricos, 18 cierres de puntuación, ocho piezas con oclusiones y una oferta I09 con datos no confirmados.
- **Cambios:** las decisiones se registraron sin alterar su redacción. `generar_semanas_03_05.js` recibió un constructor de alt text en español, cierre de signos seguro y copy coherente; I09 pasó a `LISTA DE INTERÉS · QUITO` y dejó de afirmar seis cupos o dos días. `generar_lote_fotografico_c01_c05.js` movió las líneas de C03-FOTO p02 y C04-FOTO p01 y redujo la decoración de C05-FOTO p05. `generar_variantes_fotograficas_imagenes.js` reencuadró I07-FOTO con transición de fondo y apartó el círculo de I11-FOTO. `generar_variantes_fotograficas_historias.js` subió H21, subió y espejó solo la fotografía de H23 y espejó solo la fotografía de H24. Después de un primer cero automático, la lectura humana detectó que algunos alt text aún sonaban poco naturales; se reemplazó “una quiz” por “un cuestionario” y se eliminó la construcción “sobre ¿…?.”.
- **Motivo:** resolver exactamente lo autorizado, preservar rostros como zona protegida, evitar promesas comerciales no demostradas y convertir cada defecto en una regla que sobreviva a futuras regeneraciones.
- **Archivos afectados:** los cuatro generadores anteriores; originales y manifiestos de SEMANA-03 a SEMANA-06; variantes fotográficas C03, C04, C05, I07, I09, I11, H21, H23 y H24; láminas y documentación de `REVISION-LOTES/`; biblioteca fotográfica; `AUDITORIA-CONTENIDO/20260927T054228Z/hallazgos.json`; nueva auditoría `20260927T065839Z/`; `REGLAS_QA_APRENDIDAS.md`; `CONTENIDO-ESTATICO/CHANGELOG.md`; y esta bitácora.
- **Validación:** los cuatro generadores pasaron `node --check`. Los lotes se regeneraron con la herramienta nativa de macOS y la biblioteca volvió a 54 activos. Los diez PNG directamente corregidos se inspeccionaron a resolución completa. La auditoría final recorrió 252 artes —126 originales y 126 variantes—, produjo doce láminas de contacto y reportó 0 errores, 0 alertas y un gate de solapamiento aprobado. Las doce láminas se inspeccionaron visualmente. `hallazgos.json` de origen conserva los siete hallazgos, decisiones y resultados; todos tienen `resolution_status: resolved` y referencia a `20260927T065839Z`.
- **Resultado:** los siete grupos de hallazgos quedaron resueltos y no quedan hallazgos confirmados abiertos en el alcance auditado. El cierre está documentado en `AUDITORIA-CONTENIDO/20260927T065839Z/CIERRE-AUDITORIA.md`. Nada fue publicado; la aprobación histórica de originales no se transfiere a las variantes fotográficas.
- **Aprendizaje:** un check en cero no reemplaza la lectura humana: la gramática de un alt text puede fallar aunque ninguna expresión regular se active. En composiciones con personas, espejar debe afectar solo a la fotografía; marca, texto, controles y dirección de lectura permanecen intactos. Los datos comerciales inciertos deben degradarse a lista de interés hasta que exista evidencia.
- **Pendiente:** la publicación, la aprobación editorial de las variantes fotográficas y la configuración de interacciones nativas permanecen fuera de esta corrección. La medición total de tokens se actualizará con los checkpoints de aplicación, reauditoría y documentación de cierre.

### 2026-09-27 — Retrabajo acelerado recibe V2 y un QA visual obligatorio de tres pases

- **Petición:** revisar nuevamente el explainer del Guion A porque había elementos superpuestos o prematuros, mejorar las gráficas, añadir algo más de color y elevar los subtítulos; además, revisar o crear una skill que impida repetir estos defectos mediante dos o tres controles y corrección antes de entregar.
- **Punto de partida:** `videos/retrabajo-acelerado/` ya contenía un master completo. Una auditoría nueva confirmó puntas de flecha prematuras en la escena 04, fichas y estaciones coincidentes en la escena 06, estaciones futuras y un destino cubierto en la escena 10, captions demasiado bajos y una paleta muy dependiente del coral.
- **Cambios:** se creó `videos/retrabajo-acelerado-v2/` como copia independiente. Se ocultaron conectores y estaciones hasta su entrada, se rehicieron desplazamientos internos y fades, se sacaron etiquetas de las trayectorias animadas, se retimaron los estados de la escena 10, se elevaron los captions de 1600 a 1440 px, se redujo su banda, se limitaron al final real del video y se añadieron ocre y salvia con función semántica. Se reforzaron tarjetas, bordes y leyendas. La skill personal `visual-quality-director` se actualizó para exigir diagnóstico, corrección y revisión de entrega con `t±2` fotogramas en cada transición, métricas y evidencia del MP4.
- **Motivo:** una validación automática o un snapshot aislado no detectan todos los defectos de coreografía. El control debe revisar estados intermedios, escenas cortas y el archivo renderizado, y distinguir un crossfade deliberado de un objeto residual.
- **Archivos afectados:** `NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado-v2/`; sus composiciones, captions, diseño, scripts de extracción, QA, changelog, log y render; `NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/CHANGELOG.md`; `~/.codex/skills/visual-quality-director/SKILL.md`; `~/.codex/skills/visual-quality-director/references/hyperframes-verification.md`; y esta bitácora. La V1 y VIDEO-01–VIDEO-15 se conservaron.
- **Validación:** la skill pasó `quick_validate.py`. HyperFrames check terminó aprobado con 0 errores de layout, 0 errores/avisos de motion y 42/42 comprobaciones de contraste. Cinco avisos transitorios se verificaron sobre el MP4. La tercera revisión extrajo e inspeccionó 83 fotogramas: tres estados por cada una de once escenas y cinco alrededor de cada una de diez transiciones. FFmpeg decodificó el archivo completo sin errores y no detectó intervalos negros. `ffprobe` confirmó H.264 1080×1920, 24 fps, AAC estéreo 48 kHz y 52,958333 s. El audio mide -14,13 LUFS, -1,52 dBTP y LRA 1,20 LU.
- **Resultado:** `renders/video-v2-delivery.mp4` queda como candidato V2, con SHA-256 `1873e0cd0ffa965ffa3fc6db2966c4e32123ff33eeae0b527d72cf7a53e13a5f`. En los estados inspeccionados no quedan colisiones visuales persistentes entre captions, títulos, tarjetas, diagramas o controles. La escucha humana continua y la aprobación audiovisual siguen `por confirmar`.
- **Aprendizaje:** los mundos desplazables necesitan visibilidad independiente por estación; una etiqueta de destino no debe compartir el carril de un objeto; los captions se validan contra zonas críticas y no solo contra el borde; y una entrega sólo cierra visualmente después de revisar el MP4 alrededor de todos los cambios de escena.
- **Pendiente:** reproducción humana continua con sonido, aprobación explícita de la V2 y, si se adopta como master, registro de esa aprobación ligado al hash exacto. Los avisos heredados de IDs numéricos y editabilidad de Studio quedan como deuda técnica no visual.

### 2026-09-27 — La investigación de mercado se separa del proyecto de edición

- **Petición:** mantener investigación y producción de videos separadas, completar arquitectura de captura gratuita/pagada y considerar computador, extensiones, MCP y Muse Code cuidando la cuota semanal.
- **Punto de partida:** radar Meta alojado en `Framework-Edicion-Social/research/market-intelligence/` y skill local, con nueve candidatos históricos sin verificación directa suficiente.
- **Cambios:** se trasladaron radar y skill al proyecto hermano `/Users/iomijhondavid/Documents/Codex/Investigacion-Mercado-Meta`. Las rutas previas son enlaces simbólicos de compatibilidad. Se conservaron datos/historial y se archivaron versiones previas de prompts/README. El proyecto nuevo tiene sus propias instrucciones, bitácora, arquitectura, comparación de costos, política, esquema y piloto. Los 30 videos son referencia opcional, no requisito del radar.
- **Motivo:** no mezclar investigación de mercado con edición ni sesgar descubrimiento por contenido ya producido.
- **Archivos afectados:** carpeta/skill trasladadas; `Framework-Edicion-Social/OPERACION_RADAR.md`, `Framework-Edicion-Social/CHANGELOG.md`, esta bitácora y documentos del proyecto independiente.
- **Validación:** enlaces comprobados y lectura desde la raíz nueva; documentación oficial consultada. El control Chrome devolvió navegador no disponible y el control nativo falló al iniciar; no se vieron cuentas ni métricas nuevas. La validación local definitiva queda registrada en `Investigacion-Mercado-Meta/BITACORA_INVESTIGACION.md`.
- **Resultado:** investigación físicamente separada, sin eliminar versiones ni modificar videos. No se instalaron extensiones, no se activaron proveedores pagados y no se cambió la configuración de la automatización instalada.
- **Aprendizaje:** el proyecto de investigación debe tener su propio contrato; su salida puede servir a edición sin depender de ella.
- **Pendiente:** acceso técnico a navegador/computador o captura manual y smoke test pequeño; continuar seguimiento en la bitácora nueva. No se ejecutaron siete noches ni una muestra extensa.

### 2026-09-28 — El radar técnico consolida la semana 2026-W40

- **Petición:** ejecutar el radar diario y, por ser lunes, consolidar las observaciones de los últimos siete días, revalidar fuentes y producir decisiones y experimentos acotados sin convertir tendencias en reglas.
- **Punto de partida:** existían observaciones del 23 al 27 de septiembre; los días 24 y 25 registraban cambios oficiales de YouTube, mientras el 26 y 27 no mostraban novedades materiales. `experiments/registry.json` continuaba vacío.
- **Cambios:** se añadió `research/observations/2026-09-28.json` con estado `no_material_change`; se creó `research/reports/2026-W40.md`; y se registró la consolidación en el changelog especializado. El informe mantiene el máster universal, propone condicionalmente Shorts Series y una comparación de hasta tres hooks, y deja ambas pruebas pendientes de disponibilidad y decisión humana.
- **Motivo:** transformar novedades oficiales en oportunidades verificables sin generar renders redundantes ni afirmar viralidad con una muestra insuficiente.
- **Archivos afectados:** `Framework-Edicion-Social/research/observations/2026-09-28.json`, `Framework-Edicion-Social/research/reports/2026-W40.md`, `Framework-Edicion-Social/CHANGELOG.md` y esta bitácora.
- **Validación:** se reconsultaron fuentes oficiales de YouTube, Meta y TikTok; se deduplicaron los cambios ya registrados; se revisaron las fechas de las 29 reglas y el registro vacío de experimentos. `scripts/validate_framework.py` terminó correctamente: 94 archivos JSON, 113 instancias validadas y seis observaciones diarias.
- **Resultado:** no apareció un cambio material nuevo el lunes. El informe semanal conserva tres cambios oficiales de YouTube, cero patrones observados y dos experimentos opcionales; no modifica reglas, perfiles, experimentos registrados ni renders.
- **Aprendizaje:** una función nueva de plataforma puede justificar una prueba de distribución sin justificar otra edición completa. La disponibilidad por cuenta, la atribución de métricas y una línea base comparable siguen siendo gates.
- **Pendiente:** confirmar acceso real a Shorts Series y a la prueba de cortes antes de registrar o ejecutar cualquiera de los experimentos; revisar `HOOK_UNDERSTANDABLE_FIRST_FRAME` antes del 2026-10-07.

### 2026-09-30 — Preparación del lote 21–25 y mejora continua del flujo

- **Petición:** empezar VIDEO-21, analizar una sola vez el lote 21–25, aplicar documentación, plantillas, dirección visual y QA; mejorar continuamente tiempos de edición y revisión.
- **Punto de partida:** original local sin transcripción ni take-map 21–25; recursos provisionales preparados; reglas de ingesta y QA vigentes.
- **Cambios:** fuente registrada con SHA-256, preflight de grabación, probe y muestras técnicas de audio; auditoría de métricas históricas y plan operativo de mejora continua.
- **Motivo:** evitar análisis repetidos y renders completos antes de detectar fallos de transición, sin rebajar controles de calidad.
- **Archivos afectados:** `Serie-IA-Negocios-10-Videos/00-INGESTA/source-manifest.json`, `lote-21-25.recording-preflight.json`, `analysis-21-25/`; `Framework-Edicion-Social/MEJORA_FLUJO_21_25.md`, `OPERACION_OPTIMIZACION.md`, `CHANGELOG.md`; esta bitácora.
- **Validación:** preflight de grabación 14 pass, 0 fail; preflight profundo de ingesta pass_with_warnings por selección auditiva pendiente. AAC índice 1 decodifica; pista 2 no tiene decodificador local. Hash fuente `550b859be04b16e7744ca738b1f460e16e503d9735c3581477482f33f34d33ac`. No se afirma escucha.
- **Resultado:** preparación técnica y mejoras documentadas; no hay edición ni render del 21 todavía.
- **Aprendizaje:** VIDEO-13 concentra aproximadamente 97,7 % del tiempo de render en captura HDR por capas; los fallos de VIDEO-15 justifican validar segmentos y límites en el mismo pipeline final. El ahorro futuro permanece por confirmar.
- **Pendiente:** selección de audio y revisión auditiva verificable, transcripción única, mapa de todas las tomas, proxies y gate 21–25; edición del 21, tres pasadas QA y medición comparativa.

### 2026-09-30 — Revisión y supresión de ruido en voz

- **Petición:** revisar bien el audio y aplicar supresión cuando existan sonidos de fondo ajenos a la voz.
- **Punto de partida:** QA general de ruido e inteligibilidad; sin protocolo explícito de denoise localizado en los documentos inspeccionados. No se afirma ausencia de procesamiento en todos los videos históricos.
- **Cambios:** protocolo de diagnóstico, bypass o reducción, A/B, fidelidad, sincronía y trazabilidad; integración en QA y prompt operativo; piloto exploratorio original/procesado a 48 kHz.
- **Motivo:** mejorar limpieza sin borrar consonantes, respiraciones ni naturalidad; probar corto antes de procesar tomas completas.
- **Archivos afectados:** `Framework-Edicion-Social/AUDIO_LIMPIEZA_VOZ.md`, `QA_PROFESIONAL.md`, `PROMPT_INGESTA_Y_EDICION.md`, `CHANGELOG.md`; `00-INGESTA/analysis-21-25/audio-denoise-pilot/`; bitácora.
- **Validación:** FFmpeg dispone de afftdn/arnndn/anlmdn; el piloto afftdn termina exit 0; ambos WAV son 48 kHz y 15 s, hashes registrados. DeepFilterNet no está en el Python/PATH inspeccionados.
- **Resultado:** regla aplicable desde VIDEO-21, piloto no seleccionado; escucha y mejora perceptual por confirmar. Original intacto.
- **Aprendizaje:** normalización y gate no equivalen a supresión; herramienta disponible no demuestra calidad en una voz concreta.
- **Pendiente:** diagnosticar la toma aprobada, comparar candidatos por escucha, elegir intensidad o bypass y verificar mezcla/sincronía final.

### 2026-09-30 — Revisión previa compartida y memoria de limpieza de voz

- **Petición:** continuar VIDEO-21 con análisis único 21–25, plantillas/QA y revisión de ruido persistente.
- **Punto de partida:** ingesta técnica preparada; pista pendiente de escucha; recursos sin vincular a toma.
- **Cambios:** muestreo visual compartido de trece frames inspeccionados, detección de pausas, control de seis hashes, nota de composición/plantilla T21 y persistencia de limpieza en perfil, AGENTS y prompt individual.
- **Motivo:** reutilizar decisiones comprobadas del lote y evitar que la nueva regla de audio quede solo en un documento aislado.
- **Archivos afectados:** `00-INGESTA/analysis-21-25/visual-scan/`, `silence-full-aac.log`, `silence-full-aac.json`, `REVISION_PREVIA_21_25.md`; AGENTS de serie; perfil creativo, prompt individual, changelog del framework y bitácora.
- **Validación:** trece imágenes existentes y visualmente inspeccionadas; seis hashes de recursos coinciden; silencio técnico detectado sin clasificación editorial. Se documenta que zscale no está disponible y la lámina no valida color HDR→SDR.
- **Resultado:** evidencia previa reutilizable, sin inicio de montaje ni aprobación ficticia. Muestra de pista presentada para escucha; respuesta pendiente.
- **Aprendizaje:** gestos de manos exigen muestreo de la toma definitiva; una plantilla aprobada aporta lenguaje visual, no copia de texto ni aprobación del video.
- **Pendiente:** confirmar pista por escucha, transcripción única, marcadores y correcciones verificadas, proxies/gate, edición y QA completo del 21.

### 2026-09-30 — Ingesta compartida16–20, control temprano de ASR y mejora del flujo

- **Petición:** iniciar VIDEO-16 usando documentación, plantillas, dirección visual y QA existentes; analizar el maestro16–20 una sola vez; incorporar diagnóstico/supresión de ruido cuando haga falta; proporcionar prompt para21–25 y mejorar tiempos continuamente. Agentes autorizados por el usuario.
- **Punto de partida:** maestro16–20 recién disponible, recursos provisionales sin toma aprobada; gate de ingesta aún abierto. Otro chat prepara21–25 y escribe documentación común, por lo que las actualizaciones se fusionan bajo lock sin borrar su historial.
- **Cambios:** fuente registrada por hash, probe/preflight, audio de análisis extraído una vez, detección de pausas y hoja compartida28muestras. ASR large-v3 completo conservado tras detectar bucle/omisión; recuperación en9bloques contexto0 reutilizando WAV, más dos consultas locales de puentes. Se añade validadorASR temprano con9pruebas, propuesta25bloques/5videos, dirección T16Opt-Out con protección de cara/gestos y diagnóstico/A-B de voz del16. Se actualizan reglas de ruido, operación, README/AGENTS y `MEJORA_FLUJO_16_20.md`. Se crea prompt21–25 y tablero con dueño16. El flujo HyperFrames actualizó12skills mediante su rutina de actualización; no implica cambio del modelo activo.
- **Motivo:** evitar cortes/captions basados en una transcripción corrupta, repetir análisis del maestro por video, procesar voz sin beneficio y renderizar todo antes de revisar transiciones problemáticas.
- **Archivos afectados:** `Serie-IA-Negocios-10-Videos/00-INGESTA/source-manifest.json`, preflight/lote/transcript/take-map provisionales, `analysis-16-20/` y auditorías de ingesta/reglas/audio/dirección; `scripts/validar_transcripcion_ingesta.py` y sus pruebas; AGENTS/README/QA de serie, `production-board.json`, `PROMPT_LOTE_21_25_VIDEO_21.txt`; perfil creativo y documentos AUDIO/OPERACION/MEJORA_FLUJO/CHANGELOG del framework; bitácora. Source-manifest previo y resultadosASR fallidos preservados.
- **Validación:** maestroSHA256 `b061d3bc429bea65ffbd23790a98758ea35d156ab9c357ddef5fa377ba763bac`, duración769,0517s, HEVCMain10HLG/BT.2020, visual1080×1920/≈30fps, AAC48k decodificable y APACsin decodificador local. Preflightgrabación14pass; proyecto pass_with_warnings por escucha. Nueve pruebasASR PASS; validación del original FAIL por cobertura/repetición/17,55% palabras sin duración; recuperación FAIL por marcador19 ausente y8retrocesos/8solapes. Recuperación suma30,039s de procesos, sin demostrar calidad equivalente ni ahorro global. Gate16–20 ejecutado sin recibo y falla por revisión/correcciones/tomas/proxies/pista pendientes. Hoja inspeccionada solo para geometría, no colorSDR. Diagnóstico de voz16k estima suelo≈−66dBFS/SNR≈42dB; pilotoafftdn moderado reduce suelo≈2,3–2,4dB, latencia25ms compensada en candidato técnico, escucha y validación48k pendientes.
- **Resultado:** análisis compartido y prevención operativa reutilizables. Propuesta150,95s de contenido útil, no tomas aprobadas. No se declara editado/renderizado/aprobado VIDEO-16 ni cerrada la ingesta. No se ha aplicado limpieza a voz final ni modificado videos previos aprobados. Modelo efectivo/tokens/costo de este trabajo: no verificados.
- **Aprendizaje:** validar saludASR inmediatamente evita propagar defectos; contexto0 acotado recupera semántica pero no garantiza alineación; una métrica de ruido no sustituye oído; JPEGgeométrico no demuestra colorHLG; tiempo de procesos no equivale a pared ni ahorro global. Reservas del tablero no detectan procesos reales: un proceso pesado por propietario y liberar carga al esperar revisión.
- **Pendiente:** paquete compacto de escucha, confirmar identidad19/remate y hook20, revisar última corrección/fonemas/pista, reconciliar mapa/transcripción, proxies y gate; después editar16, QA completo y aprobación explícita del candidato. CapturaQA agrupada se estudia como experimento, no cambio estable. Medir ahorro por fase al cerrar videos comparables.

### 2026-09-30 — Paquete de escucha16–20 y medición de capturas de QA

- **Petición:** concretar revisión compacta y comprobar una mejora de tiempo antes de cambiar el proceso estable.
- **Punto de partida:** propuesta semántica con dudas19/20, ASR no elegible para gate y diseño de benchmark sin medición.
- **Cambios:** se generó paquete ingesta con cinco montajes candidatos y tres ventanas originales, HTML con24botones de contexto al maestro y manifiesto de comandos/rangos/hashes. Se comparó captura de seis imágenes en un proceso frente a seis seeks. Se inspeccionaron tres muestras geométricas del candidato16 y se liberó su reserva pesada manteniendo dueño ligero.
- **Motivo:** presentar material concreto para escuchar sin repetir búsqueda del maestro y adoptar optimizaciones solo tras verificar equivalencia.
- **Archivos afectados:** `analysis-16-20/build_ingest_review_package.py`, `ingest-review-package/`; `auditor-reglas/capture-benchmark/`; informe `MEJORA_FLUJO_16_20.md`, tablero16, changelog y bitácora. `qa_post_render.py` no cambia; fuentes/proxies oficiales16–20 no se promueven.
- **Validación:** ocho salidas pasan decode completo, probeHEVCMain10HLG720×1280/AAC48k y comprobación de hashes;223,066668s/64.973.604B. Encoderhardware funciona sin fallback:81,508s sumados de encode y18,208s de decode, no pared total. Tres frames del16 (0,5/19/27s) vistos para orientación/cabeza; no prueba de color ni escucha. BenchmarkVIDEO15 de21,1s: calibración6/6PNG idénticos y PTS exactos; tres paresAB/BA/AB con36PNG idénticos dentro de cada par, mediana1,765364→0,977326s/diferencia0,788039s (44,64%) en captura. Hashfuente antes/después coincide. La suma decimal mostró un falso desacuerdo≈28µs; se preserva el informe inicial y se corrige en v2 mediante ticks1/15360, sin nueva calibración.
- **Resultado:** revisión ingesta materializada, sin aprobación humana simulada. Se corrige el recuento de la entrada anterior:24bloques retenidos, no25 (cuatro16 y cinco por cada17–20). Las24ventanas de contexto son otro recuento independiente. Captura agrupada queda propuesta condicionada; no se afirma ahorro global de QA ni edición. No se entregó VIDEO-16 editado.
- **Aprendizaje:** equivalencia exige comparar píxeles y PTS; timestamps se comparan en ticks para evitar falsos desajustes. Un archivo corto y CFR no demuestra beneficio para largos/VFR. Un paquete técnico aprobado por decode no demuestra fonemas completos ni decisión editorial.
- **Pendiente:** selección de AAC por escucha, identidad19/últimas palabras, iniciohook20 y confirmación de todas correcciones/empalmes; reconciliar mapa/transcript, proxies y recibo16–20. Después montar16 segúnT16, cerrar tres pasadas y aprobación. Verificar extracción agrupada en perfiles adicionales al existir necesidad; no repetir benchmark sin motivo.

### 2026-09-30 — Montaje provisional16 y mejora continua medible

- **Petición:** revisar dónde optimizar tiempos y revisión permanentemente; continuar16 usando reglas/plantillas, ingesta compartida y revisión de ruido.
- **Punto de partida:** análisis16–20/paquete compacto existentes, gate estricto sin aprobación; excepción vigente AGENTS autoriza avance provisional. Documentos de optimización aún contenían el bloqueo histórico por falta de escucha.
- **Cambios:** ingesta provisional auditada por hashes/rangos y montaje16 de28,5s, cuatro cortes,22grupos captionsDTW, T16, B-roll2s y cuatro SFX. SDR gestionado y voz48k desde original; denoise bypass técnico. Protocolo MEJORA_CONTINUA y medidor de comandos con intentos/logs/hash/resumen de solapes. Se alinean documentos16/21/OPERACION con excepción. Lint detectó rutas y entradaHDR duplicada; corregidas en generador, variante conservada como template. SlotsSFX ajustados; excepción tipográfica estrecha por líneas tras inspección de tinta. Capturas iniciales preservadas.
- **Motivo:** evitar repetir ingesta, descubrir fallos antes de render completo, eliminar checks redundantes y medir retrabajo sin inventar ahorro ni bloqueos incompatibles con autorización.
- **Archivos afectados:** Framework-Edicion-Social/MEJORA_CONTINUA.md, OPERACION_OPTIMIZACION.md, MEJORA_FLUJO_16_20.md, MEJORA_FLUJO_21_25.md, scripts/medir_proceso.py y su prueba/CHANGELOG; recibo/mapa/proxies/rangos provisionales de00-INGESTA; VIDEO-16/editable-hyperframes-video-16 con brief/diseño/HTML/assets/scripts/QA/varianteHDR; VIDEO-16/process-events, métricas/CHANGELOG y tablero; bitácora. Entorno: FFmpegfull9.0.2 para zscale; Homebrew actualizó x265 y se restauró compatibilidad del binario8 con symlink a librería4.2 preservada.
- **Validación:** cinco pruebas del medidor PASS (fallo/args literales/log alterado/solapes/ejecutable ausente). Primer lint FAIL7 en0,948s; primer check13,206s falla4overlaps y advierte2SFX. Check corregido estricto PASS9,678s; no significa QA integral ni motion assertions cubiertas. Director y raíz inspeccionan imágenes de títulos: tinta separada pese a bbox; evidencia limitada a imágenes. Medios: probe/hashes1080×1920/BT.70928,5s y PCM24bit48k28,5s; comandos20,556+1,282+1,197s. Ruido técnico48k≈−66..−64,5dBFS, cero clipping, no beneficio auditivo afirmado. FFmpeg8 restaurado pasa versión y decode funcional0,1s del SDR. No escucha humana realizada.
- **Resultado:** mejora persistente y medidor en uso; editable16 provisional con check estricto aprobado técnicamente. No render ni aprobación final ni QA completo declarados. CapturaQA estable intacta; ahorro global por confirmar.
- **Aprendizaje:** las herramientas de caché/dependencias existentes requieren ejecución y manifiestos, no solo cita. Rutas de subcomposición deben resolver desde raíz y existir una sola entrada. Bbox tipográfica no equivale a tinta; excepción por elemento con evidencia, nunca global. Instalaciones pueden afectar binarios previos: rutas explícitas y pruebas de compatibilidad.
- **Pendiente:** muestras de escenas y retorno, QA audio/ritmo e integral, preview y aprobación/render autorizado; naturalidad/fonemas por confirmar. Afinar ambigüedades17–20 antes de usar sus rangos. Completar tiempos y comparar fases equivalentes al cerrar cinco videos.

### 2026-09-30 — Preview provisional16 v5, QA trazable y prevención de ciclos repetidos

- **Petición:** continuar16 con dirección/QA y mejorar continuamente tiempos de edición y revisión; incluir voz limpia cuando corresponda y prompt21–25.
- **Punto de partida:** montaje provisional28,5s con check básico; faltaban cobertura de captions/cortes, titulares semánticos definitivos, auditoría sonora ligada al candidato y Studio persistente.
- **Cambios:** titulares v5 distinguen síntesis editorial y captions; frame/design sincronizados. Cursor de cortes a seis decimales, resolve23,28s en pausa, ganancias SFX1,56/0,45/0,30/0,95. Motion assertions específicas, dependency-map y ejemplo de invalidación por sonido; blueprint/recursos provisionales con hashes/esquema. Referencia registry no utilizada se conserva como template fuera de entradas activas. Prompt21–25 actualizado con excepción y medidor, previo archivado. QA provisional y manifiesto de preview fijan candidato/evidencias. Studio abierto y capacidad pesada16 liberada sin modificar21.
- **Motivo:** prevenir renders fallidos, texto redundante, SFX sobre última sílaba, falsos gaps por decimales y auditorías sobre versiones distintas; repetir controles solo con cambios relevantes y medir cobertura además de segundos.
- **Archivos afectados:** VIDEO-16 editable HTML/motion/BRIEF/frame/design/cut-plan/STORYBOARD, scripts/generador y variante; qa/audio-provisional, qa/reglas-provisional, snapshots, process-events, dependency-map/creative-blueprint/provisional-assets-manifest, QA_PREAPROBACION_PROVISIONAL.md, preview-manifest.json, métricas/CHANGELOG; auditoría VISUAL_PREVIEW_V5 e evidencia en analysis16–20; prompt21–25/tablero; MEJORA_CONTINUA/CHANGELOG y bitácora. Versiones previas preservadas.
- **Validación:** check final70,072s PASS:42tiempos dirigidos,300muestras motion/34assertions, cero errores/warnings. Snapshot30,407s:43PNG/5hojas, todos22captions; root revisa1/3/5 y director2/4 más8PNG. Sin defectos visuales bloqueantes en muestras; no inspección de cada fotograma. PCM referencia28,5s:−15,0LUFS/LRA4,4/TP−1,8, clipping0/pausas>1,25s0; loudness0,212s. Studio responde, reproducción0→28,5 observada por estado inicial/final, lint0/0 y consola consultada sin errores; no escucha humana ni QA del MP4. Esquema blueprint y10recursos alcanzables/hash pasan con licencias de fuentes por confirmar.
- **Resultado:** montaje concreto en preview provisional, aprobación y naturalidad auditiva pendientes. Las tres pasadas tienen cobertura visual/técnica documentada y límites explícitos; no se afirma gate estricto, QA final, render ni entrega aprobada. La supresión de ruido permanece bypass técnico, no se adopta el piloto sin beneficio confirmado.
- **Aprendizaje:** congelar y comparar hashes antes de distribuir imágenes; validar selectors de motion por ID antes de muestreo denso; una modificación de HTML necesita comprobar si cambió audio antes de regenerar WAV. Registrar fallos/causas/prevenciones; duración de comandos no demuestra ahorro global. Los seis screenshots del benchmark44,64% siguen siendo un experimento acotado.
- **Pendiente:** revisión/escucha del candidato y aprobación de render; comprobar MP4 exacto/color/sincronía/audio/UI tras render autorizado. Afinar dudas17–20 al usar rangos sin retranscribir maestro. Comparar tiempos equivalentes al cerrar cinco videos; no crear automatización periódica no solicitada.

- **Evidencia de congelación16:** `preview-manifest.json` creado y verificado contra17inputs/10assets/43PNG/5hojas. Puente `audio-preview-equivalence.json` acredita cinco tags/fuentes/tiempos/ganancias sonoros iguales excluyendo nuevos `data-hf-id`; WAVv3 y métricas originales intactos. No existe archivo completo del HTML histórico: baseline deriva de atributos observados en herramientas y JSON auditado, límite explícito. No se repitió WAV/ASR ni se convirtió el hash histórico en uno nuevo.

### 2026-09-30 — Preparación de entrega16 mientras espera aprobación

- **Petición:** continuar hacia entrega16 con reglas/QA y evitar trabajo repetido.
- **Punto de partida:** previewv5 congelado y sin aprobación de render; dos fuentes con documentación de licencia pendiente; varianteHDR no activada.
- **Cambios:** preflight estático de tags entre preview y templateHDR; documentación local de Inter copiada con hashes y coincidencia exacta de bytes. Evidencias separadas, sin modificar paquete congelado.
- **Motivo:** verificar reutilización del mismo montaje/audio en entrega y resolver una evidencia pendiente mientras se espera aprobación, sin renderizar antes del gate.
- **Archivos afectados:** VIDEO-16/qa-supplements/2026-09-30-delivery-preflight con hdr-template-preflight.json, font-license-evidence.json y copiasInter/LICENSE/metadata/package; changelog16 y bitácora.
- **Validación:** graph de tags idéntico excluyendo identidadesdata-hf-id y cuatro cambios de fuente/offset A-roll esperados; audio y overlays iguales; rangos41/78,3/118,7/127,9 cotejados con cut-plan y original enlazado. InterWOFF2 coincideSHA con paquete local que contieneLICENSE/OFL-1.1. EBGaramond no coincide con ningúnWOFF2 del paquete inspeccionado, origen exacto por confirmar. Preview congelado estable y aprobaciónpending.
- **Resultado:** evidencia de preparación de entrega, no activación ni render ni equivalencia de color comprobada. Inter queda documentada en suplemento; hallazgos históricos se conservan. EBpendiente, voz sin escucha y montaje sin aprobación.
- **Aprendizaje:** documentar coincidencia binaria y licencia juntas; el nombre de familia no acredita origen exacto. Comparar graph evita rehacer recursos sin demostrar equivalencia del resultado renderizado.
- **Pendiente:** aprobación del preview para render; QA del MP4 exacto/color/audio/UI; naturalidad por escucha y procedencia exactaEBGaramond por confirmar.

### 2026-09-30 — Autorización de render16 a criterio editorial

- **Petición:** «Rendirizslo a tu criterio si ya corriste todas las pruebas debe estar bien».
- **Punto de partida:** candidato16v5 congelado/QA técnico y visual provisional, render esperando aprobación.
- **Cambios:** recibo de autorización ligado al candidato; proyecto delivery-hdr-v1 aislado con mismos overlays/audio y fuente original HDR; reserva16 pesada para render. PreviewSDR intacto y versiones conservadas.
- **Motivo:** ejecutar autorización explícita sin otra confirmación y comprobar después el MP4 real.
- **Archivos afectados:** VIDEO-16/render-authorization-2026-09-30.json, delivery-hdr-v1/, tablero, changelog16 y bitácora.
- **Validación:** inputs/assets/43PNG/5hojas/evidencias congeladas conservan hashes. Comparación estática previa acredita tags iguales salvo cuatro fuentes/offsetsHDR. QA del resultado aún pendiente; no escucha humana afirmada.
- **Resultado:** render autorizado, no render final terminado todavía. El usuario delega criterio; no acredita revisión humana del preview/voz ni publicación.
- **Aprendizaje:** autorización de render y verificación del MP4 son hechos distintos; conservar preview aprobado y generar entrada de entrega aislada.
- **Pendiente:** lint de entradaHDR, render30fps/delivery y QA técnico/visual/audio del MP4 exacto, métricas y entrega.

### 2026-09-30 — Render16 v1 rechazado por captions congelados

- **Petición:** renderizar16 a criterio del agente y aplicar QA final.
- **Punto de partida:** candidato autorizado con preview/check sin defectos de captions; entradaHDR misma estructura/voz y fuente original.
- **Cambios:** renderHDRv1 guardado; QA decode/probe/loudness,42frames exactas conPTS y5hojas; auditorías visual/señal. Se rechaza salida por último cue visible todo el video. MP4 y QA preservados en qa-revisions/fail-hdr-v1. V2 prepara visibilidad explícitaGSAP/opacity para22captions y fixtureHDR4,8s antes de volver a renderizar28,5s.
- **Motivo:** comprobar MP4exacto, no confiar solo enStudio; reducir costo de corregir con prueba acotada del pipeline real.
- **Archivos afectados:** VIDEO-16/process-events, qa-revisions/fail-hdr-v1, qa-final/extract-targeted-frames.py/plan, delivery-hdr-v2, caption-hdr-smoke-4_8s; changelog16 y bitácora.
- **Validación:** primer render383,743s de pared del comando; HEVCMain10/HLG1080×1920/30fps/855frames/AAC48kstereo,28,5s/22.649.430B/SHA b7a5069e1ded5323b26faf8761083dd11aa2c8f25f9b515ab5c7eb4b67f3ab5d. QAtécnico4,631sPASSdecode completo y−15,1LUFS/LRA4,4/TP−1,4. Captura agrupada2,698s/42framesPTSverificadas. Root3/5 ydirector1/2/4 detectan último caption persistente; audio correlación0,99933/lag0en6ventanas,clip0/pausas>1,25s0. Diferencia aparente de rojo/crema tonemapped por investigar; no validaciónHDRcertificada.
- **Resultado:** FAILvisual; archivo rechazado no entregado comofinal. No vozduplicada técnica significativa; escucha humana sigueporconfirmar. ParcheV2 ysmoke aún por demostrar; no aprobación ficticia.
- **Aprendizaje:** visibilidad temporal de clips anidados puede diferir entreStudio y capturaHDR; exigir acento/caption cambiante, estado vacío y fin en un export corto antes del largo. Captura por índicesCFR30+PTS pudo cubrir42estados con un decode; no ahorro global afirmado.
- **Pendiente:** demostrar correcciónGSAP en smoke real, investigar diferencia de color, propagar prevención al generador, rerender y QA del nuevohash antes de entregar.

### 2026-09-30 — Mitigación de captionsHDR demostrada y persistida

- **Petición:** resolver el fallo y entregar16 autorizado; mejorar flujo para próximos videos.
- **Punto de partida:** MP4v1rechazado por último caption persistente, audio correcto y preview correcto.
- **Cambios:** CSSopacity0 enwrapper yGSAPon/off por22cues; parche eneditable/generador ydeliveryV2, versiones anteriores archivadas. FixtureHDR4,8s yseisframes; protocolo permanente enMEJORA_CONTINUA/QA/PROMPT. Nueva entregaHDR completa en curso ySDR1080 preparada desdeoriginal gestionado.
- **Motivo:** superar diferencia real entrevisibility deStudio ycompositorHDR sin rehacer voz/cortes/captions; ensayar corto antes de repetir largo.
- **Archivos afectados:** compositions/captions-es.html y scripts/build_composition.py, revisions/caption-opacity-fix, delivery-hdr-v2/delivery-sdr-v2/caption-hdr-smoke-4_8s, qa-final/smoke-frames yprocess-events; diagnóstico supplemental, documentos/changelogframework, changelog16 ybitácora.
- **Validación:** smokeHDRPASS29,253s; root inspeccionó0/0,8667/1,8333/2,8/3,5333/4,5s: vacío,primer/segundo/tercer cue,vacío,cuarto cue. Checkposterior42tiempos/300motion/34assertions0errores/0warnings70,488s. CódigoCLI0.8.98 respalda fuga devisibility!important por descendientes; display:flex no causa autónoma demostrada. Gamut/HLGinspeccionados estáticamente, sin dictamenperceptual.
- **Resultado:** corrección demostrada en smoke ychecks; renderlargoV2 pendienteQA. Captionbehavior previsto coincide con diseño autorizado; no nueva escucha ni entrega aprobada fingida.
- **Aprendizaje:** ocultarwrapper conopacity evita que un hijo fuercevisibility; un ensayo con trescues+gap descubre regresión. Conservar fallo ycostoreal para prevención futura, no afirmar minutosahorrados sin comparación completa.
- **Pendiente:** completarHDRV2, exportSDRcompatible, QA exacto visual/señal/color por destino, binding final/metrics y entrega. Naturalidad auditiva yHDRdisplaycertificados porconfirmar.


### 2026-09-30 — VIDEO22 reutiliza ingesta y prueba captions en HLG antes de revisión completa

**Petición:** continuar22 y mejorar el framework sin dañar el flujo. **Punto de partida:** T22 aprobado, recursos y cinco rangos/proxy del lote21–25 ya preparados; selección humana no verificada.

**Cambios y motivo:** editable propio papel/verde y cinco etapas, voz real68palabras/cierre corregido,16captions, apoyo metafórico2s y cuatroSFX. Denoise conservador conA/B y25ms compensados. PilotoHLG detectó último subtítulo persistente aunquecheck pasaba; generador ahora dirige opacity del contenido de cada cue y salida explícita. No se repiteASR ni análisis completo del maestro.

**Archivos afectados:** VIDEO22/editable-hyperframes-video-22, CHANGELOG.md y FUENTES_EDITORIALES.md; helper experimentalFramework-Edicion-Social/scripts/qa_visual_boundaries.py. **Validación:** check final120estados/44contrastes; dospilotos6fps, segundo inspeccionado en116fotogramas/cuatrohojas con captions correctos. Muestreo derive límites actuales, incluye±2/±1 y lectura;200PTS exactos comprobados en600frames sintéticos. No sustituyeQA estable ni demuestra ahorro global.

**Resultado:** montaje25,266667s provisional; render30fps yQA de candidato completo en curso. **Aprendizaje:** la visibilidad del compositorHDR puede diferir deStudio; probar captions reales y preservar fallos evita entregar una exportación errónea. Las duracionesFFmpeg llevan cero inicial. La expresión de selección de muchos frames necesita árbol balanceado. **Pendiente:** completar QA delMP4 exacto, escucha/naturalidad y aprobación22; no atribuir aprobación21 al22.

### 2026-09-30 — VIDEO16 entregado SDR y másterHDR v2 por criterio delegado

- **Petición:** renderizar a criterio del agente después de pruebas; mejorar tiempos y revisión, con limpieza de voz según necesidad.
- **Punto de partida:** preview v5 autorizado; V1HDR rechazado por caption persistente; fixopacity y smoke4,8s ya comprobados.
- **Cambios:** render finalSDR compatible y másterHDRv2; QA del archivo exacto; manifiesto/recibo de binding v2, cierre de pendientes técnicos, métricas y errata documental SDR. Reserva16 liberada y Studio detenido explícitamente después de revisión. Históricos conservados.
- **Motivo:** entregar un resultado verificable con paletaSDR coherente, conservar originalHDR y prevenir retrabajo por diferencias de compositor.
- **Archivos afectados:** VIDEO16/VIDEO-16-FINAL.mp4 y VIDEO-16-FINAL-HDR.mp4, delivery-*/, qa-final/, QA_FINAL.md, delivery-manifest.json, render-authorization-v2-binding.json, manifest/preview-manifest, METRICAS_PRODUCCION.md y CHANGELOG; Framework/MEJORA_CONTINUA.md y CHANGELOG; production-board y bitácora.
- **Validación:** ambos28,5s/855frames/1080×1920/30fps, decode/hashPASS; SDRH264BT709 y HDRHEVC10HLG/BT2020.42estados por archivo inspeccionados conjuntamente,22captions/gaps/apoyo/retorno/cierre correctos; check42tiempos/300motion/34assertions0errores/0warnings. Audio−15,1LUFS/TP−1,4, clip0/pausas>1,25s0/lag0seisventanas. SDRPCM no idéntico alHDR: QA independientePASS técnico, no equivalencia inventada.
- **Resultado:** entrega local renderizada por autorización, SDRprincipal SHA`cbc4dd2a7abd98b822739d7753db626ec14dfe796d3e4ea0eddec95598572ab3` y HDRSHA`ca5e6a004f063a6741652495e55c4e6636f39b38a853946acb2085f3c4a98a59`. V1rechazado archivado. Render36,632sSDR/392,358sHDR; perfiles distintos, no comparación equivalente. Sin afirmar escucha, aprobación humana ni publicación.
- **Aprendizaje:** check/Studio no sustituyen export real; smoke corto prueba cues/gap antes del largo. Reutilizar PCM comprobado evita QA repetido; diferencias entre variantes exigen comprobación dirigida. ExtractorSDR corrige descripción de límites sin cambiar evidencia histórica. No repetirASR maestro para17–20.
- **Pendiente:** escucha/naturalidad/fonemas/sincronía perceptual, pantallaHDR certificada, controles de plataforma y procedencia exactaEBGaramond por confirmar. Para17–20 afinar rangos ambiguos con ingesta existente. Denoise16 sigue bypass provisional por suelo de ruido bajo; original preservado.


### 2026-09-30 — VIDEO22 revisable y reutilización de imagen para corrección de audio

**Petición/punto de partida:** continuar22 con ingesta compartida; se completó el montaje provisional previamente registrado. **Cambios/motivo:** rotar entrada cálida0002 del21 a0003 aprobada y normalizar la nueva mezcla; conservar imagen comprobada sin recaptura redundante. **Archivos:** VIDEO22/manifest, QA_REVISION, dos scorecards propios, AUDITORIA_CIERRE, METRICAS_PRODUCCION, REVISION_USUARIO, editable/remix-review.py y evidencias; changelog/framework actualizados.

**Validación/resultado:** check120estados/44contrastes sin errores ni advertencias; render189,630s;161frames inspeccionados. Remux1,664s conserva hash del stream de video; nuevo QA de v2 decode/integridad/niveles−16LUFS/−1,7dBTP PASS. Source/ASR/mapa/proxy/rangos/assets ligados porhash. PerfilHDR conforme con advertencia de bitrate de revisión. Scorecard válido, delivery_allowed=false: escucha/dispositivos/aceptación no acreditados. **Aprendizaje:** aislar cambios por capa con evidencia ahorra recapturar imagen; congelar la elegibilidad/rotación antes de la primera mezcla evita detectarla tarde. Datos técnicos no sustituyen revisión humana. **Pendiente:** autorización/escucha22 antes de entrega final; no ampliar autorización21 ni aprobarpublicación. Studio3022 vivo y candidato actualv2 conservado junto a previos.

### 2026-09-30 — VIDEO16 revisión de fondo reportado por escucha del usuario

- **Petición:** corregir sonido de fondo que el usuario atribuye tentativamente al ventilador detrás del presentador.
- **Punto de partida:** entregaSDR/HDRv2 verificada técnicamente, bypass de denoise por nivel bajo; escucha nueva del usuario reporta molestia, sin confirmar aparato.
- **Cambios:** candidatoSDR/HDRv3 conafftdn8dB/perfil de pausa y contexto nativo48k antes de cortes,25ms compensados, voz renormalizada ySFX preservados; A/B de voz y residuo, receta reproducible y QA exacto. EntregasV2 sin cambios.
- **Motivo:** priorizar molestia percibida sobre suelo técnico; reducir fondo suavemente sin puerta dura ni procesar efectos.
- **Archivos afectados:** VIDEO16/qa-noise-revision-v3/* yVIDEO-16-REVISION-AUDIO[-HDR]-v3.mp4; CHANGELOG16, METRICAS_PRODUCCION y noise-revision-manifest; AUDIO_LIMPIEZA_VOZ.md, CHANGELOGframework ybitácora.
- **Validación:** ruido en tres pausas−5,89/−5,05/−6,76dB; voz cambia<0,001dB antes de normalizar/corr>0,999996; delay1200muestras medido y compensado. AAC28,5s48k,−15,1LUFS/TP−1,7,clip0/lag0seisventanas; decodePASSambos. Hash de paquetesimagen yPTS/DTS/duración iguales aV2; no nuevo rendervisual niASR.
- **Resultado:** dos copias de revisión conQA técnicoPASS pendientes de escucha nueva. SDRSHA`eaafb7679fe295bef149491bc65044bf05cafdefc34ba276bdb365a56175ec70`; HDRSHA`47e624499ffb3353a5a6d7c9bec5d3d0476ab72c58a859b1f7a380dafdb966f2`. Originales preservados; no aprobación ni fuente física fingidas.
- **Aprendizaje:** un ruido bajo puede resultar molesto tras normalización o según reproducción. La escucha reportada del usuario debe reabrir bypass; métricas no sustituyen revisión perceptual. Para ajuste soloaudio, remux con imagenexacta evita render/revisiónvisual duplicados.
- **Pendiente:** confirmar por escucha reducción suficiente y voz natural; si hace falta, intensificar por delta o evaluar otro algoritmo. Registrar criterio como feedback acotado a este fondo, sin modificar retroactivamente otros videos aprobados.

## 2026-09-30 — VIDEO22: corregir estructura narrativa expuesta al espectador

- **Petición:** el usuario detectó «la pregunta», «el contraste», «el ejemplo», «la idea» y «tu experiencia» en22; pidió usar palabras del contexto y nunca mostrar la estructura. También solicitó agente paralelo para revisar/corregir21, actualmente en curso.
- **Punto de partida:** candidato22v2 y editable T22 con rótulos narrativos. La prohibición de metadatos visibles ya estaba en QA_PROFESIONAL; la pasada anterior no la aplicó a esos nombres. Se conserva el historial y el MP4 previo.
- **Cambios/motivo:** rótulos «Lo que preguntas», «Lo que haces», «Lo que compras», «Observa la conducta», «¿Te ha pasado?»; avisos convertidos a significado contextual. Fuente de cinco escenas y generador sincronizados, BRIEF/frame/storyboard actualizados. Numeración conservada como mapa temático. Regla concretada en AGENTS de serie y QA del framework para prevenir recaídas.
- **Archivos:** VIDEO-22/editable-hyperframes-video-22/{build-composition.py,compositions/scene-*.html,BRIEF.md,frame.md,STORYBOARD.md,qa/rotulos-contextuales-2026-09-30/}; VIDEO-22/{manifest.json,REVISION_USUARIO.md,AUDITORIA_CIERRE.json,QA_REVISION.md,CHANGELOG.md}; Serie/AGENTS.md; Framework/QA_PROFESIONAL.md y CHANGELOG.md.
- **Validación:** check0.8.98 pasa120muestras y44/44contrastes, cero errores/avisos;30,129s medidos solo de comando. Modelo inspecciona cinco estados1/4,5/10/17,5/22,5s y recortes de encabezado. Comparación exacta confirma únicamente texto distinto en escenas; hashes de index/voz/audio/medios/captions/cortes iguales. Evidencia en qa/rotulos-contextuales-2026-09-30/evidence.json.
- **Resultado:** editable22 corregido y comprobado en Studio3022. MP4v2 pasa a histórico; no se presenta como la imagen corregida. Sin inventar escucha humana/aprobación/publicación.
- **Aprendizaje:** revisar todos los textos visibles, incluyendo navegación y anticipación, por intención semántica; un check técnico aprobado no detecta automáticamente una etiqueta de producción. Mantener el generador corregido evita reaparecer el error.
- **Pendiente:** MP4 con nueva imagen22 y revisión final correspondiente; agente21 prepara corrección/versionado/render bajo autorización previa. Su resultado se añadirá en entrada independiente.


## 2026-09-30 — corrección de rótulos contextuales y entrega HLG v2

Petición: revisar también VIDEO-21 en paralelo y evitar mostrar estructura narrativa. La entrega v1 contenía LA PROMESA / EL MITO / EL LÍMITE: la revisión previa no detectó este fallo editorial. Se sustituyen por NEUROMARKETING / SIN CONTROL REMOTO / COMPORTAMIENTO en HTML activo y generador; ENTENDER MEJOR conserva significado contextual. IDs internos permanecen para autoría.

Punto de partida y versiones preservadas: entrega v1, recibos históricos ENTREGA-HLG-v1.json y AUDITORIA_ENTREGA-HLG-v1.json; fuente editable anterior en qa/etiquetas-contextuales-v2/before. Cambios mínimos comprobados por comparación de HTML: solo tres rótulos (excluidos IDs editoriales HF). Todos los recursos, captions.json y cut-plan.json conservan hashes; el AAC codificado de entrega v1/v2 conserva SHA256 idéntico. No se repite ASR del lote.

Validación: diagnóstico en cuatro hojas v1; nueve estados del editable inspeccionados; check final 131 muestras, 17/17 contrastes, cero errores de runtime/layout/motion. Aviso de densidad existente: cinco conceptos coherentes en una pista, sin defecto de texto/composición observado. CLI actualizado 0.8.98→0.8.99 tras probe obligatorio y validado. Wrapper usa variables HYPERFRAMES_* oficiales y backend instalado con zscale/tonemap exclusivamente para proxy de Studio; render mantiene FFmpeg8.1.2 aislado.

Nueva entrega: renders/VIDEO-21-ENTREGA-HLG-v2.mp4, SHA256 73b68b1b51acf49269cfe9ef1f76a05ceca469e40ebb9dabb637df20bf7ef79a, 21,633333s/649frames,1080×1920/30fps HEVC Main10 HLG BT.2020. Render 148.263s; captura screenshot/hardware GPU. QApost técnico PASS 5.711s; 115 fotogramas extraídos en 3.854s con una decodificación y cuatro hojas inspeccionadas. Muestreo incluye límites ±2fotogramas, lectura de cada estado/caption y recorrido por segundo; no se afirma inspección de todos los649frames. Voz −16LUFS/LRA3.4/TP-1.5dB.

Resultado: rótulos corregidos visibles en MP4; rostro libre, captions legibles, apoyo1,9s y regreso comprobados en muestras. Gate validar_texto_visible.py PASS, cero etiquetas estructurales conocidas. Hook pre-render añadido y verificado sin nueva captura usando render --help. El gate solo reconoce la lista conocida: no sustituye lectura editorial de todo el texto.

Aprendizaje: la regla existía, pero se había comprobado legibilidad y no la diferencia entre guía interna y texto del espectador. Se corrige fuente generadora y se conecta control automático para evitar reincidencia. Pendiente: escucha/naturalidad humana por confirmar; flagsfalse, sin publicación ni nueva aprobación de visionado. Render local amparado por delegación explícita previa y petición de corrección. Studio: http://localhost:3021/#project/editable-hyperframes-video-21 (HTTP200 verificado).


### 2026-09-30 — Imágenes por contexto y realismo como regla global; alternativa tecnológica VIDEO16
+
+- **Petición:** sustituir imagen de recursos fuera de contexto por otra más tecnológica y natural; aplicar permanentemente prioridad de generación específica, banco como alternativa, evitando apariencia genérica de IA.
+- **Punto de partida:** apoyo de motor/taller20,9–22,9s y audio revisado v3; el usuario reportó «Ok mejoro» sobre ruido. Regla previa favorecía reutilización pertinente, sin este criterio explícito de realismo/diferenciación.
+- **Cambios:** imagen nueva de asesora/cliente eligiendo tecnología, prompt y hashes; candidato editablev4 con esa foto y voz limpia, fuente/captions/timing conservados. Documento IMAGENES_CONTEXTO_REALISMO, preferencia y regla confirmadas; referencias operativas en prompt/QA/flujo/README/AGENTS. Versiones anteriores preservadas.
+- **Motivo:** alinear apoyo con la frase real sobre atención personal; no forzar recursos disponibles ni asociar tecnología con clichés futuristas. Convertir la petición global en pasos de selección y QA verificables.
+- **Archivos afectados:** VIDEO16/visuals/video-16_technology_personal_service_v02.png y.prompt.txt, assets versión nueva, editable-image-v4 yqa, image-replacement-manifest-v4; Framework/IMAGENES_CONTEXTO_REALISMO.md, profiles/creative_preferences.json, rules/registry.json, PROMPT_EDICION_INDIVIDUAL.md, QA_PROFESIONAL.md, FLUJO_PRODUCCION_RAPIDA.md, README.md yCHANGELOG; AGENTS de serie, CHANGELOG16, métricas ybitácora.
+- **Validación:** PNG941×1672/hash coincide en copia runtime; agente inspeccionó imagen y cinco snapshots antes/temprano/medio/tardío/después: captions libres, caras/gesto/equipos visibles y retorno correcto. Check estrictoPASS61,874s,300motion/11contrastes, cero errores/warnings. Snapshots8,196s. CandidatoCLI0.8.98→0.8.99 por aviso, check verificado; original pin intacto. JSON/IDs únicos y referencias a regla comprobados.
+- **Resultado:** nueva imagen y editablepreview verificados; regla global adoptada por instrucción explícita, sin inferir aprobación de la foto. Imagen SHA`16f93d245445ee15eeda0997deeee708216fcec28d0a161b432600a15800d999`. Tool ImageGen integrado84,1s, modelo exacto no informado. MP4v4 no renderizado en solicitud de generación.
+- **Aprendizaje:** calidad técnica de recurso no prueba pertinencia; microacción y contexto específicos diferencian mejor que adornos de IA. Revisar plausibilidad/anatomía/miradas/pantallas e integración, sin prometer exclusividad o indetectabilidad. Mantener procedencia de la ilustración aunque su estilo sea fotográfico.
+- **Pendiente:** revisión individual de imagen/MP4v4 cuando se exporte; escucha completa de fidelidad por confirmar. Regla aplica a futuras ediciones sin reabrir renders previamente aprobados ni enviar mensajes a otros chats.
+

## 2026-09-30 — VIDEO22 aprobado, exportado y regla convertida en gate obligatorio

- **Petición:** «el22aprobado, por favor documentar esa regla y no se debe obviar, que pasa por que se salta las reglas ?». Se acepta el editable corregido y se completa su exportación local.
- **Punto de partida/causa:** la prohibición ya existía; rótulos de estructura se interpretaron erróneamente como navegación de plantilla. La revisión comprobó forma/legibilidad sin detectar esa intención editorial. Se conserva ese fallo en el historial.
- **Cambios/motivo:** guard `Framework-Edicion-Social/scripts/validar_texto_visible.py` e integración automática failclosed en wrappers21/22 antes de render. Recorre HTML/subcomposiciones activas, registra inventario/hashes, bloquea etiquetas conocidas numeradas o con anticipación y referencias ausentes. Nombres técnicos/IDs/captions grabados no se confunden con navegación. AGENTSserie/QAprofesional obligan gate y lectura visual de todo el texto; siguiente editable debe conectarlo, sin eludir wrapper. Lista conocida acotada, no detector semántico universal.
- **Archivos:** nuevo guard y `scripts/tests/test_validar_texto_visible.py`; wrappers21/22; AGENTSserie, QA_PROFESIONAL, MEJORA_CONTINUA, CHANGELOGframework; VIDEO22/{entrega/AUTORIZACION_RENDER_V1.json,entrega/VIDEO-22-ENTREGA-HLG-v1.mp4,ENTREGA.json,AUDITORIA_ENTREGA.json,AUDITORIA_CIERRE.json,manifest.json,CHANGELOG.md,QA_REVISION.md,REVISION_USUARIO.md,METRICAS_PRODUCCION.*}; evidencia específica en editable22/qa/{post-delivery-hlg-v1,delivery-v1-boundaries-full,delivery-hdr-profile-v1.json}.
- **Validación:** cinco pruebas de regresión PASS; gate22PASS ejecutado antes de captura.11checks de linaje/hashes incluidos original/ASR/mapa/proxy/HTML aprobado. Render204,500s; MP4 SHA0634dd5d27c6c4901496028505503898e7e6ce3ca01120d2185efe9c0c8879ba,25,266667s,758frames,1080×1920/30fps/HEVCMain10HLG/BT2020. Decode/integridad/metadatos/loudnessPASS3,877s,−16LUFS/LRA5/TP−1,0dB. Modelo inspecciona161frames en seis hojas: rótulos/captions/rostro/apoyo/retorno/cola correctos en muestras. Extracción3,567s conFFmpegfull9; intento previo0,179s por falta zscale8 conservado. No se alteró render/backend ni se repitióASR.
- **Resultado:** VIDEO22 entrega local completada después de aprobación del editable; VIDEO21v2 corregido en paralelo y registrado en entrada previa. Versiones anteriores conservadas. PerfilHDRcompliant, aviso de bitrate6,35Mbps frente a referencia12Mbps registrado; no certificaciónSDR/publicación.
- **Aprendizaje/optimización:** documentar por sí solo no aseguró la aplicación; convertir la regla en chequeo de entrada y leer todo el inventario evita repetir esta clase conocida de error. Reutilizar audio/cortes/medios porhash y recapturar solo cuando imagen cambia; no reciclar QA de una imagen anterior. Métricas22:19eventos675,375s de comandos, no tiempo total/tokens ni ahorro global medido.
- **Pendiente/límites:** escucha/naturalidad humana porconfirmar; aprobación editorial no acredita reproducción auditiva. Excepción y autorización permiten entrega local; no publicación ni aprobaciones ficticias. La revisión semántica completa sigue obligatoria además del blacklist.

### 2026-09-30 — VIDEO16 v4 completo para aprobación

- **Petición:** «como quedo video final para darle aprobacion».
- **Punto de partida:** editable v4 con imagen tecnológica contextual y voz limpia v3; snapshots/check aprobados técnicamente, MP4v4 aún sin exportar. Versiones anteriores preservadas.
- **Cambios:** renderSDRdelivery completo de28,5s; gate texto visible; QA del MP4 exacto, informe de tres pasadas y manifiesto para revisión. Puntero de candidato actualizado; aprobación sigue pendiente.
- **Motivo:** entregar al usuario la edición nueva reproducible para valoración, con ambas correcciones integradas.
- **Archivos afectados:** VIDEO16/VIDEO-16-PARA-APROBACION-v4.mp4, render_approval_v4.py, qa-approval-v4/, qa-final/post-render-v4/, qa-final/targeted-frames-v4/, QA_REVISION_V4.md, delivery-manifest-v4.json, image-replacement-manifest-v4.json, manifest.json, CHANGELOG.md, METRICAS_PRODUCCION.md, production-board y esta bitácora.
- **Validación:** gate textoPASS; input/check hashes iguales; render35.886s y decodePASS855frames;42PTS inspeccionados en cinco hojas y dos frames completos. AAC48k/28,5s/−15,1LUFS/TP−1,7, clip0, lag0en6ventanas, corr0.999356290, pausas>1,25s0. Escucha humana completa por confirmar.
- **Resultado:** versiónSDRv4 disponible para aprobación; SHA256df5b836f43fb38c6378dcdb34ee2ed78d2eb2e037133bffc3dc9af817f82804e. Imagen tecnológica20,9–22,9s y voz limpia integradas; no publicación ni aprobación inventada.
- **Aprendizaje:** reutilizar datos/voz y check congelados; validar diferencias sobre el MP4 exacto. Exportar una sola variante compatible para revisión y conservar antecedentes reduce trabajo redundante sin medir ahorro general.
- **Pendiente:** aprobación del usuario, escucha/fidelidad perceptual completa y origen exacto del ventilador por confirmar; HDRv3 anterior no equivale a imagenv4. Licencia exactaEBGaramond y certificados de pantalla/plataforma siguen pendientes previos.

### 2026-09-30 — Aprobación explícita del video16 v4

- **Petición:** «ok aprobado», respuesta al video final v4 presentado para revisión.
- **Punto de partida:** MP4v4 de28,5s con voz limpia e imagen tecnológica, QA técnico/visual registrado y aprobación pendiente.
- **Cambios:** recibo de aprobación explícita ligado a versión/ruta/hash; manifiestos de entrega/recurso y puntero final actualizados; añadido cierre al QA y changelog, con copias de estados anteriores.
- **Motivo:** fijar como final aprobada la versión aceptada y evitar confundirla con las revisiones previas.
- **Archivos afectados:** VIDEO16/APROBACION_VIDEO_16_V4.json, delivery-manifest-v4.json, image-replacement-manifest-v4.json, manifest.json, QA_REVISION_V4.md, CHANGELOG.md, qa-approval-v4/before-user-approval/, production-board y esta bitácora.
- **Validación:** SHA256MP4 `df5b836f43fb38c6378dcdb34ee2ed78d2eb2e037133bffc3dc9af817f82804e` verificado; hashes de siete pruebas, imagen y voz coinciden. JSON y enlaces de aprobación comprobados al guardar; no repetición de render/ASR/QA de medios intactos.
- **Resultado:** VIDEO16v4 aprobado editorialmente por el usuario; archivo de37.387.624B preservado intacto, anteriores disponibles.
- **Aprendizaje:** asociar aprobación a un artefacto exacto y conservar el estado previo separa aceptación editorial de evidencias técnicas/auditivas.
- **Pendiente:** escucha humana completa no descrita expresamente, ingesta estricta, procedencia exacta de fuenteEB y origen físico del ruido por confirmar; publicación no solicitada. Aprobación limitada a16v4, no al resto del lote ni aHDR anterior.

## 2026-09-30 — VIDEO22: imagen contextual de compra y nueva exportación

- **Petición:** «Perfecto la imagen creo que no va con el contexto del video, la imagen de recursos que se puso». Se interpreta sobre22, último video revisado/mostrado, y se corrige el recurso de apoyo.
- **Punto de partida:** entregaHLGv1 con díptico mano/tarjeta/pasos; el usuario señala falta de contexto. Diagnóstico: metáfora abstracta que no hace reconocible una compra. Regla IMAGENES_CONTEXTO_REALISMO vigente de revisión16 se aplica; se añade el caso22 sin duplicar ni omitir la regla.
- **Cambios/motivo:** recursoIMG-V22-0002 muestra mano pagando auriculares con tarjeta, ilustración hipotética del «eso» indefinido, sin marca/precio/caso real. Herramienta integradaimage_gen; PNG1060×1484, prompt/archivo fuente/hash guardados; modelo no informado/porconfirmar. Imagen anterior retirada del uso22 pero preservada. HTMLestrecho solo src/alt; generador/ledger/BRIEF/frame/storyboard/manifest/alcanceeditorial sincronizados. Mismo apoyo13,583333–15,583333s; voz/audio/captions/timing conservan hashes.
- **Archivos:** VIDEO22/visuals/video-22_broll_compra_auriculares_v02.{png,prompt.json}; editable/assets/purchase-headphones-v2.png y .media/images/image_001.png; editable/{index.html,build-composition.py,package.json,asset-ledger.json,BRIEF.md,frame.md,STORYBOARD.md,qa/recurso-compra-contextual-v2,qa/post-delivery-hlg-v2*,qa/delivery-v2-boundaries-full}; entrega/AUTORIZACION_CORRECCION_RECURSO_V2.json y dos MP4v2; docs/manifest/entrega/auditorías/métricas; Framework/IMAGENES_CONTEXTO_REALISMO yCHANGELOG.
- **Validación:** pinCLI0.8.98→0.8.99 por probe obligatorio; checkPASS120muestras44/44contrastes,30,581s. Cinco estados13,55/13,7/14,5/15,5/15,65s inspeccionados: pago/producto completos, captions no tapan acción, entrada/salida/regreso correctos. Guard de textoPASS antes de render. Render201,232s,758frames/25,266667s/1080×1920/30fps/HEVCMain10HLG.161frames delnuevoMP4 en seis hojas vistos por modelo, incluidos todos los captions/escenas/apoyo/cola en muestras; extracción3,465s.
- **Audio/resultado:** AAC del nuevo renderer difería en bytes aunque fuente intacta y métricas semejantes. Se conserva el AAC codificado de v1 sobre la nueva imagen con remuxsinrecodificación; nuevo streamvideo igual al capturav2 y streamaudio igual al v1 comprobados por hashes. Archivo vigente `entrega/VIDEO-22-ENTREGA-HLG-v2-audio-conservado.mp4`, SHAc1fcbfa0efe6a362f7d8c1600356603cb1c682b9a0caeee17d4d311937bb185e. QAexactofinaldecode/integridad/metadatos/loudnessPASS3,797s;−16LUFS/LRA5/TP−1dB. QAcaptura3,842s preservado. PerfilHDRcompliant con aviso6,29Mbps vs12referencia; no certificación de publicaciónSDR.
- **Aprendizaje/optimización:** la acción visible debe explicar la frase concreta dentro de dos segundos; una etiqueta temática del catálogo no garantiza contexto. Generar compra específica y probarla con el caption real. No repetir ingesta/ASR ni limpieza de voz; recapturar imagen cambiada, conservar audio y probar el remux exacto.24eventos medidos918,293s acumulados de comandos; no tiempo total/tokens ni ahorro global controlado.
- **Pendiente/límites:** export local continúa autorización22 previa y corrección solicitada, sin atribuir aceptación humana específica a imagen nueva. Aceptación del nuevo recurso y escucha/naturalidad humana porconfirmar. Versionesanteriores y candidato de render conservados; sin publicación ni nueva aprobación ficticia.

## 2026-09-30 — VIDEO22: aprobación de versión con imagen de compra

- **Petición:** «ok aprobado» tras presentación del22 con recurso de compra.
- **Punto de partida:** export local `VIDEO-22-ENTREGA-HLG-v2-audio-conservado.mp4`, SHA c1fcbfa0efe6a362f7d8c1600356603cb1c682b9a0caeee17d4d311937bb185e; QA técnico/modelo visual ya documentado, imagen nueva pendiente de aceptación.
- **Cambios/motivo:** aprobación editorial de versión vigente y recursoIMG-V22-0002 registrada por texto explícito, ligada a hashes. Manifest/ENTREGA/auditorías/evidencia/revisión/CHANGELOG actualizados; fuentes y recibos anteriores preservados.
- **Archivos:** VIDEO22/entrega/APROBACION_USUARIO_VIDEO22_V2.json; manifest.json; ENTREGA.json; AUDITORIA_ENTREGA.json; AUDITORIA_CIERRE.json; QA_REVISION.md; REVISION_USUARIO.md; CHANGELOG.md; editable/qa/recurso-compra-contextual-v2/{evidence.json,aprobacion-usuario/}.
- **Validación:** hash del MP4 coincide con recibo de entrega; nuevo recibo incluye hash de imagen. No cambios de medios, nuevaASR ni render innecesario.
- **Resultado/aprendizaje:**22 y nueva imagen aprobados para esta pieza. Registrar aprobación exacta sin extrapolar a publicación, biblioteca global o evidencia de escucha/visionado completo.
- **Pendiente:** escucha/naturalidad humana porconfirmar; no promoción automática del recurso ni publicación.


## Registro de nuevas entradas — continuación

### 2026-09-30 — Investigación de subtítulos y aprendizaje de18 exportaciones

- **Petición:** investigar posición, lectura sin audio, estilos con palabras grandes y estudios actuales; ampliar del16 a videos ya exportados y fijar criterios de las próximas ediciones con las plantillas existentes.
- **Punto de partida:** familias01–16/21–22 con diferentes captions y reglas de rostro/zona segura;16v4 aprobado editorialmente, archivo intacto. No existe rendimiento local por estilo ni certificación de UI real en esta auditoría.
- **Cambios:** protocolo SUBTITULOS_CONTEXTO_Y_LECTURA, catálogo de cuatro formatos y tres ubicaciones independientes, plantilla de decisión por video, tres reglas de proceso y diez fuentes fechadas. Auditoría de18MP4/54 fotogramas seleccionados y189 cues de editables actuales; comparación visual y notas por video. Integración enREADME, QA, prompts individual/ingesta/derivados y AGENTS de serie. Copias previas del framework conservadas.
- **Motivo:** priorizar comprensión sin sonido, presencia móvil y consistencia sin imponer moda, centro geométrico o coordenada única. Reducir retrabajo decidiendo caja/estilo antes de montar y reutilizando ASR/timing.
- **Archivos afectados:** Framework-Edicion-Social/{SUBTITULOS_CONTEXTO_Y_LECTURA.md,captions/catalog.json,templates/caption-decision.json,rules/registry.json,sources/catalog.json,README.md,QA_PROFESIONAL.md,PROMPT_EDICION_INDIVIDUAL.md,PROMPT_INGESTA_Y_EDICION.md,PROMPT_DERIVADOS_PLATAFORMA.md,CHANGELOG.md,research/subtitulos-2026-09-30/}; Serie-IA-Negocios-10-Videos/AGENTS.md y esta bitácora. No se modifican MP4, editables, audio, recibos de aprobación, banco de plantillas ni perfiles de plataforma.
- **Validación:**18 hojas/54 estados del MP4 inspeccionados visualmente por modelo, no reproducción completa ni escucha. Ocho verificaciones documentalesPASS:JSON, contrato de catálogo/plantilla, campos/enums/IDs/versiones/fechas de reglas, historia previa, fuentes/enlaces, seis integraciones, integridad18exports/54frames y aprobación16 ligada a mismoSHA. Primer intento no inició controles por dependenciajsonschema ausente; segundo usó comprobaciones explícitas con biblioteca disponible, sin afirmar motorJSONSchema general. Evidencia envalidation.json/validation-attempts.json; comparación de seis exports inspeccionada.
- **Resultado:** proceso adoptado para futuras ediciones: frase fiel, una/dos líneas reales, posición estable, énfasis selectivo, lectura móvil/sin audio y preview por destino. Cuatro formatos contextuales;56–72px y15–18CPS son presets internos revisables, >20/25CPS alertas editoriales sin hard fail automático.31/189 cues superan20CPS en fuentes actuales, sin inferir fallos de comprensión.16v4 mantieneSHA df5b836f43fb38c6378dcdb34ee2ed78d2eb2e037133bffc3dc9af817f82804e y aprobación previa.
- **Aprendizaje:**02–10 tienden a franja baja/pequeña;11–15 ofrecen mayor presencia, pero12 muestra tres líneas.16 tiene carril limpio demasiado cercano al área inferior de UI según perfiles internos: riesgo inferido, no captura real ni motivo para revocar aprobación.21–22 requieren revisar altura completa de dos líneas. CPS no descubre wrapping/espacios; las guías de anuncios y disponibilidad de herramientas no prueban tendencia o retención orgánica. InvestigaciónCHI2026, estudioPLOS2024, CHI2024, TikTokjunio2026 y referenciasW3C/Netflix/Meta mantienen su alcance.
- **Pendiente:** previews realesInstagram/Facebook/TikTok con descripción/CTA, pruebas de comprensión y preferencia del público, desempeño por formato y ahorro total: por confirmar. No hay selector automático nuevo ni validación automática de geometría. Facebook carece de perfil propio en catálogo actual; se revisará por destino sin certificarlo porInstagram. No se solicitó reedición retroactiva ni publicación.

### 2026-09-30 — Inicio VIDEO23 y regla permanente de mejora por edición

- **Petición:** editar VIDEO23 aplicando siempre reglas, aprendizajes y mejoras vigentes, sin hacer repetir las instrucciones al usuario.
- **Punto de partida:** VIDEO22 v2 aprobado; VIDEO23 tenía recursos provisionales y rangos compartidos, sin editable.
- **Cambios/motivo:** regla permanente en AGENTS raíz; recibo de documentos/hashes al inicio; scaffold23 CLI0.8.99; reutilización de ingesta21–25, marcador de corrección y runtime; nueva imagen ilustrativa de escucha frente a la metáfora ojo/puente que no se montará.
- **Archivos:** AGENTS.md, Framework/PROMPT_EDICION_INDIVIDUAL.md y CHANGELOG.md; VIDEO23/qa-start y editable/qa/start, editable, visuals/v02 y prompt; VIDEO23/CHANGELOG.md.
- **Validación:** inspección de plantilla T23, nueve estados del proxy y recurso antiguo; lectura de voz seleccionada en transcripción compartida. Verificación de montaje/render y métricas aún pendientes.
- **Resultado:** trabajo23 iniciado y regla guardada; no se infiere aprobación del nuevo video ni escucha humana.
- **Aprendizaje:** registrar decisiones por contexto y evidencias antes de montar evita trasladar literalmente textos/recursos de plantillas. Reutilizar análisis comprobados, sin atribuir ahorro porcentual no medido.
- **Pendiente:** montaje, audio A/B, checks, preview y QA del candidato; aprobación de23, escucha y destinos reales por confirmar.

## Registro de nuevas entradas continuación

### 2026-09-30 — Investigación de música bajo voz y banco de candidatos para IA y negocios

- **Petición:** revisar los videos y el contexto del formato, objetivo y público; investigar si conviene música bajo la voz y descargar opciones libres de uso adecuado para redes cuando aporten.
- **Punto de partida:** serie planificada de30 temas; instantánea de18 renders actuales (01–16 y21–22), piloto/reel de Miguel, wellness, explainers y pruebas Muse. Cama tecnológica propia ya documentada; música declarada como capa independiente en01/02 y ausencia de esa capa en las otras16 piezas de la serie. Esto describe editables, no acredita escucha ni separación de audio del MP4.
- **Cambios:** informe con audiencia y objetivo vinculados a briefs, evidencia científica y límites; inventario de107 archivos/versiones (incluye dos referencias externas); consulta de26 timelines, medidas de26 MP4 y52 fotogramas inspeccionados. Se descargaron tres MP3 completos oficiales de Scott Buckley, dos sin solista, con licencia CC BY4.0, créditos, copias de condiciones y hashes. Se prepararon voz sola y cuatro comparaciones de12s con el mismo fragmento deVIDEO13, además de muestras de20s de las pistas; banco HTML local con reproductores. No se modificaron videos ni preferencias confirmadas.
- **Motivo:** disponer de alternativas concretas sin convertir música en una regla universal ni confundir aprendizaje, retención de feed y ventas. Facilitar evaluación de voz y tono con procedencia verificable.
- **Archivos afectados:** `Framework-Edicion-Social/research/musica-bajo-voz-2026-09-30/` (INFORME, REVISION_EXISTENTES, banco, scripts, evidencia y audiciones); `Framework-Edicion-Social/library/music/candidates/2026-09-30/` (tres MP3, manifest, créditos, README y licencias); README de música; changelog del framework y esta bitácora.
- **Validación:** decode completo/probe de tres descargas; licencia y enlace confrontados con páginas oficiales; hashes y duración/sonoridad registrados. Validación PASS de las muestras y enlaces locales,26 hashes de renders sin cambios y52 fotogramas inspeccionados. Banco observado en captura y carga de reproductor confirmada en UI. El primer intento de captura HDR falló por zscale ausente en FFmpeg8.1.2; se recuperaron solo capturas fallidas con el binario full9.0.2, conservando el fallo y reutilizando metadatos/mediciones. No se afirma escucha ni naturalidad comprobada.
- **Resultado:** música opcional recomendada según mensaje, recursos en `candidate` y comparación local disponible. CC BY4.0 permite uso comercial/adaptación con atribución, enlace y cambios declarados; no se garantiza ausencia de reclamaciones. No hay publicación ni aplicación retroactiva.
- **Aprendizaje:** acompañamiento emocional y comprensión son objetivos distintos; un porcentaje de volumen no equivale a una relación fija voz/música. El promedio de24dB de las muestras es una referencia técnica, no prueba de cada palabra ni cumplimiento WCAG. Las recomendaciones de anuncios y los estudios universitarios no demuestran un efecto en nuestros reels.
- **Pendiente:** escucha y selección estética **por confirmar**; escoger fragmento y nivel por pieza futura y evaluar comprensión/rendimiento comparable. Edad y composición real del público, oferta/embudo, condiciones actuales de Meta fuera de su plataforma y render del video largo siguen por confirmar. No se promocionó ninguna hipótesis a preferencia confirmada.

### 2026-09-30 — VIDEO23 candidatoT23 con reglas vigentes y QA del editable

- **Petición/punto de partida:** nueva edición23 y mantener aprendizajes permanentes; recursos/rangos provisionales sin montaje.
- **Cambios/motivo:** T23calma/serif/aire, cinco rótulos contextuales sin beats visibles;68palabras reales y once captions fieles en carril reservado. Reemplazo interno de ojo/puente por imagen generada de escucha2s. Limpiezaafftdn con perfil de pausa propia, original y tres pruebas preservados;25ms compensados. Wrapper con guard de texto; caché local verifica argumentos/hash/probe para evitar reutilizar artefactos incompatibles.
- **Archivos:** VIDEO23/editable-hyperframes-video-23/{HTML/subcomposiciones,build-composition.py,prepare-media.py,prepare-audio-v2.py,prepare-audio-v3.py,assets,BRIEF.md,frame.md,STORYBOARD.md,transcript.json,captions.json,captions.srt,cut-plan.json,asset/dependency-locks,qa,review}, manifest.json,caption-decision.json,AUDITORIA_CANDIDATO.json,QA_REVISION.md,REVISION_USUARIO.md,visuals/v02y prompt,CHANGELOG.md; AGENTS raíz/PROMPT y frameworkchangelog.
- **Validación:** tres wraps y leading detectados/corregidos; snapshot de once cues a360px, recurso y fuentes inspeccionados por modelo. Check70tiempos/300muestras movimiento/14de14contrastes PASS,0errores/avisos; guard visiblePASS. ReproducciónUI silenciada inicio→fin observada, sin afirmar escucha humana ni visualización continua de todos los cuadros.7.39–8dB de ruido medido en tres pausas; correlaciones vocales.9987–.9997 y niveles prácticamente iguales no prueban naturalidad.
- **Resultado:** candidato local en Studio3023 para revisión; sin render final, publicación ni aprobación23 inferida.
- **Aprendizaje:** perfilar ruido propio funcionó mejor técnicamente que preset heredado (.02/.31dB vs7.39–8dB en muestras; no prueba perceptual). Los saltos escritos no garantizan dos líneas: comprobar wraps reales antes del render. Guardar inicio/decisiones reduce omisiones; repetir análisis del lote no aporta.
- **Tiempo/optimización:** seis comandos medidos198.606s acumulados,168.933s unión; excluyen generación/decisiones/preparación, no tiempo total ni ahorro porcentual. Se reutilizaron ingesta/timing/rangos; renderMP4 exacto y QA de frontera quedan para aprobación.
- **Pendiente:** aprobación23; render/QA exactos; escucha naturalidad/phonemas y destinos realespor confirmar. Versiones y ensayos preservados.

- **Complemento VIDEO23:** preflight estricto de ediciónFAIL conservado (TAKE_MAP_UNREVIEWED, TAKE_MAP_UNRESOLVED, EDITING_PROXY_MISSING, SOURCE_RANGE_MISSING). El candidato usa excepción autorizada y hashes del recibo provisional; no se afirma gate estricto aprobado. ScreenshotStudio guardado y plan de render sin ejecutar; aprobación23 solicitada sobre esa previa.

### 2026-09-30 — Mejora de limpieza y prevención de caché obsoleta desde VIDEO23

- **Petición/punto de partida:** mejorar tiempos/calidad y aplicar/documentar aprendizajes; preset genérico apenas reducía fondo y el cache helper inicial solo reconocía fase/archivo.
- **Cambios/motivo:** documentar perfil de pausa propia como candidato, sin imponerlo como preset universal. Helpers23 ahora ligan reutilización a hashes de archivos de entrada, argumentos, salida y probe; evita reutilizar cortes antiguos tras cambiar audio en el mismo path.
- **Archivos:** Framework/AUDIO_LIMPIEZA_VOZ.md,CHANGELOG.md; VIDEO23/prepare-media.py,prepare-audio-v2.py,prepare-audio-v3.py,qa/cache-smoke/result.json,CHANGELOG.md y bitácora.
- **Validación:** smoke real FFmpeg: entrada idéntica reutilizada; mismos argumentos/ruta con bytes de entrada distintos fuerzan procesamiento y hash de salida nuevo. No se repitió la preparación del maestro ni se modificó el montaje comprobado.
- **Resultado/aprendizaje:** optimización verificable de caché local y técnica de perfil contextual documentadas; ahorro neto y fidelidad auditiva por confirmar.
- **Pendiente:** aprobación23 y QA del render exacto; no se cambia historia de21/22 ni se afirma escuchar.

### 2026-09-30 — Rechazo de las audiciones y diagnóstico de sensación plana

- **Petición:** explicar por qué las muestras resultan muy calmadas o distraen; el usuario confirmó después que «También se siente plana sin música».
- **Punto de partida:** banco de 12 s de VIDEO-13 con voz idéntica y cuatro fondos, tres recursos licenciados candidatos y recomendación pendiente de escucha.
- **Cambios:** registrada la respuesta real y el rechazo de la tanda; banco, informe y manifiesto indican el estado actualizado. Se conserva el estado inicial en `antes-feedback-usuario/`. Medición parcial de cuatro bandas y comparación de nivel con rangos exactos del mismo original; validador conserva feedback futuro.
- **Motivo:** evitar recomendar muestras rechazadas y distinguir ajuste musical, contraste de interpretación/montaje y posible tratamiento de nivel sin inventar una causa de frecuencias.
- **Archivos afectados:** `Framework-Edicion-Social/research/musica-bajo-voz-2026-09-30/` —informe, banco, evidencia y scripts—, README/manifest del banco de candidatos y changelog del framework.
- **Validación:** voz por encima del fondo en promedio de las cuatro bandas revisadas; diferencia de ganancia origen/procesada variable en 101 ventanas. Son mediciones parciales, no escucha ni diagnóstico de EQ/compresión. Se comprobarán enlaces y preservación de audios de la tanda tras la actualización documental; validación técnica inicial PASS se conserva.
- **Resultado:** primera tanda descartada como propuesta para el fragmento. No se modificó ningún video, fuente de voz o archivo musical.
- **Aprendizaje:** si la voz sola también se percibe plana, buscar otra cama no basta para explicar la sensación. Un fondo bajo puede no funcionar emocionalmente; las métricas no invalidan el feedback humano.
- **Pendiente:** comparación dentro del video, origen/procesada a nivel percibido equivalente, énfasis/pausas/montaje y después otra dirección musical. Causa exacta y eficacia en audiencia **por confirmar**.


### 2026-09-30 — VIDEO23: congruencia del apoyo y mínimo dos SFX distintos

- **Petición:** usuario percibió un solo efecto; pide mínimo dos sonidos y apoyo en caja del presentador o vertical completa según lo que comunique mejor.
- **Punto de partida:** V1 tenía tres eventos del mismo entry y foto portrait462×820 dentro del panel920×820; aprobaciónV1 pendiente.
- **Cambios/motivo:** regenerar la misma escena de escucha en46:41, montarla enx80/y330/920×820/radio38, conservar2s y retorno. Tres eventos con dos sonidos aprobados distintos: ENTRY0002 y MOTION0003 elegible por cooldown. Calibrar-11/-10dB bajo voz contemporánea. Guardar decisión entre misma caja y vertical completa, sin imponer una opción global. Guardar mínimo dos identidades distintas para20–30s en reglas y QA.
- **Archivos:** VIDEO23/visuals/v03 y prompt, editable/{build-composition.py,index.html,assets/escucha-atenta-v3.png,deslizamiento-calido.wav,frame/brief/storyboard,asset-ledger/lock,dependency-map,qa/revision-image-sfx-v2,review/review-packet.json}; manifest,caption-decision,AUDITORIA_CANDIDATO,QA_REVISION,REVISION_USUARIO,CHANGELOG. SerieAGENTS, Framework/{IMAGENES_CONTEXTO_REALISMO,AUDIO_LIMPIEZA_VOZ,QA_PROFESIONAL,CHANGELOG}, bitácora.
- **Validación:** check70tiempos/300motion/14contrastes PASS0errores/avisos; guard textoPASS; seis snapshots entrada/centro/salida/regreso y screenshotStudio inspeccionados. Rostro/manos/teléfono y dos líneas visibles. Mix diagnóstico-15.95LUFS/-1.48dBTP, dos hashes de SFX distintos. No afirmación de escucha humana del nuevo mix.
- **Resultado:** V2 concreta para revisión enStudio3023; solicitud previaV1 sustituida, sin aprobación ni render final inferidos.
- **Aprendizaje/optimización:** contar identidades y eventos por separado; generar según geometría destino, no por defecto9:16. Reutilizar fuente/voz/captions con hashes intactos y QA afectado; no repetir ASR/denoise. Check71.242s y snapshots10.335s medidos; sin ahorro porcentual afirmado.
- **Pendiente:** aceptaciónV2, render y QA del MP4 exacto; percepción de efectos/naturalidad y plataformas por confirmar. Candidatos e historia anteriores preservados.


### 2026-09-30 — VIDEO23: audibilidad real, prosodia y hook con SFX obligatorio

- **Petición:** usuario no percibe segundo efecto aunque imagen perfecta; pide comparar aumento de volumen o sustitución, análisis técnico de voz/intensidad/entonación/pausas/ritmo/interpretación, y hook inicial siempre con efecto comprobado en QA.
- **Punto de partida:** V2 mezcla técnicamente medida pero segundo deslizamiento cálido no percibido por el usuario. No aprobación final de audio/render.
- **Cambios/motivo:** comparar mismo deslizamiento+4dB (conservado), elegir pop tonal contrastado en pausa17.433s antes de conclusión; conservar entrada0.1s y apoyo12.633s. Congelar ganancias en WAV derivados/data-volume1 sin afirmar bug de preview. Nueva dirección/perfil relativo por cinco tramos: RMS/pitch estimado/rango/pausas/velocidad por palabras reales, interpretación editorial ligada al texto. Guard obligatorio verifica presencia de hook, dos identidades fuente —no número de derivados—, bindings de timing/volumen/hashes y mix.
- **Archivos:** Framework/AUDIO_DIRECCION_Y_PROSODIA.md,scripts/{perfilar_voz.py,revisar_presencia_sfx.py},QA/PROMPT/AUDIO_LIMPIEZA/CHANGELOG,AGENTS raíz/serie; VIDEO23/{build-composition.py,media-runtime.mjs,index,assets/sfx-*-mix-v3.wav,pop-suave-original.wav,asset-ledger/lock,dependency-map,qa/audio-direction.json,qa/revision-audibility-v3,review-packet,manifest,AUDITORIA,QA_REVISION,REVISION_USUARIO,CHANGELOG}.
- **Validación:** checkV3 PASS70tiempos/300motion/14contrastes0errores/avisos; guard presencia sin errores/avisos; wrapper preflight ejecutado sin captura. Pruebas negativas detectan hook ausente y hash obsoleto. Segundoacento pico-16.01dBFS, fondo voz de ventana-45.95dBFS; mixV3-15.95LUFS/-1.48dBTP. Alternativa+4dB-15.97LUFS/-1.48dBTP. Voz/picture/captions/imagen preservados. Perfil tarda fracción de segundo en ejecución local; no ahorro neto probado ni repetición de ASR/denoise.
- **Resultado:** candidatoV3 para escucha; muestra4.4s de voz/acento. Reglas permanentes con gate hook antes del render. Imagen aceptada por comentario «esta perfecto...»; no inferir aprobación de audio que explícitamente no se percibía.
- **Aprendizaje:** identidad distinta y RMS global no garantizan percepción; revisar envolvente, ubicación, masking y voz del instante. Contrastar mismo sonido más alto con carácter distinto. Mediciones no leen emociones ni prueban audibilidad en teléfono.
- **Pendiente:** escucha humana del acento nuevo, aceptación audioV3/render y QA del MP4 exacto; destinos reales por confirmar. Versiones anteriores preservadas.

### 2026-09-30 — Análisis de voz, interpretación y dirección sonora

- **Petición:** el usuario autorizó analizar contraste, énfasis, entonación, pausas, cambios de ritmo, interpretación y proyección para decidir música y efectos.
- **Punto de partida:** tanda musical rechazada y voz sola de VIDEO-13 percibida plana; diagnóstico técnico todavía provisional.
- **Cambios:** medidas descriptivas de 18 voces declaradas —01–16,21–22 de la instantánea— y mapas de 41 frases en 11/13/14/21. Informe, ficha reutilizable de dimensiones, propuesta sonora por intención y visor local con cinco audiciones a volumen comparable.
- **Motivo:** escoger sonido desde el gesto vocal y el mensaje, distinguir interpretación de montaje/procesado y convertir la sensación plana en hipótesis comprobables.
- **Archivos afectados:** `Framework-Edicion-Social/research/musica-bajo-voz-2026-09-30/ANALISIS_VOZ.md`, `voz.html`, informe/banco, scripts de análisis/validación, `evidencia/prosodia/` y audiciones finales48k/24bits. Antecedentes16k y estado previo conservados; ninguna modificación de videos o medios fuente.
- **Validación:** PASS de 18 fuentes por hash, 41 intervalos, cinco WAV completos y enlaces. Audiciones finales −22,00/−21,99 LUFS y picos−4,09 a−4,96 dBTP; ganancia constante. Cuatro piezas y comparación origen/procesada cargaron sin error en UI; curvas/layout inspeccionados. El banco previo revalidó PASS y los26 hashes de renders permanecen iguales.
- **Resultado:** VIDEO-13 presenta8,73 semitonos de variación central y14,64 dB de energía, con siete pausas internas de0,35–0,44 s. Esa regularidad es una hipótesis para cadencia predecible. El origen con los mismos cortes conserva8,73 semitonos y14,45 dB; no evidencia una pérdida material de contraste por procesado. Propuesta sonora13: apertura con presencia, avance ligero, remate con espacio y pregunta con aire.
- **Aprendizaje:** ganancia variable en ventanas sin alinear no demuestra compresión; al compensar21,38 ms, las diferencias de previews quedan mayormente dentro de±0,42 dB. Medidas, intención del texto y percepción deben relacionarse por frase. El volumen no representa toda la energía expresiva.
- **Pendiente:** escucha en contexto, naturalidad, acento exacto de palabras y proyección percibida. Autocorrelación raw de Praat embebido6.1.38 con sensibilidad documentada; no etiquetar emociones ni inferir rasgos personales. No hay nueva música aplicada, aprobación auditiva ni rendimiento de audiencia demostrado.


### 2026-09-30 — Aprobación y render final de VIDEO23

- **Petición/punto de partida:** usuario «Perfecto aprobado.» sobre V3 con imagen misma caja y mezcla revisada; preview y QA previos listos, sin entregaMP4.
- **Cambio/motivo:** aprobación ligada a hash de index/dependency/audit de la versión presentada. Iniciar entregaHLG30fps/unworker,740frames, por wrapper con guard texto y hook/SFX/mix. Claimheavy propio23 dentro de máximo2; no alterar claim17.
- **Archivos:** VIDEO23/entrega/APROBACION_USUARIO_VIDEO23_V3.json,manifest,qa/render-plan.json,process-events/render;production-board,CHANGELOG,bitácora.
- **Validación/resultado:** vínculos de todas las dependencias comprobados antes de iniciar. Render en curso; aún no hay resultado/exportQA que certificar. Aprobación humana no equivale a escucha realizada por el modelo.
- **Aprendizaje/pendiente:** conservar exacta mezcla aprobada y distinguir etapa de proceso de entrega terminada; falta finalización, QA delMP4, hash final y liberaciónclaim.


### 2026-09-30 — VIDEO23 entrega aprobada y QA del MP4 exacto

- **Petición/punto de partida:** «Perfecto aprobado.»; V3 de imagen/SFX aprobada y render pendiente.
- **Cambios/motivo:** entregar24.667s/740frames/1080×1920/30fpsHEVCMain10HLGBT2020 conAACstereo48k, conservando diseño/captions/imagen/voz/mezcla exactos del index aprobado. Vincular recibo, export y evidencia; liberarclaim23 sin tocar17.
- **Archivos:** VIDEO23/entrega/{MP4,APROBACION_USUARIO_VIDEO23_V3.json,ENTREGA_VIDEO23.json,sha256},manifest,AUDITORIA,QA_REVISION,REVISION_USUARIO,CHANGELOG;editable/{qa/post-render-final-v1,boundaries-final-v1,final-audio,render-plan,review-packet};Framework/scripts/revisar_presencia_sfx.py,AUDIO_DIRECCION_Y_PROSODIA.md,CHANGELOG;bitácora/production-board.
- **Validación:** renderPASS172.627s; postQA completoPASS5.067s y fronteras3.329s:99fotogramas reales/4contactos inspeccionados por modelo, todos los cambios/cues/apoyo, sin afirmar vista continua de740. AACfinal-15.9LUFS/-1.3dBTP; correlación mix referencia0.999400 y por eventos0.999393/0.999785/0.999586. Guard texto/hook/identidades/hashes/mix pasó antes de captura. Index/dependency idénticos al recibo de aprobación. Hash final755a66620120b9ff7d6007494a870c5c141dc09d91f93405d3e52863c8cbe3ae.
- **Hallazgo/mejoraQA:** diagnóstico FFmpeg ingenuo negociaba mono→stereo con atenuación distinta a duplicaciónunity del motor; el acento tonal tampoco alineaba por redondeo de inicio a milisegundo (0.333ms). Se conservó comparación inicial, corrigió solo helper/referencia para representar canales/timing del motor0.8.99 y verificó acuerdo con AACreal. Fuente/HTML/MP4 aprobados no se alteraron ni se rerenderizó. El informe diferencia dominio de nivel de fuente mono de suma estéreo plegada; no confundir correlación con escucha.
- **Resultado:** VIDEO23 entregado; aprobación humana del preview/mezcla recibida, QA exacto técnico/visual documentado; modelo no afirma escucha humana propia.
- **Aprendizaje:** igualar dominio de canales y timing al comparar audio, no subir SFX porque un diagnóstico usa otra ley de mezcla. Mantener controles obligatorios/voz contextual y revisar export real además del editable. Reutilizada ingesta/ASR/voz, sin repetir maestro ni benchmark de ahorro ficticio.
- **Pendiente:** no trabajo obligatorio para esta entrega local; previews/publicación en plataformas y análisis de rendimiento no solicitados ni certificados. Versiones, muestras e historia conservadas.

Cierre de registro23: revisión HTML offline creada en editable/review/review.html; recursoIMG-V23-0003 y ledger marcan aceptación en este montaje mediante recibo, sin promoción global. Auditoría final: hash del index y todas las dependencias idénticos a aprobación, QA vinculado al hashMP4, reglas persistentes presentes y claim23 liberado.


### 2026-09-30 — VIDEO17: edición inicial y revisión de ruido

- **Petición:** editar17 con documentación, plantillas, director/QA y aprendizajes de16; usuario después reporta ruido similar a ventilador/interferencia y solicita investigar repositorios/Adobe para aislar voz.
- **Punto de partida:** master16–20 ya ingerido y toma17 provisional;16v4 aprobado se conserva intacto. Primera salida17v1 con limpieza perfiladanr8, sin aprobación humana. Registro consolidado tras trabajo; recibos originales conservan timestamps reales.
- **Cambios:** montaje27.733s/832frames desde cinco rangos del original; títulos semánticos,17captions de frases completas con énfasis y geometría108/1160/740/188; foto contextual de escucha10.1..12.1s generada e inspeccionada. CuatroSFX/dos identidades, sin música. Tras reporte, comparar afftdn18 y DeepFilterNet3 local; conservarv1, generarv2 yMP4 alternativo, cambiar solo asset de voz del editable y bindings.
- **Motivo:** pertinencia del apoyo, lectura sin audio, protección de rostro/gestos y reducir fondo que el usuario todavía percibe. Elegir provisionalmente afftdn18 por mayor reducción en las cinco pausas y menor cambio de señal vocal; preferencia perceptual por confirmar.
- **Archivos afectados:** VIDEO17/{editable-hyperframes-video-17,visuals,manifest,creative-blueprint,caption/style/recipe-decisions,render-manifest-v1/v2,qa-scorecard-v1/v2,MP4v1/v2/pruebaDF3,qa,CHANGELOG}; Framework/{AUDIO_LIMPIEZA_VOZ,research/limpieza-voz-2026-09-30,CHANGELOG}; bitácora y production-board.
- **Validación:** v1check60muestras/0errores/avisos,160fotogramas delMP4 inspeccionados en cues/cortes/imagen y tres pares de color; smoke5.6s/8estados. Checkv2PASS0errores/avisos, guardtexto y equivalentehook/SFX/hashes/mix. Dos voces nuevasASR mantienen81palabras. v2/pruebaDF3 decodificación yQApostexportPASS,832paquetes de imagen/PTS/DTS/duración idénticos av1, audio0lag en cuatro ventanas. v2-15.32LUFS/-1.69dBTP;DF3-15.43LUFS/-1.65dBTP. No escucha humana/QA de destinos/aprobación17 inferidos.
- **Resultado:** v2`e96a7e5f9147762ef5e8063e94d72bb0c6dfd860296021c4f654ad7d5a09a8d9`; alternativaDF3`075a38ad448d18e4ccd7de8d2d80fadca5d01ee2e9f63788a10c8473ce210c29`. v1`e4248d1f29594c52b88b99246909c3c11a5ff23090f0ac891dbf5127a9aeb58e` permanece. Fondo de cinco colas normalizadas:v2−11.16..−12.72dB frente av1;DF3−7.54..−10.24dB; no certifica ruido durante voz ni timbre.
- **Aprendizaje:** mayor complejidad/modelo no asegura mejor resultado para cada grabación. Comparar bajo mismo contexto/volumen y preservar A/B; motor local nativo evita dependenciasTorch y permite modelo/hash congelado. Remuxv2.382s/prueba.390s frente a render visual previo38.088s, sin atribuir ahorro total de edición. Master/ingesta y picture no reprocesados. Extra raízsmokeHTML bloqueaba strict render; archivar como.source resolvió. JSONcheck contiene prefijo: parsear objeto sin concatenarstderr. Memoria de variedad compartida incompatible se conservó ydocumentó, sin fingir validación.
- **Pendiente:** escucha de fondo/naturalidad/fonemas/SFX, selección humana de toma17 y aprobación ligada alMP4 exacto; vistas realesIG/FB/TikTok. Ladridos/tráfico/bocinas no probados aquí;ClearerVoice/Resemble/Adobe investigados pero no ejecutados. Separar cachemedia de metadatos y resolver esquema de memoria de variedad, sin promover nuevos presets/estilos/recursos como aprobados.


### 2026-09-30 — VIDEO17: validación del esquema de QA tras revisión de audio

- **Petición/punto de partida:** entregar edición17 y comparación de limpieza; QA técnica deMP4PASS, pero preflight detectó evidencia conkindfile no admitida y gates automáticos sin vínculoSHA delMP4.
- **Cambios/motivo:** conservar scorecard anterior de esta revisión, normalizarkindartifact y añadir registroscommand_output ligados al hash exacto y a las salidas existentes. No cambiar los resultados/estados humanos ni forzar autorización.
- **Archivos:** VIDEO17/qa-scorecard-v2.json,qa-scorecard.json,qa/noise-revision-v2/{qa-scorecard-v2-before-schema-correction,scorecard-schema-verification,preflight-render-strict-final,preflight-render-strict-after-schema}.json; CHANGELOG y bitácora.
- **Validación/resultado:** analyze_scorecard valid=true/errors=[],delivery_ready=false. Preflight conserva únicamente AUDIO_STREAM_UNLOCKED,VIDEO_TAKE_MISSING yQA_DELIVERY_BLOCKED por selección/escucha/signoff humanos pendientes. Todos los hashes activos de assets verificados;16v4 conserva SHA aprobado. MP4v2/pruebaDF3 no cambian.
- **Aprendizaje:** validar esquema además del contenido del informe; distinguir hash de un reporte del hash delrender al ligar evidencia automática.
- **Pendiente:** escucha/naturalidad/aprobación17 y destinos reales; material local para revisión disponible bajo excepción autorizada.


### 2026-09-30 — Inicio VIDEO24 con memoria de23 y plantilla ContrasteXL

- **Petición:** «Vamos con el video24». **Punto de partida:** rangos/proxy y recursos provisionales del lote21–25; sin editable24 ni aprobación24.
- **Cambios/motivo:** claim24 y recibo de inicio con hashes; preflight estricto preservado y excepción de montaje provisional registrada. Preparación individual reutiliza transcripción final/take-map, sin repetir maestro. T24aprobada como plantilla; textos visibles serán semánticos según voz.
- **Archivos:** VIDEO24/editable-hyperframes-video-24/qa/start/, production-board.json, VIDEO24/CHANGELOG.md y bitácora.
- **Validación/resultado:** registroT24 inspeccionado y propuesta visual revisada; audio y naturalidad humana por confirmar.
- **Aprendizaje:** la aprobación de plantilla y marcador grabado no aprueba montaje nuevo. Revisar perfiles de ruido/voz antes de escoger efectos; paridadmono aprendida en23.
- **Pendiente:** montaje, tres pasadasQA, preview y aprobación24, render exacto y QA posterior.

### 2026-09-30 — Aplicación práctica de prosodia: efectos y música por bloques en VIDEO-13

- **Petición:** tras ver el HTML de voz, el usuario pregunta para qué sirve el análisis y qué permite hacer con fondos, efectos y edición.
- **Punto de partida:** primera tanda musical rechazada y voz sola percibida plana; perfil de18 voces, mapas de41 frases y propuesta editorial de13 disponibles, sin nueva decisión sonora aprobada.
- **Cambios:** tres comparaciones aisladas de19,50 s dentro del mismo video: Avoz de referencia, Bvoz con pop/tick/acento, Cmisma voz/efectos más pulso de2,09 a13,39 s. Música fuera antes de«cien prompts», pregunta final despejada. Descarga oficial deNeon/No MelodyCC BY4.0 con crédito, página y hashes. Nuevo reproductor por bloques y guía de aplicación; visor anterior enlaza la prueba y conserva snapshot. Servidor local8868 con rangos HTTP para buscar/comparar, junto al8866 existente.
- **Motivo:** transformar mediciones e interpretación del argumento en función/momento/carácter/nivel de sonido; aislar aporte de acentos A→B y cama B→C, sin asumir que una pista nueva resolverá la sensación plana.
- **Archivos afectados:** Framework/research/musica-bajo-voz-2026-09-30/{practica.html,APLICACION_PRACTICA.md,voz.html,antes-aplicacion-practica, scripts/preparar_practica.py,validar_practica.py,servir_practica.py,audiciones/practica-v1,evidencia/practica-v1}; library/music/candidates/2026-09-30-prueba-ritmica/{MP3,manifest,README,CREDITOS,licencias}; changelog del framework y esta bitácora.
- **Validación:** tres MP4 completos, imagen por paquetes/hash y585fotogramas/HDR/cadencia idénticos al13 original; voz común PCM invariante salvo cuantización24bits. AAC/PCMcorrelación>0,99999, SFX por diferencia>0,99955 y música0,99875. Salidas−16,99/−16,99/−16,98LUFS y−2,14/−2,14/−2,22dBTP. Hook con evento y tres identidades/fuentes por hash. UI cargó19,5s sinerror, salto alremate y comparación pausadaA→B6,99s conservada; layout inspeccionado. Range206/1024bytes verificado. Perfil previo revalida18 fuentes y5audiciones; banco previo revalida26renders.
- **Resultado:** prueba concreta para escuchar; VIDEO-13 original y editables intactos, sin sustituir entregas ni publicar. Nueva candidata musical descargada; aceptación estética y escucha humana **por confirmar**.
- **Aprendizaje:** el perfil orienta jerarquía y descansos, no una frecuencia musical ideal. Ganancia común evita cambiar la voz entre pruebas; duplicaciónmonoL/R explícita evita diagnóstico por conversión implícita. Retirar cama puede crear contraste; su eficacia no se demuestra por picos/RMS. Si ambas propuestas siguen planas, probar ritmo de pausas/selección de toma/interpretación antes de atribuirlo solo al fondo.
- **Pendiente:** feedbackB/C y escucha completa en dispositivo habitual/teléfono; encaje del carácterretro, claridad y efecto en atención. Solo si se adopta, trasladar al grafo del editable y verificar su export exacto. No declarar aprobación de recursos ni efectos en audiencia.



### 2026-09-30 — VIDEO24: candidato contextual, aprobación y exportación iniciada

- **Petición:** continuarVIDEO24 y «Aprobado»; mantener documentados aprendizajes para siguientes ediciones. **Punto de partida:** ingesta compartida21–25, toma corregidaW36, diseñoT24 ContrasteXL autorizado; sin entrega24.
- **Cambios/motivo:** editable23.3667s desde originalHLG, descartar repetición viejaW34/W35 por marcador y conservar correcciónW36; perfil propio/afftdn8 y compensación25ms; imagenfotográfica contextual generada en caja920×780; titulares de contenido;15captions64px con máximo2líneas en muestras. Tres eventos/dos SFXfuente, incluidohook, ganancias congeladas y guardobligatorio. ReparaciónASRsolo9.3s para «piensa en tu marca»/«si te dice», sin recorrer maestro.
- **Archivos:** VIDEO24/editable-hyperframes-video-24/{scripts,index,compositions,assets,transcript,captions,cut-plan,dependency-map,qa}; creative-blueprint,caption-decision,style-decision,creative-recipe-abstention,visualsV02,AUDITORIA_CANDIDATO,QA_REVISION,entrega/APROBACION_USUARIO_VIDEO24_V1.json,CHANGELOG y bitácora.
- **Validación:** checkV2PASS84tiempos/0errores/avisos; contactos15cues inspeccionados, perfil vocal y gates texto/hook/identidades/bindings PASS. Mapa de animación revisado; colisiones de timelines colocadas contrastadas con estados activos reales; holds de lectura intencionales. ReproducciónStudio inicio/fin observados, sin afirmar vista de todos los frames ni escucha del modelo.
- **Resultado:** aprobación literal «Aprobado» registrada para candidatoactual; exportHDR30fpsdelivery iniciada. IngestaestrictaFAIL y excepción de avance se conservan; receta automática se abstiene por schema de ledgerglobal, sin modificarlo ni falsearPASS.
- **Aprendizaje:** captions se verifican por envoltura real y frases completas; reutilizar ASR/ingesta/voz y limitar reparación al tramo ambiguo. Preparación multimedia8.752s de comandos medidos; ASRtargetedmotor5.26651s para9.3s de entrada, sin atribuir ahorro neto total. Reglas previas permanentes comprobadas enAGENTS, guías y wrapper24.
- **Pendiente:** QA del MP4 exacto y entrega; escucha/naturalidad por confirmar, aprobación no se inventa como escucha. Destinos sociales sin certificar/publicar.

### 2026-09-30 — VIDEO17: nuevas pruebas de supresión y comparación a volumen igual

- **Petición:** el usuario aún percibe ruido mínimo y solicita probar de una vez las otras opciones para afinar cuál usar.
- **Punto de partida:** editable17 yMP4v2 conafftdn18; pruebaDeepFilterNet3 anterior; cinco contextos48k y toma/stream provisionales;16v4 aprobado. No repetir ingesta/transcripción del master.
- **Cambios:** entorno aisladoPython3.11 y fuentes/modelos oficiales congelados; ejecutarClearerVoiceMossFormer2_48K/FRCRN16K,Resemble denoiser44,1K yRNNoise48K sobre los mismos cinco contextos; compensarRN960samples/20ms y ensamblar cortes exactos. SieteA/B−22LUFS por ganancia constante, dos diferencias de señal, comparador local con posición compartida y dosMP4 de audiciónRN/Resemble; editable/v2 sin sustitución.
- **Motivo:** comparar ruido residual a niveles equivalentes y preparar elección de fidelidad/timbre, conservando versiones y evitando un ganador por marca o instalación disponible.
- **Archivos afectados:** VIDEO17/qa/noise-benchmark-v3/{env,fuentes,modelos,scripts,logs,recibos,review},VIDEO-17-PRUEBA-{RNNOISE,RESEMBLE}-v1.mp4,CHANGELOG; Framework/research/limpieza-voz-2026-09-30/COMPARACION_LOCAL_V17_V3.md,INFORME.md,AUDIO_LIMPIEZA_VOZ.md,CHANGELOG ybitácora. RecibosSHA/proveniencia/parámetros/tiempos conservados.
- **Validación:** cuatroASR locales recuperan81/81 palabras, sin repetir master; A/B27,733333s−22±0,01LUFS. RN reduce28,10–33,73dB frente av2 en cinco colas150ms; Resemble−24,32..+4,14dB, resultados mixtos; noSNR durante voz. DosMP4−15,23LUFS/−1,77 y−1,79dBTP,decode completoPASS,AAC0lag en cuatro ventanas,832paquetesvideo/timestamps idénticos; guardtexto/SFX equivalentes dentro de remux, niveles/masking registrados. UI siete archivos/duración, cambio19,60s y durante reproducción, medios de mezcla/diferencias yHTTP206 verificados; captura guardada. v2/16v4SHA intactos.
- **Resultado:** comparación concreta terminada yRN propuesto primero por medidas de pausas; ninguna naturalidad/escucha/aprobación inferida. Adobe sin cuenta conectada, no probado ni subido audio. Selección final por confirmar; gates humanos originales no se convierten enPASS.
- **Aprendizaje:** más reducción en pausas no garantiza mejor voz;16k remuestreados no son ancho de banda48k. Medir referencia monoL/R real antes de ajustar ganancia; evitar sesgo de loudness. Reutilizar ingesta/contextos/modelos y video codificado; ASRnuevo solo cuando cambia señal,QAaudio/export exacto sigue obligatorio.
- **Pendiente:** escucha humana de fondo durante voz, consonantes/timbre/respiraciones y señales retiradas; decisión entre candidatos; Adobe si se dispone sesión; pruebas etiquetadas de perros/carros/bocinas. No cambiar regla universal por un solo audio.


### 2026-09-30 — VIDEO24 entrega aprobada y QA exacto; control AAC documentado

- **Petición/punto de partida:** «Aprobado» y mantener reglas para próximas ediciones; candidato24 autorizado, render pendiente.
- **Cambios/motivo:** exportaciónHLGdelivery30fps única,701frames/23.3667s; recibo ligado al index/dependencies aprobados; entregarMP4/SRT/sha y evidencia exacta.
- **Archivos:** VIDEO24/entrega,manifest,ASSET_USAGE_FINAL,METRICAS_PRODUCCION,caption-decision,QA_REVISION,CHANGELOG;editable/qa/{render-final-v1,post-render-final-v1,boundaries-final-v1,final-audio-v1},asset-ledger;Framework/AUDIO_DIRECCION_Y_PROSODIA.md yCHANGELOG;bitácora/tablero.
- **Validación:** renderexit0/173.592s; decode/probe/loudnessPASS,postQA6.886s;145frames/cincohojas inspeccionadas,fronteras5.083s. Max2líneas y rostro/gesto de memoria visibles; apoyo2s y regreso correctos. Index/dependencies intactos. AACreal−17.0LUFS/−1.2dBTP. SHAb60f950c5807d199d2f6ad64f39acf297caac2407ff600fca2f975904e353b75.
- **Hallazgo/aprendizaje:** primerdiagnósticoPCM versusAAC difiere≈−0.97dB y falla residual de efecto sobrevoz; se conserva. Código0.8.99 cuenta paquetesAACincluida priming, recorta duración/recodifica y aplica controltruepeak si AAC>−1dBFS. Reproducción exactaPCM16→AAC→trim→−0.900dB→AAC confirma igualdad muestra por muestra del MP4, total y tres efectos; no se modificó ni rerenderizó. Nivel−0.900dB es particular, no preset. Guía permanente exige comprobar proceso completo antes de subir/reemplazarSFX.
- **Resultado:** entrega local24 aprobada y QA exacto técnico/visual terminado. Ingesta/ASR compartidos reutilizados; reparaciónsolo9.3s. Uso final registrado para rotación; conservar globalledger incompatible sin inventarPASS.
- **Pendiente/límites:** no trabajo obligatorio para entrega local; escucha/naturalidad por confirmar, modelo no escuchó. No publicación, certificación social ni ahorro neto/tokens porfase afirmados.

### 2026-09-30 — Limpieza de voz a solicitud y skill explícita

- **Petición:** conservar lo ya realizado, guardar investigación/guías/pruebas/recetas en una skill y sugerir tratamientos adicionales al detectar defectos; usar esta revisión/limpieza solo cuando el usuario la pida, sin aplicarla a todas las ediciones.
- **Punto de partida:** sieteA/B y dosMP4 de audición17 conservados; editablev2 sin adoptarRN. Documentos/prompts/perfil imponían diagnóstico/bypass/supresión de ruido al conjunto de videos. Investigación de eses/de-esser y otros defectos era explicación sin aplicación.
- **Cambios:** skill personal `revisar-limpiar-voz` con invocación implícita desactivada; instrucciones de activación, diagnóstico/sugerencias, recetas y referencias a fuentes/modelos/experimentos/QA originales, sin duplicar medios grandes. HelperRN reutilizable con libreríaSHA, salida nueva, padding/delay explícito y recibo. Actualizar alcance enAGENTS raíz/serie, procedimiento, prompts,QA/estándar, mejora y dos preferencias confirmadas. Guardar investigación/índice y versiones previas.
- **Motivo:** respetar nueva decisión explícita; edición ordinaria no debe iniciar instalaciones/denoise/comparaciones por rutina. Tratamientos extra como de-esser/de-click/de-reverb se sugieren según hallazgo, sin aplicar una cadena general.
- **Archivos afectados:** `/Users/iomijhondavid/.codex/skills/revisar-limpiar-voz/{SKILL.md,agents/openai.yaml,references/*.md,scripts/rnnoise_wav.py}`; Framework/{AUDIO_LIMPIEZA_VOZ,PROMPT_INGESTA_Y_EDICION,PROMPT_EDICION_INDIVIDUAL,QA_PROFESIONAL,MEJORA_CONTINUA}.md,profiles/creative_preferences.json,research/limpieza-voz-2026-09-30/{REVISION_A_SOLICITUD.md,skill-a-solicitud/*},CHANGELOG;AGENTS raíz/serie,ESTANDAR_QA_PREAPROBACION,CHANGELOG17 ybitácora.
- **Validación:** helper probado con señal sintética y cantidad impar de48123muestras: conserva duración48k/monoL-R y fuente; rechaza salida existente sin cambiarla y hashlib incorrecto antes de cargar/crear salida. Validación de skill/frontmatter/política/referencias, preferencias y hashes documentada en recibo de cierre. No se reprocesa voz ni render de ningún video.
- **Resultado:** workflow de restauración solo por solicitud específica. Se conservaQA/mix habitual y todo material17 sin sustituir entrega ni aprobar candidatos. Investigación de sibilancia/plosivos/clics/eco/EQ/dinámica/clipping guardada con fuentes y estado no probado donde corresponde.
- **Aprendizaje:** modificar todos los puntos de activación vivos, no solo añadir una skill; separar recomendación de tratamiento y resultado técnico de escucha. Mantener motores/recetas como recursos disponibles evita repetir instalación y masterASR.
- **Pendiente:** naturalidad/elección de audiciones17 yAdobe siguen por confirmar. De-esser y otras restauraciones específicas no ejecutados ni aprobados. Próxima activación exige petición sobre un audio/video/rango concreto.

### 2026-09-30 — Inicio VIDEO25: T25 y memoria permanente

- **Petición/punto de partida:** continuar lote21–25 y aprobación de reglas; ingesta reutilizable, toma25 con W41 corregida por W42, sin candidato25 revisable.
- **Cambios/motivo:** claim25, recibo de inicio con hashes y parámetros propios; scaffold0.8.99 confirmado vigente, history iniciado. RangosV2 con handles conservan finales/fonemas; wrapper exige texto semántico/SFX hook/dos identidades. Preparador reutilizado con caché deSHA por stat dentro de proceso para no releer maestro por segmento.
- **Archivos:** VIDEO25/source/video-25-source-ranges-v2.json; editable/qa/start/inicio-reglas.json,prepare-media.py,media-runtime.mjs,package.json; production-board;CHANGELOG y bitácora.
- **Validación/resultado:** reglas raíz/serie y plantillaT25 consultadas; CLI vigente yskillsupdate no-op. Montaje/QA aún pendientes; aprobación de reglas no se atribuye a video25.
- **Aprendizaje:** reutilizar análisis y código sin copiar un perfil de ruido, ganancias ni diseño de otro video; cachear grandes hashes por ejecución conservando verificación en cada proceso.
- **Pendiente:** preparación/audio propio, ASRdirigido, imagen contextual, tres pasadasQA, preview y aprobación25, exportexacto. Escucha/naturalidad por confirmar; no publicación.

### 2026-09-30 — Dirección sonora por intención, referencias y automatización de C

- **Petición:** el usuario escuchó C, valoró su dirección/inicio y pidió bajar música en momentos concretos como en una mezcla trabajada por frase. Aportó dos referencias para estudiar fondos, efectos, subidas/bajadas y relación con voz/imagen; aclaró que nuestras piezas de 15–30 s pueden usar una música o dos según tamaño/contexto y pidió biblioteca. No se interpreta como aprobación final ni global.
- **Punto de partida:** comparaciones aisladas A/B/C de VIDEO-13; C tenía tres acentos y cama rítmica 2,09–13,39 s con ganancia estable salvo fundidos. Primera tanda descartada, voz sola plana según usuario, análisis vocal previo y entregas/editables conservados.
- **Cambios:** ambos MP4 aportados registrados por SHA/probe; extracción sin cambiar ganancia, ASR local Whisper large-v3, separación estimada Demucs, 27 bloques, curvas RMS100ms, 46 fotogramas inspeccionados en contactos y previews con AAC copiado. Análisis extenso y visor de referencias. D conserva inicio hasta 4,05 s, voz/efectos e imagen; baja cama 4–6 dB por frase y mantiene retirada antes del remate/pregunta. Catálogo por función con tres candidatos actuales, ocho SFX y cuatro antecedentes; Resonance/alternativa y Sarsaparilla descargados del compositor con CC BY4.0, atribución, snapshots y hashes. Neon ligado al feedback de C. Criterio una/dos músicas y automatización editorial integrado en dirección de audio.
- **Motivo:** la media global voz/música no representa palabras suaves, finales ni giros. Diferenciar selección/arreglo, cambio de intención, automatización, protección local y ataque/cola permite trasladar referencias largas a piezas cortas sin cuota de canciones ni copiar faders de otra voz.
- **Archivos afectados:** Framework-Edicion-Social/research/musica-bajo-voz-2026-09-30/ (ANALISIS_REFERENCIAS_SONORAS.md, referencias.html, biblioteca.html, practica.html, APLICACION_PRACTICA.md, referencias-usuario/, audiciones/, evidencia/, scripts/); library/music/ (CATALOGO_EDITORIAL.md, catalogo-editorial.json, candidates/2026-09-30-funciones/, README.md); AUDIO_DIRECCION_Y_PROSODIA.md, changelog del framework y bitácora. Antecedentes antes de automatización, biblioteca y corrección de previews conservados.
- **Validación:** originales1/2 intactos, decode completo original/preview PASS, payloadAAC idéntico, WAV de análisis sin cambio más allá de PCM24; stemsFLOAT finitos y consistencia de suma≈0,99983/0,99961, sin certificar pureza. D: voz/SFX e inicio con error≤1,2e−7, paquetes de imagen idénticos, AAC/PCM≈0,999994; salida−16,99LUFS/−2,22dBTP. A/B/C y rangosHTTP revalidados. Biblioteca:15 registros, hashes/enlaces/formatos/energía de tres muestras20s PASS; dos licencias oficiales y decode de descargas. CUA: ambos videos cargan/saltan por capítulos, D conserva punto≈7,07s, filtros3/1/8/4 y preview20s avanza/errornull. No hubo escucha del agente.
- **Incidencias y recuperación:** urllib del Python del sistema no tenía CA local; curl con TLS validado permitió acceso, sin desactivar SSL. QA encontró previews inicialmente silenciosos por output seek posterior a filtros; se conservan archivos/diagnóstico y se corrige a seek de entrada, medida de extracto y comprobación de energía no nula. Demucs en entorno temporal privado reutiliza Torch/torchaudio2.5.1 en lectura; no cambia el entornoVIDEO17, registra desviación de dependencia antigua y ejecución exitosa.
- **Resultado:** análisis por bloques y comparaciónC/D disponibles en localhost8868; biblioteca pequeña funcional con procedencia y feedback explícitos. Referencias solo para investigación, sin reutilizar su música. Originales, C y entregas previas preservados.
- **Aprendizaje:** una pista puede producir varios estados mediante mezcla/arreglo/retirada; una segunda requiere un giro con espacio. Efectos puntúan gestos/conceptos; silencio aporta contraste. Reproducción técnica, energía y correlación no equivalen a escucha, aprobación, inteligibilidad o mejora de atención.
- **Pendiente:** escucha/elección de D; probar candidatos bajo voz; identificar auditivamente música/SFX y marcas finas de transición. Stems/faders originales desconocidos. Adopción global, cambios en editable13, prueba de teléfono y eficacia con público por confirmar.


### 2026-09-30 — RNNoise16–20 y producción16/18/19 con agentes

- **Petición:** corregir ruido16 con único motor elegido17; mismo tratamiento para lote16–20. Trabajar16/18/19 en paralelo con agentes, entregar renders revisables e informar optimización2vs3 sin consultar.
- **Punto de partida:**16v4 aprobado con imagencontextual;17RNNoise ya probado y elegido;18/19 tenían fuentes/cachés provisionales sin montaje. Denoise global sólo a solicitud.
- **Cambios:**16v5 audioRNNoise/remux preservando imagen;17v3 adopta audioya probado. Recibo autorizaciónlote y repartoagentes: editor18, auditorreglas18/anexo19, directorvisual18/19, editor19 trasliberar slot. Rootcoordina16/docs.
- **Motivo:** ruido residual reportado en misma sesión; solapar preparación/QA con límites del equipo y evitar retranscripción del master.
- **Archivos:** VIDEO16/qa-rnnoise-v5, editable-rnnoise-v5, delivery-manifest-v5, MP4v5; VIDEO17/qa/rnnoise-adoption-v3, manifest/render/scorecardv3, MP4v3; 00-INGESTA/voice-cleanup-request-16-20-rnnoise.json, qa-parallel-16-18-19/request-and-roles.json; AGENTS serie y changelogs.
- **Validación:**16checkPASS0issues,855packetsimagen+timingidénticosv4, ASRexacto, decodeAAC/metadata/lagPASS,−15,23LUFS/−1,79dBTP. RNcontext94s inferencia4,294s real.17copiaexacta del RNMP4ya verificado, textguardPASS, scorecardválido sinerrors; strictpendingnooverride.
- **Resultado:**16v5 renderizado para revisión;17editable/audio elegido coherentes.18/19enprogreso, no se afirman renderslistos todavía.
- **Aprendizaje:** revisiónaudio puede reutilizarimagen aprobada si todos sus packets/timestamps coinciden. Agentespueden prepararvideosmientrasheavyespera;25enotrochat ocupa1delos2cupos globales. No se ha medidospeedup2vs3controlado.
- **Pendiente:** finalizar18/19 y QA; informecon tiemposcomparables/limitaciones; revisiónhumana final nuevosrenders16/18/19.18–20 sólo aplicarRNpor recibo mismo lote; otros motores ni deessing no automáticos.

### 2026-09-30 — VIDEO25: candidato Forma + señal, QA y mejoras de calibración

- **Petición/punto de partida:** continuar lote25 y mantener reglas documentadas; T25aprobada, ingesta compartida, ningún montaje25aprobado.
- **Cambios/motivo:** montaje24,2333s/727frames previstos, W42reemplaza W41por marcador; cinco rangos conhandles. Paletaexacta deT25/navycrema +formas/palabras; titulares semánticos,13captions60px, fotoCompraValor generada860:770/2s. Original48k,afftdn8conperfilpropio,25mscompensados/A-B; reparacionesASRsolo9,758s. Perfilvocal propio antes deSFX. Hookdesdeprimerframe; tresSFXfuente/bindings/gainscongelados.
- **Archivos:** VIDEO25/{source,editable,visuals,creative-blueprint,style-decision,caption-decision,creative-recipe-abstention,AUDITORIA_CANDIDATO,QA_REVISION,METRICAS_PRODUCCION,ASSET_USAGE_CANDIDATE,review,CHANGELOG}; Framework/AUDIO_DIRECCION_Y_PROSODIA yCHANGELOG; bitácora.
- **Validación/resultado:** checkV4PASS80tiempos/20contrastes,0errores/avisos;52capturas/seishojas más8recapturas/hoja de cambios inspeccionadas.13cues≤2líneas; CPSmáx20,48; rostro libre en muestras. Tresidentidades/hook/guardsactualesPASS, relacionesSFX/voz−11/−12,44/−11dB; banda−11,50/−10,74/−8,21; mixPCM−16,04LUFS/−1,49dBTP. Studio reproduccióninicio/finobservados yURL3025persistente, audioUIrestaurado. PreflightestrictoFAIL/revisiónhumanafalse conservados bajoexcepciónautorizada; compiler logs/errorreal preservados sin alterar memoria global.
- **Aprendizaje/mejora:** SFXgrave inicial−18,61dBrelativo/−27,71en banda limitada generó alerta; cambiar carácter ytemporizarentrada0,30s logra−11dBfull/−11,50band, no escucha certificada. Piso arbitrario de pico hace resolución demasiadofuerte sobre frase suave; calibración por ventana sin piso fija−11dB. Hashdelmaestro cacheado porstat dentrodeprocesoevita rereads porsegmento; ASRdirigido5,382s/prepcomandos7,706s medidos, sin atribuir ahorro neto. Conservar alternativas y volver a QA sólo cambios afectados más checkfinal.
- **Pendiente:** aprobación específica25, renderfinal yQA exactoMP4/cadenaAAC; escucha/naturalidad/dispositivo y destinos realesporconfirmar. Reglasaprobadasnoequivalen a aprobación de nuevo montaje.


### 2026-09-30 — VIDEO25 aprobación del candidato y render autorizado

- **Petición:** «Aprobado», mensaje directo posterior a la presentación del candidato25.
- **Punto de partida:** T25 de24.2333s, cinco tomas corregidas,13captions y tres identidadesSFX; fuente revisada y preview mostrado, export pendiente.
- **Cambios/motivo:** congelar recibo de aprobación y24archivos con hashes; ejecutar renderdelivery30fps por wrapper con gates obligatorios, conservar candidato e históricos. Aclarar que Studio normalizó los sieteHTML: los hashes distintos no prueban equivalencia visual de archivos restantes.
- **Archivos:** VIDEO25/APROBACION_USUARIO_VIDEO25_V1.json,entrega,editable/qa/{render-approved-v1.*,changed-scope-verification.json}; Framework/AUDIO_DIRECCION_Y_PROSODIA.md yCHANGELOG.
- **Validación:**24dependencias iguales al manifiesto; check-approved-v1 ok sin errores/avisos. Gates de texto ySFX se ejecutan nuevamente antes del render.
- **Resultado:** candidato25 autorizado; render en curso. La aprobación no se atribuye a escucha ni al MP4 aún inexistente.
- **Aprendizaje:** comprobar banda/ventana real y cadenaAAC; un pico mínimo fijo delSFX puede sobrepasar una frase suave.
- **Pendiente:** QA técnico, visual y audio delMP4 exacto; uso final, manifiesto, cierre de tablero y entrega.


### 2026-09-30 — Reparación de terminación de «fácil», VIDEO16 v6

- **Petición:** usuariooyeL cortada al final de «fácil», revisar/corregir16; revisiónexacta/hashescuchado porconfirmar.
- **Punto de partida:** v5RNNoiseconASRexacto/checkPASS e imagenv4aprobada.
- **Cambios:** diagnóstico50mscontraoriginal, pruebadirigidaRN+9dBdescartada; palabraoriginal43,92–44,4s restauradacontransicionesfuera núcleo, vozfuera parche igual. Nuevoeditablev6/MP4v6;SFX/imagen/captions iguales.
- **Motivo:** preservar consonantedébil y naturalidad tieneprioridadsobre máximaeliminación deruido. Noañadir otras herramientas.
- **Archivos:** VIDEO16/qa-facil-v6, editable-facil-v6, delivery-manifest-v6, VIDEO-16-PARA-APROBACION-v6.mp4, manifest/CHANGELOG.
- **Validación:** núcleoPCM reproduceoriginal conganancia2,11035 y≤1LSBerror;855picturepackets+timingidénticosv4/v5;guardtexto/SFX/decode/metadata/AACalignedPASS;−15,23LUFS/−1,79dBTP. Verificaciónvisualv5heredada por equivalencia exactaDOM/composiciones.
- **Resultado:** v6localrenderizado para revisión;v4aprobado yv5histórico conservados. No escucha final afirmada.
- **Aprendizaje:** ASRde palabra completa no detecta terminación audibledefectuosa; señal débil−35..−57dBpuedealterarse conatenuación<12dB. Advertencia trasladada18/19; conservargrabaciónreallocalmente antesdeintroducir motoresnuevos.
- **Pendiente:** aprobaciónhumanav6; QA/render18/19 e informeflujoparalelo.


### 2026-09-30 — VIDEO25 entrega aprobada y verificación del MP4 exacto

- **Petición:** «Aprobado»; render autorizado del candidato25 y conservar mejoras para próximas ediciones.
- **Punto de partida:** candidatoT25congelado, render por wrapper con guards; entrega pendiente.
- **Cambios/motivo:** exportHLGdelivery30fps única,727frames/24.2333s; MP4/SRT/sha/recibo y uso final, manifiesto aprobado, actualizacióncaption/auditoría y conservación de documentos previos. Auditar salida exacta para evitar trasladar unPASSsolo de fuente.
- **Archivos:** VIDEO25/entrega,ASSET_USAGE_FINAL,METRICAS_PRODUCCION,AUDITORIA_CANDIDATO,caption-decision,QA_REVISION,CHANGELOG; editable/asset-ledger,dependency-map-final-v1,qa/{render-approved-v1.*,post-render-final-v1,boundaries-final-v1,model-export-visual-review-v1,verify-engine-audio-v1.py,final-audio-v1,approved-candidate-documents};Framework/AUDIO_DIRECCION_Y_PROSODIA yCHANGELOG;bitácora/tablero.
- **Validación:** renderexit0/169.873s; decode/probe/integridadPASS, postQA7.243s;137frames/cincohojas inspeccionadas,fronteras5.759s.13cues≤2líneas,rostro/imagen2s/regreso/cierre correctos enmuestras.24recursos coinciden conaprobación. AAC−16.0LUFS/−1.5dBTP; referencia completaPCM16→AAC→trim coincide muestra por muestra,total y tresSFX,0dBatenuación adicional. SHAc4d4960a6c4eefb628fb4e151304f80af747077d63674341a62aa306be81845b.
- **Resultado:** entrega local25 aprobada y QA técnico/visual terminado, tresidentidadesSFX/incluidohook. No cambios visuales después deaprobación ni nuevo masterASR;documentación/versiones conservadas.
- **Aprendizaje:** caso25no requiere correccióntruepeak adicional: nivel de24no era preset. Relación porventana/banda ycarácter delSFX resuelven presencia sinpiso arbitrario de pico; procedimiento documentado para siguientes ediciones. Medir render,QA yreparaciónporseparado; no inventar ahorro neto nitokensporfase.
- **Pendiente/límites:** no trabajoobligatorio deentrega local; escucha/naturalidad/dispositivo porconfirmar, no publicación niplataformas certificadas. Revisión137muestrasno equivale atodos727frames;gestos periféricospueden salir delcrop.


### 2026-09-30 — VIDEO18: edición paralela T18, RNNoise solicitado y QA exacto

- **Petición:** desplegar agentes para editar 18 mientras raíz corrige 16; renderizado delegado y aprobación humana al final. Petición explícita anterior limita limpieza lote 16–20 al RNNoise elegido, sin todas las herramientas investigadas.
- **Punto de partida:** fuente/proxy/ASR recovery/targeted compartidos y recursos 18 provisionales; T18Rótulo popular aprobada como diseño, sin montaje 18. CTA y límites cacheados pendientes, pista/take sin aprobación humana. Strictgate FAIL se conserva bajo excepción autorizada.
- **Cambios:** recibo de inicio/documentos/hash; montaje 21,866667s/656frames desde original 48k/HLG transformado a SDR. RNNoise nativo contexto 78s/delay 960 antes cortes, modelo/binary congelado 17; solo una ejecución. Refinar cinco cortes con ASR individual/señal, eliminar 2,60s de pausa y 2,07scola iniciales.15captions 66palabras fieles con lectura estable/énfasis, SRT ydecisión. Foto ficticia fotográfica contextual de aprender/reparar generada e inspeccionada,2s con retorno. Tres SFX/dosfuentes incluidohook, análisis prosodia ycalibración nivel/momento. Reencuadrar presentador y carril separado por 30px después bloqueo director por captions sobre manos. Guards fuente/assets/texto/hook/SFX dentro render. Único MP4v1, manifiestos, scorecard, referencias/recetas/QA/metrics.
- **Motivo:** conservar palabras y gestos, pertinencia del apoyo y limpieza limitada autorizada; reutilizar ingesta/modelos/contextos y evitar recorridos repetidos. Pausas y tiempos ASR cacheados no eran fiables como cortes; excepción permite trabajo útil sin afirmar escucha.
- **Archivos afectados:** VIDEO18/{editable-hyperframes-video-18, source/video-18-source-ranges-v2.json, visuals V02, qa, manifest, asset-lock, caption-decision, render-manifest-v1, qa-scorecard-v1, VIDEO-18-PARA-APROBACION-v1.mp4, QA_FINAL, CHANGELOG, METRICAS_PRODUCCION}; tablero claims 18/release temporal para 19. Original/script recursos previos conservados.
- **Validación:** check 78tiempos/transiciones PASS0errores/avisos; guardfuente/imagen/voz/SFX/texto PASS. Dos ASRindividuales 66/66palabras/no marcadores, no prueba fonemas. Decode/meta completo PASS1080×1920BT709/AAC48k/656frames;−15,14LUFS/−1,23dBTP; mix PCM/AACcorr 0,9999447 ylag 0cinco ventanas/largo 1.049.600muestras. Director independiente 192estados/15cues/cortes/photo/regreso ycuatroframes 360px sin bloqueantes; hash exacto comprobado. Scorecard válida/errors[], strict conserva AUDIO_STREAM_UNLOCKED/VIDEO_TAKE_MISSING/QA_DELIVERY_BLOCKED. No escucha/approval/socialpreview inferidos.
- **Resultado:** candidato MP4 SHA7978d638f464ebccd8d68b1cd54e2c939cbc3a9e0acb5a800fd0307f6f2cb960, preview 3008 listo para revisión local; aprobación 18pendiente. Nuevo diseño/audio no hereda aprobación de 16ni plantilla. Master ASR no repetido.
- **Aprendizaje:** RN78s 4,050s/extracción 0,259s, SDR4,971s; ASRmotor 7,173/7,033s individual; único render 26,0s (wall enrecibo), tiempos/retrabajo en METRICAS_PRODUCCION. Liberar cupo durante authoringligero permite 19preparar sintercerheavy; ahorro neto/tokens/comparacióncausal 2vs3 no medidos. Detector de 40dB/12dB omitía potencialesfonemas débiles: sensibilidad 4dB/−60 registra señales sin rescate automático. Holdfinal 247ms ydesplazamiento JPG diagnosticados, RGBMP4 directo correcto; no re-render innecesario. Holds de motion intencionales para leer/presentador.
- **Pendiente:** escucha/fonemas/timbre/SFX, take/stream humano, aprobación MP4 ypreviews IG/FB/TikTok; sin publicación. No extender RNNoise al universo ni aplicar de-esser/otrosrestauradores automáticamente.



# VIDEO19 — 2026-09-30 — candidato final v1

- Petición: editar VIDEO19 en paralelo con la corrección del16 y edición del18, con render a criterio para aprobación final. Aplicar únicamente el RNNoise seleccionado al lote16–20 por solicitud explícita.
- Punto de partida: cinco rangos provisionales dentro de518,55–635,15s; plantillaT19 PixelQuest aprobada. Toma y pista humanas sin aprobación confirmada.
- Cambios: cinco cortes refinados con caché, señal y ASR corto;29,6s y888frames. RNNoise a48k sobre contexto original517–637s antes de cortar, compensación960muestras. Último «persona» conserva original plegado a mono desde28,66s tras transición de60ms y normalización común; sin otro limpiador ni fundido final. HLG convertido a BT709 SDR. T19 con monospace, navy/lime, presentador840×960 y carril separado de veinte captions64px, una o dos líneas. Foto contextual reutilizada dos segundos. Hook conSFX, cuatro eventos y tres identidades.
- Motivo: preservar pregunta, contradicción, cifras, negación y CTA; corregir tiempos distorsionados delASR recuperado, proteger manos/rostro y el final débil de una palabra, sin repetir análisis completo del lote.
- Archivos: editable-hyperframes-video-19/ (scripts, HTML, composiciones, assets, captions y QA);source/video-19-source-ranges-refined-v1.json;audio-direction.json;caption-decision.json;manifest.json;render-manifest-v1.json;qa-scorecard-v1.json;VIDEO-19-PARA-APROBACION-v1.mp4. Dirección: qa/director-visual19/DESIGN_BRIEF.md ypreparation-receipt.json. Auditorías: qa/director-visual19/FINAL_MP4_VISUAL_REVIEW_V1.json yqa/independent-audio19.json. Original, primera voz RNNoise, QA previo y manifest inicial conservados.
- Validación: check sin errores en104estados/transiciones y nueve contrastes; advertencia esperada por captions en una pista. Smoke5,2s sin caption fantasma en tercer cue/hueco. Guardas internas de fuente/hash, texto ySFX pasadas antes del render. MP4 exacto: decodificación completa,1080×1920,30fps,29,6s,888frames,48k y1.420.800muestras;−15,18LUFS y−1,80dBTP. CorrelaciónAAC/PCM0,9999325, último «persona»0,99998016. Audio independiente sin bloqueantes técnicos. Director visual: PASS sin bloqueantes en218estados de ocho hojas y cincoPNG360×640, cubriendo veinte cues, cortes, foto, retorno y último frame. Scorecard formal válido, errors[], strict delivery deshabilitado.
- Resultado: candidato renderizado SHA65db6e694d3d384b190e40082dfa19005178384a51d88b4624aa4e5f8317adc4 listo para revisión final. No implica aprobación ni publicación.
- Aprendizaje: ASR puede reconocer una palabra aunque RNNoise atenúe su final débil; un rescate acotado del original conserva ese tramo sin añadir motores. Comparar SFX con voz real permitió corregir masking técnico. SmokeHTML fuera de raíz evita el error multiple_root_compositions. Leer el objetoJSON del loudnorm evita fallar por texto posterior enstderr. Sin ahorros ni rendimiento atribuidos: RNcontext5,919s, SDR6,289s, smoke6,6s, render37,1s de pipeline/40,836s de comando, extracción de218frames2,084s. Cola exacta y comparación controlada2vs3 no medidas.
- Pendiente: aprobación final, escucha humana de naturalidad/cadencia/fonemas, confirmación humana de toma/pista y previews reales deInstagram/Facebook/TikTok. Las mediciones y revisiones del modelo no sustituyen esas comprobaciones.


### 2026-09-30 — Entrega16/18/19 e informe de producción paralela

- **Petición:** tres videos con agentes/subagentes, finales renderizados para aprobación humana, informeoptimización2vs3 yconfiguraciónlímites; usuario pide verlos.
- **Punto de partida:**16v6/18v1/19v1 renderizados, QAindependiente en cierre yregistro18 integrado.
- **Cambios:** entrega consolidada paths/SHA, métricasporfase e informe `Framework-Edicion-Social/INFORME_PARALELO_16_18_19_2026_09_30.md`; cierre19integrado. Manifest/scorecard18actualizan hash delrecibovisual que explicita móduloautomaticmotiondesactivado, sin tocarMP4. Rootrevisiónparcial19(72estados) añadida. Cutplan17previo recuperado con SHAoriginalexacto yinputsactuales17reconciliados.
- **Motivo:** entregar resultados verificables, conservar historia, distinguir medición/propuesta yevitar afirmar ahorro2vs3conmaterial/configuraciones diferentes.
- **Archivos:** informe/frameworkmejora/changelogs; 00-INGESTA/qa-parallel-16-18-19/{delivery.json,measured-phases-final.json,request-and-roles.json,host-snapshot.json}; VIDEO18/qa/final-v1/receipt-qualification-update ymanifests/scorecards; VIDEO19receiptsfinales/rootscoped; VIDEO17/qa/rnnoise-adoption-v3/before/cut-plan.json yrender-manifest-v3.
- **Validación:** hashes finales16v6/18v1/19v1comprobados; decode/audio/metadataPASS; visualindependiente18(192estados)/19(218), audio19independienteAAC/PCMúltimapersona. Scorecards18/19válidaserrors[]congateshumanos pendientes.16v4aprobado/versionesanteriorespreservados.
- **Resultado:** tres MP4locales completos,listos para ver/aprobar; informeconmedidas yreparto2vs3guardado. Plazaliberada18reutilizadaQAaudio19conbriefcompacto. Heavy16/18/19 liberados, sin cambiarcupos ni publicar.
- **Aprendizaje:** separacióncaps/gestos, consonantesdébiles, imágenesencontexto yRGBdirecto previenenfallos/re-renderinnecesario. Agentes4plazasactualesyheavyboard2sonlímites distintos/configurables; capacidadmayor/costo/tokens/ahorro2vs3noevaluados.
- **Pendiente:** aprobación/escuchahumana ydestinosreales de nuevosrenders. Comparación2vs3equivalente/capacidad3heavy pendiente;20conRNNoiseautorizado para próximaedición, sin render20afirmado.


### 2026-09-30 — Recibo de consumo al cerrar objetivo paralelo

- **Petición:** informe real de optimización yentrega16/18/19; registrarcontadorfinal disponible.
- **Punto de partida:** tresMP4 yreportecerrados, objetivo completado en tracker.
- **Cambios:** añadidos `goal-completion-usage.json` yanexo del informe con3194s(53min14s)/1.394.606tokens rastreados, sinbudget.
- **Motivo:** distinguir contador global real de tiemposCPU/pareddeedición/facturación/ahorroinferido.
- **Archivos:** 00-INGESTA/qa-parallel-16-18-19/goal-completion-usage.json, INFORME_PARALELO_16_18_19_2026_09_30.md.
- **Validación:** valores copiados del resultadoestructurado `update_goal(status=complete)`; no estimaciones ni desgloseporagente.
- **Resultado:** informe añadeconsumo/elapsedglobal; board65sinclaims0heavy. Renders intactos.
- **Aprendizaje:** elapsedgoal incluye conversación, herramientas, revisiones yalcancehistórico; no es baseline2vs3 ni costo facturado.
- **Pendiente:** aprobaciónfinalhumana ycomparacióncontrolada futura.


### 2026-09-30 — Cinco pruebas de musicalización guiadas por la voz

- **Petición:** tres voces20–30s y dos narraciones largas existentes, música/SFX con volumen por momentos, biblioteca, pruebas verificadas y proceso documentado. Sin veredicto final sobre pistas con sonidos fuertes; una o dos músicas en cortos según contexto.
- **Punto de partida:** dirección/inicioC favorables con bajadas pedidas, primera tanda calmada descartada, dos referencias estudiadas. Se localizó corte01 vigente21,375s (no viejo28,893s), voces11/14 y guías Kokoro52,93s/HeyGenV05 158,798s; radio-cut humano130,892s localizado y conservado.
- **Cambios y motivo:** cinco mezclas aisladasV1/V2 con perfiles de voz, planes por texto/prosodia, música trabajada dentro de frases, retiradas y29 eventosSFX. Tres descargas oficiales Kevin MacLeod, créditos/licenciaCC BY4.0/hashes/snapshots; catálogo pasa a seis candidatos sin aprobación global, ochoSFX y cuatro antecedentes. Reindexador conserva ampliaciones/feedback. Se evita nivel musical constante y no se altera interpretación/ritmo de voz.
- **Archivos:** Framework-Edicion-Social/research/prueba-mezcla-voz-2026-09-30/{index.html,PROCESO.md,CREDITOS.md,RECIBO_INICIO.json,plan-mezcla.json,manifest.json,fuentes,evidencia,scripts,renders/v1,renders/v2}; library/music/candidates/2026-09-30-mezclas-contexto, catálogo/guía; scripts/indexar_biblioteca.py y changelogs. Editables/renders fuente intactos.
- **Validación:**45medios hash/decode/48kestéreo/energía no nula; invariancia de voz a ganancia constante y suma de stems; mínimo dos identidades y SFX en todos los hooks. AAC≈−18,01 a−19,01LUFS, techo máximo−2,99dBTP, AAC/PCM mínimo0,999800. Cinco reproducciones nativas/errornull, capítulos y comparación conservan posición. Sin escucha perceptual del agente ni aprobación auditiva humana.
- **Resultado:** banco con cinco audiciones completas, controles para voz/música/SFX y descargas, duraciones reales; documentos reproducibles. UNAUTHORIZED en búsquedaHeyGen se resolvió con fuentes públicas oficiales, sin bloquear ni subir voces.
- **Aprendizaje:** preservar montaje vigente y diferencias de cola1/16,1875ms con silencio terminal, no usar16kASR para mezclar. Relación por banda/energía residual ayuda a localizar riesgos, no prueba inteligibilidad. Ducking complementa dirección editorial sin levantar cada hueco; recortar antes de fades y validarRMS evita repetir previews silenciosos.
- **Pendiente:** escucha completa y feedback por pieza/segundo, timbre/naturalidad/claridad percibida, repertorio y adopción en editable. No publicación, rendimiento de audiencia ni elección de canciones certificada.


### 2026-09-30 — Perfiles flujo1/2/3 y piloto26–30 preparados

- **Petición:** crear flujos2/3 sin dañar lo que funciona, dejarlos listos para probar mañana con26–30; comparar conveniencia de lote nuevo versus repetir anterior.
- **Punto de partida:** procedimiento vigente y renders21–25 terminados; herramientas de cambios/caché/medición de comandos disponibles pero no automatización completa.26–30ya tenían52archivos de preproducción, sin editables/renders en inventario.
- **Cambios:** perfiles versionados y QA común:1actual/predeterminado,2misma intención/cobertura con organización/reuso,3alcance esencial con mismos controles. Snapshot de20archivos de referencia. Ruteo aditivo enAGENTS,README,MEJORA yprompts. Nuevos helpersselección/run/índice de evidencia, temporizador porfases con esperas/auditoría aparte ycontexto de dependencias que falla cerrado. Guía/comandos, planpiloto1deoctubre, inventario yplantilla de evaluación, regresión lectura25, pruebas yreciboREADY.
- **Motivo:** mejorar organización/repeticiones/documentación antes de reducir personalización; mantener controles críticos, retorno a1y medición honesta. Tres perfiles sobre base común, no tres motores separados ni eliminación progresiva deQA.
- **Archivos afectados:** Framework/workflow-profiles/{catalog,flujo-1,flujo-2,flujo-3}.json,QA_COMUN,GUIA,CHANGELOG,baseline/2026-09-30,experiments/2026-10-01-lote26-30; scripts/{workflow_run,medir_fases_edicion,qa_reuse_context}.py ytests respectivos;AGENTS raíz/serie, Framework/{README,MEJORA_CONTINUA,PROMPT_EDICION_INDIVIDUAL,PROMPT_INGESTA_Y_EDICION,CHANGELOG};bitácora.
- **Validación:**41testsPASS:8run,8timer,15reuso,5temporizador previo y5gate texto previo. Smoke CLIinit→start→evento→stop→reportePASS. Regresión25rehashea24archivos congelados iguales, contextosin cambios elegible/rechazo sin inventario actual; no render nuevo. Snapshot20archivos íntegro; scripts/QAprevios idénticos y cuerpos de documentos conservados con ruteo añadido.52recursos26–30intactos. Evidenciaenexperimento/validation/{unit-tests.json,test_workflow_run.final.log,READY.json},regression-video25/result.json.
- **Resultado:** perfiles2/3 listos para piloto experimental,1sigue default. Prueba propuesta2F1+2F2+1F3, asignaciónnullhasta ingesta/criterio de complejidad yantes de montar. Auditoríaextra/espera/huecos separadas ytotal visible. No se han editado ni renderizado26–30 ni cambiado archivos21–25.
- **Aprendizaje:** lote nuevo mide montaje real;25conocido valida herramientas, no velocidad de editar algo que ya conocemos. CambioHTML/rótulo invalida semántica; imagen también captions porcontraste/rostro. Cachepreviaomiteengine/config:contextocomplementario exigeinventarioactual yversiones/hashesreales, solo propone elegibilidad, nuncaPASS/aprobación. Copias deperfil/QAporrun permiten informes históricos tras versionado, ydetectan cambiosvivos antes de nuevos eventos. Fasesdesconocidasnull, no0inventado.
- **Pendiente:** ingesta/fuente/asignación y prueba audiovisual26–30 el1deoctubre; medidas comparables de tiempo,defectos/retrabajo/alcance y valoraciónhumana. Perfilescontinúanexperimentales, sin ahorro/equivalencia demostrados nipromociónautomática. Cincoobservaciones seránpreliminares;F3no es comparación deigualalcance. Noautomatizaciónprogramada ni autorización depublicación/restauración/render de nuevos candidatos inferida.


### 2026-09-30 — Aprobación final16/18/19 y diagnóstico de diversidad visual

- **Petición:** «Ok aprobados los 3» y explicación sobre video recortado, espacio bajo captions y ausencia de iconos/SVG/botones frente a las plantillas.
- **Punto de partida:**16v6/18v1/19v1 mostrados al usuario, QA documentado, aprobación final pendiente;16v4 aprobada históricamente.
- **Cambios:** recibos explícitos SHA256 para16v6/18v1/19v1 y estado aprobado en manifiestos/entrega consolidada; snapshots previos conservados. Inspección de CSS, textos, assets, catálogos y propuestas originales; un fotograma de cada MP4 a7/3/7s respectivamente. No cambios a medios ni reglas.
- **Motivo:** fijar qué versiones aprobó el usuario y explicar decisiones editoriales sin atribuir a la plantilla una uniformidad que no exige.
- **Archivos:** VIDEO16/18/19/APROBACION_VIDEO_N_VN.json, manifest.json, delivery/render-manifests, CHANGELOG;00-INGESTA/qa-parallel-16-18-19/delivery.json ysnapshot;bitácora.
- **Validación:** SHA256 de los tres MP4 coincide con manifiestos previos; JSON legible. Visuales comparados conT16/T18/T19. CSS16 conserva toma mediantecontain;18/19 usancover enventanas778×810/840×960, captions en1254/1280 y área restante sincontenido narrativo. Composiciones activas tienen una foto deapoyo porvideo, sinSVG inline. La muestra no es visionado completo nuevo.
- **Resultado:** tresversiones aprobadas porusuario, sin publicación ni modificación delMP4. Consulta atendida: carril separado protegegestos pero recorte/fondo inferior fueron decisiones delmontaje;18/19 perdieron parte del lenguaje gráfico original.
- **Aprendizaje:** QA de legibilidad/rostro/errores no basta para certificar fidelidad y diversidad deplantilla. T16 esminimalista;T18 proponíarótulos/gráfica cotidiana yT19mapas/elecciones/inventario/progreso. Adaptartexto alcontexto no exige borrar todos esos recursos; usar solo apoyossemánticos. Margeninterno no es requisitosocialuniversal.
- **Pendiente:** posibles mejoras de encuadre/composición/fidelidad para siguientes versiones o videos, sujetas a petición concreta;previews reales deIG/FB/TikTok yselección humanafuente siguenporconfirmar. Aprobación no acredita escucha/visionado completo no descritos.


### 2026-09-30 — Regla permanente de fidelidad y diversidad de plantillas

- **Petición:** documentar para siguientes videos/lotes la intención de plantillas distintas en estructura, diseño, iconos y demás recursos, más allá de colores.
- **Punto de partida:**16v6/18v1/19v1 aprobados; diagnóstico previo detecta simplificación deT18/T19 y ventanas con crop/carril separado/fondo inferior amplio. Catálogo ya diferenciaba mundos visuales; QA no señaló suficientemente esa pérdida.
- **Cambios:** contratoFIDELIDAD_Y_DIVERSIDAD_PLANTILLASv1, plantilla de revisión porvideo y ruteo obligatorio enAGENTS raíz/serie, QA serie/framework, README/estilos/prompts; preferencia explícita confirmada. QA_COMUNv0.1.1 aclara que perfiles1/2/3 conservan identidad.
- **Motivo:** convertir la preferencia en un control operativo consultado al inicio y revisado contra propuesta original/vecinos, antes del render y en export exacto.
- **Archivos:** Framework-Edicion-Social/{FIDELIDAD_Y_DIVERSIDAD_PLANTILLAS.md,templates/template-fidelity-review.md,README.md,QA_PROFESIONAL.md,styles/README.md,profiles/creative_preferences.json,PROMPT_EDICION_INDIVIDUAL.md,PROMPT_INGESTA_Y_EDICION.md,workflow-profiles/{QA_COMUN.md,GUIA.md,CHANGELOG.md},CHANGELOG.md};AGENTS raíz/serie,ESTANDAR_QA_PREAPROBACION ybitácora. Versionesprevias enresearch/fidelidad-plantillas-2026-09-30.
- **Validación:** revisión de enlaces locales, JSON y presencia del ruteo; hashes previos/post registrados enrecibo. Sin render ni nuevoQA audiovisual afirmados; controles editoriales no automatizados.
- **Resultado:** regla vigente para futuras ediciones/lotes y tareas delegadas, con revisiones de identidad/variación/crop/espacio negativo y funciones semánticas de recursos.16/18/19yplantillas históricas permanecen intactos.
- **Aprendizaje:** optimizar reutiliza componentes/insumos, no convierte familias distintas en la misma composición recoloreada. Minimalismo válido segúnplantilla; variedad no significa añadiradornos porcuota ni inventar contenido/interactividad.
- **Pendiente:** ejecutar y evidenciar el control en cada video nuevo; no hay todavía resultado de aplicación, ahorro/retención demostrado ni reedición autorizada de aprobados.


### 2026-09-30 — Aclaración de control temprano y referencia visual aprobada

- **Petición:** exigir desde inicio para evitar trabajo perdido; conservar reglas anteriores y retirar comparación de vecinos porque estilos/propuestas ya fueron diseñados y aprobados.
- **Punto de partida:** contrato v1.0.0 recién integrado con vecinos/mínimo de diferencias y controles inicio/final.
- **Cambios:** v1.1.0 exige ficha/tablero, mapa de voz/recursos, geometría y maqueta ligera conformes antes de composición completa; montaje/final verifican conservación. Eliminadas comparación obligatoria de vecinos y cuota de diferencias; ajustados los dos puntos históricos activos equivalentes en AGENTS/QA serie. QA_COMUNv0.1.2, prompts, README/QA/estilos y preferencia confirmada actualizados.
- **Motivo:** aplicar el diseño aprobado temprano, sin reabrir exploración comparativa ni pedir otra aprobación rutinaria; prevenir rediseño tardío.
- **Archivos:** contrato, template de revisión, AGENTS raíz/serie, QA serie/framework, README/estilos/prompts, perfiles/QA_COMUN/GUIA/changelogs, creative_preferences ybitácora. Snapshot de v1.0.0 enresearch/fidelidad-plantillas-2026-09-30.
- **Validación:** controles documentales/enlaces/JSON y comparación contra snapshots para comprobar conservación del contenido ajeno a esta aclaración. Sin ejecución audiovisual ni detector automático nuevo.
- **Resultado:** referencia única de fidelidad es propuesta/ficha aprobada; control de inicio impide pasar a composición completa con not_run/requiere_correccion. Integrado con tres pasadas vigentes.
- **Aprendizaje:** diversidad se fija al aprobar familias; la edición conserva y contextualiza ese lenguaje. QA final verifica ejecución, no es el primer momento de diseñar.
- **Pendiente:** aplicar control y evidenciarlo en próximos videos/lotes; no cambios a aprobados, ni ahorro/calidad de resultados futuros medidos.


### 2026-09-30 — Inicio autorizado lote26–30 y piloto medido

- **Petición:** editar y entregar los cinco videos26–30 renderizados e informe final de flujos, sin consultas rutinarias; Sol6.1Medio, agentes y mantener equipo activo mientras trabaja. Autorización exacta en LOTE-26-30-PRODUCCION/AUTORIZACION_Y_ARRANQUE.json; no equivale a aprobación editorial de candidatos aún no vistos.
- **Punto de partida:** master26–30 recién disponible, preproducción histórica existente; perfiles1/2/3 y QA_COMUN0.1.2/fidelidad1.1.0 vigentes. No hay editables ni renders26–30 al inicio.
- **Cambios:** iniciados temporizador compartido de ingesta, responsable único de análisis/tomas/proxies, auditor de mediciones y dirección visual independiente. Activado caffeinate-dimsu temporal con proceso vivo/session45344, PID85114 confirmado porpmset. Recibo de alcance/modelo/autorización y recuperación guardado.
- **Motivo:** producir lote real y medir organización/alcance de cada perfil conservando reglas, identidad visual y controles. EvitarASR repetido y sumar ingesta cinco veces.
- **Archivos afectados:** LOTE-26-30-PRODUCCION/AUTORIZACION_Y_ARRANQUE.json; experimento2026-10-01-lote26-30/ingesta-lote; source-manifest/recibo técnico de ingesta por agente; bitácora.
- **Validación:** master localizado700175198bytes, preflight agente14PASS con duración609.0817s; skillsupdategeneral-video informa current. pmset confirma assertions de sistema/pantalla, sin preferencias permanentes. Estas evidencias no prueban escucha ni QA final.
- **Resultado:** ingesta/planificación en curso; renders y comparación aún pendientes. Asignación2F1/2F2/1F3 se congelará después de conocer tomas yantes de montar.
- **Aprendizaje:** preparación histórica se separa del costo actual; modelo/nivel comunes reducen confusión en la prueba. Recepción de petición de render autoriza ejecutar exportes trasQA, no afirmar aceptación perceptual humana.
- **Pendiente:** ASR/marcadores/correcciones, rangos/cortes, asignación/maquetas conformes, montaje5videos, QA/renders exactos, informe medido y finalizarcaffeinate.


### 2026-09-30 — Tres tratamientos por pieza larga y cierre técnico de musicalización

- **Petición:** mejorar sistema/comprobaciones al máximo útil, varias canciones y pruebas especialmente en1/2min, más efectos/edición y cambios de nivel como mixer multimedia; referencias aportadas. Las voces halladas duran52,93s y158,798s, preservadas completas.
- **Punto de partida:** cinco primeras pruebas aún candidatas, sin aprobación de música; voz compartida y fuentes verificadas. No se borra ese resultado ni se cambia el repertorio por un veredicto no dado.
- **Cambios/motivo:** seis alternativas completasA/Pulso y precisión, B/Cálida y fluida, C/Contraste editorial, tres por voz; seis canciones, ochoSFX originales candidatos y91eventos con intención. Automatización editorial, carve dinámico sobre música, protección secundaria descendente/colas, versionesV1/finales y stems. Voz/nivel común exactamente iguales para comparar; más efectos no se declara mayor calidad.
- **Archivos:** research/prueba-mezcla-voz-2026-09-30/{variantes.html,PROCESO_VARIANTES.md,CREDITOS_VARIANTES.md,RECIBO_AMPLIACION.json,variantes-largas,scripts}, library/sfx/candidates/2026-09-30-musicalizacion. NuevoAUDIO_MEZCLA_CONTEXTO_QA.md enlazado desdeAUDIO_DIRECCION_Y_PROSODIA.md; índice anterior preserva catálogo ampliado/feedback y sus recuentos reales. Tanda/masters previos intactos.
- **Validación:**42medios nuevos +seis simulacionesmono; fuentes/bindings/hash, finitud/energía,48k/duración, voz recuperada≤2,4e−7, hooks/SFX, AAC/PCM>0,999 y true peak≤−5,84dBTP; I≈−18,01/−18,02LUFS. Seis reproducciones nativas, capas y comparación conservan posición/errornull. Biblioteca seis candidatos/ocho originales/cuatro antecedentes revalidada; nuevosSFX siguen candidatos separados.
- **Incidencias:** media de energía tuvo negativos de precisión y sqrtNaN detuvoC; se guardó fallo, se verificó límite y corrigió solo residuo, se repitieron seis salidas. ASR completo de guía repitió frases(A/C≈27/44%WER): timestampsnulos, vozPCM idéntica acontrol83,7–93,2s enA/B.32lecturas por ocho actos comunes contrastan modelo: A/C0dif contra control; B2palabras y más próxima al guion. No se ocultan fallos ni se fuerza mezcla a seguir un proxy.
- **Resultado/aprendizaje:** comparador con tres tratamientos por largo y primera prueba, voz/música/SFX, descargas. CierreLISTA_PARA_ESCUCHA por cobertura técnica; protocolo aplica comparaciones justas y separa defecto físico de contexto del reconocedor. No afirmación de escucha por agente ni de que ninguna mejora futura sea posible.
- **Pendiente:** valoración auditiva del usuario, carácter/naturalidad/claridad en dispositivo real y ajustes por segundo; elección/adopción de recursos. Sin publicación, aprobación global ni eficacia medida.

### 2026-09-30 — Dirección26/29, recurso nuevo y control HDR del piloto

Petición: editar autónomamente26–30 y crear recursos pertinentes cuando los anteriores no encajen. Punto de partida: ingesta única, preproducciónSep25 conservada y flujos congelados. Cambios: control tempranoT26/T29 con maquetas y geometría de presentador íntegra; imagen26nueva de investigación de reputación(25.957s de herramienta) sustituye metáfora mecánica, sin borrar previa; 26montaje6escenas/17cues/3SFX, voz normalizada sin restauración especializada. Fuente final26extraída del masteroriginal4.445s. Motivo: legibilidad/contexto/fidelidad. Archivos: VIDEO26/29RECIBO_INICIO,QA_FIDELIDAD,CHANGELOG,qa/inicio;26editable/assets,compositions,qa,asset-ledger; timers respectivos. Validación:poses y maquetas inspeccionadas;26checksv1/v2 detectaron solape1frame/slotsSFX, corregidos; smokeHDR1detectó titular previo fantasma, smoke2(41.1s) confirmó cierre explícito/gap/cues. Checkv4sin errores/warnings; texto visible sin etiquetas;3identidadesSFXcontra voz con evidencia técnica, no escucha humana. Resultado:26renderfinal en proceso,29conforme para montaje; no entregas finales aprobadas todavía. Aprendizaje: Studio limpio no prueba composiciónHDR exacta; hardkill al fin del titular evita dobletexto. Pendiente:5MP4exactos/postQA,escucha humana/plataforma porconfirmar y reporte medido; incluirreintentos y costescompartidos sin ocultarlos.


### 2026-10-01 — lote26–30: captions documentadas y controles de acabado durante render

Petición: preservar calidad, crear recursos pertinentes y medir los flujos sin romper el sistema existente. Punto de partida:26y28finales locales revisados,30v1 renderizado,27/29 en producción. Cambios: decisión de captions/SRT26y29; quince frases fieles a73palabras en29, contraste crema en header azul antes render; SFX29rotados a entrada cálida/tick/secuencia para evitar repetición adjacentede30. Se inicia corrección30v2 con fondo navy persistente tras auditoría de47frames: v1 pasa por negro alrededor del presentador un frame al entrar módulo; no se confunde esto con un fullblackframe. Motivo: acabado visual y trazabilidad verificable. Archivos afectados: VIDEO26/caption-decision.json ySRT/CHANGELOG; VIDEO29/editable/BRIEF,index,build-composition,qa ycaption-decision; VIDEO30v2 en curso. Validación:29fullcheck0errores0warnings,19contrastes, guard3SFX sinflags, perfil de voz ysmokeHDR6.8s/48.5s inspeccionado; header azul revisado por snapshot dirigido. Resultado:29final enrender;30v1 preservado yv2 pendiente. Aprendizaje: hashesdetectan dependencia visual cambiada y exigen revalidarla; medir presencia técnica no prueba audición. Pendiente:27/29/30v2QAexacta, informe conjunto, escucha humana/dispositivo/plataformas porconfirmar. No se promueven flujos experimentales.


### 2026-10-01 — Cierre local del lote 26–30 y resultados del piloto

- **Petición:** entregar cinco videos renderizados y el informe medido de flujos, con recursos pertinentes, ejecución autónoma autorizada y conservación del sistema vigente.
- **Punto de partida:** ingesta única provisional, 52 archivos de preproducción histórica y asignación congelada 26/27 flujo1, 28/29 flujo2, 30 flujo3. Se conserva el registro anterior y las versiones previas.
- **Cambios:** entregas finales 26v3, 27v2, 28v1, 29v2 y 30v2. Correcciones de transición para ocultar tarjetas/círculos/cierre hasta fondo opaco en26/29, fondo futuro27 y base persistente30.26 incorpora imagen contextual nueva;27 efecto de entrada original e iconos SVG adaptados. Los restantes recursos se conservaron tras revisar contexto y estilo.26v3 cambia sólo el hook a ENTRY0003 y reutiliza exactamente el HEVC de v2 con AAC nuevo.
- **Motivo:** proteger el rostro también durante transiciones, asegurar contexto y composición, cumplir rotación SFX incluyendo frontera25→26 y evitar captura de video innecesaria cuando sólo cambia audio. Crear recursos cuando los existentes no encajen, sin cuotas de creación.
- **Archivos afectados:** editables/QA/recibos/CHANGELOG de VIDEO26–30; LOTE-26-30-PRODUCCION/{MANIFEST_ENTREGAS_FINAL_v1.json,LEEME_PAQUETE_FINAL_v1.md,VERIFICACION_PAQUETE_MEDIA_v1.json,SFX_ROTACION_VERIFICADA_v1.json,FUENTE_PRESERVADA_CIERRE_v1.json,CIERRE_RELOJES_Y_BOARD_v1.json,ACLARACION_CONTADORES_26_v1.json,CHANGELOG.md}; experimento2026-10-01-lote26-30/execution-v1/{INFORME_FINAL_v1.md,RESULTADOS_FINALES_v1.csv,RESULTADOS_FINALES_v1.json,EVIDENCE_INDEX_FINAL_v1.json}; bitácora.
- **Validación:** hashes/metadatos de cinco MP4 exactos, portrait1080×1920/30fps/HEVC Main10 HLG BT2020/AAC48k estéreo; revisión creador y sombra de59/60/42/58/24frames finales respectivamente, alcance por cues documentado. Mezcla AAC completa y tres ventanasSFX verificadas en cada salida; rotación real24–30PASS. Fuente original conserva SHA201570f0…;52/52 históricos conservan hashes. Cinco relojes de producción cerrados y board vacío generación127. Informe final leído y21enlaces locales comprobados. Esto no prueba escucha ni aprobación humana.
- **Resultado:** cinco entregas locales y reporte final disponibles; nueve renders visuales completos y un derivadoAAC. Cuatro renders correctivos suman619,440s de motor mostrado; no equivale a tiempo del lote ni ahorro posible. Ingesta inicial767,083s una vez. Fases separan motor/comando/revisión/coordinación, faltantes e intervalos mezclados; no se suman agentes solapados. Flujo1 sigue predeterminado;2/3 experimentales, rapidez o equivalencia causal aún no demostradas.
- **Integridad:**28 conserva dos eventos históricos con hashes mutables rechazados; su reporte automático no se declaraPASS.26 mantiene evento histórico y ledger original, adoptando ledger-v3 separado. Contador histórico full_render=3 se distingue de2llamadas visuales+1derivado audio. No se reescribe historia para esconder defectos o costos.
- **Aprendizaje:** el acabadoHDR exige base persistente explícita, fondo dentro del child, cuerpo tras fondo opaco, apagado determinista y smoke con escenas futuras. Usar evidencias inmutables y comprobaciones dirigidas para cambios localizados, más QA del nuevoMP4. Estabilizar esa receta antes de atribuir diferencias de tiempo a perfiles.
- **Pendiente:** escucha/naturalidad, confirmación fonética del hook26 y contexto sin claqueta27, dispositivo/plataforma y colorimetría física por confirmar. Sin publicación ni aprobación editorial inferida. Siguiente comparación recomendada: misma fuente/plantilla en condiciones equivalentes y otro lote nuevo; no se crea ni se promueve ahora. Caffeinate temporal se retirará al terminar el cierre documental, con recibo de proceso; no preferencias permanentes.

Cierre operativo adicional (2026-10-01T06:03:07.331918+00:00): informe final concluido con22 enlaces locales válidos e índice estable; reloj de auditoría cerrado. CaffeinatePID85114 retirado medianteSIGTERM, proceso ausente comprobado; sin cambios permanentes de preferencias. Recibo: LOTE-26-30-PRODUCCION/CIERRE_PRODUCCION_v1.json. Se completa la entrega local autorizada; escucha humana y plataforma permanecen por confirmar.

### 2026-10-01 — Piloto real de publicación MCP: 11 casos y 17 destinos programados

- **Petición:** probar todos los formatos y dejarlos para mañana; el usuario aclaró «Programadas para publicarse realmente mañana». La etapa inicial de borradores se conserva como historia; publicación real autorizada para el 2 de octubre de 2026 en Silent Run Ecuador.
- **Punto de partida:** Metricool conectado, plan Free de una marca / 20 publicaciones mensuales y 0 publicadas al inicio. VIDEO-18 v1 aprobado disponible; se crearon seis tarjetas específicas de prueba fuera de los artes aprobados.
- **Cambios:** preparación y activación de 11 casos para 17 destinos IG/FB/TikTok/YouTube; todos `draft=false`, `autoPublish=true` global e Instagram automático en seleccionados. Copia final de 18 SVG/PNG/JPEG, contacto, manifest y 18 evidencias; informe, CSV humano de 11 filas e inventario de hashes/rutas. Borradores gráficos anteriores no se incorporaron al lote final.
- **Motivo:** aprender el flujo real de subida/programación por MCP, separar formatos/copies/medios y conservar un recibo comprobable por destino, sin alterar masters o artes existentes.
- **Archivos afectados:** `Framework-Edicion-Social/research/prueba-publicacion-mcp-2026-10-01/` (RECIBO_PROGRAMACION_v1.json, RECIBO_SEGUIMIENTO_v1.json, INFORME_PRUEBA_v1.md, CASOS_PROGRAMADOS_v1.csv, INVENTARIO_CIERRE_v1.json, assets/, evidencias/, CHANGELOG.md); Framework CHANGELOG y esta bitácora. VIDEO-18 v1 se leyó/reutilizó, sin escribir master/editable/voz/audio ni fuentes estáticas aprobadas.
- **Validación:** lectura MCP posterior confirma 11 casos / 17 proveedores PENDING, copies/medios/orden iguales y sin errores de creación/activación según recibo; JSON/CSV/rutas/enlaces y hashes de copias comprobados. PNG/JPEG RGB, dimensiones y SVG XML válidos. SHA-256 VIDEO-18 coincide antes/después con `7978d638f464ebccd8d68b1cd54e2c939cbc3a9e0acb5a800fd0307f6f2cb960`. P06 DOM readyState4, 1080×1920 y 21,866667s; no nueva escucha humana ni publicación real comprobada.
- **Resultado y valores:** cola activa para 02/10/2026. MCP 09:00–10:40 America/Guayaquil frente a editor 16:00–17:40 con misma zona: +7 h **por confirmar**, sin causa demostrada. Plan Free: previsión de 3 publicaciones restantes solo si los 17 destinos salen y no hay otros posts. Seguimiento ACTIVE verificado, una revisión el 02/10 a las 18:15 Guayaquil; ejecución real pendiente. Mac/Codex activos son requisito de la revisión local, no de la publicación SaaS.
- **Aprendizaje:** programado/PENDING no equivale a publicado. Stories IG/FB ignoran texto/copy al auto publicar (captura P04), por lo que el mensaje visible debe ir en el medio. Varias fotos FB no son carrusel publicitario; Reel IG puede solicitar feed con showReelOnFeed. No inferir éxito por desaparición de la cola ni usar preview como certificación final.
- **Pendiente:** comprobar los 17 destinos, enlaces/IDs y horarios reales el 2 de octubre; resolver diferencia de 7 h, orden/encuadre/copy/audio de salida y cupo real. Monitor no vuelve a publicar ni reprograma. No resultado publicado, eficacia ni ahorro atribuidos antes de evidencia.

### 2026-10-01 — Piloto MCP: Calendario/Listado confirman horas y aíslan anomalía del editor

- **Petición y punto de partida:** completar el cierre documental del piloto real autorizado para mañana y contrastar la diferencia +7 h observada al abrir el editor. Recibo de programación v1 y cola de 11 casos / 17 destinos ya conservados.
- **Cambios y motivo:** nuevo RECIBO_VERIFICACION_HORA_v2.json, DOM/captura del Listado y CSV final v2 con horas MCP/Calendario/Listado/editor separadas. Informe e inventario de cierre v2; recibo/CSV/inventario v1 preservados. Actualización del mismo seguimiento para leer v2, sin segundo monitor, con ACTIVE y una única revisión 02/10/2026 a las 18:15 Guayaquil.
- **Archivos afectados:** research/prueba-publicacion-mcp-2026-10-01/{RECIBO_VERIFICACION_HORA_v2.json,CASOS_PROGRAMADOS_v2.csv,INVENTARIO_CIERRE_v2.json,INFORME_PRUEBA_v1.md,CHANGELOG.md,evidencias/listado-final-dom.txt,evidencias/listado-programado-02-oct.jpg}; CHANGELOG framework y bitácora. Ningún master/editable/voz/audio/arte aprobado modificado.
- **Validación y valores:** las 11 filas del Listado están Pendiente el 02/10 de 09:00–10:40 America/Guayaquil, exactamente como MCP y Calendario; 17 destinos, draft=false y autoPublish=true. Captura muestra borrador de control aparte. CSV de 11 filas / 17 destinos, hashes/copias/rutas/enlaces comprobados; VIDEO-18 SHA-256 intacto. Recibo v1 permanece sin cambios.
- **Resultado y aprendizaje:** la anomalía +7 h (16:00–17:40) se limita al editor individual. Calendario/Listado/MCP sí coinciden; causa del editor por confirmar, sin corrección afirmada. Contrastar varias superficies permite distinguir visualización del editor de la cola programada; ninguna prueba PENDING certifica publicación.
- **Pendiente:** verificar ejecución del seguimiento y publicación real por cada destino, links/IDs/instantes y resultado final; explicar el editor. Mac/Codex activos para revisión local, no requisito de publicación por Metricool. Sin nueva programación, republicación, escucha humana o éxito publicado inferidos.



### 2026-10-01 — Revisión humana 26–30, correcciones 27/30 y auditoría visual de la serie

- **Petición:** usuario aprueba26/28/29, pide retirarDavid y resolver vacío inicial27, quitarAa repetido y recurso descontextualizado30; observar sencillez/másmotion, analizar las30piezas y generar informeHTML con referencias y observaciones escritas, manteniendo variedad.
- **Punto de partida:**27v2/30v2 y piloto cerrado;26v3/28v1/29v2 ahora aprobados expresamente. Recursos/plantillas ya existentes y QA por muestras; no se infiere escucha.
- **Cambios:**27v3 elimina13etiquetas estáticasDAVID copiadas del ejemplo, reorganiza apertura con cuatro formatos de campaña construidos por voz.30v3sustituyeAa por contenido/anuncio/página y fotoartesanía por dos participantes con mismas herramientas, conexiones y foco deelección. Ambos preservan voz,captions originales,mezcla y tomas; nuevas versiones sin aprobación humana todavía. InformeHTML30fichas, comparaciones exactas, galerías,seisreferenciasSVG originales animadas y PNG, paletas/rutas/motion, notaslocales y exportJSON.
- **Motivo:** corregir literalización de ejemplo y apoyo con metáfora débil; desarrollar funciones gráficas en vez de decoración. F1noexigíaDAVID/hueco; F3noautoriza recurso genérico o pérdida de fidelidad. No atribución causal demostrada a perfiles.
- **Archivos afectados:**VIDEO27/30editables,QA/recibos/entrega/CHANGELOG/runs postrevisionv3; aprobaciones/CHANGELOG26/28/29; LOTE-26-30-PRODUCCION/REVISION_USUARIO_2026-10-01_v1.json yMANIFEST_ENTREGAS_REVISION_v1.json; research/auditoria-30-videos-2026-10-01/{auditoria-30-videos-v1/v2.json,inspeccion-30-videos-v1/v2.md,INFORME_VISUAL_30_VIDEOS_v1.html,propuestas,qa-html,RECIBO_CIERRE_INFORME_v1.json,CHANGELOG.md}; bitácora.
- **Validación:**27v3SHAe220de199f039e09584fd3c1d33389230301ad9ed0ec4bfa86acbdc847443d0b,30v3SHA6f294af3cf1e6d087671f7ad8cb5bbb34c0d7674a6dcafc8bb00d2727619c298;62/67muestras y13/9cues revisados porcreador y sombra, metadatos exactosHLG1080×1920/30fps/AAC48kestéreo; mezclaAACcompleta ytresventanasSFX exactas,intactas. Modelo de trabajadores mantiene configuración autorizada. CLI0.8.100→0.8.102 por probe/verificación; separar esa diferencia de motor del piloto. HTML verificado escritorio/móvil,búsqueda,filtros que distinguen aprobado/pendiente,fichas,guardado/reload/exportJSON, sin erroresJS/overflowmóvil; capturas inspeccionadas.
- **Resultado:**27/30v3renderizados disponibles para revisión; aprobados26/28/29intactos.30fichas con29exports seleccionados;VIDEO20solo preproducción/proxy, ningún exporteditado encontrado. Auditmuestrasactuales/previas, no visionado humano continuo. Hallazgos: repeticiónespacial6–10, acumulaciónplacas/gestos11–15, oportunidadesdeidentidad18/19ymovimiento funcional; propuestas diversas, no rediseño de aprobados.
- **Mediciones:**motores27v3=121,539s y30v3=95,468s; runs revisiónregistran918,135s/687,881s respectivamente con comandos/documentación/coordinación incluidos, no atención pura. Auditoría independiente1005,230s, lecturasinicialessinrelojdedicado; raízsinrelojglobalaislado,seconservan tiempos decomandos comoQAHTML9,666s yextracciónantes0,914/3,182s. Procesos solapados no se suman comotiempodelote ni ahorro.
- **Aprendizaje:**copiar lenguaje gráfico, contextualizar todas las etiquetas; vincular cada objeto a frase/función, revisar espacios enmaqueta y desarrollartransformaciones/trazos ligadosal sentido. Algunas piezas requierenjerarquía ymenoscajas; otras másdesarrollo. Ni cantidaddeelementos nichecktécnicodemuestran conexiónconaudiencia.
- **Pendiente:**aprobación27/30v3,escucha/dispositivo/plataforma y rendimiento publicadosporconfirmar; hallazgoshistóricos1–25requierencontrastar exportvigenteantes dereeditar. Prototipos/colores/herramientas son propuestas,noinstalaciones niadopciones automáticas. MantenerF1default,F2/F3experimentales; informe piloto/versiones anteriores intactos.


### 2026-10-01 — Evaluación perceptual asistida y musicalización sin interfaz

- **Petición:** investigar/descargar herramientas para revisar audio real y mejorar musicalización; luego hacer que Codex implemente todos los recursos/opciones por código, fácilmente y sin depender de abrir interfaz.
- **Punto de partida:**11mezclas previas (cinco iniciales/seis alternativas largas), seis músicas y dos referencias; cierre técnico existente sin escucha del agente. Voces/ASR/recursos y preferencias preservados.
- **Cambios:** entornoPythonaislado;STOI/E-STOI,YAMNet/LiteRT y experimentosQwen/GemmaMLX;8controles ciegos. CLIaudio_multimedia condoctor/catalog/prosody/mix/review, curvas/fades/pan/anchura/EQ/carve/ducking/SFXcolas, export/stems, hash/cache/sellos y guards. Dos candidatas53/158,798s con automatización por frase yhook+2,5dB, voz común intacta; piloto21,375s por código. Informe/protocolo/comparador opcional y reglas de próximas ediciones.
- **Motivo:** hacer revisiones internas que reciben ondas y tienen alcance demostrado, impedir que respuestas convincentes de modelos sean aprobaciones, conectar cambios con frases y reutilizar cálculos sin carga de interfaz.
- **Archivos afectados:**Framework-Edicion-Social/scripts/audio_multimedia(.py);AUDIO_EVALUACION_PERCEPTUAL_ASISTIDA.md;dirección/QA/README/CHANGELOG;research/escucha-perceptual-2026-10-01/{scripts,calibracion,modelo,evidencia,fuentes,comparaciones,headless,antes,INFORME.md,index.html,styles.css,app.js,CHANGELOG.md};AGENTSraíz y esta bitácora. Entorno/cache privados nuevos; sin escribirVIDEOmasters/editables/voz original.
- **Validación:**STOI/E-STOI444ventanas sobre11mezclas y103 sobre candidatas; falla sensibilidadSFXglobal (.0246<.05) conservada y capacidad excluida. YAMNet5controlesPASS/26señales iniciales+2candidatas. Qwen omitió cama suave/efectos;Gemma inventó habla en silencio/música, descartado en esta configuración con inspección de entrada. AAC48kestéreo−18,01LUFS/TP−5,74y−5,95;correlaciónPCM≥.9999876,errorvoz escrita≤2.80e−8,monoΔ≤.002dB.17casos por códigoPASS(incluye cache,fuente alterada,hook ausente,identidades repetidas,cue fuera,parámetro inválido,SFXrechazado ypreservación de versión). Nativeplayerprobado separadamente según reciboUI; no oído humano atribuido.
- **Resultado:** implementación/revisión disponible paraCodexsininterfaz; evaluación perceptual asistida parcial y candidatas comparables, no aprobación estética. Ventanas se cruzan con contexto antes de decidir; biblioteca mantiene candidatos/aprobaciones y bloqueaSFXrechazados.
- **Medición:**CLIactual17casos; mix21,375s+review3,72s→reutilización0,67s; review53s3,19→0,64s y158,798s7,66→0,69s. Una ejecución por condición en esteMac, con arranquePython; no rapidez/equivalencia general ni ahorro de todo el flujo demostrados. PrimerCLI/pruebas conservados al corregir catálogo.
- **Aprendizaje:** calibrar cada capacidad antes de delegarle juicio; un detector básico validado puede ser útil cuando un modelo grande inventa fuentes. Métricas altas no prueban contraste/atención ni justifican apagar toda la música. No afirmar límite absoluto de mejora ni oído profesional por herramientas.
- **Pendiente:** percepción de timbre/carácter/naturalidad/SFX,fatiga,dispositivo y elección de candidatas por confirmar. Verificar de nuevo elMP4exacto cuando se integre audio en un nuevoVIDEO; sin publicación ni adopción global de nuevos recursos. Limpieza especializada permanece solo a solicitud.

Cierre de esta investigación: `research/escucha-perceptual-2026-10-01/CIERRE.json` y `evidencia/ui.json` conservan alcance/verificación.76JSON inspeccionados,23enlaces/7rutasHTTP200 y sintaxisPython/JS válidos; ambas comparaciones reproducen/cambian cinco capas conservando posición y quedan pausadas. Esto comprueba funcionamiento del comparador opcional, no escucha; laCLI17casos no requiere navegador.


### 2026-10-01 — VIDEO20 faltante: primera edición local y serie con30exports

- **Petición y punto de partida:** «Falta el20? Si falta deberíamos buscar o procesarlo porque ya tienes todos los lotes». Búsqueda global confirma solo preproducción/proxy, sin editable/exportfinal. Se conserva esa historia; no era una entrega perdida aprobada.
- **Cambios y motivo:** reutilizada ingesta16–20; revisiónASR acotada/señal/markers corrige rango viejo que incluía marcador y colas. Cinco rangos refinados y748frames/24.933s. Flujo1@1.0.0predeterminado, fuera delpiloto26–30. Recibo de inicio con30documentos/hashes, ficha/tableroT20Jardín deideas y maquetasantesdelmontaje. Construcciónorgánica semilla/raíces/dosplantas precios/flor, presentadorenarcogrande,12captioncues semánticos1–2líneas. Recursoslentes previos preservados sinuso; no diferencia de calidad o dato ficticio añadido aejemplo1000/100.
- **Voz y SFX:** única restauraciónRNNoise específicamente autorizada16–20, contexto76s48k antesdecortes,960samples compensados y+4dBconstante. Original/recetas/bypass/diferencia conservados. Prosodia/ritmo/pitch comoestimaciones por frase, noemocionesdemostradas. Cuatroeventos/tresfuentesdistintas, hookSFX obligatorio comprobado, tick situadoenpausa; nivel/calibración porcanales/mascaramiento documentados. Escucha/naturalidad/phonemes/audibilidad `por confirmar`; strictingesthumangatefalsebajoexcepciónexpresa, noapprovedtake inventado.
- **QA y correcciones:** primeras pruebas detectan cajas tipográficas/entradaSVG y tick en sílaba; se corrigen antesdelprimer render. V1motorcompleta peroQAexacta encuentra flash0/máscara rectangular no vistos enproxy. V2corrige estadoCSSinicial ycontratotemporal deSVGmáscara; arte/voz/captions intactos. SmokeHDR3s@5fps(5.359smotor) prueba soloarranque/arco. Finalv2: layout0errores, guardtexto/SFX, decodificación/meta PASS,149fotogramas exactos en5contactos realmenteinspeccionados,12cues/8escenas ycosturas/cierre. SHA95670d947f31b2a8f1fe4a5a578872ba66f1ab63b6d55568b754fc4e11a2a830,HLG10bit1080×1920/30fps/AAC48kestéreo. Mezcla -17.0LUFS/-2.9dBTP; PCMdecodificadov1/v2idéntico y4eventosverificados. ReferenciaAACindependiente no bit-exacta: causa porconfirmar/corr.999988/residual-66.17dB, investigações conservadas, sinfalsoPASSdeparidad. Esto no certifica escucha/emoções ni UIreal.
- **Archivos afectados:** VIDEO20/{RECIBO_INICIO,RECIBO_ENTREGA,manifest,source/rangosrefinados,editable-hyperframes-video-20,qa/preparation,qa-smoke-hdr-v1,QA_FIDELIDAD_PLANTILLA,caption-decision,assets-ledger,entrega/v1–v2,CHANGELOG,workflow-runs/flujo1-recuperacion-v1}; research/auditoria-30-videos-2026-10-01/{auditoria-30-videos-v3.json,INFORME_VISUAL_30_VIDEOS_v2.html,build_report_v2.py,qa_report_v2.cjs,qa-html-v2 yfallidos,RECIBO_CIERRE_INFORME_v2.json,CHANGELOG}; Framework/QA_HDR_COMPOSICION.md/CHANGELOG y referenciaaditiva enESTANDAR_QA_PREAPROBACION deSerie; productionboardliberado ybitácora.
- **Resultado e informe:** ahora30fichas/30exportslocales.20v2candidato pendiente revisiónhumana; resto de29juicios/cobertura y rendersaprobadosintactos. Informe nuevo mantieneseispropuestas, galerías/observacioneslocales, clave de notascompatibles, búsqueda/filtros/descarga; noedita aprobadosnipublica. QAHTML desktop1440/móvil390,0erroresJS/0imágenesrotas trasdecodeawait,0overflowdocumentoymodal. Primeros intentos HTML detectan cargaoffscreenpendiente ygaleríaqueforzabaancho; fuentes/capturaspreservadas, corregidos ypixelsnuevosinspeccionados.
- **Mediciones y límites:** comandosrendersv1=148.222s/v2=143.396s; postrender/boundariesv2 yHTMLPASS6.925s enrecibos. Relojdefasesincluyedocumentación/autoría/depuración,algunosbloquesamplios einformeintegrado enQApost; búsqueda/lecturasprevias sinmedicióndedicada. No suma de tiempos como ahorro ni causalidad deperfil/modelo. Errores deentorno/rutas/primerbuild/parserJSONincluyendoguardarrecibov2después delanzar render yschemaeventos quedan detallados; no sefalseafecha/evidenciadearranque.
- **Aprendizaje:** comprobarcapasHDR yestado0conmotorrealantesdeexportcompletoal crear/cambiargeometría/lifecycle; masks SVG temporales yestado inicialCSS ya tienenrecetaverificada0.8.102, sincambiarQAcomún/perfiles/defaults. Inspecciónexactaevidenciaotroresultadoqueproxy. EnHTML mediroverflowdelmodalabierto yesperardecodificación de imágenes. No obviar límites de herramientasdiagnósticas.
- **Pendiente:** aprobación/escucha/naturalidad/audibilidad ysincronía fina de20, destinosrealesydatosdeaudiência; diagnósticoparidadAACindependiente solo si se necesita confirmar ese emulador. Selección editorialreal sigue provisional, nohumaningest-ready. Sinpublicación ni nuevasaprobacionesinferidas.

- **Cierre de medición VIDEO20, 2026-10-01:** reloj cerrado de 07:00:50 a 08:36:23 UTC, 5733.195 s (95.553 min). Incluye autoría, revisión, depuración, informe, documentación y compacciones de contexto; no equivale a tiempo activo continuo ni al render. La búsqueda previa al primer start no se midió. Se guardaron `VIDEO-20/workflow-runs/flujo1-recuperacion-v1/timing-summary-v1.json`, `report-v1.json` y `RECIBO_TIEMPOS_CIERRE_VIDEO20_v1.json`. Hash del MP4 v2 y del informe v2 comprobados sin cambios; informe HTTP 200. Continúan pendientes la escucha y la aprobación humanas. No se atribuyen ahorros ni rendimiento causal al flujo o modelo.


### 2026-10-01 — Archivo de investigación y control de publicación de Negocio Aumentado

- **Petición:** guardar toda la investigación, inventariar el material publicable, crear fichas de subida y resultados, preparar miniaturas y copies, mantener medición por MCP y revisar todo desde un HTML dinámico.
- **Punto de partida:** marca editorial elegida «Negocio Aumentado — IA para crecer y vender»; cuatro redes conectadas a Metricool como «Silent Run Ecuador», brand6177067. Existían 54 piezas estáticas/108 versiones y una serie de30videos con29exports al inicio. El piloto autorizado tenía11entradas para17destinos el2deoctubre, más un borrador privado. Durante esta revisión otra tarea terminó VIDEO20v2; ese nuevo estado se incorporó preservando los inventarios anteriores.
- **Cambios y motivo:** creado CONTROL-PUBLICACION con investigación trazable, catálogo físico,84fichas de pieza/803de archivo, auditoría estática,30portadas verticales editables, copies propuestos por red, alt por imagen, propuesta local6semanas/318destinos, servidor HTML local, revisiones con autor declarado/hashes/historial e importador de IDs/métricas. Recursos/QA/fuentes y28exports/pilotos de8familias adicionales se distinguen de las piezas de la serie para no publicar variantes o atribuir otras marcas por accidente.
- **Investigación conservada:**94hallazgos/60fuentes; precios/planes/límites y comparación Metricool/Zernio/Buffer/Meta propio; diferencias MCP/API; subida/bulk/programación; edición por UUID/ID y límites después de publicación; analítica/SEO/GEO; campos/miniaturas por red. Snapshots de9herramientasMCP, Swagger,228rutas de campos/34modelos y491métricas con62deprecadas. Fechas, fuentes y estados porconfirmar quedan en cada evidencia; un catálogo no certifica que cada opción funcione en estas cuentas.
- **Material y propuestas:**252PNG+252SVG estáticos/108manifests, revisión de texto/integridad y alt individual. Cinco hallazgos confirmados, dos posibles y uno descartado;7decisiones humanas pendientes. C06/C10 tienen propuestas de copy independientes. Obstrucciones de rostro C01/C07/C11 sólo en variantes fotográficas.30portadasv2 con foto real, SVG/JPG/PNG y recortes simulados9:16/3:4/1:1; v1 conservada.14títulos fuera de ancho se corrigieron y rostros/titulares se protegieron en recortes. VIDEO20nuevo: SHA95670d947f31b2a8f1fe4a5a578872ba66f1ab63b6d55568b754fc4e11a2a830,24.933s; fallback exportv2 a12.716s. La caché anterior sin binding se preservó y se vinculó la nueva a fuente/hash/receta. No se editaron MP4/voz originales desde este control.
- **Seguimiento y automatización:** registro por destino con IDMetricool/UUID/historial, ID/enlace nativo y fecha real sólo con evidencia. Hitos24/48/72h,7/14/30d y meses calendario, con edad/retraso reales; vacío/null/ausente/no disponible≠cero. Las consultas de publicaciones actuales no devolvieron filas.113filas de evolución sin contrato de columnas se guardan intactas sin interpretar. Consultas limitadas verificaron4campos y9observaciones de SilentRun, sin atribución automática a NegocioAumentado. Importador acotado exige alternativa de un campo/rowAdapter local; publicaciones no vacías aún por probar. Heartbeat activo diario10:45Ecuador de lectura remota/registro local, con primera ejecución automática sin confirmar; exige computador/Codex/conexión disponibles. Se conserva el monitor independiente del piloto2oct18:15; no se reprogramó ni publicó el lote nuevo.
- **Archivos afectados:**CONTROL-PUBLICACION/{index.html,control.css,control.js,GUIA-OPERATIVA.html,CHANGELOG.md,INVESTIGACION,AUDITORIA-ESTATICA,OTROS-MATERIALES,VIDEOS,PORTADAS,FICHAS,FICHAS-ARCHIVOS,data,SEGUIMIENTO,REVISIONES,HISTORIAL,QA,scripts,PLAN-6-SEMANAS-PROPUESTA.csv}; esta bitácora y configuración de la rutina enCodex. No se cambiaron cuentas, destinos reales del piloto ni fuentes aprobadas para resolver metadatos.
- **Validación:**27comprobaciones del HTML en1440px/390px,0erroresJS/0respuestas fallidas/0desbordamiento. Rehash755archivos únicos,724fichas con SHA y coincidencia84fichas/catálogo;318destinos sin colisiones red/hora niIDs inventados. Fuentes estáticas:612hashes comprobados sin cambios según recibo especializado.17pruebas del importador y guardado/historial/hash de versión seleccionada en directorio temporal; ninguna revisión de usuario registrada por esas pruebas. Auditoría independiente detectó que el visor prestaba estado/hash de la versión preferida a otra seleccionada; se corrigió y verificó. Los recibos delimitan QA local, inspección visual y datos reales; no acreditan escucha, aprobación humana ni aceptación de redes.
- **Resultado:** archivo de investigación y sistema de control preparados para revisión.30exports locales actuales,10aprobaciones vinculadas al hash seleccionado; otras aprobaciones históricas requieren comprobar alcance, sin revocarlas. Más de13.000medios físicos inventariados,803fichas activas y propuestas de318destinos del5octal15nov, todavía locales. La identidad conectada sigue por alinear. IDs/métricas del piloto conservados por separado; ninguna publicación real inferida.
- **Aprendizaje:** separar pieza, versión y destino; conservar UUID e historial de ID; vincular decisiones al hash elegido; no convertir desaparición de cola en publicación ni interpretar arrays por orden supuesto. La aprobación del MP4 no aprueba una portada/copy nuevos. Capturas de feed son simulaciones, elegibilidad de miniaturas y HDR/HEVC se deben comprobar en la red real.
- **Pendiente:** revisión humana de30portadas/copies,VIDEO20,7hallazgos, elección de variantes/fechas, CTA y stickers; alineación pública de marca; elegibilidad Shorts/TikTok; resultado real del piloto/compatibilidad medios/permisos; carga/alojamiento de medios y programación posterior. Los archivos locales no sonURLs remotas. Escucha y aprobación humanas siguen porconfirmar donde no hay evidencia; ningún sistema propio Meta se construyó en esta petición.

## 2026-10-01 — Aprobación explícita de VIDEO20 v2

- **Petición y punto de partida:** el usuario respondió «Aprobado» a la entrega de VIDEO20 HLG v2, cuyo estado era candidato local pendiente de revisión. Se registra la aprobación de esa versión exacta.
- **Cambios y motivo:** se creó `VIDEO-20/APROBACION_VIDEO_20_V2.json` con el mensaje, contexto, fecha de registro, archivo y SHA-256; se actualizó únicamente el estado editorial del manifest. El manifest anterior quedó en `qa-approval-v2/before-user-approval-final/`. El informe incorpora la aprobación mediante `auditoria-30-videos-v4.json`, `build_report_v3.py` e `INFORME_VISUAL_30_VIDEOS_v3.html`; sus versiones previas y recibos permanecen intactos.
- **Archivos y validación:** changelogs de VIDEO20 y del informe actualizados; cierre en `research/auditoria-30-videos-2026-10-01/RECIBO_CIERRE_INFORME_v3.json`. Hash del MP4 comprobado sin cambios: `95670d947f31b2a8f1fe4a5a578872ba66f1ab63b6d55568b754fc4e11a2a830`. Las otras 29 fichas no cambiaron; la clave de notas se conserva. Verificación del estado y filtros en navegador aislado: PASS, 4.427 s, 30 fichas, sin errores JS ni desbordamiento del modal móvil; captura del estado aprobado inspeccionada. No se repitió el render ni el QA de los medios, porque sólo cambió documentación y estado.
- **Resultado y aprendizaje:** VIDEO20 v2 aprobado por el usuario y protegido para conservarlo. Vincular una aprobación al archivo y hash evita confundir versiones; el mensaje no certifica escucha o visionado completos que el usuario no haya descrito.
- **Pendiente y límites:** selección humana estricta de toma/pista y previews reales de plataformas conservan su alcance previo; publicación sin autorización, otras aprobaciones y rendimiento de audiencia no se infieren. La aprobación de VIDEO20 no aprueba las propuestas del informe.


### 2026-10-01 — Rotación editorial propuesta sin renombrar identidad de origen

- **Petición:** evaluar alternar los videos grabados por lotes de cinco para variar vestimenta, conservar congruencia con posts/carruseles/historias y distinguir número de creación, revisión y número de publicación.
- **Punto de partida:** control local con84piezas/318destinos y orden de videos01–30 en seis semanas; aún sin programación del lote nuevo. Se consultaron fichas/captions/textos existentes, planes editoriales/comerciales y tres láminas de portadas. La inspección visual muestra que01–10 parecen compartir camiseta verde agua, aunque pertenezcan a dos lotes distintos. Se usan cinco grupos de prenda visibles; esto no verifica todas las escenas ni fechas reales de grabación.
- **Cambios y motivo:** guardada una segunda alternativa por tema y prenda, con seis bloques semanales,30relaciones video-estático y24historias complementarias. Comparador interactivo de orden original/uno por lote/dos por lote/rotación propuesta, vista cronológica o reciente primero, tabla buscable de84correspondencias y CSV318destinos. Mantiene la propuesta actual como base para evitar aplicar una consulta como decisión de publicación.
- **Orden propuesto de videos:** S1=01,21,06,11,28;S2=04,15,10,19,27;S3=05,13,08,17,22;S4=09,12,23,29,24;S5=18,14,25,02,20;S6=03,26,07,16,30. Los grupos de vestimenta no se repiten en vecinos de esta secuencia. Conteo editorial sobre las portadas, no resultado de audiencia ni aprobación del orden.
- **Identificación:** IDoriginal permanente; versión/hash por separado; ordinal por formatoPV/PC/PI/PH y global de pieza lógica en esta versión del plan. EjemploVIDEO02→PV024, revisiónv3; C01→PC003. Semanas de creación y publicación se mantienen separadas. Cada destino conserva alias de ubicación y espacio para IDs/UUID/nativos; el video reutilizado como historia no recibe otro H. Los nombres de entrega son propuestas y no se renombraron/copiaron MP4/PNG/SVG originales.
- **Archivos afectados:**CONTROL-PUBLICACION/{scripts/proponer_rotacion.py,scripts/rotacion-vista.html,scripts/qa_rotacion.cjs,ROTACION-PROPUESTA-v1/{index.html,propuesta.json,MAPA-84-PIEZAS.csv,PLAN-318-DESTINOS.csv,RECIBO-QA-v1.json,capturasQA,HISTORIAL-QA-antes-decode},index.html,HISTORIAL/ROTACION-PROPUESTA-v1/index-base.html,CHANGELOG.md}; esta bitácora. Se agregó un acceso a la alternativa en el tablero.
- **Validación:**84IDs únicos/todas las piezas base,30videos únicos y318ubicaciones sin colisiones por red/hora.24comprobaciones HTML en escritorio1440/móvil390 yfile standalone, sin erroresJS/HTTP/desbordamiento.14previews iniciales y30de video se decodificaron antes de capturar; las primeras capturas con lazyload incompleto se conservaron y la evidencia se corrigió. SHA decontrol.json, índice de fichas, CSVcalendario base, registro de seguimiento ycatálogo deportadas coincide con el recibo de cierre previo. Ni fuentes ni calendario actual ni Metricool se cambiaron. No escucha/revisión completa de MP4 atribuida.
- **Resultado:** propuesta visual revisable, con fuentes y trazabilidad. Alternar únicamente números de lote no basta cuando dos lotes comparten prenda. Las relaciones editoriales nuevas son inferencias explícitas y no se presentan como emparejamientos originales aprobados. Los textos/captions consultados no mostraron referencia explícita a «video anterior»; no equivale a confirmar todos los overlays/cues de cada export.
- **Aprendizaje:** mantener criterio temático por semana y variar la prenda entre videos; no confundir ingesta, vestimenta, categoría, orden de creación, revisión y ordinal de publicación. Cambiar orden no exige reescribir todas las piezas; revisar dependencias temporales/comerciales y mover apoyos pertinentes.
- **Pendiente:** revisión de los bloques/relaciones y selección del plan antes de aplicarlo. Resolver I09/H17, atención real de CTA, promesa «mañana» en copyH01 si se usa y hallazgos/stickers anteriores; comprobar dependencias visibles/habladas del export exacto. Confirmar fechas finales y luego actualizar el control/los UUID-ID reales porMCP. Sin reprogramación, publicación ni aprobación nueva inferidas.


### 2026-10-01 — Calendario de rotación aplicado y revisión visual con imágenes incorporadas

- **Petición:** el usuario aceptó la propuesta del calendario por tema y vestimenta y pidió verla aplicada en un HTML con imágenes de todas las publicaciones, miniaturas que identifiquen los videos y una forma de enviar cambios.
- **Punto de partida:** ROTACION-PROPUESTA-v1 era una alternativa sin aplicar; el catálogo y las84fichas todavía mantenían las fechas originales. Las propuestas, materiales y el piloto remoto se conservaron.
- **Cambios y motivo:** se aplicaron localmente las84correspondencias y318fechas/ubicaciones del5-oct al15-nov. Las seis semanas siguen un tema; el orden de videos es01/21/06/11/28,04/15/10/19/27,05/13/08/17/22,09/12/23/29/24,18/14/25/02/20,03/26/07/16/30. Se guardan semana de creación y campos publication separados, ordinalPV/PC/PI/PH, alias por ubicación e identidad/versiones originales. El calendario principal incorpora84miniaturas y enlaza CALENDARIO-VISUAL/index.html, con186imágenes exactas incorporadas alHTML, todas las láminas de carrusel, historias, portadas, simulación de feed y enlaces/reproductor delMP4 seleccionado.
- **Revisión y controles:** elHTML ofrece notas, copy por red y solicitud de fecha/hora por ubicación. Guardar solicitud conserva en el navegador; descargar generaJSON conIDoriginal, ordinal, plan, versión y firma; guardar en el proyecto usa el formulario local existente yREVISIONES con historial. Una solicitud no cambia automáticamente la fecha base ni la cola remota. Las pruebas escribieron únicamente en un directorioQA temporal, sin decisiones reales del usuario. Cada nueva ficha abre desde su imagen superior. ABRIR-CALENDARIO.command facilita iniciar/reutilizar el servidor local.
- **Archivos y conservación:** data/control.json,84FICHAS,PLAN-6-SEMANAS-ACTUAL.csv y CSVcompatible anterior, index/controlJS/CSS,GUIA-OPERATIVA, dos scripts nuevos de aplicación/QA y plantillaHTML. Versiones anteriores en HISTORIAL/aplicacion-rotacion-*; ROTACION-PROPUESTA-v1 no se reescribe. Registro de métricas, catálogo de portadas e índice de fichas de archivo mantienen sus hashes; no se renombraron ni editaron medios ni se llamaron herramientas de mutación remota. Se vinculó la aprobación explícita ya existente deVIDEO20v2 tras comprobar suhash; portada/copy siguen independientes.
- **Validación y resultado:**26comprobaciones de navegadorPASS en escritorio/móvil yHTMLdirecto,186imágenes decodificadas, carruselC01 completo,84fichas coincidentes,84alias de pieza y318alias de ubicación únicos, cero colisiones porred/hora, cero erroresJS/respuestasHTTPfallidas. Capturas de escritorio y ficha móvil inspeccionadas; launcher y script comprobados sintácticamente. El primer reintento delQA encontró datos viejos en su propio fixture temporal; se conservaron recibos y se aisló el estado antes de volver a verificar. No fue un fallo de la programación ni una decisión del usuario.
- **Aprendizaje:** aplicar una propuesta exige separar identidad de origen, revisión del medio, posición editorial y estado remoto; incorporar imágenes alHTML permite revisar sin depender del servidor para verlas. Conservar un archivoJSON de solicitudes permite compartir cambios sin perder sus vínculos.
- **Pendiente y alcance:** revisar material, portadas/copies, CTA, widgets e identidad pública antes de cargar el lote. Horarios operativos sin mejor-hora medida. LosMP4 requieren sus archivos originales y soporte de códec del navegador; esteQA no certifica escucha/reproducción completas, previews reales ni aceptación de redes. El piloto y su monitor del2-oct18:15 permanecen independientes. El orden local está aprobado por el mensaje del usuario; esa aceptación no aprueba automáticamente cada activo ni ejecuta programación remota.

### 2026-10-01 — Entrega a Muse Code para programación mediante MCP

- **Petición:** preparar instrucciones y un archivo de continuidad para cargar todo el lote desde Muse por MCP, porque el usuario indicó que agotó su cuota aquí y no recordaba el comando del cliente.
- **Punto de partida:** calendario de rotación ya aplicado localmente,84piezas/318destinos del5-oct al15-nov; lote editorial todavía sin programación remota. Se encontró Muse Code1.4.0 instalado como muse y sin servidores MCP en los ajustes inspeccionados. Piloto, monitor independiente y registro de seguimiento se mantienen.
- **Cambios y motivo:** se creó CONTROL-PUBLICACION/ENTREGA-MUSE-METRICOOL con guíaHTML, PROMPT-PARA-MUSE, configuraciónOAuth de ejemplo, helper de fusión con backup privado, lanzador y generador de manifiestos.186medios únicos seleccionados suman486.445.785bytes:30exports,126láminas estáticas y30portadas. DESTINOS-318 incluye copies/alt/opciones/fechas/referencias y fingerprint, noIDs ni URLs inventados. La carga usa el calendario vigente y deduplica medios porSHA; las solicitudesHTML se adjuntan sin aplicarse automáticamente. El prompt contempla transporte real de archivos, validación de formato, comprobación decola, IDs/UUIDs, reanudación y mantenimiento por importador sin rebootstrap.
- **Investigación y alcance:** la compatibilidad Muse/Metricool se infiere del soporte documentado deHTTP/OAuth yCLI local; no se hizo prueba conjunta ni login. Endpoint oficial ai.metricool.com/mcp. La documentación oficial actual indica20publicaciones efectivas/mes enFree, con redacción distinta de la páginaMCP sobre capacidad decola; se conserva investigación anterior comohistorial y se añade corrección fechada. El lote tiene210destinos enoctubre y108ennoviembre, además delpiloto. Plan efectivo y contrato deupload delMCP deMuse permanecen por confirmar. MCP no eleva cuotas; API con token exigeAdvanced/Custom.
- **Archivos afectados:** paquete nuevo y enlace enGUIA-OPERATIVA.html; manifiestos anteriores y documentación previa preservados enHISTORIAL delpaquete. Catálogo aplicado, fichas, medios, cola remota y registro de seguimiento no se modificaron.
- **Validación:**23comprobaciones localesPASS sobre fusión/check/idempotencia/backup/ambigüedad, manifiestos y sintaxis. Lanzador ejecutado únicamente con un cliente simulado y ajustes temporales: verificó login antes de abrir elworkspace con la orden correcta, conservando políticas delcliente.6comprobaciones de navegadorPASS para guíaHTML directa, escritorio1280×1000/móvil390×844, enlaces, copia/selección y ausencia de errores/desbordamiento. Capturas realmente inspeccionadas. Generador verificóSHA de medios y conserva hashes de catálogo/plan. Recibo enENTREGA-MUSE-METRICOOL/RECIBO-VALIDACION.json.
- **Resultado y aprendizaje:** paquete concreto y revisable para continuar en otro cliente sin depender del historial dechat. ConexiónMCP, transferencia de medios y cupo de publicación son requisitos distintos; descubrir una interfaz compatible no acredita aceptación de archivos ni programación. Autorización para programar no equivale a revisión humana de cada medio.
- **Pendiente:** el usuario debe ejecutar el lanzador y autorizarMetricool enMuse; el agente comprobará capacidad, transporte y permisos, resolverá impedimentos concretos y guardará recibos antes de declarar la cola terminada. No se inicióMuse real, ni OAuth, ni carga, ni programación, ni contratación; no se atribuye ahorro de tiempo, escucha, aprobación nueva ni rendimiento.

### 2026-10-03 — YouTube prioriza originalidad en Shorts

- **Petición:** ejecutar el radar diario, contrastar fuentes oficiales recientes y registrar únicamente cambios materiales aplicables al video vertical de tecnología e IA.
- **Punto de partida:** la última observación verificable era del 2026-10-01 y no existía archivo del 2026-10-02. Las novedades de Made on YouTube y Content ID ya estaban deduplicadas; el proyecto conserva talking-head propio, recursos editoriales y una política de no generar derivados sin diferencia material.
- **Cambios:** se añadió `research/observations/2026-10-03.json` con un `platform_change`; `sources/catalog.json` incorporó `YOUTUBE_SHORTS_ORIGINAL_CONTENT_2026`; y el changelog especializado registró el hallazgo. La fuente oficial anuncia mayor prioridad para contenido original y menor distribución de reuploads o agregaciones sin aporte significativo.
- **Motivo:** el anuncio es relevante para la estrategia de Shorts y el uso de material de terceros, aunque no modifica el perfil técnico ni prueba una mejora de retención.
- **Archivos afectados:** `Framework-Edicion-Social/research/observations/2026-10-03.json`, `Framework-Edicion-Social/sources/catalog.json`, `Framework-Edicion-Social/CHANGELOG.md` y esta bitácora. No se modificaron reglas, perfiles, experimentos, editables ni renders.
- **Validación:** se contrastó la publicación oficial de YouTube fechada el 2026-10-01 con las fuentes y observaciones existentes; se revisaron TikTok y Meta sin encontrar otro cambio aplicable; se comparó `platforms/catalog.json` y no se identificó delta técnico. `scripts/validate_framework.py` terminó correctamente con 26 fuentes y 10 observaciones.
- **Resultado:** el framework conserva su flujo: voz, análisis, narrativa y edición propios; cualquier clip de terceros exige procedencia y aporte sustancial documentado. No se promueve una regla creativa, no se llama viral a la señal y no se genera otra versión del video.
- **Aprendizaje:** una actualización de recomendación puede cambiar la disciplina de procedencia y autoría sin justificar un nuevo render ni una modificación de códec, layout o safe zones.
- **Pendiente:** observar cómo YouTube aplica el criterio, verificar cualquier aviso disponible en la cuenta y reunir métricas propias antes de inferir efecto. La ejecución faltante del 2026-10-02 permanece como hueco explícito y no se reconstruye como si hubiera ocurrido.

### 2026-10-03 — Últimas variantes fotográficas en el plan y recuperación del visor

- **Petición y punto de partida:** el usuario detectó carruseles y posts anteriores y después informó que el enlace no abría. Existían las versiones fotográficas, pero el catálogo seleccionaba originales; la biblioteca también ignoraba el fallback seleccionado. La selección comenzó el 1-oct y el cierre continúa con comprobaciones tardías.
- **Cambios y motivo:** se seleccionan 12 carruseles y 18 posts fotográficos (102 PNG), conservando originales y aprobación histórica por separado. Catálogo, 30 fichas, referencias del plan, alt, calendario y manifiestos Muse coinciden. Registro explícito de selección y guard del bootstrap evitan volver al estado inicial.
- **Apertura:** se comprueba connection refused y ausencia de listener en 8768; se reinicia el servidor local. La vista pasa de 151 MB incorporados a 0,8 MB de estructura con carga de archivos al necesitarlos. calendario-completo.html conserva las 186 imágenes para una copia autónoma.
- **Archivos:** CONTROL-PUBLICACION/data/selecciones-editoriales.json, control.json, FICHAS, scripts/sincronizar_selecciones.py, construir_control.py, aplicar_rotacion.py, calendario-vista.html, control.js, plan-aplicado.json, guías y ENTREGA-MUSE-METRICOOL; historial y recibos conservados.
- **Validación y resultado:** 149 comprobaciones iniciales de referencias/hashes y 109 de las dos vistas/HTTP/sintaxis. Todas las láminas actuales están referenciadas; 318 horarios, orden, copies, videos e historias quedan iguales. 186 activos del paquete suman 573.214.328 bytes. No se regeneran medios ni se programa el lote.
- **Aprendizaje y pendiente:** versión elegida y aprobación son registros distintos. La apertura automática local fue rechazada por política de URL y no se eludió; la inspección visual del navegador queda pendiente del usuario. Se conservan los hallazgos anteriores, sin afirmar nueva aprobación ni auditoría completa.

### 2026-10-03 — Piloto MCP confirmado por proveedor y registro tardío de métricas

- **Petición y punto de partida:** ejecutar los avisos de seguimiento y comprobar el piloto del 2-oct sin mutaciones remotas. No había recibo de ejecución posterior al 1-oct; las 18 fichas por destino tenían 17 casos pendientes y 1 borrador.
- **Lectura y evidencia:** 12 recetas analíticas con catálogos actuales; evolution exclusivamente IGEV01/FBEV03/TKEV01/YTEV01, un campo por llamada y adapter verificado. Ventana reciente 4-sep–3-oct, con offset/from/to/capturas reales. Consulta de próximos 60 días vacía, sin declarar cola global completa. La lectura específica del 2-oct devuelve las 11 entradas originales con 17 proveedores PUBLISHED e IDs/URLs por ID/UUID.
- **Resultado:** 17 destinos del piloto confirmados según proveedor; copies y medios ordenados del planner coinciden. Dos recibos se importan con ruta absoluta y se relee estado: 187 observaciones de Silent Run Ecuador, 130 filas posicionales pendientes y 17 bindings explícitos. Identidad editorial Negocio Aumentado conservada sin atribución automática.
- **Límites:** 0 horas reales verificadas; no se convierte publicationDate planificada en hora real. No se interpretan columnas de 17 filas nuevas ni las 113 evolution originales. Render/carrusel nativo y disponibilidad de Stories pendientes; métricas desconocidas nunca son cero. Captura tardía no acredita lectura exacta del hito ni ejecución del día omitido.
- **Archivos y validación:** recibos/snapshots en SEGUIMIENTO/entradas y registro; RECIBO_RESULTADOS_20261004T022148000Z_v3.json y CSV en Framework-Edicion-Social/research/prueba-publicacion-mcp-2026-10-01. Importador con IDs/URLs explícitos, estado 17 publicados/1 borrador/0 horas y protección de 113 filas opacas validados. Guías, política local y changelogs actualizados bajo locks. El contrato mantiene el adaptador acotado y añade evidencia de las nuevas filas de publicación sin activar su interpretación.
- **Aprendizaje y pendiente:** un estado PUBLISHED con vínculo del proveedor demuestra más que ausencia de cola; datos analíticos posicionales todavía requieren contrato explícito. La web requirió inicio de sesión. No se publica, sube, edita, reprograma, borra, renombra ni envía mensajes externos; monitor independiente original sin cambios.

### 2026-10-06 — Recuperación del radar semanal 2026-W41

- **Petición:** ejecutar el radar técnico diario y conservar el informe semanal, decisiones y experimentos sin inventar métricas, tendencias ni ejecuciones ausentes.
- **Punto de partida:** la última observación era del 2026-10-03; no existían registros del 4 ni 5 de octubre y tampoco el informe previsto para el lunes 5. El registro de experimentos seguía vacío y `HOOK_UNDERSTANDABLE_FIRST_FRAME` llegaba a revisión el 2026-10-07.
- **Cambios:** se creó `research/observations/2026-10-06.json` como `no_material_change` y se recuperó `research/reports/2026-W41.md`, marcado explícitamente como tardío. El changelog especializado registra la discontinuidad, el cambio oficial de originalidad ya observado y una sola propuesta de prueba de hook pendiente de aprobación.
- **Motivo:** restaurar la continuidad documental útil sin fingir que el radar se ejecutó en fechas donde no existe evidencia.
- **Archivos afectados:** `Framework-Edicion-Social/research/observations/2026-10-06.json`, `Framework-Edicion-Social/research/reports/2026-W41.md`, `Framework-Edicion-Social/CHANGELOG.md` y esta bitácora. No se modificaron videos, editables, perfiles, reglas ni experimentos registrados.
- **Validación:** se reconsultaron fuentes oficiales de YouTube, TikTok y Meta; la novedad publicitaria de TikTok del 2026-10-05 se separó del alcance orgánico. Se revisaron reglas próximas y el registro vacío de experimentos. `scripts/validate_framework.py` terminó correctamente con 26 fuentes y 11 observaciones.
- **Resultado:** un cambio oficial consolidado, cero patrones observados y un experimento opcional de hooks aún no autorizado. La hipótesis de primer fotograma no se promueve automáticamente.
- **Aprendizaje:** recuperar un informe atrasado exige declarar el retraso y los días sin observación; una fuente de publicidad no se convierte en regla orgánica por proximidad temática.
- **Pendiente:** decidir antes o durante la revisión del 2026-10-07 si se registra la prueba de hook; investigar la causa de las ejecuciones faltantes del 2, 4 y 5 de octubre si la discontinuidad vuelve a aparecer.

### 2026-10-06 — Reducción de la entrega Windows existente para videos nuevos

- **Petición:** eliminar de la entrega ya creada los trabajos anteriores para evitar duplicación de espacio, conservando plantillas, estilos y una memoria que permita continuar editando. No crear otra entrega ni modificar el framework/flujo Mac.
- **Punto de partida:** entrega v1 de aproximadamente 18,1 GB con 30 editables completos, seis lotes, exportaciones y diagnósticos. La preparación Windows seguía pendiente de ejecución real en ambas PC.
- **Cambios:** se redujo la misma `Entrega-Windows-v1`. Se eliminaron 8.932 archivos pesados o de proyectos anteriores, además de 120 copias redundantes de cuatro imágenes de tableros que ahora se comparten. Se conservaron 30 fichas/tableros, 30 referencias de código sin medios de aquellos videos, tres estilos, 18 módulos declarativos, 59 recursos SVG/fuentes deduplicados, biblioteca de música/SFX y reglas/preferencias. Se añadió `INICIO_PARA_CODEX.md` y se adaptaron instalador/lanzadores para crear proyectos nuevos, sin dependencia de VIDEO-30.
- **Motivo:** separar la capacidad de edición y la memoria creativa del archivo de grabaciones/renders; evitar transportar o duplicar el histórico cuando solo se editarán videos nuevos.
- **Archivos afectados:** únicamente la entrega, su changelog, la documentación/registro operativo y tests dentro de su copia del framework, y esta entrada de bitácora. Catálogos originales de aprobación/configuración preservados como texto comprimido; sin respaldo oculto de videos eliminados. El framework original Mac, sus plantillas y todos los medios originales se conservan.
- **Validación:** validador del framework ligero PASS; 329 tests de la copia y nueve pruebas del adaptador PASS en Mac. Los tests de aprobación ahora usan un artefacto sintético temporal en lugar de depender del MP4 histórico; fallos previos de fixtures conservados. Tableros de las 30 propuestas idénticos por hash, referencias de código verificadas, vínculos SVG compartidos y sintaxis Python/JS comprobados. La creación de un proyecto nuevo se probó en carpeta temporal, sin montar/renderizar un video.
- **Resultado:** misma carpeta convertida en entrega ligera, con registro de proyectos vacío y lista para recibir nuevos brutos tras instalar/verificar herramientas en Windows. Tamaño exacto e integridad registrados en `Entrega-Windows-v1/evidencia/resumen-entrega.json`. La reducción del tamaño lógico de carpeta no se presenta como espacio físico liberado equivalente en APFS.
- **Aprendizaje:** conservar el conocimiento exige fichas, código, estilos, memoria y recursos; no todos los medios de producción anteriores. Retirar esos medios exige separar sus aprobaciones históricas del estado operativo de las nuevas referencias, sin reescribir la aprobación original.
- **Pendiente:** instalación/prueba real de Windows, paridad visual/audio y rendimiento en ambas PC; entorno avanzado de audio sigue pendiente. Cada nuevo video requiere fuente real, selección/adaptación de plantilla, recibo de inicio, controles y aprobación propios. Ninguna velocidad, escucha o calidad nueva se declara medida.


### 2026-10-06 — Asistente de inicio portátil para Windows y Mac

- **Petición:** entregar una sola carpeta con «INICIO Y CONFIGURACION DE FRAMEWORK», diagnóstico, instalación autorizada y consulta de versiones actuales; guiar contexto/guiones, elección de cinco paletas, visualización de las 30 plantillas y preparación de masters/carpetas para continuar en Codex. Mantener intacto el framework/flujo Mac original y evitar duplicar trabajos anteriores.
- **Punto de partida:** `Entrega-Windows-v1` ligera 1.1, aproximadamente 219,6 MB, sin videos antiguos, con 30 propuestas/referencias, tres estilos y recursos; entrada Windows sin cuestionario ni instalador completo. La ejecución real en ambas PC seguía pendiente.
- **Cambios:** se evolucionó esa misma carpeta a entrega 2.0, con lanzadores `.cmd`/`.command`, interfaz local de seis pasos y autorización separada de cada instalación. Diagnóstico de hardware, escritura, herramientas/filtros, Chrome, skills, ASR y audio. Consulta actual a fuentes oficiales/registros; Node local con SHA-256, HyperFrames versionado por lote, FFmpeg mediante gestores, audio Python 3.12 aislado con versiones calibradas, modelo ASR separado y Codex CLI opcional. No se instalaron herramientas globales en la Mac de origen.
- **Cambios creativos y de flujo:** cuestionario de tema/público/objetivo/tono/movimiento/guion/restricciones; cinco paletas sugeridas, selección editable y contraste tinta/papel; los 30 tableros se muestran con la paleta sin alterar sus originales. Se corrigió la carga de fotos dentro de SVG y el viewport según los PNG originales. Las 13 skills de edición más la skill de limpieza a solicitud se incluyen localmente. La creación de lotes reserva VIDEO-31 en adelante, comparte una ingesta y registra fuentes por ruta sin duplicarlas, con referencia de paleta/plantilla, QA pendiente e instrucción para Codex. La selección es provisional y no hereda aprobación.
- **Motivo y archivos:** facilitar inicio en otro equipo conservando reglas y contexto, con menor duplicación y pendientes visibles. Cambios exclusivamente en `Entrega-Windows-v1/` (interfaz, herramientas, perfiles, lanzadores, copia de audio, documentación, skills, pruebas/recibos) y esta entrada documental. Versiones previas de documentos/scripts preservadas en ZIP de metadatos, sin recuperar videos eliminados.
- **Validación:** 30 tests de adaptador/asistente y 329 tests del framework copiado PASS; validador del framework PASS. Se comprobó preservación de nodos SVG en las 30 propuestas, fotos embebidas solo para la vista, contraste, creación sin sobrescritura, fallos parciales, ausencia de consentimiento, origen/sesión y modo sin red. Se recorrió la interfaz real en navegador, se creó un lote sintético y luego se retiró; registro de proyectos queda vacío. Prueba técnica de 1 segundo en carpeta temporal de Mac con HyperFrames 0.8.102 existente: check/render, movimiento decodificado, pista de audio y RMS no nulo PASS. Doctor de audio adaptado PASS reutilizando entorno/modelo existentes en modo de lectura. Fuentes consultadas y disponibilidad de wheels Windows x64/Mac arm64 documentadas; no equivalen a instalación Windows ejecutada.
- **Resultado:** asistente y entrega portátil preparados, con 30 plantillas, recursos y memoria, sin masters ni MP4 históricos. Conserva configuración diferenciada de PC A/B y Mac; no promete una granja automática ni tiempos no medidos. Hashes del framework original verificados en `evidencia/mac-despues-asistente.json`.
- **Aprendizaje:** una dependencia instalada no demuestra un pipeline operativo; «todo listo» exige diagnóstico, prueba sintética en ese equipo y confirmación personal de acceso a Codex. El mayor número de versión no sustituye la calibración: el audio conserva versiones compatibles hasta una actualización validada. Un tablero recoloreado no reemplaza la maqueta adaptada a la voz ni el QA del MP4 exacto.
- **Pendiente:** primera instalación completa con PowerShell, prueba de render/audio/ASR y QA en las dos PC; instalación limpia de Mac y prueba con HyperFrames actual 0.8.138. La prueba local usó 0.8.102 existente y no valida la versión más reciente ni cada instalador. Audio/YAMNet y ASR deben comprobarse en cada destino; no se afirma escucha humana, paridad entre equipos, viralidad, edición automática terminada ni aprobación de un video nuevo. Gestores del sistema pueden requerir intervención de la persona cuando no estén instalados.

### 2026-10-06 — Entrega 2.1: guía para alumnos, progreso en carpeta y grabación visual con marcadores

- **Petición:** facilitar la instalación a alumnos sin lenguaje técnico; descargar una carpeta desde GitHub y abrir INICIO en Windows o Mac; guardar avances dentro de esa carpeta; añadir una guía visual que separe guiones, marcadores y acciones para grabar el master.
- **Punto de partida:** entrega portátil 2.0 con asistente de seis pasos, 30 propuestas, instaladores con consentimiento y memoria del framework. No tenía recorrido didáctico completo ni persistencia del borrador de edición. La validación real en Windows y una Mac limpia seguía pendiente.
- **Cambios:** `GUIASUPERDETALLADA.html` ofrece 15 pasos, casillas, notas, siguiente/anterior, recuperación, solución de problemas y progreso independiente por sistema. Los lanzadores cortos `INICIO WINDOWS.cmd` / `INICIO MAC.command` abren la guía mediante el servidor local; `INICIO.html` sirve de entrada alternativa. Si falta Python se muestra ayuda antes de pedir autorización. Los fallos de inicio dejan mensajes y registros locales. Se documentó descarga y extracción del ZIP de GitHub; no se creó ni publicó un repositorio.
- **Cambios de guardado:** progreso, borrador del cuestionario, paleta, plantillas, guion de grabación y último lote quedan en `MI-PROGRESO/`. Escrituras atómicas, copia anterior, confirmación de guardado, detección de conflictos entre ventanas, reintento y respaldo/recuperación en la propia carpeta. El servidor de una sesión abierta se reutiliza. Abrir el HTML directamente permite lectura, pero no promete escritura automática en disco; para eso se usa INICIO. Los datos personales, medios y runtimes se excluyen del repositorio mediante `.gitignore`.
- **Cambios didácticos de grabación:** `GUIA_GRABACION_MASTER.html` separa bloques naranja MARCADOR (se dice y se recorta), claros GUION (contenido) y azules PAUSA/ACCIÓN (no se lee); incluye diagrama de encuadre, guion personalizable, checklist y cuatro ejemplos: toma válida, corrección de última frase, descarte/repetición y varios videos en un master. Conserva las cinco frases documentadas: inicio, corregir última frase, aprobada, descartar y fin de sesión. Las pausas de 1–2 segundos y 1080p/30 fps se identifican como sugerencias didácticas nuevas, sin modificar las reglas de edición ni invalidar material previo. Aprobar una toma no aprueba el montaje final.
- **Motivo y archivos afectados:** hacer explícito qué decir, qué hacer y cómo continuar sin perder el trabajo. Cambios dentro de `Entrega-Windows-v1/`: HTML, lanzadores, `tools/asistente.py`, `tools/progreso.py`, `tools/bootstrap.ps1`, interfaz y cliente de progreso, pruebas, README/LEEME/instrucciones, configuración, changelog y evidencia. Esta entrada se añade también a la bitácora maestra. El framework, los medios y el flujo de la Mac original permanecen sin cambios. Las versiones previas se conservan en `evidencia/historico-v1/`.
- **Validación:** 46 pruebas Python del asistente, adaptador y persistencia PASS; contratos JavaScript de los 15 pasos por sistema, recuperación, marcadores, desconexión, reintento y conflictos PASS; sintaxis JS/Python/bash PASS. En navegador real se comprobaron navegación, casillas/notas, separación Windows/Mac, recuperación de copia de la carpeta, cuestionario restaurado al reiniciar servidor, cuatro escenas de grabación y guion personalizado. Los cuatro textos renderizados fueron reconocidos por el lector existente de marcadores con tiempos sintéticos: no fue una prueba de ASR ni de voz real. El lanzador corto Mac reutilizó la sesión existente al ejecutarse con bash. Se conservaron recibos y captura en `evidencia/validacion-guias-alumnos.json` y `evidencia/guia-grabacion-visual.png`.
- **Resultado:** entrega didáctica 2.1 preparada, con avance guardado en carpeta y guía de grabación integrada. Se retiraron los datos sintéticos de la vista inicial conservando un ZIP pequeño de evidencia. No se añadieron masters ni renders antiguos. Comparación de 2.405 archivos protegidos originales: cero cambios o ausencias, según `evidencia/mac-despues-guias.json`.
- **Aprendizaje:** una casilla marcada por el alumno no demuestra instalación ni QA. Un HTML abierto como archivo no puede garantizar escritura automática en la carpeta; el servidor local permite confirmar el guardado y mostrar fallos. Las instrucciones de grabación se entienden mejor al separar con texto y color la voz de control, el contenido y las acciones silenciosas, sin introducir un protocolo nuevo.
- **Pendiente / por confirmar:** instalación limpia, doble clic y permisos tras descargar el ZIP real en Windows y Mac; piloto con alumnos; impresión física/PDF y exportación/importación mediante diálogos externos del navegador. El navegador integrado bloqueó la navegación directa `file://` y no confirmó los diálogos de descarga/importación; se verificó en cambio el respaldo y recuperación dentro de la carpeta. No se afirma escucha humana, reconocimiento de voz real, paridad de render entre PC/Mac, ahorro de tiempo medido ni aprobación editorial. Las pruebas anteriores del framework no se repitieron, pues su código no cambió en esta entrega.

### 2026-10-06 — Distribución de la entrega portátil mediante GitHub público

- **Petición:** subir la entrega a la cuenta GitHub del usuario para descargarla en otros computadores. El usuario eligió expresamente acceso público: cualquiera podrá ver y descargar el contenido.
- **Punto de partida:** entrega portátil 2.1, aproximadamente 225,8 MB, guías y progreso local comprobados, sin repositorio Git ni remoto asociado. No se solicitaron cambios en videos ni en el framework original de Mac.
- **Cambios:** repositorio local solo dentro de `Entrega-Windows-v1/` y remoto público `https://github.com/iomiquantum/framework-edicion-social`; README con descarga ZIP directa, ruta corta sugerida en Windows e instrucciones de inicio. Se conservan los bytes del contenido mediante `.gitattributes`, finales CRLF de los lanzadores Windows y LF/permisos ejecutables de los `.command` de Mac. Identidad de commit local con correo noreply de la misma cuenta. No se otorga una licencia nueva a los recursos de terceros.
- **Motivo y archivos afectados:** distribuir exactamente la carpeta del curso sin subir el proyecto histórico de la Mac. README, atributos Git, lanzadores de la entrega (solo terminaciones), configuración, recibos, changelog y bitácoras. `.gitignore` mantiene fuera progreso, sesiones, instalaciones locales, registros de uso y medios nuevos. Historial previo preservado en `evidencia/historico-v1/antes-publicacion-github-2.1.zip`.
- **Validación inicial:** inventario de 1.980 archivos previo al recibo de publicación; ningún archivo mayor de 17 MB, sin MP4/MOV antiguos ni datos actuales de MI-PROGRESO/runtime/resultados. Búsqueda por patrones de credenciales sin hallazgos, incluyendo 52 entradas de siete ZIP históricos; es una revisión limitada por patrones, no una certificación absoluta de ausencia de secretos. Se conservaron los catálogos de procedencia, atribuciones y licencias existentes. Verificación de visibilidad pública por GitHub CLI.
- **Resultado inicial:** remoto público creado y contenido preparado. El resultado de la subida y la comprobación del ZIP de GitHub se registran en `Entrega-Windows-v1/evidencia/publicacion-github.json` y la continuación de esta entrada.
- **Aprendizaje:** descargar un ZIP no requiere Git ni una cuenta si el repositorio es público. La entrega debe excluir información cambiante del alumno y conservar nombres/permisos/bytes de los lanzadores; una descarga íntegra no demuestra que el equipo tenga las dependencias de edición instaladas.
- **Pendiente:** completar subida y validación de la descarga; primera instalación limpia, render/audio/ASR y rendimiento en ambas PC, además de instalación limpia y permisos de una Mac nueva. El contenido público queda accesible a cualquiera; esa visibilidad fue elegida por el usuario.

- **Cierre de subida y descarga:** rama `main` publicada en el repositorio público. Se descargó sin autenticación el ZIP de GitHub del commit `787d4a3be5fab943c358891395e827ba73022c90` (194,52 MB) y se compararon sus 1.983 archivos con los blobs Git: cero diferencias y cero archivos personales/medios antiguos excluidos. La copia extraída pasó 46 tests Python y los contratos JavaScript. El lanzador Mac, ejecutado mediante bash desde la carpeta extraída, inició el servidor, creó los registros vacíos, sirvió las dos guías y reutilizó la sesión. Se comprobó permiso 755 en los cuatro `.command` del ZIP. Los temporales de descarga/extracción se retiraron para no conservar otra copia completa. Recibos en `evidencia/verificacion-zip-github.json`, `tests-github-zip.log` y `publicacion-github.json`. Una segunda publicación solo incorpora documentación, bitácora y recibos; no cambia el código comprobado. La comprobación no acredita doble clic/Gatekeeper ni ejecución nativa en Windows o instalación limpia de dependencias.
