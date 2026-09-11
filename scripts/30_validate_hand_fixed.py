"""Reopen and validate saved production hand fix against source; no scene saves."""
import bpy, addon_utils, json, hashlib, struct, sys, math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('E:/RepairRig');OUT=ROOT/'tests/hand_transfer';sys.path.insert(0,str(ROOT/'scripts'))
from hand_mesh_validation import prepare,inspect_pose,F
addon_utils.enable('rigify',default_set=True,persistent=True)
SOURCES={'source':ROOT/'blend/RepairRig_05_ProductionCharacter_Test.blend','fixed':ROOT/'blend/RepairRig_05_ProductionCharacter_HandFixed.blend'}
CAN=ROOT/'blend/RepairRig_04_ActionLibrary.blend'
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CAN,*SOURCES.values()]}

def curves(a):return [fc for l in a.layers for st in l.strips for sl in a.slots if (bag:=st.channelbag(sl)) for fc in bag.fcurves]
def action_payload():return {a.name:[(c.data_path,c.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in c.keyframe_points]) for c in curves(a)] for a in bpy.data.actions}
def matrix(m):return [list(row) for row in m]
def matrix_error(a,b):return max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))
def mesh_hash(o):
 h=hashlib.sha256()
 for v in o.data.vertices:
  h.update(struct.pack('3f',*v.co))
  for g in v.groups:h.update(struct.pack('If',g.group,g.weight))
 for p in o.data.polygons:h.update(struct.pack(str(len(p.vertices))+'I',*p.vertices))
 return h.hexdigest()
def fingerprint(r,mesh):
 return {'actions':action_payload(),'mesh_weights_topology':mesh_hash(mesh),
 'bones':{b.name:{'matrix':matrix(b.matrix_local),'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in r.data.bones},
 'drivers':[(fc.data_path,fc.array_index,fc.driver.expression,[(v.name,v.type,[(t.id.name if t.id else None,t.data_path,t.bone_target,t.transform_type,t.transform_space) for t in v.targets]) for v in fc.driver.variables]) for fc in r.animation_data.drivers],
 'objects':{o.name:{'parent':o.parent.name if o.parent else None,'parent_bone':o.parent_bone,'basis':matrix(o.matrix_basis)} for o in bpy.data.objects},
 'assets':{a.name:bool(a.asset_data) for a in bpy.data.actions if a.name.startswith('POSE_')}}

def tool_metrics(mesh,prep,toolname):
 dg=bpy.context.evaluated_depsgraph_get();tool=bpy.data.objects[toolname].evaluated_get(dg);tm=tool.to_mesh();tv=[tool.matrix_world@v.co for v in tm.vertices];tm.calc_loop_triangles();tt=[tuple(t.vertices) for t in tm.loop_triangles];tree=BVHTree.FromPolygons(tv,tt,all_triangles=True)
 me=mesh.evaluated_get(dg);mm=me.to_mesh();hv=[me.matrix_world@v.co for v in mm.vertices];rows={}
 def inside(point):
  # Ray parity does not depend on imported handle normal winding.
  votes=0
  for vec in [(1,.371,.217),(.173,1,.419),(.293,.137,1)]:
   direction=Vector(vec).normalized();origin=point.copy();hits=0
   for _ in range(20):
    co,_,_,_=tree.ray_cast(origin,direction)
    if co is None:break
    hits+=1;origin=co+direction*1e-6
   votes+=hits%2
  return votes>=2
 for i in set(v for t in prep[0] for v in t):
  region=prep[2][i];co,no,face,dist=tree.find_nearest(hv[i]);row=rows.setdefault(region,{'min_surface_distance':1e9,'vertices_inside':0,'max_inside_depth':0.0})
  row['min_surface_distance']=min(row['min_surface_distance'],dist)
  if dist>1e-5 and inside(hv[i]):row['vertices_inside']+=1;row['max_inside_depth']=max(row['max_inside_depth'],dist)
 ht=BVHTree.FromPolygons(hv,prep[0],all_triangles=True);pairs=len(ht.overlap(tree));me.to_mesh_clear();tool.to_mesh_clear()
 return {'handle':toolname,'surface_triangle_intersections':pairs,'regions':rows,'method':'three-ray majority parity for interior, nearest surface distance and hand/tool triangle overlaps'}

result={'hashes_before':hashes,'scenes':{}};fps={}
for label,path in SOURCES.items():
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
 r=bpy.data.objects['RepairRig'];mesh=bpy.data.objects['Chris-Low-poly'];s=bpy.context.scene
 def update():r.update_tag();bpy.context.view_layer.update()
 fps[label]=fingerprint(r,mesh);prep=prepare(mesh)
 saved_frame=s.frame_current;saved_action=r.animation_data.action.name if r.animation_data.action else None
 poses={};r.animation_data.action=None
 for tr in r.animation_data.nla_tracks:tr.mute=True
 for p in r.pose.bones:
  if any(f in p.name for f in F) and not p.name.startswith(('ORG-','DEF-','MCH-')):p.matrix_basis=Matrix.Identity(4)
 update()
 # Use unchanged production body posture; action evaluation only supplies finger channels.
 cam=bpy.data.objects.new('VALIDATION_Camera',bpy.data.cameras.new('VALIDATION_Camera'));bpy.context.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.32
 s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='OBJECT';mesh.color=(.65,.7,.8,1);s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.08,.08,.08);s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100
 hp=r.pose.bones['DEF-hand.R'].matrix.copy();center=r.matrix_world@(hp@Vector((0,.105,0)))
 for a in [a for a in bpy.data.actions if a.name.startswith('POSE_')]:
  r.animation_data.action=a;r.animation_data.action_slot=a.slots[0];s.frame_set(1);update()
  item=inspect_pose(r,mesh,prep)
  expected={f:next(fc.evaluate(1) for fc in curves(a) if fc.data_path=='pose.bones["'+f+'.01_master.R"].scale' and fc.array_index==1) for f in F}
  ep=r.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
  item['channel_error']=max(abs(ep[f+'.01_master.R'].scale.y-v) for f,v in expected.items())
  item['bend_driver_error']=max(abs(ep['MCH-'+f+'.%02d_drv.R'%i].rotation_euler.x-(1-v)*math.pi) for f,v in expected.items() for i in [2,3])
  item['drivers_valid']=all(fc.driver.is_valid for fc in r.animation_data.drivers)
  for o in bpy.data.objects:
   if o.type=='MESH':o.hide_render=o!=mesh
  if a.name=='POSE_Grip_Screwdriver_R':
   for o in bpy.data.objects:
    if o.name.startswith('Screwdriver_'):o.hide_render=False;o.color=(.9,.3,.08,1)
   item['tool_contact']=tool_metrics(mesh,prep,'Screwdriver_Handle')
   dg=bpy.context.evaluated_depsgraph_get();t=bpy.data.objects['TOOL_Screwdriver'].evaluated_get(dg);socket=bpy.data.objects['ATTACH_Screwdriver_R'].evaluated_get(dg)
   item['tool_socket_matrix_error']=matrix_error(t.matrix_world,socket.matrix_world)
  if a.name=='POSE_Grip_Pliers_R':
   tool=bpy.data.objects['TOOL_Pliers'];tool.constraints[0].influence=1;tool.update_tag();update()
   for o in bpy.data.objects:
    if o.name.startswith('Pliers_') and o.type=='MESH':o.hide_render=False;o.color=(.9,.3,.08,1)
   item['tool_contact']=[tool_metrics(mesh,prep,'Pliers_Handle_'+str(i)) for i in [-1,1]]
  for view,v in [('palm',(1,0,0)),('side',(0,0,1))]:
   cam.location=center+hp.to_3x3()@Vector(v)*.6;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/(label+'_validated_'+a.name+'_'+view+'.png'));bpy.ops.render.render(write_still=True)
  poses[a.name]=item
  bpy.data.objects['TOOL_Pliers'].constraints[0].influence=0
  print('VALIDATED',label,a.name,flush=True)
 result['scenes'][label]={'saved_frame':saved_frame,'saved_action':saved_action,'poses':poses,'hand_triangles':len(prep[0]),'manual_axes':{f+'.'+side:bpy.data.objects['RepairRig_Metarig'].pose.bones[f+'.01.'+side].rigify_parameters.primary_rotation_axis for f in F for side in ['R','L']}}
a,b=fps['source'],fps['fixed'];checks={}
checks['action_payloads_identical']=a['actions']==b['actions'];checks['mesh_weights_topology_identical']=a['mesh_weights_topology']==b['mesh_weights_topology'];checks['driver_definitions_identical']=a['drivers']==b['drivers'];checks['bone_names_and_parents_identical']=a['bones'].keys()==b['bones'].keys() and all(a['bones'][n]['parent']==b['bones'][n]['parent'] for n in a['bones']);checks['object_transforms_and_parenting_identical']=a['objects']==b['objects'];checks['six_pose_assets']=len(b['assets'])==6 and all(b['assets'].values())
result['nonfinger_rest_max_error']=max(matrix_error(v['matrix'],b['bones'][n]['matrix']) for n,v in a['bones'].items() if not any(f in n for f in F));checks['nonfinger_rest_within_roundtrip_tolerance']=result['nonfinger_rest_max_error']<1e-5
checks['all_six_native_pose_evaluations']=all(p['channel_error']<1e-6 and p['bend_driver_error']<1e-5 and p['drivers_valid'] for p in result['scenes']['fixed']['poses'].values())
checks['both_inputs_unchanged']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
result['compatibility_checks']=checks;result['compatibility_pass']=all(checks.values());result['collision_free']=all(p['self_intersection_triangle_pairs']==0 for p in result['scenes']['fixed']['poses'].values());result['production_contact_ready']=False
(OUT/'reopen_validation.json').write_text(json.dumps(result,indent=2))
assert result['compatibility_pass'],checks
bpy.ops.wm.quit_blender()

