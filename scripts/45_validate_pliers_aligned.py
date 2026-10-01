"""Fresh-file regression tests, including native tool operators and contact."""
import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path('E:/RepairRig');OUT=ROOT/'tests/pliers_aligned'
sys.path.insert(0,str(ROOT/'scripts'))
from hand_mesh_validation import prepare
from grip_contact_validation import contact_metrics
build=json.loads((OUT/'build.json').read_text())
def mat(m):return [list(row) for row in m]
def err(a,b):return max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))
def world(o):return o.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.copy()
def update():bpy.data.objects['RepairRig'].update_tag();bpy.context.view_layer.update()
def curves(a):return [f for l in a.layers for s in l.strips for sl in a.slots if (b:=s.channelbag(sl)) for f in b.fcurves]
def actions():return {a.name:[[f.data_path,f.array_index,[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation] for k in f.keyframe_points]] for f in curves(a)] for a in bpy.data.actions}
def sample():
 r=bpy.data.objects['RepairRig'];return {'wrist':mat(world(r)@r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones['hand_ik.R'].matrix),'screw':mat(world(bpy.data.objects['SCREW_Visible']))}
def contacts():
 m=bpy.data.objects['Chris-Low-poly'];return contact_metrics(m,prepare(m),['Pliers_Handle_-1','Pliers_Handle_1','Pliers_Jaw_-1','Pliers_Jaw_1'])
source=next(p for p in build['source_hashes'] if '05D_' in p)
bpy.ops.wm.open_mainfile(filepath=source,use_scripts=False);update()
before={}
for f in (1,17,33,37,161,179,197):bpy.context.scene.frame_set(f);update();before[str(f)]=sample()
bpy.context.scene.frame_set(33);update();oldcontacts=contacts()
bpy.ops.wm.open_mainfile(filepath=build['output'],use_scripts=True);update()
r=bpy.data.objects['RepairRig'];pc=bpy.data.objects['TOOL_Pliers'].constraints['Attach / release | pliers right socket'];sc=bpy.data.objects['TOOL_Screwdriver'].constraints['Attach / release | right hand socket']
checks={'embedded_ui_registered':hasattr(bpy.types,'REPAIRRIG_PT_tools'),'actions_identical':actions()==build['actions'],'rest_identical':{b.name:mat(b.matrix_local) for b in r.data.bones}==build['rest'],'sockets_identical':{n:mat(bpy.data.objects[n].matrix_basis) for n in build['sockets']}==build['sockets']}
assert checks['embedded_ui_registered'],checks
states={}
for state in (0,1,2,1,0,2):
 assert bpy.ops.repairrig.select_tool(tool=state)=={'FINISHED'}
 update();states[str(state)]=[sc.influence,pc.influence]
checks['mutually_exclusive_buttons']=states=={'0':[0.,0.],'1':[1.,0.],'2':[0.,1.]}
checks['no_duplicate_attachments']=sum(c.type=='CHILD_OF' for c in bpy.data.objects['TOOL_Pliers'].constraints)==1 and sum(c.type=='CHILD_OF' for c in bpy.data.objects['TOOL_Screwdriver'].constraints)==1
samples={}
for f in (1,17,33,37,161,179,197):
 bpy.context.scene.frame_set(f);update();s=sample();s['screw_matrix_error']=err(s['screw'],before[str(f)]['screw']);s['wrist_rotation_error']=max(abs(s['wrist'][i][j]-before[str(f)]['wrist'][i][j]) for i in range(3) for j in range(3));samples[str(f)]=s
checks['screw_motion_unchanged']=max(s['screw_matrix_error'] for s in samples.values())<1e-6
checks['wrist_rotation_unchanged']=max(s['wrist_rotation_error'] for s in samples.values())<1e-5
bpy.context.scene.frame_set(33);update()
ref=bpy.data.objects['REF_PliersContact'];roll=bpy.data.objects['CONTACT_ScrewdriverRoll_R']
gap=(world(ref).translation-world(roll).translation).length
tips=[world(bpy.data.objects['Pliers_Jaw_'+str(i)])@Vector((0,0,.5)) for i in (-1,1)]
actualgap=((tips[0]+tips[1])/2-world(roll).translation).length
checks['pliers_work_contact']=gap<1e-5 and actualgap<1e-5
newcontacts=contacts()
def penetration(c):return sum(v['inside_vertices'] for tool in c.values() for v in tool['regions'].values())
checks['no_new_sampled_hand_penetration']=penetration(newcontacts)<=penetration(oldcontacts)
bpy.ops.repairrig.select_tool(tool=1);update()
checks['screwdriver_transform_preserved']=err(mat(world(bpy.data.objects['TOOL_Screwdriver'])),build['screwdriver_attached_world'])<1e-5
checks['screwdriver_tip_contact']=(world(bpy.data.objects['REF_ScrewdriverTip']).translation-world(roll).translation).length<1e-5
checks['drivers_valid']=all(f.driver.is_valid for o in bpy.data.objects if o.animation_data for f in o.animation_data.drivers)
checks['source_files_unchanged']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in build['source_hashes'].items())
# Prove that a separate, constant-keyed shot strip can animate the selector
# while the existing reach Action remains active. This test is never saved.
ad=r.animation_data;old_action=ad.action;old_slot=ad.action_slot;old_nla=ad.use_nla
ad.action=None
for frame,state in ((1,0),(17,1),(33,2)):
 r['repairrig_tool']=state;r.keyframe_insert(data_path='["repairrig_tool"]',frame=frame,group='Tool selection')
shot=ad.action;shot.name='TEST_ONLY_ToolSelection'
for fc in curves(shot):
 for k in fc.keyframe_points:k.interpolation='CONSTANT'
ad.action=old_action;ad.action_slot=old_slot
track=ad.nla_tracks.new();track.name='TEST_ONLY_ToolSelection'
strip=track.strips.new(shot.name,1,shot);strip.blend_type='REPLACE';strip.extrapolation='HOLD';ad.use_nla=True
keyed={}
for f in (1,16,17,32,33):
 bpy.context.scene.frame_set(f);update();keyed[str(f)]=[sc.influence,pc.influence]
checks['constant_selector_nla_animation']=keyed=={'1':[0.,0.],'16':[0.,0.],'17':[1.,0.],'32':[1.,0.],'33':[0.,1.]}
ad.nla_tracks.remove(track);bpy.data.actions.remove(shot);ad.use_nla=old_nla
bpy.context.scene.frame_set(33);bpy.ops.repairrig.select_tool(tool=2);update()
checks['shared_actions_unchanged_after_key_test']=actions()==build['actions']
report={'checks':checks,'states':states,'reference_contact_gap':gap,'actual_jaw_contact_gap':actualgap,'samples':samples,'contact_before':oldcontacts,'contact_after':newcontacts,'pass':all(checks.values())}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({'checks':checks,'actual_contact_gap':actualgap},indent=2),flush=True)
assert report['pass'],checks
# Render a disposable visual inspection; never save these review-only changes.
bpy.ops.repairrig.select_tool(tool=2);update()
s=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=o.name!='Chris-Low-poly' and not o.name.startswith(('Pliers_','SCREW_'))
center=(world(bpy.data.objects['TOOL_Pliers']).translation+world(ref).translation)*.5
cam=bpy.data.objects.new('ReviewContactCamera',bpy.data.cameras.new('ReviewContactCamera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.42
cam.location=center+Vector((-.5,-.65,.35));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';s.display.shading.show_cavity=True
bpy.data.objects['Chris-Low-poly'].color=(.65,.68,.72,1)
for o in bpy.data.objects:
 if o.name.startswith('Pliers_'):o.color=(.85,.28,.06,1)
s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.filepath=str(OUT/'contact_review.png');bpy.ops.render.render(write_still=True)
