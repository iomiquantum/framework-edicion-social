# Roadmap de optimización profesional

Este roadmap prioriza velocidad acumulativa sin convertir la edición en una cadena genérica. Cada mejora debe conservar los hard gates, la trazabilidad, la intención del mensaje y la revisión humana.

## Principio de producto

La unidad reutilizable no será únicamente “una plantilla completa”. El framework evolucionará hacia una gramática modular:

```text
hook + estructura narrativa + sistema visual + ritmo/motion + tratamiento sonoro + CTA
```

Cada módulo tiene compatibilidades, restricciones, linaje y evidencia. El selector propone una combinación según contenido, emoción, duración, audiencia, objetivo y plataforma. Una persona aprueba la solución completa.

## Prioridades

| Prioridad | Mejora | Valor | Dependencia | Estado |
| --- | --- | --- | --- | --- |
| P0 | Motor de aprendizaje con evidencia y revisión humana | Aprende sin sobreajuste ni promoción silenciosa | Framework 1.5 | Implementado en 1.5.0 |
| P0 | Recibo exacto de aprobación y doble máster HDR/SDR | Evita aprobar o publicar el archivo equivocado | Framework 1.5 | Implementado en 1.5.0 |
| P0 | Memoria de serie y portafolio de familias | Reutiliza identidad sin clonar videos | Framework 1.5 | Implementado en 1.5.0 |
| P0 | Consola de revisión por timecode + impacto | Convierte feedback en cambios ejecutables sin reabrir capas aprobadas | Contratos 1.5 | Implementado en 1.6.0 |
| P0 | Índice semántico de activos + antifatiga | Reutiliza el archivo correcto y evita repetir recursos, SFX o transiciones | Catálogo + manifests | Implementado en 1.6.0 |
| P1 | Gramática modular de plantillas | Multiplica combinaciones y reduce tiempo de montaje | Portafolio y blueprint | Implementado en 1.6.0 |
| P1 | Selector narrativo contextual | Recomienda estructura por mensaje, emoción y objetivo | Gramática modular | Implementado en 1.6.0 |
| P1 | Orquestador de aprobación atómica | Actualiza recibo, golden master, estado y memoria sin contradicciones | Contratos 1.5 | Próximo |
| P1 | Paquete de publicación | Portada, título, copy, CTA y derivados por plataforma | Máster social aprobado | Implementado en 1.6.0; sin publicación automática |
| P1 | Ingesta normalizada de métricas | Captura ventanas y cohortes antes de intentar aprender rendimiento | Publicaciones reales | Implementado en 1.6.0; esperando datos reales |
| P1 | Controlador del lote | Encadena estados y colas de 30 videos sin duplicar owners ni trabajos pesados | Módulos 1.6 | Plan 1.7 |
| P2 | Tablero de eficiencia y calidad | Mide tiempo, retrabajo, reutilización y defectos por etapa | Métricas de producción | Planificado |
| P2 | Regresión audiovisual de golden masters | Detecta cambios de layout, captions, color, audio o timing tras actualizar herramientas | Referencias aprobadas | Plan 1.7 |
| P2 | Aprendizaje de rendimiento | Ajusta recomendaciones con datos comparables reales | Tres o más publicaciones comparables por familia | Esperando datos |
| P2 | Adaptadores de evidencia externa | Reduce captura manual sin confundir integridad local con autenticidad de plataforma | Flujo manual validado con publicaciones reales | Plan posterior dentro de 1.7 |

## Gramática modular propuesta

### Hooks

- contradicción directa;
- pregunta de autodiagnóstico;
- consecuencia inesperada;
- demostración primero;
- microhistoria;
- dato verificable o comparación.

### Desarrollo

- problema → ciclo → sistema;
- afirmación → evidencia → acción;
- antes → error → después;
- lista progresiva → giro;
- historia → tensión → aprendizaje;
- demostración → explicación → conclusión.

### Sistemas visuales

- talking head con overlays discretos;
- collage editorial;
- split evidence;
- diagrama o sistema;
- B-roll inmersivo a pantalla completa;
- checklist cinética;
- human minimal.

### CTA

- pregunta reflexiva;
- acción concreta;
- guardar/compartir por utilidad;
- comentario con experiencia;
- continuación de serie;
- CTA comercial, solo cuando el objetivo lo exija.

Estas listas son familias extensibles, no cuotas obligatorias. El blueprint selecciona únicamente los módulos compatibles con el mensaje real.

## Presupuesto creativo por lote

Como política interna inicial —no como regla científica— cada lote puede reservar:

- una mayoría de videos para combinaciones ya aprobadas dentro de su contexto;
- una minoría para variaciones adyacentes de una sola familia principal;
- uno o pocos experimentos claramente etiquetados.

No se fija un porcentaje universal hasta medir capacidad y resultados. El production board define cuántos experimentos caben sin retrasar entregas ni multiplicar renders.

## Paquete de revisión ideal

Cada revisión debería mostrar en una sola vista:

- MP4 y hash vigentes;
- hook, beat medio, transición crítica y CTA;
- capas reutilizadas, nuevas y modificadas;
- diferencias frente al aprobado anterior;
- advertencias técnicas, semánticas y de variedad;
- formulario de cambio `tiempo + capa + elemento + instrucción`;
- decisiones separadas: aprobar video, activo, familia o default de serie.

El feedback resultante alimenta directamente `change_impact.py` y evita reinterpretaciones manuales.

## Ola operativa 1.6 implementada

La auditoría del lote muestra que el mayor ahorro inmediato no proviene de otra regla editorial, sino de conectar las ya existentes:

- **Consola de revisión:** `review-packet.json` + `review.html` con MP4/hash, beats, fotograma del problema, comparación de versión, formulario `inicio/fin + capa + elemento + instrucción` y preview parcial sugerida por `change_impact.py`.
- **Índice de activos:** descubrir manifests y carpetas de proyecto, deduplicar únicamente por SHA-256 exacto, rankear por metadatos semánticos declarados, registrar historial por beat y aplicar cooldowns no bloqueantes a activos, SFX y transiciones.
- **Compilador de recetas:** proponer hasta tres combinaciones explicadas de `hook + estructura + sistema visual + motion + sonido + CTA`, con costo estimado, conflictos y opción válida de abstenerse.
- **Paquete multicanal:** generar desde un único máster social aprobado derivados, portadas, copy, manifests, hashes y previews para Reels, TikTok y Shorts; el paquete se materializa por staging, se sella y nunca equivale a publicación.
- **Métricas por cohortes:** ligar receta elegida, MP4 real, entrega, evidencia local y capturas de 24 h, 72 h y 7 días; comparar contextos equivalentes con N de intersección y confusores, sin interpretar causalidad automáticamente.

Línea base previa a la integración 1.5, verificada el 2026-09-25: la serie no contenía `review-decision.json`, `platform-adaptation.json` ni `performance-review.json`; se contaron 140 archivos dentro de carpetas de recursos del lote frente a 17 activos gobernados en el catálogo global. Al cerrar 1.5, VIDEO-01 ya tiene una decisión de revisión ligada a su artefacto; los documentos de adaptación y rendimiento siguen pendientes porque todavía no existe un máster social publicado. Estos conteos son una fotografía operativa, no objetivos permanentes.

La integración 1.6 construyó para la serie un snapshot de 139 activos canónicos desde 237 registros de origen y 11 grupos de duplicados binarios exactos. Nueve eventos corresponden a recursos que sobrevivieron al VIDEO-01 aprobado; los recursos previstos para videos posteriores siguen siendo provisionales. No se creó todavía un paquete real de publicación ni una cohorte: faltan un SDR aprobado, publicación, evidencia local y capturas métricas reales, y los módulos se mantienen bloqueados hasta recibirlos.

Objetivos iniciales de esta ola:

- al menos 95 % del feedback convertido en tiempo, capa y elemento válidos;
- reducir 30–50 % el tiempo entre feedback y tarea ejecutable tras cinco videos;
- 100 % de activos usados con hash, procedencia e historial;
- al menos 80 % de búsquedas con un candidato útil entre los primeros cinco, medido en 20 consultas;
- reducir al menos 50 % el tiempo entre máster social aprobado y paquete de tres plataformas;
- cero promociones automáticas por rendimiento o similitud.

## Plan de la siguiente ola 1.7

La próxima mejora no añadirá más efectos ni otra plantilla aislada. Conectará la operación ya verificada:

1. **Orquestador de cierre atómico:** previsualizar y, con autorización explícita, actualizar recibo, golden master, fingerprint, ledger, uso real y métricas de producción bajo un solo lock y rollback seguro.
2. **Controlador del lote:** representar dependencias, owners, prioridad, estado y cupos pesados de los 30 videos; proponer el siguiente trabajo desbloqueado sin editar ni aprobar por sí solo.
3. **Tablero de eficiencia y calidad:** comparar tiempo por etapa, retrabajo, previews, renders completos, reutilización y defectos; la velocidad nunca compensa un hard fail.
4. **Regresión audiovisual:** comparar golden masters mediante fotogramas de control, captions, loudness, picos, duración y estructura para detectar deriva tras cambios de toolchain.
5. **Preproducción adaptativa:** convertir huecos confirmados del índice y la transcripción real en una cola priorizada de recursos, evitando generar por adelantado piezas que luego no llegan al montaje.
6. **Adaptadores de evidencia externa:** después de validar el flujo manual con publicaciones reales, importar exports o APIs de plataforma conservando cuenta, publicación, ventana y archivo fuente; un conector añade procedencia, pero tampoco sustituye revisión humana.

Orden propuesto: primero orquestador y controlador; después tablero y regresión; luego preproducción adaptativa con los datos observados de los primeros cinco videos. Los adaptadores externos se activan al final, cuando el registro manual ya haya demostrado qué campos y controles hacen falta. Cada módulo tendrá dry-run, escritura explícita, hashes y pruebas adversariales antes de activarse.

## Cuándo activar cada aprendizaje

- Un video aprobado: semilla y evidencia de alcance video.
- Dos videos aprobados distintos: propuesta de default estable de serie.
- Tres aprobados: recalibración supervisada de rangos y variedad.
- Varias publicaciones comparables: hipótesis de rendimiento contextual.
- Proyectos distintos y aprobación explícita: posible preferencia de creador.

Nunca se espera a tener métricas de plataforma para corregir defectos profesionales evidentes. Tampoco se usa una preferencia creativa como prueba de rendimiento.

## Métricas de éxito del roadmap

- menor tiempo hasta primer borrador revisable;
- menos rondas por errores repetidos;
- mayor porcentaje de capas reutilizadas correctamente;
- menos renders completos descartados;
- cero aprobaciones heredadas a hashes distintos;
- cero hard gates anulados por plantillas o métricas;
- cero observaciones de rendimiento sin evidencia local y atribución creativa reproducible;
- variedad observable entre episodios sin pérdida de identidad;
- crecimiento de familias útiles, no solo de archivos almacenados.
