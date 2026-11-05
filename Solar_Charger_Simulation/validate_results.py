"""Quantitative regression checks on completed ngspice runs; no third-party packages."""
from pathlib import Path
import json,math
from run_simulations import read_raw,sample
ROOT=Path(__file__).resolve().parent
checks=[];loaded={}
def row(case,t):
    if case not in loaded:loaded[case]=read_raw(ROOT/'results'/(case+'.raw'))
    names,rows=loaded[case];return dict(zip(names,sample(names,rows,t)))
def check(name,condition,detail):
    checks.append({'check':name,'passed':bool(condition),'evidence':detail})
def near(x,y,tol):return abs(x-y)<tol
def currents(r):return {n:round(r[n]*1000,6) for n in ['i(vsense)','i(vbatmon)','i(vled_green)','i(vled_red)']}
def on(r,colour):return r['i(vled_'+colour+')']>.00005

def main():
    checks.clear();a=row('01_normal_charge',.2);b=row('01_normal_charge',3.5);c=row('01_normal_charge',4.5);d=row('01_normal_charge',6.5)
    check('Normal constant-current charge at 500mA',near(a['i(vsense)'],.5,.002),currents(a))
    check('Battery voltage increases during charging',b['v(bat)']>a['v(bat)']+.5,{'start_V':a['v(bat)'],'later_V':b['v(bat)']})
    check('Green on, red off during normal charging',on(a,'green') and not on(a,'red'),currents(a))
    check('Current tapers near 4.2V',.001<c['i(vsense)']<.05 and 4.18<c['v(bat)']<4.21,{'battery_V':c['v(bat)'],**currents(c)})
    check('Both LEDs can be off before timer completion',not on(c,'green') and not on(c,'red') and c['v(done)']<.1 and c['i(vsense)']>.001,currents(c))
    check('Timer termination stops charging',d['v(done)']>.9 and abs(d['i(vsense)'])<1e-6,{'done':d['v(done)'],**currents(d)})
    check('Battery voltage stays below 4.21V after startup',max(r[loaded['01_normal_charge'][0].index('v(bat)')] for r in loaded['01_normal_charge'][1] if r[0]>.01)<4.21,'Evaluated all completed normal-charge samples after 0.01h.')
    for t,what in [(1.5,'Hot'),(3.5,'Cold')]:
        r=row('02_temperature_faults',t);check(what+' sensor fault stops charging',r['v(temp_fault)']>.9 and abs(r['i(vsense)'])<1e-6,{'sensor_C':r['v(temp_c)'],**currents(r)});check(what+' fault lights both LEDs',on(r,'green') and on(r,'red'),currents(r))
    for t in [2.5,4.5]:
        r=row('02_temperature_faults',t);check('Temperature recovery resumes charging at '+str(t)+'h',r['v(temp_fault)']<.1 and r['i(vsense)']>.1 and on(r,'green') and not on(r,'red'),currents(r))
    r=row('03_sunlight_changes',1.5);check('Partial sunlight reduces current',.01<r['i(vsense)']<.4,{'panel_V':r['v(vin)'],**currents(r)})
    r=row('03_sunlight_changes',2.5);check('Very weak light can stop charging before full',abs(r['i(vsense)'])<1e-6 and r['v(soc)']<.9 and not on(r,'green') and not on(r,'red'),{'soc':r['v(soc)'],**currents(r)})
    r=row('03_sunlight_changes',3.5);check('Night turns charging and LEDs off',r['v(vin)']<1 and abs(r['i(vsense)'])<1e-6 and not on(r,'green') and not on(r,'red'),{'panel_V':r['v(vin)'],**currents(r)})
    r=row('03_sunlight_changes',4.5);check('Sunrise resumes charging',r['i(vsense)']>.4 and on(r,'green'),currents(r))
    r=row('04_bad_battery',.1);check('Faulted low cell initially receives 75mA preconditioning',near(r['i(vsense)'],.075,.001) and r['v(bad_fault)']<.1,currents(r))
    r=row('04_bad_battery',.5);check('Bad-battery timeout stops charge and lights red only',r['v(bad_fault)']>.9 and abs(r['i(vsense)'])<1e-6 and on(r,'red') and not on(r,'green'),currents(r))
    r=row('05_preconditioning',.05);check('Recoverable low cell starts at 75mA',near(r['i(vsense)'],.075,.001),currents(r))
    r=row('05_preconditioning',.3);check('Recoverable low cell reaches normal charging',near(r['i(vsense)'],.5,.002) and r['v(bad_fault)']<.1,currents(r))
    r=row('06_load_restart',7.5);check('External load discharges finished cell',r['v(done)']>.9 and r['i(vbatmon)']<-.14,{'battery_V':r['v(bat)'],**currents(r)})
    r=row('06_load_restart',8.5);check('Charger restarts after discharge',r['v(done)']<.1 and r['i(vsense)']>.15 and r['i(vbatmon)']>0 and on(r,'green'),currents(r))
    r=row('07_sensor_open',1.5);check('Open sensor disables monitoring rather than raising a fault',r['v(ntc_open)']>.9 and r['v(temp_c)']>50 and r['v(temp_fault)']<.1 and r['i(vsense)']>.4 and not on(r,'red'),{'sensor_C':r['v(temp_c)'],**currents(r)})
    r=row('07_sensor_open',2.5);check('Reconnecting hot sensor triggers temperature fault',r['v(temp_fault)']>.9 and abs(r['i(vsense)'])<1e-6 and on(r,'green') and on(r,'red'),currents(r))
    for case in json.loads((ROOT/'cases.json').read_text()):
        ns,rs=read_raw(ROOT/'results'/(case['id']+'.raw'))
        settled=[dict(zip(ns,r)) for r in rs if r[0]>.01]
        check(case['id']+': complete transient, bounded charge and LED current',near(rs[-1][0],case['duration'],1e-6) and all(-1e-6<=r['i(vsense)']<=.501 and r['i(vled_green)']<.0028 and r['i(vled_red)']<.0028 for r in settled),{'points':len(rs),'completed_h':rs[-1][0]})
        max_error=max(abs(r['v(sense)']-r['v(bat)']-.2*r['i(vsense)']) for r in settled)
        check(case['id']+': 0.20ohm sense resistor voltage/current',max_error<1e-7,{'maximum_Ohms_law_error_V':max_error})
    ns,rs=read_raw(ROOT/'results/01_normal_charge.raw');rs=[r for r in rs if r[0]>.02];j=ns.index('i(vbatmon)');k=ns.index('v(soc)')
    ah=sum((b[0]-a[0])*(a[j]+b[j])/2 for a,b in zip(rs,rs[1:]));change=(rs[-1][k]-rs[0][k])*2.5
    check('Battery SOC agrees with integrated cell current',abs(ah-change)<.001,{'integrated_Ah':ah,'SOC_change_times_capacity_Ah':change})
    report={'scope':'Regression of an EDUCATIONAL behavioral model; not manufacturer-model or physical PCB validation.','simulator':'ngspice 44.2','passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'checks':checks}
    (ROOT/'results/VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"{report['passed']} passed; {report['failed']} failed.")
    for c in checks:
        if not c['passed']:print('FAIL',c['check'],c['evidence'])
    if report['failed']:raise SystemExit(1)
    return report
if __name__=='__main__':main()
