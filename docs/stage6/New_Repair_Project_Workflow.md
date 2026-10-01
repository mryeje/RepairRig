# Start a new repair animation

Use the standard Asset Browser and File → Append workflows below. Do not copy objects from development checkpoints. The deterministic Collection/Action Append route described here was tested in a factory-startup project; external poses were applied with Blender's native Asset Browser operator.

## 1. Import complete assets

Use **Asset Browser Apply Pose only for static `POSE_*` hand assets**. Use **File > Append for multi-frame Actions**, then Action Editor/NLA for playback. Seeing a motion thumbnail in Asset Browser does not mean double-clicking it imports a timeline clip.

1. Choose **File → New → General**; delete the default cube, camera and light if not needed. Save your project outside the library.
2. **File → Append → E:\BlenderAssets\RepairRig\Character\RepairRig_Production.blend → Collection → RepairRig_Character_Production → Append**. Keep **Instance Collections** disabled in the file-browser options. Import at the authored world origin initially.
3. Repeat for **Tools\RepairRig_Screwdriver.blend → Collection → RepairRig_Tool_Screwdriver**.
4. Repeat for **Tools\RepairRig_Pliers.blend → Collection → RepairRig_Tool_Pliers**.
5. Optionally append **Tools\RepairRig_Worksite.blend → Collection → RepairRig_Worksite_Demo**. Otherwise use your own appliance.

The same Collection assets are discoverable in Asset Browser. If using drag/drop instead, use Append rather than Link and ensure you bring in editable objects, not merely a Collection instance. Freehand placement can change the authored placement; the exact File → Append route above avoids that ambiguity. Do not move tool roots before their first binding.

## 2. Activate UI and connect assets

If you already dragged the character into the scene as a local Collection Instance, select that instance in Object Mode and choose **Object > Apply > Make Instances Real**. In the operation options (F9), enable **Parent** and **Keep Hierarchy**. Select the resulting armature, not the instance Empty; its name may be `RepairRig.001`. This combination was tested at the authored origin, including remapped reach targets and the mesh Armature modifier. Direct Collection Append with Instance Collections disabled remains the simplest default; do not import a second character to repair an existing editable one.

Select the generated `RepairRig`, run embedded **RepairRig_Library_UI.py** once from Text Editor, then return to the 3D View. Press **N → RepairRig → RepairRig Tools → Bind Imported Tools**. Binding is idempotent: it reuses the existing Child Of constraints and restores native jaw/selector drivers.

If you appended the optional worksite, click **Connect Demo Worksite**. This connects only the worksite screw to the character's work target; tools are never reparented.

## 3. Reuse body and reach Actions

### First verify one imported reach clip

1. Return to **Object Mode**. Choose **File > Append** and open **E:\BlenderAssets\RepairRig\Actions\RepairRig_Motion.blend**.
2. Open its **Action** folder, select **REACH_Forward_Mid_R**, and click **Append**. This imports the actual multi-frame datablock; it does not automatically assign it to the character.
3. Select the editable generated armature (`RepairRig`, or the realized `RepairRig.001`). Change an editor to **Dope Sheet**, then choose **Action Editor** in its mode selector. Leave the editor unpinned so it follows the selected object.
4. In the **Action datablock dropdown**, choose `REACH_Forward_Mid_R`. If needed choose its existing **OBRepairRig** Action Slot. Do not create a new empty Action or a new empty slot; the slot identifier can remain OBRepairRig even if the object has a numeric suffix.
5. Scrub **1, 17, 33**. The right hand must change position as the reach influence changes. No tool or UI script is required for this standalone reach test.
6. If there is no motion, confirm the Action and populated slot are assigned to the armature, not the mesh/instance Empty. Exit NLA tweak mode and mute conflicting NLA tracks for this isolated test. Merely applying an Asset Browser pose is not Action assignment.

The other reach/brace clips use the same procedure. Keep imported unused Actions using their Fake User/shield if they are not yet assigned or stored in NLA; appended library Actions already carry retention metadata.

### Combine clips for a shot

1. **File → Append → Actions\RepairRig_Motion.blend → Action**. Select `BODY_Kneel_L`, `REACH_Forward_Low_R`, `BRACE_Forward_L`, and `TOOL_Screwdriver_CW_R`; Append.
2. Select `RepairRig`. Change an editor to **Dope Sheet → Action Editor** and choose `BODY_Kneel_L` in the Action datablock dropdown. If needed choose its `OBRepairRig` Action Slot. Scrub frames **1–49**.
3. For a quick still test, evaluate the kneel at frame 49, then choose the right-hand reach and evaluate frame **33**. These are partial-channel Actions; the unkeyed body state remains for inspection, but this alone is not a durable layered animation.
4. For animation, push the body Action into the **NLA Editor**, then assign/push the reach onto a separate track. Use **Replace** blending on nonoverlapping channels and **Hold Forward/Hold** extrapolation as appropriate. For the demo: body starts at 1; reach starts at 65 and reaches full influence at 97. Add left `BRACE_Forward_L` at 65 on another track; otherwise the left arm can remain in its initial pose.

Do not apply a BODY/REACH motion clip as if it were a one-frame hand Pose Asset. Select it in Action Editor/NLA for playback. Slot compatibility alone does not guarantee correct control/constraint paths.

BODY, REACH/BRACE, GESTURE and `TOOL_Pliers_Squeeze_R` belong to the armature's `OBRepairRig` slot. Screwdriver CW/CCW Actions instead belong to `CONTACT_ScrewdriverRoll_R` with `OBCONTACT_ScrewdriverRoll_R`. Actions are partial-channel clips, not full-scene resets: switching Actions does not clear every unkeyed control or constraint left by a previous clip. Build intentional NLA layers and review the starting pose. Rig/control compatibility is required; this is not automatic retargeting.

## 4. Screwdriver grip, attachment and operation

1. Select the rig, enter **Pose Mode**, and select the right finger controls: the five `.01_master.R` controls plus `.01.R`, `.02.R`, `.03.R` for index, middle, ring, pinky and thumb. Selecting all control bones is also safe for these production hand assets, which only contain finger channels.
2. In Asset Browser choose **RepairRig → Hand Poses → Production**, select `POSE_Grip_Screwdriver_R_Production`, and use **Apply Pose** (right-click asset menu). This applies unkeyed values; key the finger controls if the pose must persist in a shot.
3. In RepairRig Tools click **Attach Screwdriver**. The pliers detach automatically.
4. With the right work reach fully engaged, `REF_ScrewdriverTip` should meet the work point.
5. Select **CONTACT_ScrewdriverRoll_R**, not the rig or tool mesh. Choose `TOOL_Screwdriver_CW_R` in Action Editor, with slot `OBCONTACT_ScrewdriverRoll_R`. Scrub **1, 17, 33, 37**. In a layered shot, put this clip on that object's NLA track; the demo starts it at frame 101.

The optional screw is not a physics simulator. The demo uses native, shot-local drivers on its Z rotation/translation to follow the work-roll object. Adapt screw response to your appliance; do not expect every screw model to move just because an Action is assigned to the rig.

## 5. Pliers and release

Static pose application is independent of the active body/reach Action: it sets finger values without replacing that Action or slot. Disable Auto Keying for an unkeyed preview. To animate a grip, insert keys for the selected finger controls into a shot-local hand Action and layer it in NLA; avoid adding production-specific finger keys to the reusable reach clip. Applying a pose need not leave its source Action in the local Action dropdown. Use the production pose catalog for this character; canonical poses are references for the proxy proportions.

Apply `POSE_Grip_Pliers_R_Production` through Asset Browser; click **Attach Pliers**. The existing tool selector enables the pliers-specific work offset. At full work reach, `REF_PliersContact` meets the same working target. Do not move the socket or share the screwdriver tip length to repair alignment.

Click **Release Tool** to disable both attachments. This restores each root's parked transform, not a physical drop-in-place. See [Tool_Attachment_Workflow.md](Tool_Attachment_Workflow.md) for pickup/drop keys.

Save, close and reopen your project with trusted embedded scripts allowed. Confirm one character rig, both tool targets, the intended Action Slots and the UI. Library updates do not automatically overwrite appended local copies.

## Inspect the supplied demo

Open `Demo/RepairRig_NewProject_Validated.blend` and play frames **1–260**. Markers identify kneel, reach/attachment, screwdriver operation, release, pliers grip/alignment and release. Separate tracks hold body, right reach, left brace, hand poses and tool selection; the work-roll object has its own operation track. For manual button tests, mute **04 | Tool pickup / release (Constant)** first—scrubbing otherwise restores its authored selector keys.
