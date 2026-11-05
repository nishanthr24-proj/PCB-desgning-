"""Run the actual SPICE testbenches and export CSV/viewer data. Python 3 stdlib.

Usage: python run_simulations.py --ngspice /path/to/ngspice
Requires ngspice 44 or newer on PATH (or supply --ngspice).
"""
from pathlib import Path
import argparse,subprocess,re,struct,csv,json,math,bisect,shutil,sys
ROOT=Path(__file__).resolve().parent

def read_raw(path):
    data=path.read_bytes();head,body=data.split(b'Binary:\n',1);head=head.decode('utf-8',errors='replace')
    nv=int(re.search(r'No. Variables:\s*(\d+)',head)[1]);nr=int(re.search(r'No. Points:\s*(\d+)',head)[1])
    names=[row.split()[1].lower() for row in head.split('Variables:\n',1)[1].splitlines() if row.strip()]
    assert len(names)==nv,(path,names,nv)
    rows=list(struct.iter_unpack('<'+'d'*nv,body))
    assert len(rows)==nr,(path,len(rows),nr)
    assert all(math.isfinite(x) for row in rows for x in row),(path,'Non-finite data')
    return names,rows

def sample(names,rows,t):
    times=[r[0] for r in rows];j=min(len(rows)-1,bisect.bisect_left(times,t))
    if j==0:return list(rows[0])
    a,b=rows[j-1],rows[j];q=(t-a[0])/max(1e-30,b[0]-a[0])
    return [x+q*(y-x) for x,y in zip(a,b)]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ngspice',default=shutil.which('ngspice'));args=parser.parse_args()
    if not args.ngspice:parser.error('Install ngspice or specify --ngspice /path/to/ngspice')
    cases=json.loads((ROOT/'cases.json').read_text());out=ROOT/'results';out.mkdir(exist_ok=True)
    package={'model':'Educational averaged behavioral equivalent; NOT the manufacturer LT3652 macromodel.','time_scale':'1 simulation second represents 1 hour','cases':[]}
    summary=[]
    for c in cases:
        stem=c['id'];raw=out/(stem+'.raw');log=out/(stem+'.log')
        result=subprocess.run([str(args.ngspice),'-b','-r',str(raw),'-o',str(log),stem+'.cir'],cwd=ROOT/'spice',capture_output=True,text=True,timeout=120)
        if result.returncode:raise RuntimeError(f'{stem}: ngspice exit {result.returncode}\n'+log.read_text())
        lt=log.read_text()
        if not re.search(r'No\. of Data Rows\s*:\s*[1-9]\d*',lt) or re.search(r'aborted|fatal|timestep too small|Error:',lt,re.I):raise RuntimeError(f'{stem}: simulation did not complete\n'+lt)
        names,rows=read_raw(raw)
        if rows[-1][0]<c['duration']-1e-7:raise RuntimeError(f'{stem}: transient stopped early')
        for v in ['v(bat)','i(vsense)','i(vled_green)','i(vled_red)']:assert v in names,(stem,'Missing trace',v)
        with (out/(stem+'.csv')).open('w',newline='') as f:
            w=csv.writer(f,lineterminator='\n');w.writerow(['time_h' if n=='time' else n for n in names]);w.writerows(rows)
        # Uniform playback plus exact event boundaries. All values are from SPICE,
        # interpolated for the viewer; there are no scripted LED states.
        ts={round(c['duration']*i/600,8) for i in range(601)}
        for t,_ in c['events']:
            ts.update(round(max(0,min(c['duration'],t+dx)),8) for dx in [-.002,-.0001,0,.0001,.001,.002,.005,.01])
        sampled=[[round(x,9) for x in sample(names,rows,t)] for t in sorted(ts)]
        package['cases'].append({**c,'columns':names,'data':sampled})
        diag={'case':stem,'points':len(rows),'completed_to_hours':rows[-1][0],'ngspice_exit':result.returncode}
        summary.append(diag);print('Completed',stem,':',len(rows),'points,',rows[-1][0],'virtual hours')
    (out/'viewer_data.json').write_text(json.dumps(package,separators=(',',':'))+'\n')
    (out/'run_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    # Update the self-contained browser viewer if it has already been generated.
    template=ROOT/'viewer_template.html'
    if template.exists():
        html=template.read_text().replace('/*__SIMULATION_DATA__*/',json.dumps(package,separators=(',',':')))
        (ROOT/'START_HERE.html').write_text(html)
    return package

if __name__=='__main__':main()
