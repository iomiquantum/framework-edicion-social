# STYLE 002 — Tech Editorial Color

Primer estilo probado en un reel completo del framework. Combina presentador, tarjetas editoriales, iconografía original y cortes conceptuales a pantalla completa. El movimiento responde a cambios de idea y no a intervalos arbitrarios.

## Firma visual

- Base carbón de alto contraste.
- Blanco para lectura y amarillo solo para énfasis puntual.
- Cian, teal, coral, violeta y menta para diferenciar conceptos.
- Captions de una o dos líneas en la zona inferior segura.
- Tarjetas pequeñas en espacio negativo; ojos y boca son zonas protegidas.
- Cutaways de 4–6 s cuando una metáfora visual explica mejor que el talking head.

## Sustitución de estilo

Una variante puede cambiar tipografía, paleta, tarjetas y motion manteniendo montaje, voz, tiempos, captions, imágenes aprobadas e iconos. Cambiar significado, cortes o recursos requiere una variante editorial nueva.

## Perfil de movimiento y audio V2

- Punch-ins y regresos visibles de 9–12 %, con origen de transformación adaptado al rostro y sin cortar ojos, boca, cabello o mentón.
- Cinco wipes direccionales de aproximadamente 0,55 s, reservados para cambios semánticos.
- 22 eventos SFX localizados, con `data-volume` inicial aproximado de 1,05–1,75 y auditoría obligatoria en altavoz de teléfono.
- Grupos independientes para voz, música y SFX; carve dinámico de música contra voz con `strength: 0.8`.
- Logos oficiales y cutaways conceptuales a pantalla completa; no se generan marcas con IA.

Implementación histórica V1: `editables/hyperframes-full-v1/index.html`.

Implementación V2 validada de referencia: `editables/hyperframes-full-v2/index.html`. Su entrega independiente y sus mediciones viven en `CAMBIOS.md` y `renders/manifests/MIGUEL_REEL_COMPLETO_PRO_V2.json`.
