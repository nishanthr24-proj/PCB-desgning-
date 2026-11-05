* Solar charger, averaged EDUCATIONAL behavioral equivalent, Rev A simulation.
* NOT an Analog Devices LT3652 macromodel; NOT a pin-for-pin IC replacement.
* Time acceleration: 1 simulation second represents 1 charging hour.
* Actual resistor/LED networks + behavioral current-control and timer logic.
* No switching waveforms, magnetics, PCB parasitics, thermal loss model or EMC.
.param RSENSE=0.20 RFTOP=60k RFBOT=220k RIN_TOP=562k RIN_BOT=100k
.param VF={3.3*(1+RFTOP/RFBOT)} IMAX={0.100/RSENSE}
.param VPRE={VF*2.3/3.3} VRESTART={0.975*VF}
.param VREG={2.7*(1+RIN_TOP/RIN_BOT)} TEOC={0.68u*4.4e6}
.param QAH=2.5 RCELL=0.15 ETA=0.88 ISC=0.32 VOC=22 PV_A=1.5
.param IZERO={ISC/(exp(VOC/PV_A)-1)}

* Simple one-diode panel; sun is relative irradiance (0 to 1), not watts.
BPV 0 VIN I={ISC*max(0,V(sun))-IZERO*(exp(min(40,V(VIN)/PV_A))-1)}
CIN VIN 0 10u
RPV_LEAK VIN 0 10Meg
DNEG 0 VIN DCLAMP
.model DCLAMP D(Is=1n N=1 Rs=0.1)
RIN_TOP VIN VIN_REG {RIN_TOP}
RIN_BOT VIN_REG 0 {RIN_BOT}
BPOWER_OK POWER_OK 0 V={V(VIN)>7.5 ? 1 : 0}

* Battery surrogate: 2.5Ah Coulomb counter and approximate OCV/SOC curve.
* Its 2.5F SOC capacitor is an accelerated-time mathematical state, not a cell.
CSOC SOC 0 {QAH}
BSOC 0 SOC I={V(stall)<0.5 ? I(VBATMON) : 0}
BOCV OCV 0 V={V(SOC)<0.02 ? 2.7+15*max(0,V(SOC)) : 3.0+1.2*(min(1,V(SOC))-0.02)/0.98}
VBATMON BAT CELL 0
RCELL CELL OCV {RCELL}
BLOAD BAT 0 I={max(0,V(load))}

* R6, effective output capacitance, and the battery feedback divider.
VSENSE STAGE SENSE 0
R6 SENSE BAT {RSENSE}
COUT BAT 0 22u
CBULK BAT 0 100u
RFB_TOP BAT FB_DIV {RFTOP}
RFB_BOT FB_DIV 0 {RFBOT}
RFB_COMP FB_DIV VFB 203k
RFB_INPUT VFB 0 1T

* NTC: 10k/B3380. Opening the sensor disables monitoring in the real IC.
* Here ntc_open=1 explicitly disables the sensor; the open-pin voltage is omitted.
BNTC_BIAS 0 NTC I={50u*min(1,max(0,V(VIN)/7))*(V(ntc_open)<0.5 ? 1 : 0)}
BNTC_R NTC 0 I={V(NTC)/(10000*exp(3380*(1/(V(temp_c)+273.15)-1/298.15)))}
BTEMP_DRIVE TEMP_DRIVE 0 V={V(POWER_OK)<0.5 || V(ntc_open)>0.5 ? 0 : ((V(NTC)<0.29 || V(NTC)>1.36 || (V(TEMP_FAULT)>0.5 && (V(NTC)<0.348 || V(NTC)>1.088))) ? 1 : 0)}
RTEMP TEMP_DRIVE TEMP_FAULT 1
CTEMP TEMP_FAULT 0 1u

* Timer counts active charging hours and pauses for temperature faults.
* Repeating end-of-cycle windows model three-hour retries until near float.
* Complete the narrow EOC sampling window before parking a finished timer;
* otherwise a restart inside that same window could immediately re-latch DONE.
BCLOCK 0 CLOCK I={V(POWER_OK)>0.5 && V(TEMP_FAULT)<0.5 && (V(DONE)<0.5 || V(PHASE)<0.003) && V(BAD_FAULT)<0.5 ? 1 : 0}
CCLOCK CLOCK 0 1
BCLOCK_RESET CLOCK 0 I={V(POWER_OK)<0.5 ? V(CLOCK)*10000 : 0}
BPHASE PHASE 0 V={V(CLOCK)-TEOC*floor(V(CLOCK)/TEOC)}
BDONE_DRIVE DONE_DRIVE 0 V={V(POWER_OK)<0.5 || V(BAT)<VRESTART ? 0 : ((V(DONE)>0.5 || (V(CLOCK)>0.01 && V(PHASE)<0.002 && V(BAT)>=VRESTART)) ? 1 : 0)}
RDONE DONE_DRIVE DONE 1
CDONE DONE 0 1u

* Preconditioning timeout and recoverable bad-battery latch.
BPRETIME 0 PRETIME I={V(POWER_OK)>0.5 && V(TEMP_FAULT)<0.5 && V(BAD_FAULT)<0.5 && V(BAT)<VPRE ? 1 : 0}
CPRETIME PRETIME 0 1
BPRE_RESET PRETIME 0 I={V(POWER_OK)<0.5 || V(BAT)>=VPRE ? V(PRETIME)*10000 : 0}
BBAD_DRIVE BAD_DRIVE 0 V={V(POWER_OK)<0.5 || V(BAT)>=VPRE ? 0 : ((V(PRETIME)>TEOC/8 || V(BAD_FAULT)>0.5) ? 1 : 0)}
RBAD BAD_DRIVE BAD_FAULT 1
CBAD BAD_FAULT 0 1u

* Averaged CC/CV source with input-voltage regulation and 15% preconditioning.
* 50 A/V CV gain gives small finite regulation error; not real IC loop dynamics.
BREG 0 STAGE I={V(POWER_OK)>0.5 && V(TEMP_FAULT)<0.5 && V(BAD_FAULT)<0.5 && V(DONE)<0.5 ? max(0,min(min((V(BAT)<VPRE ? 0.15*IMAX : IMAX),50*(VF-V(BAT))),13.24*(V(VIN_REG)-2.7))) : 0}
* Input power drawn by the averaged stage, with assumed fixed 88% efficiency.
BDRAW VIN 0 I={max(0,I(VSENSE))*max(0,V(SENSE))/(ETA*max(1,V(VIN)))+0.0005*min(1,max(0,V(VIN))/7.5)+(V(POWER_OK)>0.5 ? 50u : 0)}

* Actual status LED circuits: R1/R2=10k, R8/R9=100k, supplied by solar VIN.
R1 VIN GREEN_R 10k
VLED_GREEN GREEN_R GREEN_A 0
DCHG GREEN_A CHRG_N LED_GREEN
R8 VIN CHRG_N 100k
R2 VIN RED_R 10k
VLED_RED RED_R RED_A 0
DFAULT RED_A FAULT_N LED_RED
R9 VIN FAULT_N 100k
.model LED_GREEN D(Is=2e-20 N=2 Rs=10 Eg=2.2)
.model LED_RED D(Is=1e-17 N=2 Rs=10 Eg=1.8)
.model STATUS_SW SW(Ron=100 Roff=1e12 Vt=2.5 Vh=0.1)
SCHG CHRG_N 0 CHRG_CONTROL 0 STATUS_SW
SFAULT FAULT_N 0 FAULT_CONTROL 0 STATUS_SW
BCHRG_CONTROL CHRG_CONTROL 0 V={V(POWER_OK)>0.5 && V(BAD_FAULT)<0.5 && (V(TEMP_FAULT)>0.5 || I(VSENSE)>IMAX/10) ? 5 : 0}
BFAULT_CONTROL FAULT_CONTROL 0 V={V(POWER_OK)>0.5 && (V(TEMP_FAULT)>0.5 || V(BAD_FAULT)>0.5) ? 5 : 0}

.ic V(SOC)={SOC0} V(CLOCK)=0 V(PRETIME)=0 V(TEMP_FAULT)=0 V(DONE)=0 V(BAD_FAULT)=0 V(BAT)=3.2 V(VIN)=0
.options reltol=0.0001 abstol=1n vntol=1u method=gear
