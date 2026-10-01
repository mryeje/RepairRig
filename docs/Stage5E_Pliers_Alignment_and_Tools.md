# Stage 5E — Pliers contact and tool controls

Input: `E:\RepairRig\blend\RepairRig_05D_ProductionCharacter_PliersAttach.blend`

Output: `E:\RepairRig\blend\RepairRig_05E_ProductionCharacter_PliersAligned.blend`

## Diagnosis

The pliers attachment was correct. The shared `Work | TARGET_Screw` constraint targeted `CONTACT_WorkWrist_R`, calibrated for screwdriver geometry. The pliers have a shorter working length and a different fitted socket translation. Together these left the distal jaw midpoint **0.110294281 m (110.294 mm / 4.34 inches)** short at frame 33. This is a tool-specific work-target assumption, not a broken attachment or screw animation.

Both sockets are children of `REF_Hand_R`, which follows `RepairRig` / `hand_ik.R`. Their local transforms, in metres, are listed below. Rotation is 180 degrees about local Z and scale is unity, within stored floating-point noise. Full stored basis and world matrices are in `tests/pliers_aligned/inspection.json`.

| Socket | Local translation XYZ | World translation XYZ at source frame 33 |
| --- | --- | --- |
| `ATTACH_Screwdriver_R` | (-0.042999997735, 0.129999965429, 0.034999996424) | (-0.239999949932, -0.438999950886, 0.480000078678) |
| `ATTACH_Pliers_R` | (-0.042999923229, 0.130000025034, 0.007813960314) | (-0.240000039339, -0.411813914776, 0.480000078678) |

The screwdriver contact is `REF_ScrewdriverTip`, local (0, 0, 0.235) under `TOOL_Screwdriver`. Its work chain is `TARGET_Screw` → `CONTACT_ScrewdriverRoll_R` → `CONTACT_WorkGrip_R` → `CONTACT_WorkWrist_R`. WorkGrip contributes local (0, 0, -0.235); WorkWrist accounts for the fitted screwdriver grip/socket.

The pliers had **no dedicated contact reference**. Their intended work end is the midpoint between the two distal jaw ends. In the saved production grip this is local (0.000000000211, 0.000000002437, 0.151891767979) under `TOOL_Pliers`, world (-0.240000069141, -0.563705742359, 0.480000048876). The screw target is (-0.239999994636, -0.674000024796, 0.479999989271).

The 83.108 mm length difference plus 27.186 mm socket-axis difference explains the shortfall. Neither socket nor tool origin was changed: doing so would disturb the fitted grip.

## Minimal correction

- Added `REF_PliersContact` at the measured distal jaw midpoint.
- Added `CONTACT_ToolWorkOffset_R`, parented to the existing `CONTACT_WorkWrist_R`.
- Retargeted the existing `Work | TARGET_Screw` constraint to this new child, preserving its name, ordering, spaces, influence curves, and rotation behavior.
- For pliers only, the child adds local translation **(-0.000000087747, -0.000000000502, 0.110294267535)**. For screwdriver or no tool it is identity.
- The offset inherits existing tool rotation and withdrawal; it does not suppress the intentional screw-operation motion.

No existing Actions, sockets, finger pose transforms, mesh coordinates/weights, or rest bones were edited. Stage 4 and Stage 5D files remain unchanged. No reparenting or duplicate attachment constraints were introduced.

The reference is calibrated to the existing production pliers grip/jaw opening. A materially different jaw aperture or tool model warrants recalibrating its contact; this is not a physical clamping simulation.

## RepairRig Tools UI

Open Stage 5E and allow execution of its trusted embedded scripts. In the 3D View, press **N**, choose **RepairRig**, and open **RepairRig Tools**.

- **Attach Screwdriver:** screwdriver Child Of influence 1, pliers 0; original screwdriver work alignment.
- **Attach Pliers:** pliers Child Of influence 1, screwdriver 0; pliers work offset enabled.
- **Release Tool:** both influences 0.

These buttons set `RepairRig["repairrig_tool"]`: **0=None, 1=Screwdriver, 2=Pliers**. Native simple-expression drivers synchronize existing Child Of influences and the tool-specific work offset. Buttons do not apply a hand pose. Apply the appropriate existing production pose separately.

The UI is embedded as `RepairRig_Tools_UI.py` with Register enabled; no installed add-on or external package is required. If automatic script execution is disabled, run that text once in Blender's Text Editor. The integer custom property is also accessible in Object Properties → Custom Properties. Do not key the driven constraint influences directly; key the selector instead.

### Animate pickup / release without changing shared Actions

1. Select `RepairRig`. Preserve the current reach/body Action in its existing NLA setup or note it for reassignment. Unlink it from the active Action Editor before creating selector keys; **do not add selector keys to a reusable library Action**.
2. Create a separate shot Action, e.g. `SHOT_ToolSelection`.
3. At each desired frame set Tool to 0, 1, or 2. Right-click the numeric Tool property in the panel and choose **Insert Keyframe**. Add an initial key establishing the starting state.
4. In the Graph Editor, select the Tool curve's keys and use **Constant** interpolation for discrete switching.
5. Push the shot Action into its own enabled NLA track, using Replace blending and Hold extrapolation. Restore the original reach Action if it was previously active. Its channels do not overlap the selector property.
6. Scrub to verify pickup/release and reach together. Once keyed, editing a button at a keyed frame changes only the current value until you insert/replace that key.

Release follows the existing architecture: influence 0 restores the tool's unattached transform (currently its parked location). It does **not** create a physics drop or preserve the release world position automatically. For a drop-in-place shot, also author the detached tool's transform keys at release; no tool reparenting is needed.

### Add another tool later

Create its fitted hand socket and one Child Of attachment, measure a local work/contact reference, and calculate a tool-specific work offset while preserving the hand grip. Extend the selector range, mutually exclusive influence expressions, work-offset expressions, and UI button for the new state. Keep reusable body/reach Actions unchanged and author pickup timing in a shot selector Action. This extension was not performed here.

## Validation

Reopened Stage 5E in a fresh Blender process with embedded script execution enabled. Panel registration and all three native operators passed; repeated selection produced no duplicate constraints. Native drivers evaluated correctly.

- Jaw midpoint to work target at full engagement: **0.0000000745 m** residual (floating-point noise).
- Source/output comparisons at frames 1, 17, 33, 37, 161, 179, 197 preserved wrist rotation and screw transforms.
- Screwdriver attachment matrix and tip-to-work contact matched the original workflow.
- Existing Action curves, rest matrices, and socket transforms matched exactly.
- Hand/prop surface test found no increase in sampled penetrating vertices; the review render shows work-end contact. Existing low-poly surface intersections are not claimed to be eliminated.
- Separate Constant-key selector NLA playback tested without saving a new animation-library Action.
- Original Stage 4 and Stage 5D hashes were verified unchanged.

Artifacts: `tests/pliers_aligned/inspection.json`, `build.json`, `validation.json`, and `contact_review.png`. These generated artifacts and Blender binaries remain local/ignored. Source implementation: scripts 43–45 and `scripts/repairrig_tools_ui.py`.
