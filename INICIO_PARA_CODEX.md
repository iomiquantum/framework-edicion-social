# Inicio portátil 2.1 — Windows y Mac

Antes de continuar, lee `INICIO Y CONFIGURACION DE FRAMEWORK.md`. El asistente se inicia con `tools/asistente.py` o el lanzador nativo. Las instalaciones/modelos requieren autorización explícita para el plan presentado. No abras la carpeta Mac histórica ni modifiques proyectos externos.

Para editar abre `proyecto/` en Codex. Cada nuevo lote conserva `Lotes/<id>/CONTEXTO.json`, `MASTERS.json`, `GUION.md`, `ABRIR_EN_CODEX.txt` y `00-INGESTA/`. Sigue la instrucción generada y las reglas del proyecto. Las carpetas reservadas son preparación: selección provisional de plantilla, paleta y QA todavía pendiente.

Las skills de edición se incluyen en `proyecto/.agents/skills/`. Revisa su contrato antes de montar. La referencia de color del asistente no cambia geometría ni crea una aprobación. El estilo base sugerido está subordinado a la identidad de la plantilla; no uniformar las 30 propuestas.

Audio: `python tools/audio.py doctor` desde la raíz de la entrega, o el `audio_multimedia.cmd`/`audio_multimedia` de la copia. Modelo/entorno deben pasar el doctor. ASR portátil: `runtime/audio/Scripts/python.exe tools/transcribir.py --source <master> --out <lote>/00-INGESTA/transcript.json` en Windows; `runtime/audio/bin/python` en Mac. No descarga modelos implícitamente; reutiliza el JSON por hash y verifica palabras/sincronía. Este motor no tiene equivalencia medida con ASR del Mac original.

Al trasladar un trabajo activo, actualiza rutas a los masters y reconfigura runtime en el nuevo sistema. La configuración y las rutas históricas del texto siguiente son antecedentes; esta entrada 2.1 es la guía vigente de inicio. No interpretes pruebas históricas de Mac como pruebas de Windows ni como aprobación de un video nuevo.

## Guías para alumnos y progreso — 2.1

INICIO WINDOWS.cmd / INICIO MAC.command abren GUIASUPERDETALLADA.html mediante el servidor local. MI-PROGRESO conserva guía, borrador y guion de grabación; una marca manual nunca certifica herramientas instaladas, escucha, revisión humana ni aprobación editorial. Esperar confirmación de escritura, conservar datos existentes y resolver conflictos de revisión sin sobrescribir otra ventana.

GUIA_GRABACION_MASTER.html enseña los cinco marcadores originales compact_v2. Los bloques de guion y marcador se dicen; las pausas se hacen sin leerlas. La pausa didáctica de 1–2 s no cambia reglas de montaje. Repetir la frase anterior completa con Corregir mantiene abierta la toma; aún requiere Aprobada o Descartar. Fin de sesión no sustituye ese cierre.

Verifica que los números del master correspondan a los VIDEO-NN reservados. Los ejemplos empiezan en 31; la claqueta real gobierna y cualquier correspondencia distinta debe documentarse antes de montar. El ASR puede escribir números o palabras: revisa números/marcadores desconocidos contra el audio y conserva el original; no inventes aprobaciones. Reutiliza una ingesta por master. El guion de práctica guardado en MI-PROGRESO no reemplaza la voz real ni se adjunta silenciosamente al lote: contrástalo con el contexto entregado.

---

## Memoria conservada de la entrega ligera 1.1

# Memoria operativa para continuar editando en Windows

Esta entrega conserva el sistema de edición y sus aprendizajes, sin los videos anteriores. La edición ligera se preparó el 2026-10-06 por petición del usuario. El proyecto original Mac y su flujo no se modificaron.

## Documentos que gobiernan una edición nueva

1. `proyecto/AGENTS.md` y `proyecto/BITACORA_CURSO_EDICION.md` conservan instrucciones e historia. Las rutas absolutas de Mac que aparezcan son antecedentes, no ubicaciones activas en esta PC.
2. `proyecto/Framework-Edicion-Social/README.md` enlaza el flujo completo, QA y las instrucciones permanentes. Leer también `FIDELIDAD_Y_DIVERSIDAD_PLANTILLAS.md`, `SUBTITULOS_CONTEXTO_Y_LECTURA.md` y las guías de audio aplicables.
3. `proyecto/Framework-Edicion-Social/profiles/creative_preferences.json` conserva preferencias y sus alcances. Los perfiles de flujo 1/2/3 se conservan; el predeterminado sigue siendo 1. No convertir resultados experimentales en mejoras demostradas.
4. `proyecto/Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/CATALOGO_MAESTRO_01_A_30.json` y su visor conservan las 30 fichas/tableros de diseño y sus estados originales. Elegir por mensaje, voz y geometría, no por azar ni por cambiar colores.
5. `proyecto/Framework-Edicion-Social/styles/` conserva tres estilos portables. `creative-recipes/` conserva los 18 módulos declarativos; no son un generador automático de videos terminados.
6. `proyecto/plantillas-codigo/T01` a `T30` conservan referencias de HTML/CSS/JS extraídas. La extensión `.referencia` evita presentarlas como editables listos: sus textos, timings y nombres de medios pertenecían a ejemplos anteriores. Usar su composición/movimiento y adaptarlos a la nueva voz. No convertir todas las plantillas en una única composición genérica.
7. `proyecto/recursos-reutilizables/catalogo.json` localiza SVG/fuentes extraídos, deduplicados por hash y con origen. `Framework-Edicion-Social/library/` conserva iconos, música, SFX, licencias, procedencia y feedback. Extraer un recurso no le otorga aprobación nueva ni pertinencia universal.

## Secuencia para un video nuevo

- Instalar y verificar herramientas con el perfil de la PC. Los lanzadores Windows viven en la raíz de esta entrega; no ejecutar wrappers Homebrew que aparezcan en referencias históricas.
- Preparar `VIDEO-NN` con la acción `nuevo`, elegir plantilla y colocar únicamente el nuevo bruto/lote en `source/`.
- Leer documentos, ficha y tablero originales. Guardar el recibo de inicio con hashes de los documentos realmente consultados y pendientes reales. El generador de carpeta no acredita esa lectura ni revisión.
- Aplicar ingesta/ASR compartidos por lote y reutilizar resultados verificados. La voz real determina montaje, subtítulos y duración.
- Resolver geometría y recursos pertinentes, proteger rostro/gestos y revisar maqueta/fidelidad antes de montar la composición completa.
- Integrar audio habitual, hook con SFX y contraste por frase. El entorno avanzado de evaluación asistida sigue pendiente de portabilidad/calibración Windows; no afirmar escucha o equivalencia sin evidencia. La limpieza especializada se activa solo por petición explícita.
- Construir el editable con las skills HyperFrames disponibles en la PC. Conservar la identidad de la plantilla; completar `windows-project.json` con el hook real y color de entrega, y el plan SFX con recursos verificables.
- Ejecutar los controles existentes, las tres pasadas, preview y aprobación para render; después QA sobre el MP4 exacto. Ninguna aprobación del catálogo o del historial aprueba automáticamente el video nuevo.
- Guardar versiones y registrar cambios/validaciones/tiempos realmente medidos en bitácora y changelog de esta copia.

## Qué se conservó como historia y qué está activo

Las aprobaciones anteriores están documentadas en la memoria y `evidencia/historico-v1/`. Los MP4 a los que se referían ya no están en esta entrega. Por eso el registro operativo del banco Windows representa **referencias de código sin aprobación de un render activo**. No se revocó ni alteró la aprobación original en Mac. La aprobación de las 30 propuestas de diseño se mantiene en su catálogo, con alcance separado.

La instalación no trae Node, Python, FFmpeg, Chrome, venv ni modelos de la Mac. Se instalan en destino. No se declara Windows probado ni paridad audiovisual certificada desde la preparación en Mac.

## Dos computadoras

Mismas reglas, plantillas y calidad. PC A (GTX/8 GB): un trabajo pesado y memoria baja. PC B (UHD620/16 GB): preparación/revisión u otro video independiente, inicialmente un worker. Cada equipo usa su copia local y entrega versiones cerradas; los locks de esta carpeta no coordinan dos computadoras. No copiar configuraciones locales ni sincronizar resultados hacia el framework original Mac automáticamente.
