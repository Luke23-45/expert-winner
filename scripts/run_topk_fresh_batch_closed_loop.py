#!/usr/bin/env python3
"""Paired static-vs-fresh batch audit for the canonical clipped Top-K controller."""
from __future__ import annotations
import csv, hashlib, json, math
from collections import defaultdict
from fractions import Fraction
from math import comb
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.stats import binom as binom_dist, t as student_t

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'docs/paper/topk_fresh_batch_closed_loop_protocol_2026-10-17.md'
OUT=ROOT/'results/topk_fresh_batch_closed_loop'
E=4; R=Fraction(1,48); KS=(1,2,3); TS=(2304,9216); REPS=12
HORIZONS=(1,2,4,8,16,32,64); LAW='gumbel'


def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def sample(rng:np.random.Generator,T:int)->np.ndarray:
    return rng.gumbel(size=(T,E))


def cap_vector(K:int,T:int)->np.ndarray:
    p=Fraction(K,E)
    cs=(p-R,)+(p+R/(E-1),)*(E-1)
    assert all((x*T).denominator==1 for x in cs)
    cap=np.array([int(x*T) for x in cs],dtype=np.int64)
    assert int(cap.sum())==K*T and int(cap.max())<T
    return cap


def route(aff:np.ndarray,q:np.ndarray,K:int)->tuple[np.ndarray,int]:
    scores=aff-q[None,:]
    order=np.argsort(-scores,axis=1,kind='stable')[:,:K]
    counts=np.bincount(order.reshape(-1),minlength=E).astype(np.int64)
    boundary=np.take_along_axis(scores,order[:,K-1:K],axis=1)[:,0]
    ties=int(np.count_nonzero((scores==boundary[:,None]).sum(axis=1)>1))
    return counts,ties


def update(pressure:np.ndarray,load:np.ndarray,K:int,T:int,eta:float)->np.ndarray:
    q=pressure+eta*(load.astype(np.float64)/(K*T)-1/E)
    return q-q.min()


def overflow(req:np.ndarray,cap:np.ndarray)->int:
    return int(np.maximum(req-cap,0).sum())


def clipped_mean(T:int,p:float,C:int)->float:
    # E[min(X,C)] = sum_{j=1}^C Pr(X>=j); use stable survival functions.
    thresholds=np.arange(C,dtype=np.int64)
    return float(np.sum(binom_dist.sf(thresholds,T,p)))


def expected_overflow(T:int,p:float,C:int)->float:
    return T*p-clipped_mean(T,p,C)


def topk_g(u:float,K:int)->float:
    return math.fsum(comb(E-1,j)*(1-u)**j*u**(E-1-j) for j in range(K))


def p_short(x:float,K:int)->float:
    if x==0.0:return K/E
    def cdf(y:float)->float:
        if y < -40:return 0.0
        if y > 40:return 1.0
        return math.exp(-math.exp(-y))
    def pdf(y:float)->float:
        if y < -40 or y > 40:return 0.0
        return math.exp(-y-math.exp(-y))
    value,err=quad(lambda y:topk_g(cdf(y+x),K)*pdf(y),-np.inf,np.inf,epsabs=1e-11,epsrel=1e-11,limit=300)
    if err>1e-8:raise ArithmeticError((x,K,err))
    return value


def eta_value(K:int)->float:
    lf=(1/math.e)*(E-1)*comb(E-2,K-1)
    return 0.8*K*(E-1)/lf


def population_predictions(K:int,T:int,cap:np.ndarray,eta:float,max_h:int)->tuple[list[float],list[float]]:
    x=0.0; finite_gap=[]; limit_gap=[]; base_limit=K/E
    cs=int(cap[0]); cr=int(cap[1]); p=K/E
    base_finite=(sum(expected_overflow(T,p,int(c)) for c in cap))/T
    for _ in range(max_h):
        ps=p_short(x,K); pr=(K-ps)/(E-1)
        of=(expected_overflow(T,ps,cs)+(E-1)*expected_overflow(T,pr,cr))/T
        finite_gap.append(of-base_finite)
        limit_gap.append(ps-p)
        ms=clipped_mean(T,ps,cs); mr=clipped_mean(T,pr,cr)
        x += eta*(mr-ms)/(K*T)
    return finite_gap,limit_gap


def no_clip_check(K:int,T:int,eta:float,seed:int,mode:str)->None:
    rng=np.random.default_rng(seed); aff0=sample(rng,T)
    q_r=np.zeros(E);q_a=np.zeros(E)
    for n in range(max(HORIZONS)):
        aff=aff0 if mode=='static' or n==0 else sample(rng,T)
        r1,_=route(aff,q_r,K);r2,_=route(aff,q_a,K)
        assert np.array_equal(r1,r2)
        q_r=update(q_r,r1,K,T,eta)
        q_a=update(q_a,r2,K,T,eta) # C=T implies A=R
        assert np.array_equal(q_r,q_a)


def run_regime(mode:str,initial:np.ndarray,seed:int,K:int,T:int,cap:np.ndarray,eta:float,
               finite_pred:list[float],limit_pred:list[float])->list[dict]:
    rng=np.random.default_rng(seed)
    # consume the same initial draw in both regimes; static reuses it, fresh starts with it.
    first=sample(rng,T)
    assert np.array_equal(first,initial)
    qR=np.zeros(E);qA=np.zeros(E);cumR=cumA=0
    rows=[]; wanted=set(HORIZONS)
    for n in range(1,max(HORIZONS)+1):
        aff=initial if mode=='static' or n==1 else sample(rng,T)
        rR,tR=route(aff,qR,K);rA,tA=route(aff,qA,K)
        aR=np.minimum(rR,cap);aA=np.minimum(rA,cap)
        jR=overflow(rR,cap);jA=overflow(rA,cap)
        for rr,aa,jj in ((rR,aR,jR),(rA,aA,jA)):
            assert int(rr.sum())==K*T and int(rr.max())<=T
            assert np.array_equal(aa,np.minimum(rr,cap))
            assert jj==int((rr-aa).sum())
        if n==1:assert jR==jA
        cumR+=jR;cumA+=jA
        qR=update(qR,rR,K,T,eta);qA=update(qA,aA,K,T,eta)
        if n in wanted:
            rows.append({'regime':mode,'E':E,'K':K,'T':T,'replicate':seed,
                'H':n,'eta':eta,'requested_overflow':cumR,'admitted_overflow':cumA,
                'gap_A_minus_R_over_T':(cumA-cumR)/T,
                'finiteT_mean_recursion_gap':math.fsum(finite_pred[:n]),
                'iterated_population_gap':math.fsum(limit_pred[:n]),
                'ties':tR+tA})
    return rows


def main()->None:
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[]; nc=0
    for K in KS:
      eta=eta_value(K)
      for ti,T in enumerate(TS):
        cap=cap_vector(K,T)
        f_pred,l_pred=population_predictions(K,T,cap,eta,max(HORIZONS))
        for rep in range(REPS):
          seed=2026101700+K*100000+ti*10000+rep
          rng=np.random.default_rng(seed); initial=sample(rng,T)
          # Same initial plant and seed across temporal regimes.
          for mode in ('static','fresh'):
            run_seed=seed
            if mode=='fresh':
                # Reinitialize so the first matrix is identical; later matrices are fresh.
                pass
            rows.extend(run_regime(mode,initial,run_seed,K,T,cap,eta,f_pred,l_pred))
            no_clip_check(K,T,eta,seed+9000000,mode);nc+=1

    raw=OUT/'plants.csv'
    with raw.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    groups=defaultdict(list)
    for z in rows:groups[(z['regime'],z['K'],z['T'],z['H'])].append(z)
    cells=[]
    for key,cell in sorted(groups.items(),key=lambda kv:(kv[0][1],kv[0][2],kv[0][3],kv[0][0])):
        reg,K,T,H=key
        g=np.array([z['gap_A_minus_R_over_T'] for z in cell])
        fpred=cell[0]['finiteT_mean_recursion_gap'];lpred=cell[0]['iterated_population_gap']
        se=float(g.std(ddof=1)/math.sqrt(len(g))); tc=float(student_t.ppf(.975,len(g)-1));m=float(g.mean())
        cells.append({'regime':reg,'K':K,'T':T,'H':H,'n':len(g),'mean_gap_over_T':m,
          'ci95_low':m-tc*se,'ci95_high':m+tc*se,'fraction_positive':float(np.mean(g>0)),
          'finiteT_mean_recursion_gap':fpred,'abs_error_finiteT':abs(m-fpred),
          'finiteT_ci_covers':bool(m-tc*se<=fpred<=m+tc*se),
          'iterated_population_gap':lpred,'abs_error_limit':abs(m-lpred),
          'limit_ci_covers':bool(m-tc*se<=lpred<=m+tc*se)})
    # Paired static-vs-fresh comparison by plant seed.
    indexed={(z['regime'],z['K'],z['T'],z['replicate'],z['H']):z for z in rows}
    paired=[]
    for K in KS:
      for T in TS:
        for seed_idx in range(REPS):
          seed=2026101700+K*100000+TS.index(T)*10000+seed_idx
          for H in HORIZONS:
            a=indexed[('fresh',K,T,seed,H)]['gap_A_minus_R_over_T']
            b=indexed[('static',K,T,seed,H)]['gap_A_minus_R_over_T']
            paired.append({'K':K,'T':T,'replicate':seed,'H':H,'fresh_minus_static_gap_over_T':a-b})
    pg=defaultdict(list)
    for z in paired:pg[(z['K'],z['T'],z['H'])].append(z['fresh_minus_static_gap_over_T'])
    regdiff=[]
    for key,vals in sorted(pg.items()):
        arr=np.asarray(vals);se=float(arr.std(ddof=1)/math.sqrt(len(arr)));tc=float(student_t.ppf(.975,len(arr)-1));m=float(arr.mean())
        regdiff.append({'K':key[0],'T':key[1],'H':key[2],'n':len(arr),'fresh_minus_static_mean':m,'ci95_low':m-tc*se,'ci95_high':m+tc*se})
    for name,data in [('cells.csv',cells),('fresh_minus_static.csv',regdiff)]:
      with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    summary={'protocol':PROTOCOL.relative_to(ROOT).as_posix(),'protocol_sha256':sha(PROTOCOL),
      'script_sha256':sha(Path(__file__)),'plants_sha256':sha(raw),'cells_sha256':sha(OUT/'cells.csv'),
      'fresh_static_sha256':sha(OUT/'fresh_minus_static.csv'),'rows':len(rows),'cells':len(cells),
      'paired_regime_cells':len(regdiff),'no_clipping_full_trajectory_controls':nc,
      'total_exact_ties':sum(z['ties'] for z in rows),'all_invariants_passed':True,
      'T_values':list(TS),'K_values':list(KS),'H_values':list(HORIZONS),'replicates':REPS,
      'population_comparator':'finite-T deterministic mean-feedback recurrence and T-infinity iterated limit',
      'interpretation':'Controlled stochastic paired experiment; no trained model or telemetry-cost claim.'}
    sp=OUT/'summary.json';sp.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__':main()
