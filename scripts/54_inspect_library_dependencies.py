"""Read-only library boundary and Blender API inventory."""
import bpy,json,hashlib
from pathlib import Path
SRC=Path('E:/RepairRig/blend/RepairRig_05F_ProductionCharacter_HandPolished.blend');OUT=Path('E:/RepairRig/tests/library');OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC),use_scripts=False)
def refs(o):
 result=[]
 for c in o.constraints:result.append({'constraint':c.name,'type':c.type,'target':getattr(getattr(c,'target',None),'name',None),'subtarget':getattr(c,'subtarget',None)})
 if o.animation_data:
  for f in o.animation_data.drivers:result.append({'driver':f.data_path,'expression':f.driver.expression,'targets':[(getattr(t.id,'name',None),t.data_path) for v in f.driver.variables for t in v.targets]})
 return result
def curves(a):return [f for l in a.layers for s in l.strips for sl in a.slots if (b:=s.channelbag(sl)) for f in b.fcurves]
d={'hash':hashlib.sha256(SRC.read_bytes()).hexdigest(),'objects':{},'actions':{},'texts':{},'collections':{},'images':{},'libraries':[l.filepath for l in bpy.data.libraries]}
for o in bpy.data.objects:d['objects'][o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'refs':refs(o),'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,'custom_properties':{k:str(v)[:200] for k,v in o.items() if k!='_RNA_UI'}}
for a in bpy.data.actions:d['actions'][a.name]={'asset':bool(a.asset_data),'slots':[(s.identifier,s.target_id_type) for s in a.slots],'range':list(a.frame_range),'paths':sorted(set(f.data_path for f in curves(a)))}
for t in bpy.data.texts:d['texts'][t.name]={'filepath':t.filepath,'module':t.use_module,'characters':len(t.as_string())}
for c in bpy.data.collections:d['collections'][c.name]=[o.name for o in c.objects]
for i in bpy.data.images:d['images'][i.name]={'filepath':i.filepath,'packed':bool(i.packed_file),'source':i.source}
d['operators']={n:[(p.identifier,p.description) for p in getattr(bpy.ops.wm,n).get_rna_type().properties] for n in ['append','link']}
d['asset_operators']=dir(bpy.ops.asset);d['poselib_operators']=dir(bpy.ops.poselib)
(OUT/'source_inventory.json').write_text(json.dumps(d,indent=2));print(json.dumps({'objects':len(d['objects']),'actions':list(d['actions']),'collections':d['collections'],'texts':d['texts'],'images':d['images']},indent=2),flush=True)
