# Fidelidad y diversidad de las plantillas

Versión: 1.0.0. Vigente: 2026-09-30. Alcance: todos los próximos videos y lotes de este proyecto, incluidos los perfiles de edición1/2/3 y trabajos delegados. Preferencia explícita del usuario; criterio editorial interno, sin rendimiento de audiencia demostrado.

## Propósito y origen

El usuario indicó: «la idea de tener diferenets plantiallas estilos que cambien en estructura disneo iconos etc etc todo lo que mas se peuda no solo en colores como quedaron ahorita». La aprobación final de16v6/18v1/19v1 se conserva; esta instrucción rige nuevas ediciones y revisiones solicitadas.

En la comparación documentada de16/18/19, los finales18/19 conservaron principalmente paleta, tipografía y marcos, simplificando parte del lenguaje gráfico de sus propuestas. El presentador quedó dentro de ventanas cortas, captions en carril separado y una franja inferior grande sin contenido narrativo. Proteger gestos fue una intención válida; no exigía uniformar todas las composiciones. El catálogo ya proponía estructuras y mundos visuales distintos. Este aprendizaje refuerza su aplicación, no rediseña retrospectivamente las plantillas aprobadas.

## Qué debe variar

Una plantilla define un sistema visual y editorial. Consultar su tablero original, ficha y estructura antes de montar; registrar rutas y hashes en el recibo de inicio. En esta serie, usar `Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/CATALOGO_MAESTRO_01_A_30.json` y el PNG indicado en cada ficha. La elección de familia prevalece sobre un preset de color.

Revisar estos ejes y seleccionar los que tengan función en la voz real:

| Eje | Decisiones que diferencian una plantilla |
| --- | --- |
| Estructura editorial | Apertura, desarrollo del ejemplo/contraste/proceso, regreso y cierre; respetar el orden y significado de la voz grabada. |
| Composición | Presentador dominante, pantalla completa, composición dividida, escena centrada en objeto, tipografía protagonista o diagrama. |
| Lenguaje gráfico | Iconos, SVG, ilustraciones, señales, mapas, nodos, flechas, objetos pixelados, tarjetas de elección, diálogos y comparaciones. |
| Imágenes | Tipo de apoyo, acción contextual, escala, tratamiento y relación con el presentador; aplicar también reglas de pertinencia/realismo. |
| Jerarquía y captions | Roles tipográficos, integración de cifras/énfasis, ubicación y carga de lectura, con frase fiel y legibilidad móvil. |
| Movimiento y transiciones | Entradas, construcción del gráfico, cambios de escena y descansos ligados a ideas reales. |
| Paleta y superficies | Color semántico, textura, profundidad, bordes y marcos propios del mundo visual. |

Al usar plantillas distintas en videos consecutivos, señalar al menos dos diferencias observables fuera de paleta y familia tipográfica: por ejemplo composición y lenguaje gráfico, o estructura visual y movimiento. Es un mínimo editorial de este proyecto, no una métrica automática de calidad ni una obligación de cambiar cada eje. Comparar con los dos últimos videos disponibles, y con el siguiente si ya está montado. Una repetición necesaria por contenido/continuidad se explica; no se acepta como motivo suficiente «es más rápido» o «pasó el check».

Dentro de cada pieza, desarrollar las funciones visuales de la plantilla según las ideas de la voz. Evitar mantener siempre el mismo presentador en una caja más un titular arriba y captions abajo si la familia propone otros estados. No imponer cambios por segundo ni reconstruir el orden de la voz solo para copiar el tablero.

## Conservar identidad con contenido propio

Listar los rasgos que hacen reconocible la familia. Para cada rasgo, indicar dónde se usa, cómo se adapta o por qué se omite. Adaptar frases del tablero a lo realmente dicho sin borrar todo su lenguaje gráfico.

- **T16 Opt-Out:** sencillez, espacio negativo intencional, una idea dominante y descansos. No añadir iconos por cuota; el vacío debe tener propósito y proporción.
- **T18 Rótulo popular:** gráfica cotidiana de letreros, formas, marcos y rotulación expresiva. Puede explicar una transformación o un ejemplo con objetos/señales; conservar más que fondo teal y cartel amarillo.
- **T19 Pixel Quest:** lenguaje de juego con elecciones, comparaciones, diálogo, mapa/inventario/progreso cuando corresponda. En una pregunta sobre automatización y trato humano, una comparación de opciones o un diálogo puede aportar. No inventar niveles, porcentajes, logros ni promesas que la voz no sostiene.

Iconos, SVG, botones gráficos e imágenes son recursos disponibles, no una lista obligatoria en cada video. Deben explicar, comparar, orientar o acentuar contenido. Un botón dibujado en un MP4 no es interactivo: no invitar a pulsarlo como si ejecutara una acción. CTA real, cifras y representaciones de interfaces requieren contexto y no deben aparentar evidencia inexistente. Consultar biblioteca/componentes pertinentes antes de construir o generar; no reutilizar un recurso incorrecto por ahorro.

## Encuadre, espacio inferior y subtítulos

Diseñar juntos presentador, escenario gráfico y captions antes de elegir el crop. Elegir una toma grande, plano recortado, composición dividida o carril reservado según la plantilla y los gestos reales. No aplicar automáticamente una ventana corta con `object-fit: cover` a una toma vertical.

Si se recorta, registrar qué desaparece y por qué; comprobar rostro, manos/acción y continuidad en inicio/medio/final, cambios de pose y cortes. Una separación de captions que protege manos no justifica por sí sola cortar excesivamente al presentador ni dejar toda la mitad inferior inactiva.

Inspeccionar el lienzo completo, especialmente debajo de captions. Distinguir respiración intencional, reserva para interfaz real y hueco accidental. Ante un hueco grande sin función, redistribuir/agrandar zonas útiles o cambiar composición, antes de rellenar con decoración. No bajar captions al pie solo para llenar espacio. Aplicar `SUBTITULOS_CONTEXTO_Y_LECTURA.md`; sus coordenadas y márgenes son referencias internas, no requisitos universales de Reels/TikTok. Sin preview real, no certificar destino.

## Dirección creativa y QA obligatorio

Crear `VIDEO-NN/QA_FIDELIDAD_PLANTILLA.md` desde `templates/template-fidelity-review.md`. Puede enlazar evidencia ya producida, sin repetir ASR del maestro ni duplicar renders.

1. **Antes de montar:** abrir tablero/ficha, describir identidad y adaptación por escena; comparar con vecinos y planear geometría/recursos.
2. **Antes del render completo:** comparar propuesta y preview por escena, hook, ejemplo/apoyo, regreso y cierre. Revisar diferenciación fuera de color, recursos propios, encuadre, gestos, huecos, captions y móvil. Registrar tiempos/frames y alcance real. Corregir cuando la plantilla se haya convertido en un cambio cosmético sin justificación.
3. **Sobre el MP4 exacto:** enlazar ruta y SHA256; comprobar que los rasgos y correcciones se conservan, incluyendo escenas breves y transiciones. Registrar reviewer y estados `pass`, `warn`, `fail` o `not_run`; no heredar este juicio del check técnico ni de otro video.

Este control forma parte de las pasadas visual/editorial e integración; no añade una cuarta pasada duplicada. Identidad perdida sin justificación, homogeneidad cosmética entre familias o encuadre/huecos accidentales son hallazgos editoriales que requieren corrección antes de presentar la propuesta. Una excepción tiene motivo de contenido y evidencia, no una etiqueta de PASS. La aprobación humana final sigue separada.

El control exige revisión editorial documentada; no hay detector automático nuevo de fidelidad o variedad. Un script que encuentra SVG o diferencias CSS no prueba calidad. Snapshots aislados tampoco prueban visionado completo ni protección de todos los gestos.

## Optimización y conservación

Reutilizar timings, voz, componentes y activos pertinentes. La organización puede ser común; la composición final debe desarrollar la identidad elegida. Un flujo esencial puede reducir exploración o diseño a medida, pero no borrar los rasgos que distinguen su plantilla. Si no cabe su lenguaje en el alcance del perfil, registrar incompatibilidad y ajustar el plan/perfil conforme autorizaciones vigentes.

Conservar versiones, recibos y aprobaciones anteriores. Actualizar bitácora y changelog tras cambios materiales. Esta regla no autoriza reeditar16/18/19 aprobados ni modifica restauración de voz, publicación o límites de producción.
