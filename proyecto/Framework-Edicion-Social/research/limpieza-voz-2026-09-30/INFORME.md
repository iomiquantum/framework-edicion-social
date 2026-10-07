# Limpieza de voz: investigación y prueba VIDEO17

Fecha local: 2026-09-30. Investigación actual en fuentes primarias; pruebas limitadas a la grabación real de VIDEO17. No se ha probado aún un corpus propio de ladridos, tráfico o bocinas. No hay ganador perceptual universal ni aprobación humana del audio.

| Herramienta | Capacidad documentada | Estado en este proyecto |
|---|---|---|
| [FFmpeg afftdn](https://ffmpeg.org/ffmpeg-filters.html#afftdn) | Reducción espectral con perfil de ruido, ajustable. | Motor usado en16/17; dos intensidades comparadas en17. |
| [DeepFilterNet oficial](https://github.com/Rikorose/DeepFilterNet) | Supresión neuronal de voz a48kHz; framework y binario local. | Binario oficial0.5.6 Apple Silicon y modeloDF3ONNX descargados al QA de17, congelados por hash; ejecución local comprobada. |
| [ClearerVoice Studio](https://github.com/modelscope/ClearerVoice-Studio/tree/main/clearvoice) | MossFormer2_SE_48K/FRCRN y otros modelos; tareas separadas de mejora/separación. | Candidato de siguiente comparación para ruido variable difícil. No instalado ni procesado aquí. Sus benchmarks publicados no certifican este lote. |
| [Resemble Enhance](https://github.com/resemble-ai/resemble-enhance) | Denoiser separado de enhancer, modelos44.1kHz; opción denoise_only. | Candidato sin prueba local; preferir denoise_only en una primera comparación para limitar restauración de voz. No inferir superioridad. |
| [RNNoise](https://github.com/xiph/rnnoise) | Red neuronal ligera, supresión en tiempo real48kHz. | Alternativa documentada, no ensayada en17. Formatos/modelos deben corresponder; no asumir compatibilidad directa con arnndn. |
| [Adobe Enhance Speech en Premiere](https://helpx.adobe.com/premiere/desktop/add-audio-effects/adjust-volume-and-levels/enhance-speech.html) / [Podcast FAQ](https://helpx.adobe.com/podcast/adobe-podcast-faq.html) | Mejora de diálogo medianteIA; Premiere permite balancear original/mejorado. Podcast depende de audibilidad/ruido y admite idiomas diversos. | Opción comercial, sin prueba ni integración actual. No se subió audio ni se usó una cuentaAdobe. No se verificó qué herramienta utilizaba el ejemplo mencionado deClaude. |

Para este ventilador aparente, comparar motor espectral perfilado y neuronal antes de adoptar un modelo. Para ruido variable superpuesto a voz, ensayar también ClearerVoice/Adobe si procede. Esto es una recomendación de orden de pruebas, no resultado medido para ladridos/bocinas. Una reducción agresiva puede afectar consonantes y timbre; conservar A/B y decidir por escucha a volumen comparable, además de medidas. Reverberación, otra persona hablando y saturación requieren evaluación distinta; ninguna de estas herramientas garantiza aislamiento perfecto.

Prueba local reproducible: `Serie-IA-Negocios-10-Videos/VIDEO-17/qa/noise-revision-v2/`. Se reutilizaron cinco contextosPCM48k y la pausa195.7..196.7 de la misma toma. afftdn18: nr18/nf-55/tn0/gs12, latencia25ms medida/compensada. DeepFilterNet3: binario0.5.6, modeloONNX explícito,24dB límite, sin postfilter, `-D` más4800samples de pad final antes del recorte. CLI nativa evita instalarTorch/Python y procesó los cinco contextos en3.783s de comandos, sin extrapolar rendimiento general.

Con normalización a objetivo-15LUFS/-1.8dBTP, las cinco colas150ms del candidatoafftdn18 miden11.16–12.72dB menos quev1; DF3 mide7.54–10.24dB menos quev1. Alcance: fondo de esas pausas; no es mejoraMOS/SNR durante voz ni percepción. Sobre voz dominante antes de normalización: afftdn18 cambiaRMS0.031–0.051dB y correlación>.99992; DF3 cambia0.418–0.809dB y correlación>.99694. Estas señales orientan prueba, no aprueban fonemas/timbre.

Ambos ASR locales recuperan las mismas81 palabras normalizadas de la transcripción existente. AmbosMP4 pasan decodificación/QA técnica;832 paquetes de imagen idénticos, incluidosPTS/DTS/duración;AACsin desfase en cuatro ventanas. v2afftdn18:-15.32LUFS/-1.69dBTP; pruebaDF3:-15.43LUFS/-1.65dBTP. Editable apunta av2; ambos necesitan escucha del usuario.

Optimización comprobada: reutilizar ingesta, contextos, perfil y picture codificada. Remuxv2 tarda.382s; alternativa.390s; el render visual completo previo de17 tardó38.088s. Comparación de comandos concretos, no ahorro total de trabajo/QA. La revisión no reanaliza el master. ASR adicional se limita a dos voces seleccionadas para verificar texto tras cambios de procesamiento. Se conservanv1, recetas, imágenes y QA. Los gates de texto y hook/SFX siguen dentro del wrapper.

Pendiente: naturalidad y ruido residual percibido; audibilidad contextual de dos SFX suaves; corpus de sonidos externos reales; comparación localClearerVoice yAdobe si se justifica. No se instala todo ni se encadenan automáticamente limpiadores. No adoptar nr18 niDF3 como preset universal. Cache de pictureactual usa fullcut-plan: separar contrato de cortes/píxeles de metadatos editoriales sigue pendiente.


## Actualización posterior: pruebas locales ampliadas VIDEO17

La etapa anterior describía candidatos aún no ejecutados. Ahora se probaron los cuatro modelos/motores adicionales, conA/B yMP4 de audición: [resultados, límites y recetas](COMPARACION_LOCAL_V17_V3.md). Adobe sigue pendiente de sesión y no se ha subido audio. Se conserva el informe inicial como antecedente.
