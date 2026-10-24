from pathlib import Path
import concurrent.futures,json,subprocess
root=Path.cwd();manifest=json.loads((root/'formal/lake-manifest.json').read_text())
def one(p):
 if p['name']=='mathlib':return
 d=root/'formal/.lake/packages'/p['name'];d.mkdir(parents=True,exist_ok=True)
 subprocess.run(['git','init',str(d)],check=True,capture_output=True)
 subprocess.run(['git','-C',str(d),'remote','add','origin',p['url']],check=True)
 subprocess.run(['python3','results/skew-physical-curve-20261024/run_bounded.py','--out','results/skew-physical-curve-20261024/bootstrap/fetch-'+p['name'],'--timeout','45','--','git','-C',str(d),'fetch','--depth','1','origin',p['rev']],check=True)
 subprocess.run(['git','-C',str(d),'checkout','--detach','FETCH_HEAD'],check=True,capture_output=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(one,manifest['packages']))
