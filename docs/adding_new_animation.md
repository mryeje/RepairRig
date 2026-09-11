# Adding another repair animation

Use `blend/RepairRig_04_ActionLibrary.blend` as the working reference and Save As a
new shot/variant file. Keep the delivered checkpoints. Enable bundled Rigify and
the trusted generated rig UI for its standard control panel. No development runner
is needed to open, edit or play the library.

## Choose the smallest useful component

Decide whether the new item describes body support, one arm, a hand shape, a tool
cycle, or attention. Use a single-frame Pose Asset for a static hand shape. Use an
Action for motion over time. Use ordinary constraints for target contact and native
drivers for mechanical relationships such as the pliers jaws. Use a full-body
Action only when coupled balance/support changes cannot be managed reliably as
separate components; document that choice rather than forcing additive layering.

Name it `BODY_Description`, `REACH_Description_R`, `TOOL_Description_R`,
`GESTURE_Description_R`, or `POSE_Description_R`. `L` and `R` are the character's
sides. Use `SHOT_` for staging that is specific to one sequence. Keep a fake user on
library Actions; mark only static hand-pose Actions as Pose Assets.

## Duplicate and edit a native Action

1. Select the intended owner. Most motions belong to RepairRig; screwdriver cycles
   belong to CONTACT_ScrewdriverRoll_R.
2. Mute conflicting NLA tracks while authoring. Assign the source Action and its
   compatible object Action Slot in the Action Editor.
3. Make an independent copy of the Action datablock and rename it before editing.
   Duplicating only an NLA strip can leave the underlying Action shared.
4. Enter Pose Mode and key only the required Rigify controls/channels. Avoid a
   Whole Character keying set. For small edits, key only Location, Rotation, a
   selected custom property, or the needed finger scale component.
5. Set a useful range beginning at frame 1. This library uses 33-frame approaches,
   49-frame kneeling transitions, a 65-frame idle, 37-frame screwdriver cycles,
   and a 25-frame pliers cycle at 24 fps. Change timing when the motion requires it.
6. Use the Graph Editor to remove unused/accidental channels and inspect handles.
   Default AUTO_CLAMPED handles give restrained easing. Use Constant interpolation
   for discrete attachment or IK/FK switches.
7. Scrub the entire Action, including intermediate contact/clearance poses. Check
   silhouette, elbow/knee direction, support, and prop grip in multiple views.

Keep most animation in place. Torso lowering and local foot placement belong in a
kneel; walking across the room does not. Preserve compatible parent settings and
rest orientations. No Action Slot or naming convention automatically retargets
different skeletons or scales foot/hand offsets for another character.

## Contact and tools

Fit the body first, then place the wrist/contact Empty and its pole. For the right
screwdriver reach, reuse TARGET_Screw -> CONTACT_ScrewdriverRoll_R ->
CONTACT_WorkGrip_R -> CONTACT_WorkWrist_R. Keep the shaft's local +Z toward the
screw. Do not constrain the tool back to a target that depends on the same tool.

Use normal Rigify IK for planted hands and feet. If a gesture variant uses FK,
snap with Rigify's generated controls before changing mode and key both the
receiving controls and switch. Test the exact boundary frames. The existing
right-hand tool reference follows hand_ik.R, so an FK tool variant needs the
reference adapted and validated with standard constraints.

For a new grasp, apply the nearest hand Pose Asset and adjust thumb, fingers and
socket to the actual handle. A single-frame pose is not an animated close/release.
Key a separate narrow finger Action only when such timing is needed. The pliers
driver reads the index master; inspect its Graph Editor driver if changing the
open/closed scale range or jaw mechanism.

For a pickup, align hand and tool, fit the attachment, then use Child Of Set Inverse.
Key influence 0 immediately before pickup and 1 at pickup. For release, capture the
evaluated tool transform, key that placement, and disable attachment without a jump.
See `Stage3_Interaction.md` for the established workflow. Do not replace the native
constraints with an animation runtime.

## Create a hand Pose Asset

Select only the right finger controls that the asset should own, pose them, then
use Blender's Pose Library Create Pose Asset command. Name it `POSE_..._R`. It
creates a native single-frame Action asset. In Current File, test Apply Pose with
all relevant fingers selected, selected-finger-only application, and Blend Pose
from a different starting hand. Save the file to retain the asset. Extra thumb or
phalange controls are appropriate for a more precise grasp; document their scope.

Do not make a second static Action merely to duplicate the asset. For a changing
grip, apply/key the asset at the appropriate frames in a motion Action instead.

## Assemble and validate in NLA

Push Down the Action or add an Action strip on its owner. Keep the active Action
unlinked during shot playback. Use REPLACE for this library's component Actions;
their keyed channels provide separation. Two Actions owning the same arm are
alternatives or transitions, not independent layers.

Match endpoint poses before adding blending. Preserve a planted support foot
through a kneel/stand transition. Retiming BODY actions also requires retiming
shot arm carriage and contact events. Blend In/Out is useful for small adjustments,
but does not correct incompatible foot locations or unreachable wrist targets.

For a loop, make the first/last channel values compatible, check their slopes,
set NLA Repeat to at least 3, and inspect every join. For screwdriver cycles,
check engaged tip position throughout each turn and clearance during the return.
Update shot-specific screw rotation independently if changing direction/count.

Before accepting a new item, inspect its F-curves for unrelated controls, verify
its slot and intended object, and test it with a body pose and another independent
component. Save, reopen, and repeat the structural and visual checks. Add its
purpose, keyed controls, range, loop status, IK/target prerequisites and known
blend limitations to `animation_library.md`. Keep review outputs under a new test
subdirectory so earlier evidence remains understandable.
