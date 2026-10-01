import sys,collections
sys.path.insert(0,'E:/RepairRig/scripts')
from hand_polish_common import *
r,m=load();prep=prepare(m);selected=set(i for t in prep[0] for i in t);coords={i:r.matrix_world.inverted()@m.matrix_world@m.data.vertices[i].co for i in selected}
polys=[p for p in m.data.polygons if all(i in selected for i in p.vertices)]
edges=collections.Counter(tuple(sorted((p.vertices[i],p.vertices[(i+1)%len(p.vertices)]))) for p in polys for i in range(len(p.vertices)))
metas=[o for o in bpy.data.objects if o.type=='ARMATURE' and 'metarig' in o.name.lower()]
report={'hand_polygon_sizes':dict(collections.Counter(len(p.vertices) for p in polys)),'hand_vertices':len(selected),'unique_positions_1um':len(set(tuple(round(v,6) for v in p) for p in coords.values())),'boundary_edges_in_hand_selection':sum(n==1 for n in edges.values()),'nonmanifold_edges_over2':sum(n>2 for n in edges.values()),'metarigs':[o.name for o in metas],'joints':{}}
for f in F:
 for j in (1,2,3):
  b=r.data.bones['DEF-'+f+'.%02d.R'%j];axis=(b.tail_local-b.head_local).normalized();near=[p for i,p in coords.items() if prep[2][i]==f and abs((p-b.head_local).dot(axis))<.0025]
  radii=sorted((p-b.head_local-axis*(p-b.head_local).dot(axis)).length for p in near)
  row={'near_joint_vertices':len(near),'section_radius_median':radii[len(radii)//2] if radii else None,'length':b.length}
  if near:
   center=sum(near,Vector())/len(near);row['section_center_offset']=(center-b.head_local-axis*(center-b.head_local).dot(axis)).length
  for meta in metas:
   n=f+'.%02d.R'%j
   if n in meta.data.bones:
    mb=meta.data.bones[n];row['meta_head_error']=(r.matrix_world@b.head_local-meta.matrix_world@mb.head_local).length;row['meta_tail_error']=(r.matrix_world@b.tail_local-meta.matrix_world@mb.tail_local).length
  left=r.data.bones.get('DEF-'+f+'.%02d.L'%j)
  if left:
   mirror=b.head_local.copy();mirror.x=-mirror.x;row['mirror_head_error']=(mirror-left.head_local).length;row['mirror_length_error']=abs(left.length-b.length)
  if j<3:row['next_segment_x_axis_angle_degrees']=math.degrees(b.matrix_local.to_3x3().col[0].angle(r.data.bones['DEF-'+f+'.%02d.R'%(j+1)].matrix_local.to_3x3().col[0]))
  report['joints'][f+'.'+str(j)]=row
(OUT/'topology_fit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
