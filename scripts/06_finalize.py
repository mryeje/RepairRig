"""Restore neutral pose, persist schema notes, verify final rig and save."""
import bpy,json,math,traceback
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path('E:/RepairRig')
def main():
    rig=bpy.data.objects['RepairRig']; meta=bpy.data.objects['RepairRig_Metarig']
    results=json.loads((ROOT/'tests/base_validation.json').read_text())
    assert all(r['pass'] for r in results.values())
    neutral=json.loads((ROOT/'tests/neutral_bases.json').read_text())
    for name,rows in neutral.items(): rig.pose.bones[name].matrix_basis=Matrix(rows)
    for side in ('L','R'):
        for obj in (rig,meta):
            p=obj.pose.bones['lid.'+side]; p['blink']=0.
            p.id_properties_ui('blink').update(min=0.,max=1.,description='Proxy eyelid closure: 0 open, 1 closed')
        for limb in ('upper_arm','thigh'):
            p=rig.pose.bones[f'{limb}_parent.{side}']; p['IK_FK']=0.; p['IK_Stretch']=0.; p['pole_vector']=True
    rig.update_tag(); bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    def pos(name): return rig.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones[name].head.copy()
    report={'version':bpy.app.version_string,'background':bpy.app.background,'base_checks_passed':len(results)}
    for side in ('L','R'):
        hand=rig.pose.bones['hand_ik.'+side]; saved=hand.matrix_basis.copy()
        m=hand.matrix.copy(); m.translation+=Vector((-.12 if side=='L' else .12,-.16,.04)); hand.matrix=m
        rig.update_tag(); bpy.context.view_layer.update()
        elbow=pos('DEF-forearm.'+side)
        pole=rig.pose.bones['upper_arm_ik_target.'+side]; old=pole.matrix_basis.copy()
        m=pole.matrix.copy(); m.translation+=Vector((0,0,.15)); pole.matrix=m
        rig.update_tag(); bpy.context.view_layer.update()
        delta=(pos('DEF-forearm.'+side)-elbow).length
        assert delta>.002,delta
        report['elbow_pole_motion_'+side]=delta
        hand.matrix_basis=saved; pole.matrix_basis=old
    rig.update_tag(); bpy.context.view_layer.update()
    drivers=list(rig.animation_data.drivers)
    report['rigify_driver_count']=len(drivers)
    report['invalid_rigify_drivers']=[f.data_path for f in drivers if not f.driver.is_valid]
    assert len(drivers)>20 and not report['invalid_rigify_drivers']
    assert not rig.animation_data.action
    assert len(bpy.data.actions)==0, 'No temporary or library Actions in Stage 2 deliverable'
    report['actions']=len(bpy.data.actions)
    report['pose_bones']=len(rig.pose.bones)
    report['deform_bones']=sum(b.use_deform for b in rig.data.bones)
    report['mesh_count']=len(bpy.data.collections['Character | Proxy'].objects)
    report['neutral_max_basis_error']=max(abs(p.matrix_basis[i][j]-(1 if i==j else 0)) for p in rig.pose.bones for i in range(4) for j in range(4))
    assert report['neutral_max_basis_error']<1e-5
    # Preserve only generated UI scripts; all custom scripts remain external.
    for filename in ('Architecture.md','AnimatorGuide.md'):
        text=bpy.data.texts.get(filename) or bpy.data.texts.new(filename)
        text.clear(); text.write((ROOT/'docs'/filename).read_text())
    rig['README']='See AnimatorGuide.md in Text Editor or E:/RepairRig/docs. Pose the generated RepairRig; edit the hidden metarig only for generation.'
    rig['Initial_IK_settings']='Arms/legs: IK_FK=0, IK_Stretch=0, pole_vector=True. Recheck after regeneration.'
    meta['RepairRig_regeneration_note']='Same Rigify/schema; preserve names. Recheck IK defaults, skin, drivers, Actions and external constraints after regeneration.'
    meta.hide_set(True)
    for p in rig.pose.bones: p.select=False
    rig.pose.bones['torso'].select=True; rig.data.bones.active=rig.data.bones['torso']
    bpy.context.scene.frame_end=120
    out=ROOT/'blend/RepairRig_02_ControlRig.blend'; assert not out.exists()
    bpy.ops.wm.save_as_mainfile(filepath=str(out))
    report['checkpoint']=str(out); report['pass']=True
    (ROOT/'tests/final_validation.json').write_text(json.dumps(report,indent=2))
    # This file records the actual final settings, which differ from generation defaults.
    (ROOT/'docs/control_manifest.json').write_text(json.dumps({
        'schema':'1.0','rigify_version':'0.6.10','blender':bpy.app.version_string,
        'bones':[{'name':p.name,'parent':p.parent.name if p.parent else None,
                  'rotation_mode':p.rotation_mode,'collections':[c.name for c in p.bone.collections],
                  'properties':{k:p[k] for k in p.keys() if isinstance(p[k],(str,int,float,bool))}}
                 for p in rig.pose.bones if not p.name.startswith(('ORG-','MCH-','DEF-','VIS-'))]},indent=2))
if bpy.data.objects.get('RepairRig'):
    try: main()
    except Exception:
        (ROOT/'tests/finalize_exception.txt').write_text(traceback.format_exc()); raise
