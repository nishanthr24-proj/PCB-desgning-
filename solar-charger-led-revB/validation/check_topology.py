"""Check electrical intent against the exported KiCad netlist (standard library only).

Regenerate netlist.xml from the schematic before checking a changed design:
  kicad-cli sch export netlist --format kicadxml --output validation/netlist.xml Solar_Charger_LED_RevB.kicad_sch
  python3 validation/check_topology.py
"""
from pathlib import Path
import xml.etree.ElementTree as ET

root=ET.parse(Path(__file__).with_name('netlist.xml')).getroot()
pin_net={}
for net in root.findall('./nets/net'):
    for node in net.findall('node'):
        pin_net[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name']

checks=0
def connected(*pins):
    global checks
    nets=[pin_net[(ref,str(pin))] for ref,pin in pins]
    assert len(set(nets))==1,(pins,nets)
    checks+=1

connected(('U1',10),('R6',1),('L1',2))
connected(('U1',9),('R6',2),('J2',1),('C4',1),('C5',1),('R4',1),('D1',2))
assert pin_net['U1','9']!=pin_net['U1','10'];checks+=1
connected(('U1',12),('L1',1),('D2',1),('C3',2))
connected(('U1',11),('C3',1),('D1',1))
connected(('U1',13),('J1',2),('J2',2),('J3',2),('C1',2),('C2',2),('C4',2),('C5',2),('C6',2),('D2',2),('R5',2),('R11',2))
connected(('U1',1),('D5',1),('TP3',1),('C1',1),('C6',1),('R1',1),('R2',1),('R7',1),('R8',1),('R9',1),('R10',1))
connected(('U1',2),('R10',2),('R11',1),('J4',4))
assert pin_net['U1','1']!=pin_net['U1','2'];checks+=1
connected(('U1',3),('R7',2),('JP1',1))
connected(('U1',4),('D3',1),('R8',2),('J4',1))
connected(('U1',5),('D4',1),('R9',2),('J4',2))
connected(('R1',2),('D3',2))
connected(('R2',2),('D4',2))
connected(('U1',6),('C2',1))
connected(('U1',7),('R3',2))
connected(('R3',1),('R4',2),('R5',1))
connected(('U1',8),('J3',1))
values={c.attrib['ref']:c.findtext('value') for c in root.findall('./components/comp')}
for ref,prefix in [('U1','LT3652EMSE'),('R6','0.20'),('R4','60.0k'),('R5','220k'),('R3','203k'),('R7','100k'),('R10','562k'),('R11','100k'),('C4','22u'),('F1','1A / >=32VDC'),('D5','SS16 / 60V')]:
    assert values[ref].startswith(prefix),(ref,values[ref]);checks+=1
connected(('J1',1),('F1',1),('TP1',1))
connected(('F1',2),('D5',2),('TP2',1))
assert len({pin_net['J1','1'],pin_net['F1','2'],pin_net['U1','1']})==3;checks+=1
connected(('JP1',2),('U1',13),('J1',2))
for tp,ref,pin in [('TP1','J1',1),('TP2','F1',2),('TP3','U1',1),('TP4','J2',1),('TP5','R6',1),('TP6','R6',2),('TP7','U1',12),('TP8','U1',13),('TP9','J1',2)]:
    connected((tp,1),(ref,pin))
components={c.attrib['ref']:c for c in root.findall('./components/comp')}
for ref,prefix in [('F1','SolarCharger:Fuse_1206'),('D5','SolarCharger:D_SMA'),('JP1','SolarCharger:PinHeader_1x02'),('TP7','SolarCharger:ProbePad_D0.8'),('TP8','SolarCharger:ProbePad_D0.8')]:
    assert components[ref].findtext('footprint').startswith(prefix),(ref,components[ref].findtext('footprint'));checks+=1
assert values['J4']=='STATUS / VIN_REG';checks+=1
print(f'PASS: {checks} electrical topology and critical-value checks.')
