# Stage 5F — Production hand deformation and pliers grip

Saved and independently reopened:
`E:\RepairRig\blend\RepairRig_05F_ProductionCharacter_HandPolished.blend`

Source: `E:\RepairRig\blend\RepairRig_05E_ProductionCharacter_PliersAligned.blend`.

This is a scoped improvement, not certification that arbitrary tight hand poses are production-ready. Existing palm/thumb folds and extreme-curl limits remain. No packaging or animation-library expansion was performed.

## Diagnosis: multiple contributors, not just weights

**Weights.** The original hand has substantial adjacent-finger influence. By dominant-weight region, 238 index, 347 middle, 190 ring, and 108 pinky vertices have more than 1% influence from another finger. Some index vertices receive 30–49% from middle-finger groups. These counts include transitional regions and are not all automatic errors; distal cross-finger influence is the suspect portion. Raw deform-weight sums are also not consistently one. Blender normalizes during evaluation, so raw normalization alone is not evidence of the folding cause.

**Joint placement, metarig, lengths and axes.** All 15 right deform segment heads/tails match the production metarig exactly. The corresponding left/right joint positions and lengths are mirror-symmetric within floating-point tolerance. There is no one-sided roll/axis flip. Local axes vary along fitted curved finger chains; this is not a reason to impose canonical-proxy axes. The ring distal segment is only **7.356 mm** long; its sampled joint cross-section radius is about **9.320 mm**. This short, thick articulation is particularly sensitive to concentrated curl. It is a fitting/geometry limitation, not a missing bone or failed rig generation. Section-centroid measurements are approximate skin samples, not proof that every pivot is anatomically ideal.

**Topology and skinning.** The selected hand contains **8,751 quads and 8,809 unique vertex positions**. No edges with more than two incident selected faces were found; its 114 boundary edges include the selection cut. The undeformed rest hand has no detected nonadjacent triangle self-crossings. Therefore this is not simply too few polygons or an already inverted rest mesh. Supporting vertices exist, but their placement, weight transitions, joint centers and pose amplitudes still have to agree. The current armature uses linear skinning, with Preserve Volume disabled. I did not enable it globally: that would change the already-working wrist/body/tool grips.

**Pose amplitude and joint-specific evidence.** In the original Fist and Point, the ring finger produces 18 same-finger triangle crossings. Fist also has two index crossings; the small-part pose has one index crossing. Area-ratio diagnostics show strong local compression around PIP/DIP regions, especially middle PIP and ring PIP/DIP. Triangle area is a collapse indicator, not a measured closed-volume loss. The existing ring Fist/Point concentrates approximately 69.421° at PIP and 64.867° at DIP despite its short distal segment. Redistributing 15° from PIP to MCP removes those 18 ring crossings without reducing total curl.

**Thumb base.** Thumb-base/palm interaction is broad and pose-dependent. Even the neutral/OpenHand controls have six palm/thumb crossings in the saved work posture, whereas the rest mesh has none. The first thumb joint's sampled section centroid is about 11.155 mm from the pivot, inside a broad approximately 24.647 mm median-radius region; this is not a thin finger hinge. The synthetic all-joints-tight test strongly worsens palm/thumb intersections. These observations implicate base fitting/weight transition and amplitude together; they do not justify blindly repainting or rotating the thumb base.

Neutral hand controls and `POSE_OpenHand_R_Production` are equivalent identity transforms on the 20 finger controls. Rest-mesh and posed-neutral checks were performed separately. All six requested poses were compared from palm and side views.

## Exact changes

### Localized weights

Changed **257 right-hand vertices**, and no others. The complete per-vertex, per-group before/after values are recorded in `tests/hand_polished/checkpoint.json` → `weight_changes`.

The cleanup:

1. Selects confidently finger-owned vertices beyond 55% of the proximal segment, excluding palm, webs, MCP and thumb-base regions.
2. Requires proximity within 19 mm of that finger chain and at least a 1.25 distance separation from neighboring chains, with at least 45% existing own-finger influence.
3. Transfers foreign-finger influence into the vertex's existing own-finger groups proportionally. The transfer fades in between 55% and 85% of the proximal segment. No broad smoothing across fingers is used.
4. Bounds the trial's displacement in the working screwdriver pose to approximately 0.35 mm, then normalizes all affected deform weights.
5. Rejects the middle-finger portion of the trial because it added six local crossings to Fist/Point. The accepted cleanup is deliberately narrower than a whole-hand repaint.

All affected deform-weight sums validate to one within 1e-5. Palm/wrist vertices and all mesh coordinates/topology remain unchanged. Screwdriver contact remains clear.

The rig is symmetric, but this mesh is not exactly mirror-correspondent: no candidate reflected vertex matched within the conservative 0.05 mm threshold. Example nearest discrepancies were 0.315–1.421 mm. Consequently **no left-side weights were changed**; copying onto arbitrary nearest vertices would not preserve meaningful symmetry. Left-side anatomical weight fitting should use its own mesh correspondence if requested later. No left-side pose or rest asymmetry was introduced.

### Three production Pose Assets only

`POSE_Fist_R_Production` and `POSE_Point_R_Production`: ring MCP **+15°**, ring PIP **−15°**, DIP unchanged. Final ring flexion is approximately **62.135°, 54.421°, 64.867°**. Total curl is preserved; the other fingers are unchanged.

`POSE_Grip_Pliers_R_Production`: changes relative to Stage 5E, in local FK Euler degrees:

| Finger | MCP flexion | PIP flexion | DIP flexion | MCP splay | MCP opposition/roll |
| --- | ---: | ---: | ---: | ---: | ---: |
| Index | 0 | −6 | 0 | −3 | 0 |
| Middle | +3 | 0 | 0 | +3 | 0 |
| Ring | 0 | −3 | 0 | +6 | 0 |
| Pinky | −6 | 0 | 0 | 0 | 0 |
| Thumb | 0 | +3 | −6 | 0 | 0 |

The existing opposed thumb base was retained; the thumb's distal distribution was adjusted to improve pad contact/clearance. Index splay and middle closure better seat the fingers; ring splay and pinky MCP clearance remove handle crossings without globally relaxing all poses. Masters remain unchanged, so the pliers jaw opening/contact calibration does not change.

The three assets retain their names, native slots, asset metadata and reset channels. `OpenHand`, `HoldSmallPart`, and `Grip_Screwdriver` Actions are **bit-for-bit identical in their F-curve payloads**. No canonical hand assets or body/reach/tool Actions were changed. Full original/final angle arrays are in the checkpoint report; stored rotations are native quaternions.

### Intentionally unchanged

- All metarig and generated rig rest matrices, bone lengths and local axes.
- Mesh positions, topology, modifier architecture, palm and wrist weight regions.
- Tool sockets, origins, contact references, work-target offset and hierarchy.
- Screwdriver grip Action, attachment, work position and operation.
- Pliers jaw driver and calibrated contact point.
- RepairRig Tools embedded UI text, selector and driver architecture.
- Canonical Stage 4 and source Stage 5E files, verified by hashes.

## Reopened validation

All six assets passed both slotted-Action evaluation and actual native Asset Browser application in a separate Blender GUI session. Every asset channel matched exactly on application.

| Pose | Before hand self-crossing pairs | After |
| --- | ---: | ---: |
| OpenHand | 36 | 36 |
| Fist | 52 | 34 |
| Point | 50 | 32 |
| HoldSmallPart | 33 | 33 |
| Screwdriver grip | 32 | 32 |
| Pliers grip | 80 | 76 |

These totals include palm/wrist intersections and must not be confused with prop penetration. Pliers reaches farther than screwdriver, so its saved work posture has more palm-region intersections even with the same wrist orientation. After refinement, Fist and Point have **zero ring/ring crossings**. Residual Fist pairs are 29 palm/palm, three palm/thumb and two index/index; Point has only the first two categories. Pliers retains 74 palm/palm, one ring/palm and one index/index pair.

**Hand/handle surface crossings:** pliers **66 → 0**; screwdriver **0 → 0**. No sampled hand vertices lie inside either handle. Pliers nearest sampled finger/thumb gaps are approximately **0.32–0.47 mm**, and nearest palm clearance is about **1.22 mm**. This supports a close visual grasp but does not simulate pressure or certify a physical clamp.

The two work references still coincide with the existing operation target at full engagement within 1e-5 m. UI attach/release states are correct and mutually exclusive. Tool/screw operation samples at frames 1, 17, 33, 37 and body/reach samples at 1, 17, 33 have **zero maximum matrix-element difference** from Stage 5E. Tested body/reach Actions: `BODY_Kneel_L`, both right forward reaches, left low reach and left brace. Neutral-hand mesh difference is only 0.000000255 m (evaluation noise).

## Remaining limits and future character requirements

This pass does **not** eliminate all palm/thumb-base folds or make arbitrary extreme curls safe. The deliberately severe synthetic test (65°/80°/45° on every finger including thumb, without anatomical opposition fitting) remains badly folded: **582 → 584** crossing pairs. That slight regression is recorded, not treated as success. The delivered named poses improve or remain unchanged; a tight-fist or squeeze-cycle production shot still needs dedicated fitting and review.

Further work on those extremes would need a separate, coordinated hand-fitting pass: anatomically suitable MCP/PIP/DIP centers and segment lengths, deliberate crease/knuckle loop placement, isolated distal finger weights with smooth adjacent-segment transitions, and possibly pose-corrective shapes or a carefully evaluated local skinning solution. Simply subdividing this already-dense mesh or weakening every pose is not the remedy. No such structural/topology expansion was performed here.

For future production characters:

- Fit pivots to actual knuckle/crease locations and validate joint thickness versus available segment length before generating the deform rig.
- Provide clean quad flow with supporting loops on both sides of bending creases, enough outer-knuckle volume, and a broad, well-supported thumb saddle/web.
- Keep distal finger weights isolated from neighboring digits; allow intentional blending at webs and the thumb base. Normalize and test each joint independently before whole-hand curls.
- Validate open, point, moderate and tight closure, opposition, grasp transitions, and the intended tool squeeze cycle. Review skin, not just bone tips.
- Keep rig/control naming, reach architecture, tool switching and generic body motions reusable. Keep weights, exact joint fit, thumb opposition, grip poses, sockets and any corrective shapes character-specific.

## Evidence

Local artifacts in `tests/hand_polished/`:

- `diagnosis.json`, `topology_fit.json`, `rest_stress_validation.json`: diagnosis and limitations.
- `checkpoint.json`: exact weight changes, pose parameters, preservation data and input/output hashes.
- `reopen_validation.json`, `asset_browser_validation.json`: saved-file tests.
- `before_*_palm.png`, `before_*_side.png`, `saved_*_palm.png`, `saved_*_side.png`: comparable diagnostic renders. These use isolated evaluated hand geometry to expose folds without body occlusion; faceted shading emphasizes topology.

Reproduction/inspection code: `scripts/46_inspect_hand_deformation.py` through `scripts/53_hand_rest_and_stress_audit.py`, plus `scripts/hand_polish_common.py`. Blender files and generated artifacts remain local and Git-ignored.
