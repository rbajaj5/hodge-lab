#!/usr/bin/env python3
"""Independent Fraction reconstruction of the swapped-curve evaluation germ.

The calculation uses truncated Q(i)[b,U,h] jets inside Q(i)[b,U,h][u]. It
reconstructs G from the raw protected source and solves five physical Taylor
equations simultaneously, rather than importing the producer's elimination.
"""
from pathlib import Path
from fractions import Fraction as Q
import ast
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-unfolding'
CURVE=ROOT/'results/cyclic-fano-curve'
ORDER=4
ZLOCAL=(0,0,0)
DIRECTION=0
ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0));II=(Q(0),Q(1))
VARIABLES=('X0','X1','X2','Y0','Y1','Y2')
Z6=(0,)*6
def ca(a,b):return (a[0]+b[0],a[1]+b[1])
def cn(a):return (-a[0],-a[1])
def cm(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def ci(a):
    norm=a[0]**2+a[1]**2;assert norm;return (a[0]/norm,-a[1]/norm)
def strings(a):return list(map(str,a))
def sha(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def clean(a):return {m:v for m,v in a.items()if v!=ZERO}
def add(a,b):
    out=a.copy()
    for m,v in b.items():out[m]=ca(out.get(m,ZERO),v)
    return clean(out)
def scale(a,q):return clean({m:cm(q,v)for m,v in a.items()})
def multiply(a,b,cutoff=None):
    out={}
    for m,x in a.items():
        for n,y in b.items():
            k=tuple(i+j for i,j in zip(m,n))
            if cutoff is not None and sum(k)>cutoff:continue
            out[k]=ca(out.get(k,ZERO),cm(x,y))
    return clean(out)
def power(a,n,zero,cutoff=None):
    out={zero:ONE}
    for _ in range(n):out=multiply(out,a,cutoff)
    return out
def parse(text,variables=VARIABLES):
    zeromon=(0,)*len(variables)
    def visit(node):
        if isinstance(node,ast.Constant):
            assert type(node.value)==int;return clean({zeromon:(Q(node.value),Q(0))})
        if isinstance(node,ast.Name):
            if node.id=='I':return {zeromon:II}
            assert node.id in variables
            mon=[0]*len(variables);mon[variables.index(node.id)]=1;return {tuple(mon):ONE}
        if isinstance(node,ast.UnaryOp):
            assert isinstance(node.op,(ast.USub,ast.UAdd))
            return scale(visit(node.operand),(-ONE[0],ONE[1])if isinstance(node.op,ast.USub)else ONE)
        assert isinstance(node,ast.BinOp)
        if isinstance(node.op,ast.Pow):
            assert isinstance(node.right,ast.Constant)and type(node.right.value)==int and node.right.value>=0
            return power(visit(node.left),node.right.value,zeromon)
        a,b=visit(node.left),visit(node.right)
        if isinstance(node.op,ast.Add):return add(a,b)
        if isinstance(node.op,ast.Sub):return add(a,scale(b,(-Q(1),Q(0))))
        if isinstance(node.op,ast.Mult):return multiply(a,b)
        assert isinstance(node.op,ast.Div)and set(b)=={zeromon};return scale(a,ci(b[zeromon]))
    return visit(ast.parse(text,mode='eval').body)
def constant(q):return {ZLOCAL:q}if q!=ZERO else {}
def umul(a,b):
    out=[{}for _ in range(min(7,len(a)+len(b)-1))]
    for j,x in enumerate(a):
        for k,y in enumerate(b):
            if j+k<7:out[j+k]=add(out[j+k],multiply(x,y,ORDER))
    return out
def upower(a,n):
    out=[constant(ONE)]
    for _ in range(n):out=umul(out,a)
    return out
def coefficient_equations(G,b,U,h,z,unknown):
    C,E,k,l,m=unknown
    r=add(constant(ONE),h)
    coordinates=([U if DIRECTION==0 else {},b],[constant(ONE)],[z,k,l,m],
                 [add(constant(II),U if DIRECTION==3 else {}),add(constant(II),C)],
                 [r,constant(ONE)],[add(scale(r,II),U if DIRECTION==5 else {}),E])
    total=[{}for _ in range(7)]
    for mon,coefficient in G.items():
        term=[constant(coefficient)]
        for coordinate,n in zip(coordinates,mon):term=umul(term,upower(coordinate,n))
        for j,value in enumerate(term):total[j]=add(total[j],value)
    return total
def inverse(a):
    n=len(a);out=[row[:]+[ONE if i==j else ZERO for j in range(n)]for i,row in enumerate(a)]
    determinant=ONE
    for col in range(n):
        pivot=next(i for i in range(col,n)if out[i][col]!=ZERO)
        if pivot!=col:out[col],out[pivot]=out[pivot],out[col];determinant=cn(determinant)
        value=out[col][col];determinant=cm(determinant,value);out[col]=[cm(ci(value),v)for v in out[col]]
        for i in range(n):
            if i!=col:
                factor=out[i][col];out[i]=[ca(x,cn(cm(factor,y)))for x,y in zip(out[i],out[col])]
    return [row[n:]for row in out],determinant
def matvec(a,v):return [sum_pairs(cm(x,y)for x,y in zip(row,v))for row in a]
def sum_pairs(values):
    out=ZERO
    for v in values:out=ca(out,v)
    return out
def sparse(a):return [{'powers':list(m),'coefficient':strings(v)}for m,v in sorted(a.items())]
def homogeneous(a,n):return {m:v for m,v in a.items()if sum(m)==n}
def homogeneous_monomials(n):
    return [(a,b,n-a-b)for a in range(n+1)for b in range(n-a+1)]
def decode(terms):
    out={}
    for term in terms:
        mon=tuple(term['powers']);value=tuple(map(Q,term['coefficient']))
        assert len(mon)==3 and all(type(n)==int and n>=0 for n in mon)and sum(mon)<=ORDER
        assert mon not in out and value!=ZERO;out[mon]=value
    return out
def check_equal(a,b):assert a==b
def rejects(operation):
    try:operation()
    except AssertionError:return 1
    raise AssertionError('Mutation was not detected')

def derive(direction):
    global DIRECTION
    DIRECTION=direction
    manifest=load(CURVE/'target.json')
    text=(CURVE/'source/instance.rec').read_text(encoding='utf-8')
    values={};key=None
    for line in text.splitlines():
        match=re.match(r'^(q|F|A):\s*(.*)$',line)
        if match:key=match[1];values[key]=match[2]
        elif key and line.startswith('  '):values[key]+=' '+line.strip()
        else:key=None
    assert values==manifest['target']and values['q']=='1'
    assert sha(CURVE/'source/instance.rec')=='d99d10c84d25dc5def72cd7a9a17e5d022e18f562660c8e33bf106675b4a418c'
    F=parse(values['F']);G={}
    for mon,value in F.items():
        assert mon[2]%3==0
        new=list(mon);new[2]//=3;G[tuple(new)]=value
    assert len(G)==len(F)
    b={(1,0,0):ONE};U={(0,1,0):ONE};h={(0,0,1):ONE};none=[{}for _ in range(5)]
    assert all(not e for e in coefficient_equations(G,{},{},{},{},none))
    columns=[]
    for j in range(5):
        trial=[{}for _ in range(5)];trial[j]=b
        columns.append([e.get((1,0,0),ZERO)for e in coefficient_equations(G,{},{},{},{},trial)[1:6]])
    jacobian=[list(row)for row in zip(*columns)];jac_inverse,determinant=inverse(jacobian)
    # Lift the actual target surface G(U,1,z,i,1+h,i(1+h))=0 on z(0)=0.
    z={};target_pivot=(Q(0),Q(5,7))
    probe=coefficient_equations(G,{},{},{},b,none)[0]
    assert probe.get((1,0,0),ZERO)==target_pivot
    for degree in range(1,ORDER+1):
        residual=coefficient_equations(G,{},U,h,z,none)[0]
        z=add(z,scale(homogeneous(residual,degree),cn(ci(target_pivot))))
    assert not coefficient_equations(G,{},U,h,z,none)[0]
    solutions=[{}for _ in range(5)];stages=[]
    for degree in range(1,ORDER+1):
        residual=coefficient_equations(G,b,U,h,z,solutions)
        for mon in homogeneous_monomials(degree):
            rhs=[cn(e.get(mon,ZERO))for e in residual[1:6]]
            correction=matvec(jac_inverse,rhs)
            for j,value in enumerate(correction):
                if value!=ZERO:solutions[j][mon]=value
        checked=coefficient_equations(G,b,U,h,z,solutions)
        assert all(not any(sum(mon)<=degree for mon in eq)for eq in checked[:6])
        stages.append({'degree':degree,'five_physical_equations_vanish_through_degree':True})
    equations=coefficient_equations(G,b,U,h,z,solutions)
    assert all(not e for e in equations[:6])
    scalar=equations[6]
    kappa=scalar.get((3,0,0),ZERO);quartic=scalar.get((4,0,0),ZERO)
    assert kappa==(Q(-1),Q(-48,175))
    assert all(scalar.get((j,0,0),ZERO)==ZERO for j in range(3))
    t1=[[scalar.get(mon,ZERO)for mon in row]for row in
        [[(0,1,0),(0,0,1)],[(1,1,0),(1,0,1)]]]
    t1det=ca(cm(t1[0][0],t1[1][1]),cn(cm(t1[0][1],t1[1][0])))
    prepared=[[],[]]
    for j in range(2):
        prepared[0].append(cm(t1[0][j],ci(kappa)))
        prepared[1].append(ca(cm(t1[1][j],ci(kappa)),cn(cm(cm(quartic,t1[0][j]),cm(ci(kappa),ci(kappa))))))
    result={'source_instance_lf_sha256':sha(CURVE/'source/instance.rec'),
            'order':ORDER,'variables':['b',{0:'U',3:'V',5:'W'}[direction],'h'],'unknown_order':['C','E','k','l','m'],
            'physical_first_five_jacobian':[[strings(x)for x in row]for row in jacobian],
            'physical_first_five_jacobian_determinant':strings(determinant),
            'implicit_jets':{name:sparse(value)for name,value in zip(('C','E','k','l','m'),solutions)},
            'target_z_jet':sparse(z),'remaining_sixth_equation_jet':sparse(scalar),'stages':stages,
            'T1_matrix':[[strings(x)for x in row]for row in t1],'T1_determinant':strings(t1det),
            'central_cubic':strings(kappa),'central_quartic':strings(quartic),
            'prepared_constant_linear_parameter_matrix':[[strings(x)for x in row]for row in prepared]}
    return result,G

def audit_axis(direction):
    assert __debug__,'Run without -O'
    result,G=derive(direction)
    direction_name=VARIABLES[direction];parameter={0:'U',3:'V',5:'W'}[direction]
    path=OUT/('unfolding-'+direction_name+'.json');packet=load(path)
    assert packet['schema']=='cyclic-fano-unfolding-v1'and packet['instance']=='cyclic-triple-fano'
    assert packet['source_commit']=='d96911d725077e66a8f10848908be01a643b1714'
    assert packet['producer_sha256']==sha(ROOT/'experiments/cyclic_fano_unfolding.py')
    assert packet['fixed_target_manifest_sha256']==sha(CURVE/'target.json')
    assert packet['base_fiber_packet_sha256']==sha(ROOT/'results/cyclic-fano-fibers/fiber-equations.json')
    assert packet['parameter_direction']==direction_name
    assert packet['jet_variables']==['b',parameter,'h']and packet['jet_total_order']==ORDER
    assert packet['unknown_order']==['k','l','m','C','E']
    # Verify the full exact surface equation independently of its fourth-order jet.
    U= {(1,0,0):ONE};h={(0,1,0):ONE};z={(0,0,1):ONE}
    r=add(constant(ONE),h)
    coords=[U if direction==0 else {},constant(ONE),z,
            add(constant(II),U if direction==3 else {}),r,add(scale(r,II),U if direction==5 else {})]
    assert [parse(p,(parameter,'h','z'))for p in packet['target_surface_coordinates']]==coords
    exact_surface={}
    for mon,c in G.items():
        term=constant(c)
        for coord,n in zip(coords,mon):term=multiply(term,power(coord,n,ZLOCAL))
        exact_surface=add(exact_surface,term)
    assert exact_surface==parse(packet['exact_target_surface_equation'],(parameter,'h','z'))
    assert packet['target_z_derivative_at_origin']==['0','5/7']
    assert decode(packet['target_z_jet'])==decode(result['target_z_jet'])
    order=[2,3,4,0,1]
    assert packet['constant_implicit_jacobian']==[[row[j]for j in order]for row in result['physical_first_five_jacobian']]
    # This permutation has even sign.
    assert packet['constant_implicit_jacobian_determinant']==result['physical_first_five_jacobian_determinant']
    for name,jet in zip(packet['unknown_order'],packet['unknown_jets']):
        assert decode(jet)==decode(result['implicit_jets'][name])
    for stage in packet['hensel_stages']:
        n=stage['degree'];assert 1<=n<=ORDER and len(stage['corrections'])==5
        for name,jet in zip(packet['unknown_order'],stage['corrections']):
            assert decode(jet)==homogeneous(decode(result['implicit_jets'][name]),n)
    assert [stage['degree']for stage in packet['hensel_stages']]==list(range(1,ORDER+1))
    scalar=decode(result['remaining_sixth_equation_jet'])
    assert decode(packet['scalar_germ_jet'])==scalar
    assert packet['scalar_cubic_at_central_fiber']==result['central_cubic']
    assert packet['scalar_quartic_at_central_fiber']==result['central_quartic']
    assert packet['T1_basis']==['1','b']and packet['T1_parameter_order']==[parameter,'h']
    assert packet['T1_parameter_matrix']==result['T1_matrix']
    assert packet['T1_determinant']==result['T1_determinant']==['0','0']and packet['T1_rank']==1
    assert packet['normalized_Weierstrass_constant_and_linear_parameter_matrix']==result['prepared_constant_linear_parameter_matrix']
    assert decode(packet['seed_line_slice_second_parameter_zero'])=={m:c for m,c in scalar.items()if m[1]==0}
    kappa=tuple(map(Q,result['central_cubic']));hlinear=scalar[(0,0,1)]
    h_cubic=cn(cm(kappa,ci(hlinear)))
    assert hlinear==(Q(6,5),Q(0))and h_cubic==(Q(5,6),Q(8,35))
    assert scalar.get((1,0,0),ZERO)==scalar.get((2,0,0),ZERO)==ZERO

    b={(1,0,0):ONE};U={(0,1,0):ONE};h={(0,0,1):ONE}
    target_z=decode(result['target_z_jet'])
    implicit=[decode(result['implicit_jets'][name])for name in ('C','E','k','l','m')]
    negative=0
    bad_z=add(target_z,U)
    negative+=rejects(lambda:check_equal(coefficient_equations(G,b,U,h,bad_z,implicit)[0],{}))
    bad_implicit=[p.copy()for p in implicit];bad_implicit[0]=add(bad_implicit[0],h)
    negative+=rejects(lambda:check_equal(coefficient_equations(G,b,U,h,target_z,bad_implicit)[1],{}))
    bad_scalar=add(scalar,{(3,0,0):ONE})
    negative+=rejects(lambda:check_equal(bad_scalar,coefficient_equations(G,b,U,h,target_z,implicit)[6]))
    negative+=rejects(lambda:check_equal(packet['T1_parameter_matrix'][0][0],['1','0']))
    negative+=rejects(lambda:check_equal(h_cubic,(Q(0),Q(0))))
    receipt={'schema':'cyclic-fano-unfolding-axis-independent-v1','status':'PASS','parameter_direction':direction_name,
             'checker_lf_sha256':sha(Path(__file__)),'packet_lf_sha256':sha(path),
             'source_instance_lf_sha256':result['source_instance_lf_sha256'],
             'arithmetic':'Python standard-library Fraction pairs; independent raw-source polynomial composition and simultaneous Hensel elimination; no producer or CAS import',
             'jet_order':ORDER,'target_equation_exactly_reconstructed':True,
             'target_z_jet_checked':True,'physical_unknown_jets_checked':5,
             'physical_incidence_coefficients_zero_through_order4':list(range(6)),
             'physical_first_five_jacobian_determinant':result['physical_first_five_jacobian_determinant'],
             'scalar_germ_jet':result['remaining_sixth_equation_jet'],
             'central_cubic':result['central_cubic'],'central_quartic':result['central_quartic'],
             'T1_rank':1,'T1_matrix':result['T1_matrix'],
             'prepared_constant_linear_parameter_matrix':result['prepared_constant_linear_parameter_matrix'],
             'genuine_seed_path_smoothing':{'g_h_at_origin':strings(hlinear),'h_of_b_cubic_coefficient':strings(h_cubic),
                  'ramification_index':3,'local_sheet_monodromy':'a three-cycle, up to labeling and orientation',
                  'argument':'The implicit function theorem gives h(b)=alpha*b^3+O(b^4), alpha nonzero. A local analytic cube root of the unit changes b to w with h=w^3.'},
             'local_flatness':'On the selected target surface germ, the scalar is b-regular of order three. Weierstrass preparation identifies its completed/analytic local algebra with a monic cubic quotient, finite and free of rank three over the local target base.',
             'failed_approach':'This selected two-parameter surface has T1 rank one, so this computation does not establish a versal two-parameter unfolding or cusp branch equation.',
             'limits':'These are local jets on an actual fixed-hypersurface target surface. No quantitative convergence radius, full-target discriminant, global branch/support divisor, seed-component degree, certificate or Lean proof follows.',
             'negative_controls_rejected':negative}
    return receipt

def main():
    axes=[audit_axis(i)for i in (0,3,5)]
    matrices=[[[tuple(map(Q,x))for x in row]for row in a['T1_matrix']]for a in axes]
    full=[[matrices[0][row][0],matrices[1][row][0],matrices[0][row][1],matrices[2][row][0]]for row in range(2)]
    for row in range(2):
        assert full[row][0]==full[row][1]==ZERO
        assert all(m[row][1]==full[row][2]for m in matrices)
        assert full[row][3]==cm((Q(0),Q(-1)),full[row][2])
    assert full[0][2]==(Q(6,5),Q(0))
    summary=load(OUT/'unfolding.json')
    assert summary['schema']=='cyclic-fano-unfolding-summary-v1'
    assert summary['producer_sha256']==sha(ROOT/'experiments/cyclic_fano_unfolding.py')
    assert summary['fixed_target_manifest_sha256']==sha(CURVE/'target.json')
    assert summary['axis_packet_sha256']=={a['parameter_direction']:a['packet_lf_sha256']for a in axes}
    assert summary['full_T1_matrix']==[[strings(row[j])for j in (0,1,3,2)]for row in full]
    assert summary['full_T1_rank']==1 and summary['miniversal']is False
    tangent_basis=[[ONE,ZERO,ZERO,ZERO],[ZERO,ONE,ZERO,ZERO],
                   [ZERO,ZERO,ZERO,ONE],[ZERO,ZERO,ONE,II]]
    assert summary['target_tangent_basis_matrix']==[[strings(x)for x in row]for row in tangent_basis]
    assert summary['target_tangent_basis_determinant']==strings(inverse(tangent_basis)[1])==['-1','0']
    scalar=decode(axes[0]['scalar_germ_jet']);gh=scalar[(0,0,1)]
    a3=cn(cm(scalar[(3,0,0)],ci(gh)))
    a4=cn(cm(ca(scalar[(4,0,0)],cm(scalar[(1,0,1)],a3)),ci(gh)))
    assert a3==(Q(5,6),Q(8,35))and a4==(Q(-97,70),Q(-2227,210))
    hseries=[ZERO,ZERO,ZERO,a3,a4]
    assert summary['h_of_b_jet_coefficients_ascending']==list(map(strings,hseries))
    assert summary['h_of_b_remainder']=='O(b^5)'and summary['ramification_index']==3
    # Substitute the derived branch into the complete four-jet, retaining the
    # original b-coordinate, rather than drawing conclusions from a model alone.
    branch={(3,0,0):a3,(4,0,0):a4};substitution={}
    for mon,c in scalar.items():
        if mon[1]:continue
        term=multiply({(mon[0],0,0):c},power(branch,mon[2],ZLOCAL,ORDER),ORDER)
        substitution=add(substitution,term)
    assert not substitution
    receipt={'schema':'cyclic-fano-unfolding-independent-v1','status':'PASS',
             'checker_lf_sha256':sha(Path(__file__)),'summary_packet_lf_sha256':sha(OUT/'unfolding.json'),'axes':axes,
             'all_four_target_directions':{'coordinates':['U','V','h','W'],
                 'target_chart':'(X0,Y0,Y1,Y2)=(U,i+V,1+h,i(1+h)+W); Z is solved by G_Z=5i/7 at the origin.',
                 'T1_matrix':[[strings(x)for x in row]for row in full],
                 'T1_rank':1,'argument':'The three axis computations supply U,V,W derivatives and the common h derivative. These four are independent target coordinates, so this is the full first-order T1 map.',
                 'conclusion':'The full target evaluation unfolding fails the first-order versality test at this triple point. A cusp branch normal form is not established.'},
             'actual_seed_path_branch_jet':{'h_coefficients_ascending':list(map(strings,hseries)),
                 'remainder':'O(b^5)','substitution_into_scalar_four_jet_zero':True},
             'negative_controls_rejected':sum(a['negative_controls_rejected']for a in axes),
             'limits':'The h path has a certified local degree-three smoothing and three-cycle monodromy. The complete target branch germ and all global boundary/support equations remain uncomputed.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'independent-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','jet_order':ORDER,'axes':3,'full_T1_rank':1,'negative_controls':receipt['negative_controls_rejected']}))

if __name__=='__main__':main()
