# Add another tool using the same architecture

The shipped UI supports two known tools. Adding a tool is an explicit authoring step, not automatic discovery/retargeting. Keep existing sockets, Actions and work alignment intact.

## Model, root and contact

1. Author a tool Collection with one local root Empty, geometry beneath it, sensible scale, and a defined grip-space origin/orientation. Use stable names such as `TOOL_NewTool` and `REF_NewToolContact`.
2. Define the functional point in tool-local coordinates: blade tip, jaw contact midpoint or socket center. Do not assume the object origin is the working end.
3. Add a character-side socket under `REF_Hand_R`, fitted with the appropriate production hand pose. Keep the wrist comfortable and check real skin clearance.
4. Add **one Child Of** to the tool root. Target the socket in the working project; calibrate its inverse so the attached root has the intended grip relationship. Do not add a second attachment constraint or reparent the root to switch ownership.
5. Define a tool-specific child offset in the work-target chain so its contact reaches the work point. Verify rotation and stroke behavior. Do not rewrite the shared `REACH_Forward_Low_R` just because the tool is shorter or longer.

For a new work location, move/orient the character's existing `TARGET_Screw`; its +Z is the working axis and the roll/grip/wrist chain follows it. Move brace/look targets separately where needed. For another simultaneous interaction, duplicate and name a complete target chain, add a deliberately named constraint on the appropriate hand, and author a compatible reach variant. Blindly renaming the existing constraint breaks its Action paths.

## Extend the selector and binding explicitly

In an authoring copy of the Character package's embedded `RepairRig_Library_UI.py`:

- Add the role/socket entry to `REPAIRRIG_OT_bind_library_tools`.
- Add a rig socket ID pointer and a tool-root `repairrig_asset_role` tag.
- Extend the selector property's UI range, the operator IntProperty range, its value-to-role lookup, and the panel's button list. The existing 1/2 ternary role lookup must become an explicit mapping when adding state 3.
- Give the new existing Child Of a mutually exclusive selector influence expression, and extend the work-offset driver expressions for the new state. Release remains state 0.
- Keep rig references out of the exported standalone tool file. Store native driver specifications as tool metadata if they need reconnecting on import, as the pliers jaw expression does.

The binder must refuse ambiguous candidates rather than silently connect a tool to the wrong character. Use stable ID pointers once bound, not absolute paths or development-script imports.

## Package and verify

Clear shot animation and cross-file rig references from the standalone tool source; leave its existing attachment disabled/unbound. Mark the complete tool Collection as an Asset under **RepairRig/Tools**, add description/contact conventions and a preview, then save a dedicated `.blend` under Tools. Pack any textures and remove unused authoring objects.

Append the updated Character and tool into a fresh project. Run the embedded UI, bind, attach, reach, operate and release. Verify no duplicate rigs/constraints, driver validity, hand clearance, contact alignment, save/reopen, and portability. Model-only linked geometry is an advanced option described in Asset_Library_Setup; interactive wrappers should remain local unless you explicitly validate overrides.

The current tool meshes and worksite are simple proxies. A detailed replacement model usually needs new contact and grip fitting even if the interface and Action names remain reusable.
