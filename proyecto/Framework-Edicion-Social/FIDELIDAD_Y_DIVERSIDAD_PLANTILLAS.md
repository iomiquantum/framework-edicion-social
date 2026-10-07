# Fidelidad y diversidad de las plantillas

Versión: 1.1.0. Vigente: 2026-09-30. Alcance: todos los próximos videos y lotes de este proyecto, incluidos los perfiles de edición1/2/3 y trabajos delegados. Preferencia explícita del usuario; criterio editorial interno, sin rendimiento de audiencia demostrado.

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

La propuesta visual y la ficha de la plantilla ya aprobadas son la referencia. Desarrollar sus rasgos propios fuera de paleta y tipografía cuando formen parte de ese diseño. No se exige comparar con videos vecinos ni inventar un número mínimo de diferencias entre entregas: la diversidad se definió al crear y aprobar las familias. No reinterpretar cada plantilla como la misma composición recoloreada ni rediseñarla por rutina. «Es más rápido» o «pasó el check» no justifican perder su identidad.

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

## Control obligatorio desde el inicio y QA de conservación

Crear `VIDEO-NN/QA_FIDELIDAD_PLANTILLA.md` desde `templates/template-fidelity-review.md` al iniciar, junto al recibo de documentos/hash. Es un control editorial humano o del editor/agente con alcance declarado; no una aprobación nueva que se pida al usuario para reutilizar su plantilla aprobada. Puede enlazar evidencia existente y usar timings compartidos sin repetir ASR del maestro.

### Antes de construir la composición completa

1. Abrir el tablero y la ficha aprobados de la plantilla seleccionada. Registrar rutas/SHA256, rasgos de estructura/diseño y recursos que la definen. No empezar desde un layout genérico del video anterior.
2. Mapear las ideas de la voz real a los estados visuales de la propuesta. Mantener estructura de voz y adaptar textos/ejemplos, sin inventar información. Identificar los recursos previstos y resolver temprano los necesarios, con pertinencia y procedencia.
3. Definir encuadre, escenario gráfico, posición de captions, gestos protegidos y función del espacio negativo. Registrar crop y qué elimina. Preparar una maqueta ligera o capturas equivalentes de los estados distintos antes del montaje completo; aprovechar componentes existentes. No requiere render final ni reanalizar el lote.
4. Revisar esa maqueta contra la propuesta aprobada: estructura, composición, lenguaje gráfico, jerarquía y movimiento previsto. Resolver aquí desvíos de identidad, ventanas/recortes injustificados, huecos accidentales y recursos faltantes. Registrar estado `conforme_para_montaje`, reviewer, evidencia y límites. `not_run` o `requiere_correccion` no permiten pasar al montaje completo; corregir el plan/maqueta primero. Esto no autoriza publicación ni sustituye QA del video.

La elección de plantilla ya aprobada no solicita una nueva aprobación humana rutinaria. Una incompatibilidad real de la toma se resuelve temprano con adaptación documentada que preserve identidad y reglas; un cambio fuera del alcance autorizado mantiene el pendiente correspondiente. No dejar decisiones básicas de composición para el final.

### Durante el montaje y antes del render completo

Usar el plan inicial como referencia; comprobar estados al integrarlos. La pasada visual/editorial vigente verifica que se conserva la propuesta y que la adaptación sigue siendo pertinente, legible y segura. Comparar hook, estados distintos, ejemplo/apoyo, regreso y cierre con el tablero y la maqueta inicial. Registrar tiempos/frames y alcance real. Un defecto nuevo se corrige cuando aparece; no esperar al render largo para evaluar por primera vez el diseño.

### Sobre el MP4 exacto

Dentro de la pasada de integración final vigente, enlazar ruta/SHA256 y comprobar que composición, recursos y correcciones coinciden con el plan ya revisado, incluyendo escenas breves y transiciones. Registrar reviewer y estados `pass`, `warn`, `fail` o `not_run`; no heredar este juicio del check técnico ni de otro video. Esta revisión confirma conservación y detecta defectos de ejecución; no inaugura el diseño ni añade otra pasada duplicada.

Identidad perdida sin justificación, reducción de una familia a cambio cosmético o encuadre/huecos accidentales requieren corrección editorial. Una excepción tiene motivo de contenido y evidencia. El control es documental/editorial obligatorio; no se implementó un detector automático ni un wrapper nuevo. Un script que encuentra SVG o diferencias CSS no prueba calidad. Snapshots aislados no prueban visionado completo ni todos los gestos.

### Precedencia y conservación de reglas

Esta instrucción complementa las reglas anteriores de voz real, recursos pertinentes, subtítulos, rostro/gestos, movimiento, audio/SFX, tres pasadas, export, versionado y aprobación. No las reduce ni las sustituye. Por aclaración expresa del usuario se retira únicamente la comparación obligatoria de vecinos para decidir fidelidad/diversidad, incluida la exigencia histórica equivalente de QA de serie; la referencia sigue siendo la plantilla aprobada. No modificar retrospectivamente ledgers, scorecards, snapshots o controles históricos de otras funciones.

## Optimización y conservación

Reutilizar timings, voz, componentes y activos pertinentes. La organización puede ser común; la composición final debe desarrollar la identidad elegida. Un flujo esencial puede reducir exploración o diseño a medida, pero no borrar los rasgos que distinguen su plantilla. Si no cabe su lenguaje en el alcance del perfil, registrar incompatibilidad y ajustar el plan/perfil conforme autorizaciones vigentes.

Conservar versiones, recibos y aprobaciones anteriores. Actualizar bitácora y changelog tras cambios materiales. Esta regla no autoriza reeditar16/18/19 aprobados ni modifica restauración de voz, publicación o límites de producción.

## Historial de esta regla

- v1.0.0,2026-09-30: primera integración con comparación de vecinos y mínimo de diferencias; versión preservada en research/fidelidad-plantillas-2026-09-30.
- v1.1.0,2026-09-30: usuario exige control desde el inicio y confirma que las propuestas aprobadas son referencia suficiente. Retirados comparación obligatoria de vecinos y mínimo de diferencias; añadido control antes de composición completa. Demás reglas permanecen vigentes.
