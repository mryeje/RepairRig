"""Give collection packages clean editable scenes and persistent custom thumbnails."""
import bpy,json,hashlib
from pathlib import Path
LIB=Path('E:/BlenderAssets/RepairRig');OUT=Path('E:/RepairRig/tests/library/previews')
manifest=json.loads((LIB/'Docs/Library_Manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for item in [a for a in manifest['assets'] if a['type']=='Collection']:
 path=LIB/item['file'];key=next(k for k in manifest['files'] if k.replace('\\','/')==item['file']);assert sha(path)==manifest['files'][key]['sha256']
 bpy.ops.wm.open_mainfile(filepath=str(path),use_scripts=False)
 c=bpy.data.collections[item['name']]
 if c.name not in bpy.context.scene.collection.children:bpy.context.scene.collection.children.link(c)
 with bpy.context.temp_override(id=c):result=bpy.ops.ed.lib_id_load_custom_preview(filepath=str(OUT/(c.name+'.png')))
 print('PREVIEW_BEFORE_SAVE',c.name,result,list(c.preview.image_size) if c.preview else None,flush=True)
 s=bpy.context.scene;s.name='RepairRig Asset Source';s.render.filepath='//Preview_';s.render.engine='BLENDER_WORKBENCH'
 if item['catalog']=='Character':
  r=bpy.data.objects['RepairRig'];bpy.context.view_layer.objects.active=r;r.select_set(True)
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True,relative_remap=True)
 manifest['files'][key]={'bytes':path.stat().st_size,'sha256':sha(path)}
(LIB/'Docs/Library_Manifest.json').write_text(json.dumps(manifest,indent=2))
