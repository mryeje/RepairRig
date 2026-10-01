"""Self-contained Stage 5E UI. Embedded in the blend; no add-on dependencies."""
import bpy
from bpy.props import IntProperty


class REPAIRRIG_OT_select_tool(bpy.types.Operator):
    bl_idname = 'repairrig.select_tool'
    bl_label = 'Select RepairRig Tool'
    bl_options = {'REGISTER', 'UNDO'}
    tool: IntProperty(default=0, min=0, max=2)

    def execute(self, context):
        rig = bpy.data.objects.get('RepairRig')
        if rig is None or 'repairrig_tool' not in rig:
            return {'CANCELLED'}
        rig['repairrig_tool'] = self.tool
        rig.update_tag()
        context.view_layer.update()
        return {'FINISHED'}


class REPAIRRIG_PT_tools(bpy.types.Panel):
    bl_label = 'RepairRig Tools'
    bl_idname = 'REPAIRRIG_PT_tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RepairRig'

    @classmethod
    def poll(cls, context):
        r = bpy.data.objects.get('RepairRig')
        return r is not None and 'repairrig_tool' in r

    def draw(self, context):
        layout = self.layout
        rig = bpy.data.objects['RepairRig']
        state = int(rig['repairrig_tool'])
        for value, label in ((1, 'Attach Screwdriver'), (2, 'Attach Pliers'), (0, 'Release Tool')):
            layout.operator('repairrig.select_tool', text=label, depress=state == value).tool = value
        layout.prop(rig, '["repairrig_tool"]', text='Tool (0/1/2)')
        layout.label(text='Hand pose is unchanged.')
        layout.label(text='Key Tool in a separate shot Action.')
        layout.label(text='Use Constant key interpolation.')


def register():
    classes = (REPAIRRIG_OT_select_tool, REPAIRRIG_PT_tools)
    for cls in reversed(classes):
        old = getattr(bpy.types, cls.__name__, None)
        if old:
            bpy.utils.unregister_class(old)
    for cls in classes:
        bpy.utils.register_class(cls)


register()
