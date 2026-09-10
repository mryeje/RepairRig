"""Milestone B: generate stock Rigify and inventory actual control names."""
import bpy, json
from pathlib import Path
ROOT=Path('E:/RepairRig')
meta=bpy.data.objects['RepairRig_Metarig']
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
meta.hide_set(False)
meta.select_set(True)
bpy.context.view_layer.objects.active=meta
bpy.ops.pose.rigify_generate()
rig=bpy.context.object
assert rig != meta and 'root' in rig.pose.bones
rig.name='RepairRig'
rig.show_in_front=True
rig['RepairRig_schema']='1.0'
meta.hide_set(True)
report={'rig':rig.name,'collections':[{'name':c.name,'visible':c.is_visible} for c in rig.data.collections_all],
        'bones':[{'name':p.name,'deform':p.bone.use_deform,'head':list(p.bone.head_local),'tail':list(p.bone.tail_local),
                  'properties':{k:str(p[k]) for k in p.keys()},'rotation_mode':p.rotation_mode} for p in rig.pose.bones]}
(ROOT/'tests/generated_rig.json').write_text(json.dumps(report,indent=2))
out=ROOT/'blend/RepairRig_02a_Generated.blend'
assert not out.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(out))
