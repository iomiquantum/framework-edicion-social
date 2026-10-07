# Visual quality audit checklist

Use this rubric for a serious audit. Scores guide priorities; they are not a substitute for visual inspection.

| Area | Points | What good evidence looks like |
|---|---:|---|
| Editorial clarity | 15 | Every state has one job; the visual explains or intensifies the spoken idea. |
| Composition and hierarchy | 15 | One dominant focus, one supporting focus, intentional negative space, clear reading order. |
| Face and safe-zone protection | 15 | Moving face/gesture envelopes inspected; no panel crosses eyes, nose, mouth, or chin; destination UI considered. |
| Typography and mobile legibility | 15 | Distinct type roles, short display copy, readable captions, no overflow or accidental overlap. |
| Color and contrast | 10 | Semantic palette, contrast measured, color is not the only carrier of meaning. |
| Visual rhythm | 10 | Changes follow ideas and vocal accents; meaningful reactivation without constant motion. |
| Continuity and variation | 10 | Scenes belong to one system but do not repeat the same card layout. |
| Execution and QA | 10 | Runtime/layout checks, representative snapshots, transition review, and unresolved caveats documented. |

## High-priority defects

- Opaque or translucent graphics crossing a moving face.
- Captions competing with a headline or lower face.
- Disconnected floating boxes or connector lines that land in empty space.
- Repeated equal-weight cards with no dominant idea.
- Tiny nodes and thin strokes inside a large empty canvas.
- Similar sans-serif faces doing every role.
- Long sentences used as display headlines.
- Color contrast below target or white text placed on a bright accent without measurement.
- Decorative motion unrelated to a semantic or vocal change.
- A technically passing composition presented as visually approved.

## “Paint-like” symptoms and corrections

| Symptom | Likely cause | Better response |
|---|---|---|
| Flat rectangles and thin outlines | UI defaults used as visual language | Build one larger editorial object with depth, scale contrast, and a clear focal edge. |
| Large inert gaps | Elements were shrunk instead of composed | Enlarge the explanatory object or restructure the frame into explicit zones. |
| Everything looks the same | One layout and one headline treatment repeated | Alternate presenter+graphic, object-led, type-led, process, and calm close states. |
| More elements make it worse | Decoration added without narrative roles | Remove unassigned elements; keep background, structural, data, annotation, and focal roles distinct. |
| The face is “mostly visible” | Safety judged from one frame | Inspect early/middle/late plus pose changes; reserve the full movement envelope. |

## Practical defaults for 1080×1920 review

These are starting ranges, not platform laws:

- display titles: roughly 90–140 px;
- concepts and nodes: roughly 38–64 px;
- captions: roughly 40–54 px;
- metadata: roughly 24–30 px;
- borders: commonly 3–5 px when they must read on a phone;
- entry motion: roughly 0.30–0.50 s;
- exit motion: roughly 0.18–0.30 s;
- stagger: roughly 0.08–0.12 s.

Prefer a meaningful state change every 2.5–6 seconds as an editorial hypothesis. A slower explanation may need a longer hold; a faster number is not automatically better.

## Final human review

Inspect the piece once without sound and once for audio-visual continuity. Confirm:

- hook and conflict are understood immediately;
- text remains readable at phone size;
- the recommended version works without relying on animation to explain missing logic;
- no transition creates a one-frame collision or flash;
- the close resolves rather than merely stops;
- remaining uncertainties are named.
