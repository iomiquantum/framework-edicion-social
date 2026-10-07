# Prompt para preproducción paralela de recursos

## Uso rápido en otro chat

Copia este bloque y añade los guiones debajo:

```text
Trabaja dentro de este mismo proyecto. Lee completamente y aplica:

- Framework-Edicion-Social/README.md
- Framework-Edicion-Social/FLUJO_PRODUCCION_RAPIDA.md
- Framework-Edicion-Social/MATRIZ_PRODUCCION_PRO.md
- Framework-Edicion-Social/POLITICA_EDITORIAL.md
- Framework-Edicion-Social/OPERACION_OPTIMIZACION.md
- Framework-Edicion-Social/profiles/creative_preferences.json
- Framework-Edicion-Social/library/catalog.json
- Framework-Edicion-Social/PROMPT_PREPRODUCCION_RECURSOS.md

Voy a entregarte guiones identificados como VIDEO 01, VIDEO 02, etc. Mientras yo grabo, prepara en paralelo sus recursos provisionales para edición. Trabaja con autonomía y no hagas preguntas salvo que falte un dato verdaderamente bloqueante.

Los guiones comienzan después de la línea GUIONES:

GUIONES:
[PEGAR AQUÍ]
```

## Contrato que debe seguir el agente

1. El guion es provisional porque el presentador puede improvisar. No se trata como transcripción final.
2. Todo se organiza por número de `VIDEO`, nunca por número de toma.
3. Cada guion se divide por beats: hook, ideas, ejemplos, entidades, cifras, proceso, contraste y CTA.
3.1 Crear un `creative-blueprint.json` provisional por video con trazabilidad al guion, función visual, arco emocional, descansos y presupuestos; después se reconciliará con la toma aprobada.
4. Antes de generar se construye o consulta el índice semántico del lote. Se reutiliza un recurso aprobado solo cuando el significado encaja, se respetan `avoid_for` y estados de reutilización, y se registra cualquier cooldown como aviso no bloqueante.
4.1 Solo un SHA-256 idéntico demuestra duplicación exacta. El score por descripción y etiquetas no demuestra similitud visual ni aprobación creativa.
5. Si basta cambiar color, encuadre o formato, se crea una variante vinculada al original.
6. Solo se genera lo que falte: imágenes conceptuales, iconos, diagramas, fondos o recursos de apoyo.
7. Los logos deben ser oficiales y verificables; nunca se generan con IA.
8. Cifras, interfaces y evidencia requieren fuente. Si no se verifican, quedan pendientes y no se inventan.
9. La cromática debe ser variada, agradable y coherente con el tema; no todo amarillo o dorado.
10. Los recursos se preparan para 9:16. Los overlays priorizan fondo transparente y espacio para rostro, captions e interfaz.
11. Las imágenes generadas no llevan texto incrustado; el texto se compone durante la edición.
12. Las escenas a pantalla completa deben aportar significado y quedar descritas como cutaways.
13. Los recursos nuevos viven primero dentro de una carpeta por video con estado `provisional`.
14. Nada provisional se promueve a la biblioteca global hasta ser utilizado y aprobado.
15. Cada recurso registra ID, nombre, archivo, descripción semántica, etiquetas, mejor uso, usos a evitar, procedencia, prompt, modelo, licencia, dimensiones, hash y estado.
16. Cada video recibe `PLAN_RECURSOS.md` y `manifest.json`.
17. Al terminar se entrega un resumen de recursos reutilizados, variantes, recursos nuevos y elementos pendientes de confirmar contra la grabación.
18. No seleccionar definitivamente el estilo ni bloquear el blueprint hasta comparar con la transcripción real; `score_style.py` puede abstenerse cuando ningún preset encaje con suficiente confianza.
18.1 Se puede compilar una receta provisional para estimar recursos y esfuerzo, pero debe recompilarse desde la toma aprobada. Ninguna propuesta autoriza producir activos innecesarios, crea `creative-attribution.json` ni convierte una familia en default; la atribución existe solo después de una selección humana real.
19. Crear `CHECKLIST_GRABACION.md` por video con 1–3 planos complementarios concretos, su propósito y una decisión entre `ya disponible`, `grabar ahora`, `resolver después` o `no usar`.
20. El checklist creativo es no bloqueante: si ningún apoyo se graba, se continúa con el A-roll y se documenta el fallback de edición.
21. Para guiones largos, organizar los planos complementarios por locación, utilería y persona para capturarlos en bloque con el menor retrabajo.
22. Los recursos generados después mediante proveedores externos conservan prompt, modelo, proveedor, licencia, fecha, dimensiones, hash y restricciones de privacidad. Nunca se sube metraje sensible sin autorización.

## Estructura de salida

```text
Preproduccion-Recursos/
├── VIDEO-01-tema/
│   ├── PLAN_RECURSOS.md
│   ├── CHECKLIST_GRABACION.md
│   ├── manifest.json
│   ├── imagenes/
│   ├── iconos/
│   ├── logos/
│   └── referencias/
├── VIDEO-02-tema/
└── RESUMEN.md
```

La toma marcada como aprobada y su transcripción serán después la fuente definitiva. Al recibir el metraje se genera un delta entre guion y audio real: se retiran recursos que ya no correspondan y se resuelven únicamente los conceptos añadidos durante la improvisación.
