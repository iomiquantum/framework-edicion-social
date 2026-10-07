# QA profesional de video

Este contrato convierte la revisión final en evidencia verificable sin confundir dos clases de decisión:

1. **Hard gates:** requisitos objetivos de integridad, fidelidad, seguridad y entrega. Se comprueban de forma automática o híbrida. Un `fail` bloquea siempre la entrega.
2. **Criterios editoriales:** juicios humanos sobre ritmo, claridad, intención y calidad percibida. No se reducen a una métrica automática y requieren firma editorial.

La plantilla operativa vive en [`templates/qa-scorecard.json`](templates/qa-scorecard.json) y su contrato de datos en [`schemas/qa-scorecard.schema.json`](schemas/qa-scorecard.schema.json). Se crea una copia por cada render candidato; nunca se reutiliza el scorecard de un render anterior cambiándole únicamente el nombre.

## Estados

| Estado | Significado | Consecuencia |
| --- | --- | --- |
| `pass` | El criterio fue ejecutado y existe evidencia suficiente de cumplimiento. | Continúa. |
| `warn` | El criterio fue ejecutado; existe una desviación acotada que no invalida la pieza. | Exige evidencia, nota y aceptación editorial antes de entregar. |
| `fail` | El criterio no cumple su requisito. | Un hard gate bloquea automáticamente. Un criterio editorial exige corrección o una decisión editorial documentada. |
| `not_run` | No se ejecutó o no existe evidencia suficiente. | Un hard gate requerido mantiene la entrega bloqueada; un criterio editorial mantiene la revisión pendiente. |

`not_run` no equivale a “no aplica”. Cuando un control sea genuinamente condicional, debe llevar `required: false` y una nota que explique por qué no aplica al render. No se marca `pass` por ausencia de revisión.

## Regla de entrega

La propiedad `summary.delivery_allowed` solo puede ser `true` cuando se cumplen todas estas condiciones:

- no existe ningún hard gate en `fail`;
- no existe ningún hard gate requerido en `not_run`;
- todo hard gate en `warn` tiene evidencia, explicación y aceptación editorial;
- la revisión editorial está completa y firmada;
- no queda ningún criterio editorial en `fail` o `not_run` cuando sea requerido;
- toda excepción referenciada está resuelta;
- `summary.delivery_decision` es `ready`.

**Cualquier hard fail bloquea la entrega, aunque exista una excepción.** La excepción documenta contexto y riesgo, pero no cambia el resultado de un requisito duro. El hard gate solo deja de bloquear después de corregir, volver a ejecutar el control y obtener `pass` o un `warn` técnicamente válido.

Ninguna recomendación del motor de aprendizaje, default de serie, similitud con un aprobado ni resultado de rendimiento puede anular esta regla. La memoria acelera preparación y selección; el render exacto conserva su propio QA.

No se calcula una nota porcentual. Noventa y nueve controles aprobados no compensan una fuente incorrecta, un fonema cortado, un activo sin derechos o un archivo corrupto.

## Qué revisa cada sección

### Fuente y toma

- Hash del original y correspondencia con el manifiesto de ingesta.
- Inmutabilidad de la fuente.
- Asociación inequívoca entre marcador, toma aprobada, `cut-plan` y rangos usados.
- Ausencia de claqueta, esperas posteriores, tomas descartadas y material fuera de rango.
- Si hay varias tomas aprobadas, elección humana de la interpretación más adecuada.

### Fonemas y cadencia

- Primera y última palabra completas; ataques consonánticos y sílabas finales intactos.
- Ausencia de clics, dobles fonemas, respiraciones partidas, palabras solapadas y saltos de room tone.
- Correspondencia de hashes entre transcripción, `cut-plan` y montaje final.
- Escucha humana de respiración, énfasis, pausas semánticas y continuidad expresiva.

### Captions

- Fidelidad a lo realmente dicho, incluidos nombres, marcas y cifras.
- Sincronización posterior al cierre del montaje de voz.
- Contraste, tiempo de lectura y ausencia de clipping o colisiones.
- Jerarquía humana de frase base, palabras clave y CTA sin enfatizarlo todo.

### Rostro, gestos y zonas seguras

- Ojos, boca, manos, rostros y sujetos significativos visibles cuando deben estarlo, tanto en la toma principal como en imágenes generadas, B-roll y cutaways.
- Reencuadres sin cortes accidentales ni saltos de origen.
- Preflight con la guía o preview del destino declarado.
- Uso humano del espacio negativo; texto y gráficos se colocan después de inspeccionar el sujeto, no encima de él.
- Si un tratamiento de fondo aporta valor pero invade al sujeto, comprobar primero la composición por capas: placa original abajo, gráfico al medio y recorte sincronizado del sujeto arriba.
- En toda máscara revisar cabello, orejas, hombros, manos, apoyacabezas, halos, parpadeo del matte y sincronía exacta con zooms o reencuadres; el suavizado se aplica al alfa, no al rostro.
- La transparencia de video debe verificarse en el MP4 final, no solo en preview. Si el compositor HDR aplana o ignora el alfa, precomponer únicamente el tramo afectado en el mismo espacio HLG, aplicar el tratamiento con el matte invertido sobre el fondo y conservar sin reinterpretación los píxeles del sujeto.
- Escalar títulos según el espacio negativo realmente disponible, manteniendo jerarquía y aire; no reducirlos por rutina cuando existe una zona amplia y segura.

### Visuales semánticos

- Ningún dato, logo, interfaz, resultado o caso real inventado.
- Hash, procedencia, licencia y elegibilidad vigente de cada activo.
- Bloqueo de cualquier activo `explicit_rejected`, `deprecated`, `ineligible` o `do_not_reuse`.
- Correspondencia temporal entre recurso y beat hablado.
- Correspondencia inequívoca de iconos y SVG con la frase activa; un recurso ambiguo o meramente decorativo se elimina.
- Balance entre rostro, overlay, B-roll, cutaway y descanso visual.

### Color

- Ausencia de clipping destructivo, flicker, banding y saltos entre cortes.
- Revisión humana de piel, balance de blancos, exposición y coherencia entre planos.
- Una fuente HDR HLG o PQ no puede entrar directamente en un render declarado SDR si el compositor no demuestra una transformación de color gestionada. Primero se crea y verifica un intermedio BT.709 trazable —o se conserva un flujo HDR extremo a extremo—; cambiar etiquetas o forzar `SDR` no constituye conversión.
- El preflight debe comparar el mismo fotograma antes y después de la transformación, comprobando piel, blancos, prenda y fondo. Piel lavada, gris, sobreexpuesta o con saturación incoherente es `fail`, aunque `ffprobe` reporte BT.709 correcto.
- Paleta compatible con tema y tono, sin aplicar mecánicamente un único acento.
- Máscaras y capas de primer plano deben conservar los píxeles y el espacio de color de la grabación original; bloquear la entrega si piel o vestuario cambian perceptiblemente o aparece un salto de color al entrar o salir del efecto.
- Comparar al menos un fotograma del precompuesto con el original en la zona del sujeto y volver a comprobar el MP4 exportado a ambos lados de la transición.

### Audio, música y SFX

- Sincronía audiovisual, canales completos y ausencia de silencios accidentales.
- True peak, clipping y frecuencia de muestreo conforme al perfil de entrega.
- Voz inteligible sobre música, SFX y procesamiento.
- Elegibilidad y hashes actuales de música y efectos.
- Escucha humana de motivación semántica, sincronía, fatiga y espacios de descanso.
- En video corto, la firma inicial puede usar una o dos capas breves durante los primeros 600 ms, siempre ligadas a la entrada o énfasis visual; no añadir novedad auditiva sin evento correspondiente.
- Revisar que el hook sonoro sea perceptible en altavoz de teléfono sin competir con el primer fonema ni reducir la claridad de la voz.

### Estructura, hook y CTA

- Fidelidad al significado y orden de la toma aprobada.
- CTA completo y correcto cuando exista en el brief o en la toma.
- Hook comprensible y honesto, sin promesas superiores al contenido.
- Cuando el hook se coloca sobre una zona luminosa o variable, usar una placa o sistema de contraste consistente con la familia visual, aprovechando el espacio negativo y sin invadir el sujeto.
- Progresión clara y cierre visual y narrativo completo.

### Preflight visual antes del render completo

- Generar una hoja de contacto o storyboard en el aspecto final con, como mínimo, hook, desarrollo, B-roll o transición crítica y cierre.
- En derivados por plataforma se genera una hoja de contacto independiente por archivo final. Revisar solo una variante o snapshots neutrales no valida las demás.
- Revisar cada captura al 100 % y a tamaño de teléfono. Ningún título, banner, caption o gráfico puede cubrir cabello, cabeza, ojos, boca, manos o el sujeto principal; cuando exista espacio, se prioriza reencuadrar o bajar el video antes que reducir mecánicamente la jerarquía tipográfica.
- En talking head, captions persistentes se colocan por defecto debajo del mentón, sobre pecho o espacio negativo. Cualquier invasión breve del rostro exige intención documentada, duración medida y revisión cuadro a cuadro; no se presume aceptable por ser una transición.
- Verificar que cada placa, fondo, resaltado y contenedor cubra íntegramente su texto, conserve el padding previsto y no termine en un borde incompleto, salvo que esa ruptura esté documentada como una decisión intencional.
- Dentro del área renderizable solo puede aparecer texto destinado al espectador. Timecodes de trabajo, nombres de beats, números de escena, instrucciones de animación, etiquetas como `hook`, `pattern break`, `caption` o `cierre`, y cualquier nota de composición deben permanecer fuera del fotograma o en una capa técnica no renderizable.
- Los rótulos visibles de plantillas describen el contenido de la voz real, nunca la estructura narrativa. No mostrar «la pregunta», «el contraste», «el ejemplo», «la idea», «tu experiencia», hook o cierre como nombres de etapas. Una numeración solo se conserva como navegación temática útil; los nombres técnicos de beats quedan en archivos y notas internas. Revisar todos los rótulos y avisos siguientes antes de renderizar.
- Confirmar que todo el texto cabe, mantiene contraste y permanece dentro del cuadro y de las zonas seguras del destino.
- Verificar los límites entre captions adyacentes: la salida de una frase debe terminar antes o exactamente cuando entra la siguiente. Extraer al menos un fotograma del MP4 real en un límite crítico; un cruce breve de opacidad también cuenta como solape si ambas frases siguen siendo legibles.
- El render completo queda bloqueado hasta que este preflight visual pase o las excepciones queden justificadas y registradas.

### Validación técnica

- Proyecto HyperFrames válido y sin errores de composición o render.
- Resolución, orientación, aspecto, fps, códecs y audio según destino.
- Decodificación completa del MP4, duración y streams esperados, hash final.
- Render determinista y manifiesto con versiones y dependencias fijadas.
- Revisión humana de cuadros negros, freezes, tearing, aliasing, assets tardíos, transiciones lentas sin intención o dobles exposiciones confusas entre sujetos.
- Hoja de contacto o fotogramas representativos aprobados por el preflight visual antes del render completo.
- Fotogramas del MP4 final en transiciones de captions, B-roll y CTA; los snapshots HTML no sustituyen esta comprobación.

### Dispositivos

La pieza se reproduce completa, a velocidad normal y sin saltar tramos:

1. Con audífonos o monitores, para detectar empalmes, ruido, clicks, picos y enmascaramiento.
2. En altavoz de teléfono, para confirmar que la voz y el mensaje sobreviven a un sistema pequeño.
3. En pantalla de teléfono al tamaño real de consumo, para revisar captions, rostro, CTA, contraste y zonas seguras.

Una escucha de segmento sirve para iterar, pero no sustituye las reproducciones completas exigidas para la entrega.

### Derivados por plataforma

Instagram Reels es el máster social universal por defecto. Si el mismo MP4 cumple encuadre, safe zones, captions, CTA, duración y requisitos técnicos de TikTok y Shorts, se reutiliza exactamente el mismo archivo y no se renderizan derivados redundantes. Cada superficie conserva su propia preview, pero puede referenciar el mismo SHA-256.

El QA del máster neutral no se transfiere automáticamente a una variante materialmente distinta. Cada nuevo archivo recibe su propio preflight técnico y revisión visual en la superficie o dispositivo representativo. Esa revisión conserva el `profile_id` y el SHA-256 exacto; si cambia un byte, queda inválida.

Antes de autorizar otro render, registrar el motivo material. Cambios decorativos menores, nombres de archivo, copy, hashtags, portada o metadata externa no justifican una variante. Sin diferencia material, el gate exige `reuse_instagram_master`.

Cuando el usuario rechaza un derivado, su estado anterior se invalida inmediatamente aunque hubiera pasado controles técnicos. El archivo se conserva en un archivo de rechazados, su manifiesto registra la causa y no vuelve a enlazarse como candidato vigente. La corrección recibe revisión, hash y manifiesto nuevos; nunca se reescribe el rechazo como si no hubiera ocurrido.

Antes de construirlos, `content-lock-evidence.json` registra el inventario de proyecto, cut-plan, mezcla y activos por ruta, tamaño y SHA-256. `build_publish_package.py` vuelve a verificar ese inventario, SDR, HDR, recibos, perfil y catálogo; materializa el paquete completo mediante staging y sella package, adaptación y briefs. Un paquete válido habilita trabajo de derivados; no aprueba ni publica sus MP4. Cada target mantiene pendientes `derivative_render`, `technical_delivery_check`, `live_platform_preview`, `semantic_match` y `human_publication_approval` hasta recibir evidencia propia.

`ready_for_derivative_build` solo significa que el paquete local puede usarse para construir el derivado. Los sellos SHA-256 prueban integridad y linaje de archivos locales; no son una firma de identidad humana, una autenticación de cuenta ni evidencia suficiente de publicación remota.

Las guías de zona segura de Studio y `platforms/catalog.json` son overlays de trabajo. No se queman en el render y no sustituyen la preview real. Un derivado no puede declararse listo si altera toma, cortes, voz, significado o identidad de activos del máster aprobado.

## Evidencia

Todo check en `pass`, `warn` o `fail` contiene al menos un objeto en `evidence`. La evidencia debe permitir que otra persona reproduzca o inspeccione la decisión.

- Un defecto localizado usa `start_s` y `end_s` sobre la línea de tiempo del **render final**, no sobre el original.
- Un cuadro específico usa `frame` y el fps fijado por el manifiesto.
- Un resultado automático guarda comando, métrica, valor, unidad y, cuando exista, ruta o hash del reporte.
- Una escucha registra dispositivo, observador y tramo.
- Una inspección global puede apuntar al archivo completo; no se inventa un tiempo artificial.
- `warn` y `fail` siempre explican el hallazgo en `notes`.

Ejemplo de evidencia temporal:

```json
{
  "evidence_id": "EVID-VIDEO01-CAP-001",
  "kind": "timestamp_range",
  "artifact_path": "outputs/VIDEO-01-review.mp4",
  "artifact_sha256": "REEMPLAZAR_CON_SHA256_DEL_RENDER_EXACTO",
  "start_s": 4.2,
  "end_s": 5.1,
  "frame": null,
  "device": null,
  "command": null,
  "metric": null,
  "value": null,
  "unit": null,
  "observed_by": "editorial-review",
  "recorded_at": "2026-09-25T10:30:00-05:00",
  "note": "La segunda línea invade la zona reservada para controles de plataforma."
}
```

## Excepciones justificadas

Una excepción existe para conservar una decisión consciente, no para ocultar un defecto. Cada registro incluye:

- IDs exactos de los checks afectados;
- rango temporal cuando la excepción sea local;
- razón editorial o técnica;
- riesgo aceptado;
- controles compensatorios;
- solicitante, responsable de aprobación y fecha;
- disposición `pending`, `accepted`, `rejected` o `superseded`.

`hard_gate_override` siempre es `false`. Una excepción aceptada puede justificar un `warn` o una decisión editorial contextual, pero nunca convertir un hard gate en `pass` ni autorizar la entrega con un hard gate en `fail`.

## Secuencia operativa

1. Copiar la plantilla para el render candidato y completar IDs, rutas, versiones y hashes.
2. Ejecutar primero los hard gates `automatic`.
3. Ejecutar los hard gates `hybrid`, combinando medición con escucha o inspección visual.
4. Registrar evidencia con tiempos sobre el render candidato exacto.
5. Corregir y volver a ejecutar todo hard gate en `fail`.
6. Realizar la revisión humana de todos los criterios editoriales.
7. Reproducir la pieza completa en los tres contextos de dispositivo.
8. Resolver excepciones, actualizar contadores y listas de blockers/warnings.
9. Completar `editorial_signoff`.
10. Marcar `delivery_allowed: true` únicamente cuando la regla de entrega se cumpla completa.

Si el render cambia después de la revisión, se crea un scorecard nuevo o se reinician a `not_run` todos los controles afectados y sus dependencias. La evidencia de otro hash de render no demuestra la calidad del archivo actual.

### Limpieza de voz — requisito desde 2026-09-30

Aplicar [AUDIO_LIMPIEZA_VOZ.md](AUDIO_LIMPIEZA_VOZ.md) antes de mezclar: diagnóstico de ruido, bypass justificado o supresión en copia, comparación A/B, conservación de consonantes/respiración/timbre, compensación de latencia y sincronía. Guardar parámetros y hashes; sin evidencia auditiva no marcar mejora perceptual como pass.

## Prevención verificada — captions anidados en export HDR (VIDEO-16, 2026-09-30)

CLI0.8.98 puede forzar visibility:visible!important a descendientes de una capa DOM, aunque el wrapper temporizado esté oculto. En16, las22cajas ocuparon el mismo lugar y quedó el último caption durante todo el MP4. Studio/check correctos no detectaron esa diferencia del compositorHDR.

- Mantener tiempos data-start/data-duration y añadir opacity:0 inicial al wrapper de cada cue, con GSAP determinista que lo activa al inicio y lo apaga al final. Opacity protege todo el subtree. No rebautizar display:flex como causa demostrada ni parchear dependencias instaladas.
- Después de autorización de render, validar primero un export corto del pipeline real con al menos tres cues distintos, un gap vacío y un corte. Luego comprobar todos los cues, pausas y cola en el MP4 exacto. No sustituirlo por screenshots deStudio.
- Smoke16 de4,8s/29,253s de comando: seis estados inspeccionados con cues correctos y lanevacía0/3,5333s. Check actualizado42tiempos/300muestrasPASS70,488s. El render largoV2 sigue sujeto aQA.
- Para color, comparar el destino correcto: HDRtonemapped no acredita paleta idéntica aSDR ni pantallaHDRcertificada. No compensar coloresCSS a ojo. Producir/revisar un derivadoSDR gestionado para reproducción compatible cuando corresponda.

Diagnóstico con código/hash: Serie-IA-Negocios-10-Videos/VIDEO-16/qa-supplements/2026-09-30-caption-render-diagnostic/. V1rechazada se preserva; no modificar videos anteriores aprobados sin solicitud.

### Gate de texto visible obligatorio — corrección21/22, 2026-09-30

Antes de toda captura de render, ejecutar `Framework-Edicion-Social/scripts/validar_texto_visible.py --project RUTA_EDITABLE --report RUTA_QA_NUEVA.json`. Un resultado `fail` detiene el render: corregir las etiquetas, no omitir el comando ni desactivar el guard. Los wrappers `media-runtime.mjs` de21/22 lo ejecutan automáticamente y fallan si no pueden comprobarlo. Las siguientes ediciones deben incorporar el mismo gate en su entrada de render; no invocar el render por fuera del wrapper para eludirlo.

El informe recorre HTML/subcomposiciones activas y conserva hashes e inventario del texto. Bloquea etiquetas conocidas de producción, incluidas formas numeradas y «SIGUE: UN EJEMPLO». No inspecciona IDs ni nombres de archivos; los captions de voz se distinguen de la navegación editorial. Esta lista no cubre toda forma posible de estructura narrativa: sigue siendo obligatorio leer e inspeccionar visualmente cada rótulo, titular y aviso de contenido. La plantilla define el diseño; no autoriza mostrar el nombre de sus beats.

## Imágenes contextuales y realismo — regla confirmada 2026-09-30

Aplicar [IMAGENES_CONTEXTO_REALISMO.md](IMAGENES_CONTEXTO_REALISMO.md). Un recurso fuera de contexto o con defectos visibles de generación no supera QA aunque cargue correctamente. Revisar la frase exacta, microacción y plausibilidad: anatomía/manos/miradas, perspectiva, sombras/reflejos, equipos/pantallas y textura de piel/tela. Priorizar generación específica cuando la opción disponible no encaja; el banco es alternativa adecuada, no obligación de reutilización. Revisar también el recurso dentro del encuadre y sus transiciones. Mantener origen ilustrativo y aprobación del candidato separados de la regla global.
