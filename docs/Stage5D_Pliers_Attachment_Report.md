# Stage 5D: enable the existing pliers attachment

Inspected input: `E:/RepairRig/blend/RepairRig_05C_ProductionCharacter_GripRefined.blend`.
New checkpoint: `E:/RepairRig/blend/RepairRig_05D_ProductionCharacter_PliersAttach.blend`.

## Findings before correction

| Requested item | Screwdriver | Pliers |
|---|---|---|
| Exact tool root object | `TOOL_Screwdriver` | `TOOL_Pliers` |
| Attachment constraint | `Attach / release \| right hand socket` | `Attach / release \| pliers right socket` |
| Constraint type | Native Child Of | Native Child Of |
| Owner / target space | World / World | World / World |
| Target socket | `ATTACH_Screwdriver_R` | `ATTACH_Pliers_R` |
| Saved influence in 05C | 1 | 0 |
| Muted | No | No |
| Active object Action / NLA tracks | None / none | None / none |
| Attachment influence driver | None | None |
| Stored attachment Action | `STAGE3_TOOL_AttachRelease_R` | None |

Both sockets already exist and are children of `REF_Hand_R`. That reference has a native Copy Transforms constraint targeting `RepairRig`, bone `hand_ik.R`, at influence 1. Both Child Of inverse matrices are valid: enabling the pliers constraint aligns the tool root to the fitted pliers socket within floating-point tolerance. No required attachment target, socket, constraint, or driver is missing.

The unused screwdriver attachment Action has slot `OBTOOL_Screwdriver`. It keys `constraints["Attach / release | right hand socket"].influence` at frames 1=0, 111=0, 112=1, and 288=1. It is not active in 05C and does not cause the screwdriver's current attachment. The screwdriver is already attached because its saved influence is 1.

No Action in 05C keys the pliers attachment influence. Its available pliers-specific Actions are `POSE_Grip_Pliers_R`, `POSE_Grip_Pliers_R_Production`, and `TOOL_Pliers_Squeeze_R`. These belong to the rig's hand controls. The squeeze Action and existing jaw drivers control grip/jaw motion, not pickup or attachment.

The exact cause of the reported behavior is therefore saved influence 0 on the pliers Child Of. Applying the pliers hand pose cannot change a separate tool object's constraint. Stage 5C intentionally parked the pliers and selected the screwdriver for its saved review state.

## Smallest correction

In 05D, pliers attachment influence is 1 and screwdriver attachment influence is 0. This selects one tool for the saved hand demonstration. The existing `POSE_Grip_Pliers_R_Production` values were applied as an unkeyed finger state; its Action was not edited. The existing right reach remains active at frame 33.

No new Action, driver, constraint, target, socket, rig system, or automatic pose-to-tool coupling was added. No inverse matrix was recalculated. Both tool workflows remain available through their existing native Child Of influences.

## Attach, detach, and switch tools

Select the tool root object and open Object Constraints:

- Pliers: on `TOOL_Pliers`, set `Attach / release | pliers right socket` Influence to 1 to attach or 0 to detach.
- Screwdriver: on `TOOL_Screwdriver`, set `Attach / release | right hand socket` Influence to 1 to attach or 0 to detach.
- When switching, turn off the old tool's attachment, turn on the new tool's attachment, and apply the corresponding production hand pose. A hand pose alone does not select a tool.

For a timed switch, insert ordinary Influence keyframes and use Constant interpolation for an instantaneous attach/detach. The inactive tool returns to its existing unconstrained parked transform. This toggle is not an animated physical pickup or a drop-in-place solution: releasing at a new world location additionally requires fitting/keying the tool's unconstrained transform at the release frame using Blender's normal visual-transform/keying workflow. No new pickup choreography was authored here.

## Validation and preservation

After reopening 05D:

- Pliers influence is 1; screwdriver influence is 0 for the saved selection.
- Pliers follow the moving socket at reach frames 1,17,33; maximum socket-relative matrix difference is 1.79e-7.
- Detaching restores the original parked transform; reattaching restores socket alignment.
- Re-enabling the screwdriver restores its source attachment transform.
- All Action payloads, including every production hand pose, are identical to 05C.
- All armature rest matrices are identical to 05C.
- Stage 5C and the canonical Stage 4 file remain byte-identical.

Evidence: `tests/pliers_attach/inspection.json` and `correction_validation.json`. Implementation: `scripts/42_enable_production_pliers.py`. The new Blender file remains local and Git-ignored.
