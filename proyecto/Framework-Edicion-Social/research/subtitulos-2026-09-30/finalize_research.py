"""Persist a scoped read-only export audit and future editorial caption policy.

Does not edit media, editables, approval receipts, platform profiles or template bank.
Shared documentation updates use the project lock, current reads and atomic replace.
"""
import fcntl
import hashlib
import json
import os
import re
import shutil
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FW = ROOT / 'Framework-Edicion-Social'
HERE = Path(__file__).resolve().parent
NOW = datetime.now(timezone.utc).isoformat()
DATE = datetime.now(ZoneInfo('America/Guayaquil')).date().isoformat()
assert DATE == '2026-09-30', 'Review research date before running on another day.'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2) + '\n' if isinstance(value, (dict, list)) else value
    tmp = path.with_name(path.name + '.subtitle-research.tmp')
    tmp.write_text(data, encoding='utf-8')
    os.replace(tmp, path)


def backup(path):
    rel = Path(path).relative_to(ROOT)
    dst = HERE / 'before-framework-update' / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    assert not dst.exists(), f'Preserved version already exists: {dst}'
    shutil.copy2(path, dst)


sources = [
    dict(id='CAP_TIKTOK_SAFE_ZONE_2026', publisher='TikTok for Business',
         url='https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads',
         type='official_platform_specification', published_or_updated='June 2026',
         use='Zona segura variable según dimensiones, descripción y formatos adicionales.',
         limitations='Guía de anuncios; no fija un y universal para subtítulos orgánicos. Preview no específico del dispositivo.',
         access='primary_page_opened'),
    dict(id='CAP_META_REELS_ADS_GUIDE', publisher='Meta, documento de autor alojado por organizador de evento',
         url='https://d3m889aznlr23d.cloudfront.net/img/events/458925814/assets/e042d2be.reels_ads_guide1.pdf',
         type='primary_platform_authored_pdf', published_or_updated='Fecha de edición no declarada; estudios citados 2021–2023',
         use='Referencia de reservar el 35 % inferior en anuncios; página 4 del PDF.',
         limitations='No certifica interfaz orgánica de 2026. Ads Guide actual bloqueada por login. No trasladar CTR/CPA a efecto causal de captions.',
         access='primary_pdf_opened_7_pages'),
    dict(id='CAP_SOUND_OFF_PLOS2024', publisher='Autores / University of East Anglia / PLOS ONE',
         url='https://ueaeprints.uea.ac.uk/id/eprint/96946/',
         type='peer_reviewed_primary_study', published_or_updated='2024-10-07',
         use='Mayor esfuerzo lector sin audio; n=168, contenido inglés con subtítulos ingleses.',
         limitations='No compara nuestros tamaños, posición ni Reels españoles; no estima porcentaje de usuarios actuales sin sonido.',
         access='primary_repository_abstract_opened'),
    dict(id='CAP_TIKTOK_ACCESSIBILITY_CHI2024', publisher='McDonnell y coautores / ACM CHI / Makeability Lab',
         url='https://makeabilitylab.cs.washington.edu/media/publications/McDonnell_CaptionItInAnAccessibleWayThatIsAlsoEnjoyableCharacterizingUserDrivenCaptioningPracticesOnTiktok_CHI2024.pdf',
         type='peer_reviewed_primary_study', published_or_updated='CHI 2024, May 11–16; TikToks collected April 2023',
         use='Consistencia, legibilidad y prácticas de captions: 300 videos y nueve entrevistas.',
         limitations='Muestra situada; no tendencia de frecuencia en 2026 ni prueba causal de retención.',
         access='primary_author_pdf_downloaded_and_text_extracted',
         local_file=str(HERE / 'CHI2024-caption-practices.pdf'),
         local_sha256=sha(HERE / 'CHI2024-caption-practices.pdf')),
    dict(id='CAP_SOCIAL_REVIEW_CHI2026', publisher='Nguyen y coautores / ACM CHI / SInC Lab',
         url='https://sinc-lab.com/publications/2026-04-13-nguyen2026like',
         type='peer_reviewed_systematic_review_primary_abstract', published_or_updated='2026-04-13',
         use='Revisión de 36 trabajos 2015–2025 sobre captions sociales y accesibilidad.',
         limitations='Se verificó resumen primario; no atribuir al artículo una posición o tipografía ganadora.',
         access='primary_author_abstract_opened'),
    dict(id='CAP_NETFLIX_SPANISH_READING', publisher='Netflix Partner Help Center',
         url='https://partnerhelp.netflixstudios.com/hc/en-us/articles/217349997-Spanish-Latin-America-Spain-Timed-Text-Style-Guide',
         type='official_delivery_style_guide', published_or_updated='Fecha de edición no verificada',
         use='Referencia de 17 CPS adultos en español y dos líneas.',
         limitations='Especificación Netflix, no requisito de redes ni permiso para omitir palabras de nuestra voz.',
         access='primary_guide_opened'),
    dict(id='CAP_W3C_SEMANTIC_COVERAGE', publisher='W3C WAI',
         url='https://www.w3.org/WAI/media/av/captions/', type='primary_accessibility_guidance',
         published_or_updated='Fecha de edición no verificada',
         use='Voz fiel, sincronía, sonidos significativos y corrección de captions automáticos.',
         limitations='Aplicar principios no acredita conformidad integral WCAG del video.', access='primary_page_opened'),
    dict(id='CAP_W3C_CONTRAST', publisher='W3C WAI',
         url='https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html',
         type='primary_accessibility_guidance', published_or_updated='WCAG 2.2, página consultada en 2026',
         use='Objetivo interno de contraste 4,5:1 para todo caption.',
         limitations='Escala física del teléfono y fondo variable deben revisarse; px fuente no implica texto grande WCAG.',
         access='primary_page_opened'),
    dict(id='CAP_TIKTOK_CREATIVE_GUIDE', publisher='TikTok for Business',
         url='https://ads.tiktok.com/resources/help/article/creative-best-practices?lang=en',
         type='official_ad_creative_guidance', published_or_updated='June 2025',
         use='Texto para contexto, zona UI y experimentación creativa.',
         limitations='Los 5–10 words/sec del texto publicitario no se adoptan como velocidad de lectura de subtítulos de voz.',
         access='primary_page_opened'),
    dict(id='CAP_CAPCUT_AVAILABLE_FORMATS', publisher='CapCut',
         url='https://www.capcut.com/resource/types-of-captions', type='primary_tool_vendor_description',
         published_or_updated='Fecha de edición no verificada',
         use='Disponibilidad actual de estilos de frase, énfasis y captions dinámicos.',
         limitations='La oferta de una herramienta no mide moda, preferencia ni eficacia independiente.',
         access='primary_vendor_page_search_index_checked'),
]
for source in sources:
    source['checked_at'] = DATE

formats = [
    dict(id='CAP-FRASE-EDITORIAL-001', name='Frase estable',
         use_when=['explicación densa', 'instrucciones', 'tono sobrio'],
         treatment='Bloque de sentido completo visible, sin animación por palabra.',
         motion='Entrada/salida suave de la caja; sin movimiento durante lectura.',
         avoid_when='Una escena exige un énfasis narrativo puntual: se permite combinar con un acento, sin eliminar cobertura.'),
    dict(id='CAP-ENFASIS-SEMANTICO-001', name='Frase y palabras destacadas',
         use_when=['contraste', 'objeción', 'idea principal', 'conclusión'],
         treatment='Conservar frase completa; destacar una o dos palabras relevantes con peso, color o escala moderada.',
         motion='Reservar espacio de énfasis para no alterar saltos ni posición; escala 1,1–1,2 como preset interno.',
         avoid_when='Destacar casi todas las palabras o cuando ya haya un gran titular repetido.'),
    dict(id='CAP-RESALTADO-PROGRESIVO-001', name='Frase visible y resaltado sincronizado',
         use_when=['ritmo conversacional', 'frase con secuencia clara'],
         treatment='Mostrar bloque completo; actualizar énfasis con el tiempo real de cada palabra.',
         motion='Caja y texto base estables; nada desaparece por el resaltado.',
         requires=['Tiempos de palabra verificados y reutilizados de ingesta/montaje'],
         fallback='CAP-FRASE-EDITORIAL-001',
         avoid_when='No hay tiempos precisos, el texto parpadea o el cambio reduce contraste.'),
    dict(id='CAP-IMPACTO-INTEGRADO-001', name='Hito con palabra o cifra protagonista',
         use_when=['hook breve', 'dato clave', 'remate', 'contraste corto'],
         treatment='Acento grande que acompaña una frase legible completa; puede integrarse en ella evitando duplicación.',
         motion='Uso breve por función; vuelve a la base de lectura elegida.',
         avoid_when='Explicación continua convertida en una sucesión de palabras sueltas.'),
]

catalog = dict(schema_version='1.0.0', catalog_version='1.0.0', updated_at=DATE,
               status='adopted_editorial_selection_process_with_unvalidated_style_presets',
               protocol='SUBTITULOS_CONTEXTO_Y_LECTURA.md',
               decision_template='templates/caption-decision.json',
               performance_status='por_confirmar', automatic_selector_implemented=False,
               numeric_defaults_provenance='internal_editorial_starting_points_not_platform_requirements',
               defaults=dict(canvas=[1080, 1920], max_lines=2, font_px_explore=[56,72],
                             font_px_initial=[60,64], line_height_explore=[1.08,1.18],
                             cps_target=[15,18], cps_review_above=20, cps_priority_above=25,
                             multiword_short_cue_review_below_seconds=0.8,
                             contrast_goal=4.5,
                             numeric_thresholds_are_automatic_fail=False),
               placements=[dict(id='CHEST_NEGATIVE_SPACE', instruction='Debajo del mentón, fuera de rostro/gestos y UI.'),
                           dict(id='RESERVED_SAFE_LANE', instruction='Carril dentro de la zona útil, diseñado antes del encuadre.'),
                           dict(id='SCENE_INTEGRATED', instruction='Texto dentro de escena sin ocultar acción ni lecturas competidoras.')],
               formats=formats)

decision = dict(schema_version='1.0.0', status='template_not_a_completed_review', video_id='VIDEO-NN',
                caption_catalog_version='1.0.0', spoken_source_path=None, spoken_source_sha256=None,
                main_format_id=None, editorial_reason=None, beats=[],
                geometry=dict(canvas=[1080,1920], placement_id=None, box_px=None,
                              font_family=None, base_font_px=None, line_height=None, max_lines=2,
                              face_gesture_exclusion_evidence=None, actual_wrap_review_status='not_run'),
                reading=dict(cps_counting='Visible characters including spaces/punctuation over full block duration; once per progressive block.',
                             max_cps=None, over20cps_count=None, short_multiword_cues=[],
                             decisions_for_flagged_cues=[], muted_full_review=dict(status='not_run', reviewer=None, evidence=None),
                             mobile_size_review=dict(status='not_run', display_width_px=None, evidence=None,
                                                     physical_device_review=False)),
                destinations=[dict(platform=p, surface='organic_reels' if p!='tiktok' else 'organic_vertical',
                                   preview_status='not_run', description_and_cta_checked=False,
                                   exact_render_sha256=None, evidence=None)
                              for p in ['instagram','facebook','tiktok']],
                word_timing=dict(required=False, source_path=None, source_sha256=None, checked=False),
                subtitle_sidecar=dict(status='not_run', path=None, sha256=None, duplicate_caption_policy=None),
                exact_export_review=dict(render_path=None, sha256=None, status='not_run', evidence=None),
                performance_status='por_confirmar', approval_not_inferred=True)

observations = {
    'VIDEO-01': 'Derivado Instagram con override de plataforma: texto sobre pecho/parte baja. No atribuir bottom255 o fuente49 del CSS base al MP4: override43 y zona variable. Frase con énfasis útil; relativamente pequeña a tamaño móvil.',
    'VIDEO-02': 'Frase y acento legibles en la muestra, pero letra pequeña y franja muy baja; alto titular compite con lectura. Riesgo de UI inferido, sin captura real de plataforma.',
    'VIDEO-03': 'Bloques completos y contraste; ubicación baja y fuente48 del editable. Revisar ancho derecho y carga del titular en siguientes plantillas.',
    'VIDEO-04': 'Diagrama y caption simultáneos requieren repartir lectura. Franja baja de tamaño48; no repetir esta posición como default.',
    'VIDEO-05': 'Énfasis semántico existente es reutilizable; fuente48 y caja inferior deben ganar presencia móvil y espacio útil.',
    'VIDEO-06': 'Fuente45 y banda baja; la jerarquía favorece mucho el titular. Mantener cobertura y redistribuir peso tipográfico en futuras ediciones.',
    'VIDEO-07': 'Frases relativamente concisas y palabras destacadas útiles. La banda pequeña/baja sigue siendo una referencia débil para UI móvil.',
    'VIDEO-08': 'Frase completa con acento útil; tamaño45 y ubicación baja frente al gran titular. Mejorar jerarquía de lectura.',
    'VIDEO-09': 'Captions bajos. En la muestra se observa unión de frontera de pregunta “seguir?¿Alguien”; comprobar separación entre nodos y puntuación en QA futuro.',
    'VIDEO-10': 'Franja baja con letra45. Se observa frontera “resuelto.¿Qué”; incorporar separación tipográfica explícita y revisión del texto ya renderizado.',
    'VIDEO-11': 'Referencia más fuerte: letra52/peso alto y caption elevado sobre pecho/espacio libre. El ancho casi completo requiere contrastar con UI derecha.',
    'VIDEO-12': 'Mejor tamaño/posición que familias anteriores, pero la muestra de 7,2s muestra tres líneas. El CPS por sí solo no detecta ese problema.',
    'VIDEO-13': 'Letra52–58 con énfasis visible; captions cerca del pecho. Revisar competencia con diagrama y extremo derecho de la caja.',
    'VIDEO-14': 'Letra60–64 y lectura más presente: buen referente visual. Titulares/quotes adicionales deben limitarse según carga y UI.',
    'VIDEO-15': 'Buena presencia y contraste con letra54–60; caption elevado. Conservar lectura clara y comprobar caja completa/UI por destino.',
    'VIDEO-16': 'v4 editorialmente aprobado: carril limpio, separado de rostro/gestos, pero placa y1592–1724 está muy abajo. Mejorar diseño del carril en videos futuros; no mover texto ciegamente sobre las manos. UI real no certificada aquí.',
    'VIDEO-21': 'Letra58 y carril elevado; buena base. Top1400 y alto de dos líneas pueden acercarse a interfaz inferior; cara está alta en esta toma: reflujo antes de subir indiscriminadamente.',
    'VIDEO-22': 'Archivo congelado en esta auditoría, no promesa de última versión permanente. Letra62 y top1380: presencia clara, pero revisar altura de dos líneas e interfaz inferior. Primer cue de0,49s merece reagruparse en futuras decisiones.'
}

audit_path = HERE / 'export-audit.json'
audit = json.loads(audit_path.read_text())
assert len(audit['videos']) == 18
assert sum(v['cue_count'] for v in audit['videos']) == 189
for v in audit['videos']:
    assert sha(v['file']) == v['sha256'], f'Export changed: {v["video_id"]}'
    assert len(v['review_frames']) == 3
    for f in v['review_frames']:
        assert sha(f['path']) == f['sha256']

# Contact sheet: unmodified decoded sample images; labels stay outside each image.
font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
bold_path = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
font = ImageFont.truetype(font_path, 18)
bold = ImageFont.truetype(bold_path, 24)
small = ImageFont.truetype(font_path, 16)
board = Image.new('RGB', (1152, 1576), '#eef1f4')
draw = ImageDraw.Draw(board)
draw.text((24,18), 'Subtítulos en seis exportaciones: posición y tamaño', font=bold, fill='#152338')
draw.text((24,54), 'Fotogramas seleccionados del MP4; tamaño 360×640. Sin interfaz real de la plataforma.', font=small, fill='#425266')
choices = [('VIDEO-01',0,'Frase y énfasis; letra pequeña'),('VIDEO-08',0,'Franja baja; titular dominante'),
           ('VIDEO-12',1,'Cue con tres líneas'),('VIDEO-14',0,'Mayor presencia de lectura'),
           ('VIDEO-16',0,'Carril limpio, muy bajo'),('VIDEO-22',0,'Mayor letra; revisar caja/UI')]
for i,(vid,fi,label) in enumerate(choices):
    v = next(v for v in audit['videos'] if v['video_id']==vid)
    x = 24+(i%3)*376
    y = 96+(i//3)*728
    draw.text((x,y), vid + f' · {v["review_frames"][fi]["time_s"]:.2f}s', font=bold, fill='#152338')
    frame = Image.open(v['review_frames'][fi]['path']).convert('RGB')
    assert frame.size == (360,640)
    board.paste(frame, (x,y+36))
    draw.text((x,y+686), label, font=font, fill='#263c55')
draw.text((24,1550), 'Auditoría parcial: no equivale a reproducción completa, escucha o certificación de destinos.', font=small, fill='#425266')
board.save(HERE / 'COMPARACION_6_EXPORTACIONES.png')

shutil.copy2(audit_path, HERE / 'export-audit.before-visual-review.json')
audit['status'] = 'scoped_visual_review_complete'
audit['reviewed_at_utc'] = NOW
audit['reviewer'] = 'Codex root; model visual inspection of 18 contact sheets / 54 selected decoded MP4 frames'
audit['limitations'] = ['Not complete playback, listening, user testing or live-platform preview.',
                        'Editable cue metrics are separate from exact historical-render source binding.',
                        'HDR previews were tone mapped for inspection, not HDR/color certification.',
                        'UI risks are inferred from internal masks/guidance, not observed platform screenshots.',
                        'No export or prior approval status was modified.']
audit['totals'] = dict(exports=18, selected_frames=54, editable_cues=189,
                      editable_cues_above20cps=31, threshold_provenance='internal_review_reference_not_automatic_failure')
for v in audit['videos']:
    v['visual_review_completed'] = True
    v['visual_review_scope'] = 'three selected frames only'
    v['visual_observations'] = observations[v['video_id']]
    v['live_platform_preview_status'] = 'not_run_in_this_audit'
    v['sha256_unchanged_after_audit'] = True
atomic(audit_path, audit)
atomic(HERE / 'source-notes.json', dict(research_date_local=DATE, timezone='America/Guayaquil',
                                     checked_at_utc=NOW, sources=sources,
                                     excluded_claims=['85% sound-off as universal current audience statistic',
                                                      'Word-by-word captions universally improve retention',
                                                      'Meta ad safe zones or CTR equal organic caption causal effect',
                                                      'A tool feature list measures current trend prevalence']))
atomic(FW / 'captions/catalog.json', catalog)
atomic(FW / 'templates/caption-decision.json', decision)

rows = []
for v in audit['videos']:
    n = v['video_id']
    contact = Path(v['contact_sheet']).relative_to(HERE)
    rows.append(f'| [{n}]({contact}) | {v["cue_count"]} | {v["max_cps"]:.1f} | {v["over20cps"]} | {observations[n]} |')
source_rows = '\n'.join(f'| {s["id"]} | [{s["publisher"]}]({s["url"]}) | {s["published_or_updated"]} | {s["limitations"]} |' for s in sources)
report = '''# Investigación y auditoría de subtítulos — 2026-09-30

## Encargo y conclusión

El usuario pidió investigar ubicación y estilos de subtítulos para Instagram/Facebook Reels y TikTok, pensando también en quienes ven sin audio; amplió la revisión a exportaciones previas para fijar reglas de las próximas ediciones.

Conviene dar mayor presencia a la lectura y diseñar su ubicación desde el encuadre. No hay fundamento para imponer el centro geométrico ni palabras sueltas a todas las piezas. Se adopta un proceso común de cobertura, legibilidad y verificación, con cuatro estilos y tres ubicaciones contextuales. Los valores de tamaño/CPS son presets internos revisables.

## Muestra y método

- 18 videos distintos: 01–16, 21 y 22; la elección exacta de archivo y su SHA-256 están en `export-audit.json`.
- Tres estados seleccionados por video, 54 fotogramas decodificados del MP4 y 18 hojas de contacto inspeccionadas visualmente por el modelo. No fue reproducción completa, escucha ni revisión humana.
- 189 cues extraídos de editables actuales: texto, tiempos, CPS y CSS base/overrides. No se acredita igualdad entre cada editable actual y el origen histórico del export sin recibo. El01 exige considerar su override Instagram; no confundir CSS base con geometría final.
- Conversión de HDR a una vista SDR para observar composición cuando corresponde; no certificación de color HDR.
- Exportaciones verificadas por hash antes/después y conservadas intactas. El16v4 tiene aprobación editorial explícita previa; esta auditoría no revoca esa aprobación ni certifica la interfaz de todos sus destinos. El22 se congeló según su puntero vigente al inicio; otra tarea puede generar versiones posteriores.
- No se abrió ninguna interfaz real de publicación. “Riesgo de UI” es inferencia basada en perfiles internos y guía primaria, no evidencia de un botón tapando texto en pantalla.

## Qué aprendemos de las familias

01 tiene una adaptación de plataforma con caption más alto que su CSS base, pero fuente pequeña. 02–10 muestran repetidamente bandas inferiores con letras relativamente pequeñas frente a titulares grandes; no conviene perpetuar esa jerarquía. 11–15 elevan el texto y aumentan su presencia, con14 como referente útil de tamaño, no como default aprobado de todo el catálogo. El12 ilustra que un CPS razonable no evita que aparezcan tres líneas.

16 ofrece separación editorial limpia; la placa original del carril está en x108/y1592/w864/h132 y puede entrar en el espacio usado por interfaces inferiores. Una mejora futura requiere redistribuir el carril y el encuadre, preservando rostro/manos. 21–22 tienen letra más grande, pero una segunda línea aumenta la altura real de caja: comprobar solo su coordenada superior no basta.

Las fronteras tipográficas observadas en09/10 (“seguir?¿Alguien” y “resuelto.¿Qué”) refuerzan el control ya existente de espacios entre nodos y puntuación en el MP4. Se documenta el aprendizaje sin editar esos archivos.

## Inventario revisado

Máximo CPS y conteo sobre20 corresponden al editable inspeccionado, con espacios/puntuación. Son avisos para revisión, no fallos automáticos ni métricas de comprensión. Pulsar el video abre su hoja de tres muestras.

| Video | Cues | Máx. CPS | Sobre20 | Observación en las muestras |
| --- | ---: | ---: | ---: | --- |
''' + '\n'.join(rows) + '''

31 de189 cues superan20 CPS en esta extracción. Diez están en16, donde hay22 bloques cortos; es un candidato a revisar agrupación en siguientes ediciones, sin concluir que todo cue rápido es ilegible. La revisión móvil, el contexto y la sincronía deciden.

![Comparación de seis exportaciones](COMPARACION_6_EXPORTACIONES.png)

## Investigación actual y diferencias de alcance

La especificación TikTok consultada está actualizada a junio2026. La revisión académica CHI2026 reúne36 trabajos de2015–2025; se verificó su resumen primario. El experimento de2024 sobre ausencia de audio incluye168 participantes y material inglés: apoya reducir esfuerzo de lectura, pero no compara nuestros formatos ni promete retención.

El PDF primario CHI2024 está archivado con hash. Analiza300 TikToks recogidos enabril2023 y nueve entrevistas:83,3% de la muestra usó bloques de pocas líneas que se reemplazaban, mientras5% usó una o pocas palabras rápidas. Eso describe esa muestra histórica, no prevalencia actual ni eficacia. Consistencia y tiempo para leer guían nuestra adaptación.

La disponibilidad actual de resaltados/dinámica en CapCut muestra opciones de producción; no demuestra que un estilo sea la tendencia dominante ni el más eficaz. No se hizo muestreo representativo del feed2026 ni estudio de nuestra audiencia. Se catalogan formatos contemporáneos disponibles sin atribuirles superioridad por moda.

La referencia de lectura Netflix y la guía Meta corresponden a entregas profesionales y anuncios, respectivamente. El35% inferior de la guía Meta no se aplica como requisito orgánico universal. No trasladar los5–10 words/sec de overlays publicitarios deTikTok a captions fieles de voz. Las páginas actuales deMeta Ads Guide con login no se pudieron comprobar directamente; se conserva esta limitación.

## Fuentes primarias consultadas

Consulta local:2026-09-30. “Fecha no verificada” no equivale a publicación reciente. Notas estructuradas, alcance y acceso: `source-notes.json`.

| ID | Fuente | Fecha de publicación/actualización | Límite |
| --- | --- | --- | --- |
''' + source_rows + '''

## Aplicación y optimización

El protocolo operativo es `../../SUBTITULOS_CONTEXTO_Y_LECTURA.md`; el catálogo separa estilo de ubicación. La elección se documenta con `templates/caption-decision.json`, sin imponer una plantilla única ni fingir un selector automático.

Se reutilizan transcripción/timing y la memoria de este muestreo. Cada nuevo video conserva su QA propio: cue más largo/rápido, dos líneas reales, rostro/gestos y destino. No repetir la inspección de todos los exports ni el maestro completo por cada edición. Un cambio solo de color no exige rehacer alineación; un reflujo de caja sí exige revisar wrapping, colisiones y MP4 nuevo.

Los previews parciales permiten corregir antes del render largo. Su ahorro total todavía no se midió. La comparación sin sonido, el review a tamaño móvil y el preview real por plataforma deben registrarse con alcance y evidencia; la hoja de contacto no los sustituye.

## Pendiente y límites

Por confirmar: preferencia del público de la cuenta, rendimiento por formato, test de usuarios en móvil y previews reales deInstagram/Facebook/TikTok con descripción/CTA. Estos pendientes no impiden definir y usar los criterios editoriales en nuevos candidatos locales. Sin evidencia de destino no declarar una entrega certificada para esa plataforma. No se solicitaron publicación ni reedición de archivos aprobados.
'''
atomic(HERE / 'INFORME.md', report)

rule_specs = [
    ('CAPTION_CONTEXTUAL_FORMAT_SELECTION', 'principle',
     'Elegir formato y ubicación de captions por toma real, contexto y plantilla; registrar caption-decision.json usando SUBTITULOS_CONTEXTO_Y_LECTURA.md y captions/catalog.json. Mantener cobertura fiel de voz, no sustituirla por titulares o palabras sueltas. Los presets no están validados por rendimiento.',
     ['CAP_TIKTOK_ACCESSIBILITY_CHI2024','CAP_W3C_SEMANTIC_COVERAGE','CAP_SOCIAL_REVIEW_CHI2026']),
    ('CAPTION_MOBILE_READABILITY_AND_STABLE_LAYOUT', 'principle',
     'Verificar una o dos líneas reales, contraste, separación entre nodos y lectura sin sonido a tamaño móvil. Mantener posición estable y énfasis selectivo; medir CPS para priorizar revisión, sin convertir presets numéricos en hard fails ni borrar palabras para pasar una métrica.',
     ['CAP_SOUND_OFF_PLOS2024','CAP_NETFLIX_SPANISH_READING','CAP_W3C_CONTRAST']),
    ('CAPTION_DESTINATION_UI_EVIDENCE', 'principle',
     'Diseñar la caja completa de captions fuera de rostro, gestos, acción e interfaz del destino. Revisar Instagram, Facebook y TikTok por separado antes de declarar listos esos destinos; perfiles internos y guías de anuncios no certifican UI orgánica. Si falta preview real, mantener pending sin falsear evidencia; la revisión editorial local puede continuar.',
     ['CAP_TIKTOK_SAFE_ZONE_2026','CAP_META_REELS_ADS_GUIDE']),
]

shared_files = [FW/'README.md', FW/'PROMPT_EDICION_INDIVIDUAL.md', FW/'QA_PROFESIONAL.md',
                FW/'PROMPT_INGESTA_Y_EDICION.md', FW/'PROMPT_DERIVADOS_PLATAFORMA.md',
                FW/'rules/registry.json', FW/'sources/catalog.json',
                ROOT/'Serie-IA-Negocios-10-Videos/AGENTS.md', FW/'CHANGELOG.md']

with (ROOT/'.project-shared-write.lock').open('a+') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    for p in shared_files:
        backup(p)

    registry = json.loads((FW/'rules/registry.json').read_text())
    ids = {r['id'] for r in registry['rules']}
    for rid, kind, instruction, evidence in rule_specs:
        assert rid not in ids
        registry['rules'].append(dict(id=rid, version='1.0.0', kind=kind, status='adopted',
                                     instruction=instruction,
                                     scope=dict(platforms=['all'],topics=['all'],formats=['vertical_video','talking_head']),
                                     confidence='high', review_due_at='2026-12-30', evidence=evidence,
                                     approval=dict(type='explicit_user_framework_instruction',date=DATE)))
    atomic(FW/'rules/registry.json', registry)

    source_catalog = json.loads((FW/'sources/catalog.json').read_text())
    assert not {s['id'] for s in sources} & {s['id'] for s in source_catalog['sources']}
    source_catalog['sources'].extend(sources)
    # verified_at is deliberately preserved: unrelated sources were not re-reviewed.
    source_catalog['last_addition_at'] = DATE
    atomic(FW/'sources/catalog.json', source_catalog)

    readme_path = FW/'README.md'
    readme = readme_path.read_text()
    anchor = 'La entrega profesional se rige por [QA_PROFESIONAL.md](QA_PROFESIONAL.md).'
    assert readme.count(anchor)==1
    readme = readme.replace(anchor, anchor+'\nLos subtítulos de las próximas ediciones se eligen por contexto con [SUBTITULOS_CONTEXTO_Y_LECTURA.md](SUBTITULOS_CONTEXTO_Y_LECTURA.md), [catálogo de formatos](captions/catalog.json) y [decisión por video](templates/caption-decision.json). Estilo y ubicación se separan; presets de tamaño/CPS no son requisitos oficiales ni rendimiento probado. La auditoría de18 exportaciones vive en [INFORME.md](research/subtitulos-2026-09-30/INFORME.md).')
    atomic(readme_path, readme)

    prompt_path = FW/'PROMPT_EDICION_INDIVIDUAL.md'
    prompt = prompt_path.read_text()
    anchor = '- Framework-Edicion-Social/QA_PROFESIONAL.md'
    assert prompt.count(anchor)==1
    prompt = prompt.replace(anchor, anchor+'\n- Framework-Edicion-Social/SUBTITULOS_CONTEXTO_Y_LECTURA.md\n- Framework-Edicion-Social/captions/catalog.json\n- Framework-Edicion-Social/templates/caption-decision.json')
    anchor = 'Monta por capas, protege rostro y captions,'
    assert prompt.count(anchor)==1
    prompt = prompt.replace(anchor, 'Antes de montar captions, copia caption-decision.json dentro de VIDEO-NN y decide por contexto frase estable, énfasis, resaltado progresivo o impacto puntual; elige aparte pecho/espacio negativo, carril seguro o integración en escena. Conserva voz completa, máximo dos líneas reales y posición predecible. Verifica lectura sin sonido, tamaño móvil, caja completa/gestos/UI y tiempos; CPS/tamaños son presets de revisión, no hard fails numéricos. Reutiliza transcripción/timing, sin volver a analizar el maestro. Si falta preview real de destino, mantenlo pending sin certificar plataforma ni impedir un candidato editorial local.\n\n'+anchor)
    atomic(prompt_path, prompt)

    qa_path = FW/'QA_PROFESIONAL.md'
    qa = qa_path.read_text()
    anchor = '### Captions\n'
    assert qa.count(anchor)==1
    qa = qa.replace(anchor, anchor+'\nAplicar [SUBTITULOS_CONTEXTO_Y_LECTURA.md](SUBTITULOS_CONTEXTO_Y_LECTURA.md) y guardar decisión por video. Comprobar una o dos líneas realmente renderizadas, posición estable, cobertura completa y lectura sin sonido a tamaño móvil. Revisar cues largos/rápidos y textos simultáneos; los presets CPS/fuente son referencias editoriales, no hard fails automáticos. La pasada completa sin sonido exige evidencia propia: snapshots aislados no la acreditan.\n')
    anchor = '- Preflight con la guía o preview del destino declarado.'
    assert qa.count(anchor)==1
    qa = qa.replace(anchor, anchor+'\n- Revisar caja completa, padding y énfasis con la interfaz de Instagram, Facebook y TikTok por separado cuando se declaren listos esos destinos. Los perfiles internos y la guía de anuncios no certifican Reels orgánicos. Sin preview real, registrar pendiente de destino; no confundir un candidato editorial local con entrega certificada para plataforma.')
    atomic(qa_path, qa)

    for name in ['PROMPT_INGESTA_Y_EDICION.md','PROMPT_DERIVADOS_PLATAFORMA.md']:
        p = FW/name
        text = p.read_text()
        text += '\n\n## Subtítulos por contexto — 2026-09-30\n\nAplicar `SUBTITULOS_CONTEXTO_Y_LECTURA.md` y `captions/catalog.json`. Registrar estilo y ubicación por separado en `VIDEO-NN/caption-decision.json` usando la plantilla del framework; preservar voz y sincronía. Revisar dos líneas reales, tamaño móvil, lectura sin audio, rostro/gestos y caja completa frente a UI de cada destino. No imponer palabras sueltas, coordenadas o CPS universales. Mantener preview pendiente cuando no exista evidencia real; no certificar plataforma por un check local ni reanalizar el maestro.\n'
        atomic(p,text)

    agents_path = ROOT/'Serie-IA-Negocios-10-Videos/AGENTS.md'
    agents = agents_path.read_text()
    agents += '\n\n## Subtítulos según contexto — próximas ediciones — 2026-09-30\n\nAplicar `../Framework-Edicion-Social/SUBTITULOS_CONTEXTO_Y_LECTURA.md` y `captions/catalog.json`; documentar la elección con `templates/caption-decision.json` dentro de cada VIDEO-NN. Estilo y ubicación son decisiones independientes. Conservar frase fiel, una o dos líneas reales, posición predecible, lectura móvil/sin sonido y énfasis selectivo. Proteger rostro, manos y acción; revisar toda la caja con UI real de Instagram, Facebook y TikTok cuando se declaren listos esos destinos. Sin preview, mantener destino pendiente y continuar candidato editorial local sin certificarlo. Los valores de fuente/CPS son presets revisables, no hard fails automáticos. Reutilizar ASR/timing compartidos; este cambio no autoriza modificar exportaciones ya aprobadas.\n'
    atomic(agents_path,agents)

    changelog_path = FW/'CHANGELOG.md'
    changelog = changelog_path.read_text()
    assert changelog.startswith('# Changelog\n')
    entry = '''\n## Subtítulos por contexto y auditoría de exportaciones — 2026-09-30

- Petición: ampliar investigación de subtítulos a videos exportados y fijar criterios de futuras ediciones con las plantillas existentes.
- Auditoría parcial de18 MP4/54 estados y189 cues de editables actuales; archivos y aprobaciones preservados. Mayor legibilidad en familias11–15; bandas bajas/pequeñas02–10, tres líneas12 y carril muy bajo16 documentados. No equivale a reproducción completa/escucha/UI real.
- Nuevo protocolo y catálogo: cuatro estilos, ubicación independiente, decisión por video, cobertura fiel, dos líneas reales, énfasis selectivo y QA de lectura móvil/sin sonido/destino. Presets56–72px y CPS son referencias internas; sin rendimiento probado ni selector automático.
- Fuentes primarias TikTokjunio2026, CHI2026/2024, PLOS2024, W3C, Netflix y guía de anunciosMeta con límites registrados. No aplicar porcentajes de anuncios a orgánico ni estadísticas genéricas de sonido/retención.
- Integración enREADME, tres prompts,QA,AGENTSserie y tres reglas; fuentes individuales fechadas sin revalidar el catálogo previo. Historial antes del cambio conservado en research/subtitulos-2026-09-30/before-framework-update/.
- Validación: extracción originalPASS; hash18exports/54frames comprobado al finalizar; validación documental/hash posterior en validation.json. Preview real por destino, comprensión por público y rendimiento siguen por confirmar; ningún nuevo render, ASR, audio, editable o publicación.
'''
    atomic(changelog_path, '# Changelog\n'+entry+changelog[len('# Changelog\n'):])
    fcntl.flock(lock, fcntl.LOCK_UN)

print(json.dumps(dict(status='written', exports_unchanged=18, selected_frames=54,
                      editable_cues=189, protocol=str(FW/'SUBTITULOS_CONTEXTO_Y_LECTURA.md'),
                      report=str(HERE/'INFORME.md'), comparison=str(HERE/'COMPARACION_6_EXPORTACIONES.png')),
                 ensure_ascii=False))
