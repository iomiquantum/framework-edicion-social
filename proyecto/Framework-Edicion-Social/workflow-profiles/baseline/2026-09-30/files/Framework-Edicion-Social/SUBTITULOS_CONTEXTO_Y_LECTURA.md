# Subtítulos según contexto y lectura en móvil

Versión: 1.0.0. Fecha: 2026-09-30, America/Guayaquil. Aplicación: próximas ediciones verticales de Instagram Reels, Facebook Reels y TikTok. Los archivos ya exportados conservan sus versiones y aprobaciones; este aprendizaje no autoriza modificarlos.

La regla común es que una persona pueda seguir el mensaje sin sonido. El estilo y la posición se deciden con la toma real, la plantilla y la interfaz del destino. Ningún número de este documento acredita una mejora de retención en nuestra cuenta.

## Decisión antes del montaje

Leer `captions/catalog.json` y copiar `templates/caption-decision.json` dentro de `VIDEO-NN`. Registrar formato principal, posibles acentos por beat, ubicación, tamaño, máscara de rostro/gestos, perfil de destino y motivo. Se trata de un contrato editorial documentado: todavía no existe un selector automático ni un validador de geometría para este nuevo catálogo.

Separar tres cosas: subtítulo fiel de la voz, titular que resume una idea y palabra de énfasis. Un titular o una palabra grande no sustituye el subtítulo. Se puede integrar un titular y el subtítulo cuando muestran exactamente el mismo texto y conservan cobertura, tiempo y sincronía; comprobarlo y registrar la decisión, sin dejar la frase incompleta.

## Reglas comunes

1. Conservar las palabras de la toma montada, incluidas negaciones, cifras e improvisaciones. Corregir ASR, puntuación y espacios sin inventar voz a partir del guion. Incluir sonidos solo cuando aporten significado al mensaje; no convertir cada SFX decorativo en otra línea.
2. Mostrar bloques de sentido de una o dos líneas. Medir las líneas que realmente envuelve el navegador, no solo los saltos escritos en HTML. Si aparece una tercera, reagrupar los cues o redistribuir la plantilla antes de reducir la letra. No partir unidades sintácticas por rutina.
3. Mantener una posición estable dentro de cada plano y preservar ojos, boca, manos y la acción relevante. Cambiar de zona por un cambio real de composición, con transición predecible; no hacer que el lector busque cada palabra.
4. Asegurar contraste durante toda la aparición, incluidos resaltados y entradas. Usar como objetivo interno 4,5:1 entre texto y fondo; una placa estable ayuda sobre imagen variable. No afirmar cumplimiento de accesibilidad de toda la pieza por comprobar un color.
5. Dar prioridad a la lectura del subtítulo. Retirar o simplificar titulares, diagramas y CTA simultáneos cuando obliguen a leer tres mensajes diferentes. Evitar repetir la misma frase en dos cajas.
6. Usar énfasis selectivo: una o dos palabras relevantes por bloque como punto de partida. Conservar tamaño base, saltos y caja; evitar saltos de layout, parpadeos y rebotes continuos. El color no será el único indicador de importancia.
7. No usar una palabra que desaparece tras otra como default para explicaciones. El formato progresivo conserva visible el bloque completo y cambia su resaltado. Requiere tiempos de palabra comprobados; si no existen, usar frase estable sin repetir ASR del maestro.

## Ubicación: más cerca de la mirada cuando haya espacio

En talking head, buscar primero pecho o espacio negativo debajo del mentón, con separación de manos y rostro. Subir el texto respecto de los modelos pegados al pie puede acercar la lectura a la mirada. Es una decisión de composición, no una orden de poner texto sobre el centro geométrico o la cara.

En 1080×1920, explorar una caja de lectura en la zona aproximada del 55–70 % de la altura es un punto de partida interno. El contenedor completo, padding, placa y énfasis deben caber en el espacio disponible. Si el presentador o la interfaz ocupan esa zona, redistribuir encuadre, titulares y carril de captions. No copiar una coordenada de otra plantilla sin revisar la toma y sus gestos.

Opciones independientes del estilo:

| Ubicación | Cuándo conviene | Control |
| --- | --- | --- |
| Pecho / espacio negativo | Presentador con una zona libre bajo el mentón | Proteger rostro y gestos en movimiento |
| Carril reservado | Plantilla editorial, demostración o imagen que exige separación | Diseñarlo dentro de la zona útil del destino; no pegarlo al pie |
| Integrado en la escena | B-roll, diagramas y escenas sin rostro central | No ocultar acción ni crear varias lecturas competidoras |

Los perfiles actuales de `platforms/catalog.json` contienen márgenes conservadores internos, no mapas oficiales de botones. Conservar esa distinción. Facebook Reels no tiene aún perfil propio en ese catálogo: revisar su interfaz por separado; no declarar certificación por haber revisado Instagram.

TikTok indica que la zona segura de anuncios varía con dimensiones, descripción y elementos adicionales, y que el preview puede diferir del dispositivo real. [Especificación oficial, actualizada junio de 2026](https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads).

La guía de anuncios de Meta consultada reserva el 35 % inferior para evitar tapar elementos esenciales. En 1920 px equivale a empezar esa reserva en y=1248. Es una referencia para anuncios, no una ley de todos los Reels orgánicos; su edición no declara fecha y cita estudios de 2021–2023. [Guía de Meta, página 4](https://d3m889aznlr23d.cloudfront.net/img/events/458925814/assets/e042d2be.reels_ads_guide1.pdf). Las páginas actuales de Ads Guide con login no pudieron verificarse directamente; no adoptar como oficial ningún porcentaje adicional de terceros.

Antes de declarar listo un destino, comprobar su preview real con la descripción, botones y CTA previstos, sin publicar. Si no está disponible, registrar `pending`; se puede entregar revisión editorial local sin afirmar que supera esa comprobación. Un mismo MP4 puede reutilizarse si cada destino queda verificado. Crear una variante solo ante una incompatibilidad material.

## Tamaño y tiempo: presets revisables

Para fuente sans de peso medio/alto en 1080×1920, explorar 56–72 px de letra base, empezando aproximadamente en 60–64, con interlineado 1,08–1,18. Son presets internos sujetos a la fuente y al ancho útil, no mínimos oficiales ni sustitutos de revisar en móvil. A 360 px de ancho, 48 px de fuente original se reducen aproximadamente a 16; 64 a 21,3. No compensar un mal encuadre encogiendo todo.

Calcular `CPS = caracteres visibles, con espacios y puntuación / segundos visibles del bloque`. Para una frase completa con resaltado progresivo, contar la frase y su duración total una sola vez, no cada estado del resaltado. Registrar qué se cuenta; títulos adicionales aumentan carga, aunque no entren en el CPS del subtítulo.

- Objetivo inicial interno de lectura: aproximadamente 15–18 CPS cuando la voz y las pausas lo permitan; un valor menor no es fallo.
- Más de 20 CPS: revisar agrupación, carga simultánea y tiempo real disponible.
- Más de 25 CPS o bloques de varias palabras menores de 0,8 s: prioridad de revisión, sin considerarlos fallos automáticos por el número solo.
- Conservar sincronía y voz. No alargar sobre la frase siguiente ni borrar palabras para obtener una métrica verde. Reagrupar bloques dentro de límites reales, aprovechar pausas existentes y quitar texto redundante; si persiste rapidez, registrar juicio editorial.

Netflix usa hasta 17 CPS para subtítulos adultos en español y máximo dos líneas. Se toma como referencia profesional de lectura, con un contexto de distribución diferente; no se traslada su política completa de condensación a esta serie. [Guía oficial de español](https://partnerhelp.netflixstudios.com/hc/en-us/articles/217349997-Spanish-Latin-America-Spain-Timed-Text-Style-Guide).

## Formatos disponibles

| ID | Formato | Uso principal | Límite |
| --- | --- | --- | --- |
| CAP-FRASE-EDITORIAL-001 | Frase estable | Explicación, instrucciones, tono sobrio | Legibilidad y bloques de sentido |
| CAP-ENFASIS-SEMANTICO-001 | Frase + palabras destacadas | Contraste, objeción, conclusión | No destacar todo ni mover los saltos |
| CAP-RESALTADO-PROGRESIVO-001 | Frase visible + resaltado sincronizado | Ritmo conversacional con tiempos fiables | Sin flashes ni ocultar las otras palabras |
| CAP-IMPACTO-INTEGRADO-001 | Palabra o cifra protagonista + cobertura de la frase | Un hito breve, hook o remate | Acento puntual; no sustituir el relato por palabras sueltas |

La plantilla puede alternar una base editorial con un acento en un beat. Registrar la función del cambio. No alternar estilo en cada frase por obligación ni copiar siempre el formato del video anterior.

## QA y ahorro de trabajo

1. Reutilizar la transcripción y los tiempos compartidos; revisar solo la toma y el montaje del video actual. Mantener formato, posición y movimiento como decisiones distintas para evitar reconstruir captions por cambiar un color.
2. Antes del render largo, revisar primer cue, más largo, mayor CPS, máximo énfasis, transiciones, gestos y CTA. Comprobar caja real de una y dos líneas, espacios entre nodos y ausencia de una tercera línea.
3. Revisar a 360–390 px de ancho sin zoom. Esta simulación de tamaño no equivale a prueba de dispositivo físico. Con el sonido apagado, recorrer el video completo y comprobar si se entiende mensaje, ejemplo y conclusión; registrar quién lo revisó y el alcance. Una hoja de contacto aislada no acredita esa pasada.
4. Validar cues y gaps en el MP4 exacto, además del editable. Mantener la prevención de captions anidados y las tres pasadas del QA existente.
5. Revisar la interfaz real de Instagram, Facebook y TikTok cuando esos destinos se declaren listos. Archivar evidencia por destino/hash/fecha y no inferir aprobación o publicación.
6. Conservar SRT/VTT si se deriva de la misma transcripción verificada, para accesibilidad y futura adaptación; evitar duplicar a la vez subtítulos nativos y quemados cuando se superponen. No regenerar ASR por producir un sidecar.
7. Anotar tiempo invertido y retrabajo real. Comparar legibilidad y QA por formato antes de atribuir rendimiento. Sin métricas vinculadas a publicaciones, el efecto sobre retención sigue `por confirmar`.

## Evidencia y límites

Un estudio de 2024 con 168 participantes encontró mayor esfuerzo y menor comprensión al ver material subtitulado sin audio; no comparó estos presets ni Reels en español. [Estudio y resumen en UEA](https://ueaeprints.uea.ac.uk/id/eprint/96946/).

El estudio CHI 2024 analizó 300 TikToks e hizo nueve entrevistas con usuarios de captions. La lectura y la consistencia importaron; esa muestra no mide la moda de 2026 ni prueba que letras gigantes causen retención. [Publicación de los autores](https://makeabilitylab.cs.washington.edu/media/publications/McDonnell_CaptionItInAnAccessibleWayThatIsAlsoEnjoyableCharacterizingUserDrivenCaptioningPracticesOnTiktok_CHI2024.pdf).

Una revisión CHI publicada en abril de 2026 reúne 36 trabajos de 2015–2025 y sitúa los captions como infraestructura de accesibilidad compartida. Su resumen no establece una posición o animación ganadora. [Laboratorio de los autores](https://sinc-lab.com/publications/2026-04-13-nguyen2026like).

Fidelidad y sonidos significativos se apoyan en [W3C sobre captions](https://www.w3.org/WAI/media/av/captions/); el objetivo de contraste, en [W3C 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). La adaptación a nuestra serie es una decisión editorial documentada, no certificación WCAG.

La auditoría local y sus límites están en `research/subtitulos-2026-09-30/INFORME.md`: 18 exportaciones, 54 fotogramas seleccionados y 189 cues de editables actuales. No fue reproducción completa, escucha ni test de usuarios. Fecha límite de investigación: 2026-09-30 local.
