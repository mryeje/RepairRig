"""Native linked-model availability test, no scene writes."""
import bpy,json
from pathlib import Path
LIB=Path('E:/BlenderAssets/RepairRig');report={}
for file,name in [('RepairRig_Screwdriver.blend','RepairRig_Tool_Screwdriver'),('RepairRig_Pliers.blend','RepairRig_Tool_Pliers')]:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 result=bpy.ops.wm.link(directory=str(LIB/'Tools'/file)+'/Collection/',filename=name,instance_collections=True)
 c=bpy.data.collections[name];row={'result':list(result),'linked':bool(c.library),'meshes':sum(o.type=='MESH' for o in c.all_objects),'armatures_imported':sum(o.type=='ARMATURE' for o in bpy.data.objects),'instances':sum(o.instance_collection==c for o in bpy.context.scene.objects)}
 assert result=={'FINISHED'} and row['linked'] and row['meshes'] and row['armatures_imported']==0 and row['instances']==1
 report[name]=row
report['scope']='Static linked Collection model instances only; interactive wrapper overrides are not certified.';report['pass']=True
(Path('E:/RepairRig/tests/library')/'linked_models_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
