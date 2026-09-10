"""Milestone C: modest segmented mannequin, native skinning and facial drivers."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Quaternion
ROOT=Path('E:/RepairRig')
rig=bpy.data.objects.get('RepairRig')
assert rig is not None, 'This milestone requires the successfully generated rig.'
if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
assert not bpy.data.objects.get('Proxy_Head'), 'Already built; reload previous checkpoint to rebuild.'
collection=bpy.data.collections.new('Character | Proxy')
bpy.context.scene.collection.children.link(collection)
def material(name,color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); return m
body=material('Proxy | warm gray',(.48,.55,.60))
joint=material('Proxy | joints',(.12,.20,.25))
face=material('Proxy | face',(.67,.72,.74))
dark=material('Proxy | eyes and mouth',(.025,.045,.055))
white=material('Proxy | sclera',(.88,.90,.88))
def bind(obj,bone,mat):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    g=obj.vertex_groups.new(name=bone); g.add(list(range(len(obj.data.vertices))),1,'REPLACE')
    mod=obj.modifiers.new('Armature | Rigify DEF','ARMATURE'); mod.object=rig; mod.use_deform_preserve_volume=True
    obj.parent=rig
    for p in obj.data.polygons: p.use_smooth=True
    return obj
def ellipsoid(name,center,scale,bone,mat=body,rotation=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=center)
    obj=bpy.context.object; obj.name=name; obj.scale=scale
    if rotation is not None:
        obj.rotation_mode='QUATERNION'; obj.rotation_quaternion=rotation
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return bind(obj,bone,mat)
def segment(name,bone,radius):
    b=rig.data.bones[bone]; h,t=b.head_local,b.tail_local
    return ellipsoid(name,(h+t)/2,(radius,radius,(t-h).length*.58),bone,body,(t-h).to_track_quat('Z','Y'))
for side in ('L','R'):
    for part,radius in [('upper_arm',.045),('forearm',.037),('thigh',.068),('shin',.050)]:
        for suffix in ('','.001'):
            bone=f'DEF-{part}.{side}{suffix}'
            if bone in rig.data.bones: segment('Proxy_'+bone,bone,radius)
    h=rig.data.bones[f'DEF-hand.{side}']
    ellipsoid('Proxy_Palm.'+side,(h.head_local+h.tail_local)/2,(.040,.022,.054),h.name,body,(h.tail_local-h.head_local).to_track_quat('Z','Y'))
    for finger in ('thumb','f_index','f_middle','f_ring','f_pinky'):
        for i in range(1,4):
            segment(f'Proxy_{finger}.{i:02}.{side}',f'DEF-{finger}.{i:02}.{side}',.009 if finger=='thumb' else .007)
    foot=rig.data.bones[f'DEF-foot.{side}']
    ellipsoid('Proxy_Foot.'+side,(foot.head_local+foot.tail_local)/2+Vector((0,-.025,-.01)),(.063,.115,.043),foot.name,joint)
    for part in ('upper_arm','forearm','thigh','shin'):
        b=rig.data.bones[f'DEF-{part}.{side}']
        ellipsoid(f'Proxy_Joint_{part}.{side}',b.head_local,(.038,)*3,b.name,joint)
for i,width,depth in [(0,.115,.075),(1,.12,.073),(2,.15,.085),(3,.17,.09)]:
    bone='DEF-spine'+(f'.{i:03}' if i else '')
    b=rig.data.bones[bone]
    ellipsoid('Proxy_Torso_'+str(i),(b.head_local+b.tail_local)/2,(width,depth,b.length*.75),bone)
segment('Proxy_Neck','DEF-spine.005',.037)
head=rig.data.bones['DEF-spine.006']; z=head.head_local.z
ellipsoid('Proxy_Head',(0,-.005,z+.11),(.088,.078,.124),head.name,face)
ellipsoid('Proxy_Jaw',(0,-.052,z+.028),(.057,.040,.030),'DEF-jaw',face)
ellipsoid('Proxy_Mouth',(0,-.091,z+.047),(.027,.004,.003),'DEF-jaw',dark)
for side in ('L','R'):
    sign=1 if side=='L' else -1
    center=Vector((sign*.035,-.077,z+.115))
    ellipsoid('Proxy_Eye.'+side,center,(.022,)*3,'DEF-eye.'+side,white)
    ellipsoid('Proxy_Pupil.'+side,center+Vector((0,-.020,0)),(.009,.003,.009),'DEF-eye.'+side,dark)
    ellipsoid('Proxy_Brow.'+side,(sign*.035,-.084,z+.155),(.024,.006,.005),'DEF-brow.'+side,dark)
    ellipsoid('Proxy_MouthCorner.'+side,(sign*.03,-.09,z+.045),(.007,.004,.004),'DEF-mouth_corner.'+side,dark)
    # A spherical eyelid cap expands over the eyeball via a normal shape key.
    def cap(closed):
        verts=[]
        for j in range(9):
            theta=.02+(j/8)*(.55+closed*2.50)
            for k in range(17):
                phi=math.pi*k/16
                verts.append(tuple(center+Vector((.023*math.sin(theta)*math.cos(phi),-.023*math.sin(theta)*math.sin(phi),.023*math.cos(theta)))))
        return verts
    faces=[(j*17+k,j*17+k+1,(j+1)*17+k+1,(j+1)*17+k) for j in range(8) for k in range(16)]
    mesh=bpy.data.meshes.new('Lid surface.'+side); mesh.from_pydata(cap(0),[],faces)
    obj=bpy.data.objects.new('Proxy_Lid.'+side,mesh); collection.objects.link(obj)
    bind(obj,head.name,face)
    obj.shape_key_add(name='Basis'); key=obj.shape_key_add(name='Blink')
    for v,co in zip(key.data,cap(1)): v.co=co
    control=rig.pose.bones['lid.'+side]; control['blink']=0.0
    control.id_properties_ui('blink').update(min=0,max=1,description='Close the proxy eyelid: 0 open, 1 closed')
    driver=key.driver_add('value').driver; driver.type='AVERAGE'
    var=driver.variables.new(); var.name='blink'; var.type='SINGLE_PROP'
    var.targets[0].id=rig; var.targets[0].data_path=f'pose.bones["lid.{side}"]["blink"]'
# Connected, blended elbow sleeve: proves multi-bone skinning, not only rigid pieces.
for side in ('L','R'):
    upper=rig.data.bones[f'DEF-upper_arm.{side}.001']; lower=rig.data.bones[f'DEF-forearm.{side}']
    center=lower.head_local; axis=(lower.tail_local-upper.head_local).normalized()
    u=axis.cross(Vector((0,1,0))).normalized(); v=axis.cross(u)
    verts=[]; faces=[]
    for j in range(9):
        t=j/8
        for k in range(16):
            a=2*math.pi*k/16
            verts.append(center+axis*((t-.5)*.09)+.036*(math.cos(a)*u+math.sin(a)*v))
    for j in range(8):
        for k in range(16): faces.append((j*16+k,j*16+(k+1)%16,(j+1)*16+(k+1)%16,(j+1)*16+k))
    mesh=bpy.data.meshes.new('Elbow blend'); mesh.from_pydata(verts,[],faces)
    obj=bpy.data.objects.new('Proxy_ElbowBlend.'+side,mesh); collection.objects.link(obj)
    bind(obj,upper.name,joint); g0=obj.vertex_groups[upper.name]; g1=obj.vertex_groups.new(name=lower.name)
    for j in range(9):
        ids=list(range(j*16,(j+1)*16)); g0.add(ids,1-j/8,'REPLACE'); g1.add(ids,j/8,'REPLACE')
for side in ('L','R'):
    for limb in ('upper_arm','thigh'):
        p=rig.pose.bones[f'{limb}_parent.{side}']; p['IK_Stretch']=0.; p['pole_vector']=True
for c in rig.data.collections_all:
    if any(s in c.name for s in ('Tweak','Detail','(FK)')) or c.name in ('Face','Face (Primary)','Face (Secondary)','Simple Face'):
        c.is_visible=False
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='POSE')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        s=area.spaces.active; s.region_3d.view_distance=3.1; s.region_3d.view_location=Vector((0,0,1))
        s.region_3d.view_rotation=Quaternion((.703,.703,.075,.075)).normalized()
        s.shading.color_type='MATERIAL'; s.overlay.show_floor=True; s.show_region_ui=True
out=ROOT/'blend/RepairRig_02b_Mannequin.blend'; assert not out.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(ROOT/'tests/mannequin.json').write_text(json.dumps({'mesh_count':len(collection.objects),'vertices':sum(len(o.data.vertices) for o in collection.objects)},indent=2))
