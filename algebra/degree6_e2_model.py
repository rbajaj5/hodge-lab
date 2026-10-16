"""Export the complete normalized degree-six E2 system, modulo F.

Input: degree6_e1_basis.json from degree6_e1.py. The proven degree-six
Euler gauge removes the F coordinate, leaving 108 denominator parameters.
ALL 315 quadratic-coefficient Koszul syzygies are retained; no parity,
geometric ansatz, or strict-quotient restriction is imposed.

For D=sum(a_i D_i), N0=sum(a_i N_i), K=sum(z_j K_j), the exported exact
quadratic equations are B_D(N0+K)=0 modulo (F). This is the full E2
condition (with arbitrary quotient C), NOT its weaker reduction modulo J.
No solver or certificate is claimed. The optional removed scalar c can be
restored as D+cF, N+c A*Euler/6, C+c div(N)+c^2 A.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations,combinations_with_replacement
import importlib.util,json,gzip,time,hashlib
spec=importlib.util.spec_from_file_location('qs',Path(__file__).with_name('degree6_quadratic_structure.py'))
qs=importlib.util.module_from_spec(spec);spec.loader.exec_module(qs);e1=qs.e1
def decode(terms):return {tuple(u):Q(c) for c,u in terms}
LEAD=(6,0,0,0,0,0)
def modF(poly):
    """Canonical polynomial remainder for lex leading term X0^6."""
    v=dict(poly)
    while True:
        candidates=[u for u in v if u[0]>=6]
        if not candidates:break
        u=max(candidates);c=v.pop(u);shift=(u[0]-6,)+u[1:]
        for m,coef in e1.F.items():
            if m==LEAD:continue
            r=e1.expadd(m,shift);z=v.get(r,0)-c*coef
            if z:v[r]=z
            elif r in v:del v[r]
    return v

def main():
    started=time.perf_counter();source=e1.OUT/'degree6_e1_basis.json';bundle=json.loads(source.read_text())
    pairs=[(decode(p['D']),[decode(n)for n in p['N']])for p in bundle['basis']]
    # F has coefficient one on basis108; remove precisely that column.
    assert bundle['F_basis_coordinates']['108']=='1'
    pairs=pairs[:108]
    rows=[u for u in e1.mons(12)if u[0]<6];rowidx={u:i for i,u in enumerate(rows)}
    koszul=[];labels=[]
    for i,j in combinations(range(6),2):
        for u in e1.mons(2):
            K=[{}for _ in range(6)];K[i]=e1.pmul({u:1},e1.DF[j]);K[j]={m:-c for m,c in e1.pmul({u:1},e1.DF[i]).items()}
            koszul.append(K);labels.append([i,j,list(u)])
    aa=list(combinations_with_replacement(range(108),2));entries=[];column_nonzero=[]
    for col,(i,j)in enumerate(aa):
        p=qs.B(pairs[i][0],pairs[j][1])
        if i!=j:p=e1.padd(p,qs.B(pairs[j][0],pairs[i][1]))
        remainder=modF(p);column_nonzero.append(len(remainder))
        for u,c in sorted(remainder.items()):entries.append([rowidx[u],col,c.numerator,c.denominator])
    aa_nnz=len(entries);offset=len(aa)
    for i,(D,N)in enumerate(pairs):
        for k,K in enumerate(koszul):
            col=offset+i*len(koszul)+k;remainder=modF(qs.B(D,K));column_nonzero.append(len(remainder))
            for u,c in sorted(remainder.items()):entries.append([rowidx[u],col,c.numerator,c.denominator])
    # A sparse deterministic exact identity check compares full assembly to
    # the exported polynomial-coordinate model. This is validation, not a
    # candidate search or a claim of finding a zero of the equations.
    avec={0:Q(2),7:Q(-1),28:Q(3),36:Q(-2),82:Q(1),96:Q(1),105:Q(-1)}
    zvec={0:Q(1),20:Q(-2),57:Q(1),106:Q(2),314:Q(-1)}
    D={};N=[{}for _ in range(6)]
    for i,c in avec.items():
        D=e1.padd(D,pairs[i][0],c)
        for k in range(6):N[k]=e1.padd(N[k],pairs[i][1][k],c)
    for j,c in zvec.items():
        for k in range(6):N[k]=e1.padd(N[k],koszul[j][k],c)
    direct={rowidx[u]:c for u,c in modF(qs.B(D,N)).items()}
    weights=[avec.get(i,0)*avec.get(j,0) for i,j in aa]
    weights.extend(avec.get(i,0)*zvec.get(j,0)for i in range(108)for j in range(315))
    assembled={}
    for row,col,num,den in entries:
        if weights[col]:assembled[row]=assembled.get(row,0)+Q(num,den)*weights[col]
    assembled={r:c for r,c in assembled.items()if c}
    assert direct==assembled
    model={'instance':'holdout','degree':6,'coefficient_field':'Q','denominator_parameters':108,'numerator_correction_parameters':315,
           'denominator_basis_indices':list(range(108)),'source_basis_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
           'quotient_rows':len(rows),'row_monomials':[list(u)for u in rows],
           'aa_columns':[list(p)for p in aa],'az_column_offset':offset,'az_column_formula':'offset + a_index*315 + z_index',
           'koszul_labels':labels,'entries_format':['row','column','numerator','denominator'],'entries':entries,
           'equations':'sum(COO_aa[row,i,j]*a_i*a_j) + sum(COO_az[row,i,k]*a_i*z_k)=0',
           'legal_denominator_note':'a must be nonzero; these basis columns are independent modulo F. Complex coprimality relies on the standing irreducibility of this smooth target, not numerical checks.',
           'scope':'Complete normalized E2 modulo F in declared degree after proven F gauge; no solution or exclusion is asserted'}
    path=e1.OUT/'degree6_full_e2_model.json.gz'
    with gzip.open(path,'wt',encoding='utf-8',compresslevel=9)as handle:json.dump(model,handle,separators=(',',':'))
    report={'rows':len(rows),'denominator_parameters':108,'koszul_correction_parameters':315,'quadratic_aa_columns':len(aa),'bilinear_az_columns':108*315,
            'aa_nonzero_coefficients':aa_nnz,'az_nonzero_coefficients':len(entries)-aa_nnz,'total_nonzero_coefficients':len(entries),
            'structurally_zero_columns':sum(x==0 for x in column_nonzero),'sparse_identity_test_passed':direct==assembled,
            'model_bytes':path.stat().st_size,'model_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'seconds':time.perf_counter()-started,
            'claim':'Full exact polynomial E2 model prepared, not solved'}
    (e1.OUT/'degree6_full_e2_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    main()
