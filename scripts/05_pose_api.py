import bpy,json
from pathlib import Path
if bpy.data.objects.get('RepairRig'):
    Path('E:/RepairRig/tests/pose_api.json').write_text(json.dumps({p.identifier:p.description for p in bpy.ops.poselib.create_pose_asset.get_rna_type().properties},indent=2))
