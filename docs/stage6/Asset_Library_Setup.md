# RepairRig Asset Library setup

Tested with **Blender 5.0.1**. Use this version or test a newer version before production. Files use slotted Actions; older Blender versions are not certified.

## Register the library

1. Open Blender normally.
2. Choose **Edit → Preferences → File Paths**.
3. Find **Asset Libraries** and click **+**.
4. Select **E:\BlenderAssets\RepairRig\** and confirm **Add Asset Library**.
5. Name it **RepairRig**. If Auto-Save Preferences is disabled, choose **Save Preferences** from the Preferences menu.
6. Change an editor's type to **Asset Browser**. In its library dropdown, choose **RepairRig**.
7. Expand the **RepairRig** catalog tree. Use the refresh button/menu if the files were added while Blender was running.

The build/test sessions did not overwrite your saved preferences; perform these steps in your normal Blender profile.

## Contents and ownership

| File | Assets / responsibility |
| --- | --- |
| `Character/RepairRig_Production.blend` | One production Character Collection: low-poly production mesh, generated Rigify rig/widgets, fitted hand sockets, work/pickup/brace/look targets, embedded UI |
| `Actions/RepairRig_Motion.blend` | 6 BODY, 4 REACH/BRACE, 3 TOOL, 2 GESTURE Actions |
| `Poses/RepairRig_HandPoses_Canonical.blend` | Six generic proxy hand-pose references |
| `Poses/RepairRig_HandPoses_Production.blend` | Six Chris production-specific hand poses, including Stage 5F refinements |
| `Tools/RepairRig_Screwdriver.blend` | Independent screwdriver Collection and tip reference |
| `Tools/RepairRig_Pliers.blend` | Independent pliers Collection, jaw helpers and contact reference |
| `Tools/RepairRig_Worksite.blend` | Optional appliance/screw proxy Collection |
| `Demo/RepairRig_NewProject_Validated.blend` | Independent appended project, with layered animation and timeline markers |

There are **31 cataloged assets**, with 256×256 rendered previews. Catalogs: Character; Body Actions; Reach Actions; Tool Actions; Gestures; Hand Poses/Canonical; Hand Poses/Production; Tools; Interaction Helpers. Keep the root `blender_assets.cats.txt` with the library.

The fitted attachment sockets deliberately belong to the character package, not to each tool file. This prevents appending a tool from importing a second rig. Tool-local tip/jaw references travel with the tool. Bind the two sides once after Append.

## Append versus Link

- **Append the Character Collection** for ordinary projects. It is local and editable. Do not append individual rig/mesh/helper objects separately.
- **Append Actions** when local timing or curve edits are expected. Make a single-user copy before changing shared shot usage.
- **Apply Pose Assets through Asset Browser**; application sets a pose, not an animated timeline clip.
- **Append interactive tools** for the tested automatic binding/UI workflow.
- **Link tool models** when central geometry updates are required. A fully linked tool Collection is read-only; the binder intentionally rejects it. For advanced use, keep the appended local tool wrappers/constraints and replace their mesh data with linked mesh datablocks through **File → Link → tool .blend → Mesh**, then the mesh datablock selector in Object Data Properties. This preserves local attachment ownership while geometry remains linked. Verify transforms, materials, contact offsets and deformation after each model update. This advanced linked-geometry variant is not the validated default.

## Trusted embedded scripts

Appending a Collection does not execute its Text blocks. After importing, select `RepairRig`; change an editor to **Text Editor**, choose **RepairRig_Library_UI.py**, and press **Run Script** (Alt-P). This registers both RepairRig Tools and the included standard generated Rigify UI. No add-on installation, development folder, external Python package or network access is needed.

On reopening a saved project, allow execution of these trusted embedded scripts in Blender's file-open security options/prompt. Do not globally trust arbitrary downloaded .blend files. If execution is disabled, run the embedded text manually again. Standard constraints and animation remain native Blender data; the script supplies buttons and one-time binding.

Read [New_Repair_Project_Workflow.md](New_Repair_Project_Workflow.md) next. The library files are not an installer and do not alter startup files.
