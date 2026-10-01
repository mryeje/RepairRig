"""Surface diagnostics for hand/prop fits; no scene modifications."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def contact_metrics(mesh,prepared,names):
 dg=bpy.context.evaluated_depsgraph_get();ev=mesh.evaluated_get(dg);me=ev.to_mesh();hv=[mesh.matrix_world@v.co for v in me.vertices];ht=BVHTree.FromPolygons(hv,prepared[0],all_triangles=True);results={}
 for name in names:
  o=bpy.data.objects[name].evaluated_get(dg);m=o.to_mesh();m.calc_loop_triangles();verts=[o.matrix_world@v.co for v in m.vertices];tris=[tuple(t.vertices) for t in m.loop_triangles];tree=BVHTree.FromPolygons(verts,tris,all_triangles=True);regions={}
  for i in set(v for t in prepared[0] for v in t):
   p=hv[i];co,no,idx,dist=tree.find_nearest(p);region=prepared[2][i];row=regions.setdefault(region,{'min_surface_gap':1e9,'inside_vertices':0,'max_depth':0.})
   row['min_surface_gap']=min(row['min_surface_gap'],dist)
   if dist<1e-5:continue
   votes=0
   for vec in [(1,.371,.217),(.173,1,.419),(.293,.137,1)]:
    direction=Vector(vec).normalized();origin=p.copy();hits=0
    for _ in range(20):
     hit,_,_,_=tree.ray_cast(origin,direction)
     if hit is None:break
     hits+=1;origin=hit+direction*1e-6
    votes+=hits%2
   if votes>=2:row['inside_vertices']+=1;row['max_depth']=max(row['max_depth'],dist)
  results[name]={'surface_intersections':len(ht.overlap(tree)),'regions':regions};o.to_mesh_clear()
 ev.to_mesh_clear();return results
