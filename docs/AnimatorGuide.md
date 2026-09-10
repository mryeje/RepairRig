# RepairRig animator guide

## Open and pose

Open `blend/RepairRig_02_ControlRig.blend` in Blender 5.0.1. Select **RepairRig**
and enter **Pose Mode**. Press **N** in the 3D Viewport for Rigify's **Rig Main
Properties** and **Rig Layers** panels (Rigify still labels its collection buttons
"layers"). The mannequin faces -Y; +Z is up; .L/.R refer to the character's sides.
The rest pose is a neutral A-pose, not a standing-idle animation.

The generated `rig_ui.py` Text datablock is part of standard Rigify. Enable
execution for this trusted project if Blender asks, or run that Text once to
register its UI. No RepairRig add-on is required. Enable bundled Rigify in
Preferences > Add-ons when editing/regenerating the metarig.

## Controls

| Purpose | Standard control |
|---|---|
| Whole rig placement | root |
| Body translation / squat | torso |
| Pelvis tilt | hips |
| Chest | chest |
| Extra spine shaping | spine_fk, spine_fk.001–.003 |
| Neck / head | neck, head |
| Hand IK | hand_ik.L / hand_ik.R |
| Elbow poles | upper_arm_ik_target.L / .R |
| Arm settings | upper_arm_parent.L / .R |
| Arm FK | upper_arm_fk, forearm_fk, hand_fk with .L/.R |
| Foot IK | foot_ik.L / .R |
| Foot roll / pivot | foot_heel_ik.L / .R, foot_spin_ik.L / .R |
| Knee poles | thigh_ik_target.L / .R |
| Leg settings | thigh_parent.L / .R |
| Leg FK | thigh_fk, shin_fk, foot_fk with .L/.R |
| Finger master | f_index.01_master.R, f_middle.01_master.R, etc. |
| Thumb master | thumb.01_master.L / .R |

Move IK hands and feet with G; rotate with R. IK/FK is **0 = IK, 1 = FK**.
The initial rig uses IK, pole vectors on, and IK Stretch 0 for predictable limb
length. Move torso downward to bend the legs while feet stay planted. Move knee
or elbow poles to set bend direction. Keep targets within limb reach.

For FK, show the corresponding FK collection and use Rigify's snap controls
before changing IK/FK to avoid jumps. Key the switch property alongside the
relevant transforms. Parent-space changes also need Rigify's snapping workflow.
Final parent settings are recorded in `docs/control_manifest.json`; they are
part of the reuse contract, not arbitrary interchangeable options.

Finger masters curl the chain using **local Y scale** (S, Y, Y); approximately
0.55–0.7 is a useful test curl. Enable **Fingers (Detail)** for individual
phalanges, spread and thumb adjustment. Master curl alone is not a validated
tool grip. Grip pose assets are deferred to Stage 3/4.

## Minimal face

Show **Simple Face** in the Rigify collection buttons. Rotate eye.L/eye.R for
eye direction; rotate jaw about its local X for opening. Move brow.L/R and
mouth_corner.L/R subtly for brows and a simple smile indication. Select lid.L/R
and set its **blink** custom property from 0 to 1 in Bone Properties > Custom
Properties. These sliders drive standard eyelid shape keys. The lids are
stylized spherical covers; the mouth corners are separate proxy geometry,
not a continuous facial skin or FACS system. Head/eye target constraints are
reserved for Stage 3.

The simple face bones are native Rigify `basic.super_copy` components. The
metarig in the final checkpoint includes the blink properties for regeneration.
Proxy shape-key drivers refer to the generated rig by bone/property path.
Check these paths after regeneration. Rigify may reset generated limb properties;
reapply IK Stretch 0 and pole vectors on if needed. Never clear the rig's entire animation
data to switch Actions: that would also delete Rigify's constraint drivers.

## Add an animation manually (later library work)

1. Save a new .blend checkpoint. Select RepairRig in Pose Mode.
2. Open Dope Sheet > Action Editor. Create/name an Action, for example
   BODY_Bend_Forward. Ensure the **RepairRig object slot** is selected.
3. Choose the controls the motion owns; insert only needed location/rotation/
   scale keys. Hover a custom property and press I when its value is needed.
4. Pose and key the next frame. Check planted feet, limb reach and finger
   intersections. Record the frame range and required IK/FK/parent settings.
5. Preserve the Action with Fake User or an NLA strip. Push Down to NLA when
   ready, then create the next Action. An active Action may override NLA, so
   unlink it when testing the strip assembly outside Tweak Mode.
6. Use NLA strip influence and transitions for compatible channels. Prefer
   REPLACE for disjoint control ownership first. ADD/COMBINE requires a planned
   reference pose and tested rotations/scales. Slots are not body-part masks.

For a hand pose: select only the relevant hand/finger controls, pose them, and
use Pose Library > Create Pose Asset. Name it POSE_Grip_Screwdriver_R. It is a
single-frame Action asset with a slot. Browse **Current File** in Asset Browser
to inspect it. An external asset library directory can later point inside this
project; that preference has not been installed globally.

## Tools and targets (planned, not implemented)

A tool can use Child Of targeting the rig and a suitable hand bone, with
Set Inverse to preserve placement. An explicit grip Empty can provide an offset.
For contact, position a repair_target/screw_target Empty on the appliance and
constrain hand_ik to a compatible target with native constraints. Verify axes,
space, inverse and dependency direction before animating influence. The tool
must not drive a hand that also drives that same tool.

## Characters and limitations

Use the same metarig schema and Rigify version for future characters. Fit bones
in Edit Mode, regenerate and bind the new mesh to DEF groups. Object scale stays
one. Reusing an Action by name/path is not automatic retargeting. Moderate limb
changes can invalidate IK contact; rest orientation changes also affect FK.
Cross-character transfer and animation survival through regeneration are not
certified by this base-rig build. Test them before publishing library Actions.

The 78-piece proxy is for posing and dependency checks. Segmented shoulders,
hips and torso cannot validate production skin quality. Elbow sleeves do test
blended Armature deformation. No walk, kneel Action, tool, appliance, grip
library or NLA demo is included at this stage.
