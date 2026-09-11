import bpy, addon_utils, json, math
from pathlib import Path
from mathutils import Vector, Matrix
from rigify.utils.bones import align_chain_x_axis
ROOT=Path('E:/RepairRig'); OUT=ROOT/'tests/hand_transfer'; F=['f_index','f_middle','f_ring','f_pinky','thumb']
addon_utils.enable('rigify',default_set=True,persistent=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blend/RepairRig_05_ProductionCharacter_Test.blend'),use_scripts=False)
r=bpy.data.objects['RepairRig']; m=bpy.data.objects['RepairRig_Metarig']; s=bpy.context.scene
out={'frame':s.frame_current,'rig_animation':{'action':r.animation_data.action.name if r.animation_data.action else None,'nla':[(t.name,t.mute,[(st.name,st.action.name) for st in t.strips]) for t in r.animation_data.nla_tracks]},'offsets':{},'axes':{},'meshes':{},'objects':{}}
for p in r.pose.bones:
 if any(f in p.name for f in F) and not p.name.startswith(('ORG-','DEF-','MCH-')):
  err=max(abs(p.matrix_basis[i][j]-(1 if i==j else 0)) for i in range(4) for j in range(4))
  if err>1e-6:out['offsets'][p.name]={'location':list(p.location),'rotation':list(p.rotation_quaternion),'scale':list(p.scale)}
for o in bpy.data.objects:
 if o.type=='MESH' and any(md.type=='ARMATURE' for md in o.modifiers):out['meshes'][o.name]={'world':[list(v) for v in o.matrix_world],'modifiers':[(md.name,md.type) for md in o.modifiers]}
 if any(t in o.name for t in ['TOOL_','ATTACH_','CONTACT_']):out['objects'][o.name]={'world':[list(v) for v in o.matrix_world],'constraints':[(c.name,c.type,c.influence) for c in o.constraints]}
c=m.copy();c.data=m.data.copy();bpy.context.collection.objects.link(c);c.hide_set(False);bpy.context.view_layer.objects.active=c;c.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for side in ['R','L']:
 for f in F:
  ns=[f+'.%02d.'%i+side for i in [1,2,3]]
  old=[c.data.edit_bones[n].matrix.copy() for n in ns]
  align_chain_x_axis(c,ns)
  out['axes'][f+'.'+side]=[]
  for n,oldmat in zip(ns,old):
   eb=c.data.edit_bones[n];gen=r.data.bones['ORG-'+n]
   out['axes'][f+'.'+side].append({'name':n,'head_error':(gen.head_local-eb.head).length,'tail_error':(gen.tail_local-eb.tail).length,'generated_vs_recomputed_x_degrees':math.degrees(gen.matrix_local.to_3x3().col[0].angle(eb.x_axis)),'meta_vs_generated_x_degrees':math.degrees(oldmat.to_3x3().col[0].angle(gen.matrix_local.to_3x3().col[0]))})
bpy.ops.object.mode_set(mode='OBJECT');bpy.data.objects.remove(c,do_unlink=True)
(OUT/'root_cause_detail.json').write_text(json.dumps(out,indent=2))
# Non-saving close views of the production mesh, with hand controls neutral.
if r.animation_data:
 r.animation_data.action=None
 for tr in r.animation_data.nla_tracks:tr.mute=True
for p in r.pose.bones:
 if any(t in p.name for t in F) and not p.name.startswith(('ORG-','MCH-','DEF-')):p.matrix_basis=Matrix.Identity(4)
r.update_tag();bpy.context.view_layer.update()
mesh=bpy.data.objects['Chris-Low-poly']
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=(o!=mesh)
mesh.hide_render=False
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.65,.7,.8);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.08,.08,.08)
s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100
cam=bpy.data.objects.new('AUDIT_Camera',bpy.data.cameras.new('AUDIT_Camera'));bpy.context.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.32
hp=r.pose.bones['DEF-hand.R'].matrix; center=r.matrix_world@(hp@Vector((0,.12,0)))
for label,v in [('palm',(1,0,0)),('back',(-1,0,0)),('side',(0,0,1))]:
 cam.location=center+hp.to_3x3()@Vector(v)*.6;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/('production_open_'+label+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.quit_blender()

