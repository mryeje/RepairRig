# Add Actions and Pose Assets

Author in a separate working project. Do not edit the shipped library or shared clips accidentally while animating a shot. Maintain backups and a fresh-file import test.

## Motion Action

1. Append the compatible Character Collection and any required tools; register UI and bind normally.
2. Select the correct owner: rig for body/reach/gesture/finger motion, work-roll helper for screwdriver rotation/withdrawal.
3. In **Dope Sheet → Action Editor**, create a new Action with a compatible OBJECT slot. Use `BODY_`, `REACH_`, `BRACE_`, `TOOL_`, or `GESTURE_` naming. Do not rename existing shared Actions to reuse them for a different purpose.
4. Key only the controls/properties owned by this layer. A reach should not key every body or finger control. Preserve the established constraint names and data paths.
5. Validate start, middle and end, plus NLA overlap with body, hand and tool-selector tracks. Ensure every F-curve resolves on the intended owner.
6. Right-click the Action datablock and choose **Mark as Asset** (or the datablock's Asset menu). In Asset Browser assign its catalog, description, owner/slot requirements, tags and useful preview. Preserve it with a Fake User if not assigned in the source scene.
7. Save into the appropriate library file or a clearly named new Actions file. Use standard File → Append to transfer the Action into an authoring copy of that source file; do not drag an entire character into a motion-only library file.
8. Test discovery and Append from a brand-new project before publishing the update. Appended projects retain local copies and do not auto-update.

The shipped motion files contain only Action data, not scene objects. A .blend data library can open as an empty scene; access its Actions through Action Editor/Blender File datablocks or Append. This is intentional.

## Static Pose Asset

1. Start from a known reset. Select only the controls the asset should own.
2. For production right-hand poses, select the five `.01_master.R` controls and each digit's `.01.R`, `.02.R`, `.03.R` FK controls. Avoid wrist/arm channels.
3. Fit the skin against the actual prop from palm, side and back views. Inspect pad contact, thumb base, adjacent fingers, handle crossings and joint folds—not only bone tips.
4. In Pose Mode use Blender's **Create Pose Asset** command (F3 search), or create a single-frame Action containing these channels and mark it as an Asset. Include explicit location, quaternion and scale resets where needed so switching poses clears the previous state.
5. Put generic reference poses in **Hand Poses/Canonical** and character-fitted variants in **Hand Poses/Production**, using a clear character suffix for additional characters. Do not label untested proxy poses as production-compatible.
6. Test native Apply Pose in an external Asset Browser, save/reopen, and combine it with reach and the correct tool selector. Pose application itself is unkeyed; insert finger keys into a separate shot Action for animation.

## NLA discipline

Separate tracks by channel ownership: body; right reach; left brace; fingers; tool selector. The work-roll helper has its own operation track. Use Replace for nonoverlapping channels. Use intentional blend-in/out or explicit release keys when tracks do overlap. Use Constant interpolation for the integer selector. Avoid an active Action silently overriding the NLA stack during tests.

Keep shot Actions such as tool switching sequences and screw results out of reusable asset catalogs. The demo's local copies are deliberately not asset-marked, avoiding duplicate search results from the Demo folder.
