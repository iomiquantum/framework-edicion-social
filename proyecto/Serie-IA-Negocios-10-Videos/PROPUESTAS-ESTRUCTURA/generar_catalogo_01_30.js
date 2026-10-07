const fs = require('fs');
const path = require('path');

const root = __dirname;
const outputDir = path.join(root, 'CATALOGO-PLANTILLAS');

const collections = {
  fundamentos: { label: 'Fundamentos 01–05', short: 'Fundamentos', color: '#ff596f' },
  angulos: { label: 'Ángulos de comunicación 06–10', short: 'Ángulos', color: '#ffb22e' },
  mundos: { label: 'Mundos visuales 11–20', short: 'Mundos visuales', color: '#7a6cff' },
  inclusivo: { label: 'Diseño inclusivo 21–30', short: 'Diseño inclusivo', color: '#17b897' }
};

const baseAccessibility = 'Texto esencial sobre superficie estable, jerarquía clara, información no dependiente solo del color, subtítulos revisados y movimiento reducible.';

const templates = [
  {
    id: 'T01', name: 'Editorial impreso', collection: 'fundamentos', status: 'approved',
    concept: 'Convierte una idea educativa en una portada y una secuencia editorial de alta autoridad.',
    angle: 'Claridad editorial y autoridad.', motivation: 'Comprensión y confianza.',
    visual: 'Retícula de revista, placas oscuras, titulares grandes y acentos rosa/cian.',
    structure: 'Pregunta frontal → dato o tensión → contraste → síntesis → llamada a la acción.',
    extension: 'Añadir páginas como portada, dato, cita, ejemplo, síntesis y cierre sin cambiar la retícula.',
    accessibility: baseAccessibility, ideal: 'Explicaciones, datos, opinión profesional y educación de negocio.', metric: 'Retención por bloque y guardados.',
    artifact: 'OPCION-01_EDITORIAL-IMPRESO/propuesta-01.png'
  },
  {
    id: 'T02', name: 'Internet nativo', collection: 'fundamentos', status: 'approved',
    concept: 'Habla el lenguaje de interfaz y reacción de las plataformas sin imitar una red específica.',
    angle: 'Interrupción controlada y participación.', motivation: 'Novedad y reacción rápida.',
    visual: 'Ventanas, badges, gráficos, barras y acentos neón sobre fondos digitales.',
    structure: 'Hook disruptivo → reacción → prueba visual → intervención del presentador → CTA social.',
    extension: 'Alternar módulos de reacción, encuesta, comparación, comentario y resultado.',
    accessibility: baseAccessibility, ideal: 'Mitos, tendencias, comparativas y preguntas de comunidad.', metric: 'Elección de ver, comentarios y retención inicial.',
    artifact: 'OPCION-02_INTERNET-NATIVO/propuesta-02.png'
  },
  {
    id: 'T03', name: 'Minidocumental humano', collection: 'fundamentos', status: 'approved',
    concept: 'Presenta el aprendizaje como una pequeña historia observacional y cercana.',
    angle: 'Curiosidad progresiva y cercanía.', motivation: 'Empatía y reflexión.',
    visual: 'Fotografía protagonista, rótulos sobrios, aire cinematográfico y textos contenidos.',
    structure: 'Situación humana → tensión → hallazgo → significado → pregunta reflexiva.',
    extension: 'Añadir escenas por momentos reales: contexto, gesto, dificultad, decisión y consecuencia.',
    accessibility: baseAccessibility, ideal: 'Historias reales, procesos, errores y transformaciones.', metric: 'Retención narrativa y comentarios de identificación.',
    artifact: 'OPCION-03_MINIDOCUMENTAL-HUMANO/propuesta-03.png'
  },
  {
    id: 'T04', name: 'Sistema claro', collection: 'fundamentos', status: 'approved',
    concept: 'Hace visible un mecanismo complejo mediante piezas, relaciones y decisiones ordenadas.',
    angle: 'Explicación lógica y decisión visual.', motivation: 'Orden y control.',
    visual: 'Diagramas modulares, tarjetas, flechas y comparaciones de lectura rápida.',
    structure: 'Problema → mecanismo → comparación → ventaja → criterio de decisión.',
    extension: 'Sumar pasos numerados, bifurcaciones, ejemplos o verificaciones dentro del mismo sistema.',
    accessibility: baseAccessibility, ideal: 'Procesos, frameworks, tutoriales y decisiones técnicas.', metric: 'Guardados y retención hasta la solución.',
    artifact: 'OPCION-04_SISTEMA-CLARO/propuesta-04.png'
  },
  {
    id: 'T05', name: 'Cómic pop', collection: 'fundamentos', status: 'approved',
    concept: 'Transforma una explicación en diálogo expresivo, exagerado y fácil de compartir.',
    angle: 'Diálogo expresivo y entretenimiento.', motivation: 'Energía social y juego.',
    visual: 'Globos, viñetas, onomatopeyas, contornos gruesos y contraste pop.',
    structure: 'Pregunta → diálogo → reacción → contraste → desafío final.',
    extension: 'Agregar viñetas como réplicas, reacciones, ejemplos y remates sin romper el lenguaje gráfico.',
    accessibility: baseAccessibility, ideal: 'Objeciones, conversaciones, humor y verdades incómodas.', metric: 'Compartidos, comentarios y retención en el remate.',
    artifact: 'OPCION-05_COMIC-POP/propuesta-05.png'
  },
  {
    id: 'T06', name: 'Confesión cruda', collection: 'angulos', status: 'approved',
    concept: 'Una admisión concreta abre una historia honesta y convierte el error en aprendizaje.',
    angle: 'Vulnerabilidad y aprendizaje.', motivation: 'Identificación y confianza.',
    visual: 'Papel crema, líneas de diario, tinta borgoña, tachados y notas personales.',
    structure: 'Admisión → creencia equivocada → consecuencia → descubrimiento → aprendizaje.',
    extension: 'Continuar con entradas de diario, pruebas, costos, cambio de criterio y conclusión.',
    accessibility: baseAccessibility, ideal: 'Errores propios, lecciones difíciles y detrás de cámaras.', metric: 'Retención después de la admisión y comentarios personales.',
    artifact: 'OPCION-06_CONFESION-CRUDA/propuesta-06.png'
  },
  {
    id: 'T07', name: 'Caso abierto', collection: 'angulos', status: 'approved',
    concept: 'Organiza el contenido como una investigación cuya conclusión se gana con evidencia.',
    angle: 'Investigación y evidencia visible.', motivation: 'Verificación y reducción de incertidumbre.',
    visual: 'Archivo negro/blanco/rojo, fichas, listas, sellos, comparación y prueba.',
    structure: 'Pregunta del caso → pistas → contraste → verificación → veredicto.',
    extension: 'Añadir evidencia numerada, fuente, descarte, comparación y conclusión provisional.',
    accessibility: baseAccessibility, ideal: 'Desmontar afirmaciones, auditorías, casos y comparativas.', metric: 'Guardados y retención hasta el criterio de verificación.',
    artifact: 'OPCION-07_CASO-ABIERTO/propuesta-07.png'
  },
  {
    id: 'T08', name: 'Duelo de ideas', collection: 'angulos', status: 'approved',
    concept: 'Pone dos posturas legítimas frente a frente y obliga a elegir con criterio.',
    angle: 'Contraste y toma de postura.', motivation: 'Elección y expresión pública.',
    visual: 'Pantalla dividida rojo/azul, versus, columnas opuestas y marcador de decisión.',
    structure: 'Tesis A vs. tesis B → argumento A → argumento B → matiz → elección.',
    extension: 'Agregar rondas comparables con el mismo número de argumentos y un cierre no engañoso.',
    accessibility: baseAccessibility, ideal: 'Debates, métodos alternativos y decisiones con trade-offs.', metric: 'Comentarios con postura y compartidos.',
    artifact: 'OPCION-08_DUELO-DE-IDEAS/propuesta-08.png'
  },
  {
    id: 'T09', name: 'Manifiesto de autor', collection: 'angulos', status: 'approved',
    concept: 'Convierte una idea en declaración de identidad y posicionamiento reconocible.',
    angle: 'Identidad reconocible y aspiración.', motivation: 'Diferenciación y expresión personal.',
    visual: 'Verde oscuro, crema y oro; composición editorial premium y firma de autor.',
    structure: 'Declaración → aquello que se rechaza → principio → conducta → firma.',
    extension: 'Sumar principios, frases bandera, ejemplos y compromisos manteniendo voz y sello.',
    accessibility: baseAccessibility, ideal: 'Marca personal, visión, valores y posicionamiento.', metric: 'Compartidos, guardados y comentarios sobre identidad.',
    artifact: 'OPCION-09_MANIFIESTO-DE-AUTOR/propuesta-09.png'
  },
  {
    id: 'T10', name: 'Reto de autor', collection: 'angulos', status: 'approved',
    concept: 'Convierte el mensaje en una prueba breve que la audiencia puede realizar y reportar.',
    angle: 'Autoevaluación y participación.', motivation: 'Autonomía, competencia y progreso.',
    visual: 'Coral, turquesa y crema; checklist, números grandes y tarjetas de reto.',
    structure: 'Promesa → instrucción 1 → instrucción 2 → instrucción 3 → resultado/CTA.',
    extension: 'Agregar pasos solo si cada uno es realizable, verificable y tiene retroalimentación.',
    accessibility: baseAccessibility, ideal: 'Ejercicios, diagnósticos no clínicos, hábitos y desafíos.', metric: 'Respuestas numeradas y retención hasta el resultado.',
    artifact: 'OPCION-10_RETO-DE-AUTOR/propuesta-10.png'
  },
  {
    id: 'T11', name: 'Realidad deformada', collection: 'mundos', status: 'approved',
    concept: 'Una idea cotidiana cruza un portal y revela una lectura inesperada.',
    angle: 'Sorpresa visual y reencuadre.', motivation: 'Curiosidad y descubrimiento.',
    visual: 'Portales, escalas imposibles, círculos, masas flotantes y espacio surreal.',
    structure: 'Realidad conocida → anomalía → cruce → nueva lectura → regreso con pregunta.',
    extension: 'Crear nuevos portales o transformaciones, una por beat, conservando el ancla narrativa.',
    accessibility: baseAccessibility, ideal: 'Reencuadres, paradojas, futuro e ideas contraintuitivas.', metric: 'Repetición y retención después del portal.',
    artifact: 'OPCION-11_REALIDAD-DEFORMADA/propuesta-11.png'
  },
  {
    id: 'T12', name: 'Prompt Playground', collection: 'mundos', status: 'approved',
    concept: 'El aprendizaje ocurre manipulando una interfaz creativa, no solo escuchando una explicación.',
    angle: 'Proceso visible y experimentación.', motivation: 'Descubrimiento y control.',
    visual: 'Ventanas retro, cursores, archivos, selecciones, comandos y guardado.',
    structure: 'Prompt inicial → ajuste → respuesta → comparación → guardar/aplicar.',
    extension: 'Añadir iteraciones como ventanas nuevas sin ocultar el antes/después.',
    accessibility: baseAccessibility, ideal: 'IA, prompts, herramientas y procesos iterativos.', metric: 'Guardados, finalización y comentarios sobre el proceso.',
    artifact: 'OPCION-12_PROMPT-PLAYGROUND/propuesta-12.png'
  },
  {
    id: 'T13', name: 'Explorecore', collection: 'mundos', status: 'approved',
    concept: 'La idea se descubre recorriendo un mapa con hitos y observaciones de campo.',
    angle: 'Exploración guiada y pausa.', motivation: 'Curiosidad y calma.',
    visual: 'Mapa, brújula, ruta, sellos, coordenadas y cuaderno de campo.',
    structure: 'Destino → salida → hallazgo → desvío útil → aprendizaje del viaje.',
    extension: 'Agregar hitos, no pantallas arbitrarias; cada hito debe cambiar la comprensión.',
    accessibility: baseAccessibility, ideal: 'Procesos de descubrimiento, investigación y aprendizaje gradual.', metric: 'Porcentaje visto, guardados y respuestas reflexivas.',
    artifact: 'OPCION-13_EXPLORECORE/propuesta-13.png'
  },
  {
    id: 'T14', name: 'Texture Check', collection: 'mundos', status: 'approved',
    concept: 'Usa cambios materiales para volver tangible una idea abstracta.',
    angle: 'Metáfora sensorial y transformación.', motivation: 'Curiosidad táctil.',
    visual: 'Vidrio, arcilla, volumen, transparencias, sombras blandas y superficies.',
    structure: 'Materia inicial → presión → deformación → nueva forma → significado.',
    extension: 'Introducir una sola cualidad material nueva por beat y relacionarla con la idea.',
    accessibility: baseAccessibility, ideal: 'Conceptos abstractos, cambio, resistencia y construcción.', metric: 'Replays y recuerdo visual cualitativo.',
    artifact: 'OPCION-14_TEXTURE-CHECK/propuesta-14.png'
  },
  {
    id: 'T15', name: 'Notes App Chic', collection: 'mundos', status: 'approved',
    concept: 'Presenta el mensaje como registro personal capturado en el momento.',
    angle: 'Intimidad de proceso y autenticidad.', motivation: 'Cercanía e identificación.',
    visual: 'Carrete, nota, audio, checklist, recortes y anotaciones personales.',
    structure: 'Captura → nota personal → prueba → audio/recordatorio → decisión.',
    extension: 'Añadir registros fechados, fotos, listas y notas de voz con función narrativa.',
    accessibility: baseAccessibility, ideal: 'Rutinas, aprendizajes personales, making-of y confesiones ligeras.', metric: 'Comentarios de identificación y compartidos privados.',
    artifact: 'OPCION-15_NOTES-APP-CHIC/propuesta-15.png'
  },
  {
    id: 'T16', name: 'Opt-Out', collection: 'mundos', status: 'approved',
    concept: 'Reduce el estímulo para que una sola idea tenga espacio y peso.',
    angle: 'Silencio visual y foco.', motivation: 'Alivio cognitivo y claridad.',
    visual: 'Mucho espacio negativo, tipografía contenida y una idea por pantalla.',
    structure: 'Pausa → idea → respiración → matiz → cierre limpio.',
    extension: 'Añadir beats solo cuando la idea anterior haya concluido; no acumular tarjetas.',
    accessibility: baseAccessibility, ideal: 'Mensajes profundos, premium, reflexión y temas sensibles.', metric: 'Finalización frente a plantillas densas.',
    artifact: 'OPCION-16_OPT-OUT/propuesta-16.png'
  },
  {
    id: 'T17', name: 'Drama Club', collection: 'mundos', status: 'approved',
    concept: 'Construye el contenido como una escena dramática con conflicto y giro.',
    angle: 'Tensión emocional y revelación.', motivation: 'Expectativa y emoción.',
    visual: 'Cortinas, spotlight, actos, rótulos teatrales y contraste escénico.',
    structure: 'Personaje/tesis → conflicto → escalada → giro → decisión.',
    extension: 'Agregar actos, nunca relleno; cada acto debe elevar o resolver la tensión.',
    accessibility: baseAccessibility, ideal: 'Storytelling, dilemas, errores y transformaciones.', metric: 'Retención hasta el giro y comentarios con postura.',
    artifact: 'OPCION-17_DRAMA-CLUB/propuesta-17.png'
  },
  {
    id: 'T18', name: 'Rótulo popular', collection: 'mundos', status: 'approved',
    concept: 'Da al mensaje la calidez y memorabilidad de una gráfica cotidiana hecha a mano.',
    angle: 'Cercanía cultural y oficio.', motivation: 'Familiaridad y pertenencia.',
    visual: 'Rótulos pintados, color cálido, marcos decorativos y señal urbana.',
    structure: 'Llamado → refrán/idea → ejemplo cotidiano → aprendizaje → invitación.',
    extension: 'Añadir letreros como escenas y mantener legibilidad sobre la ornamentación.',
    accessibility: baseAccessibility, ideal: 'Consejos directos, cultura emprendedora y saber práctico.', metric: 'Compartidos y reconocimiento cultural cualitativo.',
    artifact: 'OPCION-18_ROTULO-POPULAR/propuesta-18.png'
  },
  {
    id: 'T19', name: 'Pixel Quest', collection: 'mundos', status: 'approved',
    concept: 'Convierte el aprendizaje en misión con progreso, elecciones y recompensa.',
    angle: 'Gamificación de una decisión.', motivation: 'Competencia y avance.',
    visual: 'Pixel art, mapa de misión, inventario, diálogo y marcador de progreso.',
    structure: 'Misión → obstáculo → opción → acción → recompensa/desbloqueo.',
    extension: 'Agregar niveles o ítems solo si representan pasos reales del aprendizaje.',
    accessibility: baseAccessibility, ideal: 'Retos, procesos por niveles, hábitos y participación.', metric: 'Respuestas 1–2–3, finalización y replays.',
    artifact: 'OPCION-19_PIXEL-QUEST/propuesta-19.png'
  },
  {
    id: 'T20', name: 'Jardín de ideas', collection: 'mundos', status: 'approved',
    concept: 'Representa el conocimiento como algo que se planta, cuida y cosecha.',
    angle: 'Crecimiento orgánico y proceso.', motivation: 'Propósito y progreso.',
    visual: 'Semilla, raíz, brote, hojas, etiquetas botánicas y textura natural.',
    structure: 'Semilla → raíz → cuidado → brote → cosecha/aplicación.',
    extension: 'Añadir etapas orgánicas o ramas, manteniendo visible la relación causa–crecimiento.',
    accessibility: baseAccessibility, ideal: 'Hábitos, aprendizaje, estrategia de largo plazo y comunidad.', metric: 'Guardados, finalización y aplicación reportada.',
    artifact: 'OPCION-20_JARDIN-DE-IDEAS/propuesta-20.png'
  },
  {
    id: 'T21', name: 'Ruta de foco', collection: 'inclusivo', status: 'approved',
    concept: 'Guía la atención con una sola prioridad y un próximo paso inequívoco.',
    angle: 'Atención guiada y priorización.', motivation: 'Reducir competencia entre estímulos.',
    visual: 'Ruta visible, foco central, señal de avance y zonas despejadas.',
    structure: 'Objetivo → paso actual → ejemplo → confirmación → siguiente paso.',
    extension: 'Una pieza nueva por paso; nunca mostrar simultáneamente todos los caminos.',
    accessibility: 'Una idea y un siguiente paso visibles; no presupone una preferencia universal asociada al TDAH.', ideal: 'Tutoriales, instrucciones y llamadas a la acción secuenciales.', metric: 'Finalización de secuencia.',
    artifact: 'OPCION-21_RUTA-DE-FOCO/propuesta-21.png'
  },
  {
    id: 'T22', name: 'Camino predecible', collection: 'inclusivo', status: 'approved',
    concept: 'Hace visible dónde estamos, qué sigue y cuándo cambia la estructura.',
    angle: 'Orientación y anticipación.', motivation: 'Seguridad cognitiva y continuidad.',
    visual: 'Zonas estables, barra de progreso, pasos nombrados y aviso de transición.',
    structure: 'Mapa previo → paso 1 → paso 2 → recapitulación → próximo destino.',
    extension: 'Repetir posiciones y numeración; avisar cualquier excepción antes de introducirla.',
    accessibility: 'Estructura estable y anticipación; no presupone que todas las personas autistas rechacen la sorpresa.', ideal: 'Cursos, explicaciones largas, onboarding y procesos.', metric: 'Orientación correcta entre pasos.',
    artifact: 'OPCION-22_CAMINO-PREDECIBLE/propuesta-22.png'
  },
  {
    id: 'T23', name: 'Pausa sensorial', collection: 'inclusivo', status: 'approved',
    concept: 'Protege el mensaje con espacio, pocos estímulos y transiciones suaves.',
    angle: 'Menor carga visual y sonora.', motivation: 'Comodidad y permanencia.',
    visual: 'Paleta tenue, fondos serenos, pocos elementos y respiración amplia.',
    structure: 'Entrada suave → idea → pausa → ejemplo → cierre sin sobresalto.',
    extension: 'Alternar idea y descanso; evitar capas simultáneas, flashes o sobresaturación sonora.',
    accessibility: 'Carga sensorial moderada y variante de movimiento reducido; no elimina energía de toda la colección.', ideal: 'Temas sensibles, bienestar, reflexión y explicaciones densas.', metric: 'Comodidad sensorial reportada y finalización.',
    artifact: 'OPCION-23_PAUSA-SENSORIAL/propuesta-23.png'
  },
  {
    id: 'T24', name: 'Contraste XL', collection: 'inclusivo', status: 'approved',
    concept: 'Prioriza lectura inmediata en pantallas pequeñas mediante pocas palabras de gran escala.',
    angle: 'Legibilidad extrema.', motivation: 'Acceso visual rápido.',
    visual: 'Tipografía extra grande, contraste reforzado, fondos sólidos y síntesis.',
    structure: 'Palabra clave → frase breve → dato → conclusión → acción.',
    extension: 'Dividir el guion en más pantallas antes que reducir el tamaño tipográfico.',
    accessibility: 'Apoya baja visión y móvil, pero no sustituye ampliación real ni audiodescripción.', ideal: 'Mensajes esenciales, hooks, pasos breves y cifras.', metric: 'Precisión de lectura en móvil.',
    artifact: 'OPCION-24_CONTRASTE-XL/propuesta-24.png'
  },
  {
    id: 'T25', name: 'Forma + señal', collection: 'inclusivo', status: 'approved',
    concept: 'Repite cada diferencia mediante color, forma, símbolo y palabra.',
    angle: 'Significado redundante y verificable.', motivation: 'Comprensión independiente del color.',
    visual: 'Formas geométricas, iconos, patrones, etiquetas y color secundario.',
    structure: 'Código visual → opción A → opción B → comparación → elección.',
    extension: 'Cada nuevo estado recibe una forma, un símbolo y una etiqueta consistentes.',
    accessibility: 'Nunca codifica una diferencia solo por color; no propone una paleta universal.', ideal: 'Comparaciones, estados, semáforos, dashboards y decisiones.', metric: 'Comprensión sin información cromática.',
    artifact: 'OPCION-25_FORMA-MAS-SENAL/propuesta-25.png'
  },
  {
    id: 'T26', name: 'Lectura fácil', collection: 'inclusivo', status: 'approved',
    concept: 'Reduce la carga lingüística sin infantilizar el contenido.',
    angle: 'Lenguaje literal y lectura progresiva.', motivation: 'Comprensión con menor esfuerzo.',
    visual: 'Frases cortas, alineación izquierda, interlineado amplio y bloques claros.',
    structure: 'Idea simple → ejemplo concreto → consecuencia → resumen → acción.',
    extension: 'Una oración por bloque; definir términos antes de agregar excepciones.',
    accessibility: 'Apoya comprensión y carga de lectura; no depende de una supuesta fuente universal para dislexia.', ideal: 'Información pública, educación básica y conceptos nuevos.', metric: 'Comprensión literal.',
    artifact: 'OPCION-26_LECTURA-FACIL/propuesta-26.png'
  },
  {
    id: 'T27', name: 'Subtítulo primero', collection: 'inclusivo', status: 'approved',
    concept: 'Diseña desde el texto hablado para que el video funcione plenamente sin audio.',
    angle: 'Acceso auditivo y seguimiento del diálogo.', motivation: 'Comprensión silenciosa.',
    visual: 'Subtítulos protagonistas, voz identificada, cortes por sentido y sonidos relevantes.',
    structure: 'Voz identificada → idea subtitulada → énfasis → sonido significativo → resumen.',
    extension: 'Cada nueva voz conserva etiqueta; todo sonido narrativamente útil se describe.',
    accessibility: 'Subtítulos completos y revisados, sin cubrir rostro ni demostración; no transcribe ruido irrelevante.', ideal: 'Entrevistas, conversación, tutoriales y consumo sin sonido.', metric: 'Comprensión sin audio.',
    artifact: 'OPCION-27_SUBTITULO-PRIMERO/propuesta-27.png'
  },
  {
    id: 'T28', name: 'Audio guía', collection: 'inclusivo', status: 'approved',
    concept: 'Integra en la narración todos los datos y cambios visuales indispensables.',
    angle: 'Acceso a información visual esencial.', motivation: 'Comprensión sin mirar la pantalla.',
    visual: 'Onda de audio, foco narrativo, descripciones breves y señales de cambio.',
    structure: 'Contexto hablado → dato visual verbalizado → acción → cambio → conclusión.',
    extension: 'Antes de sumar una imagen, decidir qué debe verbalizarse y qué es decoración.',
    accessibility: 'La información visual esencial se expresa en audio; evita describir decoración irrelevante.', ideal: 'Datos, demostraciones, transformaciones y contenido de escucha.', metric: 'Comprensión sin pantalla.',
    artifact: 'OPCION-28_AUDIO-GUIA/propuesta-28.png'
  },
  {
    id: 'T29', name: 'Ritmo y recuerdo', collection: 'inclusivo', status: 'approved',
    concept: 'Protege la memoria de trabajo mediante ejemplo, pausa y recapitulación útil.',
    angle: 'Procesamiento gradual y refuerzo.', motivation: 'Recordar sin saturación.',
    visual: 'Ciclos visibles, marcadores de pausa, recap y una progresión estable.',
    structure: 'Idea → ejemplo → pausa → recapitulación → acción.',
    extension: 'Repetir el ciclo con una sola idea nueva; la recapitulación resume, no duplica.',
    accessibility: 'Apoya memoria de trabajo y procesamiento sin repetir mecánicamente cada frase.', ideal: 'Clases, instrucciones, listas y conceptos encadenados.', metric: 'Recuerdo de la idea después del ejemplo.',
    artifact: 'OPCION-29_RITMO-Y-RECUERDO/propuesta-29.png'
  },
  {
    id: 'T30', name: 'Múltiples puertas', collection: 'inclusivo', status: 'approved',
    concept: 'Entrega la misma idea por varios canales para permitir distintas rutas de acceso.',
    angle: 'Acceso multimodal y elección.', motivation: 'Autonomía de comprensión.',
    visual: 'Texto, voz, símbolo y resumen en módulos coordinados y claramente delimitados.',
    structure: 'Idea central → versión textual → versión sonora → símbolo/ejemplo → resumen.',
    extension: 'Cada canal debe comunicar la misma idea, no añadir información crítica exclusiva.',
    accessibility: 'La idea llega por texto, voz, símbolo y recap; no afirma que una sola versión sirva a todas las personas.', ideal: 'Contenido educativo, campañas públicas y piezas de alcance amplio.', metric: 'Comprensión multimodal.',
    artifact: 'OPCION-30_MULTIPLES-PUERTAS/propuesta-30.png'
  }
];

const topicMap = {
  T01: ['marketing', 'marca', 'contenido', 'autoridad', 'educación'],
  T02: ['marketing', 'redes sociales', 'campañas', 'tendencias', 'viralidad'],
  T03: ['storytelling', 'marca personal', 'testimonios', 'servicios', 'confianza'],
  T04: ['productos', 'procesos', 'estrategia', 'educación', 'software'],
  T05: ['marketing', 'comunidad', 'humor', 'redes sociales', 'engagement'],
  T06: ['storytelling', 'marca personal', 'ventas', 'servicios', 'confianza'],
  T07: ['productos', 'ventas', 'comparación', 'evidencia', 'auditoría'],
  T08: ['marketing', 'ventas', 'objeciones', 'debate', 'comunidad'],
  T09: ['marketing', 'branding', 'marca personal', 'posicionamiento', 'autoridad'],
  T10: ['ventas', 'leads', 'participación', 'reto', 'formación'],
  T11: ['marketing', 'creatividad', 'innovación', 'campañas', 'tendencias'],
  T12: ['IA', 'prompts', 'herramientas', 'software', 'productos'],
  T13: ['educación', 'estrategia', 'investigación', 'servicios', 'storytelling'],
  T14: ['productos', 'diseño', 'innovación', 'creatividad', 'demostración'],
  T15: ['marketing', 'redes sociales', 'marca personal', 'contenido', 'autenticidad'],
  T16: ['servicios', 'premium', 'bienestar', 'marca', 'claridad'],
  T17: ['marketing', 'storytelling', 'ventas', 'lanzamientos', 'expectativa'],
  T18: ['negocios', 'ventas', 'comercio local', 'comunidad', 'emprendimiento'],
  T19: ['educación', 'gamificación', 'productos', 'onboarding', 'participación'],
  T20: ['educación', 'estrategia', 'hábitos', 'comunidad', 'crecimiento'],
  T21: ['educación', 'tutoriales', 'productividad', 'foco', 'procesos'],
  T22: ['productos', 'onboarding', 'procesos', 'educación', 'cursos'],
  T23: ['bienestar', 'salud', 'sensibilidad', 'educación', 'calma'],
  T24: ['accesibilidad', 'marketing', 'campañas', 'datos', 'móvil'],
  T25: ['productos', 'datos', 'dashboards', 'accesibilidad', 'comparación'],
  T26: ['educación', 'comunicación pública', 'accesibilidad', 'cursos', 'claridad'],
  T27: ['marketing', 'redes sociales', 'entrevistas', 'accesibilidad', 'subtítulos'],
  T28: ['productos', 'demostración', 'datos', 'accesibilidad', 'audio'],
  T29: ['educación', 'formación', 'memoria', 'accesibilidad', 'tutoriales'],
  T30: ['marketing', 'productos', 'educación', 'campañas', 'accesibilidad']
};

for (const template of templates) template.topics = topicMap[template.id];

const statusLabels = { approved: 'Aprobada', por_confirmar: 'Por confirmar', pending: 'Pendiente' };

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function card(template) {
  const collection = collections[template.collection];
  const n = template.id.slice(1);
  const imagePath = `../${template.artifact}`;
  const searchable = [template.id, template.name, collection.label, template.concept, template.angle, template.motivation, template.visual, template.ideal, ...template.topics].join(' ').toLowerCase();
  const topicPills = template.topics.map((topic) => `<span>${escapeHtml(topic)}</span>`).join('');
  return `
    <article class="card" data-index="${Number(n)}" data-collection="${template.collection}" data-status="${template.status}" data-topics="${escapeHtml(template.topics.join('|'))}" data-search="${escapeHtml(searchable)}" style="--accent:${collection.color}">
      <a class="preview-link" href="${escapeHtml(imagePath)}" target="_blank" aria-label="Abrir tablero completo de ${escapeHtml(template.id)} ${escapeHtml(template.name)}">
        <img src="${escapeHtml(imagePath)}" alt="Tablero horizontal con cinco capturas de la plantilla ${escapeHtml(template.id)} ${escapeHtml(template.name)}" loading="lazy" width="3200" height="1400">
      </a>
      <div class="card-body">
        <div class="card-topline">
          <span class="template-number">${n}</span>
          <span class="status status-${template.status}">${statusLabels[template.status]}</span>
        </div>
        <p class="collection-label">${escapeHtml(collection.short)}</p>
        <h2>${escapeHtml(template.name)}</h2>
        <p class="concept">${escapeHtml(template.concept)}</p>
        <div class="topics" aria-label="Temas recomendados">${topicPills}</div>
        <details>
          <summary>Ver características</summary>
          <dl>
            <div><dt>Ángulo</dt><dd>${escapeHtml(template.angle)}</dd></div>
            <div><dt>Motivación</dt><dd>${escapeHtml(template.motivation)}</dd></div>
            <div><dt>Lenguaje visual</dt><dd>${escapeHtml(template.visual)}</dd></div>
            <div><dt>Estructura narrativa</dt><dd>${escapeHtml(template.structure)}</dd></div>
            <div><dt>Regla para extender</dt><dd>${escapeHtml(template.extension)}</dd></div>
            <div><dt>Accesibilidad</dt><dd>${escapeHtml(template.accessibility)}</dd></div>
            <div><dt>Ideal para</dt><dd>${escapeHtml(template.ideal)}</dd></div>
            <div><dt>Métrica principal</dt><dd>${escapeHtml(template.metric)}</dd></div>
          </dl>
        </details>
      </div>
    </article>`;
}

function generateHtml() {
  const cards = templates.map(card).join('\n');
  return `<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Catálogo maestro de 30 sistemas visuales para videos verticales.">
  <title>Biblioteca visual · 30 plantillas</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23161318'/%3E%3Cpath d='M16 16h14v14H16zm18 0h14v14H34zM16 34h14v14H16zm18 0h14v14H34z' fill='%23f7f1e8'/%3E%3C/svg%3E">
  <style>
    :root { color-scheme: dark; --ink:#161318; --paper:#f4eee5; --muted:#a9a2aa; --line:#363039; --focus:#fff16a; }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { margin:0; background:var(--ink); color:var(--paper); font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size:16px; line-height:1.5; }
    a { color:inherit; }
    button, input { font:inherit; }
    .shell { width:min(1500px, calc(100% - 40px)); margin:0 auto; }
    .masthead { padding:36px 0 24px; border-bottom:1px solid var(--line); }
    .eyebrow { margin:0 0 8px; color:#ffcc73; font-size:.78rem; font-weight:800; letter-spacing:.15em; text-transform:uppercase; }
    h1 { margin:0; max-width:900px; font-family:Georgia, "Times New Roman", serif; font-size:clamp(2.3rem, 7vw, 6rem); line-height:.93; font-weight:500; letter-spacing:-.045em; }
    .intro { max-width:850px; margin:22px 0 0; color:#d2ccd2; font-size:clamp(1rem, 2vw, 1.18rem); }
    .stats { display:flex; flex-wrap:wrap; gap:10px; margin-top:24px; }
    .stat { padding:8px 13px; border:1px solid var(--line); border-radius:999px; color:#ddd6dc; font-size:.88rem; }
    .stat strong { color:white; }
    .toolbar-wrap { position:sticky; top:0; z-index:10; background:rgba(22,19,24,.94); backdrop-filter:blur(14px); border-bottom:1px solid var(--line); }
    .toolbar { display:grid; grid-template-columns:minmax(280px, 1fr) auto; gap:12px 14px; padding:16px 0; align-items:center; }
    .search { width:100%; min-height:46px; padding:0 16px; color:white; background:#211d23; border:1px solid #4a434d; border-radius:10px; outline:none; }
    .search:focus { border-color:var(--focus); box-shadow:0 0 0 3px rgba(255,241,106,.18); }
    .filters { display:flex; gap:8px; flex-wrap:wrap; }
    .filter { min-height:42px; padding:0 13px; border:1px solid #4a434d; border-radius:999px; background:#211d23; color:#d8d1d8; cursor:pointer; }
    .filter:hover { border-color:#77707a; }
    .filter[aria-pressed="true"] { background:var(--paper); border-color:var(--paper); color:var(--ink); font-weight:800; }
    .smart-topics { grid-column:1 / -1; display:flex; align-items:center; gap:8px; overflow-x:auto; padding-top:2px; scrollbar-width:thin; }
    .smart-label { flex:0 0 auto; margin-right:2px; color:#a9a2aa; font-size:.76rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }
    .smart-topic { flex:0 0 auto; min-height:34px; padding:0 11px; border:1px solid #4a434d; border-radius:999px; background:transparent; color:#d8d1d8; cursor:pointer; font-size:.82rem; }
    .smart-topic:hover, .smart-topic:focus-visible { border-color:#ffcc73; color:#fff; }
    .result-line { display:flex; justify-content:space-between; gap:20px; padding:24px 0 12px; color:var(--muted); font-size:.88rem; }
    .grid { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:22px; padding:0 0 70px; }
    .card { min-width:0; overflow:hidden; background:#211d23; border:1px solid var(--line); border-top:5px solid var(--accent); border-radius:14px; box-shadow:0 14px 38px rgba(0,0,0,.18); }
    .card[hidden] { display:none; }
    .preview-link { display:block; background:#0f0d10; overflow:hidden; }
    .preview-link img { display:block; width:100%; height:auto; aspect-ratio:16 / 7; object-fit:cover; transition:transform .25s ease, opacity .25s ease; }
    .preview-link:hover img { transform:scale(1.015); opacity:.9; }
    .card-body { padding:18px 20px 20px; }
    .card-topline { display:flex; align-items:center; justify-content:space-between; gap:10px; }
    .template-number { display:grid; place-items:center; width:44px; height:44px; border:1px solid var(--accent); border-radius:50%; color:var(--accent); font-family:Georgia, serif; font-size:1.2rem; }
    .status { padding:5px 9px; border-radius:999px; font-size:.73rem; font-weight:800; letter-spacing:.04em; text-transform:uppercase; }
    .status-approved { background:#d8ffe9; color:#07562c; }
    .status-por_confirmar { background:#fff0bd; color:#644900; }
    .status-pending { background:#343039; color:#c9c2cb; }
    .collection-label { margin:18px 0 5px; color:var(--accent); font-size:.76rem; font-weight:850; letter-spacing:.12em; text-transform:uppercase; }
    .card h2 { margin:0; font-family:Georgia, "Times New Roman", serif; font-size:clamp(1.55rem, 3vw, 2.1rem); font-weight:500; line-height:1.05; }
    .concept { min-height:3em; margin:12px 0 18px; color:#d3cdd4; }
    .topics { display:flex; flex-wrap:wrap; gap:6px; margin:-4px 0 18px; }
    .topics span { padding:4px 8px; border:1px solid #413a44; border-radius:999px; color:#bdb6be; font-size:.72rem; }
    details { border-top:1px solid var(--line); }
    summary { padding:14px 0 0; color:#fff; font-weight:750; cursor:pointer; list-style-position:outside; }
    summary:focus-visible, .preview-link:focus-visible, .filter:focus-visible, .smart-topic:focus-visible { outline:3px solid var(--focus); outline-offset:3px; }
    dl { margin:18px 0 0; }
    dl div { display:grid; grid-template-columns:145px 1fr; gap:14px; padding:11px 0; border-top:1px solid #342e36; }
    dt { color:var(--accent); font-size:.76rem; font-weight:850; letter-spacing:.07em; text-transform:uppercase; }
    dd { margin:0; color:#d7d1d7; }
    .empty { display:none; padding:70px 0 90px; text-align:center; color:#c5bec6; }
    .empty.visible { display:block; }
    footer { padding:28px 0 50px; border-top:1px solid var(--line); color:var(--muted); font-size:.85rem; }
    @media (max-width: 980px) { .toolbar { grid-template-columns:1fr; } .grid { grid-template-columns:1fr; } .concept { min-height:auto; } }
    @media (max-width: 620px) { .shell { width:min(100% - 24px, 1500px); } .masthead { padding-top:24px; } .filters { flex-wrap:nowrap; overflow-x:auto; padding-bottom:4px; } .filter { flex:0 0 auto; } .smart-topics { margin-right:-12px; } .result-line { align-items:flex-end; } dl div { grid-template-columns:1fr; gap:4px; } .card-body { padding:16px; } }
    @media (prefers-reduced-motion: reduce) { html { scroll-behavior:auto; } *, *::before, *::after { transition:none !important; } }
  </style>
</head>
<body>
  <header class="masthead">
    <div class="shell">
      <p class="eyebrow">Archivo creativo · edición 2026</p>
      <h1>30 sistemas para contar una idea.</h1>
      <p class="intro">Biblioteca operativa de composiciones para videos verticales. Cada ficha conserva su ángulo de comunicación, reglas de construcción, accesibilidad y métrica de aprendizaje.</p>
      <div class="stats" aria-label="Resumen del catálogo">
        <span class="stat"><strong>30</strong> plantillas</span>
        <span class="stat"><strong>4</strong> colecciones</span>
        <span class="stat"><strong>5</strong> capturas por tablero</span>
        <span class="stat">Fuente maestra: <strong>JSON normalizado</strong></span>
      </div>
    </div>
  </header>

  <div class="toolbar-wrap">
    <div class="shell toolbar" aria-label="Controles del catálogo">
      <label>
        <span style="position:absolute;clip:rect(0 0 0 0);clip-path:inset(50%);width:1px;height:1px;overflow:hidden">Buscar plantillas</span>
        <input class="search" id="search" type="search" placeholder="Describe lo que necesitas: marketing, ventas, productos…" autocomplete="off">
      </label>
      <div class="filters" role="group" aria-label="Filtrar por colección">
        <button class="filter" type="button" data-filter="all" aria-pressed="true">Todas</button>
        <button class="filter" type="button" data-filter="fundamentos" aria-pressed="false">01–05 Fundamentos</button>
        <button class="filter" type="button" data-filter="angulos" aria-pressed="false">06–10 Ángulos</button>
        <button class="filter" type="button" data-filter="mundos" aria-pressed="false">11–20 Mundos</button>
        <button class="filter" type="button" data-filter="inclusivo" aria-pressed="false">21–30 Inclusivo</button>
      </div>
      <div class="smart-topics" aria-label="Búsquedas sugeridas">
        <span class="smart-label">Búsqueda inteligente</span>
        <button class="smart-topic" type="button" data-query="marketing">Marketing</button>
        <button class="smart-topic" type="button" data-query="ventas">Ventas</button>
        <button class="smart-topic" type="button" data-query="productos">Productos</button>
        <button class="smart-topic" type="button" data-query="IA">IA</button>
        <button class="smart-topic" type="button" data-query="educación">Educación</button>
        <button class="smart-topic" type="button" data-query="storytelling">Storytelling</button>
        <button class="smart-topic" type="button" data-query="accesibilidad">Accesibilidad</button>
      </div>
    </div>
  </div>

  <main class="shell">
    <div class="result-line" aria-live="polite">
      <span id="count">Mostrando 30 de 30</span>
      <span id="order-label">Orden fijo T01 → T30</span>
    </div>
    <section class="grid" id="catalog" aria-label="Plantillas visuales">
      ${cards}
    </section>
    <p class="empty" id="empty">No hay plantillas que coincidan con esa búsqueda.</p>
  </main>

  <footer>
    <div class="shell">Catálogo local del proyecto · 30 plantillas aprobadas el 25 de septiembre de 2026 · La búsqueda inteligente funciona sin enviar datos fuera del equipo.</div>
  </footer>

  <script>
    const search = document.querySelector('#search');
    const cards = [...document.querySelectorAll('.card')];
    const filters = [...document.querySelectorAll('.filter')];
    const smartTopics = [...document.querySelectorAll('.smart-topic')];
    const count = document.querySelector('#count');
    const empty = document.querySelector('#empty');
    const catalog = document.querySelector('#catalog');
    const orderLabel = document.querySelector('#order-label');
    let activeCollection = 'all';

    const stopWords = new Set(['para', 'como', 'algo', 'quiero', 'necesito', 'una', 'uno', 'unos', 'unas', 'que', 'con', 'por', 'del', 'las', 'los', 'video', 'videos', 'plantilla', 'plantillas', 'hacer', 'sobre']);
    const intents = {
      marketing: ['marketing', 'mercadeo', 'marca', 'branding', 'campana', 'campanas', 'contenido', 'redes', 'social media', 'audiencia', 'engagement', 'posicionamiento', 'viralidad'],
      ventas: ['ventas', 'venta', 'vender', 'conversion', 'comercial', 'cliente', 'clientes', 'oferta', 'objecion', 'objeciones', 'leads', 'negocio', 'negocios'],
      productos: ['producto', 'productos', 'software', 'herramienta', 'herramientas', 'demostracion', 'demo', 'lanzamiento', 'lanzamientos', 'onboarding'],
      ia: ['ia', 'inteligencia artificial', 'prompt', 'prompts', 'automatizacion', 'chatgpt'],
      educacion: ['educacion', 'educativo', 'educativa', 'curso', 'cursos', 'ensenar', 'ensenanza', 'formacion', 'tutorial', 'tutoriales', 'aprendizaje'],
      storytelling: ['storytelling', 'historia', 'historias', 'narrativa', 'testimonio', 'testimonios', 'emocion', 'relato'],
      accesibilidad: ['accesibilidad', 'inclusivo', 'inclusion', 'subtitulos', 'baja vision', 'daltonismo', 'lectura facil', 'audio descripcion', 'neurodiversidad'],
      servicios: ['servicio', 'servicios', 'consultoria', 'asesoria', 'profesional', 'premium']
    };

    function normalize(value) {
      return value.toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    function analyzeQuery(rawQuery) {
      const query = normalize(rawQuery.trim());
      const tokens = query.split(/[^a-z0-9]+/).filter((token) => (token.length > 2 || token === 'ia') && !stopWords.has(token));
      const matchedIntents = Object.entries(intents).filter(([, aliases]) => aliases.some((alias) => query.includes(alias)));
      return { query, tokens, matchedIntents };
    }

    function scoreCard(card, analysis) {
      if (!analysis.query) return 1;
      const haystack = normalize(card.dataset.search);
      const topics = normalize(card.dataset.topics);
      const topicList = topics.split('|');
      let score = 0;
      analysis.tokens.forEach((token) => {
        const directMatch = token === 'ia' ? topicList.includes('ia') : haystack.includes(token);
        if (directMatch) score += 2;
      });
      analysis.matchedIntents.forEach(([intent]) => {
        if (topicList.includes(intent)) score += 10;
      });
      const exactPhraseMatch = analysis.query === 'ia' ? topicList.includes('ia') : haystack.includes(analysis.query);
      if (exactPhraseMatch) score += 6;
      return score;
    }

    function update() {
      const analysis = analyzeQuery(search.value);
      let visible = 0;
      const ranked = [];
      cards.forEach((card) => {
        const collectionMatch = activeCollection === 'all' || card.dataset.collection === activeCollection;
        const score = scoreCard(card, analysis);
        const searchMatch = !analysis.query || score > 0;
        card.hidden = !(collectionMatch && searchMatch);
        if (!card.hidden) {
          visible += 1;
          ranked.push({ card, score, index: Number(card.dataset.index) });
        }
      });
      const ordered = analysis.query
        ? [...ranked].sort((a, b) => b.score - a.score || a.index - b.index)
        : [...ranked].sort((a, b) => a.index - b.index);
      ordered.forEach(({ card }) => catalog.appendChild(card));
      count.textContent = analysis.query
        ? visible + (visible === 1 ? ' recomendación para “' : ' recomendaciones para “') + search.value.trim() + '”'
        : 'Mostrando ' + visible + ' de ' + cards.length;
      orderLabel.textContent = analysis.query ? 'Ordenadas por relevancia inteligente' : 'Orden fijo T01 → T30';
      empty.classList.toggle('visible', visible === 0);
    }

    filters.forEach((button) => button.addEventListener('click', () => {
      activeCollection = button.dataset.filter;
      filters.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
      update();
    }));
    smartTopics.forEach((button) => button.addEventListener('click', () => {
      search.value = button.dataset.query;
      update();
      search.focus();
    }));
    search.addEventListener('input', update);
  </script>
</body>
</html>`;
}

function validate() {
  if (templates.length !== 30) throw new Error(`Se esperaban 30 plantillas y existen ${templates.length}.`);
  const ids = new Set(templates.map((item) => item.id));
  if (ids.size !== 30) throw new Error('Hay identificadores duplicados.');
  for (const template of templates) {
    const missing = ['id', 'name', 'collection', 'status', 'concept', 'angle', 'motivation', 'visual', 'structure', 'extension', 'accessibility', 'ideal', 'metric', 'artifact', 'topics'].filter((field) => !template[field]);
    if (missing.length) throw new Error(`${template.id}: faltan ${missing.join(', ')}`);
    const artifactPath = path.join(root, template.artifact);
    if (!fs.existsSync(artifactPath)) throw new Error(`${template.id}: no existe ${artifactPath}`);
  }
}

function generateAudit() {
  const lines = [
    '# Auditoría documental — plantillas 01 a 30',
    '',
    'Fecha: **2026-09-25**  ',
    'Estado: **completa; 30 plantillas aprobadas con evidencia explícita**',
    '',
    '## Resultado',
    '',
    'Las 30 plantillas tienen tablero PNG y una ficha normalizada con concepto, ángulo, motivación, lenguaje visual, estructura narrativa, regla para ampliar la pieza, accesibilidad, usos recomendados, temas de búsqueda, métrica principal y estado de aprobación.',
    '',
    'La fuente consolidada de consulta es `CATALOGO_MAESTRO_01_A_30.json`. Su fuente editable es `generar_catalogo_01_30.js`, que genera también el visor `CATALOGO-PLANTILLAS/index.html`; así las características no se mantienen manualmente en dos lugares.',
    '',
    '## Cobertura',
    '',
    '| ID | Plantilla | Colección | Imagen | Ficha completa | Estado |',
    '|---|---|---|---:|---:|---|',
    ...templates.map((item) => `| ${item.id} | ${item.name} | ${collections[item.collection].short} | ✓ | ✓ | ${statusLabels[item.status]} |`),
    '',
    '## Reglas de mantenimiento',
    '',
    '1. Editar características en `generar_catalogo_01_30.js` y volver a ejecutar `node generar_catalogo_01_30.js`.',
    '2. No marcar una plantilla como aprobada sin una frase inequívoca del usuario y registro en la bitácora.',
    '3. Cuando un video dure 30–60 segundos, agregar beats respetando `structure` y `extension`; no improvisar pantallas que rompan el concepto.',
    '4. Registrar métricas reales en los planes de medición. Una preferencia visual o un buen resultado aislado no demuestra causalidad.',
    '5. Aplicar el estándar `ESTANDAR_ACCESIBILIDAD_BASE_01_A_30.md` a cualquier adaptación.',
    '',
    '## Estado de aprobación',
    '',
    `- Aprobadas con evidencia: ${templates.filter((item) => item.status === 'approved').map((item) => item.id).join(', ')}.`,
    '- Evidencia: el usuario indicó explícitamente “que queden todas aprobadas” el 2026-09-25 después de revisar las correcciones T22 y T30.',
    '',
    '## Búsqueda inteligente local',
    '',
    'El catálogo interpreta términos y sinónimos de marketing, ventas, productos, IA, educación, storytelling, accesibilidad y servicios. Los resultados se ordenan por relevancia y la búsqueda funciona completamente en el navegador, sin enviar consultas o datos a servicios externos.'
  ];
  return lines.join('\n') + '\n';
}

validate();
fs.mkdirSync(outputDir, { recursive: true });
fs.writeFileSync(path.join(root, 'CATALOGO_MAESTRO_01_A_30.json'), JSON.stringify({
  updated_at: '2026-09-25',
  purpose: 'Fuente consolidada de concepto, construcción, accesibilidad, medición y estado de las 30 plantillas.',
  approval_evidence: "El usuario aprobó explícitamente las 30 plantillas el 2026-09-25 con la frase: 'que queden todas aprobadas'.",
  search_mode: 'Búsqueda semántica local por temas y sinónimos; no transmite consultas a servicios externos.',
  collections,
  templates
}, null, 2) + '\n');
fs.writeFileSync(path.join(root, 'AUDITORIA_DOCUMENTACION_01_A_30.md'), generateAudit());
fs.writeFileSync(path.join(outputDir, 'index.html'), generateHtml());

console.log(`Catálogo generado: ${templates.length} plantillas.`);
console.log(`HTML: ${path.join(outputDir, 'index.html')}`);
