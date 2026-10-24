# Deterministic new matrix specification

Prime32003; Python random.Random seed2026102458. Draw r,v,t with three
successive randrange(1,32003) calls. Skip points with A=0, Delta=0, or a
vanishing literal connection denominator. Keep1230 accepted triples.
Append compact output row0 thenrow1 for each triple:2460rows.

Use A=r³+r^-3+(rv-1)^6/r15,
b=tv,c=t(1-t²)/7,d=1+t6,
N=(Ar Ma,Av Ma+t Mb,v Mb+c' Mc+d' Md), positive packet orientation,
input columns e0,e1. The pinned connection source SHA256 is
a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d.

Column tuple format: (sector,direction,input_row,r_exp,v_exp,t_exp).
Directions0,1,2 mean r,v,t. Top h3 uses direction=-1 as a marker.

```python
basis = [('h3', -1, j, m, n, k)
         for j in range(2) for m in range(-10, -5)
         for n in range(2) for k in range(3)]
basis += [('k3', 2, j, m, n, k)
          for j in range(2) for m in range(-10, 3)
          for n in range(3) for k in range(3)]
for sector in ['P2', 'P1', 'P0']:
    basis += [(sector, direction, j, m, n, k)
              for direction in range(3) for j in range(2)
              for m in range(-10, 3)
              for n in range(3) for k in range(3)]
```

The first2400 columns are coefficients; the last column is A³r^-4 Mb e0/12.
All lower sectors stay unrestricted. For a monomial u and input column e_j:

- h3 column: W3(u e_j), with tau3=r7+12r.
- k3 column: (partial_t+Nt)(u e_j).
- P2 in direction i: A[(partial_i+N_i)(u e_j)-2A_i/A*u e_j].
- P1 in direction i: A²[(partial_i+N_i)(u e_j)-A_i/A*u e_j].
- P0 in direction i: A³(partial_i+N_i)(u e_j).

Every finite sample is interpreted also as the same integer-valued rational
sample over Q. All inverted denominators are units modulo32003. A nonzero
2401-square augmented minor therefore proves rational inconsistency; no
assumption on the modular reductions of unknown solution coefficients is used.

Only the new A³ joint system is computed. Earlier determinants and mathematical
batches are not rerun. A lower-rank modular gap would need additional exact
kernel/rank evidence; the receipt must distinguish that case explicitly.
