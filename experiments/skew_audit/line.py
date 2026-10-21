"""Independent source-based line/Jacobian audit. Standard library only.

Reconstructs source coefficients and both tangent maps without notebook arithmetic imports.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import comb, prod
from itertools import permutations, combinations
import ast
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'results/one-reflection-skew-audit-20261021'
LIVE = HERE / 'inputs/live'
SOURCE = LIVE / 'upstream/data/one-reflection-skew'
P = 11
VARIABLES = ['X0', 'X1', 'X2', 'Y0', 'Y1', 'Y2']
A_POINT = [1, 0, 6, 3, 2, 7]
B_SLOPE = [0, 1, 2, 2, 0, 8]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def add(a, b):
    out = dict(a)
    for m, c in b.items():
        out[m] = out.get(m, Q(0)) + c
        if not out[m]:
            del out[m]
    return out


def mul(a, b):
    out = {}
    for m, c in a.items():
        for n, d in b.items():
            key = tuple(x+y for x, y in zip(m, n))
            out[key] = out.get(key, Q(0)) + c*d
    return {m:c for m,c in out.items() if c}


def parse_expression(text):
    zero = (0,)*6
    def visit(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return {zero:Q(node.value)} if node.value else {}
        if isinstance(node, ast.Name):
            m = [0]*6; m[VARIABLES.index(node.id)] = 1
            return {tuple(m):Q(1)}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return {m:-c for m,c in visit(node.operand).items()}
        if isinstance(node, ast.BinOp):
            left = visit(node.left)
            if isinstance(node.op, ast.Pow):
                require(isinstance(node.right, ast.Constant) and isinstance(node.right.value,int) and node.right.value >= 0, 'Polynomial exponent')
                out = {zero:Q(1)}
                for _ in range(node.right.value): out = mul(out,left)
                return out
            right = visit(node.right)
            if isinstance(node.op, ast.Add): return add(left,right)
            if isinstance(node.op, ast.Sub): return add(left,{m:-c for m,c in right.items()})
            if isinstance(node.op, ast.Mult): return mul(left,right)
            if isinstance(node.op, ast.Div):
                require(set(right)=={zero} and right[zero]!=0, 'Only scalar division')
                return {m:c/right[zero] for m,c in left.items()}
        raise ValueError(ast.dump(node))
    return visit(ast.parse(text,mode='eval').body)


def mod(c):
    c=Q(c)
    return c.numerator % P * pow(c.denominator % P,-1,P) % P


def conv(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,c in enumerate(a):
        for j,d in enumerate(b):out[i+j]=(out[i+j]+c*d)%P
    return out


def restrict(poly,a,b,degree):
    out=[0]*(degree+1)
    for powers,c in poly.items():
        term=[mod(c)]
        for ai,bi,e in zip(a,b,powers):
            term=conv(term,[(comb(e,j)*pow(ai,e-j,P)*pow(bi,j,P))%P for j in range(e+1)])
        for i,x in enumerate(term):out[i]=(out[i]+x)%P
    return out


def gradient(poly,i):
    out={}
    for m,c in poly.items():
        if m[i]:
            n=list(m);n[i]-=1;out[tuple(n)]=c*m[i]
    return out


def truncated_product(a,b,epsilon_bound=1):
    out={}
    for (t,e),c in a.items():
        for (u,f),d in b.items():
            if e+f<=epsilon_bound:
                k=(t+u,e+f);out[k]=(out.get(k,0)+c*d)%P
    return {m:c for m,c in out.items() if c}


def perturbation_expansion(poly,da,db,epsilon_bound=1):
    # Direct substitution into F, independently of differentiated source terms.
    out={}
    for powers,c in poly.items():
        term={(0,0):mod(c)}
        for i,e in enumerate(powers):
            x={(0,0):A_POINT[i],(1,0):B_SLOPE[i],(0,1):da[i],(1,1):db[i]}
            for _ in range(e):term=truncated_product(term,x,epsilon_bound)
        for key,value in term.items():out[key]=(out.get(key,0)+value)%P
    return {m:c for m,c in out.items() if c}


def rref(matrix):
    out=[list(map(lambda x:x%P,row)) for row in matrix];pivots=[];r=0
    for c in range(len(out[0])):
        pivot=next((i for i in range(r,len(out)) if out[i][c]),None)
        if pivot is None:continue
        out[r],out[pivot]=out[pivot],out[r]
        inv=pow(out[r][c],-1,P);out[r]=[x*inv%P for x in out[r]]
        for i in range(len(out)):
            if i!=r and out[i][c]:
                d=out[i][c];out[i]=[(x-d*y)%P for x,y in zip(out[i],out[r])]
        pivots.append(c);r+=1
        if r==len(out):break
    return out,pivots


def kernel(matrix):
    reduced,pivots=rref(matrix);n=len(matrix[0]);out=[]
    for f in range(n):
        if f in pivots:continue
        v=[0]*n;v[f]=1
        for i,p in enumerate(pivots):v[p]=(-reduced[i][f])%P
        out.append(v)
    return out


def matvec(matrix,v):
    return [sum(a*b for a,b in zip(row,v))%P for row in matrix]


def determinant(matrix):
    # Leibniz formula, independent of the RREF routine.
    n=len(matrix);out=0
    for perm in permutations(range(n)):
        c=(-1)**sum(perm[i]>perm[j] for i in range(n) for j in range(i+1,n))
        for i,j in enumerate(perm):c=c*matrix[i][j]%P
        out=(out+c)%P
    return out


def parse_rec_header(text,key):
    lines=text.splitlines();i=next(i for i,l in enumerate(lines) if l.startswith(key+':'))
    out=lines[i].split(':',1)[1].strip();i+=1
    while i<len(lines) and lines[i].startswith(' '):out+=' '+lines[i].strip();i+=1
    return out


def parse_reported_matrix(text,name,rows):
    tail=text.split('\n'+name+' =\n',1)[1]
    lines=[line.strip() for line in tail.splitlines() if line.strip()]
    return [[int(x) for x in line.split()] for line in lines[:rows]]


def main():
    manifest=json.loads((LIVE/'source-manifest.json').read_text(encoding='utf-8'))
    pinned='78632ddad42489fe92f14e588f1ed4b8909395dd'
    require(manifest['upstream_head']==pinned,'Upstream head changed')
    source_records={row['path']:row for row in manifest['files']}
    for name in ['instance.rec','record.json']:
        key='data/one-reflection-skew/'+name
        data=(SOURCE/name).read_bytes();row=source_records[key]
        require(row['commit']==pinned,'Source commit changed')
        require(hashlib.sha256(data).hexdigest()==row['sha256'],'Raw source SHA256')
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob_sha1'],'Source git blob SHA1')
    record=json.loads((SOURCE/'record.json').read_text(encoding='utf-8'))
    rec=(SOURCE/'instance.rec').read_text(encoding='utf-8')
    polys={key:{tuple(m):Q(c) for c,m in record[key]['terms']} for key in ['F','A']}
    for key,poly in polys.items():
        require(poly==parse_expression(record[key]['expression']),key+' record expression mismatch')
        require(poly==parse_expression(parse_rec_header(rec,key)),key+' instance.rec mismatch')
    require(record['q']==int(parse_rec_header(rec,'q'))==1,'q changed')
    F,A=polys['F'],polys['A']
    require(all(sum(m)==6 for m in F) and len(F)==10,'F degree/term count')
    require(A=={(3,0,0,3,0,0):Q(1)},'A changed')
    line=restrict(F,A_POINT,B_SLOPE,6);source=restrict(A,A_POINT,B_SLOPE,6)
    require(line==[0]*7,'Line incidence')
    require(source==[5,10,3,8,0,0,0],'Source restriction')
    gradients=[restrict(gradient(F,i),A_POINT,B_SLOPE,5) for i in range(6)]
    J=[[gradients[i][r] for i in range(6)] for r in range(6)]
    columns=[];labels=[]
    for i in range(2,6):
        columns.extend([gradients[i]+[0],[0]+gradients[i]])
        labels.extend([VARIABLES[i]+' intercept',VARIABLES[i]+' slope'])
    M=[[col[r] for col in columns] for r in range(7)]
    rankM=len(rref(M)[1]);rankJ=len(rref(J)[1]);kerM=kernel(M);kerJ=kernel(J)
    require((rankM,rankJ)==(7,4),'Ranks')
    minorM=determinant([row[:7] for row in M]);require(minorM==6,'M minor')
    j_minor=None
    for rows in combinations(range(6),4):
        for cols in combinations(range(6),4):
            d=determinant([[J[i][j] for j in cols] for i in rows])
            if d:j_minor={'rows':list(rows),'columns':list(cols),'determinant_mod11':d};break
        if j_minor:break
    require(j_minor is not None,'J minor')
    require(matvec(J,A_POINT)==[0]*6 and matvec(J,B_SLOPE)==[0]*6,'Forced kernel')
    require(len(rref([A_POINT,B_SLOPE])[1])==2 and len(rref(kerJ+[A_POINT,B_SLOPE])[1])==2,'Kernel span')
    direct_columns=0
    for i in range(2,6):
        for slope in [False,True]:
            da,db=[0]*6,[0]*6;(db if slope else da)[i]=1
            exp=perturbation_expansion(F,da,db)
            direct=[exp.get((r,1),0) for r in range(7)]
            require(direct==columns[2*(i-2)+int(slope)],'Direct Grassmann derivative');direct_columns+=1
    for i in range(6):
        db=[0]*6;db[i]=1;exp=perturbation_expansion(F,[0]*6,db)
        require([exp.get((r+1,1),0) for r in range(6)]==gradients[i],'Direct fixed-endpoint derivative');direct_columns+=1
    discussion=(LIVE/'discussion-127.md').read_text(encoding='utf-8').replace('\r','')
    require(M==parse_reported_matrix(discussion,'M',7),'Reported M mismatch')
    require(J==parse_reported_matrix(discussion,'J',6),'Reported J mismatch')
    projective_source_values=[{'point':[1,t],'value':sum(source[j]*pow(t,j,P) for j in range(7))%P} for t in range(P)]
    projective_source_values.append({'point':[0,1],'value':source[-1]})
    zeros=[row['point'] for row in projective_source_values if not row['value']]
    require(zeros==[[1,4],[0,1]],'Source zero points')
    # Geometrically trivial slope changes, exact incidence rather than first order only.
    reparam=[(b+a)%P for a,b in zip(A_POINT,B_SLOPE)]
    scaled=[2*b%P for b in B_SLOPE]
    require(restrict(F,A_POINT,reparam,6)==[0]*7 and restrict(F,A_POINT,scaled,6)==[0]*7,'Slope gauge incidence')
    bad_a=list(A_POINT);bad_a[2]=5
    bad_line=restrict(F,bad_a,B_SLOPE,6);require(any(bad_line),'Bad line unexpectedly accepted')
    bad_slope=list(B_SLOPE);bad_slope[2]=(bad_slope[2]+1)%P
    bad_slope_residual=restrict(F,A_POINT,bad_slope,6);require(any(bad_slope_residual),'Nonkernel slope perturbation')
    da=[0,0]+kerM[0][::2];db=[0,0]+kerM[0][1::2]
    tangent_expansion=perturbation_expansion(F,da,db,6)
    require(all(e>=2 for t,e in tangent_expansion),'Tangent first-order error')
    require(any(e==2 for t,e in tangent_expansion),'Expected nonlinear remainder')
    controls=[]
    for name,ok in [('changed_X2_intercept_rejected',any(bad_line)),('nonkernel_slope_change_rejected',any(bad_slope_residual)),('A_is_not_nowhere_zero',len(zeros)==2),('7F_minor_differs',minorM*pow(7,7,P)%P!=minorM)]:
        require(ok,name);controls.append(name)
    badM=[row[:] for row in M];badM[0][0]=(badM[0][0]+1)%P
    require(badM!=M and matvec(badM,kerM[0])!=[0]*7,'Altered matrix detected');controls.append('altered_M_entry_breaks_source_and_kernel')
    evaluation=[[da[i],B_SLOPE[i]] for i in range(1,6)]
    require(len(rref(evaluation)[1])==2,'Marked evaluation rank')
    target_differential=[gradients[i][0] for i in range(1,6)]
    require(any(target_differential),'Target not smooth at the marked point')
    require(all(sum(target_differential[i]*evaluation[i][j] for i in range(5))%P==0 for j in range(2)),'Evaluation tangent lies in target tangent')
    rational_value=sum(c*prod(Q(x)**e for x,e in zip(A_POINT,m)) for m,c in F.items())
    require(rational_value==165099 and rational_value!=0,'Same integer point is not a rational point on F')
    report={
        'schema':'one-reflection-skew-line-independent-source-audit-v1','status':'PASS','field':11,
        'upstream_commit':pinned,'source_git_blob_and_raw_sha256_checks':2,
        'source_bindings_lf_sha256':{str(path.relative_to(LIVE)).replace('\\','/'):sha(path) for path in [SOURCE/'instance.rec',SOURCE/'record.json',LIVE/'discussion-127.md',LIVE/'source-manifest.json']},
        'checker_lf_sha256':sha(Path(__file__)),
        'protected':{'q':1,'variables':VARIABLES,'F_terms':record['F']['terms'],'A_terms':record['A']['terms'],'record_and_instance_expressions_match':True},
        'line':{'a':A_POINT,'b':B_SLOPE,'F_coefficients_s6_to_t6':line,'seven_F_coefficients':[(7*x)%P for x in line],'same_integer_point_F_over_Q':str(rational_value)},
        'source_restriction':{'coefficients_s6_to_t6':source,'factorization':'s^3 (3s+2t)^3','value_at_1_0':5,'zero_points_P1_F11':zeros,'zero_multiplicity_each':3,'projective_values':projective_source_values,'not_identically_zero':True,'nowhere_zero':False},
        'restricted_gradients':{'rows_are_coordinates':VARIABLES,'coefficients_t0_to_t5':gradients},
        'ordinary_incidence':{'domain':'8-dimensional Grassmann chart: X0=s,X1=t; other four coordinates alpha_i*s+beta_i*t','codomain':'7 coefficients s^6,...,t^6 of F','columns':labels,'matrix':M,'rank':rankM,'kernel':kerM,'first_seven_columns_minor':minorM,'first_seven_columns_minor_if_using_7F':minorM*pow(7,7,P)%P,'local_incidence_dimension':1},
        'fixed_endpoint':{'domain':'6 slope coefficients b_i with endpoint a fixed; residual parameterization gauges span(a,b)','codomain':'coefficients t^1,...,t^6 of F(a+t*b); constant coefficient already zero','matrix':J,'rank':rankJ,'kernel':kerJ,'kernel_equals_span_a_b':True,'kernel_dimension':2,'nonzero_minor':j_minor,'quotient_domain_dimension':4,'induced_quotient_map_injective':True,'rank_four_is_maximal_given_gauges':True},
        'marked_evaluation':{'point':'a, in affine chart X0=1','target_coordinates':VARIABLES[1:],'domain_columns':['ordinary-incidence kernel parameter','marked point parameter t'],'derivative_matrix':evaluation,'rank':2,'target_tangent_equation_coefficients':target_differential,'target_tangent_dimension':4,'image_is_in_target_tangent':True,'scope':'The local two-dimensional marked-line family at this smooth incidence point does not dominate the four-dimensional target.'},
        'derivative_checks':{'direct_dual_number_columns_checked':direct_columns,'reported_matrices_match':True,'Euler_and_line_derivative_kernel_identities_checked':True},
        'perturbations':{'X2_intercept_6_to_5_F_coefficients':bad_line,'X2_slope_2_to_3_F_coefficients':bad_slope_residual,'same_line_b_plus_a_incidence':True,'same_line_2b_incidence':True,'Grassmann_kernel_tangent':kerM[0],'straight_tangent_path_first_nonzero_epsilon_order':2,'straight_tangent_epsilon2_coefficients':[tangent_expansion.get((t,2),0) for t in range(7)]},
        'controls':controls,
        'limits':['Ranks and smooth-incidence conclusion are over F11 for this line and these explicitly specified charts.','Rank4 is not an accidental defect: two slope gauge directions are forced.','The line source is nonzero as a polynomial but vanishes at two projective points.','Ordinary incidence smoothness supplies no independent generic-endpoint or characteristic-zero construction here.','No rational primitive, HasCertificate proof, or target-solve claim.']
    }
    (HERE/'line-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','M_rank':rankM,'M_minor':minorM,'J_rank':rankJ,'J_minor':j_minor,'source_zeros':zeros,'direct_derivative_columns':direct_columns,'controls':len(controls)}))


if __name__=='__main__':main()
