"""Validate existing Stage 3 files in an isolated UI session; never rebuild them."""
import bpy, json, runpy, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def execute():
    try:
        runpy.run_path(str(ROOT/'tests/validate_stage3_reopen.py'), run_name='__main__')
        runpy.run_path(str(ROOT/'tests/validate_stage3_components.py'), run_name='__main__')
        scene = bpy.context.scene
        scene.render.filepath = str(ROOT/'renders/stage3_reopened.jpg')
        bpy.ops.render.render(write_still=True)
        result = {'pass': True, 'reopen': 'tests/stage3_reopen_validation.json',
                  'components': 'tests/stage3_component_validation.json',
                  'render': 'renders/stage3_reopened.jpg'}
    except Exception:
        result = {'pass': False, 'traceback': traceback.format_exc()}
    (ROOT/'tests/stage3_fresh_session.json').write_text(json.dumps(result, indent=2))
    bpy.app.timers.register(lambda: bpy.ops.wm.quit_blender() and None, first_interval=1)

bpy.app.timers.register(execute, first_interval=2)
