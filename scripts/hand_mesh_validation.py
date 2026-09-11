"""Disposable evaluated-mesh validation, never saves scenes."""
import bpy, math, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
F=['f_index','f_middle','f_ring','f_pinky','thumb']
def prepare(mesh):
 names={g.index:g.name for g in mesh.vertex_groups}
 weights=[];regions=[];selected=set()
 for v in mesh.data.vertices:
  by={}
  for g in v.groups:
   n=names[g.group]
   if n.endswith('.R') and (any(f in n for f in F) or 'hand' in n or 'palm' in n):
    region=next((f for f in F if f in n),'palm');by[region]=by.get(region,0)+g.weight
  regions.append(max(by,key=by.get) if by else 'other')
  if sum(by.values())>.25:selected.add(v.index)
 mesh.data.calc_loop_triangles()
 tris=[tuple(t.vertices) for t in mesh.data.loop_triangles if all(i in selected for i in t.vertices)]
 labels=[max(set(regions[i] for i in t),key=lambda n:sum(regions[i]==n for i in t)) for t in tris]
 return tris,labels,regions

def inspect_pose(r,mesh,prepared):
 dg=bpy.context.evaluated_depsgraph_get();em=mesh.evaluated_get(dg).to_mesh();verts=[mesh.matrix_world@v.co for v in em.vertices];tris,labels,regions=prepared
 tree=BVHTree.FromPolygons(verts,tris,all_triangles=True,epsilon=0)
 pairs=[];categories={}
 for i,j in tree.overlap(tree):
  if i>=j or set(tris[i])&set(tris[j]):continue
  # Exclude coincident seam duplicates from separate topology islands.
  if any((verts[a]-verts[b]).length<1e-6 for a in tris[i] for b in tris[j]):continue
  key='/'.join(sorted([labels[i],labels[j]]));categories[key]=categories.get(key,0)+1;pairs.append((i,j))
 ep=r.evaluated_get(dg).pose.bones;hand=(r.matrix_world@ep['DEF-hand.R'].matrix).inverted()
 tips={f:list(hand@(r.matrix_world@ep['DEF-'+f+'.03.R'].tail)) for f in F}
 directions={f:list((hand.to_3x3()@r.matrix_world.to_3x3()@(ep['DEF-'+f+'.03.R'].tail-ep['DEF-'+f+'.03.R'].head)).normalized()) for f in F}
 thumb=Vector(tips['thumb']);index=Vector(tips['f_index'])
 out={'self_intersection_triangle_pairs':len(pairs),'intersection_categories':categories,'tips_in_hand':tips,'tip_directions_in_hand':directions,'thumb_index_tip_distance':(thumb-index).length}
 mesh.evaluated_get(dg).to_mesh_clear();return out
