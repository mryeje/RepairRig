"""Rebuild native drivers after all proxy datablocks exist, then validate."""
import bpy,runpy
rig=bpy.data.objects['RepairRig']
for p in rig.pose.bones: p.matrix_basis.identity()
for side in ('L','R'):
    rig.pose.bones['lid.'+side]['blink']=0.
    key=bpy.data.objects['Proxy_Lid.'+side].data.shape_keys.key_blocks['Blink']
    key.driver_remove('value')
    d=key.driver_add('value').driver; d.type='AVERAGE'
    var=d.variables.new(); var.name='blink'; var.type='SINGLE_PROP'
    var.targets[0].id=rig; var.targets[0].data_path=f'pose.bones["lid.{side}"]["blink"]'
bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
runpy.run_path('E:/RepairRig/tests/validate_base.py',run_name='__main__')
