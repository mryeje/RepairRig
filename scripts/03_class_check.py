import bpy, rigify, json, contextlib, io
from pathlib import Path
p=bpy.data.objects['RepairRig_Metarig'].pose.bones['spine'].rigify_parameters
buf=io.StringIO()
with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):
    print('instance',type(p),id(type(p)),list(p.bl_rna.properties.keys()))
    print('module',rigify.RigifyParameters,id(rigify.RigifyParameters),list(rigify.RigifyParameters.bl_rna.properties.keys()))
    print('same',type(p) is rigify.RigifyParameters)
    print('registered',rigify.RigifyParameters.is_registered)
    print('attr',getattr(rigify.RigifyParameters,'make_custom_pivot','MISSING'))
    print('fixed',bpy.types.PoseBone.bl_rna.properties['rigify_parameters'].fixed_type)
    print('subclass',bpy.types.PropertyGroup.bl_rna_get_subclass_py('RigifyParameters'))
Path('E:/RepairRig/tests/class_check.txt').write_text(buf.getvalue())
