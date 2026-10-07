# Motor de estilos

El estilo se selecciona después del análisis semántico y espacial, nunca antes. El sistema puntúa cada preset por tema, intención, ritmo del guion, geometría del A-roll, plataforma y tono de marca. Si dos estilos son compatibles, se propone primero el de mayor ajuste; el segundo queda como variante comparable.

## Contrato de sustitución

Cambiar de estilo puede reutilizar sin reconstruir:

- montaje y tiempos aprobados;
- voz, música y SFX separados;
- transcripción y bloques de captions;
- mapa semántico, cutaways e iconos aprobados;
- zonas protegidas de rostro, manos y UI.

El preset puede sustituir paleta, tipografía, placas, motion, transiciones y mezcla relativa. Si el cambio altera el significado, el orden del guion, los cortes o los recursos, ya no es un cambio cosmético: requiere una nueva revisión editorial.

## Selección mínima

1. Clasificar tema e intención.
2. Detectar acciones reales que conviene preservar.
3. Medir espacio negativo y tamaño del rostro.
4. Identificar silencios intencionales frente a colas descartables.
5. Puntuar estilos compatibles del `catalog.json`.
6. Registrar el estilo elegido, excepciones y recursos reutilizados en el manifiesto del render.

Los estilos permanecen en estado `testing` hasta contar con métricas comparables de varias publicaciones. Una pieza visualmente buena no convierte por sí sola un preset en regla universal.


## Fidelidad y diversidad visual — 2026-09-30

Aplicar [FIDELIDAD_Y_DIVERSIDAD_PLANTILLAS.md](../FIDELIDAD_Y_DIVERSIDAD_PLANTILLAS.md) a nuevos videos/lotes. La identidad incluye estructura, composición, recursos gráficos, encuadre y movimiento, además de color/tipografía. Consultar propuesta/ficha aprobadas desde el inicio; completar `VIDEO-NN/QA_FIDELIDAD_PLANTILLA.md` desde [la plantilla de revisión](../templates/template-fidelity-review.md), con maqueta y estado `conforme_para_montaje` ANTES de composición completa, luego verificación de conservación durante montaje y sobre el MP4 exacto. No exigir comparación con vecinos ni cuota de diferencias. El check técnico no acredita esta revisión editorial. Conservar minimalismo cuando sea propio del estilo y evitar huecos/crops accidentales o gráficos sin función.
