"""Check the saved deliverable in the visible session, leaving it open."""
import bpy,json,traceback
from pathlib import Path
ROOT=Path('E:/RepairRig')
if bpy.data.objects.get('RepairRig'):
    try:
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blend/RepairRig_02_ControlRig.blend'),use_scripts=True)
        rig=bpy.data.objects['RepairRig']
        bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
        before=rig.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones['DEF-hand.R'].head.copy()
        p=rig.pose.bones['hand_ik.R']; old=p.matrix_basis.copy(); p.location.x+=.025
        rig.update_tag(); bpy.context.view_layer.update()
        delta=(rig.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones['DEF-hand.R'].head-before).length
        assert delta>.005
        p.matrix_basis=old
        lids={}
        for side in ('L','R'):
            rig.pose.bones['lid.'+side]['blink']=1.
            rig.update_tag(); bpy.context.scene.frame_set(2); bpy.context.view_layer.update()
            keys=bpy.data.objects['Proxy_Lid.'+side].data.shape_keys
            lids[side]=keys.key_blocks['Blink'].value
            assert lids[side]>.99
            rig.pose.bones['lid.'+side]['blink']=0.
        rig.update_tag(); bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
        invalid=[f.data_path for f in rig.animation_data.drivers if not f.driver.is_valid]
        assert not invalid
        report={'pass':True,'reopened':bpy.data.filepath,'hand_motion':delta,'blink_values':lids,
                'rigify_drivers':len(rig.animation_data.drivers),'invalid_drivers':invalid,
                'embedded_rig_ui':[t.name for t in bpy.data.texts if 'rig_ui' in t.name],
                'metarig_has_blink':all('blink' in bpy.data.objects['RepairRig_Metarig'].pose.bones['lid.'+s] for s in ('L','R'))}
        (ROOT/'tests/reopen_validation.json').write_text(json.dumps(report,indent=2))
        # Reload once more so the visible document is the exact saved neutral file.
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blend/RepairRig_02_ControlRig.blend'),use_scripts=True)
    except Exception:
        (ROOT/'tests/reopen_exception.txt').write_text(traceback.format_exc()); raise
