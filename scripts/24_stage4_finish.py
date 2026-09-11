import sys,traceback,runpy
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
try:
 # Keep the Pose Browser restricted to static poses, avoiding accidental motion-as-pose use.
 for name in json.loads((OUT/'expected_actions.json').read_text()):
  a=bpy.data.actions[name]
  if a.asset_data: a.asset_clear()
  a.use_fake_user=True
 pliers=bpy.data.objects['TOOL_Pliers']; update(); pliers.constraints[0].inverse_matrix=pliers.matrix_basis.inverted()
 # Make the native NLA visible at useful height in the opening layout.
 area=max((a for a in bpy.context.screen.areas if a.type=='VIEW_3D'),key=lambda a:a.width*a.height)
 before=set(a.as_pointer() for a in bpy.context.screen.areas)
 with bpy.context.temp_override(area=area): bpy.ops.screen.area_split(direction='HORIZONTAL',factor=.65)
 views=[a for a in bpy.context.screen.areas if a.type=='VIEW_3D']; bottom=min(views,key=lambda a:a.y); bottom.type='NLA_EDITOR'
 for area in bpy.context.screen.areas:
  if area.type=='NLA_EDITOR':
   area.spaces.active.dopesheet.show_only_selected=False
   with bpy.context.temp_override(area=area,region=next(reg for reg in area.regions if reg.type=='WINDOW')): bpy.ops.nla.view_all()
 r.animation_data.action=None; update(179)
 report=runpy.run_path(str(OUT/'validate_library.py'))['validate']('presave_validation')
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blend/RepairRig_04_ActionLibrary.blend'))
 (OUT/'finish.json').write_text(json.dumps({'pass':True,'sha256':hashlib.sha256((ROOT/'blend/RepairRig_04_ActionLibrary.blend').read_bytes()).hexdigest(),'motion_actions':15,'hand_pose_assets':6},indent=2))
 # Final pliers attachment and driver review, after saving; never save test state.
 reset(); assign(bpy.data.actions['TOOL_Pliers_Squeeze_R']); tool=bpy.data.objects['TOOL_Screwdriver']; tool.constraints[0].influence=0; pliers.constraints[0].influence=1
 errors=[]
 for f in [1,11,25]:
  update(f); dg=bpy.context.evaluated_depsgraph_get(); m=pliers.evaluated_get(dg).matrix_world; socket=bpy.data.objects['ATTACH_Pliers_R'].evaluated_get(dg).matrix_world
  errors.append(max(abs(m[i][j]-socket[i][j]) for i in range(4) for j in range(4)))
 assert max(errors)<1e-5,errors
 center=pliers.matrix_world.translation; cam=bpy.data.objects['CAM_Grip_Detail']; cam.location=center+Vector((-.4,.4,.25)); cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=.4; s.camera=cam
 render('pliers_final_closed',11); render('pliers_final_open',1)
 (OUT/'pliers_attachment_validation.json').write_text(json.dumps({'pass':True,'matrix_errors':errors},indent=2))
except: (OUT/'error_finish.txt').write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
