"""Use --factory-startup RepairRig_01_RigifySetup.blend --python this file.
Enable Rigify for this session; do not save global user preferences.
"""
import bpy, addon_utils, runpy
addon_utils.enable('rigify',default_set=True,persistent=True)
runpy.run_path('E:/RepairRig/scripts/visible_runner.py',run_name='__main__')
