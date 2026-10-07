# Motor de aprendizaje profesional

El motor de aprendizaje convierte decisiones verificadas en velocidad reutilizable sin reducir el piso de calidad. No aprende por intuición, aceptación silenciosa ni moda aislada. Conserva la evidencia original, distingue alcance y contexto, propone una promoción y exige revisión humana antes de cambiar un valor predeterminado.

## Objetivo

Cada video debe producir dos resultados separados:

1. una pieza terminada y verificable;
2. conocimiento estructurado que pueda disminuir el trabajo del siguiente video.

Una plantilla solo ahorra decisiones ya resueltas. Nunca sustituye el análisis de mensaje, toma, rostro, ritmo, semántica, fuentes, derechos, plataforma o intención del nuevo video.

## Capas de memoria

| Capa | Qué conserva | Vigencia predeterminada |
| --- | --- | --- |
| Historial inmutable | Feedback, aprobaciones, rechazos, métricas y versiones originales | Permanente; una corrección añade un evento |
| Video | Excepciones y decisiones válidas para un render exacto | Ese video y hash |
| Serie | ADN común y rangos de variación entre episodios relacionados | Versión de la serie |
| Creador/cuenta | Preferencias explícitas repetidas en trabajos distintos | Hasta revocación o revisión |
| Principio profesional | Seguridad, fidelidad, trazabilidad y controles técnicos | Global; no depende de gustos |

Una observación nunca salta directamente de video a regla global. La promoción siempre recorre el alcance mínimo compatible con su evidencia: video/activo → serie o estilo → creador o cuenta → global. Todo evento por encima de video o activo necesita una autorización humana de evaluación ligada a un artefacto y SHA-256; esa autorización no equivale a aprobar la promoción. El alcance global aprendido se reserva para contratos técnicos y nunca para gustos creativos.

## Cuatro tipos de evidencia

| Tipo | Pregunta | Puede demostrar | No demuestra |
| --- | --- | --- | --- |
| Técnica | ¿El archivo cumple el contrato? | Integridad, códec, color, audio, layout y ausencia de hard fails | Gusto o rendimiento |
| Creativa | ¿La edición comunica y fue aprobada? | Preferencia explícita para un render, elemento o estilo dentro de su alcance | Que funcione para toda temática |
| Repetición | ¿El patrón volvió a aprobarse en contextos distintos? | Candidato a valor predeterminado de serie o creador | Causalidad de rendimiento |
| Rendimiento | ¿Una variante comparable mejoró la métrica acordada? | Hipótesis respaldada dentro de ese contexto | Regla universal o causalidad automática |

Las señales externas y tendencias entran como hipótesis de experimento. Nunca como preferencias del usuario ni como reglas ganadoras.

`Repetición` es una propiedad derivada del conjunto, no una etiqueta que pueda autodeclarar un evento. Un contexto natural —video o experimento verificable— usa un solo `independent_context_id`, y ese identificador no puede reutilizarse para otro contexto. Así, duplicar IDs o inventar IDs nuevos para el mismo video no multiplica evidencia.

Toda señal vinculante conserva dos hashes: el del artefacto que contiene la evidencia y el del sujeto exacto evaluado. Un path vacío, un hash ausente o una aprobación sin sujeto exacto no entra al motor.

Un recibo distingue `created_at` —preparación del documento—, `decided_at` —momento real de la decisión humana— y `recorded_at` —momento en que se incorporó al sistema—. Esto permite registrar aprobaciones retrospectivas sin falsear la cronología. El SHA-256 detecta alteraciones, pero no autentica por sí solo la identidad de quien aprobó; la referencia humana sigue siendo auditable por separado.

## Ciclo de aprendizaje

```text
evento verificable
  -> normalización y hash de evidencia
  -> clasificación por tipo y alcance
  -> control de autoridad, contexto y hard gates
  -> detección de conflictos y excepciones
  -> recomendación: conservar / probar / promover / limitar / retirar
  -> revisión humana obligatoria
  -> snapshot versionado
  -> aplicación al siguiente brief como default reversible
  -> nueva medición sin reescribir la historia
```

El motor recomienda. La promoción material de una regla, activo, estilo o plantilla continúa siendo una decisión humana explícita.

## Estados de madurez

| Estado | Condición mínima | Uso permitido |
| --- | --- | --- |
| `observed` | Existe una señal trazable | Analizar; no aplicar por defecto |
| `candidate` | Feedback explícito o hipótesis documentada | Probar en alcance limitado |
| `series_default` | Dos videos distintos aprobados o instrucción explícita de serie | Inicializar nuevos videos de esa serie |
| `creator_default` | Evidencia explícita o repetida entre proyectos distintos | Sugerir para esa cuenta, con posibilidad de excepción |
| `performance_supported` | Experimentos comparables revisados humanamente | Priorizar dentro del contexto medido |
| `deprecated` | Revocación activa, deriva técnica o rendimiento/uso adverso confirmado | Mantener historial; recomendar retirada; excluir de uso automático |

Después de tres videos aprobados de una serie se recalculan rangos con el conjunto. El primer piloto es una semilla, no una ley.

Para proponer un default `locked` o `bounded`, cada aprobación contada debe incluir QA técnica en `pass`, ruta y hash de su evidencia, y el mismo SHA-256 de artefacto que verificó el recibo. Una instrucción humana explícita puede fijar un default cuando el contrato lo permita, pero no se presenta como evidencia derivada de varios videos.

## ADN de serie sin monotonía

Cada contrato de serie divide sus decisiones en cuatro grupos:

- `locked`: calidad, identidad y seguridad que no deben variar silenciosamente.
- `bounded`: valores que pueden moverse dentro de un rango, como preroll, velocidad, loudness, escala de captions o intensidad de cámara.
- `rotating`: familias que deben alternarse para evitar fatiga, como metáfora, paleta dominante, medio visual, transición, CTA y patrón SFX.
- `free`: decisiones gobernadas por el mensaje y la toma actual.

El control de serie debe detectar dos fallos opuestos:

1. deriva: el video pierde la identidad o el piso profesional;
2. clonación: el video repite recursos y gramática aunque el tema exija otra solución.

La similitud no demuestra coherencia y la diferencia no demuestra creatividad. Ambas requieren lectura editorial.

## Portafolio de plantillas, no una plantilla única

El objetivo no es encontrar una fórmula y repetirla. El framework mantiene varias familias de plantillas, cada una adecuada para una función narrativa distinta. Por ejemplo:

- contradicción o mito → revelación;
- problema → ciclo → sistema;
- pregunta → comparación → decisión;
- historia breve → tensión → aprendizaje;
- lista progresiva → giro → acción;
- demostración → evidencia → conclusión;
- pantalla completa inmersiva con retornos puntuales al rostro;
- conversación directa reforzada por overlays discretos.

Cada familia conserva `lineage`: plantilla de origen, variantes, videos donde se usó, cambios estructurales, aprobaciones, rechazos y resultados. Una variante nueva no reemplaza a su familia anterior; amplía el portafolio.

Las dimensiones de exploración se controlan por separado:

| Dimensión | Ejemplos de variación |
| --- | --- |
| Estructura | orden de hook, tesis, evidencia, contraste y CTA |
| Formato visual | talking head, collage, diagrama, B-roll, demostración, pantalla completa |
| Estilo | tipografía, geometría, textura, contraste y dirección artística |
| Ritmo | densidad de cortes, descansos, velocidad y duración de beats |
| Motion | zooms, entradas, transiciones y comportamiento de cámara |
| Sonido | familia musical, densidad y rol semántico de SFX |

Una comparación útil cambia una familia principal por vez y conserva el resto documentado. El selector elige por adecuación al mensaje, no por popularidad total. Ninguna familia se declara universalmente ganadora: puede ser preferida para un tema, duración, emoción, objetivo o plataforma y resultar inadecuada fuera de ese contexto.

Cuando dos valores incompatibles empatan dentro del mismo contexto de variante, ninguno queda habilitado para revisión de promoción, aunque el margen configurado para el alcance sea cero. El empate exige más evidencia o una decisión humana explícita.

## Índice y recetas no son aprobación

El índice semántico acelera búsqueda y reutilización, pero sus señales conservan significados limitados:

- un hash idéntico prueba contenido binario idéntico, no pertinencia creativa;
- un score semántico prueba coincidencia con metadatos declarados, no similitud visual perceptual;
- un cooldown indica repetición reciente, no baja calidad;
- una asignación provisional no cuenta como uso hasta sobrevivir a un artefacto aprobado;
- un activo aprobado en biblioteca todavía puede ser incorrecto para el beat actual.

El compilador de recetas también es un motor de propuestas. Cada combinación se evalúa contra el blueprint, los activos elegibles y la memoria completa de serie. Puede devolver hasta tres opciones o abstenerse. Una persona selecciona, modifica o rechaza la solución. Las recetas híbridas conservan `primary_family_id`, `hybrid` y `contributing_family_ids`; las cohortes atribuyen una publicación una sola vez a su familia primaria y analizan las contribuciones como dimensiones, no como publicaciones duplicadas.

## Precedencia cuando hay conflicto

1. Seguridad, legalidad, fidelidad y hard gates técnicos.
2. Instrucción explícita vigente del usuario para el trabajo actual.
3. Aprobación ligada al hash exacto y a su alcance declarado.
4. Contrato vigente de serie o creador.
5. Hipótesis respaldada por rendimiento comparable.
6. Tendencia o patrón externo todavía experimental.

Una regla inferior nunca puede invalidar una superior. Toda excepción conserva motivo, responsable, alcance y fecha.

Las correcciones conservan tipo y fuente de evidencia. Una revocación debe tener autoridad igual o superior a la evidencia que retira; una medición de rendimiento o un proceso automático no puede revocar feedback humano. Una oposición humana explícita activa bloquea la promoción aunque exista mayor volumen de rendimiento favorable. Un hard gate tampoco revoca gustos: bloquea la candidatura por una vía separada del score y solo una nueva medición técnica en `pass` puede despejarlo.

## Calidad no negociable

Ninguna optimización puede omitir:

- selección trazable de toma y fuente;
- conservación de palabras, intención y continuidad;
- protección de rostros y sujetos principales;
- inteligibilidad de voz, control de picos y revisión de audio;
- captions legibles y zonas seguras;
- relevancia semántica de imágenes, iconos, logos, motion y SFX;
- derechos, procedencia y hashes de activos;
- QA ligado al render exacto;
- aprobación separada de rendimiento;
- proyecto por capas y versiones anteriores recuperables.

Si una plantilla entra en conflicto con uno de estos puntos, se adapta o se descarta para ese video.

Los hard gates no suman ni restan votos. `fail` y `not_run` son bloqueos absolutos activos; `pass` solo confirma el piso técnico y no demuestra calidad creativa. La evidencia técnica que no sea hard gate solo puede evaluar contratos de los ejes `technical` o `workflow`. Para esos contratos la diversidad creativa y el voto de gusto no se inventan: basta evidencia técnica repetida, más la autorización humana de alcance y la revisión final cuando correspondan.

## Qué se automatiza y qué no

Se automatiza:

- lectura de eventos y verificación de esquemas;
- agrupación por atributo, alcance y contexto;
- cálculo de evidencia suficiente;
- detección de contradicciones, caducidad y repetición excesiva;
- extracción de fingerprints técnicos;
- preparación de plantillas, matrices y paquetes de revisión;
- recomendación explicada de promoción o retirada.

Permanece humano:

- juzgar si el mensaje se entiende y se siente auténtico;
- decidir si una solución creativa merece convertirse en patrón;
- resolver contradicciones de gusto o contexto;
- aprobar el máster, una plantilla o un cambio de alcance;
- atribuir causalidad a resultados de publicación.

Una señal de rendimiento direccional (`supports` u `opposes`) requiere comparación real contra cohorte, control o A/B, benchmark numérico, dirección de la métrica, ventana positiva, confianza suficiente y el tamaño de muestra mínimo de la policy. Una métrica absoluta sin comparación solo puede registrarse como neutral.

## Registro de publicación y cohortes

Una observación de red entra al motor únicamente si resuelve esta cadena local:

```text
registro de publicación
  → paquete multicanal y target exactos
  → MP4 derivado por hash y tamaño
  → control de entrega ready
  → evidencia local de publicación y captura por hash
  → atribución creativa seleccionada por una persona
  → observación normalizada
```

El framework vuelve a comprobar los archivos en vez de confiar en hashes copiados dentro de una fila. Inspecciona el MP4 real con `ffprobe`, reproduce el perfil técnico y exige que `creative-attribution.json` seleccione una propuesta existente del plan ligado. Las ventanas de 24 h, 72 h y 7 días admiten tolerancias bilaterales explícitas; una captura demasiado temprana o tardía no se fuerza dentro de la ventana. Las tasas conservan su denominador y el N efectivo conjunto usa la intersección de publicaciones que poseen todas las métricas nucleares.

Una cohorte solo compara proyecto, plataforma, superficie, perfil, cuenta, idioma, tema, campaña, periodo, moneda, ventana, tráfico, objetivo, audiencia y banda de duración compatibles. Además registra variación en familia primaria, receta, hook, estructura, sistema visual, motion, sonido y CTA. Un confusor material limita la fuerza de la evidencia. La eficiencia de producción se informa en otro bloque; solo registros `verified` con evidencia se comparan y nunca se combinan con el rendimiento creativo en una puntuación causal.

Tres publicaciones comparables permiten una revisión humana de hipótesis; no demuestran por sí solas causalidad. El reporte no puede modificar reglas, elegir una receta ni promover una plantilla.

La evidencia ligada por SHA-256 garantiza integridad del artefacto local desde el momento del registro. No autentica por sí misma a la plataforma, la cuenta, la persona ni la exhaustividad de un export remoto. El motor conserva este límite como `integrity_scope`, no lo convierte en una certeza inexistente.

## Salidas por cada video

Al cerrar una revisión se deben producir o actualizar, según corresponda:

1. recibo de aprobación ligado al SHA-256;
2. evento de feedback atómico;
3. fingerprint del video;
4. delta frente al contrato de serie;
5. ledger de variedad y reutilización;
6. recomendación del motor con evidencia a favor y en contra;
7. métricas de producción con método y estado de verificación: tiempo, renders, cambios y retrabajo;
8. atribución creativa exacta cuando una persona seleccionó una receta;
9. después de publicar, registro con evidencia local, observaciones normalizadas y revisión de cohortes contextual.

## Métricas del propio sistema

El motor también debe demostrar que optimiza el proceso. Por lote se comparan:

- tiempo hasta primera revisión;
- tiempo de render frente a tiempo creativo;
- porcentaje de capas reutilizadas sin cambios;
- número de rondas y cambios reabiertos;
- defectos encontrados antes y después de entrega;
- recursos generados frente a reutilizados;
- decisiones heredadas aceptadas, modificadas o rechazadas;
- diversidad entre videos consecutivos;
- rendimiento de publicación solo cuando el contexto sea comparable.

La meta no es maximizar reutilización. Es minimizar retrabajo y decisiones repetidas manteniendo o elevando la calidad observada.

## Regla operativa permanente

Después de cada aprobación:

1. congelar el archivo y su evidencia;
2. registrar exactamente qué se aprobó;
3. separar lo específico del video de lo potencialmente reutilizable;
4. ejecutar el motor en modo recomendación;
5. revisar la propuesta antes de promoverla;
6. versionar la memoria resultante;
7. iniciar el siguiente video desde esa memoria, pero volver a analizar su contenido real.

Así las plantillas se vuelven progresivamente más rápidas y precisas sin sacrificar criterio editorial, estructura ni lógica.

La ingesta serializa bajo un lock exclusivo el ciclo completo de lectura, validación y reemplazo atómico del ledger. Dos procesos concurrentes no pueden aprobar sobre snapshots distintos ni perder eventos silenciosamente. Los pisos de la policy tampoco pueden reducirse por debajo del contrato conservador, y los umbrales de escala, diversidad, ratio positivo y margen no disminuyen al ampliar alcance.
