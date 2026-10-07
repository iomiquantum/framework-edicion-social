# HyperFrames verification for visual direction

Use only after reading the active HyperFrames project instructions and the relevant HyperFrames skills.

## Build discipline

- Every scene should be a sub-composition.
- Keep one captions track and separate voice, music, and SFX tracks.
- Build the intended static end state before adding motion.
- Use deterministic, seek-safe timelines.
- Store fonts and required assets locally.
- Use stable id and data-hf-id values for Studio-editable elements.

## Verification sequence

### Pass 1 — diagnosis

1. Capture at least one meaningful frame per scene; capture early/middle/late states for scenes with moving panels or type.
2. Inspect a whole-piece contact sheet at phone scale and inspect short scenes separately so uniform sampling cannot skip them.
3. Record every visible overlap, occlusion, detached connector, weak hierarchy, low-contrast label and caption/UI collision before editing.

### Pass 2 — correction

1. Run lint after structural changes.
2. Run the full HyperFrames check with dense representative samples, transition boundaries and snapshots.
3. Fix text overflow, held overlaps, detached connectors, runtime errors and contrast failures. Do not replace a correction with an allow-marker unless snapshots prove the layering is intentional and readable.
4. Re-capture the corrected scene states and compare them to the diagnosis list.

### Pass 3 — rendered delivery

1. Open the persistent Studio preview only after checks pass.
2. After explicit render approval, extract frames from the produced MP4 at early, middle and late states of every scene, including every short scene.
3. Around every transition, inspect at least `t-2`, `t-1`, `t`, `t+1` and `t+2` rendered frames at the delivery frame rate. Cross-scene text, connector remnants and outgoing objects must read as deliberate choreography, not accidental double exposure.
4. Inspect the final video contact sheets at phone scale and confirm that the caption lane never collides with titles, UI, faces or critical actions.
5. Verify the exact rendered artifact with a new modification time or checksum, `ffprobe` dimensions/frame rate/codecs, full-file decode, integrated loudness and true peak. Record human listening as `por confirmar` when it was not performed.
6. The delivery gate requires zero unresolved visual errors. Tool warnings may remain only when the corresponding rendered frames were inspected and documented as intentional or non-visual technical debt.
7. If any defect remains, return to Pass 2 and repeat Pass 3; never label the output final based only on source snapshots.

Passing automation does not prove visual quality. Record both automated results and what was actually inspected visually.

## Face and caption QA

- Treat the entire face movement envelope as protected, not only the frame midpoint.
- Keep the caption lane physically separate when possible.
- Sample the last frame of a scene: late pose changes often create collisions absent at the midpoint.
- If an overlay crosses a face, recompose the zones; do not merely lower opacity.

## Documentation

For a material redesign, keep:

- the prior version unchanged;
- a version-specific creative-direction note;
- source and research links with caveats;
- a scene-by-scene audit;
- validation output or summary;
- a review note that states what still needs human judgment.
