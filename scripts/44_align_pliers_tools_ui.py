"""Build Stage 5E without changing existing Actions, sockets, or hand pose."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path('E:/RepairRig')
SRC = ROOT/'blend/RepairRig_05D_ProductionCharacter_PliersAttach.blend'
DST = ROOT/'blend/RepairRig_05E_ProductionCharacter_PliersAligned.blend'
CAN = ROOT/'blend/RepairRig_04_ActionLibrary.blend'
OUT = ROOT/'tests/pliers_aligned'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def mat(m): return [list(row) for row in m]
def curves(a):
    return [fc for l in a.layers for s in l.strips for sl in a.slots if (b := s.channelbag(sl)) for fc in b.fcurves]
def actions():
    return {a.name:[(f.data_path,f.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in f.keyframe_points]) for f in curves(a)] for a in bpy.data.actions}
def update():
    bpy.data.objects['RepairRig'].update_tag()
    bpy.context.view_layer.update()
def world(o): return o.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.copy()
def geometry():
    return {o.name: {'vertices':[list(v.co) for v in o.data.vertices], 'weights':[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices]} for o in bpy.data.objects if o.type == 'MESH'}
def driver(owner, path, expression, rig, index=None):
    fc = owner.driver_add(path) if index is None else owner.driver_add(path,index)
    d = fc.driver; d.type = 'SCRIPTED'
    v = d.variables.new(); v.name = 'tool'; v.type = 'SINGLE_PROP'
    v.targets[0].id = rig; v.targets[0].data_path = '["repairrig_tool"]'
    d.expression = expression

assert not DST.exists(), 'Refusing to overwrite checkpoint'
hashes = {str(p):sha(p) for p in (SRC,CAN)}
bpy.ops.wm.open_mainfile(filepath=str(SRC),use_scripts=False)
update()
r = bpy.data.objects['RepairRig']
baseline = actions()
rest = {b.name:mat(b.matrix_local) for b in r.data.bones}
mesh = geometry()
pose = {b.name:mat(b.matrix_basis) for b in r.pose.bones}
socket = {n:mat(bpy.data.objects[n].matrix_basis) for n in ('ATTACH_Pliers_R','ATTACH_Screwdriver_R')}
oldwork = bpy.data.objects['CONTACT_WorkWrist_R']
oldwork_world = world(oldwork)
tips = [world(bpy.data.objects['Pliers_Jaw_'+str(i)]) @ Vector((0,0,.5)) for i in (-1,1)]
mid = (tips[0]+tips[1])/2
local_contact = world(bpy.data.objects['TOOL_Pliers']).inverted() @ mid
target = world(bpy.data.objects['TARGET_Screw']).translation
delta = oldwork_world.to_3x3().inverted() @ (target-mid)
sd = bpy.data.objects['TOOL_Screwdriver']; pl = bpy.data.objects['TOOL_Pliers']
sc = sd.constraints['Attach / release | right hand socket']; pc = pl.constraints['Attach / release | pliers right socket']
pc.influence = 0; sc.influence = 1; update()
sd_baseline = mat(world(sd))
sc.influence = 0; pc.influence = 1; update()
r['repairrig_tool'] = 2
r.id_properties_ui('repairrig_tool').update(min=0,max=2,description='0=None, 1=Screwdriver, 2=Pliers. Key in a separate shot Action using Constant interpolation.')
driver(sc,'influence','1.0 if tool == 1 else 0.0',r)
driver(pc,'influence','1.0 if tool == 2 else 0.0',r)
ref = bpy.data.objects.new('REF_PliersContact',None)
pl.users_collection[0].objects.link(ref); ref.parent = pl; ref.location = local_contact
ref.empty_display_type = 'SPHERE'; ref.empty_display_size = .008
ref['purpose'] = 'Distal jaw midpoint calibrated to POSE_Grip_Pliers_R_Production; not a physical jaw simulation.'
offset = bpy.data.objects.new('CONTACT_ToolWorkOffset_R',None)
oldwork.users_collection[0].objects.link(offset); offset.parent = oldwork
offset.empty_display_type = 'ARROWS'; offset.empty_display_size = .04
for i in range(3): driver(offset,'location',f'{delta[i]!r} if tool == 2 else 0.0',r,i)
r.pose.bones['hand_ik.R'].constraints['Work | TARGET_Screw'].target = offset
text = bpy.data.texts.new('RepairRig_Tools_UI.py')
text.write((ROOT/'scripts/repairrig_tools_ui.py').read_text()); text.use_module = True
exec(compile(text.as_string(),text.name,'exec'),{'__name__':'__main__'})
update()
assert actions() == baseline
assert geometry() == mesh
assert {b.name:mat(b.matrix_basis) for b in r.pose.bones} == pose
assert (world(ref).translation-target).length < 1e-5
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(DST))
(OUT/'build.json').write_text(json.dumps({'source_hashes':hashes,'original_gap':(mid-target).length,'offset_local':list(delta),'pliers_contact_local':list(local_contact),'original_work_world':mat(oldwork_world),'screwdriver_attached_world':sd_baseline,'actions':baseline,'rest':rest,'sockets':socket,'output':str(DST)},indent=2))
print('STAGE5E_SAVED',str(DST),'offset',list(delta),flush=True)
