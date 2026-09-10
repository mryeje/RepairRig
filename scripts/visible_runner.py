"""Development-only script runner, not part of the rig or animation system.

Launch with Blender --python (never --background). Submit a JSON object with
unique id and relative script path in scripts/job.json. Executes only project
scripts, once per id in this session; records exceptions. Remove the timer by
restarting Blender. Does not listen on a network socket.
"""
import bpy, json, traceback, runpy
from pathlib import Path
ROOT = Path('E:/RepairRig')
seen = set()
def poll():
    jobfile = ROOT/'scripts/job.json'
    if jobfile.exists():
        job = json.loads(jobfile.read_text())
        if job['id'] not in seen:
            seen.add(job['id'])
            path = (ROOT/job['script']).resolve()
            result = {'id': job['id'], 'script': str(path)}
            try:
                assert path.is_relative_to(ROOT/'scripts') or path.is_relative_to(ROOT/'tests')
                runpy.run_path(str(path), run_name='__main__')
                result['status'] = 'ok'
            except Exception:
                result.update(status='error', traceback=traceback.format_exc())
            (ROOT/'tests'/('job_'+job['id']+'.json')).write_text(json.dumps(result, indent=2))
    return 1.0
bpy.app.timers.register(poll, first_interval=3, persistent=True)
