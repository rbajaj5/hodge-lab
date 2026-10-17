#!/usr/bin/env python3
"""Render the actual cyclic-character correction maps, after exact validation."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import cyclic_fano_transfer as audit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-transfer-figures'
SOURCE=ROOT/'results/cyclic-fano-transfer'


def main():
    packet=json.loads((SOURCE/'packet.json').read_text(encoding='utf-8'))
    assert packet==audit.calculate()
    receipt=json.loads((SOURCE/'validation.json').read_text(encoding='utf-8'))
    assert receipt['status']=='PASS' and receipt['packet_sha256']==audit.poly.sha(SOURCE/'packet.json')
    independent=json.loads((SOURCE/'independent-validation.json').read_text(encoding='utf-8'))
    assert independent['status']=='PASS' and independent['packet_lf_sha256']==audit.poly.sha(SOURCE/'packet.json')
    assert independent['checker_lf_sha256']==audit.poly.sha(ROOT/'experiments/check_cyclic_fano_transfer.py')
    OUT.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none','svg.hashsalt':'cyclic-fano-transfer','axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(15,8.4))
    fig.patch.set_facecolor('#fcfaf5')
    fig.suptitle('Cyclic symmetry reduces the search; three geometric denominators still fail',x=.04,ha='left',y=.97,fontsize=18,fontweight='bold',color='#153a42')
    fig.text(.04,.905,'Fixed cyclic-triple-fano target  |  '+r'$X_2\mapsto\zeta_3 X_2$'+'  |  Degree-three denominators',fontsize=12,color='#50616b')
    fig.text(.04,.855,r'756 numerator coefficients  $\longrightarrow$  150 after the exact character projector and Piola transfer',fontsize=14,color='#087f83')
    names=[r'Cyclic-cover branch: $E=Z$',r'Quadratic branch: $E=2Z+Q$',r'Omitted section: $E=X_1^3$']
    summaries=[]
    for ax,test,title in zip(axes,packet['tests'],names):
        ax.set_facecolor('#fcfaf5');split=sum(row[0]=='E1' for row in test['coefficient_rows'])
        for equation,color in [('E1','#087f83'),('E2','#8065ac')]:
            xx=[];yy=[]
            for j,column in enumerate(test['columns']):
                for i,_ in column:
                    if test['coefficient_rows'][i][0]==equation:xx.append(j);yy.append(i)
            ax.scatter(xx,yy,s=2,c=color,marker='s',linewidths=0,rasterized=False)
        ax.scatter([155]*len(test['rhs']),[i for i,_ in test['rhs']],s=16,c='#d55246',marker='D',linewidths=0)
        ax.axvline(151.5,color='#bdc7c7',lw=.8)
        ax.axhline(split-.5,color='#bdc7c7',lw=.8)
        ax.set_xlim(-3,160);ax.set_ylim(test['shape'][0]-.5,-.5)
        ax.set_xticks([0,50,100,155],['0','50','100','RHS'])
        ax.set_title(title,fontsize=12,pad=13)
        ax.set_xlabel('Weighted numerator column')
        ax.set_ylabel('Supported coefficient row')
        ax.text(.02,-.17,f"{test['shape'][0]} rows × 150 columns\nExact ranks: 150 → 151\nDual witness: {len(test['dual'])} coefficient terms",transform=ax.transAxes,va='top',fontsize=11,color='#153a42',linespacing=1.7)
        summaries.append({'candidate':test['candidate'],'shape':test['shape'],'rank':test['rank'],'augmented_rank':test['augmented_rank'],'dual_terms':len(test['dual']),'equation1_rows':split})
    fig.legend(handles=[Line2D([],[],marker='s',linestyle='',color='#087f83',label='E1: normal equation'),Line2D([],[],marker='s',linestyle='',color='#8065ac',label='E2: divergence equation'),Line2D([],[],marker='D',linestyle='',color='#d55246',label='Required right side')],loc='lower left',bbox_to_anchor=(.04,.06),frameon=False,ncol=3)
    fig.text(.04,.035,'Each exact dual annihilates every column and evaluates to 1 on the right side. Other denominators, powers, and products remain untested.',fontsize=10,color='#50616b')
    fig.subplots_adjust(top=.76,bottom=.29,left=.06,right=.98,wspace=.30)
    for ext in ('png','svg'):
        path=OUT/f'cyclic-fano-character-maps.{ext}'
        fig.savefig(path,dpi=180,facecolor=fig.get_facecolor(),metadata={'Date':None}if ext=='svg'else None)
        if ext=='svg':path.write_text('\n'.join(line.rstrip()for line in path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
    plt.close(fig)
    data={'status':'PASS','packet_sha256':audit.poly.sha(SOURCE/'packet.json'),'validation_sha256':audit.poly.sha(SOURCE/'validation.json'),'independent_validation_sha256':audit.poly.sha(SOURCE/'independent-validation.json'),'plot_script_sha256':audit.poly.sha(Path(__file__)),'maps':summaries,'scope':'Actual coefficient occupancy; exact ranks come from arithmetic checks, not image appearance.'}
    (OUT/'plot-data.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(data))


if __name__=='__main__':main()
