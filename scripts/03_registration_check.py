import bpy, rigify, contextlib, io, runpy
from pathlib import Path
buf=io.StringIO()
with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):
    rigify.register_rig_parameters()
Path('E:/RepairRig/tests/registration.txt').write_text(buf.getvalue())
runpy.run_path('E:/RepairRig/scripts/03_generate.py',run_name='__main__')
