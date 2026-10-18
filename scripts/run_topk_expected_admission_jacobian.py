#!/usr/bin/env python3
"""Exact synthetic audit of clipped expected Top-1 feedback derivatives."""
from __future__ import annotations
import csv, hashlib, json, math
from fractions import Fraction
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'docs/paper/topk_expected_admission_jacobian_protocol_2026-10-17.md'
OUT=ROOT/'results/topk_expected_admission_jacobian'
PROFILES={
    'uniform':(1/3,1/3,1/3),
    'witness':(1/2,1/3,1/6),
    'strong_skew':(2/3,1/4,1/12),
}
TOTALS=(6,12,24,48,96,192)
CAPACITY_RATIOS=(Fraction(1,6),Fraction(1,3),Fraction(1,2),Fraction(1,1))
MU=np.full(3,1/3,dtype=np.float64)
P0=np.eye(3)-np.ones((3,3))/3
U=np.array([1.,0.,-1.])
V=np.array([0.,1.,-1.])
EPS=1e-5


def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def binpmf(n:int,p:float,k:int)->float:
    if k<0 or k>n: return 0.0
    if p==0: return float(k==0)
    if p==1: return float(k==n)
    return math.comb(n,k)*(p**k)*((1-p)**(n-k))


def alpha(T:int,C:int,p:float)->float:
    return math.fsum(binpmf(T-1,p,j) for j in range(C))


def clipped_mean(T:int,C:int,p:float)->float:
    # E[min(X,C)] = sum_{j=1}^C P(X >= j).
    return math.fsum(math.fsum(binpmf(T,p,k) for k in range(j,T+1)) for j in range(1,C+1))


def softmax_negq(q:np.ndarray)->np.ndarray:
    z=-q-np.max(-q)
    e=np.exp(z)
    return e/e.sum()


def q_for_p(p:np.ndarray)->np.ndarray:
    q=-np.log(p)
    return q-q.min()


def field(q:np.ndarray,T:int,C:int)->np.ndarray:
    p=softmax_negq(q)
    m=np.array([clipped_mean(T,C,float(x)) for x in p])
    return P0@(m/T-MU)


def analytic(q:np.ndarray,T:int,C:int)->tuple[np.ndarray,np.ndarray,np.ndarray]:
    p=softmax_negq(q)
    al=np.array([alpha(T,C,float(x)) for x in p])
    dp=-np.diag(p)+np.outer(p,p)
    jac=P0@np.diag(al)@dp
    return p,al,jac


def quotient_curl(jac:np.ndarray)->float:
    return float(U@jac@V-V@jac@U)


def fd_jac(q:np.ndarray,T:int,C:int)->np.ndarray:
    eye=np.eye(3)
    return np.column_stack([(field(q+EPS*eye[:,j],T,C)-field(q-EPS*eye[:,j],T,C))/(2*EPS) for j in range(3)])


def exact_witness()->tuple[tuple[Fraction,...],Fraction]:
    T,C=6,2
    probs=(Fraction(1,2),Fraction(1,3),Fraction(1,6))
    alphas=tuple(sum((Fraction(math.comb(T-1,j))*x**j*(1-x)**(T-1-j)
                      for j in range(C)),Fraction(0)) for x in probs)
    h12=probs[0]*probs[1]
    h13=probs[0]*probs[2]
    h23=probs[1]*probs[2]
    curl=((alphas[0]-alphas[1])*h12
          -(alphas[0]-alphas[2])*h13
          +(alphas[1]-alphas[2])*h23)
    assert alphas==(Fraction(3,16),Fraction(112,243),Fraction(3125,3888))
    assert curl==Fraction(-29,2187)
    return alphas,curl


def main()->None:
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[]
    for profile,praw in PROFILES.items():
        p0=np.array(praw,dtype=np.float64)
        q=q_for_p(p0)
        for T in TOTALS:
            for ratio in CAPACITY_RATIOS:
                c=int(ratio*T)
                assert c>=1 and c<=T and Fraction(c,T)==ratio
                p,al,jac=analytic(q,T,c)
                jac_fd=fd_jac(q,T,c)
                err=float(np.max(np.abs(jac-jac_fd)))
                curl=quotient_curl(jac)
                curl_fd=quotient_curl(jac_fd)
                assert np.max(np.abs(p-p0))<1e-14
                assert err<2e-7,(profile,T,c,err)
                rows.append({
                    'profile':profile,'E':3,'K':1,'T':T,'C_per_expert':c,
                    'capacity_fraction':str(ratio),'p1':float(p[0]),'p2':float(p[1]),'p3':float(p[2]),
                    'alpha1':float(al[0]),'alpha2':float(al[1]),'alpha3':float(al[2]),
                    'curl_analytic':curl,'curl_finite_difference':curl_fd,
                    'max_jacobian_fd_error':err,
                })
    # Locked exact-rational theorem witness.
    witness=next(x for x in rows if x['profile']=='witness' and x['T']==6 and x['C_per_expert']==2)
    exact_alphas,exact_curl=exact_witness()
    target=float(exact_curl)
    assert abs(witness['curl_analytic']-target)<1e-14
    # Symmetry and no-clipping negative controls across all registered T values.
    for row in rows:
        if row['profile']=='uniform': assert abs(row['curl_analytic'])<1e-12
        if row['capacity_fraction']=='1': assert abs(row['curl_analytic'])<1e-12
    # Strict overload attenuation tends to zero and strict underload attenuation to one.
    strong=[x for x in rows if x['profile']=='strong_skew' and x['capacity_fraction']=='1/3']
    assert strong[-1]['alpha1']<strong[0]['alpha1']
    assert strong[-1]['alpha1']<1e-8
    assert strong[-1]['alpha3']>1-1e-8
    out=OUT/'grid.csv'
    with out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summary={
        'protocol':PROTOCOL.relative_to(ROOT).as_posix(),
        'protocol_sha256':sha(PROTOCOL),'script_sha256':sha(Path(__file__)),
        'grid_sha256':sha(out),'cells':len(rows),'profiles':list(PROFILES),
        'T_values':list(TOTALS),'capacity_fractions':[str(x) for x in CAPACITY_RATIOS],
        'max_abs_jacobian_fd_error':max(x['max_jacobian_fd_error'] for x in rows),
        'witness_attenuation_exact':[str(x) for x in exact_alphas],
        'witness_curl_exact':str(exact_curl),'witness_curl_numeric':witness['curl_analytic'],
        'nonzero_clipped_skew_cells':sum(abs(x['curl_analytic'])>1e-10 for x in rows if x['profile']!='uniform' and x['capacity_fraction']!='1'),
        'uniform_curl_controls':sum(abs(x['curl_analytic'])<1e-12 for x in rows if x['profile']=='uniform'),
        'no_clipping_curl_controls':sum(abs(x['curl_analytic'])<1e-12 for x in rows if x['capacity_fraction']=='1'),
        'all_checks_passed':True,
        'interpretation':'Exact deterministic numerical audit of an analytically evaluated synthetic model; not Monte Carlo evidence.',
    }
    summary_path=OUT/'summary.json'
    summary_path.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__': main()
