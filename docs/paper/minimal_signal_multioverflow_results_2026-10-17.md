# Exact multi-overflow telemetry audit: results

**Protocol:** [preregistered exact protocol](minimal_signal_multioverflow_protocol_2026-10-17.md)  
**Executable:** [`audit_minimal_signal_multioverflow.py`](../../scripts/audit_minimal_signal_multioverflow.py)  
**Machine-readable result:** [`summary.json`](../../results/minimal_signal_multioverflow/summary.json)

## Result

The exact enumeration passed in all 16 `(E,D)` groups and covered 611
Top-1-realizable worlds. For `E in {2,3,4,8}` and `D in {1,2,3,4}`, with
`T=E+D`, unit capacity per expert, and admitted vector `A=1`, it verified:

- every bounded-composition request vector `R=1+d`, `sum(d)=D`, is realized
  by an explicit one-hot Top-1 affinity batch;
- all worlds have the same admitted observation and admitted next gauge state;
- every world has a distinct requested next gauge state;
- the centered rejected-load vector `P_0(R-A)` is injective over the fiber;
- the exact fiber size is `binomial(E+D-1,D)`, so the zero-error fixed-length
  message size for reproducing that requested update is
  `ceil(log2 binomial(E+D-1,D))` bits.

At `E=8`, the exact message lengths for `D=1,2,3,4` are respectively
`3,6,7,9` bits. This is an exact discrete information count, not an estimate
of communication latency or the marginal cost of a collective.

## What this contributes to the current line

This extends the controlled audit of T4b beyond the single-overflow case and
checks the multi-overflow corollary T4c in the canonical per-expert clipping
model. It supports a concrete statement about how much information the
requested **next update** contains on a fixed clipping fiber.

It does not give the minimum signal for an overflow-optimal redesigned
controller, a multi-round value-of-information theorem, a break-even against
measured system cost, or a separation from the general active-testing
benchmark. The bit-count step is the standard injective-message bound; the
MoE-specific ingredients here are the clipping fiber, Top-1 realizability,
and the requested-update map. Thus this strengthens the evidence for the
professor's costed-information layer, but does not by itself clear the
top-conference novelty gate.
