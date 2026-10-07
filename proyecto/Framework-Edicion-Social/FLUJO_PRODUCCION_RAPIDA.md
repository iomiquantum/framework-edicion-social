# Flujo de producción rápida con calidad profesional

## Objetivo

Reducir el tiempo entre grabación, primera revisión y publicación sin degradar la claridad, el audio, la seguridad visual ni la trazabilidad. La velocidad proviene de preparar en paralelo, reutilizar decisiones aprobadas y revisar únicamente lo que cambió; no de omitir controles esenciales.

La vista compacta de módulos, artefactos y gates está en [MATRIZ_PRODUCCION_PRO.md](MATRIZ_PRODUCCION_PRO.md). La operación conectada para el lote completo está en [OPERACION_OPTIMIZACION.md](OPERACION_OPTIMIZACION.md).

## Fuente de verdad

1. El guion recibido antes de grabar es una guía provisional para preparar recursos.
2. La toma marcada como aprobada es la fuente editorial definitiva.
3. La transcripción de esa toma gobierna captions, entidades, cifras, logos y sincronización.
4. Ningún recurso provisional se conserva si ya no corresponde con lo que realmente se dijo.

## Carriles paralelos

### Carril 0 — antes de grabar: preflight creativo no bloqueante

- Crear `CHECKLIST_GRABACION.md` por `VIDEO-NN` a partir del guion provisional.
- Proponer únicamente planos adicionales que materialicen un beat: manos, escritura, teclado, pantalla, vehículos, luces, rutas, objetos, espacios o procesos.
- Para cada plano marcar una sola decisión: `ya disponible`, `grabar ahora`, `resolver después` o `no usar`.
- Explicar encuadre, acción, duración, seguridad, privacidad y significado editorial.
- Si no se dispone del recurso o no se desea grabarlo, el A-roll continúa sin bloqueo. La edición activa un fallback de locutor, icono, lettering, diagrama, B-roll existente o generación posterior.
- No exigir recursos complementarios que no aporten comprensión o que compliquen innecesariamente el rodaje.
- Para guiones largos, agrupar planos por locación y utilería para grabarlos en bloque después del A-roll.

### Carril A — mientras se graba

- Dividir el guion provisional por ideas.
- Detectar marcas, conceptos, cifras, procesos y oportunidades visuales.
- Construir o refrescar el índice semántico y consultar primero la biblioteca global.
- Preparar recursos flexibles y marcar cada uno como `provisional`.
- Crear un mapa de recursos por `VIDEO-NN`, nunca por número de toma.

### Carril B — cuando llega el metraje

- Hashear, escuchar y transcribir cada archivo maestro una sola vez.
- Detectar la claqueta verbal, revisar el `take-map.json` y conservar solo las tomas aprobadas.
- Crear un proxy independiente por `VIDEO-NN` para que cada tarea trabaje sin volver a recorrer el maestro.
- Comparar lo dicho con el guion provisional.
- Confirmar recursos útiles, retirar los que ya no correspondan y resolver únicamente los faltantes.
- Analizar espacio negativo, rostro, ojos, boca y gestos antes de ubicar overlays.

Ambos carriles convergen en un único plan semántico. El montaje no espera a que se regenere un recurso que ya existe y la biblioteca no obliga a utilizar un recurso irrelevante.

## Claqueta verbal compacta

- Inicio: `MARCADOR. Video N, toma N, inicio.`
- Corrección parcial: `MARCADOR. Corregir, corregir. Última frase.`
- Correcta: `MARCADOR. Aprobada, aprobada.`
- Incorrecta: `MARCADOR. Descartar, descartar.`
- Cierre: `MARCADOR. Fin de sesión.`

Una toma sin cierre inequívoco nunca se aprueba automáticamente. Si una aprobación o descarte no puede asociarse con una toma abierta, queda en revisión y no entra al montaje.

La corrección parcial mantiene abierta la misma toma. Después del marcador, el locutor repite **la frase completa desde su comienzo**, no únicamente la palabra equivocada, y puede continuar con el resto del contenido. En edición se escucha el tramo nuevo, se localiza por audio y significado el inicio de la frase inmediatamente anterior, se retiran esa versión equivocada y la claqueta, y se conserva la repetición nueva. La puntuación del ASR solo orienta: nunca decide por sí sola el inicio del reemplazo. Si la nueva repetición también falla, se pronuncia otra vez el mismo marcador y la última versión verificada reemplaza al intento inmediatamente anterior. Este comando no aprueba la toma; al finalizar todavía debe decirse `MARCADOR. Aprobada, aprobada.`

## Entrada local de lotes grandes

- Cuando el metraje ya está en el mismo equipo, se entrega por ruta absoluta dentro del proyecto; no se vuelve a subir al chat ni se duplica.
- Los originales viven en una carpeta de ingesta, se conservan inmutables y reciben hash antes de crear proxies o derivados.
- Un archivo maestro puede contener varios `VIDEO-NN`. La claqueta verbal, no el nombre del archivo, determina los límites y la toma aprobada de cada video.
- Para lotes divididos por tamaño se recomienda `LOTE-VIDEOS-01-05-ORIGINAL.MOV`, `LOTE-VIDEOS-06-10-ORIGINAL.MOV`, etc.; se conserva la extensión real de la cámara y se evita una doble extensión como `.mp4.MOV`.
- Cada salida mantiene trazabilidad hacia archivo, rango temporal, `VIDEO-NN`, toma y decisión de aprobación.

## Arranque limpio y cadencia de voz

La edición de diálogo no corta por un umbral ciego. Combina transcripción por palabra, forma de onda, escucha y continuidad gestual. Los valores siguientes son el punto de partida para material a 30 fps; en otra tasa se convierten conservando el tiempo equivalente.

### Entrada después del marcador

- Eliminar por completo la claqueta y la espera posterior sin valor narrativo.
- Detectar el primer fonema real, no solo el inicio estimado de la primera palabra.
- Usar **4 fotogramas antes del primer fonema** como valor predeterminado (`0,13 s` a 30 fps).
- Rango normal adaptable: **2–6 fotogramas** (`0,07–0,20 s`).
- Conservar **6–12 fotogramas** cuando una respiración, mirada o gesto prepare naturalmente la frase.
- Conservar **15–30 fotogramas** solo si la anticipación tiene una función expresiva deliberada.
- No dejar un segundo completo por defecto: suele sentirse como espera. Tampoco imponer un solo fotograma: puede cortar consonantes, respiración o movimiento de labios.

### Clasificación de pausas

| Función | Tratamiento | Duración final orientativa a 30 fps |
| --- | --- | ---: |
| Silencio muerto, duda, búsqueda o reinicio | retirar o comprimir | solo la continuidad necesaria |
| Respiración natural | conservar o acortar | 3–8 fotogramas |
| Dentro de una misma idea | compactar sin atropellar | 4–8 fotogramas (`0,13–0,27 s`) |
| Entre frases relacionadas | mantener separación legible | 8–14 fotogramas (`0,27–0,47 s`) |
| Cambio de idea o énfasis | preservar el beat | 12–24 fotogramas (`0,40–0,80 s`) |
| Pausa dramática, humor, reacción o demostración | conservar según intención | excepción documentada |

Cuando una pausa accidental es larga, se retira principalmente su zona central y se conservan pequeñas colas naturales. Nunca se cortan un fonema, una sílaba final, una respiración emocional ni un gesto que aporte significado. La meta es una interpretación continua y humana, no una cadencia de palabras pegadas.

### Continuidad de imagen y audio

- Priorizar cortes durante parpadeos, movimientos de cabeza, cambios de postura o reinicios naturales del gesto.
- El jump cut directo es válido. Si distrae, cubrirlo con un punch-in semántico de aproximadamente 5–10 %, reencuadre, B-roll o corte sobre movimiento.
- No alternar zoom in/zoom out en cada frase de forma mecánica; el cambio de escala responde a énfasis o estructura.
- Aplicar microfundidos de voz de **10–33 ms**. Usar hasta 1–2 fotogramas solo con respiración o room tone limpio y nunca solapar fonemas.
- Un J-cut o L-cut puede desplazar el empalme de audio 1–3 fotogramas respecto al corte visual cuando mejore la naturalidad.
- Conservar normalmente 4–8 fotogramas después del último fonema; ampliar a 10–20 si debe concluir una sonrisa, gesto o reacción.
- Recalcular los subtítulos después de cerrar el montaje de voz.

### Plan no destructivo y QA

Antes de montar se crea `cut-plan.json` desde `templates/cut-plan.json`. Cada pausa modificada registra rango original, clasificación, acción, duración final y recurso visual usado para ocultar el empalme, si existe. El plan queda ligado al hash del original y de la transcripción para poder cambiar estilo, motion o recursos sin rehacer la selección.

La revisión obligatoria comprueba que:

- no aparecen la claqueta ni la espera posterior;
- la primera y la última palabra están completas;
- el discurso suena continuo y humano al escucharlo con los ojos cerrados;
- ningún corte rompe de forma molesta una expresión o gesto al verlo sin audio;
- no existen clics, fonemas duplicados, respiraciones partidas ni saltos de room tone;
- todo silencio neutro mayor de 24 fotogramas tiene una justificación o se corrige;
- el resultado se revisa a velocidad normal con audífonos y altavoz de teléfono.

## Secuencia operativa

### -1. Checklist creativo previo al A-roll

Antes de comenzar cada `VIDEO-NN`, abrir su `CHECKLIST_GRABACION.md` y decidir el destino de cada apoyo. Este gate organiza el rodaje pero nunca impide grabar al locutor.

- `Ya disponible`: registrar la ruta o fuente.
- `Grabar ahora`: incluirlo en la lista de planos del día.
- `Resolver después`: dejar una especificación suficiente para stock, motion graphics o generación externa.
- `No usar`: conservar la decisión para que edición no vuelva a solicitarlo.

La ausencia de todos los apoyos activa `A-roll + recursos provisionales` como fallback válido. Vehículos se graban únicamente desde una posición segura, con el conductor dedicado a conducir; pantallas y documentos no muestran datos privados; personas identificables requieren autorización.

### 0. Preflight de grabación y ownership

Antes de transcribir, inspeccionar cada fuente con `scripts/check_recording_preflight.py`. Un hard fail de video, audio requerido, resolución, FPS o códec bloquea la ingesta; una advertencia de VFR o color queda registrada y se resuelve conscientemente.

Antes de escribir un `VIDEO-NN`, reclamarlo de forma atómica con `scripts/production_board.py`. Un video tiene un solo owner activo y una tarea heavy solo comienza si existe capacidad. Esto permite preparar recursos y editar otros videos en paralelo sin que dos tareas modifiquen la misma composición.

### 1. Ingesta y selección

- Conservar el original como archivo inmutable.
- Escuchar las pistas disponibles y fijar explícitamente la correcta; no elegirla por posición sin verificar.
- Transcribir el maestro completo una sola vez y compilar sus marcadores en `take-map.json`.
- Revisar humanamente tomas abiertas, marcadores desconocidos, correcciones parciales y aprobaciones múltiples antes de continuar.
- Para cada corrección parcial, completar en el `take-map` los límites escuchados de la frase anterior y su reemplazo, marcarla `resolved` y trasladar la decisión no destructiva a `cut-plan.json`.
- Crear un proxy liviano por toma aprobada. Si ya existe un `take-map.json` y un proxy verificados, ninguna tarea vuelve a transcribir ni a escanear el maestro.
- Generar `cut-plan.json` y revisarlo antes de codificar o montar.
- Exportar o montar únicamente las tomas aprobadas.
- En el render final volver al rango exacto del original; el proxy es exclusivamente de trabajo.

El procedimiento completo y sus artefactos obligatorios viven en [INGESTA_MAESTRA.md](INGESTA_MAESTRA.md).

### 1.1 Preflight bloqueante

Antes de iniciar una edición individual:

```bash
python3 Framework-Edicion-Social/scripts/preflight_project.py \
  --project <RUTA-DEL-PROYECTO> --video VIDEO-NN --stage edit
```

Antes del render de entrega se repite con `--stage render --deep`. Un error bloquea el avance. Las advertencias requieren revisión y no se convierten silenciosamente en aprobaciones. El preflight comprueba originales, hashes, recursos, estado de aprobación, estilos autocontenidos y ausencia de referencias o copias exactas de activos rechazados, incluso si fueron renombradas. Las copias históricas se conservan únicamente en una cuarentena `do_not_reuse`, fuera de los árboles activos.

### 2. Bloqueo semántico interno

- Confirmar transcripción, orden de ideas y términos dudosos.
- Identificar claims, nombres propios, marcas y cifras.
- Crear `creative-blueprint.json` con hook, beats, arco emocional, descansos, función de cada recurso y presupuestos máximos de motion/SFX.
- Compilar hasta tres recetas de hook, estructura, sistema visual, motion, sonido y CTA desde blueprint, contrato, ledger e índice completos. Seleccionar humanamente o conservar la abstención.
- Ejecutar `scripts/score_style.py`; aceptar una selección solo cuando supere umbral y margen. Una abstención abre revisión editorial y no autoriza a elegir arbitrariamente.
- Los cambios posteriores de estilo no reabren esta capa.

### 3. Reutilización antes de generación

Para cada necesidad visual o sonora:

1. Buscar candidatos por intención, etiquetas, descripción y restricciones.
2. Reutilizar un recurso aprobado cuando el significado coincida.
3. Crear una variante si solo cambia color, encuadre o formato.
4. Si la imagen disponible no coincide con la frase real o resulta genérica, preferir generar una imagen específica según `IMAGENES_CONTEXTO_REALISMO.md`; un banco con una opción adecuada es alternativa. No forzar reutilización por conveniencia.
5. Registrar el resultado y su procedencia en `library/catalog.json` y en el manifiesto del proyecto.

`scripts/asset_intelligence.py` agrupa únicamente copias con SHA-256 idéntico y ordena candidatos mediante metadatos semánticos declarados. `avoid_for`, rechazo, deprecación y `do_not_reuse` pueden excluir; el cooldown solo advierte. El score no es similitud visual ni aprobación. El historial de uso se actualiza después de aprobar el artefacto, no al asignar provisionalmente un recurso.

### 4. Ensamblaje por capas

Mantener separadas como mínimo:

1. Fuente y montaje.
2. Reencuadre y cámara.
3. Corrección visual.
4. Voz.
5. Captions.
6. Logos y evidencia.
7. Imágenes y cutaways.
8. Iconos y diagramas.
9. Transiciones y motion.
10. Música.
11. SFX.

Cada elemento recibe un identificador estable. Una corrección debe poder expresarse como `tiempo + capa + elemento + cambio`.

Antes del primer montaje se copia `templates/dependency-map.json` y se genera una clave con `scripts/cache_key.py`. Antes de un cambio se ejecuta `scripts/change_impact.py`; solo sus capas transitivamente dependientes pierden validez. Un cambio en cualquiera de los seis grupos —fuente, transcripción, cut-plan, estilo, activos o mezcla— produce una clave distinta y evita reutilizar un resultado obsoleto.

Cada `VIDEO-NN` tiene una carpeta de escritura exclusiva. Las tareas pueden preparar recursos, captions o montaje en paralelo, pero los trabajos pesados —transcripción, codificación y render— se encolan con un máximo inicial de dos procesos simultáneos en el mismo equipo.

### 5. Primera revisión económica

- Crear `review-packet.json` y `review.html` desde render, manifiesto, dependency-map, blueprint y cambios ligados por SHA-256.
- Usar preview, snapshots, contact sheet y renders cortos de los tramos críticos.
- Presentar una sola ronda consolidada de decisiones, no preguntas por cada recurso.
- Mostrar el video completo en calidad de revisión solo cuando ritmo y sincronización lo exijan.
- Reservar el render final 1080 × 1920 para después de cerrar los cambios editoriales.

### 6. Cambios por delta

| Solicitud | Se conserva | Se revisa |
| --- | --- | --- |
| Cambiar color o tipografía | montaje, audio, captions y recursos | estilo y contraste |
| Cambiar imagen o icono | montaje, voz y tiempos | recurso, entrada, salida y zona facial |
| Ajustar zoom o transición | guion, captions y mezcla base | tramo afectado y límites adyacentes |
| Ajustar SFX o música | todas las capas visuales | mezcla, inteligibilidad y picos |
| Corregir una palabra | resto del montaje | caption, sincronía y recursos vinculados |
| Cambiar significado u orden | recursos reutilizables | montaje y todas las capas dependientes |

Se valida localmente el tramo cambiado y sus límites. Antes de entregar, siempre se realiza una comprobación global del MP4 final.

Las variantes se describen con `variant-plan.json`. El cuerpo, la voz, el timing de captions, el plan semántico, los activos y las zonas faciales quedan compartidos y bloqueados; solo se modifica la familia declarada, por ejemplo hook y CTA. Si cambian varias familias sin control, dejan de ser comparables.

## Gate de entrega profesional

Cada render candidato recibe una copia de `templates/qa-scorecard.json`. Se completa con evidencia del archivo exacto y se valida según [QA_PROFESIONAL.md](QA_PROFESIONAL.md). La entrega permanece bloqueada cuando exista un hard gate en `fail`, un hard gate requerido en `not_run`, evidencia insuficiente o una revisión editorial sin firma. Una excepción puede explicar un `warn`, pero nunca anular un hard fail.

### 7. Aprobación y aprendizaje

- Registrar feedback en `templates/review-decision.json`.
- Preparar y sellar `approval-receipt.json` contra el SHA-256, tamaño, rol y alcance del archivo exacto.
- Una instrucción global explícita puede convertirse inmediatamente en preferencia confirmada.
- Una inferencia o aceptación silenciosa nunca se convierte en preferencia.
- Una preferencia creativa observada se mantiene como candidata hasta repetirse en dos proyectos distintos.
- Aprobar una edición no aprueba automáticamente su plantilla, cada activo ni un derivado; esos alcances se registran por separado.
- Una edición completa aprobada puede convertirse en semilla descriptiva para una receta versionada de estilo, estructura y parámetros.
- El archivo aprobado se registra con `scripts/golden_master.py`; una diferencia de hash o metadatos invalida la coincidencia y nunca hereda aprobación.
- Un rechazo aislado se registra con su contexto; no se interpreta automáticamente como prohibición universal.
- Registrar en `asset-usage-history.json` solo los recursos presentes en el artefacto aprobado.
- Si se eligió una receta, conservar `creative-attribution.json` con la opción real, los seis módulos y el hash de su plan; una propuesta no seleccionada nunca recibe crédito de rendimiento.

### 8. Derivados por plataforma

Cuando la edición conserva HDR, el primer aprobado es un mezzanine editorial y no un archivo de publicación. Desde su recibo exacto se genera un máster social SDR BT.709 distinto. `scripts/check_master_profile.py` verifica el perfil, loudness y linaje; la revisión humana comprueba que la conversión no alteró pieles, gradientes, exposición ni intención.

Solo con aprobación explícita se sella `content-lock-evidence.json` y `scripts/build_publish_package.py` vuelve a comprobar SDR, HDR, ambos recibos, reporte técnico, catálogo e inventario. El paquete llama al plan de derivados desde el máster social neutral, se materializa completo mediante staging, sella package/adaptación/briefs y permanece separado de cualquier acción de subida. `ready_for_derivative_build` no significa publicado.

- Se conservan toma, cortes, voz, significado y activos.
- Se adaptan layout, saltos de captions, CTA equivalente y exportación.
- Reels, TikTok y Shorts usan el mismo proyecto y variables de perfil, no tres montajes independientes.
- Cada render se comprueba con `scripts/check_platform_delivery.py`.
- La revisión de preview real queda ligada al SHA-256 exacto; cualquier cambio obliga a repetirla.

Las zonas seguras son overlays de Studio y nunca se queman en el video. Sus coordenadas son conservadoras internas, no reglas oficiales permanentes.

### 9. Rendimiento posterior

Después de publicar se registra la relación entre publicación, paquete, target, MP4, control de entrega, evidencia local y referencia de origen. Cada captura de métricas lleva su propia evidencia por ruta + SHA y resuelve `creative-attribution.json`. `scripts/performance_cohorts.py` inspecciona el MP4 real, normaliza ventanas de 24 h, 72 h y 7 días, tasas, confusores, ocho dimensiones creativas y N efectivo conjunto por intersección de publicaciones. Separa además cuenta, idioma, tema, campaña, periodo y moneda. `performance-review.json` permanece fail-closed hasta ligarse mediante un verificador semántico a un reporte/cohorte exacto; ninguna salida promueve reglas automáticamente.

Los hashes prueban integridad local, no identidad humana ni autenticidad remota. Los tiempos autodeclarados se conservan para operación, pero solo producción `verified` con evidencia participa en comparaciones.

### 10. Memoria de serie y portafolio

- Extraer un fingerprint descriptivo del render y su editable.
- Añadirlo al ledger solo con evidencia de aprobación válida; un marcador de toma no equivale a aprobación creativa.
- Compararlo con `series-contract.json`: `locked` conserva calidad, `bounded` permite rangos, `rotating` evita monotonía y `free` responde al mensaje.
- Mantener linaje entre familias y variantes de estructura, formato, estilo, ritmo y transiciones.
- Tratar el primer aprobado como semilla, no como ley. Dos aprobados distintos pueden proponer un default estable; tres activan una recalibración supervisada.
- Ejecutar `scripts/learning_engine.py` en modo recomendación. El motor no promueve, revoca ni amplía alcance por sí mismo.

La similitud es una señal de repetición, no una nota de calidad. Una pieza distinta puede ser incoherente y una pieza parecida puede estar plenamente justificada; ambas requieren juicio editorial.

## Presupuesto de renders

- Edición: preview en vivo y proxies cuando sean necesarios.
- Revisión puntual: render solo del segmento afectado.
- Revisión de ritmo: borrador completo de baja o media resolución.
- Entrega: un render completo de calidad y un segundo únicamente si la validación descubre un defecto real.

El MP4 final debe renderizarse completo porque aplana las capas. Eso no significa rehacer la edición: montaje, recursos, decisiones y cachés se conservan.

## Piso de calidad no negociable

La vía rápida nunca omite:

- Toma aprobada y transcripción verificadas.
- Rostro, ojos y boca protegidos.
- Captions legibles y sincronizados.
- Voz inteligible sobre música y SFX.
- Logos oficiales y datos con procedencia.
- Movimiento motivado por el significado.
- Revisión del inicio, final, transiciones y CTA.
- Validación técnica y visual del archivo final.

## Métricas internas de eficiencia

Por video se registran:

- Tiempo hasta el primer borrador revisable.
- Porcentaje de recursos reutilizados.
- Recursos generados que finalmente no se usaron.
- Cantidad de rondas de revisión.
- Número de renders completos.
- Capas responsables de cada corrección.
- Porcentaje de decisiones aprobadas en primera revisión.
- Defaults heredados aceptados, ajustados o rechazados.
- Diversidad estructural y visual entre los últimos videos, sin convertirla en nota de calidad.

El objetivo es mejorar la primera decisión y reducir trabajo descartado, no simplemente renderizar más rápido.
