# QA de capas HDR, máscaras y estado inicial

Fecha: 2026-10-01. Caso verificado: VIDEO20, HyperFrames0.8.102, render nativo HLG1080×1920. Recibos en `../Serie-IA-Negocios-10-Videos/VIDEO-20/editable-hyperframes-video-20/qa/`.

Al crear o cambiar un diseño que combine video HLG nativo con máscaras o capas HTML/SVG, comprobar pronto un fragmento con el mismo motor HDR. La vista previa usa proxy y puede mostrar bien una máscara que el render nativo omita. No repetir esta prueba cuando no cambia la geometría/lifecycle y existe evidencia exacta aplicable.

1. El primer estado visible debe existir en CSS antes de avanzar la timeline. En VIDEO20, el primer panel usa opacity1 en CSS; sus salidas siguen controladas por GSAP. Un `tl.set(...,0)` solo no evitó el destello de video en el fotograma0.
2. Una máscara/arte que debe cubrir el video nativo debe participar en el contrato temporal: elemento con id único, classclip, data-start y data-duration. En0.8.102 la consulta de apilado nativo `queryElementStacking` enumera `[data-start]`. El SVG estático sin esos atributos se veía en el proxy, pero no recortaba el render. Conservar z-index, geometría, gestos y transparencia del hueco.
3. Preparar una composición de diagnóstico corta desde la fuente actual, conservando el proyecto completo y sus recursos. Registrar hashes, alcance, fps y orden. En20,3s a5fps bastaron para comprobar0s y la primera ventana; motor5.359s. Esta muestra no acredita sincronía, legibilidad dinámica, audio ni resto de la pieza a30fps.
4. Inspeccionar píxeles del diagnóstico, resolver diferencias y renderizar la versión completa. En el MP4 final, revisar frame0, los vecinos de cada cambio de escena/caption y el cierre. Usar hash del archivo exacto y extracción única cuando la herramienta lo permita.
5. Conservar los intentos fallidos. Registrar que un check de layout o un proxy aprobado no certifica el resultado HDR. Medir la prueba y el retrabajo; no atribuir ahorro futuro a partir de este único caso.

Esta receta se integra en las pasadas existentes y no cambia perfiles1/2/3, aprobaciones, QA de cada MP4 ni activación especializada de voz. No reedita archivos aprobados. Un motor o modalidad nuevos requieren volver a verificar la hipótesis; no generalizar el comportamiento de0.8.102 a todos los renderizadores.

Evidencia: `hdr-correction-v1.json`, `check-built-v3.json`, `../qa-smoke-hdr-v1/receipt.json`, `final-boundaries-v1/evidence.json`, `final-boundaries-v2/evidence.json`, `final-editorial-review-v2.json`. El árbol original y los rendersv1/v2 se conservan.
