# Mejora continua de edición y revisión

Actualizado: 2026-09-30. Aplicable a 16–20 y próximos lotes dentro del flujo autorizado. Es una práctica por video; no crea una tarea programada.

## Prioridad por evidencia

| Prioridad | Acción | Estado y evidencia |
| --- | --- | --- |
| 1 | Revisar retorno del presentador, retirada de rótulos y captions en límites antes del render completo. Usar t−2/t/t+2 fotogramas, escena breve y cierre; verificar también el pipeline de entrega. | Aplicable ahora. VIDEO-15 registró renders de 380,68 s y 162,39 s rechazados por capas persistentes. Preview SDR no demuestra equivalencia HDR. |
| 2 | Una ingesta por lote; reutilizar WAV, rangos y recursos. Reparar ASR solo en ventanas con dudas. | Aplicado 16–20. Control temprano y paquete compartido; no volver a transcribir el maestro por video. Escucha y aprobación se declaran por separado. |
| 3 | Fijar voz/cortes antes de alinear captions. Activar revisión/limpieza especializada solo cuando el usuario la solicite; entonces comparar A/B y sincronía. | Aplicado a preparación16: voz48k original, bypass provisional por ruido técnico bajo. No se afirma naturalidad escuchada. |
| 4 | Correcciones por rango/capa/dependencias, con handles; un check completo del candidato antes de entrega. | Herramientas existentes `change_impact.py`, `cache_key.py` y `build_review_packet.py`. No afirmar que cache/invalidación son automáticos sin ejecutar y ligar sus manifiestos. |
| 5 | Medir fases y retrabajo desde el comando; conservar fallos sin sobreescribirlos. | Nuevo `scripts/medir_proceso.py`, cinco pruebas funcionales. Primer lint de16 registrado; fallo detectado antes del navegador/render. |
| 6 | Hojas de contacto primero y capturas completas dirigidas a defectos/texto. Agrupar capturas si el perfil verificado lo permite. | Experimento: 44,64% menos en extraer seis imágenes de un VIDEO-15 corto, CFR30/start0. No adoptado como default de QA ni ahorro global. |

VIDEO-13 atribuyó 1.204,4 de 1.233,02 s de render a captura HDR por capas (≈97,7%). El mayor margen medido está en prevenir renders fallidos y estudiar esa fase; cambiar el modelo por sí solo no demuestra aceleración de render. La configuración de workers/códec/resolución solo se compara sobre el mismo tramo y con calidad equivalente, cuando un render esté autorizado.

## Ciclo obligatorio de mejora, sin repetir trabajo

1. Inicio del lote: leer reglas vigentes, localizar fuentes y verificar manifiestos; después releer solo cambios y necesidades específicas. Una lectura truncada se completa en la parte faltante. En terminal imprimir resumen de hallazgos, guardar JSON/logs completos en disco.
2. Antes de proceso pesado: comprobar propietario/carga; máximo dos trabajos pesados globales y uno por dueño. Preparación ligera de otro video puede avanzar sin duplicar ASR, diseño ni escritura de carpeta.
3. Primera composición: lint temprano. Después de corregir estructura, `check` ya incluye lint; no repetir ambos por rutina. Revisar imágenes reales y hallazgos de la ejecución.
4. Cambio local: identificar rango, capa y dependencias; probar allí primero. Hash nuevo invalida aprobación previa del artefacto; QA completo del candidato final se conserva.
5. Tras cada video: registrar cuello de botella, defecto/causa, corrección, prevención reutilizable y tiempos disponibles. Al cerrar cinco, comparar fases con igual cobertura y decidir conservar, ajustar o descartar la mejora.
6. Promover una optimización de cómputo solo con equivalencia visual/audio/timestamps y ganancia medida. Para prevención de defectos, documentar el fallo que evita sin inventar minutos ahorrados. Mantener versiones y evidencias anteriores.

## Medición operativa

```bash
python3 Framework-Edicion-Social/scripts/medir_proceso.py run \
  --out Serie-IA-Negocios-10-Videos/VIDEO-NN/process-events \
  --scope VIDEO-NN --phase check \
  --cwd Serie-IA-Negocios-10-Videos/VIDEO-NN/editable-hyperframes-video-NN \
  --reason "Qué cambió y por qué se necesita este intento" \
  -- npx --yes hyperframes@VERSION_FIJADA check --json

python3 Framework-Edicion-Social/scripts/medir_proceso.py summary \
  --events Serie-IA-Negocios-10-Videos/VIDEO-NN/process-events --scope VIDEO-NN
```

El wrapper ejecuta argv sin shell, devuelve el exit code, registra reloj monotónico, intervalo UTC y stdout/stderr con hash en una carpeta única por intento. No agrega reintentos automáticamente. Variables de entorno/versiones deben quedar en los manifiestos del proceso; no registra el entorno completo ni secretos. No incluir credenciales en argv.

Ingesta común usa scope `LOTE-16-20` y carpeta del lote, sin imputar todo su costo a cada video. Los eventos miden comandos, no pensamiento/espera humana/tiempo total. La suma de procesos puede superar la pared por solapes; el resumen distingue unión de intervalos observados. No mide GPU, energía, costo ni tokens. Procesos desacoplados de preview no quedan medidos hasta su terminación. Logs locales comprueban integridad, no aprobación ni calidad audiovisual. No emitir `production-metrics.json` completo con ceros para fases aún sin medir: consolidar con el schema vigente cuando exista cobertura suficiente.

## Excepción vigente y pendientes honestos

La excepción de `Serie-IA-Negocios-10-Videos/AGENTS.md` permite montaje y preview provisionales sin escucha directa. Conservar `human_review_completed:false`, recibo `ingest-provisional-XX-YY.json` y pendientes explícitos; no falsear ingest-ready ni aprobar tomas ambiguas. Afinar un tramo ambiguo antes de usarlo. Seguir trabajando sobre resultados concretos.

La revisión humana no se confunde con tests automáticos. La aprobación final, QA y autorización de render/publicación siguen sus reglas vigentes. No se rebajan las tres pasadas por acelerar el proceso.

## Prevenciones concretas detectadas en VIDEO-16

- Subcomposiciones sirven assets desde raíz del proyecto: `assets/...`, no `../assets/...`. Corregir también el generador para impedir regresión.
- Una sola entrada HTML de raíz. Conservar variante HDR como template fuera de las entradas activas; no mantener dos roots que puedan duplicar audio.
- Evitar repetir comandos de descubrimiento/benchmark sin cambios ni hipótesis nueva. Usar catálogo/recurso pertinente ya localizado y resultados existentes.
- Dependencias de medios: comprobar primero capacidad del binario existente y usar ruta/versiones explícitas. Si hay instalación necesaria, comprobar que los flujos anteriores siguen funcionando; no atribuir actualización del sistema a ganancia de producción sin medición.

## Aprendizajes del candidato16 v5

- Congelar hashes de la composición y de imágenes antes de distribuir hojas entre revisores. Si cambian durante revisión, revalidar solo estados afectados y preservar el paquete anterior.
- Cada selector de motion debe resolver al elemento correcto sin ambigüedad. Verificarlo antes del check denso: un selector compartido por varios hosts causó un intento fallido de68,921s en16. El muestreo integral del candidato final sigue obligatorio.
- Distinguir cambios de imagen de cambios de mezcla: comparar fuentes/hash y schedule/gain/fades de audio para reutilizar una medición equivalente. Un hashHTML distinto por geometría no justifica repetir transcripción ni voz; registrar el puente de equivalencia sin alterar el informe histórico.
- VIDEO16 registró cinco checks, dos con fallos y230,940s sumados. Esta cifra identifica ciclos para prevenir, no minutos automáticamente ahorrados ni tiempo total de producción. Consolidar una única versión antes del check integral; no repetirlo después de cambios solo de documentación.

## Prevención verificada — captions anidados en export HDR (VIDEO-16, 2026-09-30)

CLI0.8.98 puede forzar visibility:visible!important a descendientes de una capa DOM, aunque el wrapper temporizado esté oculto. En16, las22cajas ocuparon el mismo lugar y quedó el último caption durante todo el MP4. Studio/check correctos no detectaron esa diferencia del compositorHDR.

- Mantener tiempos data-start/data-duration y añadir opacity:0 inicial al wrapper de cada cue, con GSAP determinista que lo activa al inicio y lo apaga al final. Opacity protege todo el subtree. No rebautizar display:flex como causa demostrada ni parchear dependencias instaladas.
- Después de autorización de render, validar primero un export corto del pipeline real con al menos tres cues distintos, un gap vacío y un corte. Luego comprobar todos los cues, pausas y cola en el MP4 exacto. No sustituirlo por screenshots deStudio.
- Smoke16 de4,8s/29,253s de comando: seis estados inspeccionados con cues correctos y lanevacía0/3,5333s. Check actualizado42tiempos/300muestrasPASS70,488s. El render largoV2 sigue sujeto aQA.
- Para color, comparar el destino correcto: HDRtonemapped no acredita paleta idéntica aSDR ni pantallaHDRcertificada. No compensar coloresCSS a ojo. Producir/revisar un derivadoSDR gestionado para reproducción compatible cuando corresponda.

Diagnóstico con código/hash: Serie-IA-Negocios-10-Videos/VIDEO-16/qa-supplements/2026-09-30-caption-render-diagnostic/. V1rechazada se preserva; no modificar videos anteriores aprobados sin solicitud.

## Evidencia de cierre VIDEO16 — 2026-09-30

SDR compatible v2 renderizó36,632s (drawElement/GPU/1worker); másterHDRv2,392,358s (screenshot/GPU/2workers). Son destinos/procesos distintos: no traducir diferencia a ahorro global ni eliminar requisitosHDR. UsarSDR cuando corresponde al destino y conservarHDR requerido; después de cambios de captions comprobar primero un export real corto con cues/gap, luego revisar el MP4 exacto. Captura yencode se superponen; sus duraciones no se suman.

Medición parcial20eventos≈1212,237s no incluye decisiones/revisión/espera/ingesta. Reutilizar ingesta16–20 una sola vez. HDRPCM idéntico permitió heredar auditoría técnica; SDRPCM difería y se verificó dirigido, sinASR/loudness repetidos. Registro de comandos yhashes enVIDEO16. Escucha humana permanece por confirmar; ninguna métrica la reemplaza.


## 2026-09-30 — Rótulos temáticos y estructura interna

- Corrección humana22: rótulos de beats visibles pasaron inadvertidos pese a la regla existente de no mostrar metadatos. Se reemplazaron por significado del contenido en escenas/generador y avisos.
- QA_PROFESIONAL y AGENTS de serie concretan ejemplos en español y exigen leer todos los rótulos/avisos; numeración permitida como navegación temática, no nombre de escena.
- No basta contraste/layout:22 pasa120muestras y44/44contrastes, además de inspección visual de cinco estados y comparación exacta del alcance. Renders anteriores conservados y marcados históricos; el editable corregido requiere nueva captura de imagen para MP4.
- Optimización acotada: reutilizar voz, corte, medios y timings inalterados por hashes; no repetir ASR ni mezcla para una corrección textual. Una imagen modificada impide reutilizar/remuxear el stream gráfico antiguo como si estuviese corregido.21 revisado en paralelo por solicitud explícita del usuario; resultado se añade al cerrar.


## 2026-09-30 — Gate obligatorio de texto visible y aprobación22

- Usuario aprueba22 y solicita documentar regla sin omisiones. Causa identificada: se interpretaron nombres de estructura como navegación válida pese a la prohibición existente; el check técnico no evalúa esa intención.
- Nuevo `scripts/validar_texto_visible.py`: recorre HTML activo/subcomposiciones, registra hashes e inventario, bloquea etiquetas conocidas con numeración/anticipación, falla ante referencias ausentes. Excluye notas técnicas, script/style/captions y capas inline display:none.
- Cinco pruebas de regresión PASS: rechaza etiqueta numerada/aviso y texto anidado; acepta rótulos contextuales y separa captions/IDs/notas ocultas; falla cerrado ante fuente activa ausente. No pretende demostrar semántica universal.
- Wrapper22 ejecuta gate antes de render, aborta ante fallo y conserva informe único. Wrapper21 lo incorpora después de su render en curso. AGENTS/QA obligan usar el gate y revisar visualmente todo el texto; futuras ediciones deben conectar la misma entrada, sin saltarse wrapper.
- Aprobación22 ligada a hashes del HTML corregido; exportación local en curso. Escucha humana no declarada por esa aprobación.21v2 exportado yQA técnico/modelo visual PASS, cierre especializado en curso.


## 2026-09-30 — VIDEO22: microacción de compra frente a metáfora abstracta

- Feedbackhumano rechaza mano/pasos por falta de contexto. Se aplica regla globalIMAGENES_CONTEXTO_REALISMO: escena generada específica de pago de auriculares como ilustración de comprar, sin afirmar caso/producto real. Caso22 añadido a regla existente; recurso previo conservado.
- Fuente/generador/ledger alineados; root solo cambia src/alt. Cinco estados del apoyo y161frames de nuevoMP4 inspeccionados. Check0.8.99PASS120/44, upgradedesde0.8.98validado. Render201,232s, QA3,842s, muestreo3,465s.
- Audiooriginal fuente/hash/timing intactos, pero AAC delrenderer nuevo varió; se copia AACv1sinencode sobre imagenv2. Identidad de ambosstreams demostrada yQA del remux final3,797s. Preservar audio codificado evita cambios no pedidos en una revisión solo visual; no transcribir ni limpiar de nuevo. Sin atribuir ahorro globalcontrolado.
- Recursos/documentación/recibos y versiones históricas preservados; aprobación específica de imagen nueva y escucha humana porconfirmar, sin publicación.
