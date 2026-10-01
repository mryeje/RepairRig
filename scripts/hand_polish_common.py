"""Offline Stage 5F diagnostics; no runtime dependencies in delivered checkpoint."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector, Matrix, Euler
from hand_mesh_validation import prepare, inspect_pose
from grip_contact_validation import contact_metrics
ROOT=Path('E:/RepairRig'); OUT=ROOT/'tests/hand_polished'; OUT.mkdir(exist_ok=True)
SRC=ROOT/'blend/RepairRig_05E_ProductionCharacter_PliersAligned.blend'
DST=ROOT/'blend/RepairRig_05F_ProductionCharacter_HandPolished.blend'
F=['f_index','f_middle','f_ring','f_pinky','thumb']
POSES=['OpenHand','Fist','Point','HoldSmallPart','Grip_Screwdriver','Grip_Pliers']
def curves(a):return [f for l in a.layers for s in l.strips for sl in a.slots if (b:=s.channelbag(sl)) for f in b.fcurves]
def update():bpy.data.objects['RepairRig'].update_tag();bpy.context.view_layer.update()
def load(path=SRC):
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False);update()
 return bpy.data.objects['RepairRig'],bpy.data.objects['Chris-Low-poly']
def pose(short):
 r=bpy.data.objects['RepairRig']
 for fc in curves(bpy.data.actions['POSE_'+short+'_R_Production']):r.path_resolve(fc.data_path)[fc.array_index]=fc.evaluate(1)
 r['repairrig_tool']=1 if short=='Grip_Screwdriver' else 2 if short=='Grip_Pliers' else 0
 update()
def evaluated(mesh):
 ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=[mesh.matrix_world@x.co for x in me.vertices];ev.to_mesh_clear();return v
def joint_labels(r,mesh,prep):
 joints={f+'.'+str(j):r.matrix_world@r.data.bones['DEF-'+f+'.%02d.R'%j].head_local for f in F for j in (1,2,3)}
 coords=[mesh.matrix_world@v.co for v in mesh.data.vertices]
 labels={i:min((n for n in joints if n.startswith(prep[2][i]+'.')),key=lambda n:(coords[i]-joints[n]).length) for i in set(v for t in prep[0] for v in t) if prep[2][i] in F}
 return labels
def metrics(r,mesh,prep):
 result=inspect_pose(r,mesh,prep);coords=evaluated(mesh);rest=[mesh.matrix_world@v.co for v in mesh.data.vertices];labs=joint_labels(r,mesh,prep);areas={}
 for t in prep[0]:
  if not all(i in labs for i in t):continue
  a,b,c=t;ar=(rest[b]-rest[a]).cross(rest[c]-rest[a]).length;de=(coords[b]-coords[a]).cross(coords[c]-coords[a]).length
  if ar>1e-10:areas.setdefault(labs[a],[]).append(de/ar)
 result['joint_triangle_area_ratios']={n:{'min':min(v),'p10':sorted(v)[int(len(v)*.1)],'median':sorted(v)[len(v)//2],'below_025':sum(x<.25 for x in v),'triangles':len(v)} for n,v in areas.items()}
 return result
def render_hand(r,mesh,prep,name,tool=None,view='palm'):
 s=bpy.context.scene;coords=evaluated(mesh);me=bpy.data.meshes.new('ReviewHand');me.from_pydata(coords,[],prep[0]);me.update();o=bpy.data.objects.new('ReviewHand',me);s.collection.objects.link(o);o.color=(.68,.7,.73,1)
 visibility={x.name:x.hide_render for x in bpy.data.objects if x.type=='MESH'}
 for x in bpy.data.objects:
  if x.type=='MESH':x.hide_render=x!=o and not (tool and x.name.startswith(tool))
 h=r.matrix_world@r.pose.bones['DEF-hand.R'].matrix;center=h@Vector((-.015,.12,.02))
 cam=bpy.data.objects.new('ReviewCamera',bpy.data.cameras.new('ReviewCamera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.28
 direction={'palm':(-1,.3,.4),'side':(-.25,.2,1),'back':(1,.3,.4)}[view]
 cam.location=center+h.to_3x3()@Vector(direction)*.7;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';s.display.shading.show_cavity=True
 for x in bpy.data.objects:
  if x.name.startswith(('Pliers_','Screwdriver_')):x.color=(.85,.28,.06,1)
 s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(OUT/(name+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
 bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(me);bpy.data.objects.remove(cam,do_unlink=True)
 for n,v in visibility.items():
  if n in bpy.data.objects:bpy.data.objects[n].hide_render=v
