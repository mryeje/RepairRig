import sys,traceback,runpy
sys.path.insert(0,'E:/RepairRig/scripts')
from stage4_common import *
try:
 report=runpy.run_path(str(OUT/'validate_library.py'))['validate']('reopen_validation')
 report['quit_operator_properties']=[p.identifier for p in bpy.ops.wm.quit_blender.get_rna_type().properties]
 report['sha256']=hashlib.sha256((ROOT/'blend/RepairRig_04_ActionLibrary.blend').read_bytes()).hexdigest()
 (OUT/'reopen_validation.json').write_text(json.dumps(report,indent=2))
except: (OUT/'error_reopen.txt').write_text(traceback.format_exc())
bpy.ops.wm.quit_blender()
