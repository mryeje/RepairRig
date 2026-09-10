# Stage 3 - appliance interaction proof of concept

Open `blend/RepairRig_03_InteractionTest.blend` in Blender 5.0.1. The scene uses the
existing Stage 2 RepairRig and its original proxy character. The metarig, generated
control architecture, deformation bones and 109 Rigify drivers were retained.
No Stage 4 animation library, custom animation runtime or new rig generator was built.

The file opens at a working pose. Shift-Left Arrow returns to frame 1; Space plays
frames 1-288 at 24 fps. Timeline markers name the phases. Numpad 0 toggles the
review camera. The saved clean viewport hides overlays: Shift-Alt-Z is not needed;
use the Viewport Overlays button (or Shift-Alt-Z only if mapped in your keymap).
The standard Blender default overlay toggle is Shift-Alt-Z? To avoid keymap
ambiguity, use the two-overlapping-circles button in the viewport header.
Select RepairRig, enter Pose Mode, and enable overlays to see Rigify controls.

## Sequence and reusable ownership

| Action / asset | Owner and purpose | Timing |
|---|---|---|
| BODY_Kneel_L | RepairRig: torso/chest, foot IK and knee poles only | Stand 1-16, lower/step 16-64, hold to 288 |
| REACH_Forward_Low_R | Right hand IK, elbow pole, pickup/work constraint influence | Pickup at 104; work contact at 146 |
| LEFT_Brace | Left hand IK, elbow pole and brace influence | Contact at 94; hold |
| GRIP_Close_Screwdriver_R | Five right finger-master scales | Close 101-112; hold |
| POSE_Grip_Screwdriver_R | Native single-frame Action asset; five finger masters only | Reusable static grip |
| HEAD_Look_Target | Head Damped Track influence | Gradual attention to work area |
| TOOL_AttachRelease_R | Screwdriver Child Of influence | Off through 111, on from 112 |
| TOOL_Screwdriver_CW_R | CONTACT_ScrewdriverRoll_R local Z rotation and withdrawal | Action 1-37; NLA repeats 3 times at 152-260 |
| SHOT_Screw_QuarterTurns | Visible screw rotation | Shot-specific matching quarter turns |

Every rig Action owns disjoint F-curve channels. Each has a native object Action
Slot. Slots identify the animated object; they are **not** body-part masks.
The selected keyed channels provide the separation. There is no full-body baked
Action. Keep the rig's active Action unlinked when reviewing the NLA assembly.
Never clear RepairRig.animation_data: it contains Rigify's drivers too.

## Kneeling and reach

BODY_Kneel_L lowers the torso 0.50 m, shifts it 0.06 m in +Y, adds about 31.5 degrees
of forward torso lean and 14.3 degrees of chest lean. The left knee goes to the
pad; the left foot moves backward and tilts onto its toe, while the right foot
steps forward with a lift. Leg IK holds the final feet. Knee poles establish bend
planes. These values fit this approximately 2 m test mannequin, not every human.

Edit the BODY track in NLA Tweak Mode (select its strip, Tab), or assign its Action
and slot in the Action Editor with the corresponding NLA track muted. Pose the
Rigify controls; do not edit generated DEF/MCH bones. Arm/leg IK_FK is 0, IK Stretch
is 0 and pole vectors are on. Existing parent settings remain those of Stage 2.
Exit Tweak Mode before testing the complete shot.

A nearly upright kneel failed to reach both contacts without arm stretch. The
forward lean and higher left brace were fitted manually. This was a pose-fitting
issue, not a reason to modify the base rig. Farther targets still need fitting.

## Appliance targets and dependency direction

The mannequin faces -Y; Z is up; .R/.L are the character's sides. Target transforms
are in scene metres with identity armature object transform.

- TARGET_Screw is at (-0.24, -0.674, 0.48). Its local +Z points into the appliance.
  Place its origin at the screw/blade contact plane. It owns the visible screw,
  TARGET_Look and the working-hand reference hierarchy.
- TARGET_Brace_L is the **left wrist** contact transform, not a fingertip location.
  At (0.27, -0.642, 0.75), its rotation makes the fingers point up and the palm face
  the cabinet. Allow for palm thickness and appliance depth.
- TARGET_Look inherits the screw location. The head uses native Damped Track,
  Track Z, with partial influence 0.78. This guides the head generally toward
  work; it is not eye tracking or a neck collision solver.
- TARGET_ToolGrip is an independent pickup reference at the screwdriver's grip
  centre. Moving this reference does not automatically move the unattached tool
  or its stand. Align all three when laying out a different pickup.

Right hand_ik.R has WORLD-to-WORLD Copy Transforms constraints to
CONTACT_PickupWrist_R and CONTACT_WorkWrist_R, with keyed influence. The pickup
reference is a child of TARGET_ToolGrip. The working reference is derived from:

TARGET_Screw -> CONTACT_ScrewdriverRoll_R -> CONTACT_WorkGrip_R -> CONTACT_WorkWrist_R

CONTACT_WorkGrip_R is 0.235 m behind the screw along target local Z. The wrist
reference uses the inverse of the hand-to-grip offset. Rotating the roll Empty
therefore moves the wrist around the tool axis while keeping the engaged blade
tip fixed. Rigify solves the elbow and forearm from the resulting IK control.
The left hand has its own WORLD Copy Transforms constraint to TARGET_Brace_L.

These are normal editable Empty hierarchies and Blender constraints. Targets drive
the hand; the hand drives the tool. The tool never drives a target that drives the
same hand, so this dependency chain has no tool/hand feedback cycle.

## Grip, attachment and release

TOOL_Screwdriver is an Empty at the grip centre, with tool geometry as children.
Local +Z follows the shaft; REF_ScrewdriverTip is at local (0, 0, 0.235).
The handle has a visible stripe so rotation can be read in the viewport.

REF_Hand_R copies hand_ik.R. Its child ATTACH_Screwdriver_R provides the grip offset:
(-0.027, 0.122, 0) in hand space, with orientation aligning the shaft to hand local
+Z. This fits the current curled fingers. TOOL_Screwdriver has an ordinary Child Of
constraint targeting that socket, with an inverse established at pickup. It is
not permanently parented to the hand. Constraint influence switches discretely
from 0 to 1 at frame 112; this is not a gradual attachment blend.

For a new pickup, place the tool, pose the hand/grip around it, fit the socket,
and use Child Of > Set Inverse at the attachment frame while other conflicting
constraints are disabled. Key influence 0 on the preceding frame and 1 at pickup;
use Constant interpolation for the switch. Check for a jump by scrubbing both
frames. Merely changing influence without fitting the inverse can jump the tool.

For release, retain the tool's **evaluated world transform** at the release frame.
Key influence 1 on the preceding frame and 0 on release, and key the tool's own
location/rotation to that retained visual pose on release. Blender's Visual
Transform/Visual Keying workflow can capture the constrained pose; after disabling
the constraint, verify the unconstrained tool has that same placement before
inserting ordinary location/rotation keys. Then animate the released tool on its
own. Do not reset its inverse while it is still attached. The validation performs
this operation, moves the hand, confirms zero tool drift, then restores the main
shot. The main shot intentionally ends holding the screwdriver.

The Pose Asset is a native single-frame Action with an object slot. In an Asset
Browser choose **Current File**, select POSE_Grip_Screwdriver_R, and apply it to
RepairRig in Pose Mode using the normal Pose Library controls. It stores only the
five right finger masters (Y scale 0.58 for fingers, 0.70 for thumb), so it does not
move the body or wrist. The separate grip-close Action animates into that pose.
Mute that animated grip track when manually experimenting, or its keyed values
will reassert on frame changes. Different handle diameters require finger/thumb
and attachment-offset fitting; this is not automatic grasp synthesis.

## Screwdriver Action and NLA

TOOL_Screwdriver_CW_R contains one 90-degree clockwise stroke, a 22 mm withdrawal,
a wrist return, and reseating. Clockwise is viewed from the handle toward the screw.
The cross-shaped blade/recess permits reseating after each quarter turn. The screw
mesh has a shot-specific Action that holds its new angle while the hand returns.
There is no simulated thread advance, torque, friction or screw extraction.

The Action acts on CONTACT_ScrewdriverRoll_R, not the whole arm. The hand follows
the rolling wrist reference and Rigify solves the limb. This permits limited wrist
and forearm motion rather than winding the whole arm through repeated 360-degree
turns. Some elbow movement is necessary because the wrist is offset from the shaft.

The roll Empty has an NLA strip starting at 152, Action range 1-37, Repeat 3,
REPLACE, HOLD extrapolation. The rig has separate REPLACE/HOLD_FORWARD tracks for
body, reach, brace, grip-close and look. The assembly uses disjoint channels;
additive whole-body layering was unnecessary. Pickup/contact influence remains
inside the reach Action because it is coupled to the reach timing. The visible
screw's cumulative rotation is shot-specific, not part of the repeating wrist
Action; retime it if changing the stroke count or timing.

The NLA test compares corresponding frames of repeated strokes and checks that
muting the tool track stops its motion without changing body or brace. Blender
can retain the last evaluated value when a track is muted; mute does not promise
a neutral wrist pose. Explicitly reset the roll Empty when a neutral comparison
is wanted, then unmute to restore the animated evaluation.

## Actual second-location trial

The screw target was moved +0.06 m in X and +0.04 m in Z to
(-0.18, -0.674, 0.52). The entire 1-288 sequence was evaluated again. All Action
F-curves and keys were compared before/after and were identical. The test file is
`tests/RepairRig_03_TargetB.blend`; the main file retains location A.
REF_Screw_Location_B is an unanimated bookmark of the tested second position.

Automatically adapted: working right-hand IK, attached screwdriver, tip contact,
roll/withdrawal motion, visible screw and head look target. The reach's blend into
the working target also changed without new keys. The body, left brace and pickup
remained as authored and needed no edits for this small move.

For another appliance: reposition and orient TARGET_Screw and TARGET_Brace_L,
place TARGET_ToolGrip plus the loose tool and support, and check reach/clearance.
For larger changes: fit the root/body, foot/knee and elbow poles, contact offsets,
trajectory and timing as needed. Constraints do not avoid obstacles or preserve
anatomical reach automatically. Cross-character or rotated-appliance transfer was
not tested. The successful nearby translation is the scope of the reuse claim.

## Evidence and limits

`tests/stage3_validation.json` records every frame, the second-target trial,
attachment/release, actual deformed-hand grip error and Rigify driver validity.
`tests/stage3_component_validation.json` records NLA isolation/repeat and a grip
Pose Asset Action-slot application test. `tests/stage3_reopen_validation.json`
checks the deliverable after loading it again. Renders and visible-window captures
are in `renders/` (ignored by Git). Human review covered standing, lowering,
kneeling, pickup, grip, contact, turn and withdrawn return poses.

This is an architectural POC. The proxy is segmented, the elbow sleeves kink in
some poses, fingers can touch/intersect the simple handle, and the kneel has only
a few keys. There is no collision system, balance simulation, finger pressure,
thread advance, production skin validation, generic retargeter or repair library.
Foot placement and support transitions are approximate. Nearby target movement
worked; arbitrary placement, body proportions and regeneration remain unproven.

Before Stage 4, agree on tool axis/grip-offset conventions, contact ownership and
Action timing; test one additional character proportion and a larger/oriented
appliance move; improve thumb fitting, contact clearance and transition poses.
Only then expand the library. Stage 3 stops here.

## Standard Blender references

These features use Blender/Rigify's existing systems, with ordinary scene data:
[Blender 5 animation changes](https://developer.blender.org/docs/release_notes/5.0/animation_rigging/),
[Rigify arm controls](https://docs.blender.org/manual/en/5.0/addons/rigging/rigify/rig_types/limbs.html),
[Child Of](https://docs.blender.org/manual/en/5.0/animation/constraints/relationship/child_of.html),
[Pose Library](https://docs.blender.org/manual/en/5.0/animation/armatures/posing/editing/pose_library.html),
[NLA strips](https://docs.blender.org/manual/en/5.0/editors/nla/strips.html).
The external scripts are authoring/validation helpers only; no helper is needed
to open, edit, play or render either saved interaction file.
