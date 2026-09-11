import bpy, json, os
from pathlib import Path
out={}
for name in ('quit.blend','RepairRig_02_ControlRig_30100_autosave.blend'):
    path=Path(os.environ['TEMP'])/name
    with bpy.data.libraries.load(str(path)) as (src,dst):
        out[name]={'objects':list(src.objects),'actions':list(src.actions),'scenes':list(src.scenes)}
Path('E:/RepairRig/tests/stage3_recovery_inventory.json').write_text(json.dumps(out,indent=2))
