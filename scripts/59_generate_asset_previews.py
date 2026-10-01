"""Render real native asset thumbnails; only generated library metadata changes."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,'E:/RepairRig/scripts')
from hand_mesh_validation import prepare
LIB=Path('E:/BlenderAssets/RepairRig');OUT=Path('E:/RepairRig/tests/library/previews');OUT.mkdir(exist_ok=True)
manifest=json.loads((LIB/'Docs/Library_Manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def append(file,kind,name):bpy.ops.wm.append(directory=str(LIB/file)+'/'+kind+'/',filename=name,instance_collections=False,do_reuse_local_id=True)
def curves(a):return [f for l in a.layers for s in l.strips for sl in a.slots if (b:=s.channelbag(sl)) for f in b.fcurves]
def values(owner,name,frame):
 for fc in curves(bpy.data.actions[name]):
  value=owner.path_resolve(fc.data_path)
  if isinstance(value,(float,int,bool)):
   if fc.data_path.endswith(']'):
    prefix,key=fc.data_path.rsplit('[',1);owner.path_resolve(prefix)[key[1:-2]]=fc.evaluate(frame)
   else:
    prefix,key=fc.data_path.rsplit('.',1);setattr(owner.path_resolve(prefix),key,fc.evaluate(frame))
  else:value[fc.array_index]=fc.evaluate(frame)
 owner.update_tag();bpy.context.view_layer.update()
bpy.ops.wm.read_factory_settings(use_empty=True)
for item in manifest['assets']:
 if item['type']=='Collection':append(item['file'],'Collection',item['name'])
for file in ['Actions/RepairRig_Motion.blend','Poses/RepairRig_HandPoses_Canonical.blend','Poses/RepairRig_HandPoses_Production.blend']:
 with bpy.data.libraries.load(str(LIB/file),link=False) as (src,dst):dst.actions=src.actions
r=bpy.data.objects['RepairRig'];m=bpy.data.objects['Chris-Low-poly'];bpy.context.view_layer.objects.active=r
text=r['repairrig_library_ui'];exec(compile(text.as_string(),text.name,'exec'),{'__name__':'__main__'});bpy.ops.repairrig.bind_library_tools();bpy.ops.repairrig.bind_worksite()
prep=prepare(m);s=bpy.context.scene;cam=bpy.data.objects.new('PreviewCamera',bpy.data.cameras.new('PreviewCamera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO'
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.render.resolution_x=256;s.render.resolution_y=256;s.render.resolution_percentage=100
for item in manifest['assets']:
 name=item['name'];hand=name.startswith('POSE_');temp=None
 for p in r.pose.bones:p.matrix_basis=Matrix.Identity(4)
 for p in r.pose.bones:
  for c in p.constraints:
   if c.name.startswith(('Pickup |','Reach |','Work |','Brace |','Look |')):c.influence=0
 r['repairrig_tool']=0;r.update_tag();bpy.context.view_layer.update();values(r,'BODY_Idle_Standing',1)
 visible=[m];center=Vector((0,0,.95));direction=Vector((2,-4,1.1));scale=2.1
 if item['type']=='Action':
  if item['owner']=='RepairRig':values(r,name,bpy.data.actions[name].frame_range[1])
  else:
   values(r,'BODY_Kneel_L',49);values(r,'REACH_Forward_Low_R',33);values(r,'POSE_Grip_Screwdriver_R_Production',1);r['repairrig_tool']=1;values(bpy.data.objects['CONTACT_ScrewdriverRoll_R'],name,17)
  if hand:
   ev=m.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();coords=[m.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
   mesh=bpy.data.meshes.new('PreviewOnlyHand');mesh.from_pydata(coords,[],prep[0]);mesh.update();temp=bpy.data.objects.new('PreviewOnlyHand',mesh);s.collection.objects.link(temp)
   for p in mesh.polygons:p.use_smooth=True
   visible=[temp];h=r.matrix_world@r.pose.bones['DEF-hand.R'].matrix;center=h@Vector((-.015,.12,.02));direction=h.to_3x3()@Vector((-1,.3,.4));scale=.28
  elif name.startswith('TOOL_Screwdriver'):
   visible += [o for o in bpy.data.objects if o.name.startswith('Screwdriver_')];h=r.matrix_world@r.pose.bones['DEF-hand.R'].matrix;center=h@Vector((-.015,.12,.02));direction=h.to_3x3()@Vector((-1,.3,.4));scale=.55
 elif name.startswith('RepairRig_Tool_'):
  prefix='Screwdriver_' if 'Screwdriver' in name else 'Pliers_';visible=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(prefix)]
  bounds=[o.matrix_world@Vector(p) for o in visible for p in o.bound_box];lo=Vector([min(p[i] for p in bounds) for i in range(3)]);hi=Vector([max(p[i] for p in bounds) for i in range(3)]);center=(lo+hi)/2;scale=(hi-lo).length*1.25;direction=Vector((1,-1,1))
 elif name=='RepairRig_Worksite_Demo':
  visible=[o for o in bpy.data.collections[name].all_objects if o.type=='MESH'];center=Vector((0,-.4,.6));scale=1.6;direction=Vector((2,-4,2))
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o not in visible
 cam.location=center+direction.normalized()*4;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
 if temp:mesh=temp.data;bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(mesh)
 print('PREVIEW',name,flush=True)
# Re-read the original packages; never export the bound preview rig/tool session.
for file,old in manifest['files'].items():
 path=LIB/file;assert sha(path)==old['sha256'],'Library was edited during preview generation'
 bpy.ops.wm.read_factory_settings(use_empty=True)
 normalized=file.replace('\\','/')
 kind='actions' if normalized.startswith(('Actions/','Poses/')) else 'collections'
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):setattr(dst,kind,getattr(src,kind))
 expected={item['name']:item for item in manifest['assets'] if (item['type']=='Action' if kind=='actions' else item.get('file')==normalized)}
 ids=[id for id in getattr(bpy.data,kind) if id.name in expected]
 assert ids,'No asset IDs loaded from '+file
 for id in ids:
  # Native append may clear asset metadata; restore the curated manifest labels.
  if not id.asset_data:
   item=expected[id.name];id.asset_mark();id.asset_data.catalog_id=manifest['catalogs'][item['catalog']];id.asset_data.author='RepairRig'
   id.asset_data.description=(f"{id.name}. Owner: {item.get('owner','Collection')}. RepairRig-compatible rigs only; no automatic retargeting. " + ('Chris production-specific finger fit; 20 reset controls.' if item['catalog'].endswith('Production') else 'Canonical proxy reference; clear production FK offsets first.' if item['catalog'].endswith('Canonical') else 'Reusable native RepairRig asset.'))
   for tag in ('RepairRig','Stage 6',item['catalog'].split('/')[-1]):id.asset_data.tags.new(tag)
  with bpy.context.temp_override(id=id):bpy.ops.ed.lib_id_load_custom_preview(filepath=str(OUT/(id.name+'.png')))
 bpy.data.libraries.write(str(path),set(ids),path_remap='RELATIVE',fake_user=True,compress=True)
 manifest['files'][file]={'bytes':path.stat().st_size,'sha256':sha(path)}
manifest['previews']='31 rendered native custom previews embedded in asset datablocks'
(LIB/'Docs/Library_Manifest.json').write_text(json.dumps(manifest,indent=2));print('PREVIEWS_COMPLETE',flush=True)
