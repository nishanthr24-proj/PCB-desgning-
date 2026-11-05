"""Generate portable SPICE testbenches. No external Python packages needed."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
CASES=[
 dict(id='01_normal_charge',name='Charge, taper, and finish',duration=8,soc=.2,
      sun='1',temp='25',load='0',stall='0',ntc='0',
      description='Bright sunlight: charge at 500 mA, approach 4.2 V, taper below the green-LED threshold, then reach timer termination.',
      events=[(0,'Bright sunlight; charging begins'),(3.0,'First timer cycle retries if the cell is not near full'),(4.5,'Green off during taper does not mean charging has ended'),(6.0,'Second timer cycle can terminate charging')]),
 dict(id='02_temperature_faults',name='Hot / cold fault and recovery',duration=6,soc=.25,
      sun='1',temp='PWL(0 25 1 25 1.001 55 2 55 2.001 25 3 25 3.001 -10 4 -10 4.001 25 6 25)',load='0',stall='0',ntc='0',
      description='55 C and -10 C sensor conditions pause charging and light both LEDs. Returning to 25 C resumes charging.',
      events=[(1,'Temperature rises to 55 C'),(2,'Temperature returns to 25 C'),(3,'Temperature falls to -10 C'),(4,'Temperature returns to 25 C')]),
 dict(id='03_sunlight_changes',name='Clouds, night, and sunrise',duration=6,soc=.25,
      sun='PWL(0 1 1 1 1.001 0.15 2 0.15 2.001 0.02 3 0.02 3.001 0 4 0 4.001 1 6 1)',temp='25',load='0',stall='0',ntc='0',
      description='Partial cloud reduces available charging current. Very weak light can stop charging while the battery is not full. Night turns the solar-powered LEDs off.',
      events=[(1,'Partial cloud: 15% irradiance'),(2,'Very weak light: 2% irradiance'),(3,'Night: no sunlight'),(4,'Sunrise: full irradiance')]),
 dict(id='04_bad_battery',name='Bad-battery timeout',duration=1.2,soc=.0,
      sun='1',temp='25',load='0',stall='1',ntc='0',
      description='Fault-injection fixture: the cell voltage does not rise despite preconditioning current. After about 22.4 minutes the red LED turns on and charging stops.',
      events=[(0,'Fault injection: battery cannot recover voltage'),(.374,'Preconditioning timeout near 22.4 minutes')]),
 dict(id='05_preconditioning',name='Recover a low-voltage model cell',duration=1.5,soc=.01,
      sun='1',temp='25',load='0',stall='0',ntc='0',
      description='An approximately 2.85 V model cell starts at 75 mA preconditioning, rises above the threshold, and moves to 500 mA charging. This is not permission to recover a damaged real cell.',
      events=[(0,'75 mA preconditioning'),(.3,'Normal charging after model voltage recovers')]),
 dict(id='06_load_restart',name='Full battery, load, and recharge',duration=12,soc=.2,
      sun='1',temp='25',load='PWL(0 0 7 0 7.001 0.15 10 0.15 10.001 0 12 0)',stall='0',ntc='0',
      description='After timer termination a 150 mA external load discharges the cell. Below the recharge threshold the charger restarts. An external load can affect charging and termination.',
      events=[(6,'Timer termination expected near this time'),(7,'150 mA external load connected'),(10,'External load removed')]),
 dict(id='07_sensor_open',name='Disconnected temperature sensor',duration=3,soc=.25,
      sun='1',temp='PWL(0 25 1 25 1.001 55 3 55)',load='0',stall='0',ntc='PWL(0 0 0.9 0 0.901 1 2 1 2.001 0 3 0)',
      description='Opening the NTC disables temperature monitoring; it does not produce an open-sensor alarm. Reconnecting it at 55 C produces the temperature fault.',
      events=[(.9,'Sensor disconnected: monitoring disabled'),(1,'Cell sensor temperature becomes 55 C'),(2,'Sensor reconnected while hot')]),
]
for c in CASES:
    text='Solar charger behavioral demonstration: '+c['name']+'\n'
    text+='* EDUCATIONAL AVERAGED MODEL, not the manufacturer LT3652 model.\n'
    text+='* 1 simulation second represents 1 hour of charging.\n'
    text+=f".param SOC0={c['soc']}\n"
    for ref,node,key in [('VSUN','sun','sun'),('VTEMP','temp_c','temp'),('VLOAD','load','load'),('VSTALL','stall','stall'),('VNTCOPEN','ntc_open','ntc')]:
        text+=f"{ref} {node} 0 {c[key]}\n"
    text+='.include "behavioral_core.inc"\n'
    text+=f".tran 0.001 {c['duration']} 0 0.001 uic\n"
    text+='.save V(VIN) V(BAT) V(SENSE) V(SOC) V(TEMP_C) V(SUN) V(NTC) V(TEMP_FAULT) V(BAD_FAULT) V(DONE) V(CLOCK) V(VIN_REG) V(NTC_OPEN) V(LOAD) I(VSENSE) I(VBATMON) I(VLED_GREEN) I(VLED_RED)\n'
    text+='.end\n'
    (ROOT/'spice'/(c['id']+'.cir')).write_text(text)
(ROOT/'cases.json').write_text(json.dumps(CASES,indent=2)+'\n')
print('Generated',len(CASES),'SPICE testbenches.')
