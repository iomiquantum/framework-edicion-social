from pathlib import Path
import json,hashlib,datetime,fcntl,re
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];FW=ROOT/'Framework-Edicion-Social'
M=json.loads((OUT/'manifest.json').read_text());V=json.loads((OUT/'evidencia/validacion-entrega.json').read_text());date='2026-09-30'
text='''# Cinco pruebas de musicalización por contexto

Petición: probar la dirección sonora en tres voces cortas de20–30s y dos piezas largas existentes, sin dar veredicto final sobre canciones. Cambiar nivel como una mezcla editorial, incluir música y efectos, documentar el proceso y dejar audiciones completas. Una o dos músicas en cortos según duración y contexto, sin obligación de cambiar por cronómetro.

## Punto de partida y selección

C tenía dirección/inicio favorables según el usuario, con bajadas solicitadas. La primera tanda calmada fue rechazada y la tanda reciente se percibió con sonidos fuertes; no se declaró rechazo definitivo de sus canciones completas. Las dos referencias sirven para estudiar entradas, retiros, cambios de intención y acentos; ninguna música extraída se reutiliza.

Se localizaron voces nativas existentes. Para01 se usa el corte vigente21,375s, no el antiguo voice-master28,893s. Para14 el máster anterior a música/SFX del editable vigente, no el final con efectos integrados. La pieza52,93s es la voz genérica Kokoro seleccionada en el explainer; se conserva sin usar la alternativa de clon con error documentado. La pieza158,798s es la guía HeyGen de V05 que une01–15; es voz artificial, no clon del usuario. El recuerdo de1/2min era aproximado: se conservan sus duraciones reales. También se localizó radio-cut humano130,892s en V03, sin modificarlo ni presentarlo como la guía más reciente.

Inventario/hashes/formatos: fuentes/inventario.json. Las tres fuentes humanas están a48k; Kokoro fue creado originalmente a24k y el máster localizado a48k; la guía HeyGen está a44,1k. Remuestrear a48k no recupera información ausente. Mono se duplica unity en L/R para comparar en el mismo dominio; no se usa PCM16k de reconocimiento para mezcla. La cola01 tiene1ms de silencio de alineación y11 tiene16,1875ms: diferencias entre duración de audio y contenedor, sin mover palabras ni cortes.

## Voz antes de música

Se reutilizan transcripciones/metadata y tiempos del montaje.01 usa captions actuales porque el transcript-final correspondía a una versión anterior.11/14 usan ASR existente;14 contiene errores escritos y una frontera fusionada entre mejor/pregunta: se toma contexto corregido del guion/cut-plan, se conserva ASR y se trata como aproximación. Largos: líneas reales de metadataKokoro y366 palabras de guíaV05. No nueva ASR ni nueva voz.

Praat autocorrelación75–400Hz/20ms, RMS50ms y umbral de baja energía relativo al propio audio. Cada fuente tiene perfil global, por frases, ritmo descriptivo y pausas en evidencia/prosodia-*.json. F0 puede errar por octavas; pausas de baja energía incluyen respiración/residuo. Métricas no prueban emoción, defecto vocal, intención psicológica ni recepción de la audiencia. Lectura del texto/contexto es inferencia editorial. No se activó restauración especializada ni se aplicaron nueva EQ/compresión/denoise sobre voz.

| Voz | F0 mediano estimado | Rango central estimado | Contraste central de energía activa |
| --- | ---: | ---: | ---: |
'''
for m in M:
 p=json.loads((OUT/f"evidencia/prosodia-{m['id']}.json").read_text())['global'];text+=f"| {m['title']} | {p['f0_median_hz']}Hz | {p['f0_p90_p10_semitones']}st | {p['active_rms_range_p90_p10_db']}dB |\n"
text+='''
## Diseño y procesamiento

Cada plan escribe función por tramo antes de elegir archivo. Una pista puede desaparecer, volver más discreta o dejar una frase desnuda. Las tres pruebas cortas usan una pista cada una; el largo53s cambia de mecanismo a aplicación con dos; el largo2:39 usa cuatro recursos y tres funciones (contraste/mecanismo, conversación/evidencia, acción), repetidos y transformados entre actos. Ninguna selección está aprobada globalmente.

Nuevas fuentes oficiales: Backbay Lounge, Clean Soul y Cipher de Kevin MacLeod. Se obtiene filename/ISRC del catálogo público oficial pieces.json y el enlace de la página real; Cipher usa Cipher2.mp3. Se congelan originales, HTML y licenciaCC BY4.0 actual, créditos y hashes. HeyGen search devolvió UNAUTHORIZED; se continuó por fuentes públicas, sin enviar voces ni cambiar conexión. Biblioteca principal conserva seis candidatos musicales, ochoSFX y cuatro antecedentes, con feedback específico; no limpia la historia.

Voz: ganancia constante por pieza para aproximar−18LUFS estéreo con techo fuente−3,2dBTP. Mezcla y control tienen exactamente el mismo aporte de voz; no se aplana su dinámica. Música: highpass70Hz/lowpass9kHz y resta de60% de banda400–4000Hz en el derivado, sin alterar originales. Este carve deja espacio y es una elección provisional; no se afirma que el timbre sea óptimo sin escucha.

V1 contiene automatización editorial en dB por frases y SFX. V2 añade protección secundaria solo descendente: lecturaRMS50ms, anticipación aproximada100ms, recuperación suavizada; nunca devuelve la música por encima del plan en cada silencio. Ajusta frases/sílabas suaves y evalúa la banda350–5000Hz. Objetivo orientativo de margen14dB: curvas suavizadas y energía residual no garantizan cumplimiento por cada50ms, inteligibilidad ni percepción. Se mantienen todas las curvas, incluidas ventanas de posible competencia. No hay fórmula universal de volumen ideal.

SFX: biblioteca originalCC0, mínimo dos identidades por corto y un acento en todos los hooks. Cada evento tiene función, fuente/hash, ataque/cola, calibración contra voz local y techo de pico; no se usan impactos por cada palabra. En pausas, el SFX puede superar el residual de voz: una relación positiva no es por sí misma enmascaramiento. Se revisa contexto hablado cercano y reproducción nativa. Efectos conservan su identidad aunque cambie nivel.

Suma48kfloat, archivoWAVPCM24 y AAC256kbps estéreo. Se estima true peak a4× antes de escribir; se mide AAC real y existe corrección global compartida con control si el codec supera−1,5dBTP. En estas cinco mezclas no fue necesaria correcciónAAC. V1 permanece junto a V2 y las fuentes originales. Cada procesamiento queda en scripts y plan-mezcla.json, sin gráficos de audio ocultos dependientes del preview.

## Dirección por pieza y tramos exactos
'''
for m in M:
 text+='\n### '+m['title']+' · '+str(m['duration_s'])+'s\n\n'+m['direction']+'\n\n| Tramo musical | Fuente/offset | Función |\n| --- | --- | --- |\n'
 for q in m['music_clips']:text+=f"| {q['start']:.3f}–{q['end']:.3f}s | {q['music']} desde{q['source_start']:.3f}s | {q['role']} |\n"
 text+='\nCurvas de ganancia absolutas en plan-mezcla.json; protección secundaria y relación medida en evidencia/relacion-'+m['id']+'.json.\n\n| SFX | Tiempo | Decisión |\n| --- | ---: | --- |\n'
 for q in m['sfx_events']:text+=f"| {q['file']} | {q['start']:.3f}s | {q['reason']} |\n"
text+='\n## Validación y resultado\n\n45 archivos de las cinco piezas verificados por hash, formatos, decode completo y energía no nula. Fuentes intactas; suma de stems y voz a ganancia constante verificadas. AAC/PCM correlación mínima'+f"{min(m['aac_pcm_correlation'] for m in M):.6f}"+'; es equivalencia técnica, no aprobación estética. No se certifica escucha ni atención/retención de audiencia.\n\n| Mezcla final AAC | Duración | LUFS estéreo | True peak | Identidades/eventosSFX |\n| --- | ---: | ---: | ---: | ---: |\n'
for m in M:text+=f"| {m['title']} | {m['duration_s']:.3f}s | {m['mix_loudness_aac']['input_i']:.2f} | {m['mix_loudness_aac']['input_tp']:.2f}dBTP | {m['sfx_identities']}/{len(m['sfx_events'])} |\n"
text+='''
La relación de banda en ventanas activas con voz350–5000Hz por encima−40dBFS se resume en validacion-entrega.json, conservando también datos de energía menor. Ese recorte describe habla suficientemente energética para comparar; no borra las curvas ni convierte residuos en palabras. P95relativoV2: aproximadamente−16,0/−23,4/−22,2/−19,3/−23,3dB en01/11/14/53/159. Valores más bajos no demuestran mejor mezcla; sirven para localizar una revisión.

Reproducción nativa en banco: los cinco AAC cargaron con duración correcta, errornull y reproducción activa. Comprobados salto11,695s/control de voz conservando≈11,93s; largo83,449s y cambios música/efectos conservando≈83,47/83,49s. La UI pausa otras pruebas al reproducir una y ofrece descarga. Evidencia UI separada de percepción. No se escuchó directamente por el agente; claridad, timbre, naturalidad y preferencia humana siguen por confirmar.

Incidencia real: primera ejecución detuvo el guard por tolerancia de2muestras para voz/contenedor. Se comprobó1ms/16,1875ms de cola, se añadió silencio terminal explícito con tope50ms y se repitió. Script previo/diagnóstico conservados. Aprendizaje previo aplicado: seek antes de entrada/recorte explícito antes de fades; comprobarRMS no nulo además de decode para no entregar previews silenciosos.

## Reproducir y continuar

Scripts, orden: preparar_fuentes.py → perfilar_voces.py (entornoPraat) → crear_plan.py → mezclar.py → crear_banco.py → verificar_entrega.py → integrar_biblioteca.py. FFmpegfull9.0.2; entornoDSP privado scipy/NumPy/soundfile; entornoPraat separado. No se modifican dependencias de otros editables. El servidor8868 ya existente sirve este banco con rangos. El usuario puede usar index.html local o localhost; el banco no requiere Internet para reproducir.

Para afinar, registrar pieza/segundo/qué compite o qué emoción busca. Primero carácter/ubicación/nivel de música/SFX; mantener voz intacta salvo nueva petición. No elegir según rapidez ni según el mayor número de efectos. Pendiente: escucha humana completa, ajustes tras feedback, decisión de repertorio y adopción en el editable que se solicite. Ningún video original reemplazado, ningún contenido publicado, ningún resultado de audiencia medido.

Fuentes verificadas: [catálogo oficial](https://incompetech.com/music/royalty-free/pieces.json), [licencias del compositor](https://incompetech.com/music/royalty-free/licenses/), [CC BY4.0](https://creativecommons.org/licenses/by/4.0/), [Neon](https://www.scottbuckley.com.au/library/neon/). Créditos completos y cambios en CREDITOS.md; derechos de las referencias no se trasladan a esta biblioteca.
'''
(OUT/'PROCESO.md').write_text(text)
(OUT/'CHANGELOG.md').write_text('# Changelog\n\n## 2026-09-30 — Cinco mezclas completas\n\nTres voces humanas vigentes21,375/29,1/23,26s, dos narraciones artificiales existentes52,93/158,798s. Fuentes preservadas, seis candidatos musicales en biblioteca tras tres descargas oficiales,29 eventosSFX. Plan, V1/V2,45 medios con QA, banco nativo y proceso documentado. Escucha/elección humana por confirmar. No modificación de editables ni publicación.\n')
# Append in master chronological log and preserve entries written by other chats.
entry='''
### 2026-09-30 — Cinco pruebas de musicalización guiadas por la voz

- **Petición:** tres voces20–30s y dos narraciones largas existentes, música/SFX con volumen por momentos, biblioteca, pruebas verificadas y proceso documentado. Sin veredicto final sobre pistas con sonidos fuertes; una o dos músicas en cortos según contexto.
- **Punto de partida:** dirección/inicioC favorables con bajadas pedidas, primera tanda calmada descartada, dos referencias estudiadas. Se localizó corte01 vigente21,375s (no viejo28,893s), voces11/14 y guías Kokoro52,93s/HeyGenV05 158,798s; radio-cut humano130,892s localizado y conservado.
- **Cambios y motivo:** cinco mezclas aisladasV1/V2 con perfiles de voz, planes por texto/prosodia, música trabajada dentro de frases, retiradas y29 eventosSFX. Tres descargas oficiales Kevin MacLeod, créditos/licenciaCC BY4.0/hashes/snapshots; catálogo pasa a seis candidatos sin aprobación global, ochoSFX y cuatro antecedentes. Reindexador conserva ampliaciones/feedback. Se evita nivel musical constante y no se altera interpretación/ritmo de voz.
- **Archivos:** Framework-Edicion-Social/research/prueba-mezcla-voz-2026-09-30/{index.html,PROCESO.md,CREDITOS.md,RECIBO_INICIO.json,plan-mezcla.json,manifest.json,fuentes,evidencia,scripts,renders/v1,renders/v2}; library/music/candidates/2026-09-30-mezclas-contexto, catálogo/guía; scripts/indexar_biblioteca.py y changelogs. Editables/renders fuente intactos.
- **Validación:**45medios hash/decode/48kestéreo/energía no nula; invariancia de voz a ganancia constante y suma de stems; mínimo dos identidades y SFX en todos los hooks. AAC≈−18,01 a−19,01LUFS, techo máximo−2,99dBTP, AAC/PCM mínimo0,999800. Cinco reproducciones nativas/errornull, capítulos y comparación conservan posición. Sin escucha perceptual del agente ni aprobación auditiva humana.
- **Resultado:** banco con cinco audiciones completas, controles para voz/música/SFX y descargas, duraciones reales; documentos reproducibles. UNAUTHORIZED en búsquedaHeyGen se resolvió con fuentes públicas oficiales, sin bloquear ni subir voces.
- **Aprendizaje:** preservar montaje vigente y diferencias de cola1/16,1875ms con silencio terminal, no usar16kASR para mezclar. Relación por banda/energía residual ayuda a localizar riesgos, no prueba inteligibilidad. Ducking complementa dirección editorial sin levantar cada hueco; recortar antes de fades y validarRMS evita repetir previews silenciosos.
- **Pendiente:** escucha completa y feedback por pieza/segundo, timbre/naturalidad/claridad percibida, repertorio y adopción en editable. No publicación, rendimiento de audiencia ni elección de canciones certificada.
'''
p=ROOT/'BITACORA_CURSO_EDICION.md'
with (ROOT/'.BITACORA_CURSO_EDICION.md.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);s=p.read_text();s=re.sub(r'Última actualización: [^\n]+','Última actualización: '+date+'.',s,count=1)
 if '### 2026-09-30 — Cinco pruebas de musicalización guiadas por la voz' not in s:s+='\n'+entry
 p.write_text(s)
p=FW/'CHANGELOG.md'
with (FW/'.CHANGELOG.md.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);s=p.read_text();entry='''## Cinco pruebas completas de musicalización y biblioteca — 2026-09-30

- Tres cortos21,375/29,1/23,26s y dos voces artificiales existentes52,93/158,798s, fuentes intactas y voz solo con ganancia constante común. Una pista por corto, dos en53s, cuatro recursos/tres funciones en2:39;29SFX con hook y mínimo dos identidades.
- Research/prueba-mezcla-voz-2026-09-30: planes, prosodia, V1/V2, stems, banco escucha, créditos, inventario, incidencias y PROCESO.md. Tres pistas Kevin MacLeod oficialesCC BY4.0 con previews20s no nulos; catálogo seis candidatos/ochoSFX/cuatro antecedentes e historial de feedback. Reindexador conserva entradas/feedback ampliados.
- QA45mediosPASS, hash/decode48k/energía, voz constante, suma de stems, AAC/PCM≥0,999800 y true peak≤−2,99dBTP. Cinco reproducciones nativas y conservación de posición al cambiar/saltar; escucha perceptual/elección por confirmar.
- Tolerancia inicial de cola2muestras detenía mezcla: diferencias1ms/16,1875ms documentadas, silencio terminal acotado50ms, previo conservado. HeyGen no autorizado resuelto con catálogo público sin enviar voces. Ningún editable/video original reemplazado, publicación ni eficacia medida.

'''
 if '## Cinco pruebas completas de musicalización y biblioteca' not in s:s=s.replace('# Changelog\n','# Changelog\n\n'+entry,1)
 p.write_text(s)
print('DOCUMENTED',OUT/'PROCESO.md')
