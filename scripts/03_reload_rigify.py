import bpy, addon_utils, runpy
# Refresh the add-on through Blender's standard add-on lifecycle. No source edits.
addon_utils.disable('rigify', default_set=False)
addon_utils.enable('rigify', default_set=False, persistent=True)
meta=bpy.data.objects['RepairRig_Metarig']
assert hasattr(meta.pose.bones['spine'].rigify_parameters,'make_custom_pivot')
runpy.run_path('E:/RepairRig/scripts/03_generate.py',run_name='__main__')
