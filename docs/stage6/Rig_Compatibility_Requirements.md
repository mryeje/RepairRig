# Rig compatibility and production limits

This is a RepairRig/Rigify-compatible library, **not an automatic retargeting system**. A matching Action Slot type is necessary but insufficient. Arbitrary characters, bone names, proportions or unrelated Rigify generations are not guaranteed compatible.

## Required structure

- The existing generated RepairRig control hierarchy, rest conventions and FK/IK mechanisms.
- Required control names and custom properties, including `hand_ik.R/L`, `upper_arm_parent.R/L`, pole targets, `IK_FK`, `pole_vector` and `IK_Stretch`.
- Exact right-hand constraint names: `Pickup | TARGET_ToolGrip`, `Work | TARGET_Screw`, `Reach | Mid_R`; exact left names: `Brace | TARGET_Brace_L`, `Reach | Low_L`.
- Rig-side pickup/work/brace/reach target chains and native tool selector/work-offset drivers.
- An OBJECT Action Slot compatible with the actual owner. BODY, REACH/BRACE, GESTURE, hand poses and `TOOL_Pliers_Squeeze_R` target the rig. Screwdriver CW/CCW target `CONTACT_ScrewdriverRoll_R`.
- Finger masters and FK controls for the five named digits; production poses specify 20 right-finger controls, including reset channels.

Do not change `pole_vector`, `IK_Stretch`, constraint order, spaces, inverse matrices or fitted axes blindly. The packaged configuration preserves the validated production setup. Do not animate deform bones directly in place of the controls.

## Generic versus character-specific

Reusable: control/constraint conventions, BODY/REACH/BRACE/GESTURE clip organization, tool selector semantics, native attachment architecture, NLA layering, and canonical master-curl hand references.

Character-specific: production mesh and weights; bone fitting/proportions; precise grip FK values; thumb opposition; socket placement; tool-specific wrist/contact offsets; any future corrective shapes. The `_Production` poses are fitted to the supplied Chris mesh, not every human mesh.

Canonical hand poses drive the original master controls and do not clear all production FK offsets. Apply `POSE_OpenHand_R_Production` first before testing a canonical pose after a production pose. Canonical poses remain references, not a promise of a clean grip on this production mesh.

## Preserved Stage 5F limitations

- Local weight cleanup and ring-curl redistribution improve the named poses, but palm/thumb folds and extreme closed-fist limits remain.
- The validated pliers grip has no detected hand/handle triangle crossings at its calibrated state; this is not a physical clamp or universal collision-free guarantee.
- `TOOL_Pliers_Squeeze_R` is retained as a reusable master-scale clip. Combining it with production FK curls changes finger/jaw geometry and has not been contact-fitted across its full cycle. The demo intentionally demonstrates aligned pliers holding, not a newly validated squeeze cycle.
- BODY motions need shot/character review for foot planting, knee contact, clothing and appliance clearance. Body-only clips do not pose every arm/finger channel.
- Release restores parked transforms; pickup and drop are animation, not simulation.
- Default validation covers one complete production rig and one screwdriver/pliers set per project. Multi-character scenes and library overrides need separate validation; they are not certified by this release.

The package contains the generated rig, not the development metarig or alternate high/medium-poly meshes. Rig regeneration is an authoring task requiring the original fitting workflow. Ordinary animation and project-local pose/weight adjustments do not need Rigify regeneration or external dependencies.

Blender 5.0.1 was used for saving and tests. Validate version changes, preserve source library backups, and review rights to the supplied character before redistribution beyond your authorized projects.
