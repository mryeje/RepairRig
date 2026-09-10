import bpy,json
from pathlib import Path
rig=bpy.data.objects['RepairRig']; out={}
for side in ('L','R'):
    rig.pose.bones['lid.'+side]['blink']=1.
    key=bpy.data.objects['Proxy_Lid.'+side].data.shape_keys
    key.update_tag(); rig.update_tag(refresh={'OBJECT','DATA','TIME'})
    bpy.context.scene.frame_set(2); bpy.context.view_layer.update()
    out[side]={'key':key.key_blocks['Blink'].value,'drivers':[{'valid':f.driver.is_valid,'path':f.data_path,'mute':f.mute,'target':f.driver.variables[0].targets[0].data_path,'resolved':rig.path_resolve(f.driver.variables[0].targets[0].data_path)} for f in key.animation_data.drivers]}
Path('E:/RepairRig/tests/driver_diagnose.json').write_text(json.dumps(out,indent=2))
