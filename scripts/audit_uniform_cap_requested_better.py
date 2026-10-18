from __future__ import annotations
import csv, hashlib, json, random, subprocess
from fractions import Fraction as F
from pathlib import Path
import torch

E, K, T, C, H = 8, 2, 128, 32, 120
ALPHA = F(1, 40)
EDGE_COUNTS = (30, 8, 22, 10, 26, 6, 18, 8)
SEED = 5

def make_affinities():
    gen = torch.Generator().manual_seed(SEED)
    x = torch.full((T, E), -2.0, dtype=torch.float64)
    row = 0
    for edge, count in enumerate(EDGE_COUNTS):
        left, right = edge, (edge + 1) % E
        for _ in range(count):
            noise = torch.rand(E, generator=gen, dtype=torch.float64) * 0.02
            x[row] += noise
            x[row, left] = 2.0 + noise[left]
            x[row, right] = 1.8 + noise[right]
            row += 1
    x = x[torch.randperm(T, generator=gen)]
    return [[F(str(v)) for v in row] for row in x.tolist()]

def run(affinities, sensor, horizon=H, replication=1):
    b = [F(0)] * E
    counts_history, overflow, margins = [], [], []
    batch = [row for row in affinities for _ in range(replication)]
    capacity = C * replication
    for _ in range(horizon):
        r = [0] * E
        min_margin = None
        for row in batch:
            order = sorted(range(E), key=lambda e: (-(row[e] + b[e]), e))
            for e in order[:K]:
                r[e] += 1
            margin = (row[order[K-1]] + b[order[K-1]]) - (row[order[K]] + b[order[K]])
            min_margin = margin if min_margin is None else min(min_margin, margin)
        a = [min(v, capacity) for v in r]
        if sensor == 'requested':
            observed = r
        elif sensor == 'admitted':
            observed = a
        else:
            observed = [sum(r) // E] * E
        mean = F(sum(observed), E)
        u = [0] * E if sensor == 'none' else [1 if mean > v else -1 if mean < v else 0 for v in observed]
        z = [b[e] + ALPHA * u[e] for e in range(E)]
        zmean = sum(z, F(0)) / E
        b = [v - zmean for v in z]
        counts_history.append(r)
        overflow.append(sum(r) - sum(a))
        margins.append(min_margin)
    return {'counts': counts_history, 'overflow': overflow, 'cost': sum(overflow), 'min_margin': min(margins), 'all_strict': all(v > 0 for v in margins)}

A_generated = make_affinities()
fixture_path = Path('docs/paper/fixtures/uniform_capacity_seed5_affinities.csv')
with fixture_path.open(newline='', encoding='utf-8') as f:
    A = [[F(v) for v in row] for row in csv.reader(f)]
assert A == A_generated, 'seeded Torch generator no longer matches the exact checked-in fixture'
base = {sensor: run(A, sensor) for sensor in ('admitted','requested','none')}
assert all(sum(r) == K*T for v in base.values() for r in v['counts'])
assert all(v['all_strict'] for v in base.values())
assert {k:v['cost'] for k,v in base.items()} == {'admitted':2449,'requested':1918,'none':1920}
assert base['admitted']['min_margin'] == F(542933344799, 10**16)
assert base['requested']['min_margin'] == F(114112300983, 25*10**14)
# Perturbation radius: pairwise score margins move by at most 2 epsilon.
EPS = F(1,100000)
assert 2*EPS < min(base['admitted']['min_margin'],base['requested']['min_margin'])
# Verify a seeded sample within the analytically certified open neighborhood.
rng=random.Random(20261017)
TRIALS=10
for _ in range(TRIALS):
    perturbed=[[A[t][e]+F(rng.choice((-1,0,1)),100000) for e in range(E)] for t in range(T)]
    for sensor in ('admitted','requested'):
        x=run(perturbed,sensor)
        assert x['counts']==base[sensor]['counts']
        assert x['cost']==base[sensor]['cost']
# Replication invariant: repeat all rows m times and scale every capacity by m.
replication={}
for m in (1,2):
    a=run(A,'admitted',replication=m)
    r=run(A,'requested',replication=m)
    assert a['cost']==2449*m and r['cost']==1918*m
    replication[str(m)]={'admitted_overflow':a['cost'],'requested_overflow':r['cost'],'requested_minus_admitted':r['cost']-a['cost']}
# Write exact affinity data as decimal strings in stable row order.
outdir=Path('results/bidirectional_bias_comparison')
outdir.mkdir(parents=True,exist_ok=True)
affpath=outdir/'uniform_seed5_affinities.csv'
with affpath.open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f)
    for row in A: w.writerow([str(v) for v in row])
affhash=hashlib.sha256(affpath.read_bytes()).hexdigest()
try:
    revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
except Exception:
    revision='unavailable'
summary={
 'status':'PASS', 'exact_arithmetic':'fractions.Fraction over decimal-rational affinity file',
 'plant':{'E':E,'K':K,'T':T,'uniform_capacity':C,'gain':str(ALPHA),'horizon':H,'generator':'ring-pair counts '+str(EDGE_COUNTS)+'; torch CPU float64 uniform noise [0,0.02), seed 5, followed by exact decimal rationalization','tie_rule':'lower expert index wins exact ties'},
 'overflow':{s:base[s]['cost'] for s in base},
 'initial_saturated_expert_count':{s:sum(v>=C for v in base[s]['counts'][0]) for s in base},
 'first_globally_saturated_state':{s:next((i for i,r in enumerate(base[s]['counts']) if all(v>=C for v in r)),None) for s in base},
 'minimum_top2_cutoff_margin':{s:str(base[s]['min_margin']) for s in base},
 'strict_routes_entire_horizon':{s:base[s]['all_strict'] for s in base},
 'requested_minus_admitted_overflow':base['requested']['cost']-base['admitted']['cost'],
 'replication_checks':replication,
 'robustness':{'entrywise_epsilon':str(EPS),'twice_epsilon':str(2*EPS),'strict_margin_guarantee':True,'exact_random_perturbation_trials':TRIALS,'seed':20261017,'all_trials_preserved_paths_and_costs':True},
 'affinity_file':str(fixture_path).replace('\\','/'),'affinity_file_sha256':affhash,'source_revision':revision
}
(outdir/'uniform_cap_requested_better.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
