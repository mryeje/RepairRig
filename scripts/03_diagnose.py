import bpy, rigify, json
from pathlib import Path
from rigify.rigs.spines.basic_spine import Rig
p=bpy.data.objects['RepairRig_Metarig'].pose.bones['spine'].rigify_parameters
Path('E:/RepairRig/tests/rigify_diagnose.json').write_text(json.dumps({
 'rigs':list(rigify.rig_lists.rigs), 'params':list(p.bl_rna.properties.keys()),
 'class':str(Rig), 'method':str(Rig.add_parameters),
 'table':list(rigify.RIGIFY_PARAMETER_TABLE)},indent=2))
