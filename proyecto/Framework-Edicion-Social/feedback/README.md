# Feedback y aprendizaje

`events.jsonl` conserva decisiones atómicas y explícitas. Cada línea es un objeto JSON independiente. El objetivo es aprender el atributo correcto —por ejemplo duración de transición o densidad de SFX— sin interpretar la aprobación técnica de un render como gusto general.

## Reglas

- Registrar únicamente feedback explícito o resultados medidos.
- Indicar alcance: proyecto, tema, formato, estilo o global.
- Una aceptación silenciosa no es aprobación.
- Un rechazo contextual no se convierte automáticamente en prohibición global.
- Las métricas de publicación viven separadas del gusto subjetivo.
- Nunca modificar eventos históricos; una corrección crea un nuevo evento que referencia al anterior.

## Estados separados

- QA: validez técnica.
- Editorial: fidelidad, derechos y coherencia.
- Usuario: gusto o aprobación explícita.
- Reutilización: elegibilidad y alcance.
- Rendimiento: resultados reales en plataforma.

El perfil consolidado vive en `../profiles/creative_preferences.json`. Los eventos son evidencia; el perfil contiene únicamente las preferencias vigentes.
