"""Optional: rebuild the shareable PDF/PNG charts. Requires matplotlib."""
from pathlib import Path
import json,textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from run_simulations import read_raw
ROOT=Path(__file__).resolve().parent
cases=json.loads((ROOT/'cases.json').read_text());report=json.loads((ROOT/'results/VALIDATION.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,'pdf.fonttype':42})
with PdfPages(ROOT/'Simulation_Report.pdf') as pdf:
    fig=plt.figure(figsize=(11.7,8.3));fig.patch.set_facecolor('#f5f8f6')
    fig.text(.08,.88,'SOLAR BATTERY CHARGER',fontsize=26,weight='bold',color='#173e3b')
    fig.text(.08,.81,'Simulation demonstration and results',fontsize=19,color='#36534a')
    lines=[
        'Open START_HERE.html in Microsoft Edge, Chrome, or Firefox for the interactive viewer.',
        'Seven completed ngspice transient runs; '+str(report['passed'])+' numerical checks passed; '+str(report['failed'])+' failed.',
        'Educational averaged behavioral equivalent, NOT the manufacturer LT3652 macromodel.',
        'This demonstrates modeled behavior; it does not prove the physical PCB works.',
        'Design targets: 4.20 V / 500 mA, 0.20 ohm sense resistor, nominal 12 V solar panel.',
        'Demonstration assumptions: 2.5 Ah model cell; 0.15 ohm cell resistance; fixed 88% efficiency.',
        'Time scaling: 1 SPICE second = 1 modeled charging hour. Real charging time is not validated.',
    ]
    y=.71
    for line in lines:
        for s in textwrap.wrap(line,105):fig.text(.08,y,s,fontsize=11,color='#30483e');y-=.035
        y-=.019
    fig.text(.08,.22,'Demonstrated conditions',fontsize=13,weight='bold',color='#173e3b')
    fig.text(.08,.16,'Normal charge / taper / finish · Hot and cold faults · Cloud / night / sunrise\nBad-battery timeout · Preconditioning · Load / recharge · Disconnected sensor',fontsize=11,linespacing=1.7)
    fig.text(.08,.06,'Read README.md for reproduction steps, modeling assumptions, and limitations.',fontsize=9,color='#627468')
    pdf.savefig(fig);plt.close(fig)
    for k,c in enumerate(cases,1):
        names,rows=read_raw(ROOT/'results'/(c['id']+'.raw'));rows=[r for r in rows if r[0]>.01];ix={n:i for i,n in enumerate(names)}
        t=[r[0] for r in rows]
        def v(n,scale=1):return [r[ix[n]]*scale for r in rows]
        fig,ax=plt.subplots(2,2,figsize=(11.7,8.3));fig.subplots_adjust(top=.80,bottom=.12,wspace=.26,hspace=.39)
        fig.suptitle(f"{k:02d}  {c['name']}",x=.08,y=.96,ha='left',fontsize=18,weight='bold',color='#173e3b')
        fig.text(.08,.905,'\n'.join(textwrap.wrap(c['description'],140)),fontsize=10,color='#506258')
        fig.text(.08,.844,'EDUCATIONAL BEHAVIORAL MODEL — not an LT3652 manufacturer-model or PCB validation',fontsize=9,weight='bold',color='#8a6031')
        ax[0,0].plot(t,v('v(bat)'),color='#356ba1',lw=1.5,label='Battery terminal')
        ax[0,0].axhline(4.2,color='#9a9a9a',ls='--',lw=.8,label='4.20 V target');ax[0,0].set(ylabel='Battery voltage (V)',ylim=(2.6,4.3));ax[0,0].legend(loc='lower right',fontsize=8)
        ax[0,1].plot(t,v('i(vsense)',1000),color='#b78021',lw=1.5,label='Charger output')
        ax[0,1].plot(t,v('i(vbatmon)',1000),color='#16845e',lw=1.0,alpha=.8,label='Net cell current');ax[0,1].set(ylabel='Current (mA)',ylim=(-200,550));ax[0,1].legend(fontsize=8)
        ax[1,0].plot(t,v('i(vled_green)',1000),color='#16845e',lw=1.4,label='Green LED')
        ax[1,0].plot(t,v('i(vled_red)',1000),color='#c54442',lw=1.4,label='Red LED');ax[1,0].set(ylabel='LED branch current (mA)',ylim=(-.05,2.6));ax[1,0].legend(fontsize=8)
        ax[1,1].plot(t,v('v(temp_c)'),color='#b85b48',lw=1.2,label='Sensor temperature');ax[1,1].set(ylabel='Sensor temperature (°C)',ylim=(-15,65));ay=ax[1,1].twinx();ay.spines['right'].set_visible(True);ay.plot(t,v('v(sun)',100),color='#7e8f3f',lw=1.0,ls='--',label='Sunlight');ay.set(ylabel='Relative sunlight (%)',ylim=(-5,110));ay.grid(False)
        ax[1,1].legend(loc='lower left',fontsize=8);ay.legend(loc='upper right',fontsize=8)
        for a in ax.flat:a.set(xlabel='Modeled charging time (hours)',xlim=(0,c['duration']))
        fig.text(.08,.045,'1 SPICE second = 1 modeled hour. Hour-scale plots; startup and fast transients are not validated. Full data: results/*.csv.',fontsize=8,color='#627468')
        pdf.savefig(fig)
        if k in [1,2,4]:fig.savefig(ROOT/'previews'/('Waveforms_'+c['id']+'.png'),dpi=150)
        plt.close(fig)
print('Generated Simulation_Report.pdf (8 pages) and standalone waveform figures.')
