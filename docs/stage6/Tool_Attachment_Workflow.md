# Tool attachment and work contact

## Structure

The character package contains `REF_Hand_R`, which follows `hand_ik.R`, and its fitted child sockets `ATTACH_Screwdriver_R` and `ATTACH_Pliers_R`. Each separate tool asset already has exactly one native Child Of constraint, initially disabled and without an external rig target:

- Screwdriver: **Attach / release | right hand socket**.
- Pliers: **Attach / release | pliers right socket**.

After appending, **Bind Imported Tools** assigns the matching existing socket, restores the selector influence driver, and connects the native pliers jaw driver. It does not duplicate constraints, reparent tool roots, change the grip, or move the tool origin. Repeated binding is safe for one unambiguous set of local tools. Bind while roots retain their authored transforms; moving them first invalidates the stored inverse calibration.

## Buttons and selector

`RepairRig["repairrig_tool"]` is an integer property:

| Value | State | Screwdriver Child Of | Pliers Child Of |
| --- | --- | ---: | ---: |
| 0 | Release Tool | 0 | 0 |
| 1 | Attach Screwdriver | 1 | 0 |
| 2 | Attach Pliers | 0 | 1 |

The panel exposes all three buttons plus the numeric property. Hand poses are always separate. Use the appropriate production Pose Asset yourself. The script uses the selected rig or an unambiguous single library rig, not a development-file path.

## Work alignment

The work chain is `TARGET_Screw → CONTACT_ScrewdriverRoll_R → CONTACT_WorkGrip_R → CONTACT_WorkWrist_R → CONTACT_ToolWorkOffset_R`. The existing `Work | TARGET_Screw` constraint on `hand_ik.R` targets the final helper.

- Screwdriver contact: `REF_ScrewdriverTip`, local tool +Z = 0.235 m.
- Pliers contact: `REF_PliersContact`, approximately local +Z = 0.151891768 m at the calibrated production jaw opening.
- Pliers selection adds approximately 0.110294268 m along the fitted local wrist-work Z direction; screwdriver selection leaves that offset zero.

These dimensions and the socket fit are character/tool-specific. The shared reach Action animates constraint influence, not the contact geometry. Keep that separation when adding tools.

## Key pickup / release

1. Select `RepairRig`. Preserve body/reach animation in NLA, and unlink any shared Action from the active Action Editor before creating selector keys.
2. Create a new **shot-specific Action**, e.g. `SHOT_ToolSelection`.
3. At the initial frame set Tool = 0. Right-click the numeric Tool property in RepairRig Tools and choose **Insert Keyframe**.
4. At pickup set 1 or 2 and insert another key. At release set 0 and key again.
5. In Graph Editor select this property's keys and set **Interpolation Mode → Constant**.
6. Push the shot Action to its own NLA track with Replace blending and appropriate Hold extrapolation. Do not add these keys to reusable BODY/REACH Actions.

Key the **selector**, not the already-driven influences. It keeps both attachments and the work-offset choice synchronized. A button alone changes the current value; it does not automatically insert a key or override a keyed NLA strip on later frames.

Release returns the unattached tool root to its authored/animated transform. For a drop at a new location, author detached-root transform keys matching the desired world pose at release, with attachment influence off. There is no automatic physics, world-position preservation, or grip change. Moving the detached root later may require intentional inverse recalibration before another attach.

## Troubleshooting

- **Panel absent:** run embedded `RepairRig_Library_UI.py`; allow trusted scripts when reopening.
- **Tool stays parked:** append the complete Collection, select the local rig, bind, then attach; check selector keys/NLA.
- **Duplicate tools/rigs:** append complete assets once. Binder refuses ambiguous duplicate role candidates; it does not guess.
- **Linked tool is read-only:** use the documented appended interactive wrapper workflow.
- **Pliers miss target:** check the production grip/master scale, work constraint target and selector offset before moving sockets. A different jaw aperture changes the real end-effector geometry.
