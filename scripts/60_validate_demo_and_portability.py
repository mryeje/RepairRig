"""Saved-demo playback, native UI, package dependency and path audit."""
import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
LIB=Path('E:/BlenderAssets/RepairRig');OUT=Path('E:/RepairRig/tests/library');DEMO=LIB/'Demo/RepairRig_NewProject_Validated.blend'
manifest=json.loads((LIB/'Docs/Library_Manifest.json').read_text());source_actions=json.loads((OUT/'source_action_payloads.json').read_text());report={'packages':{}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mat(m):return [list(row) for row in m]
def curves(a):return [f for l in a.layers for s in l.strips for sl in a.slots if (b:=s.channelbag(sl)) for f in b.fcurves]
def payload(a):return [[f.data_path,f.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation] for k in f.keyframe_points]] for f in curves(a)]
def all_ids():
 for prop in bpy.data.bl_rna.properties:
  if prop.type=='COLLECTION':
   for id in getattr(bpy.data,prop.identifier):
    if isinstance(id,bpy.types.ID):yield id
def audit():
 ids=list(all_ids());strings=[];external=[]
 def walk(value,label):
  if isinstance(value,str):
   if 'e:/repairrig/' in value.replace('\\','/').lower():strings.append(label)
  elif hasattr(value,'items') and not isinstance(value,bpy.types.ID):
   for k,v in value.items():walk(v,label+'.'+str(k))
 for id in ids:
  for key,value in id.items():walk(value,id.name+'['+key+']')
  if id.library:external.append([id.name,id.library.filepath])
 for text in bpy.data.texts:
  walk(text.as_string(),'Text:'+text.name);walk(text.filepath,'Text.filepath:'+text.name)
 images=[{'name':i.name,'filepath':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source!='VIEWER']
 missing=[i['name'] for i in images if not i['packed'] and i['filepath'] and not Path(bpy.path.abspath(i['filepath'])).exists()]
 resource_paths=list(bpy.utils.blend_paths(absolute=False,packed=False)) if hasattr(bpy.utils,'blend_paths') else list(bpy.utils.blend_paths())
 for p in resource_paths:walk(p,'resource:'+p)
 return {'development_path_hits':strings,'linked_ids':external,'images':images,'missing_external_images':missing,'resource_paths':resource_paths,'texts':[t.name for t in bpy.data.texts],'objects':len(bpy.data.objects),'armatures':[o.name for o in bpy.data.objects if o.type=='ARMATURE']}
def fingerprint():
 m=bpy.data.objects['Chris-Low-poly'];h=hashlib.sha256()
 for v in m.data.vertices:
  h.update(struct.pack('3f',*v.co))
  for g in v.groups:h.update(struct.pack('If',g.group,g.weight))
 for p in m.data.polygons:h.update(struct.pack(str(len(p.vertices))+'I',*p.vertices))
 r=bpy.data.objects['RepairRig'];return {'mesh':h.hexdigest(),'rest':{b.name:mat(b.matrix_local) for b in r.data.bones}}
for relative in manifest['files']:
 p=LIB/relative;bpy.ops.wm.open_mainfile(filepath=str(p),use_scripts=False)
 row=audit();row['assets']=[{'name':id.name,'catalog':id.asset_data.catalog_id,'preview_size':list(id.preview.image_size) if id.preview else None} for id in all_ids() if id.asset_data]
 row['action_payloads_preserved']=all(a.name in source_actions and payload(a)==source_actions[a.name] for a in bpy.data.actions)
 row['sha256']=sha(p);report['packages'][relative]=row
 print('PACKAGE_ASSETS',relative,row['assets'],flush=True)
 (OUT/'audit_progress.json').write_text(json.dumps(report,indent=2))
 if relative.replace('\\','/').startswith('Character/'):character_fingerprint=fingerprint()
 assert not row['development_path_hits'] and not row['linked_ids'] and not row['missing_external_images'],row
 assert row['action_payloads_preserved'],relative
 assert all(a['preview_size'] and a['preview_size'][0]>0 for a in row['assets']),relative
 assert len(bpy.data.objects)==0 if relative.replace('\\','/').startswith(('Actions/','Poses/')) else True
# Source is read only for preservation comparison, never for constructing the new project.
SRC=Path('E:/RepairRig/blend/RepairRig_05F_ProductionCharacter_HandPolished.blend')
assert sha(SRC)==manifest['source_sha256'];bpy.ops.wm.open_mainfile(filepath=str(SRC),use_scripts=False);report['character_mesh_weights_rest_unchanged']=fingerprint()==character_fingerprint;assert report['character_mesh_weights_rest_unchanged']
before=sha(DEMO);bpy.ops.wm.open_mainfile(filepath=str(DEMO),use_scripts=True)
r=bpy.data.objects['RepairRig'];s=bpy.context.scene;report['demo_audit']=audit();report['demo_samples']={}
assert hasattr(bpy.types,'REPAIRRIG_PT_tools')
def update():r.update_tag();bpy.context.view_layer.update()
for f in [1,49,65,97,101,117,133,137,149,180,181,201,240,241,260]:
 s.frame_set(f);update();state=int(r['repairrig_tool']);ref='REF_ScrewdriverTip' if state==1 else 'REF_PliersContact'
 row={'tool':state,'influences':[bpy.data.objects[n].constraints[0].influence for n in ('TOOL_Screwdriver','TOOL_Pliers')],'work_influence':r.pose.bones['hand_ik.R'].constraints['Work | TARGET_Screw'].influence,'contact_gap':(bpy.data.objects[ref].matrix_world.translation-bpy.data.objects['CONTACT_ScrewdriverRoll_R'].matrix_world.translation).length,'screw_rotation_z':bpy.data.objects['SCREW_Visible'].rotation_euler.z,'roll_rotation_z':bpy.data.objects['CONTACT_ScrewdriverRoll_R'].rotation_euler.z,'screw_world':mat(bpy.data.objects['SCREW_Visible'].matrix_world),'wrist_world':mat(r.matrix_world@r.pose.bones['hand_ik.R'].matrix),'torso_location':list(r.pose.bones['torso'].location)}
 assert row['influences']==([1.,0.] if state==1 else [0.,1.] if state==2 else [0.,0.]),row
 if f in [97,101,117,133,137,181,201,240]:assert row['contact_gap']<1e-5,row
 report['demo_samples'][str(f)]=row
assert report['demo_samples']['1']['torso_location']!=report['demo_samples']['49']['torso_location']
assert abs(report['demo_samples']['101']['screw_rotation_z']-report['demo_samples']['117']['screw_rotation_z'])>.1
report['invalid_drivers']=[(o.name,f.data_path) for o in bpy.data.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid];assert not report['invalid_drivers']
# Manual UI is tested with the shot's selector track muted; no data is saved.
track=next(t for t in r.animation_data.nla_tracks if 'Tool pickup' in t.name);track.mute=True;bpy.context.view_layer.objects.active=r
report['ui']={}
for value in [0,1,2,0]:
 assert bpy.ops.repairrig.select_tool(tool=value)=={'FINISHED'};update();report['ui'][str(value)]=[bpy.data.objects[n].constraints[0].influence for n in ('TOOL_Screwdriver','TOOL_Pliers')]
assert report['ui']=={'0':[0.,0.],'1':[1.,0.],'2':[0.,1.]}
track.mute=False;s.frame_set(117);update()
for f,label in [(117,'Demo_Screwdriver'),(201,'Demo_Pliers')]:
 s.frame_set(f);s.render.filepath=str(LIB/'Demo'/label)+'.png';bpy.ops.render.render(write_still=True)
assert not report['demo_audit']['development_path_hits'] and not report['demo_audit']['linked_ids'] and not report['demo_audit']['missing_external_images']
assert sha(DEMO)==before;report['demo_sha256']=before;report['source_unchanged']=sha(SRC)==manifest['source_sha256'];report['pass']=True
(OUT/'final_validation.json').write_text(json.dumps(report,indent=2));(LIB/'Docs/Validation_Report.json').write_text(json.dumps(report,indent=2));print('STAGE6_FINAL_VALIDATION_PASS',flush=True)
