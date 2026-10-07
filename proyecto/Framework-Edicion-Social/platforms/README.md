# Perfiles por plataforma

Este modulo evita mantener tres montajes o renders equivalentes. Primero se aprueba un **master vertical neutral** y se obtiene un **máster de Instagram Reels**, que funciona como entrega social universal para Reels, TikTok y YouTube Shorts mientras sea compatible. Solo se produce otro archivo cuando existe una diferencia material documentada.

## Que formato es el principal

`PLATFORM-MASTER-VERTICAL-001` es el formato principal del framework:

- 1080 x 1920, relacion 9:16;
- 30 fps;
- MP4, H.264 High, `yuv420p`;
- AAC-LC a 48 kHz;
- SDR BT.709;
- objetivo interno de video: 8 Mbps.

Es un **master social vertical neutral** de producción. Después de revisar el perfil de Instagram, el MP4 de Reels aprobado se convierte en el archivo universal de publicación. El mismo archivo —los mismos bytes— se usa en TikTok y Shorts cuando subtítulos, CTA, elementos esenciales, duración y codificación también funcionan allí. Cada superficie conserva su preview real, pero esa revisión no obliga a generar otro MP4.

## Gate de necesidad de variante

No se crea un render adicional por costumbre. TikTok o Shorts requieren otro archivo únicamente si se documenta al menos una diferencia material:

- duración o relación de aspecto distinta;
- reencuadre o safe zone realmente incompatible;
- CTA exclusivo que debe estar dentro del video;
- limitación técnica de códec, audio, color o peso;
- hook, estructura o experimento creativo deliberadamente diferente y aprobado.

No son diferencias materiales por sí solas: mover unos píxeles un caption que ya es legible, cambiar una línea decorativa, renombrar el archivo o variar copy, hashtags, portada o metadata externa. Esos elementos se resuelven en publicación sin renderizar de nuevo.

## Separacion entre evidencia y decisiones internas

Cada perfil separa dos capas que nunca deben confundirse:

1. `official_constraints`: afirmaciones trazables a una pagina oficial, con alcance y fuerza. Una guia publicitaria no se presenta como una regla organica.
2. `internal_defaults`: decisiones conservadoras del framework para exportacion, layout y QA.

Las coordenadas de `safe_zones` son siempre `internal_conservative_not_official`. Se expresan entre 0 y 1 desde la esquina superior izquierda y son overlays de trabajo; **no se queman en el render final**. Las interfaces cambian por dispositivo, version, longitud del copy y pruebas de producto. Por eso todos los perfiles exigen vista previa real.

| Perfil | Uso | Zona esencial interna `(x, y, w, h)` | Zona de captions interna |
|---|---|---:|---:|
| `PLATFORM-MASTER-VERTICAL-001` | master neutral | `0.10, 0.10, 0.80, 0.80` | `0.10, 0.64, 0.80, 0.16` |
| `PLATFORM-INSTAGRAM-REELS-ORGANIC-001` | Reels organico | `0.08, 0.10, 0.74, 0.70` | `0.08, 0.62, 0.70, 0.15` |
| `PLATFORM-TIKTOK-ORGANIC-001` | TikTok organico | `0.07, 0.08, 0.73, 0.68` | `0.07, 0.60, 0.68, 0.14` |
| `PLATFORM-YOUTUBE-SHORTS-001` | YouTube Shorts | `0.08, 0.08, 0.74, 0.74` | `0.08, 0.64, 0.72, 0.16` |

Estos rectangulos son una primera red de seguridad, no una promesa de que la UI nunca ocupara otras zonas.

## Contrato de adaptacion

Un derivado conserva obligatoriamente:

- toma seleccionada;
- cortes y timing;
- voz;
- significado, claims y promesa;
- identidad de los assets aprobados.

Solo puede cambiar por defecto:

- reflujo y posicion de elementos;
- saltos de linea de captions sin reescribirlos;
- wording del CTA si es semanticamente equivalente;
- preset de exportacion.

Si cambia una toma, un corte, el mensaje, un claim o un asset, ya no es un derivado: se invalida el content lock y vuelve al ciclo de aprobacion del master.

## Flujo operativo

1. Editar una sola composicion usando el perfil neutral.
2. Aprobar el master de forma explicita.
3. Registrar hashes y bloquear toma, cortes, voz, semantica y assets en un `platform-master.json`.
4. Generar el plan sin `--target`: por defecto incluye únicamente Instagram Reels.
5. Revisar ese mismo MP4 en las superficies de TikTok y Shorts. Si funciona, reutilizarlo sin copiarlo ni volver a renderizar.
6. Añadir `--target` para TikTok o Shorts solamente después de registrar una diferencia material; aplicar únicamente ese delta sobre el mismo proyecto aprobado.
7. Renderizar y ejecutar el preflight técnico solo para las variantes justificadas.
8. Vincular cada preview al SHA-256 exacto. Varias plataformas pueden referenciar el mismo hash universal; una variante nueva conserva su hash y revisión propios.

La salida del plan es `ready_for_platform_preview`, no `approved_for_render`: aun faltan los gates de preview y coincidencia semantica.

## Generar un plan

Primero copie `templates/platform-master.json` al proyecto y complete aprobacion, locks y hashes. Luego:

```bash
python3 scripts/plan_platform_derivatives.py \
  --master /ruta/al/proyecto/platform-master.json \
  --target PLATFORM-INSTAGRAM-REELS-ORGANIC-001 \
  --target PLATFORM-TIKTOK-ORGANIC-001,PLATFORM-YOUTUBE-SHORTS-001 \
  --output-dir deliveries \
  --out /ruta/al/proyecto/platform-adaptation.json
```

Sin `--target`, se incluye solamente Instagram Reels como máster social universal. Los demás perfiles siguen disponibles, pero deben solicitarse explícitamente después de documentar por qué no puede reutilizarse el mismo archivo. El script no renderiza ni modifica la composición.

## Comprobar una entrega

Preflight tecnico inicial:

```bash
python3 scripts/check_platform_delivery.py \
  --profile PLATFORM-YOUTUBE-SHORTS-001 \
  --media /ruta/al/proyecto/deliveries/youtube/VIDEO-01-shorts.mp4 \
  --out /ruta/al/proyecto/deliveries/youtube/VIDEO-01-shorts-check.json
```

El codigo `4` significa que el archivo paso la comprobacion tecnica, pero aun necesita revision visual. El codigo `3` significa fallo tecnico o visual; `2`, entrada invalida; `0`, entrega lista.

La revision visual es un JSON persistente y ligado al hash del render:

```json
{
  "schema_version": "1.0.0",
  "profile_id": "PLATFORM-YOUTUBE-SHORTS-001",
  "output_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "reviewer": "nombre-humano",
  "reviewed_at": "2026-09-25T12:00:00Z",
  "preview_context": "YouTube Shorts preview en iPhone y Android",
  "checks": {
    "live_preview_on_target_surface": true,
    "essential_content_inside_safe_zone": true,
    "captions_legible_and_unobstructed": true,
    "cta_legible_and_unobstructed": true,
    "face_not_obscured": true,
    "content_semantics_unchanged": true
  },
  "note": "Sin colisiones visibles."
}
```

Vuelva a ejecutar con `--review revision.json`. Si el render cambia un solo byte, el hash deja de coincidir y la revision no es reutilizable.

## Evidencia oficial vigente al 25 de septiembre de 2026

- Meta: [Reels ads creative guidance](https://www.facebook.com/business/ads/facebook-instagram-reels-ads). Recomienda 9:16, audio y mensajes clave en zona segura; el alcance citado es publicitario.
- TikTok: [Auction in-feed ad specifications](https://ads.tiktok.com/resources/help/article/tiktok-auction-in-feed-ads?lang=en-GB) y [creative quality checklist](https://ads.tiktok.com/business/library/Top_Tips_One_Pager_SMB.pdf). El alcance citado es publicitario y la propia documentacion advierte que la zona segura varia.
- YouTube: [three-minute Shorts eligibility](https://support.google.com/youtube/answer/15424877?hl=en) y [upload encoding guidance](https://support.google.com/youtube/answer/1722171?hl=en-GB).

Antes de cambiar un limite oficial, actualice la fuente, `evidence_reviewed_at`, la version del perfil y sus pruebas. Nunca convierta por intuicion una zona segura interna en una regla oficial.
