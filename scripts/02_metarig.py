"""Milestone A: standard human metarig with deliberately small face."""
import bpy, addon_utils, json
from pathlib import Path
from mathutils import Vector, Quaternion
ROOT = Path('E:/RepairRig')
assert bpy.app.version == (5,0,1), bpy.app.version_string
assert not bpy.app.background
assert not bpy.data.filepath, 'Start this milestone in a new scene.'
addon_utils.enable('rigify', default_set=True, persistent=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.armature_human_metarig_add()
meta = bpy.context.object
meta.name = 'RepairRig_Metarig'
meta.data.name = 'RepairRig_Metarig_v1'
face = meta.data.bones['face']
remove = [face.name] + [b.name for b in face.children_recursive]
bpy.ops.object.mode_set(mode='EDIT')
for name in remove:
    meta.data.edit_bones.remove(meta.data.edit_bones[name])
head = meta.data.edit_bones['spine.006']
z = head.head.z
specs = {'jaw': ((0,-.045,z+.025),(0,-.095,z+.005)),
         'eye.L': ((.035,-.075,z+.115),(.035,-.12,z+.115)),
         'eye.R': ((-.035,-.075,z+.115),(-.035,-.12,z+.115)),
         'lid.L': ((.035,-.084,z+.13),(.035,-.11,z+.13)),
         'lid.R': ((-.035,-.084,z+.13),(-.035,-.11,z+.13)),
         'mouth_corner.L': ((.03,-.09,z+.045),(.03,-.115,z+.045)),
         'mouth_corner.R': ((-.03,-.09,z+.045),(-.03,-.115,z+.045)),
         'brow.L': ((.035,-.078,z+.155),(.035,-.105,z+.155)),
         'brow.R': ((-.035,-.078,z+.155),(-.035,-.105,z+.155))}
for name,(h,t) in specs.items():
    b = meta.data.edit_bones.new(name)
    b.head, b.tail, b.parent = h,t,head
bpy.ops.object.mode_set(mode='OBJECT')
coll = meta.data.collections.new('Simple Face')
coll.rigify_ui_row = 8
for name in specs:
    p = meta.pose.bones[name]
    p.rigify_type = 'basic.super_copy'
    p.rigify_parameters.make_control = True
    p.rigify_parameters.make_deform = True
    coll.assign(p.bone)
meta['RepairRig_schema'] = '1.0 — stock human body/hands; minimal super_copy face'
meta.show_in_front = True
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.render.fps = 24
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces.active.region_3d.view_distance = 3.3
        area.spaces.active.region_3d.view_location = Vector((0,0,1))
        area.spaces.active.region_3d.view_rotation = Quaternion((.7071,.7071,0,0))
out = ROOT/'blend/RepairRig_01_RigifySetup.blend'
assert not out.exists(), 'Preserve existing checkpoint'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(ROOT/'tests/metarig.json').write_text(json.dumps({'bones':len(meta.data.bones),'face_controls':list(specs)},indent=2))
