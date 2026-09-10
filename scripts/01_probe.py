"""Run in a new visible Blender: blender.exe --python scripts/01_probe.py."""
import bpy, addon_utils, json, traceback
from pathlib import Path
ROOT = Path('E:/RepairRig')
for folder in ('blend','scripts','assets/tools','assets/characters','references','renders','docs','tests'):
    (ROOT / folder).mkdir(parents=True, exist_ok=True)
def run():
    try:
        addon_utils.enable('rigify', default_set=False, persistent=True)
        import rigify
        bpy.ops.object.armature_human_metarig_add()
        meta = bpy.context.object
        result = {'version': bpy.app.version_string, 'background': bpy.app.background,
                  'rigify': rigify.__file__, 'bones': [{'name': p.name, 'type': p.rigify_type} for p in meta.pose.bones],
                  'action_properties': list(bpy.types.Action.bl_rna.properties.keys()),
                  'nla_properties': list(bpy.types.NlaStrip.bl_rna.properties.keys()),
                  'pose_asset_operators': [n for n in dir(bpy.ops.poselib) if not n.startswith('_')]}
        (ROOT/'tests/environment.json').write_text(json.dumps(result, indent=2))
        bpy.data.objects.remove(meta, do_unlink=True)
    except Exception:
        (ROOT/'tests/probe_error.txt').write_text(traceback.format_exc())
    return None
bpy.app.timers.register(run, first_interval=2)
