# Stage 4 completion report

Delivered locally on 2026-09-11:

- `blend/RepairRig_04_ActionLibrary.blend`
- `docs/animation_library.md`
- `docs/adding_new_animation.md`
- Group checkpoints, review renders and validation evidence under `tests/stage4/`.

The library contains all 15 requested motion Actions: six BODY Actions, three
REACH Actions, BRACE_Forward_L, two screwdriver directions, the pliers squeeze,
and both presentation gestures. All six requested POSE_ hand assets are present.
See the action/asset tables in `animation_library.md` for their exact names,
ranges, owners and prerequisites.

BODY motion, arm motion, hand grip, tool-axis motion and head attention remain
separate. No complete full-body animation was required. The demo adds only three
shot-specific Actions: relaxed arm carriage, head attention timing, and cumulative
visible screw rotation. It begins with the screwdriver already held and ends
explaining with the same tool; pickup/release remain Stage 3 workflows.

## What blends and what requires fitting

Standing idle, the left-kneel entry, and the matching stand transition have
compatible endpoints. The demo reuses idle and reverses reach/brace strips for
withdrawal. BODY + right reach + left brace + head attention + screwdriver
rotation run on separate channels. The tool can be muted without changing body
or brace. Three CW cycles play in the main NLA sequence; both directions and all
other declared loops pass three-repeat tests.

These are REPLACE component Actions, not additive deltas. Two right-arm Actions,
or left reach plus left brace, cannot independently own the same channels.
Different foot placements need pose fitting before a crossfade. Body retiming
requires retiming shot arm carriage and contact events. A different appliance
requires wrist-target/pole fitting; larger changes may require a different body
pose. Pointing is manually aimed, with no brittle target solver.

Low right reach and screwdriver cycles depend on the existing screw/wrist
hierarchy. Mid right and low left use their explicitly named wrist targets.
Brace uses TARGET_Brace_L. All use Rigify IK. Free gestures also use native IK
to preserve compatibility with the current interaction workflow; there are no
within-Action IK/FK switches. An FK variant remains an ordinary Rigify authoring
task, with snapping and attachment-reference fitting as documented.

## Validation

The saved file was opened in a fresh Blender 5.0.1 process and all 485 demo frames
were inspected. The saved and reopened checksums match in `finish.json` and
`reopen_validation.json`. All 15 motions and six pose assets survive reopening.
Action/slot references resolve, keyed controls respect their scopes, and the
original Rigify rest skeleton, 109 drivers, contact constraints and screwdriver
hierarchy are retained. Earlier checkpoint hashes are unchanged.

Final demo maximums:

- Hand IK/deform-hand position difference: about 0.126 mm.
- Leg IK/deform-foot position difference: about 0.235 mm.
- Actual deformed-hand/tool-grip difference: about 0.126 mm.
- Engaged screwdriver tip error: below 0.001 mm.
- Stationary kneeling foot drift: zero at sampled frames.
- Repeated tool-transform difference: zero at corresponding frames.

Both kneeling sides and stand-up were checked for a planted support foot through
the transition and stationary final feet. The inherited simultaneous foot lift
was replaced with staggered placements. A brief resting-left-arm overreach was
corrected by raising its intermediate wrist pose. The mid-reach target was also
moved inside the unstretched arm's range before expanding the library.

Native Asset Browser tests cover all six poses, selected-finger-only application,
50% blending, and screwdriver-to-open switching. Pliers jaw drivers match the
open/closed values, and its fitted Child Of matches the hand socket at open,
closed, and returned frames. The pliers is a simple editable proxy mechanism.

One persistence issue was caught by the final fresh-process check: clearing an
Action's Asset status also cleared its fake user. The unused variants were
restored from the Stage 4 backup, fake users explicitly restored, and the entire
saved-file validation repeated successfully. Static hand poses remain Asset
Browser assets; motion clips are chosen through the Action Editor/NLA.

## Quality and reuse limits

The motions have restrained timing, readable utility poses and explicit support
transfers. Balance is visually authored, not physically simulated. Review used
the existing segmented proxy, whose elbow seams and separated finger segments
limit deformation assessment. Master-only hand poses need thumb/phalange fitting
for a final prop. HoldSmallPart is a cupped supporting pose, not a precision pinch.
There is no collision, force, torque, pressure, thread or centre-of-mass solver.

Action Slots provide ownership, not retargeting or bone masking. Reuse on another
compatible Rigify character requires matching names, parent settings and control
orientations, with offsets fitted to its proportions. Cross-character transfer,
large/oriented target moves and production skin were not validated here.

For Stage 5, prioritize testing one production character, refining thumb/tool
clearance and kneel support on its proportions, and collecting animator feedback
on a few differently placed appliance targets before adding more motions.
Stage 5 has not been started.
