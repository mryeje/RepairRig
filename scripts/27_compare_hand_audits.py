"""Compare non-saving scene audits; does not open or modify blend files."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tests/hand_transfer'
a = json.loads((OUT / 'canonical_current.json').read_text())
b = json.loads((OUT / 'production.json').read_text())

def dot(u, v):
    return sum(x*y for x, y in zip(u, v))

def unit(v):
    length = math.sqrt(dot(v, v))
    return [x/length for x in v]

def angle(u, v):
    return math.degrees(math.acos(max(-1, min(1, dot(unit(u), unit(v))))))

def cross(u, v):
    return [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]

def axis(matrix, column):
    return unit([matrix[i][column] for i in range(3)])

x = a['armatures']['RepairRig']
y = b['armatures']['RepairRig']
result = {'canonical_sha256': a['sha256'], 'production_sha256': b['sha256'],
          'drivers_equal': x['drivers'] == y['drivers'], 'assets': {}, 'fingers': {}}
for name, asset in a['pose_assets'].items():
    other = b['pose_assets'].get(name)
    result['assets'][name] = {'curves_equal': bool(other and asset['curves'] == other['curves']),
                             'canonical_asset': asset['is_asset'],
                             'production_asset': other['is_asset'] if other else None}
for finger in ['f_index', 'f_middle', 'f_ring', 'f_pinky', 'thumb']:
    name = finger + '.01_master.R'
    r, s = [z['bones'][name]['rest_in_palm'] for z in [x, y]]
    # Minimal rotation transports the canonical chain direction to production.
    # Residual X-axis difference separates bend-plane change from chain aim.
    u, v, normal = axis(r, 1), axis(s, 1), axis(r, 0)
    k = cross(u, v)
    c = dot(u, v)
    assert c > -0.99999, 'Antiparallel chain needs explicit transport choice'
    first = cross(k, normal)
    second = cross(k, first)
    transported = [normal[i]+first[i]+second[i]/(1+c) for i in range(3)]
    data = {'chain_direction_degrees': angle(u, v),
            'transported_bend_axis_degrees': angle(transported, axis(s, 0)),
            'raw_axis_angles_degrees': [angle(axis(r, i), axis(s, i)) for i in range(3)],
            'tip_samples': {}}
    for label, rig in [('canonical', x), ('production', y)]:
        samples = rig['samples'][finger]
        tip = 'DEF-' + finger + '.03.R'
        start = samples['1'][tip]['tail_in_hand']
        end = samples['0.58'][tip]['tail_in_hand']
        data['tip_samples'][label] = {'open': start, 'scale_058': end,
                                     'delta': [q-p for p, q in zip(start, end)]}
    result['fingers'][finger] = data
(OUT / 'comparison.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
