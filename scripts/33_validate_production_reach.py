"""Fresh-file behavioral validation; no .blend saves."""
import bpy,json,math,hashlib,traceback,sys
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path('E:/RepairRig');OUT=ROOT/'tests/reach_fixed';sys.path.insert(0,str(ROOT/'scripts'))
from hand_mesh_validation import prepare,inspect_pose
DST=ROOT/'blend/RepairRig_05B_ProductionCharacter_ReachFixed.blend'
SRC=ROOT/'blend/RepairRig_05_ProductionCharacter_HandFixed.blend'
S=Matrix.Diagonal((-1,1,1))
def angle(a,b):
 v=math.degrees(a.to_quaternion().rotation_difference(b.to_quaternion()).angle);return min(v,360-v)
def open_file(path=DST):
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
 return bpy.data.objects['RepairRig']
def assign(r,name):
 a=bpy.data.actions[name];ad=r.animation_data;ad.use_nla=False;ad.action=a;ad.action_slot=a.slots[0];return a
def update(r,f):
 bpy.context.scene.frame_set(f);r.update_tag();bpy.context.view_layer.update()
def snapshot(r):
 dg=bpy.context.evaluated_depsgraph_get();ep=r.evaluated_get(dg).pose.bones
 o=bpy.data.objects['Chris-Low-poly'];ev=o.evaluated_get(dg);me=ev.to_mesh();groups={g.index:g.name for g in o.vertex_groups}
 points={}
 for side in ['L','R']:
  ids=[v.index for v in o.data.vertices if any(groups[g.group]=='DEF-hand.'+side and g.weight>.5 for g in v.groups)]
  assert ids
  points[side]=list(sum((o.matrix_world@me.vertices[i].co for i in ids),Vector())/len(ids))
 finite=all(math.isfinite(c) for v in me.vertices for c in v.co);ev.to_mesh_clear()
 return {'hand_heads':{side:list(r.matrix_world@ep['DEF-hand.'+side].head) for side in ['L','R']},'hand_mesh_centroids':points,'ik_def_distance':{side:(ep['DEF-hand.'+side].head-ep['hand_ik.'+side].head).length for side in ['L','R']},'torso':list(ep['torso'].head),'mesh_finite':finite,'wrist_mirror_angle':angle(ep['hand_ik.L'].matrix.to_3x3(),S@ep['hand_ik.R'].matrix.to_3x3()@S),'drivers_valid':all(fc.driver.is_valid for fc in r.animation_data.drivers)}
def render(r,name,center,scale):
 s=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.name!='Chris-Low-poly'
 cam=bpy.data.objects.new('ValidationCamera',bpy.data.cameras.new('ValidationCamera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=scale;cam.location=Vector(center)+Vector((0,-4,1));cam.rotation_euler=(Vector(center)-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.65,.68,.72);s.display.shading.show_cavity=True;s.render.resolution_x=1000;s.render.resolution_y=700;s.render.resolution_percentage=100;s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
report={'file':str(DST),'sha256_before':hashlib.sha256(DST.read_bytes()).hexdigest(),'motions':{},'pose_assets':{}}
try:
 r=open_file();report['saved_state']=snapshot(r)
 for name in ['BODY_Kneel_L','REACH_Forward_Low_R','REACH_Forward_Mid_R','REACH_Forward_Low_L','BRACE_Forward_L']:
  r=open_file();assign(r,name);frames=[1,25,49] if name.startswith('BODY') else [1,17,33];samples={}
  for f in frames:update(r,f);samples[str(f)]=snapshot(r)
  first=samples[str(frames[0])];last=samples[str(frames[-1])]
  item={'samples':samples,'hand_displacement':{side:(Vector(first['hand_heads'][side])-Vector(last['hand_heads'][side])).length for side in ['L','R']},'mesh_hand_displacement':{side:(Vector(first['hand_mesh_centroids'][side])-Vector(last['hand_mesh_centroids'][side])).length for side in ['L','R']},'torso_displacement':(Vector(first['torso'])-Vector(last['torso'])).length}
  if not name.startswith('BODY'):
   side=name[-1];assert item['hand_displacement'][side]>.01;assert item['mesh_hand_displacement'][side]>.01
  else:assert item['torso_displacement']>.01;assert max(v['wrist_mirror_angle'] for v in samples.values())<.1
  assert all(v['mesh_finite'] and v['drivers_valid'] for v in samples.values())
  report['motions'][name]=item
  print('MOTION',name,item['hand_displacement'],item['mesh_hand_displacement'],flush=True)
 # Tool cycle: hold the restored low reach at its end, then evaluate the existing tool-owner Action.
 r=open_file();assign(r,'BODY_Kneel_L');update(r,49);a=assign(r,'REACH_Forward_Low_R');update(r,33)
 # Bake only the evaluated in-memory action values by disconnecting without changing current properties.
 r.animation_data.action=None
 roll=bpy.data.objects['CONTACT_ScrewdriverRoll_R'];a=bpy.data.actions['TOOL_Screwdriver_CW_R'];roll.animation_data.use_nla=False;roll.animation_data.action=a;roll.animation_data.action_slot=a.slots[0]
 tool=bpy.data.objects['TOOL_Screwdriver'];tool_samples={}
 for f in [1,17,33,37]:
  update(r,f);dg=bpy.context.evaluated_depsgraph_get();te=tool.evaluated_get(dg);socket=bpy.data.objects['ATTACH_Screwdriver_R'].evaluated_get(dg);ep=r.evaluated_get(dg).pose.bones
  tool_samples[str(f)]={'roll_z':roll.rotation_euler.z,'tool_position':list(te.matrix_world.translation),'socket_position_error':(te.matrix_world.translation-socket.matrix_world.translation).length,'socket_orientation_error':angle(te.matrix_world.to_3x3(),socket.matrix_world.to_3x3()),'ik_def_distance':(ep['hand_ik.R'].head-ep['DEF-hand.R'].head).length}
 assert abs(tool_samples['17']['roll_z']-tool_samples['1']['roll_z'])>.1
 report['tool_cycle']=tool_samples
 # Pose assets: native slot evaluation; compare local hand geometry with the unchanged input.
 pose_results={}
 for label,path in [('source',SRC),('fixed',DST)]:
  r=open_file(path);mesh=bpy.data.objects['Chris-Low-poly'];prepared=prepare(mesh);pose_results[label]={}
  for name in sorted(a.name for a in bpy.data.actions if a.name.startswith('POSE_')):
   a=assign(r,name);update(r,1);values={}
   for l in a.layers:
    for st in l.strips:
     bag=st.channelbag(a.slots[0])
     if not bag:continue
     for fc in bag.fcurves:
      value=r.path_resolve(fc.data_path);actual=value if isinstance(value,(int,float)) else value[fc.array_index];values[fc.data_path+str(fc.array_index)]={'expected':fc.evaluate(1),'actual':actual}
   assert a.asset_data and all(abs(v['expected']-v['actual'])<1e-5 for v in values.values())
   pose_results[label][name]={'channels_match':True,'geometry':inspect_pose(r,mesh,prepared)}
 report['pose_assets']=pose_results
 # Neutral rest-offset check and saved-pose visual evidence, in disposable memory only.
 r=open_file();render(r,'saved_pose',(0,0,1),2.3)
 r=open_file();r.animation_data.action=None;r.animation_data.use_nla=False
 for p in r.pose.bones:p.matrix_basis=Matrix.Identity(4)
 for side in ['L','R']:
  for c in r.pose.bones['hand_ik.'+side].constraints:c.influence=0
 update(r,1);report['neutral_state']=snapshot(r);assert report['neutral_state']['wrist_mirror_angle']<.1
 render(r,'neutral_pose',(0,0,1),2.3)
 report['sha256_after']=hashlib.sha256(DST.read_bytes()).hexdigest();assert report['sha256_before']==report['sha256_after']
 report['pass']=True
except:report['error']=traceback.format_exc();print(report['error'],flush=True)
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print('VALIDATION_COMPLETE',report.get('pass',False),flush=True)
bpy.ops.wm.quit_blender()
