# Start a new repair animation

Use the standard Asset Browser and File → Append workflows below. Do not copy objects from development checkpoints. The deterministic Collection/Action Append route described here was tested in a factory-startup project; external poses were applied with Blender's native Asset Browser operator.

## 1. Import complete assets

1. Choose **File → New → General**; delete the default cube, camera and light if not needed. Save your project outside the library.
2. **File → Append → E:\BlenderAssets\RepairRig\Character\RepairRig_Production.blend → Collection → RepairRig_Character_Production → Append**. Keep **Instance Collections** disabled in the file-browser options. Import at the authored world origin initially.
3. Repeat for **Tools\RepairRig_Screwdriver.blend → Collection → RepairRig_Tool_Screwdriver**.
4. Repeat for **Tools\RepairRig_Pliers.blend → Collection → RepairRig_Tool_Pliers**.
5. Optionally append **Tools\RepairRig_Worksite.blend → Collection → RepairRig_Worksite_Demo**. Otherwise use your own appliance.

The same Collection assets are discoverable in Asset Browser. If using drag/drop instead, use Append rather than Link and ensure you bring in editable objects, not merely a Collection instance. Freehand placement can change the authored placement; the exact File → Append route above avoids that ambiguity. Do not move tool roots before their first binding.

## 2. Activate UI and connect assets

Select the generated `RepairRig`, run embedded **RepairRig_Library_UI.py** once from Text Editor, then return to the 3D View. Press **N → RepairRig → RepairRig Tools → Bind Imported Tools**. Binding is idempotent: it reuses the existing Child Of constraints and restores native jaw/selector drivers.

If you appended the optional worksite, click **Connect Demo Worksite**. This connects only the worksite screw to the character's work target; tools are never reparented.

## 3. Reuse body and reach Actions

1. **File → Append → Actions\RepairRig_Motion.blend → Action**. Select `BODY_Kneel_L`, `REACH_Forward_Low_R`, `BRACE_Forward_L`, and `TOOL_Screwdriver_CW_R`; Append.
2. Select `RepairRig`. Change an editor to **Dope Sheet → Action Editor** and choose `BODY_Kneel_L` in the Action datablock dropdown. If needed choose its `OBRepairRig` Action Slot. Scrub frames **1–49**.
3. For a quick still test, evaluate the kneel at frame 49, then choose the right-hand reach and evaluate frame **33**. These are partial-channel Actions; the unkeyed body state remains for inspection, but this alone is not a durable layered animation.
4. For animation, push the body Action into the **NLA Editor**, then assign/push the reach onto a separate track. Use **Replace** blending on nonoverlapping channels and **Hold Forward/Hold** extrapolation as appropriate. For the demo: body starts at 1; reach starts at 65 and reaches full influence at 97. Add left `BRACE_Forward_L` at 65 on another track; otherwise the left arm can remain in its initial pose.

Do not apply a BODY/REACH motion clip as if it were a one-frame hand Pose Asset. Select it in Action Editor/NLA for playback. Slot compatibility alone does not guarantee correct control/constraint paths.

## 4. Screwdriver grip, attachment and operation

1. Select the rig, enter **Pose Mode**, and select the right finger controls: the five `.01_master.R` controls plus `.01.R`, `.02.R`, `.03.R` for index, middle, ring, pinky and thumb. Selecting all control bones is also safe for these production hand assets, which only contain finger channels.
2. In Asset Browser choose **RepairRig → Hand Poses → Production**, select `POSE_Grip_Screwdriver_R_Production`, and use **Apply Pose** (right-click asset menu). This applies unkeyed values; key the finger controls if the pose must persist in a shot.
3. In RepairRig Tools click **Attach Screwdriver**. The pliers detach automatically.
4. With the right work reach fully engaged, `REF_ScrewdriverTip` should meet the work point.
5. Select **CONTACT_ScrewdriverRoll_R**, not the rig or tool mesh. Choose `TOOL_Screwdriver_CW_R` in Action Editor, with slot `OBCONTACT_ScrewdriverRoll_R`. Scrub **1, 17, 33, 37**. In a layered shot, put this clip on that object's NLA track; the demo starts it at frame 101.

The optional screw is not a physics simulator. The demo uses native, shot-local drivers on its Z rotation/translation to follow the work-roll object. Adapt screw response to your appliance; do not expect every screw model to move just because an Action is assigned to the rig.

## 5. Pliers and release

Apply `POSE_Grip_Pliers_R_Production` through Asset Browser; click **Attach Pliers**. The existing tool selector enables the pliers-specific work offset. At full work reach, `REF_PliersContact` meets the same working target. Do not move the socket or share the screwdriver tip length to repair alignment.

Click **Release Tool** to disable both attachments. This restores each root's parked transform, not a physical drop-in-place. See [Tool_Attachment_Workflow.md](Tool_Attachment_Workflow.md) for pickup/drop keys.

Save, close and reopen your project with trusted embedded scripts allowed. Confirm one character rig, both tool targets, the intended Action Slots and the UI. Library updates do not automatically overwrite appended local copies.

## Inspect the supplied demo

Open `Demo/RepairRig_NewProject_Validated.blend` and play frames **1–260**. Markers identify kneel, reach/attachment, screwdriver operation, release, pliers grip/alignment and release. Separate tracks hold body, right reach, left brace, hand poses and tool selection; the work-roll object has its own operation track. For manual button tests, mute **04 | Tool pickup / release (Constant)** first—scrubbing otherwise restores its authored selector keys.
