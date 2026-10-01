"""Export curated native datablocks. Source blend is opened read-only, never saved."""
import bpy,json,hashlib,uuid,sys
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path('E:/RepairRig');OUT=ROOT/'tests/library';LIB=Path('E:/BlenderAssets/RepairRig')
SRC=ROOT/'blend/RepairRig_05F_ProductionCharacter_HandPolished.blend'
CATALOGS=['Character','Body Actions','Reach Actions','Tool Actions','Gestures','Hand Poses/Canonical','Hand Poses/Production','Tools','Interaction Helpers']
CATS={n:str(uuid.uuid5(uuid.NAMESPACE_URL,'RepairRig/6/'+n)) for n in CATALOGS}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def curves(a):return [f for l in a.layers for s in l.strips for sl in a.slots if (b:=s.channelbag(sl)) for f in b.fcurves]
def action_payload(a):return [(f.data_path,f.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in f.keyframe_points]) for f in curves(a)]
def mark(id,cat,desc):
 id.asset_mark();id.asset_data.catalog_id=CATS[cat];id.asset_data.description=desc;id.asset_data.author='RepairRig'
 for name in ['RepairRig','Stage 6',cat.split('/')[-1]]:
  if name not in id.asset_data.tags:id.asset_data.tags.new(name)
 id.use_fake_user=True
def strip_animation(o):
 if o.animation_data:
  o.animation_data.action=None
  for t in list(o.animation_data.nla_tracks):o.animation_data.nla_tracks.remove(t)
def save(path,ids):
 path=LIB/path
 if path.exists():
  assert '--refresh-generated' in sys.argv and str(path.relative_to(LIB)) in previous,'Refusing to overwrite '+str(path)
  assert sha(path)==previous[str(path.relative_to(LIB))]['sha256'],'Generated asset changed externally: '+str(path)
 bpy.data.libraries.write(str(path),set(ids),path_remap='RELATIVE',fake_user=True,compress=True)
 exports[str(path.relative_to(LIB))]={'bytes':path.stat().st_size,'sha256':sha(path)}
 print('EXPORTED',path,path.stat().st_size,flush=True)
def collection(name,objects,cat,desc):
 c=bpy.data.collections.new(name)
 for o in objects:c.objects.link(o)
 mark(c,cat,desc);return c
def open_source():bpy.ops.wm.open_mainfile(filepath=str(SRC),use_scripts=False);bpy.context.view_layer.update()
for n in ['Character','Actions','Poses','Tools','Demo','Docs']:(LIB/n).mkdir(exist_ok=True)
previous=json.loads((LIB/'Docs/Library_Manifest.json').read_text())['files'] if (LIB/'Docs/Library_Manifest.json').exists() else {}
source_hash=sha(SRC);exports={};manifest={'source_sha256':source_hash,'blender_version':bpy.app.version_string,'assets':[],'catalogs':CATS,'files':exports}
catalog='# This is an Asset Catalog Definition file for Blender.\nVERSION 1\n\n'+''.join(f'{CATS[n]}:RepairRig/{n}:{n.split("/")[-1]}\n' for n in CATALOGS)
(LIB/'blender_assets.cats.txt').write_text(catalog)
open_source();original_actions={a.name:action_payload(a) for a in bpy.data.actions}
# Export Actions independently: no character/scene owners are needed for channel data.
motion=[];canonical=[];production=[]
for a in bpy.data.actions:
 if a.name.startswith('BODY_'):cat='Body Actions';owner='RepairRig';motion.append(a)
 elif a.name.startswith(('REACH_','BRACE_')):cat='Reach Actions';owner='RepairRig';motion.append(a)
 elif a.name.startswith('GESTURE_'):cat='Gestures';owner='RepairRig';motion.append(a)
 elif a.name.startswith('TOOL_'):cat='Tool Actions';owner='CONTACT_ScrewdriverRoll_R' if 'Screwdriver' in a.name else 'RepairRig';motion.append(a)
 elif a.name.startswith('POSE_'):
  prod=a.name.endswith('_Production');cat='Hand Poses/Production' if prod else 'Hand Poses/Canonical';owner='RepairRig';(production if prod else canonical).append(a)
 else:continue
 desc=f'{a.name}. Apply to {owner}; frames {int(a.frame_range[0])}–{int(a.frame_range[1])}. Requires RepairRig/Rigify control schema, not automatic retargeting.'
 if cat.endswith('Production'):desc+=' Chris production-specific hand fit; includes 20 right-finger reset controls.'
 if cat.endswith('Canonical'):desc+=' Generic proxy master-curl reference; clear production FK offsets before use.'
 if a.name=='TOOL_Pliers_Squeeze_R':desc+=' Master-scale squeeze; not contact-fitted with extra production FK curls.'
 mark(a,cat,desc);a['repairrig_owner_role']=owner
 manifest['assets'].append({'name':a.name,'type':'Action','catalog':cat,'owner':owner,'range':list(a.frame_range)})
save(Path('Actions/RepairRig_Motion.blend'),motion)
save(Path('Poses/RepairRig_HandPoses_Canonical.blend'),canonical)
save(Path('Poses/RepairRig_HandPoses_Production.blend'),production)
assert all(action_payload(bpy.data.actions[n])==p for n,p in original_actions.items())
# Character owns fitted sockets and interaction targets. Tool models never own the rig.
r=bpy.data.objects['RepairRig'];m=bpy.data.objects['Chris-Low-poly']
for o in bpy.data.objects:strip_animation(o)
for p in r.pose.bones:p.matrix_basis=Matrix.Identity(4)
for fc in curves(bpy.data.actions['BODY_Idle_Standing']):
 try:r.path_resolve(fc.data_path)[fc.array_index]=fc.evaluate(1)
 except (TypeError,AttributeError):pass
for p in r.pose.bones:
 for c in p.constraints:
  if c.name.startswith(('Pickup |','Reach |','Work |','Brace |','Look |')):c.influence=0
r['repairrig_tool']=0;r['RepairRig_library_version']='6.0'
r['README']='Select this rig. Text Editor: run RepairRig_Library_UI.py once after append. Read the library Docs folder. Append complete Character Collection, not individual objects.'
ui=bpy.data.texts.new('RepairRig_Library_UI.py');ui.write((ROOT/'scripts/repairrig_library_ui.py').read_text());ui.use_module=True
r['repairrig_library_ui']=ui
for key,name in [('repairrig_socket_screwdriver','ATTACH_Screwdriver_R'),('repairrig_socket_pliers','ATTACH_Pliers_R'),('repairrig_work_target','TARGET_Screw'),('repairrig_work_roll','CONTACT_ScrewdriverRoll_R')]:r[key]=bpy.data.objects[name]
names=['RepairRig','Chris-Low-poly','REF_Hand_R','ATTACH_Screwdriver_R','ATTACH_Pliers_R','CONTACT_PickupWrist_R','CONTACT_ScrewdriverRoll_R','CONTACT_WorkGrip_R','CONTACT_WorkWrist_R','CONTACT_ToolWorkOffset_R','TARGET_Screw','TARGET_ToolGrip','TARGET_Brace_L','TARGET_Look','TARGET_Reach_Mid_R','TARGET_Reach_Low_L']
character=collection('RepairRig_Character_Production',[bpy.data.objects[n] for n in names],'Character','Validated Stage 5F Chris character + Rigify controls, sockets, work targets and embedded UI. Append this Collection at origin. Tools are separate assets; run embedded UI once, then Bind Imported Tools. Character-specific hand fit.')
widgets=bpy.data.collections.new('RepairRig_ControlWidgets');character.children.link(widgets);widgets.hide_render=True
for p in r.pose.bones:
 if p.custom_shape and p.custom_shape.name not in widgets.objects:widgets.objects.link(p.custom_shape)
for o in character.all_objects:
 if o!=r and o!=m and o.type=='EMPTY':o.empty_display_size=min(o.empty_display_size,.08)
# Avoid accidentally importing a metarig through generated-rig metadata.
for owner in [r,r.data]:
 for key in list(owner.keys()):
  val=owner[key]
  if isinstance(val,bpy.types.Object) and val.name not in names and not val.name.startswith('WGT-'):del owner[key]
bpy.context.view_layer.update()
save(Path('Character/RepairRig_Production.blend'),[character])
manifest['assets'].append({'name':character.name,'type':'Collection','catalog':'Character','file':'Character/RepairRig_Production.blend'})
# Export tools after severing only cross-asset references; preserve stored inverse and geometry.
for role,name,file in [('screwdriver','TOOL_Screwdriver','RepairRig_Screwdriver.blend'),('pliers','TOOL_Pliers','RepairRig_Pliers.blend')]:
 root=bpy.data.objects[name];parts=[root]+list(root.children_recursive)
 for o in parts:
  if o.animation_data:
   for fc in list(o.animation_data.drivers):
    if o!=root and fc.data_path=='rotation_euler':o['repairrig_jaw_expression']=fc.driver.expression
    o.driver_remove(fc.data_path,fc.array_index)
  strip_animation(o)
 for c in root.constraints:
  if c.type=='CHILD_OF':c.target=None;c.influence=0
 root['repairrig_asset_role']=role;root['repairrig_library_version']='6.0'
 for o in parts:
  if o.get('repairrig_jaw_expression'):o.rotation_euler.y=-.18 if o.name.endswith('-1') else .18
 c=collection('RepairRig_Tool_'+role.title(),parts,'Tools',f'Append interactive {role} with calibrated contact reference. No rig dependency. Select imported character and Bind Imported Tools; uses one existing Child Of. Keep authored root transform until bound.')
 save(Path('Tools')/file,[c]);manifest['assets'].append({'name':c.name,'type':'Collection','catalog':'Tools','file':'Tools/'+file})
# Optional simple worksite, detached from the character and all shot animation.
scene_names=['APPLIANCE_Washer_Proxy','APPLIANCE_LowerServicePanel','APPLIANCE_ControlPanel','APPLIANCE_Door','APPLIANCE_DoorGlass','GROUND','KNEEL_Pad_L','SCREW_Visible','SCREW_Slot','SCREW_Slot_Cross','TOOL_RestStand']
screw=bpy.data.objects['SCREW_Visible'];local=screw.matrix_local.copy();world=screw.matrix_world.copy();screw.parent=None;screw.matrix_world=world;screw['repairrig_screw_local']=[x for row in local for x in row];screw['repairrig_asset_role']='work_screw'
work=collection('RepairRig_Worksite_Demo',[bpy.data.objects[n] for n in scene_names],'Interaction Helpers','Optional appliance/screw proxy. Append at origin, select character, Connect Demo Worksite. Move character TARGET_Screw to adapt a new repair location. No baked shot animation.')
save(Path('Tools/RepairRig_Worksite.blend'),[work]);manifest['assets'].append({'name':work.name,'type':'Collection','catalog':'Interaction Helpers','file':'Tools/RepairRig_Worksite.blend'})
assert sha(SRC)==source_hash
(OUT/'source_action_payloads.json').write_text(json.dumps(original_actions,indent=2))
(LIB/'Docs/Library_Manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'build_manifest.json').write_text(json.dumps(manifest,indent=2))
print('LIBRARY_EXPORT_COMPLETE',len(manifest['assets']),'assets',flush=True)
