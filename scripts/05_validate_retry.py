import bpy,runpy,traceback
from pathlib import Path
if bpy.data.objects.get('RepairRig'):
    try:
        runpy.run_path('E:/RepairRig/scripts/05_refresh_face_drivers.py',run_name='__main__')
    except Exception:
        Path('E:/RepairRig/tests/validation_exception.txt').write_text(traceback.format_exc())
        raise
