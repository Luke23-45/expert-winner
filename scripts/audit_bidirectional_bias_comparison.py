from __future__ import annotations
import json
import random
from fractions import Fraction as F
from pathlib import Path

# Exact fixed Top-2 plant from the strict-margin search.
A = [
    [F('0.819180'), F('1.028240'), F('0.056863'), F('-0.175017')],
    [F('1.160296'), F('0.072379'), F('-0.139075'), F('1.158428')],
    [F('-0.002522'), F('1.170735'), F('0.186723'), F('0.836694')],
    [F('0.022639'), F('1.145491'), F('-0.166813'), F('0.971930')],
    [F('0.040438'), F('0.897060'), F('0.196673'), F('0.937628')],
    [F('0.015482'), F('0.153365'), F('0.812693'), F('0.913671')],
    [F('0.187260'), F('-0.087490'), F('0.845061'), F('0.929071')],
    [F('-0.097150'), F('0.118014'), F('0.859227'), F('0.800792')],
]
E, K, T = 4, 2, 8
C = [1, 2, 3, 3]
GAMMA = F(1, 100)
H = 34

def route(scores):
    order = sorted(range(E), key=lambda e: (-scores[e], e))
    return order[:K], scores[order[K-1]] - scores[order[K]]

def run(sensor, replicate=1, entry_noise=None, horizon=H):
    affinities = [[x for x in row] for row in A]
    if entry_noise is not None:
        affinities = [[x + entry_noise[t][e] for e, x in enumerate(row)] for t, row in enumerate(A)]
    # replication repeats each row and scales capacities, preserving feedback signs
    batch = [row[:] for row in affinities for _ in range(replicate)]
    caps = [c * replicate for c in C]
    b = [F(0) for _ in range(E)]
    counts_history, margins, overflows, biases = [], [], [], []
    for step in range(horizon):
        counts = [0] * E
        step_margin = None
        for row in batch:
            chosen, margin = route([row[e] + b[e] for e in range(E)])
            for e in chosen:
                counts[e] += 1
            step_margin = margin if step_margin is None else min(step_margin, margin)
        admitted = [min(counts[e], caps[e]) for e in range(E)]
        overflow = sum(counts) - sum(admitted)
        obs = counts if sensor == 'requested' else admitted
        avg = F(sum(obs), E)
        u = [0] * E if sensor == 'none' else [1 if avg > x else -1 if avg < x else 0 for x in obs]
        raw = [b[e] + GAMMA * u[e] for e in range(E)]
        mean = sum(raw, F(0)) / E
        b = [x - mean for x in raw]
        counts_history.append(counts)
        margins.append(step_margin)
        overflows.append(overflow)
        biases.append(b[:])
    return {
        'sensor': sensor,
        'counts': counts_history,
        'overflow': overflows,
        'cumulative_overflow': sum(overflows),
        'minimum_cutoff_margin': min(margins),
        'minimum_cutoff_margin_H34': min(margins[:H]),
        'all_routes_strict': all(x > 0 for x in margins),
        'bias': biases,
        'first_unsaturated_step': next((i for i, r in enumerate(counts_history) if any(r[e] < C[e] * replicate for e in range(E))), None),
    }

admitted = run('admitted', horizon=47)
requested = run('requested', horizon=47)
none = run('none')
# Independent check of exact mass and clipping identities along saved trajectories.
assert all(sum(r) == K*T for r in admitted['counts'] + requested['counts'] + none['counts'])
assert admitted['all_routes_strict'] and requested['all_routes_strict']
assert admitted['counts'][0] == [2,4,3,7]
assert requested['counts'][0] == [2,4,3,7]
assert admitted['counts'][33] == [3,5,1,7]
assert all(requested['counts'][33][e] >= C[e] for e in range(E))
assert admitted['first_unsaturated_step'] == 33
assert requested['first_unsaturated_step'] == 46
assert admitted['overflow'][33] == 9
assert requested['overflow'][33] == 7
assert sum(admitted['overflow'][:H]) == 240
assert sum(requested['overflow'][:H]) == 238
assert none['cumulative_overflow'] == 238
assert admitted['minimum_cutoff_margin_H34'] == F(21,31250)
assert requested['minimum_cutoff_margin_H34'] == F(9971,1000000)

# Prove strict-open-neighborhood robustness by sufficient perturbation bound:
# any entrywise affinity perturbation <= eps changes any pairwise score gap by <=2eps.
eps = F(1,10000)
min_margin = min(admitted['minimum_cutoff_margin_H34'], requested['minimum_cutoff_margin_H34'])
assert 2*eps < min_margin

# Exact random perturbation audit inside the analytically certified open ball.
rng = random.Random(20261017)
perturbation_trials = 100
for _ in range(perturbation_trials):
    noise = [[F(rng.choice((-1, 0, 1)), 10000) for _ in range(E)] for _ in range(T)]
    perturbed_admitted = run('admitted', entry_noise=noise, horizon=H)
    perturbed_requested = run('requested', entry_noise=noise, horizon=H)
    assert perturbed_admitted['counts'] == admitted['counts'][:H]
    assert perturbed_requested['counts'] == requested['counts'][:H]
    assert sum(perturbed_admitted['overflow']) == 240
    assert sum(perturbed_requested['overflow']) == 238

# Scale by replication m: score paths, signs, and biases remain unchanged; counts/costs scale by m.
replications = {}
for m in (1, 2, 5, 10):
    x = run('admitted', replicate=m, horizon=47)
    y = run('requested', replicate=m, horizon=47)
    assert x['minimum_cutoff_margin_H34'] == admitted['minimum_cutoff_margin_H34']
    assert y['minimum_cutoff_margin_H34'] == requested['minimum_cutoff_margin_H34']
    assert sum(x['overflow'][:H]) == 240*m
    assert sum(y['overflow'][:H]) == 238*m
    assert x['bias'] == admitted['bias'] and y['bias'] == requested['bias']
    replications[str(m)] = {'admitted_cumulative_overflow': sum(x['overflow'][:H]), 'requested_cumulative_overflow': sum(y['overflow'][:H]), 'difference': sum(x['overflow'][:H]) - sum(y['overflow'][:H])}

out = {
  'exact_arithmetic': True,
  'plant': {'E':E,'K':K,'T':T,'capacities':C,'gamma':str(GAMMA),'horizon_batches':H,'tie_rule':'stable descending score; lower expert index wins exact ties'},
  'admitted': {'initial_R': admitted['counts'][0], 'R_at_33': admitted['counts'][33], 'first_unsaturated_step': admitted['first_unsaturated_step'], 'overflow_at_33': admitted['overflow'][33], 'cumulative_overflow_H34': sum(admitted['overflow'][:H]), 'minimum_cutoff_margin_states_0_to_33': str(admitted['minimum_cutoff_margin_H34']), 'strict_all_states': admitted['all_routes_strict']},
  'requested': {'initial_R': requested['counts'][0], 'R_at_33': requested['counts'][33], 'first_unsaturated_step': requested['first_unsaturated_step'], 'overflow_at_33': requested['overflow'][33], 'cumulative_overflow_H34': sum(requested['overflow'][:H]), 'minimum_cutoff_margin_states_0_to_33': str(requested['minimum_cutoff_margin_H34']), 'strict_all_states': requested['all_routes_strict']},
  'no_feedback_cumulative_overflow_H34': none['cumulative_overflow'],
  'robustness': {'entrywise_affinity_perturbation_epsilon':str(eps),'minimum_margin_both_arms':str(min_margin),'twice_epsilon':str(2*eps),'same_route_paths_guaranteed_by_margin_induction':True,'exact_random_perturbation_trials':perturbation_trials,'exact_random_perturbation_seed':20261017,'all_trials_preserved_both_trajectories_and_costs':True},
  'replication_family':replications,
}
path = Path('results/bidirectional_bias_comparison/strict_requested_better_witness.json')
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
print(json.dumps(out, indent=2))





