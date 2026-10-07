#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Uso: $0 ENTRADA_HLG.mp4 MATE_SUJETO_ALPHA.mov SALIDA_HLG.mp4" >&2
  exit 2
fi

input_path=$1
subject_matte_path=$2
output_path=$3

if [[ ! -f "$input_path" ]]; then
  echo "No existe la entrada: $input_path" >&2
  exit 2
fi

if [[ ! -f "$subject_matte_path" ]]; then
  echo "No existe el mate temporal del sujeto: $subject_matte_path" >&2
  exit 2
fi

if [[ -e "$output_path" ]]; then
  echo "La salida ya existe; no se sobrescribe: $output_path" >&2
  exit 2
fi

color_info=$(ffprobe -v error -select_streams v:0 \
  -show_entries stream=color_transfer,color_primaries \
  -of default=noprint_wrappers=1:nokey=1 "$input_path")

if [[ "$color_info" != *"arib-std-b67"* || "$color_info" != *"bt2020"* ]]; then
  echo "La entrada no está etiquetada como BT.2020/HLG; se detiene para evitar una conversión implícita." >&2
  exit 3
fi

matte_pix_fmt=$(ffprobe -v error -select_streams v:0 \
  -show_entries stream=pix_fmt -of default=noprint_wrappers=1:nokey=1 "$subject_matte_path")

if [[ "$matte_pix_fmt" != yuva* ]]; then
  echo "El mate no contiene un canal alfa temporal (pix_fmt=$matte_pix_fmt)." >&2
  exit 3
fi

# Ajuste obtenido del par original/propuesta de la referencia aprobada.
# El fondo usa el ajuste completo. El sujeto mezcla ese ajuste al 55 % con
# la identidad para evitar el exceso de naranja observado en la prueba v11.
filter_complex="[0:v]split=2[bg0][fg0];\
[bg0]format=gbrp16le,colorchannelmixer=rr=0.931130:rg=0.131949:rb=-0.229718:ra=0.012599:gr=0.236443:gg=0.406716:gb=0.260868:ga=0.008644:br=0.145923:bg=-0.043128:bb=0.704654:ba=0.015791,format=yuv444p16le[bg];\
[fg0]format=gbrp16le,colorchannelmixer=rr=1.019488:rg=0.175584:rb=-0.191031:ra=-0.019583:gr=0.129402:gg=0.805126:gb=-0.002934:ga=-0.010563:br=0.089360:bg=0.065759:bb=0.788446:ba=-0.021106,format=rgba64le[subrgb];\
[1:v]alphaextract,format=gray16le[a];\
[subrgb][a]alphamerge[fg];\
[bg][fg]overlay=0:0:shortest=1:format=auto,format=yuv420p10le[out]"

ffmpeg -hide_banner -loglevel error -stats -i "$input_path" -i "$subject_matte_path" \
  -filter_complex "$filter_complex" -map "[out]" -an \
  -c:v libx265 -preset medium -crf 18 -tag:v hvc1 -pix_fmt yuv420p10le \
  -color_primaries bt2020 -color_trc arib-std-b67 -colorspace bt2020nc \
  -movflags +faststart "$output_path"

ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,profile,pix_fmt,color_space,color_transfer,color_primaries,width,height,r_frame_rate,duration \
  -of json "$output_path"
