from pathlib import Path
import json,hashlib,fcntl,re,datetime
import numpy as np,soundfile as sf
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];FW=ROOT/'Framework-Edicion-Social';M=json.loads((OUT/'variantes-largas/manifest.json').read_text());V=json.loads((OUT/'variantes-largas/validacion-entrega.json').read_text());A=json.loads((OUT/'variantes-largas/asr-qa/results.json').read_text());S=json.loads((OUT/'variantes-largas/asr-por-actos/results.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ui={'date_local':'2026-09-30','method':'CUA navegador nativo2, tab8; acciones de UI, evaluaciónsolo lectura; reproducción no equivale a escucha.','six_mix_observations':[{'id':'largo-53','variant':'A','duration':52.93,'time':35.258947,'paused':False,'readyState':4,'error':None},{'id':'largo-53','variant':'B','duration':52.93,'time':35.264041,'paused':False,'readyState':1,'error':None,'followup':{'time':5.181749,'paused':False,'readyState':4,'error':None}},{'id':'largo-53','variant':'C','duration':52.93,'time':35.264041,'paused':False,'readyState':4,'error':None},{'id':'largo-159','variant':'A','duration':158.798,'time':121.131535,'paused':False,'readyState':4,'error':None},{'id':'largo-159','variant':'B','duration':158.798,'time':121.153659,'paused':False,'readyState':4,'error':None},{'id':'largo-159','variant':'C','duration':158.798,'time':121.159167,'paused':False,'readyState':4,'error':None}],'layers_short_B':{'music_time':5.178294,'effects_time':5.203298,'readyState':4,'error':None},'long_voice_to_first_mix':{'voice_time':83.460941,'first_mix_time':83.46102,'readyState':4,'error':None},'scope':'Carga/reproducción/seek/conservación de posición; no pruebas perceptuales ni teléfono real.','human_listening':'por confirmar'}
(OUT/'variantes-largas/validacion-ui.json').write_text(json.dumps(ui,ensure_ascii=False,indent=2)+'\n')
for r in M:r['native_playback']='verified_native_UI_not_heard'
(OUT/'variantes-largas/manifest.json').write_text(json.dumps(M,ensure_ascii=False,indent=2)+'\n')
text='''# Ampliación: seis tratamientos completos y sistema de comprobación

Fecha local:2026-09-30. El usuario pidió seguir mejorando técnicamente, probar varias canciones sobre las voces largas, más efectos/edición y subidas/bajadas como mezcla multimedia. Solicitó llegar al punto donde la siguiente decisión dependiera de su escucha. Este documento complementa PROCESO.md: conserva aquella tanda, no reescribe su resultado.

## Resultado preparado

Tres versiones completas de52,93s y tres de158,798s. A/Pulso y precisión, B/Cálida y fluida, C/Contraste editorial. Mismo audio de voz y nivel exactos en todas las versiones, sin restauración nueva ni edición de palabras/ritmo. Controles para mix/voz/música/SFX mantienen el momento. Primera prueba conservada para comparación. Tres cortos iniciales intactos.

Seis músicas existentes se probaron en contextos completos, no solo previews: Neon, Cipher, Backbay Lounge, Clean Soul, Resonance y Sarsaparilla. Las cuatro últimas selecciones de paleta se basan en función/argumento y procedencia verificada; los títulos no garantizan encaje. CréditosCC BY4.0, cambios y snapshots se conservan. OchoSFX originales nuevos,91eventos entre las seis alternativas, con semilla/receta/hash y dedicaciónCC0, candidatos sin adopción global. No se reutiliza audio de referencias ni se genera otra voz.

## Relación con las dos referencias

Se reutilizó su análisis de27bloques, contexto visual/textual y contrastes medidos, no se afirmó identificación de canciones/SFX o faders originales sin escucha. Aplicaciones concretas: una entrada en la promesa, cambio de carácter ligado a idea, puente con menos densidad, retirada marcada en tesis/criterio, reentrada de solución y pregunta despejada. Las referencias de≈66/69s no imponen cuota de canciones a cada pieza.

En53s, bucle→definición de flujo→tesis seca→prueba práctica→pregunta. En2:39, atención/ventas→cliente→evidencia→ventaja→criterio sin cama→riesgo→acción→pregunta. Cada variante cambia paleta y densidad, no la contribución de voz. C incluye anticipaciones y más acentos; B menos sonidos y más continuidad. Más eventos no se presentan como mayor calidad.

## Mezcla e iteración

Plan completo con tiempos/offsets/curvas: variantes-largas/plan.json. V1 por variante con automatización editorial y acentos; salida final añade protección local y de colas. Música más presente que primera tanda en ciertos tramos, con intervalos de silencio mantenidos. Fuente→highpass80/lowpass9,5k, filtro5,5k solo para arreglos densos/oscursos marcados, anchuraM/S0,86; carve dinámico400–4000Hz35% A/C y28%B, sobre música, ligado a actividad vocal suavizada. Parámetros provisionales de estos recursos, no presets globales.

Ganancia por puntos en dB anticipa palabras/listas/tesis. Segunda capa descendente para frases suaves y relación de banda350–5000Hz a250ms; objetivo10,5dB orientativo, con suavizado y límites. No devuelve música por encima del plan en cada silencio. SFX se calibran contra voz y contexto cercanos, con techo de pico fuente−18,5dBFS y protección de cola cuando vuelve el habla; algunos deC tienen paneo±0,10. Control de headroom reduce acompañamiento si es necesario y deja voz común. No se requirió esa corrección en las seis salidas.

Los originales no se filtran ni se reemplazan. WAV48kPCM24 y AAC256k, duración/canales comunes. Se conservan mezclasV1 y finales, stems y curvas. Primera ejecución de variantes detectó energía rodante ligeramente negativa por precisión antes de sqrt y guardó A/B finitas, deteniendo C porNaN. Se preservó esa tanda, se verificó mínimo≥−1e−12, se hizo clamp únicamente de residuo de precisión antes de sqrt, se añadió guard explícito y se repitieron las seis. Evidencia: incidencias-ampliacion.json y antes-correccion-media-cuadratica. No se convirtió un fallo enPASS relajando finitud.

## Verificación de archivos

42medios principales nuevos: hashes, decode completo,48k/estéreo/duración, finitud/energía no nula. Seis simulaciones adicionales de downmixmono, banda180–7200Hz/AAC128k; no constituyen escucha en teléfono. Reconstrucción de aporte de voz por resta de música/SFX≤2,4e−7; identidad de voz compartida comprobada. Cada uno de91eventos tiene binding/hash/presencia en elPCM, todas las entradas llevanSFX y hay múltiples identidades. AAC exacto contraPCM de proceso completo y sonoridad/true peak reales. Salidas y métricas en variantes-largas/validacion-entrega.json.

| Pieza/versión | Músicas distintas | Eventos/identidadesSFX | AAC LUFS | dBTP | CorrelaciónAAC/PCM | RMSmono frenteaestéreo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
'''
for m in M:
 r=next(r for r in V['records'] if r['id']==m['id'] and r['variant']==m['variant']);d=m['diagnostics']['v2_mix'];text+=f"| {m['id']}/{m['variant']} | {len(set(q['music'] for q in m['music_clips']))} | {len(m['sfx_events'])}/{m['sfx_identities']} | {d['input_i']:.2f} | {d['input_tp']:.2f} | {m['aac_pcm_correlation']:.6f} | {r['mono_mix_rms_change_db']:.4f}dB |\n"
text+='''
Relación medida por banda en ventanas con voz por encima−40dBFS: P95 música/voz≈−17,1/−22,1/−15,9dB para53A/B/C y−19,2/−20,8/−19,7dB para159A/B/C. Curvas completas conservan las ventanas suaves/pausas. Ese margen y el pico no prueban naturalidad, audibilidad móvil, inteligibilidad ni una emoción. No se usa una puntuación de calidad a partir de RMS.

## Reconocimiento: fallo contrastado, sin ocultarlo

Whisper.cpp large-v3 local, idiomaes,4threads, defaults y sin prompt con guion. Se decodificó elAAC final a16kmono SOLO para QA. Ocho lecturas completas (dos controles, seis mixes); no nuevoASR del lote, ninguna fuente16k mezclada.

Las tres variantes53s reconocen el texto del control y guion conWER0. En2:39, control≈0,82% contra guion; ASR completoA≈27,05%, B≈3,01%, C≈44,54%. A/C repiten frases, algunas con timestamps de duración0. Esto detuvo la conclusión de ese proxy y exigió diagnóstico; los archivos/results/logs se preservan en asr-qa. No se baja toda la música para obtener un porcentaje bonito.

Contraste de señal: entre83,70–93,20s las mezclasA/B y el control son exactamente iguales enPCM (diferencia máxima0); el reconocedor completoA repetía la frase durante ese tramo. El resto del aporte vocal también coincide por suma/resta de stems. Se revisaron las ocho fronteras narrativas preexistentesV05, comunes para control/A/B/C, sin dar guion al motor, en32lecturas independientes. Así se limita contexto del modelo, no se seleccionan solo fragmentos favorables.

| Guía2:39 por ocho actos | Errores contra guion366 palabras | Diferencia contra reconocimiento de control |
| --- | ---: | ---: |
'''
for k,d in S['summary'].items():text+=f"| {k} | {d['script_word_errors']} ({d['script_wer']*100:.2f}%) | "+('referencia' if k=='control' else f"{d['control_word_errors']} ({d['control_wer']*100:.2f}%)")+' |\n'
text+='''
A/C coinciden con reconocimiento del control por actos; B cambia dos palabras y queda más próxima al guion. Esto respalda un problema de contexto/repetición del reconocedor completo, no repetición física del audio ni supresión de esas frases en la mezcla. No demuestra escucha perfecta. Se conserva el resultado completo fallido junto al contraste, no se reemplaza retrospectivamente por el que salió mejor. No se alteró el guion/voz para resolver ese fallo del proxy.

## Reproducción y cierre

Navegador nativo: seis mixes con duración correcta/errornull; cambiosA/B/C conservan≈35,26s y121,15s. B53 inicialmente estaba en estado de seek1 y se comprobó luego estado4/tiempo5,18s; no se certifica avance a partir de una petición deplay solamente. Música/efectos deB53 reproducen y conservan≈5,2s. Comparación voz/primera mezcla de2:39 conserva≈83,46s. GUI pausa otras pruebas; controles/descargas y capítulos vinculados. validacion-ui.json conserva observaciones reales, distintas de audibilidad percibida.

Cierre **LISTA_PARA_ESCUCHA**: checks aplicables de fuente/plan/señal/mezcla/codec/mono/proxyASR/reproductor completos; incidencia numérica corregida, divergencia del reconocedor contrastada y ninguna pérdida física de voz detectada. No hay un problema técnico conocido que justifique seguir modificando estas seis mezclas a ciegas. No afirma agotamiento de toda mejora posible ni que el agente escuchó. Timbre, emoción, jerarquía, naturalidad, fatiga y percepción en altavoz real necesitan valoración del usuario.

## Sistema reutilizable

Nuevo protocoloFramework-Edicion-Social/AUDIO_MEZCLA_CONTEXTO_QA.md enlazado desdeAUDIO_DIRECCION_Y_PROSODIA.md. Integra relaciones por contexto, comparación completa con voz/nivel comunes, guard numérico/export, ASR opcional sin reingesta y cierre honesto. No convierte estas canciones/ganancias en reglas aprobadas ni activa limpieza especializada automáticamente.

Scripts: crear_variantes.py→mezclar_variantes.py→verificar_variantes.py; comprobar_reconocimiento.py y comprobar_asr_por_actos.py investigan el proxy; crear_banco_variantes.py crea el comparador. Solo repetir checks afectados por cambios/fallos/incertidumbre real. Modelos/entornos locales existentes, sin uploads de voces ni modificaciones de dependencias de otros proyectos. fuentes originales/primeros renders conservados.

Pendiente: escucha del usuario por versión/segundo y ajustes concretos; adopción de repertorio en editables solicitados. Ninguna aprobación global/publicación ni mejora de rendimiento de audiencia afirmada. Fuentes/licencias en CREDITOS_VARIANTES.md y manifiestos de biblioteca, mismas páginas oficiales verificadas antes de descarga.
'''
(OUT/'PROCESO_VARIANTES.md').write_text(text)
changes='''
## 2026-09-30 — Ampliación a seis tratamientos largos

Tres versiones por voz52,93/158,798s, seis músicas de biblioteca, ochoSFX originales candidatos y91eventos. Voz/nivel comunes exactos, automatización por frase, carve/protección de cola y comparadorvariantes.html.42medios nuevos y seis stressmonos verificados; ASR ocho completos y32poractos, fallo de repetición del modelo documentado/contrastado, no ocultado. GuardNaN corrigió residuo de precisión antes de sqrt con intentos previos retenidos. Protocolo reutilizable incorporado; estadoLISTA_PARA_ESCUCHA, juicio perceptual humano pendiente.
'''
p=OUT/'CHANGELOG.md';s=p.read_text()
if '## 2026-09-30 — Ampliación a seis tratamientos largos' not in s:p.write_text(s+'\n'+changes)
p=OUT/'PROCESO.md';s=p.read_text()
if '## Ampliación posterior solicitada por el usuario' not in s:p.write_text(s+'\n\n## Ampliación posterior solicitada por el usuario\n\nLa primera tanda se conserva. Hay seis nuevos tratamientos completos para53s/2:39 y un protocolo de cierre técnico. [Comparador](variantes.html), [proceso y diagnósticos](PROCESO_VARIANTES.md). No convierte la primera tanda en una mezcla aprobada ni borra sus decisiones.\n')
# Current local date remainsSeptember30 (UTC offset-5), use real clock for final receipt.
receipt={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request':'Ampliación de revisión técnica y versiones largas, varias canciones/más efectos/automatización.','initial_receipt':'RECIBO_INICIO.json','documents_updated':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [FW/'AUDIO_MEZCLA_CONTEXTO_QA.md',FW/'AUDIO_DIRECCION_Y_PROSODIA.md',OUT/'PROCESO_VARIANTES.md']],'technical_state':'LISTA_PARA_ESCUCHA','human_review':'por confirmar'};(OUT/'RECIBO_AMPLIACION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
entry='''
### 2026-09-30 — Tres tratamientos por pieza larga y cierre técnico de musicalización

- **Petición:** mejorar sistema/comprobaciones al máximo útil, varias canciones y pruebas especialmente en1/2min, más efectos/edición y cambios de nivel como mixer multimedia; referencias aportadas. Las voces halladas duran52,93s y158,798s, preservadas completas.
- **Punto de partida:** cinco primeras pruebas aún candidatas, sin aprobación de música; voz compartida y fuentes verificadas. No se borra ese resultado ni se cambia el repertorio por un veredicto no dado.
- **Cambios/motivo:** seis alternativas completasA/Pulso y precisión, B/Cálida y fluida, C/Contraste editorial, tres por voz; seis canciones, ochoSFX originales candidatos y91eventos con intención. Automatización editorial, carve dinámico sobre música, protección secundaria descendente/colas, versionesV1/finales y stems. Voz/nivel común exactamente iguales para comparar; más efectos no se declara mayor calidad.
- **Archivos:** research/prueba-mezcla-voz-2026-09-30/{variantes.html,PROCESO_VARIANTES.md,CREDITOS_VARIANTES.md,RECIBO_AMPLIACION.json,variantes-largas,scripts}, library/sfx/candidates/2026-09-30-musicalizacion. NuevoAUDIO_MEZCLA_CONTEXTO_QA.md enlazado desdeAUDIO_DIRECCION_Y_PROSODIA.md; índice anterior preserva catálogo ampliado/feedback y sus recuentos reales. Tanda/masters previos intactos.
- **Validación:**42medios nuevos +seis simulacionesmono; fuentes/bindings/hash, finitud/energía,48k/duración, voz recuperada≤2,4e−7, hooks/SFX, AAC/PCM>0,999 y true peak≤−5,84dBTP; I≈−18,01/−18,02LUFS. Seis reproducciones nativas, capas y comparación conservan posición/errornull. Biblioteca seis candidatos/ocho originales/cuatro antecedentes revalidada; nuevosSFX siguen candidatos separados.
- **Incidencias:** media de energía tuvo negativos de precisión y sqrtNaN detuvoC; se guardó fallo, se verificó límite y corrigió solo residuo, se repitieron seis salidas. ASR completo de guía repitió frases(A/C≈27/44%WER): timestampsnulos, vozPCM idéntica acontrol83,7–93,2s enA/B.32lecturas por ocho actos comunes contrastan modelo: A/C0dif contra control; B2palabras y más próxima al guion. No se ocultan fallos ni se fuerza mezcla a seguir un proxy.
- **Resultado/aprendizaje:** comparador con tres tratamientos por largo y primera prueba, voz/música/SFX, descargas. CierreLISTA_PARA_ESCUCHA por cobertura técnica; protocolo aplica comparaciones justas y separa defecto físico de contexto del reconocedor. No afirmación de escucha por agente ni de que ninguna mejora futura sea posible.
- **Pendiente:** valoración auditiva del usuario, carácter/naturalidad/claridad en dispositivo real y ajustes por segundo; elección/adopción de recursos. Sin publicación, aprobación global ni eficacia medida.
'''
p=ROOT/'BITACORA_CURSO_EDICION.md'
with (ROOT/'.BITACORA_CURSO_EDICION.md.lock').open('a+') as f:
 fcntl.flock(f,fcntl.LOCK_EX);s=p.read_text();s=re.sub('Última actualización: [^\n]+','Última actualización: 2026-09-30.',s,count=1)
 if '### 2026-09-30 — Tres tratamientos por pieza larga y cierre técnico' not in s:s+='\n'+entry
 p.write_text(s)
p=FW/'CHANGELOG.md'
with (FW/'.CHANGELOG.md.lock').open('a+') as f:
 fcntl.flock(f,fcntl.LOCK_EX);s=p.read_text();new='''## Seis tratamientos largos y protocolo de cierre técnico — 2026-09-30

- Tres alternativas completas por voz52,93/158,798s, seis músicas, ochoSFX candidatos originales/91eventos. Voz/nivel comunes, automatización por frase, carve/protección de colas, WAV/AAC/stems y comparadorvariantes.html; primeros cinco mixes intactos.
- QA42medios +seis stressmonoPASS, fuentes/hash/energía48k/suma/voz, AAC/PCM>0,999 y techo−5,84dBTP. Seis reproducciones nativas y conservación de posición/capas. No escucha/juicio estético del agente.
- GuardNaN corrige energía rodante negativa por precisión con evidencia/límite, tandas previas retenidas. ASR ocho completos reveló repeticiones de modelo;32poractos y contrastePCM/control separan contexto de audio: A/C0dif, B2palabras. Se preservan resultados fallidos, no se certifica inteligibilidad por ASR.
- AUDIO_MEZCLA_CONTEXTO_QA.md enlazado en dirección: comparaciones completas/voz común, checks proporcionales y estadoLISTA_PARA_ESCUCHA. Registro de proceso/créditos/recibo/bitácora. Recursos nuevos sin adopción global; percepción/elección humana pendientes, sin publicación.

'''
 if '## Seis tratamientos largos y protocolo de cierre técnico' not in s:s=s.replace('# Changelog\n','# Changelog\n\n'+new,1)
 p.write_text(s)
print('DOCUMENTED VARIANTS, protocol, receipts and chronological logs')
