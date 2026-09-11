"""Offline authoring helpers. Saved files use native Blender data only."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector, Quaternion, Matrix
ROOT=Path('E:/RepairRig'); OUT=ROOT/'tests/stage4'; OUT.mkdir(exist_ok=True)
r=bpy.data.objects['RepairRig']; s=bpy.context.scene
FINGERS=['f_index','f_middle','f_ring','f_pinky','thumb']
BODY=['torso','chest','foot_ik.L','foot_ik.R','thigh_ik_target.L','thigh_ik_target.R']
def update(f=None):
 if f is not None: s.frame_set(f)
 r.update_tag(); bpy.context.view_layer.update()
def curves(a):
 return [fc for l in a.layers for st in l.strips for sl in a.slots if (bag:=st.channelbag(sl)) for fc in bag.fcurves]
def capture():
 return {p.name:{'location':list(p.location),'rotation_quaternion':list(p.rotation_quaternion),'scale':list(p.scale)} for p in r.pose.bones if not p.name.startswith(('DEF-','MCH-','ORG-'))}
def mute_all():
 for o in bpy.data.objects:
  if o.animation_data:
   o.animation_data.action=None
   for tr in o.animation_data.nla_tracks: tr.mute=True
def reset():
 mute_all()
 neutral=json.loads((OUT/'poses.json').read_text())['stand']
 for n,vals in neutral.items():
  for k,v in vals.items(): setattr(r.pose.bones[n],k,v)
 for n in ['hand_ik.R','hand_ik.L','head']:
  for c in r.pose.bones[n].constraints:
   if c.name.startswith(('Pickup |','Work |','Brace |','Look |','Reach |')): c.influence=0
 update()
def new(name,owner=r,desc='',loop=False,scope=''):
 owner.animation_data_create(); owner.animation_data.action=None
 a=bpy.data.actions.new(name); a.use_fake_user=True
 owner.animation_data.action=a
 a['Stage']='4'; a['intended_use']=desc; a['loopable']=loop; a['scope']=scope; a['owner']=owner.name
 return a
def key(n,path,frame,value,index=-1):
 p=r.pose.bones[n]; setattr(p,path,value); p.keyframe_insert(path,index=index,frame=frame,group=n)
def prop(n,name,frame,val):
 p=r.pose.bones[n]; p[name]=val; p.keyframe_insert('["'+name+'"]',frame=frame,group=n)
def finish(a,owner=r):
 for fc in curves(a):
  for k in fc.keyframe_points:
   k.handle_left_type='AUTO_CLAMPED'; k.handle_right_type='AUTO_CLAMPED'
 a['channels']=len(curves(a)); owner.animation_data.action=None
 return a
def pose_keys(pose,frame,bones=BODY):
 for n in bones:
  for path in (('rotation_quaternion',) if n=='chest' else ('location','rotation_quaternion')):
   key(n,path,frame,pose[n][path])
def assign(a,owner=r):
 owner.animation_data.action=a; owner.animation_data.action_slot=a.slots[0]; update()
def strip(owner,track,a,start,repeat=1,end=None):
 owner.animation_data_create(); owner.animation_data.action=None
 tr=owner.animation_data.nla_tracks.get(track) or owner.animation_data.nla_tracks.new(); tr.name=track; tr.mute=False
 st=tr.strips.new(a.name,int(start),a); st.action_slot=a.slots[0]; st.extrapolation='HOLD_FORWARD'; st.blend_type='REPLACE'; st.repeat=repeat
 if end is not None: st.frame_end=end
 return st
def save(name): bpy.ops.wm.save_as_mainfile(filepath=str(OUT/name))
def render(name,frame):
 update(frame); s.render.resolution_x=840; s.render.resolution_y=800; s.render.resolution_percentage=100
 s.render.image_settings.file_format='PNG'; s.render.filepath=str(OUT/(name+'.png')); bpy.ops.render.render(write_still=True)
def structure():
 return {'bones':{p.name:(p.parent.name if p.parent else None,[list(x) for x in p.matrix_local]) for p in r.data.bones},'drivers':[(f.data_path,f.array_index,f.driver.expression) for f in r.animation_data.drivers], 'contacts':{n:[(c.name,c.type,c.target.name if getattr(c,'target',None) else None) for c in r.pose.bones[n].constraints] for n in ['hand_ik.R','hand_ik.L','head']},'hierarchy':{n:(bpy.data.objects[n].parent.name if bpy.data.objects[n].parent else None) for n in ['CONTACT_ScrewdriverRoll_R','CONTACT_WorkGrip_R','CONTACT_WorkWrist_R','ATTACH_Screwdriver_R','REF_ScrewdriverTip']}}
def check_actions(names,label):
 result={}
 for name in names:
  a=bpy.data.actions[name]; fs=curves(a)
  assert fs and len(a.slots)==1
  assert not any(any(x in f.data_path for x in ['DEF-','ORG-','MCH-','pose.bones["root"]']) for f in fs)
  result[name]={'range':list(a.frame_range),'channels':len(fs),'paths':sorted(set(f.data_path for f in fs))}
 (OUT/(label+'.json')).write_text(json.dumps(result,indent=2))
