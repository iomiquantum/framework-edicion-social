# Diagnóstico y sugerencias adicionales

Investigación consultada2026-09-30. Usar dentro de una revisión de voz solicitada; no cadena obligatoria de efectos. Registrar tiempo/frase, síntoma, evidencia, sugerencia y alcance pendiente.

| Hallazgo | Sugerencia si existe | Qué preservar/comprobar |
|---|---|---|
| Fondo continuo/zumbido | Supresión espectral/neural o corrección puntual | Ruido durante voz/pausas; evitar bombeo, sonido metálico y pérdida de fonemas |
| Ladrido, carro, bocina/transitorio | Comparación neural o reparación localizada | Voz solapada; no prometer aislamiento ni extrapolar pruebas de ventilación |
| “s”, “sh”, “ch” excesivas | De-esser/reducción dinámica selectiva | Consonantes claras; evitar ceceo/voz apagada. Denoiser no equivale a de-esser |
| Golpes de aire en “p”/“b” | De-plosive/reparación puntual | Cuerpo/ataque vocal; sin frecuencia universal de corte |
| Clics de saliva/labios/lengua | De-click localizado | Ataques y consonantes; revisar lo retirado |
| Eco/reverberación | Proponer de-reverb y audición dirigida | Espacio natural; evitar voz hueca |
| Retumbo/dureza/nasalidad | EQ correctiva dirigida | Timbre original; sin receta fija por frecuencia |
| Frases con niveles muy distintos | Ganancia por frase; compresión moderada si procede | Interpretación/contraste; loudness global no corrige toda dinámica |
| Saturación/clipping | Revisar fuente y proponer reparación/mejor toma | Limitar después no recupera automáticamente audio ya distorsionado |
| Empalme con clic/sílaba truncada | Ajustar handles/corte/microfundido | Voz real, respiración y sincronía |

Respiraciones no son ruido a eliminar por defecto. Silencio perfecto puede degradar fonemas. Diferencia original−procesado contiene ruido y componentes vocales cambiados: energía vocal no demuestra palabras ausentes, pero invita a revisar fidelidad. Comparar a igual volumen y conservar original.

VIDEO17: se probaron denoisers y normalización; **no de-esser/de-click/de-plosive/de-reverb dedicados**. RN fue primera recomendación por cinco colas quietas, sin escucha/naturalidad certificada. No afirmar que corrigió satisfactoriamente las eses.

Fuentes primarias resumidas, sin copiar manuales:

- [Adobe Audition: amplitud/compresión](https://helpx.adobe.com/ph_en/audition/desktop/effects-reference/amplitude-compression-effects.html): de-esser para sibilancia; centro/banda/umbral ajustados a señal y escucha de sibilancia detectada. También dinámica y mezcla de canales.
- [iZotope: voz para video/podcast](https://www.izotope.com/community/blog/how-to-clean-up-voice-recordings-video-podcasts): fondo, golpes de aire y sonidos de boca; reparar con contexto y escucha de lo retirado.
- [iZotope: plosivos](https://www.izotope.com/community/blog/removing-plosives-from-a-voice-recording): corrección específica, sin adoptar frecuencias de ejemplo universalmente.
- [FFmpeg: filtros](https://ffmpeg.org/ffmpeg-filters.html): comprobar sintaxis/disponibilidad en versión instalada; disponibilidad no equivale a resultado aprobado.

Las fuentes respaldan tratamientos, no presencia de esos defectos en una toma nueva ni disponibilidad local de Adobe/iZotope. Sugerir los tratamientos adicionales al usuario antes de aplicarlos cuando excedan su petición.
