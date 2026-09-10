import bpy,json,math
from pathlib import Path
from mathutils import Quaternion,Matrix
rig=bpy.data.objects['RepairRig']; scene=bpy.context.scene
body=bpy.data.actions['BODY_Kneel_L']; bag=body.layers[0].strips[0].channelbag(body.slots[0])
results=[]
for angle in (.45,.60,.72,.85):
    for fc in bag.fcurves:
        if fc.data_path=='pose.bones["chest"].rotation_quaternion':
            for k in fc.keyframe_points:
                t={1:0,16:0,38:.3,64:1,288:1}[round(k.co.x)]; k.co.y=Quaternion((1,0,0),angle*t)[fc.array_index]
            fc.update()
    for height in (.43,.48,.53):
        bpy.data.objects['TARGET_Screw'].location.z=height
        errors=[]
        for f in (146,152,170,174,184,210,246):
            scene.frame_set(f); rig.update_tag(); bpy.context.view_layer.update()
            p=rig.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones
            errors.append({s:(p['hand_ik.'+s].head-p['DEF-hand.'+s].head).length for s in ('L','R')})
        results.append({'angle':angle,'height':height,'max_R':max(x['R'] for x in errors),'max_L':max(x['L'] for x in errors)})
Path('E:/RepairRig/tests/stage3_reach_fit.json').write_text(json.dumps(results,indent=2))
