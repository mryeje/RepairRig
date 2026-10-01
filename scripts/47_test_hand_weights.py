"""Conservative distal-finger cross-influence cleanup, bounded by grip regression."""
import sys
sys.path.insert(0,'E:/RepairRig/scripts')
from hand_polish_common import *
r,m=load();prep=prepare(m);groups={g.index:g.name for g in m.vertex_groups};indices={g.name:g.index for g in m.vertex_groups}
original={v.index:{g.group:g.weight for g in v.groups} for v in m.data.vertices}
def segment_distance(p,a,b):
 t=max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared));return (p-(a+(b-a)*t)).length
chains={f:[r.data.bones['DEF-'+f+'.%02d.R'%j] for j in (1,2,3)] for f in F}
proposal={};audit=[]
for v in m.data.vertices:
 f=prep[2][v.index]
 if f not in F:continue
 p=r.matrix_world.inverted()@m.matrix_world@v.co;bs=chains[f]
 along=(p-bs[0].head_local).dot((bs[0].tail_local-bs[0].head_local).normalized())/bs[0].length
 # Leave palm, webs, MCP and thumb base untouched.
 if along<.55:continue
 d=min(segment_distance(p,b.head_local,b.tail_local) for b in bs)
 other=min(segment_distance(p,b.head_local,b.tail_local) for ff in F if ff!=f for b in chains[ff])
 if d>.019 or other<d*1.25:continue
 weights=original[v.index];foreign=[i for i in weights if any(ff in groups[i] for ff in F if ff!=f)]
 foreign_sum=sum(weights[i] for i in foreign)
 if foreign_sum<.005:continue
 own=[i for i in weights if 'DEF-'+f+'.' in groups[i]];own_sum=sum(weights[i] for i in own)
 if own_sum<.45:continue
 fade=min(1,(along-.55)/.3)
 new=dict(weights)
 for i in foreign:new[i]=weights[i]*(1-fade)
 for i in own:new[i]+=foreign_sum*fade*weights[i]/own_sum
 deform=[i for i in new if groups[i] in r.data.bones and r.data.bones[groups[i]].use_deform];total=sum(new[i] for i in deform)
 for i in deform:new[i]/=total
 proposal[v.index]=new;audit.append({'vertex':v.index,'finger':f,'foreign_before':foreign_sum,'along':along})
def setweights(changes):
 for vid,ws in changes.items():
  for i,w in ws.items():m.vertex_groups[i].add([vid],w,'REPLACE')
 m.data.update();update()
pose('Grip_Screwdriver');before=evaluated(m);setweights(proposal);after=evaluated(m)
# Cap the cleanup at 0.35 mm movement in the established screwdriver grip.
bounded={};caps={}
for vid,new in proposal.items():
 dist=(after[vid]-before[vid]).length;strength=min(1,.00035/max(dist,1e-12));caps[vid]=strength
 bounded[vid]={i:original[vid].get(i,0)+(w-original[vid].get(i,0))*strength for i,w in new.items()}
setweights(bounded)
report={'candidate_vertices':len(proposal),'full_cleanup_vertices':sum(s==1 for s in caps.values()),'minimum_strength':min(caps.values(),default=1),'audit':audit,'poses':{}}
for short in POSES:
 pose(short);report['poses'][short]=metrics(r,m,prep)
 if short.startswith('Grip_'):report['poses'][short]['contact']=contact_metrics(m,prep,['Screwdriver_Handle'] if short=='Grip_Screwdriver' else ['Pliers_Handle_-1','Pliers_Handle_1'])
 render_hand(r,m,prep,'weight_trial_'+short,'Pliers_' if short=='Grip_Pliers' else 'Screwdriver_' if short=='Grip_Screwdriver' else None,'side')
 print('TRIAL',short,report['poses'][short]['self_intersection_triangle_pairs'],flush=True)
(OUT/'weight_trial.json').write_text(json.dumps(report,indent=2));(OUT/'weight_changes_right.json').write_text(json.dumps({str(v):{groups[i]:{'before':original[v].get(i,0),'after':w} for i,w in ws.items()} for v,ws in bounded.items()},indent=2))
print('WEIGHT_CANDIDATES',len(proposal),'full',report['full_cleanup_vertices'],flush=True)
