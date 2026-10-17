"""Visualize post six's correction maps, exact duals, and proof dependencies.

The figures are derived from pinned proof packets, not a surface simulation.
--check checks the figure manifest and reruns the displayed cancellation
identities against stored physical equations; it does not rebuild F.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, gzip, hashlib, json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/degree7-rank-strata'
sys.path.insert(0,str(ROOT/'algebra'))
import degree7_syzygies as s

BG,FG,MUTED='#151a24','#f1f4f8','#abb8cc'
COLORS={16:'#61d4be',137:'#88b7ff'}
GOLD,PINK='#f4d67b','#e79ac9'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':FG,
 'axes.labelcolor':FG,'xtick.color':MUTED,'ytick.color':MUTED,'axes.edgecolor':MUTED,
 'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG,
 'svg.fonttype':'none','svg.hashsalt':'hodge-post-six'})


def read(path):
    if path.suffix=='.gz':
        with gzip.open(path,'rt',encoding='utf-8') as f:return json.load(f)
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    raw=path.read_bytes()
    if path.suffix in {'.json','.py','.md','.svg'}:raw=raw.replace(b'\r\n',b'\n')
    return hashlib.sha256(raw).hexdigest()


def collect():
    sources={}
    def source(name):
        path=OUT/name;sources[name]=digest(path);return read(path)
    manifest=source('koszul-manifest.json')
    validation=source('koszul-validation.json')
    independent=source('koszul-independent-validation.json')
    assert validation['status']==independent['status']=='PASS'
    assert validation['charts']==independent['charts']
    checks={(v['family'],v['pivot']):v for v in validation['charts']}
    paths=['koszul-16-11.json.gz']+[v['file'] for v in manifest['refinements']]
    paths += [v['file'] for v in manifest['family137_charts']]
    charts=[];packets={};matrices={};replayed=0;products=0
    for name in paths:
        p=source(name);key=(p['family'],p['pivot']);packets[key]=p
        nD=len(p['system']['basis_indices']);nK=len(p['system']['Koszul_indices'])
        assert (nD,nK)==(18,256) and checks[key]['excluded']
        rel=p.get('baseline',[])+[p['relations'][j] for j in p.get('selected_new',[])]
        count=sum(len(v['products']) for v in rel)
        assert len(rel)==checks[key].get('syzygy_identities',0)
        assert count==checks[key].get('physical_products',0)
        claims=[v for stage in p.get('continuation',{}).get('power_stages',[]) for v in stage['claims']]
        assert sum(len(v['products']) for v in claims)==checks[key].get('power_equation_products',0)
        method=('physical closure' if p.get('affine_chart',{}).get('excluded') else
                'syzygy closure' if 'denominator_contradiction' in p else
                'unit identity' if any(v.get('constant') for v in claims) else 'powers + closure')
        charts.append({'family':key[0],'pivot':key[1],'method':method,
                       'relations':len(rel),'baseline':len(p.get('baseline',[])),
                       'physical_products':count,'power_products':sum(len(v['products']) for v in claims),
                       'dependency':p.get('dependency_closed_chart')})
        if key in {(16,11),(137,13)}:
            rows=[s.cert.decode(v) for v in p['rows']]
            R=np.zeros((len(rows),nK),dtype=np.int32)
            for j,row in enumerate(rows):
                for mon,coef in row.items():
                    z=[i for i in mon if i>=nD];assert len(z)<=1
                    if z:R[j,z[0]-nD]+=1
            U=np.zeros((len(rel),len(rows)),dtype=np.int32)
            for i,v in enumerate(rel):
                products += s.verify_relation(rows,nD,p['variables'],v);replayed+=1
                assert len({(j,tuple(mon)) for j,mon,coef in v['products']})==len(v['products'])
                for j,mon,coef in v['products']:U[i,j]+=1
            assert int(U.sum())==count
            matrices[key]=(R,U)
    assert len(charts)==10 and sum(c['relations'] for c in charts)==685
    for family,pivot in [(16,11),(137,13)]:
        others=[c for c in charts if c['family']==family and c['pivot']!=pivot]
        assert len(others)==4 and all(c['dependency']==pivot for c in others)
    global_rows=source('global-linear-identities.json')
    for g in global_rows:
        assert [Q(v[1]) for v in g['square_identity']]==[Q(9,2),Q(-27)]
    attempts=[source(name) for name in ['attempts.json','followup-attempts.json',
              'family137-attempts.json','refinement-attempts.json','family137-refinement-attempts.json']]
    assert all(not source(f"chart-{v['family']}-{v['pivot']}.json.gz")['excluded'] for v in attempts[0])
    timeouts=[{'family':v['family'],'pivot':v['pivot'],'limit_seconds':v['timeout_seconds']}
              for group in attempts[1:3] for v in group if v['status']=='timeout']
    assert len(timeouts)==4
    local_checks=0
    for L in [Q(-2),Q(-1,2),Q(0),Q(1,3),Q(2)]:
        for w1,w2 in [(Q(1),Q(1)),(Q(1,10000),Q(1)),(Q(4),Q(1)),(Q(1),Q(4))]:
            r=[4*L,Q(2,3)*L];b=[Q(0),-L*L/27];u=[Q(9,2),Q(-27)]
            assert sum(x*y for x,y in zip(u,r))==0
            assert sum(x*y for x,y in zip(u,b))==L*L
            z=w2*L/(18*(36*w1+w2));e=[b[i]+r[i]*z for i in range(2)]
            assert w1*r[0]*e[0]+w2*r[1]*e[1]==0
            energy=w1*e[0]**2+w2*e[1]**2
            assert energy==4*w1*w2*L**4/(81*(36*w1+w2))
            if L:assert energy/(w2*b[1]**2)==36*w1/(36*w1+w2)
            else:assert r==b==e==[0,0]
            local_checks+=1
    data={'proof_commit':'17799c6c210373d4e7d2e9dcab837097161f8bfc',
          'charts':charts,'sources_sha256':sources,
          'displayed_cancellation_identities_replayed':replayed,
          'displayed_physical_products_replayed':products,'local_block_rational_checks':local_checks,
          'timeouts':timeouts,'scope':'Visual companion only; stored physical rows and passed prior reconstructions are inputs. No new family exclusion or geometric identification.'}
    return data,packets,matrices,global_rows


def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=170)
    svg=OUT/(name+'.svg')
    fig.savefig(svg,metadata={'Date':None})
    # Matplotlib emits trailing spaces in SVG path data; normalize for Git.
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',
                   encoding='utf-8',newline='\n')
    plt.close(fig)


def clean(ax):
    for spine in ax.spines.values():spine.set_visible(False)
    ax.tick_params(length=0)


def header(fig,title,subtitle):
    fig.text(.055,.95,title,fontsize=23,weight='bold')
    fig.text(.055,.91,subtitle,fontsize=11.5,color=MUTED)


def support_figure(data,packets,matrices):
    fig=plt.figure(figsize=(16,10))
    header(fig,'Seeing the Koszul correction map',
           'Post six · actual polynomial support after checked substitutions · both pivotal charts')
    binned={}
    for key,(R,U) in matrices.items():
        upad=np.pad(U,((0,0),(0,(-U.shape[1])%16)))
        binned[key]=upad.reshape(U.shape[0],-1,16).sum(axis=2)
    max_terms=max(int(v.max()) for v in binned.values())
    ticks=[v for v in [1,4,16,64,256,1024] if v<max_terms]+[max_terms]
    for f,x in [(16,.055),(137,.54)]:
        key=(f,11 if f==16 else 13);p=packets[key];R,U=matrices[key]
        nbase=len(p['baseline']);nrel=U.shape[0];nrows=R.shape[0]
        fig.text(x,.85,f'Family {f} · chart a{key[1]} = 1',color=COLORS[f],fontsize=16,weight='bold')
        # U columns group 16 consecutive physical rows, retaining every term.
        ub=binned[key]
        # R rows group eight physical equations; color counts nonzero cells.
        rpad=np.pad(R!=0,((0,(-nrows)%8),(0,0)))
        rb=rpad.reshape(-1,8,256).sum(axis=1)
        ax=fig.add_axes([x,.39,.245,.39])
        im=ax.imshow(np.ma.masked_equal(ub,0),aspect='auto',interpolation='nearest',
             cmap='viridis',norm=LogNorm(1,max_terms),extent=(-.5,ub.shape[1]*16-.5,nrel-.5,-.5))
        ax.axhline(nbase-.5,color=FG,lw=.8)
        ax.set_yticks([(nbase-1)/2,(nbase+nrel-1)/2],
                     [f'C1–{nbase}',f'A1–{nrel-nbase}'])
        ax.set_xticks([0,700,nrows-1]);ax.set_xlabel('Physical equation index',fontsize=10)
        ax.set_title(r'Selected left syzygies $U(a)$',loc='left',fontsize=12,pad=13)
        clean(ax)
        ax2=fig.add_axes([x+.29,.39,.14,.39])
        im2=ax2.imshow(rb,aspect='auto',interpolation='nearest',cmap='cividis',vmin=0,vmax=8,
                 extent=(-.5,255.5,rb.shape[0]*8-.5,-.5))
        ax2.set_xticks([0,128,255]);ax2.set_yticks([0,700,nrows-1]);ax2.yaxis.tick_right()
        ax2.set_xlabel('Correction index',fontsize=10)
        ax2.set_title(r'Map $R(a)$',loc='left',fontsize=12,pad=13);clean(ax2)
        ca=fig.add_axes([x,.31,.245,.015]);cb=fig.colorbar(im,cax=ca,orientation='horizontal',ticks=ticks)
        cb.set_ticklabels([str(v) for v in ticks]);cb.minorticks_off()
        cb.set_label('Multiplier terms / relation / 16-row bin',fontsize=9)
        ca2=fig.add_axes([x+.29,.31,.14,.015]);cb2=fig.colorbar(im2,cax=ca2,orientation='horizontal',ticks=[0,4,8])
        cb2.set_label('Nonzero cells / 8-row bin',fontsize=9)
        fig.text(x,.21,r'$U(a)R(a)=0\qquad U(a)b(a)=P(a)$',fontsize=17,color=COLORS[f])
        fig.text(x,.15,f'{nrel} displayed identities · {int(U.sum()):,} physical products\n'
                 f'{nrows:,} equations · all 256 correction coordinates shown',fontsize=11,color=MUTED,linespacing=1.8)
    fig.text(.055,.075,'C = constant multipliers; A = selected affine multipliers. Zero columns may reflect proved substitutions.',fontsize=11,color=MUTED)
    fig.text(.055,.04,'Colors count support, not coefficients or rank. Each family has its own equation order; U is not claimed to be the full syzygy module.',fontsize=10.5,color=MUTED)
    save(fig,'koszul-map-support')


def operator_figure():
    fig=plt.figure(figsize=(14,10))
    header(fig,'A syzygy sees what correction cannot remove',
           'The same exact two-row block occurs in both families · operator viewpoint inspired by the earlier Dubédat studies')
    fig.text(.055,.82,r'$R(L)=(4L,\;\frac{2}{3}L)^T\quad b(L)=(0,\;-L^2/27)^T$',fontsize=19)
    fig.text(.055,.755,r'$u=(\frac{9}{2},-27):\qquad uR=0,\qquad ub=L^2$',fontsize=20,color=COLORS[16])
    ax=fig.add_axes([.08,.31,.35,.36]);ax.set_aspect('equal',adjustable='box')
    xs=np.linspace(-.5,.65,100);ax.plot(xs,xs/6,color=MUTED,lw=2)
    b=np.array([0.,-1.]);p=np.array([-6/37,-1/37])
    for start,end,color in [(np.zeros(2),b,GOLD),(np.zeros(2),p,COLORS[137]),(p,b,PINK)]:
        ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'-|>','color':color,'lw':2.5,'mutation_scale':15})
    ax.text(.28,.10,'image of R',fontsize=11,color=MUTED)
    ax.text(.08,-1.02,'b',fontsize=15,color=GOLD)
    ax.text(-.51,-.12,'removable part',fontsize=10,color=COLORS[137])
    ax.text(.08,-.59,'cokernel\nremainder',fontsize=11,color=PINK,linespacing=1.6)
    ax.set_xlim(-.52,.68);ax.set_ylim(-1.15,.3)
    ax.set_xticks([-.5,0,.5]);ax.set_yticks([-1,-.5,0]);clean(ax)
    ax.set_xlabel('First row coordinate × 27',fontsize=10)
    ax.set_ylabel('Second row coordinate × 27',fontsize=10)
    ax.set_title('Euclidean projection at L = 1',loc='left',fontsize=12,pad=15)
    ax2=fig.add_axes([.56,.38,.37,.26]);rho=np.geomspace(1e-4,1e4,501)
    ax2.semilogx(rho,36*rho/(36*rho+1),color=GOLD,lw=2.8)
    ax2.scatter([1e-4,1],[36e-4/(36e-4+1),36/37],color=GOLD,s=35,zorder=4)
    ax2.annotate('0.36%',(1e-4,36e-4/(36e-4+1)),xytext=(12,16),textcoords='offset points',color=GOLD)
    ax2.annotate('97.3%',(1,36/37),xytext=(8,-23),textcoords='offset points',color=GOLD)
    ax2.set_ylim(-.04,1.08);ax2.set_yticks([0,.5,1],['0%','50%','100%'])
    ax2.set_xlabel(r'Equation weight ratio $\rho=w_1/w_2$')
    ax2.set_title('Metric changes the score, not solvability',loc='left',fontsize=12,pad=15)
    ax2.set_ylabel('Residual / initial weighted energy',fontsize=10);clean(ax2)
    fig.text(.56,.27,r'$\frac{\min_z\|b+Rz\|_W^2}{\|b\|_W^2}=\frac{36\rho}{36\rho+1}$',fontsize=18)
    fig.text(.56,.20,'Throughout this weight sweep: L = 1 and ub = 1.\nEvery positive weighting leaves the exact obstruction.',fontsize=11,color=MUTED,linespacing=1.7)
    fig.text(.055,.16,r'$G_W=R^TWR=(16w_1+\frac{4}{9}w_2)L^2$',fontsize=16)
    fig.text(.055,.105,'L ≠ 0: rank R = 1, rank [R | b] = 2     →     L = 0: both ranks are zero',fontsize=12,color=COLORS[16])
    fig.text(.055,.055,'At L = 0 this block passes; the other equations still need the chart proofs. Real plots illustrate an identity valid over C.',fontsize=10.5,color=MUTED)
    fig.text(.055,.025,'This is the actual holdout coefficient block, not a dimer operator, geometric Hodge decomposition, or new genus experiment.',fontsize=10.5,color=MUTED)
    save(fig,'koszul-operator-obstruction')


def dependency_figure(data):
    fig=plt.figure(figsize=(14.5,10.5))
    header(fig,'Why rebuilding closes all ten charts',
           'Post six · proof dependencies read from the archived packets · families 16 and 137 are labels, not genera')
    fig.text(.055,.835,r'$\frac{9}{2} E_j-27E_k=L^2=0\quad\Longrightarrow\quad L=0$',fontsize=21,color=GOLD)
    fig.text(.055,.795,'Two unnormalized equations; every exceptional rank case is retained.',fontsize=11,color=MUTED)
    for family,x,pivot in [(16,.055,11),(137,.54,13)]:
        ax=fig.add_axes([x,.19,.405,.55]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
        color=COLORS[family];items=[v for v in data['charts'] if v['family']==family]
        first=next(v for v in items if v['pivot']==pivot)
        ax.text(0,.97,f'Family {family}',fontsize=18,color=color,weight='bold')
        ax.text(0,.88,r'$L=0,\quad a_1=a_9=0$',fontsize=16)
        ax.text(0,.81,'All 256 allowed corrections included before reduction',fontsize=10,color=MUTED)
        ax.annotate('',xy=(.025,.73),xytext=(.025,.78),arrowprops={'arrowstyle':'-|>','color':color,'lw':1.7})
        ax.text(0,.66,rf'Close $a_{{{pivot}}}=1$',fontsize=15,weight='bold')
        ax.text(0,.59,f"Degree-four unit identity · {first['power_products']} multiplier terms",fontsize=10.5,color=MUTED)
        ax.annotate('',xy=(.025,.51),xytext=(.025,.56),arrowprops={'arrowstyle':'-|>','color':color,'lw':1.7})
        ax.text(0,.45,rf'Now $a_{{{pivot}}}=0$ throughout the family',fontsize=14,color=color)
        ax.text(0,.37,'Rebuild the other four normalized charts:',fontsize=11)
        for y,v in zip([.29,.22,.15,.08],[v for v in items if v['pivot']!=pivot]):
            ax.text(.015,y,rf'$a_{{{v["pivot"]}}}=1$',fontsize=12)
            detail=v['method']
            if v['power_products']:detail+=f" · {v['power_products']} terms"
            ax.text(.28,y,detail,fontsize=10.5,color=MUTED)
            ax.text(.95,y,'✓',fontsize=13,color=color,ha='right')
    fig.text(.055,.135,'All third-character coefficients vanish  →  the previously proved X0/Y0 pair exclusion applies.',fontsize=12)
    fig.text(.055,.09,'136/136 fixed-pair extensions excluded · 136/152 selected triples · holdout remains unsolved',fontsize=12,color=COLORS[16])
    fig.text(.055,.045,'History retained: ten unresolved local rank searches; four later timeouts; successful closure after proved reductions.',fontsize=10.5,color=MUTED)
    save(fig,'koszul-proof-dependencies')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    data,packets,matrices,global_rows=collect()
    path=OUT/'visualization-report.json'
    names=['koszul-map-support','koszul-operator-obstruction','koszul-proof-dependencies']
    if args.check:
        saved=read(path);assert saved['data']==data
        for name,value in saved['figures_sha256'].items():assert digest(OUT/name)==value
    else:
        support_figure(data,packets,matrices);operator_figure();dependency_figure(data)
        report={'data':data,'figures_sha256':{name+ext:digest(OUT/(name+ext)) for name in names for ext in ['.png','.svg']}}
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','figures':names,
        'displayed_syzygies_checked':data['displayed_cancellation_identities_replayed'],
        'physical_products_checked':data['displayed_physical_products_replayed'],
        'local_rational_checks':data['local_block_rational_checks']},indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    main()
