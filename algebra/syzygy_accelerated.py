"""Optional FLINT discovery accelerator. Never imported by the proof replayer.

Install python-flint for this module. All exported coefficients are rational
strings, replayed independently using fractions.Fraction and original equations.
"""
import time
from flint import fmpq
import degree7_syzygies as s
c = s.cert

def export(span):
    return [{'polynomial':[[list(m),str(q)] for (_,m),q in sorted(row.items())],
             'products':[[j,list(mon),str(q)] for (j,mon),q in sorted(track.items())]}
            for k,(row,track) in sorted(span.items()) if k[0]==1]

def eliminate(rows,nD,multipliers,progress=True,checkpoint=None):
    span={};start=time.perf_counter()
    converted=[{m:fmpq(v.numerator,v.denominator) for m,v in row.items()} for row in rows]
    def addmul(dst,src,scale):
        for i,e in src.items():
            z=dst.get(i,0)-scale*e
            if z:dst[i]=z
            elif i in dst:del dst[i]
    for mi,mon in enumerate(multipliers):
        for j,row in enumerate(converted):
            v={(0 if any(i>=nD for i in m+mon) else 1,tuple(sorted(m+mon))):q for m,q in row.items()}
            track={(j,mon):fmpq(1)}
            while v:
                k=min(v);coef=v[k]
                if k not in span:
                    span[k]=({i:e/coef for i,e in v.items()},{i:e/coef for i,e in track.items()})
                    break
                other,comb=span[k]
                addmul(v,other,coef);addmul(track,comb,coef)
        if progress and (mi%5==0 or mi==len(multipliers)-1):
            print('multiplier',mi+1,'of',len(multipliers),'rank',len(span),'relations',sum(k[0] for k in span),'seconds',round(time.perf_counter()-start,3),flush=True)
        if checkpoint and (mi%5==0 or mi==len(multipliers)-1):
            checkpoint(export(span),len(span),mi+1)
    return export(span),len(span)

def reduce_span(polynomials):
    monomials=sorted({m for p in polynomials for m in p},key=lambda m:(-len(m),m))
    lookup={m:i for i,m in enumerate(monomials)};span={}
    def add(dst,src,scale):
        for i,e in src.items():
            z=dst.get(i,0)+scale*e
            if z:dst[i]=z
            elif i in dst:del dst[i]
    for j,p in enumerate(polynomials):
        v={lookup[m]:fmpq(q.numerator,q.denominator) for m,q in p.items()};track={j:fmpq(1)}
        while v:
            k=min(v);q=v[k]
            if k not in span:
                span[k]=({i:e/q for i,e in v.items()},{i:e/q for i,e in track.items()});break
            row,comb=span[k];add(v,row,-q);add(track,comb,-q)
    def witness(p):
        if any(m not in lookup for m in p):return None
        v={lookup[m]:fmpq(q.numerator,q.denominator) for m,q in p.items()};track={}
        while v:
            k=min(v);q=v[k]
            if k not in span:return None
            row,comb=span[k];add(v,row,-q);add(track,comb,q)
        return {'polynomial':c.encode(p),'equation_weights':[[j,str(q)] for j,q in sorted(track.items())]}
    linear=[{monomials[k]:s.triples.Q(str(q)) for k,q in row.items()}
            for k,(row,_) in sorted(span.items()) if len(monomials[k])==1]
    return witness,linear,len(span)

