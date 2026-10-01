"""RepairRig library support. Embedded, self-contained, Blender-only.

Run once after appending a character; allow trusted scripts when reopening.
No handlers, filesystem access, downloads, or changes to user preferences.
"""
import bpy
from bpy.props import IntProperty
from mathutils import Matrix


def active_rig(context):
    obj = context.object
    if obj and obj.type == 'ARMATURE' and obj.get('RepairRig_library_version'):
        return obj
    if obj:
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object and mod.object.get('RepairRig_library_version'):
                return mod.object
        owner = obj.get('repairrig_owner')
        if isinstance(owner, bpy.types.Object):
            return owner
    rigs = [o for o in context.scene.objects if o.type == 'ARMATURE' and o.get('RepairRig_library_version')]
    return rigs[0] if len(rigs) == 1 else None


def selector_driver(owner, path, rig, value):
    fc = owner.driver_add(path)
    d = fc.driver
    while d.variables:
        d.variables.remove(d.variables[0])
    d.type = 'SCRIPTED'
    var = d.variables.new(); var.name = 'tool'; var.type = 'SINGLE_PROP'
    var.targets[0].id = rig; var.targets[0].data_path = '["repairrig_tool"]'
    d.expression = f'1.0 if tool == {value} else 0.0'


class REPAIRRIG_OT_bind_library_tools(bpy.types.Operator):
    bl_idname = 'repairrig.bind_library_tools'
    bl_label = 'Bind Imported Tools'
    bl_description = 'Connect unbound local tool assets to this rig; does not reparent tools or duplicate Child Of constraints'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = active_rig(context)
        if not rig or rig.library:
            self.report({'ERROR'}, 'Select an appended/local RepairRig character')
            return {'CANCELLED'}
        roles = (('screwdriver', 1, 'repairrig_socket_screwdriver'), ('pliers', 2, 'repairrig_socket_pliers'))
        pending = []
        for role, value, socket_key in roles:
            candidates = [o for o in context.scene.objects if o.get('repairrig_asset_role') == role and o.get('repairrig_owner') in (None, rig)]
            if len(candidates) > 1:
                self.report({'ERROR'}, f'Multiple {role} assets: remove the duplicate or use one tool of each type per rig')
                return {'CANCELLED'}
            if not candidates:
                continue
            obj = candidates[0]
            if obj.library or obj.override_library:
                self.report({'ERROR'}, 'Append interactive tool objects; linked model-only use is documented separately')
                return {'CANCELLED'}
            child = [c for c in obj.constraints if c.type == 'CHILD_OF']
            if len(child) != 1 or not rig.get(socket_key):
                self.report({'ERROR'}, f'{role}: expected exactly one existing Child Of and a rig socket')
                return {'CANCELLED'}
            pending.append((obj, child[0], rig[socket_key], value, role))
        if not pending:
            self.report({'ERROR'}, 'Append a RepairRig screwdriver or pliers Collection asset first')
            return {'CANCELLED'}
        for obj, constraint, socket, value, role in pending:
            constraint.target = socket
            # A collection appended at its authored origin retains the calibrated inverse.
            selector_driver(constraint, 'influence', rig, value)
            obj['repairrig_owner'] = rig
            rig['repairrig_bound_' + role] = obj
            if role == 'pliers':
                for part in obj.children_recursive:
                    if part.get('repairrig_jaw_expression'):
                        fc = part.driver_add('rotation_euler', 1)
                        d = fc.driver
                        while d.variables:
                            d.variables.remove(d.variables[0])
                        d.type = 'SCRIPTED'; d.expression = part['repairrig_jaw_expression']
                        var = d.variables.new(); var.name = 'grip'; var.type = 'SINGLE_PROP'
                        var.targets[0].id = rig
                        var.targets[0].data_path = 'pose.bones["f_index.01_master.R"].scale[1]'
                        part.update_tag()
        rig.update_tag(); context.view_layer.update()
        self.report({'INFO'}, 'Tool sockets connected; use Attach / Release. Apply a hand pose separately.')
        return {'FINISHED'}


class REPAIRRIG_OT_bind_worksite(bpy.types.Operator):
    bl_idname = 'repairrig.bind_worksite'
    bl_label = 'Connect Demo Worksite'
    bl_description = 'Connect the optional worksite screw to this character work target'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rig = active_rig(context)
        screws = [o for o in context.scene.objects if o.get('repairrig_asset_role') == 'work_screw']
        if not rig or len(screws) != 1 or screws[0].library:
            self.report({'ERROR'}, 'Append one optional Worksite asset and select the local RepairRig')
            return {'CANCELLED'}
        screw = screws[0]
        screw.parent = rig['repairrig_work_target']
        screw.matrix_parent_inverse = Matrix.Identity(4)
        screw.matrix_basis = Matrix([list(screw['repairrig_screw_local'])[i:i+4] for i in range(0,16,4)])
        screw['repairrig_owner'] = rig
        context.view_layer.update()
        return {'FINISHED'}


class REPAIRRIG_OT_select_tool(bpy.types.Operator):
    bl_idname = 'repairrig.select_tool'
    bl_label = 'Select RepairRig Tool'
    bl_options = {'REGISTER', 'UNDO'}
    tool: IntProperty(default=0, min=0, max=2)

    def execute(self, context):
        rig = active_rig(context)
        if not rig or rig.library:
            return {'CANCELLED'}
        if self.tool and not rig.get('repairrig_bound_' + ('screwdriver' if self.tool == 1 else 'pliers')):
            self.report({'ERROR'}, 'Use Bind Imported Tools first')
            return {'CANCELLED'}
        rig['repairrig_tool'] = self.tool
        rig.update_tag(); context.view_layer.update()
        return {'FINISHED'}


class REPAIRRIG_PT_tools(bpy.types.Panel):
    bl_label = 'RepairRig Tools'
    bl_idname = 'REPAIRRIG_PT_tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RepairRig'

    @classmethod
    def poll(cls, context):
        return active_rig(context) is not None

    def draw(self, context):
        layout = self.layout; rig = active_rig(context)
        layout.label(text='Character: ' + rig.name)
        layout.operator('repairrig.bind_library_tools')
        state = int(rig['repairrig_tool'])
        for value, label in ((1, 'Attach Screwdriver'), (2, 'Attach Pliers'), (0, 'Release Tool')):
            layout.operator('repairrig.select_tool', text=label, depress=state == value).tool = value
        layout.prop(rig, '["repairrig_tool"]', text='Tool (0 / 1 / 2)')
        layout.label(text='Hand pose is unchanged.')
        layout.label(text='Key Tool in a separate shot Action.')
        layout.label(text='Use Constant interpolation.')
        layout.separator()
        layout.operator('repairrig.bind_worksite')


def register():
    classes = (REPAIRRIG_OT_bind_library_tools, REPAIRRIG_OT_bind_worksite, REPAIRRIG_OT_select_tool, REPAIRRIG_PT_tools)
    for cls in reversed(classes):
        old = getattr(bpy.types, cls.__name__, None)
        if old:
            bpy.utils.unregister_class(old)
    for cls in classes:
        bpy.utils.register_class(cls)


register()

# Standard generated Rigify UI is retained as a Text dependency of the rig.
# Appending never auto-runs Text blocks, so this trusted one-time registration
# also brings up the familiar Rigify controls in the new project.
_rig = active_rig(bpy.context)
if _rig:
    _text = _rig.get('rig_ui')
    if isinstance(_text, bpy.types.Text):
        exec(compile(_text.as_string(), _text.name, 'exec'), {'__name__': '__main__'})
