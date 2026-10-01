"""Disposable GUI probe of native external Asset Browser discovery."""
import bpy,json,traceback
from pathlib import Path
OUT=Path('E:/RepairRig/tests/library');LIB='E:/BlenderAssets/RepairRig'
lib=bpy.context.preferences.filepaths.asset_libraries.new(name='RepairRig',directory=LIB)
area=next(a for a in bpy.context.screen.areas if a.type=='PROPERTIES');area.type='FILE_BROWSER';area.ui_type='ASSETS'
report={}
def finish():
 (OUT/'browser_probe.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.quit_blender()
def inspect():
 try:
  with bpy.context.temp_override(area=area,region=next(r for r in area.regions if r.type=='WINDOW')):
   bpy.ops.file.select_all(action='SELECT')
   assets=list(bpy.context.selected_assets)
   report['asset_rna']=[(p.identifier,p.description) for p in assets[0].bl_rna.properties] if assets else []
   report['assets']=[{'name':a.name,'full_library_path':a.full_library_path,'id_type':a.id_type,'local_id':getattr(a.local_id,'name',None)} for a in assets]
   report['params']=str(area.spaces.active.params.asset_library_reference)
 except:report['error']=traceback.format_exc()
 finish()
def setup():
 try:
  p=area.spaces.active.params
  report['enum']=[(e.identifier,e.name,e.value) for e in p.bl_rna.properties['asset_library_reference'].enum_items]
  try:p.asset_library_reference='RepairRig'
  except Exception as e:
   report['set_error']=str(e)
   p.asset_library_reference='ALL'
  bpy.app.timers.register(inspect,first_interval=8)
 except:report['error']=traceback.format_exc();finish()
bpy.app.timers.register(setup,first_interval=2)
