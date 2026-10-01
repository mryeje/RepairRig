"""Offline pose fitting helpers; no runtime dependency in delivered Blender files."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector,Euler
ROOT=Path('E:/RepairRig');OUT=ROOT/'tests/grip_refined';SRC=ROOT/'blend/RepairRig_05B_ProductionCharacter_ReachFixed.blend'
F=['f_index','f_middle','f_ring','f_pinky','thumb']
CONTROLS=[f+'.01_master.R' for f in F]+[f+'.%02d.R'%i for f in F for i in [1,2,3]]
def load():
 bpy.ops.wm.open_mainfile(filepath=str(SRC),use_scripts=False)
 r=bpy.data.objects['RepairRig'];r.animation_data.action=None;r.animation_data.use_nla=False
 for side in ['L','R']:
  for c in r.pose.bones['hand_ik.'+side].constraints:c.influence=0
 return r
def update(r):r.update_tag();bpy.context.view_layer.update()
def reset(r):
 for n in CONTROLS:r.pose.bones[n].matrix_basis=Matrix.Identity(4)
 update(r)
def set_finger(r,f,v):
 # v: MCP flexion, PIP flexion, DIP flexion, MCP splay, MCP opposition roll (degrees).
 for i in [1,2,3]:
  p=r.pose.bones[f+'.%02d.R'%i];p.rotation_quaternion=Euler(tuple(math.radians(x) for x in ([v[0],v[4],v[3]] if i==1 else [v[i-1],0,0])),'XYZ').to_quaternion()
def apply(r,pose):
 reset(r)
 for f,v in pose.items():set_finger(r,f,v)
 update(r)
def bones(r,f):
 ep=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones;h=ep['DEF-hand.R'].matrix.inverted()
 return [h@ep['DEF-'+f+'.01.R'].head]+[h@ep['DEF-'+f+'.%02d.R'%i].tail for i in [1,2,3]]
def render(r,name,tool=None,view='palm'):
 s=bpy.context.scene;h=r.matrix_world@r.pose.bones['DEF-hand.R'].matrix;center=h@Vector((-.015,.115,.025))
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.name!='Chris-Low-poly' and not (tool and o.name.startswith(tool))
 cam=bpy.data.objects.new('GripReviewCamera',bpy.data.cameras.new('GripReviewCamera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.30
 direction={'palm':(-1,.2,.3),'back':(1,.1,.3),'side':(-.25,.1,1),'oblique':(-1,.65,1)}[view]
 cam.location=center+h.to_3x3()@Vector(direction)*.7;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';bpy.data.objects['Chris-Low-poly'].color=(.65,.68,.72,1)
 for o in bpy.data.objects:
  if o.name.startswith(('Screwdriver_','Pliers_')):o.color=(.9,.3,.07,1)
 s.display.shading.show_cavity=True;s.render.resolution_x=720;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.filepath=str(OUT/(name+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
