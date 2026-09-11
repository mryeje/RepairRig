# RepairRig Stage 4 animation library

Open `blend/RepairRig_04_ActionLibrary.blend` in Blender 5.0.1. The file opens at
frame 179 in the repair demonstration. Play frames 1–485 at 24 fps. The technician
starts with the screwdriver held, kneels, reaches and braces, performs three
quarter turns, withdraws, stands, and explains while still holding the tool.
This demonstration does not include a pickup or release; those remain in Stage 3.

The original Stage 1–3 checkpoints are unchanged. The generated Rigify skeleton,
109 Rigify drivers, screwdriver attachment, contact hierarchy, and existing
constraints are retained. Stage 3 Actions are retained as `STAGE3_*` reference
data in the new file. Their old NLA assembly remains in the original Stage 3 file.
No authoring script is needed to use the saved library.

## Naming and channel ownership

Motion names use `CATEGORY_Description[_Side]`, with `L` and `R` meaning the
character's sides. `BODY_` owns torso/chest and leg IK controls; `REACH_` and
`BRACE_` own one arm; `TOOL_` owns the tool cycle or finger motion; `GESTURE_`
owns the right arm. `POSE_` identifies a single-frame hand Action marked as an
Asset for Blender's normal Pose Library. `SHOT4_` identifies demonstration
staging rather than a general-purpose library motion.

Each motion has one native object Action Slot. A slot identifies its animated
object; it is **not a bone mask**. The keyed F-curves determine which controls
the Action affects. The Actions have fake users so unused variants survive saving.
Descriptions, intended owner, scope, and loop status are also stored in Action
custom properties. No root control, armature object translation, or DEF/MCH/ORG
control is keyed by the 15 library motions.

## The 15 motion Actions

All ranges are inclusive. A repeating 1–37 Action has a 36-frame period: the last
key duplicates the first cycle boundary. These timings assume 24 fps.

| Action | Range | Ownership and intended use | Loop / dependency |
|---|---:|---|---|
| BODY_Idle_Standing | 1–65 | Torso/chest breathing and standing leg support | Loop, 64-frame period; leg IK |
| BODY_Bend_Forward | 1–33 | Mild forward service-panel bend, planted feet | Transition then hold; leg IK |
| BODY_Crouch_Shallow | 1–33 | Lower centre of mass over planted feet | Transition then hold; leg IK |
| BODY_Kneel_L | 1–49 | Lower to left knee; step right foot first, then move left | Transition then hold; leg IK; fit knee pad |
| BODY_Kneel_R | 1–49 | Mirrored right-knee support transfer | Transition then hold; leg IK; move pad |
| BODY_Stand_From_Kneel_L | 1–49 | Matching left-kneel-to-standing support transfer | Transition; leg IK |
| REACH_Forward_Low_R | 1–33 | Right wrist/pole and contact influences | Approach then hold; right IK, Stage 3 screw target |
| REACH_Forward_Mid_R | 1–33 | Right wrist/pole and contact influences | Approach then hold; right IK, TARGET_Reach_Mid_R |
| REACH_Forward_Low_L | 1–33 | Left wrist/pole and contact influences | Approach then hold; left IK, TARGET_Reach_Low_L |
| BRACE_Forward_L | 1–33 | Left wrist/pole and brace influence | Approach then hold; left IK, TARGET_Brace_L |
| TOOL_Screwdriver_CW_R | 1–37 | CONTACT_ScrewdriverRoll_R local Z rotation/withdrawal | Loop, 36-frame period; engaged right-hand IK |
| TOOL_Screwdriver_CCW_R | 1–37 | Same roll Empty, opposite quarter turn | Loop, 36-frame period; engaged right-hand IK |
| TOOL_Pliers_Squeeze_R | 1–25 | Y scale on five right finger masters | Loop, 24-frame period; pliers jaw drivers |
| GESTURE_Talk_OneHand_R | 1–49 | Restrained right hand/pole arc, returns to rest | One-shot; normal arm IK, no target |
| GESTURE_Point_R | 1–41 | Right arm extends, holds, returns | One-shot; normal arm IK; apply Point hand pose |

None is a complete full-body clip. BODY motions describe support and torso pose,
not arm carriage or head direction. Reaches/gestures are upper-limb motions, not
whole-upper-body clips. All BODY motions share channels and replace one another;
do not add them together. The demo uses `SHOT4_ArmRest` to coordinate otherwise
independent arms with lowering and standing. Retiming body transitions requires
retiming this shot track too.

The longer screwdriver period is intentional: turn, withdraw 22 mm, return the
wrist, and reseat take 1.5 seconds. The wrist makes a bounded 90-degree stroke;
it does not accumulate full-arm rotations. CW is viewed from handle toward tip.
The visible screw uses `SHOT4_ScrewResult` for cumulative rotation. That shot Action
must be changed if stroke timing/count/direction changes; the tool cycle does not
simulate screw threads or extraction.

## Layering and blending

Use REPLACE NLA blending on disjoint channels. BODY + one right reach + one left
brace + the tool-axis Action + head look can run together. This is partial-channel
composition, not additive animation. None of the library Actions is authored as
an additive delta Action. COMBINE/ADD over the full rig is neither needed nor tested.

Idle ends in the standing pose used by Kneel_L; Stand_From_Kneel_L starts at its
matching kneel and ends in standing. Their sequential strip boundaries match.
No NLA transition strip is needed at these exact boundaries. For a variant,
adjust endpoint poses first; a short overlap using a higher track and Blend In/Out
can soften a small residual difference. Check foot contacts throughout: crossfading
two different planted-foot positions causes sliding and is not a foot-lock solver.

The reach and brace clips finish with contact influence 1. Hold that result with
Hold Forward extrapolation. A second strip of the same Action with Reversed
enabled provides the demo's withdrawal; its extrapolation is Nothing, allowing
the underlying relaxed-arm track to resume. Do not reverse a reach through an
obstacle without editing its path. One right reach and a right gesture share
channels and cannot independently play at full strength. Left reach and left brace
also replace each other. Hand poses and the pliers squeeze overlap finger channels.

## IK, targets, and compatible characters

Arm and leg IK_FK are 0 (IK), IK Stretch is 0, and pole vectors are enabled. The
reach/gesture Actions key the relevant arm IK_FK property to 0 throughout; they do
not switch modes within a clip. Free gestures also use ordinary Rigify IK to keep
their rest endpoints compatible with the existing interaction workflow. An FK
variant is a valid future edit, not a different rig architecture.

For an FK variant, use the generated Rigify panel's normal IK/FK snapping controls
to match the visible pose before changing modes. Key the receiving controls and
the IK/FK property at the boundary, use Constant interpolation on a discrete switch,
and check the adjacent frames. Simply keying the mode property does not snap a limb.

The mannequin faces -Y with Z up. Targets are wrist/contact transforms, not generic
fingertip positions. Low_R uses TARGET_Screw and the existing offset hierarchy;
Mid_R uses TARGET_Reach_Mid_R, tested with BODY_Bend_Forward; Low_L uses
TARGET_Reach_Low_L, tested with Kneel_L. Brace uses TARGET_Brace_L. Move and orient
the appropriate Empty, then fit the body, wrist path and elbow pole. Larger changes
can exceed reach or intersect the cabinet. The initial mid target exceeded reach;
moving its wrist position to (-0.28, -0.38, 1.08) m resolved that case.

BODY poses require foot/pad placement fitting, but no appliance constraint.
Point_R is aimed manually with hand_ik.R and its elbow pole; it has no automatic
point-at solver. Head attention is the retained native Damped Track constraint,
with demo timing in SHOT4_Look. It is separate from arm/body channels.

Compatible Rigify rigs need matching control names, rest orientation, proportions,
parent settings, and custom properties. Append the desired Actions and assign an
appropriate object slot. BODY/gesture curves remain in rig-control coordinates;
contact Actions additionally require the named constraints and target architecture.
Action Slots do not retarget, scale distances, or transfer constraints. Transfer to
another character proportion or a rotated appliance was not validated in Stage 4.

## Hand Pose Assets

| Asset | Purpose |
|---|---|
| POSE_Grip_Screwdriver_R | Existing fitted screwdriver curl |
| POSE_Grip_Pliers_R | Open operating grip for the pliers squeeze cycle |
| POSE_HoldSmallPart_R | Loose cupped support for a small part; not a precision pinch |
| POSE_OpenHand_R | Open finger masters |
| POSE_Fist_R | Closed finger curl |
| POSE_Point_R | Extended index with other fingers curled |

These assets own only five right finger masters. They do not position the wrist.
They are native single-frame Action assets, not duplicated static motion clips.
The animated pliers Action is separate because it describes changing grip over time.

Select RepairRig, enter Pose Mode, and open an Asset Browser set to Current File.
Select all five right finger masters for the complete stored hand pose. Double-click
the asset or use Apply Pose. To affect only one finger, select only its master
before applying. Drag the pose or use Blend Pose to blend toward it; a 50% blend
from open hand to screwdriver grip was tested. Applying OpenHand after Screwdriver
was also tested. Key the selected finger controls if the pose should change over
time; otherwise an applied pose is just the rig's current unkeyed state.

Mute any finger animation that would override manual experiments. The demo's
screwdriver grip is saved as an unkeyed applied hand pose. Applying a pose in the
demo can therefore change the grip for the whole shot until you key a change.
Fit individual finger phalanges and thumb to actual prop dimensions. The segmented
proxy and master-only poses are utility starting points, not collision-free grasps.

TOOL_Pliers is a simple hinged proxy. Its Child Of targets ATTACH_Pliers_R under
the existing right-hand reference. The two jaw-pivot Y-rotation drivers read right
index-master Y scale: 0.78 gives the open grip and 0.52 closes it. The squeeze cycle
also curls the other masters. For a shot beginning with pliers held, activate its
attachment and deactivate the screwdriver attachment. For a pickup, fit the tool
and use standard Child Of Set Inverse/visual keying as documented in Stage 3.
REF_Hand_R follows hand_ik.R: an FK tool workflow needs a corresponding native
hand-reference adjustment and separate validation.

## Human animator workflow

1. Select RepairRig and choose a BODY Action in the Action Editor.
2. Fit appliance targets and the body/feet to the repair location.
3. Add a reach or brace, adjusting hand IK controls and elbow poles as necessary.
4. Apply a hand Pose Asset and fit the tool socket/grasp.
5. Push the motion down to the NLA or add its Action strip to the correct owner.
6. Adjust strip start, scale, repetition, extrapolation and blending.
7. Refine poses manually and scrub contact frames, including transitions.

For manual Action editing, select a strip and Tab into NLA Tweak Mode, then edit
Rigify controls in Pose Mode using the Action Editor/Graph Editor. Exit Tweak Mode
before reviewing the assembly. Alternatively mute the relevant NLA tracks and
assign the Action and its object slot directly in the Action Editor. Unlink the
active Action afterward so it does not override NLA evaluation. Never clear the
rig's animation data: its Rigify drivers also live there.

To make a variant, use the Action datablock's copy/make-single-user control in the
Action Editor, rename the new Action, and keep its fake user enabled. A linked NLA
strip copy still shares the Action. Check the datablock name/users before editing.

To repeat a tool cycle, select CONTACT_ScrewdriverRoll_R, add the CW or CCW Action
strip, and set Repeat in the strip properties. The demo uses Repeat 3 at frame 161,
ending at 269. Use the correct object slot. Do not put that Empty's Action on the
armature. Set the right Work constraint to full contact, attach the screwdriver,
and apply the hand grip before judging alignment.

## NLA demonstration and evidence

The rig's six tracks are ordered BODY, arm rest, right reach, left brace,
presentation, and head. The roll Empty and visible screw have their own tracks.
Enable the NLA Editor's object filtering as needed to see those objects; select
the roll Empty to edit the repeated tool strip. Hover over the NLA Editor and
Ctrl-Space to maximize it, then Home to frame the strips.

Key intervals: idle 1–65; kneel 65–113; approach/brace 129–161; screwdriver 161–269;
reverse approach/brace 269–301; stand 325–373; reused idle 373–485; talk 405–453.
The first reaches hold between their end and the reverse strips. Body holds during
repair, and head/tool/brace motion remains independently editable.

Evidence is under `tests/stage4/`: group channel/validation JSON, pose application
tests, before-save and reopened validation, additional loop/isolation tests, and
PNG review frames. `validate_library.py` can be run from Blender's Text Editor on
the delivered file. The scripts under `scripts/15_*` through `25_*` are offline
authoring/test helpers, not a required animation runtime.

Reopened checks inspect all 485 demo frames, valid Action/slot references, restricted
control ownership, original rest skeleton/drivers/constraints, checkpoint hashes,
actual deform-hand/tool alignment, and stationary feet. All four declared loopable
motions were additionally repeated three times in ordinary NLA. Muting the tool
track was tested to leave body and brace unchanged. Both kneeling variants and the
stand transition keep a support foot planted; final holds have zero measured drift.

Limits: weight and balance are authored visually, not simulated; there is no floor
collision or centre-of-mass solver. Pole directions and clearances still need fitting
on a different body. The segmented mannequin exposes elbow joint seams. Precision
pinches, production skin deformation, arbitrary transfer, and long motion review
on a final character remain future validation work. Stage 5 should prioritize one
production character, thumb/tool clearance, target-placement variants and animator
feedback before expanding the library. No Stage 5 implementation is included.
