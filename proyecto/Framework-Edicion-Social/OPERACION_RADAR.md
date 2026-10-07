# Operación del radar de tendencias

## Radar de mercado Meta LATAM — 02:30 America/Guayaquil

La investigación de mercado se trasladó el 2026-09-27 al proyecto independiente `/Users/iomijhondavid/Documents/Codex/Investigacion-Mercado-Meta`. `research/market-intelligence/` es un enlace de compatibilidad. Su primera fase prioriza Instagram y usa Facebook como contraste; TikTok y YouTube Shorts permanecen desactivados.

El radar Meta conserva evidencia por URL y fecha y estudia cuentas emergentes. Los 30 videos son una referencia opcional, no un filtro de investigación. La política nueva propone un piloto supervisado y acotado; no se cambió la automatización instalada ni se verificó su estado actual. El radar técnico de edición de las 09:00 descrito abajo permanece separado.

## Radar diario — 09:00 America/Guayaquil

1. Leer `config/radar.json`, el catálogo de fuentes, la última observación y las reglas próximas a revisión.
2. Buscar cambios publicados desde la consulta anterior y señales de los últimos 7 días; usar 30 días solo como contexto.
3. Priorizar Ecuador y español. Si no existe muestra, usar LATAM/español y declarar que es un proxy.
4. Separar plataforma, país, idioma, nicho, formato y distribución orgánica/pagada.
5. Deduplicar por URL canónica, plataforma, patrón y fecha.
6. Registrar hasta cinco cambios materiales; si no existen, registrar `no_material_change`.
7. No promover reglas ni afirmar causalidad.
8. Avisar únicamente ante cambio aplicable de plataforma, señal perecedera bien documentada o contradicción de una regla activa.
9. Comparar cambios oficiales con `platforms/catalog.json`. Proponer un cambio de perfil con fuente, alcance y fecha; nunca sustituir automáticamente una safe zone interna ni convertir una especificación de anuncios en requisito orgánico.

## Informe semanal — lunes 09:00 America/Guayaquil

El informe semanal se ejecuta dentro del mismo ciclo del radar diario para mantener una sola automatización vinculada al proyecto.

1. Consolidar las observaciones de siete días y revalidar fuentes.
2. Revisar reglas vencidas o próximas a revisión.
3. Publicar como máximo tres decisiones: mantener, probar o retirar.
4. Proponer uno o dos experimentos realizables; el resto permanece en cola.
5. Documentar qué cambió, a qué videos aplica, coste, variable y métrica.
6. Declarar limitaciones de acceso y ausencia de evidencia.
7. Actualizar el índice y el changelog sin reescribir informes pasados.
8. Marcar perfiles cuya `evidence_reviewed_at` venció y separar actualización técnica de hipótesis creativa.

## Priorización 0–100

- Encaje con audiencia y tema: 30.
- Calidad y consistencia de evidencia: 25.
- Utilidad para el objetivo: 20.
- Frescura: 15.
- Facilidad de ejecución: 10.

Cada criterio se puntúa de 0 a 5 y se pondera. El total ordena candidatos; no es una probabilidad de viralidad.

- 75–100: candidato a prueba si supera los filtros de alcance y evidencia.
- 55–74: observación.
- 0–54: archivo.

Una tendencia vencida o una afirmación con evidencia C no se transforma en regla por tener una puntuación alta.

## Preflight antes de editar

- Confirmar brief y plataforma destino.
- Consultar reglas vigentes y su versión.
- Revisar zonas seguras en la interfaz real.
- Confirmar términos, marcas, cifras y derechos.
- Seleccionar recursos por significado.
- Definir qué variable se probará y qué permanecerá estable.
- Si el máster ya fue aprobado, generar únicamente deltas compatibles con su content lock y registrar el perfil exacto usado.

## Informe útil

Cada reporte incluye período, cobertura, cambios confirmados, patrones observados, aplicación al proyecto, experimentos, reglas revisadas, fuentes y datos faltantes. Si no se auditó una muestra suficiente, debe decirlo explícitamente.
