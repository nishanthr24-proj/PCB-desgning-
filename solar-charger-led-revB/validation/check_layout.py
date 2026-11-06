"""Independent Rev B PCB intent checks; run with KiCad's Python/pcbnew.
This supplements, and does not replace, KiCad ERC/DRC/parity or physical tests.
"""
from pathlib import Path
import math,json
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(ROOT/'Solar_Charger_LED_RevB.kicad_pcb'))
fps={fp.GetReference():fp for fp in b.GetFootprints()};checks=0
def pad(ref,num):return next(pd for pd in fps[ref].Pads() if pd.GetNumber()==str(num))
def xy(v):return p.ToMM(v.x),p.ToMM(v.y)
def same(*pins):
    global checks
    ns=[pad(r,n).GetNetname() for r,n in pins];assert len(set(ns))==1,(pins,ns);checks+=1
same(('J1',1),('F1',1),('TP1',1));same(('F1',2),('D5',2),('TP2',1))
same(('D5',1),('U1',1),('C1',1),('C6',1),('R7',1),('R10',1),('TP3',1))
assert len({pad('J1',1).GetNetname(),pad('F1',2).GetNetname(),pad('D5',1).GetNetname()})==3;checks+=1
same(('JP1',1),('U1',3),('R7',2));same(('JP1',2),('U1',13))
for tp,r,n in [('TP4','J2',1),('TP5','R6',1),('TP6','R6',2),('TP7','U1',12),('TP8','U1',13),('TP9','J1',2)]:same((tp,1),(r,n))
start=xy(pad('TP7',1).GetPosition());end=xy(pad('C3',2).GetPosition())
branches=[t for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname()==pad('TP7',1).GetNetname() and ((math.dist(xy(t.GetStart()),start)<.001 and math.dist(xy(t.GetEnd()),end)<.001) or (math.dist(xy(t.GetEnd()),start)<.001 and math.dist(xy(t.GetStart()),end)<.001))]
assert len(branches)==1 and p.ToMM(branches[0].GetLength())<2.0;checks+=1
assert math.dist(start,xy(pad('TP8',1).GetPosition()))<2.5;checks+=1
assert p.ToMM(pad('TP7',1).GetSize().x)==.8;checks+=1
for ref in ['TP5','TP6']:
    assert math.dist(xy(pad(ref,1).GetPosition()),xy(pad('R6',1 if ref=='TP5' else 2).GetPosition()))<4.0;checks+=1
edges=b.GetBoardEdgesBoundingBox();assert abs(p.ToMM(edges.GetWidth())-60)<.1 and abs(p.ToMM(edges.GetHeight())-55)<.1;checks+=1
pro=json.loads((ROOT/'Solar_Charger_LED_RevB.kicad_pro').read_text())
assert not pro.get('erc',{}).get('erc_exclusions');assert not pro.get('board',{}).get('design_settings',{}).get('drc_exclusions');checks+=1
assert not [k for k,v in pro.get('erc',{}).get('rule_severities',{}).items() if v=='ignore'];checks+=1
print(f'PASS: {checks} PCB intent, probe geometry, and check-configuration checks. SW stub {p.ToMM(branches[0].GetLength()):.3f} mm.')
