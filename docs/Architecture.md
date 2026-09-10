# RepairRig architecture — Stages 1–2

## Decision before implementation

Use Blender 5.0.1's bundled Rigify human metarig. Preserve its body, limb,
palm and finger components and their stock names. Remove the full face component
before generation: a technical mannequin does not need Rigify's full facial rig.
Add a small set of standard `basic.super_copy` facial bones to the metarig so
they survive regeneration. No separate animation/retargeting framework.

The metarig is the editable construction source. The generated armature is the
animation owner. Meshes use Armature modifiers and DEF-bone vertex groups.
Animator controls use Rigify's bone collections and generated sidebar UI;
ORG/MCH/DEF internals stay hidden. The proxy is intentionally simple segmented
geometry, with smooth blended joint test geometry where useful; it is not a
production skinning example.

## Reuse contract

Version and reuse this same metarig template, Rigify version, bone names,
component types, parent topology, rotation modes, IK/FK settings and parent-space
settings. Keep object transforms at identity and use meters. Fit metarig bones in
Edit Mode before generating another character. Do not rename generated controls.
Actions live on generated rig OBJECTS, not metarigs or armature data.

Matching channel names permit Action reuse but do not constitute retargeting.
Local FK rotations and finger poses are the strongest candidates for transfer.
IK translations use distances in rig units; changed limb lengths/rest frames
change the result. Planted hands/feet, reach, kneeling and tool contacts require
target repositioning and pose correction. No successful cross-proportion
transfer is claimed until measured on a second generated character.

Regenerate into Rigify's assigned target rig only after saving a new checkpoint.
Rigify rebuilds bones and rig UI. Even when Actions remain assigned, changes to
rest poses, topology or settings can change motion. Avoid hand-editing generated
bones/constraints as permanent architecture; add supported components to the
metarig. Re-test animation, bindings and external constraints after regeneration.

## Native animation plan (later stages)

Use one object Action Slot for the generated rig per Action. Slots bind channels
to animated data-blocks; they are not body-part masks. Key only needed controls.
Use separate Actions for body, reach, hand and head only when their channels and
IK/parent dependencies permit independent composition. NLA tracks/strips provide
timing, transitions, influence and REPLACE/ADD/COMBINE blending; do not assume
arbitrary overlapping IK Actions blend into a valid contact pose. Explicitly
key IK/FK and space switches when required. Avoid baked root motion by default.

Names: BODY_Kneel_L, REACH_Forward_Mid_R, TOOL_Screwdriver_CW_R,
POSE_Grip_Screwdriver_R. Record frame ranges and control ownership for each.
Hand poses are single-frame Action assets for the native Pose Library/Asset
Browser. Library creation and NLA assembly are out of scope for Stages 1–2;
temporary API/posing tests are permitted and removed from the deliverable.

## Interaction plan (Stage 3, not implemented yet)

Use logical names in documentation mapped to stock controls, not replacement
bones: hand.R/L -> hand_ik.R/L; foot targets -> foot_ik.R/L; root -> root;
pelvis reference -> hips. Tool grip empties may be bone-parented to the hand
deformation bone for evaluated hand motion. Tools use native Child Of constraints
with Set Inverse. Appliance empties: repair_target, screw_target, brace_target,
pickup_target, handle_target, tool_grip_target. Use a world-space target to drive
hand IK through Copy Transforms/Child Of where appropriate; prevent circular
dependencies between hand, tool and repair target. A head/look target uses native
tracking constraints with influence control after axis and parenting tests.

## References

- https://docs.blender.org/manual/en/5.0/addons/rigging/rigify/introduction.html
- https://docs.blender.org/manual/en/5.0/addons/rigging/rigify/metarigs.html
- https://docs.blender.org/manual/en/5.0/animation/actions.html
- https://developer.blender.org/docs/release_notes/5.0/animation_rigging/
- Runtime API inspection: tests/environment.json (installed Blender is authoritative).

Official Rigify documentation describes generated rigs as standard Blender rigs.
Local installed source and visible-session tests will resolve API details.
