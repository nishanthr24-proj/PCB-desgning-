"""Verify portable model coverage, model hashes, and preserved ECAD geometry.
Run with Python 3 from any folder. FreeCAD STEP-import results are recorded in
3D.json; their input hashes are checked here to detect stale evidence.
"""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
class Atom(str):pass
def parse(s):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s);pos=0
    def read():
        nonlocal pos
        t=tokens[pos];pos+=1
        if t=='(':
            result=[]
            while tokens[pos]!=')':result.append(read())
            pos+=1;return result
        return json.loads(t) if t.startswith('"') else Atom(t)
    result=read()
    assert pos==len(tokens),'Trailing tokens'
    return result

def children(x,key):return [y for y in x if isinstance(y,list) and y and y[0]==key]
def without_models(x):
    if not isinstance(x,list):return x
    return [without_models(y) for y in x if not(isinstance(y,list) and y and y[0]=='model')]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def geometry_digest(p):
    return hashlib.sha256(json.dumps(without_models(parse(p.read_text())),ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def resolve(model):
    path=model[1];prefix='${KIPRJMOD}/3dmodels/'
    assert path.startswith(prefix),f'Nonportable model path: {path}'
    p=ROOT/path[len('${KIPRJMOD}/'):]
    assert p.is_file(),f'Missing model: {path}'
    assert ROOT/'3dmodels' in p.resolve().parents,'Model outside bundle'
    return p

def main():
    report=json.loads((ROOT/'validation/3D.json').read_text())
    board=parse((ROOT/'Solar_Charger_LED_RevB.kicad_pcb').read_text())
    fitted={};empty=[]
    for fp in children(board,'footprint'):
        ref=next(y[2] for y in children(fp,'property') if y[1]=='Reference')
        models=children(fp,'model')
        if not models:empty.append(ref);continue
        assert len(models)==1,ref
        p=resolve(models[0]);fitted[ref]=str(p.relative_to(ROOT))
        assert children(models[0],'scale')[0][1][1:]==['1','1','1'],ref
        assert children(models[0],'offset')[0][1][1:]==['0','0','0'],ref
        assert children(models[0],'rotate')[0][1][1:]==['0','0','0'],ref
    assert len(fitted)==30,len(fitted)
    assert set(empty)=={*[f'H{i}' for i in range(1,5)],*[f'TP{i}' for i in range(1,10)]},empty
    assert 'Green' in fitted['D3'] and 'Red' in fitted['D4']
    for p in (ROOT/'SolarCharger.pretty').glob('*.kicad_mod'):
        for model in children(parse(p.read_text()),'model'):resolve(model)
    sources=json.loads((ROOT/'3dmodels/SOURCES.json').read_text())
    assert len(sources['models'])==16
    for m in sources['models']:
        assert digest(ROOT/'3dmodels'/m['file'])==m['sha256'],m['file']
    for rel,expected in report['preservation']['files'].items():
        assert geometry_digest(ROOT/rel)==expected,f'Non-model ECAD change: {rel}'
    for rel,expected in report['preservation']['manufacturing_sha256'].items():
        assert digest(ROOT/rel)==expected,f'Manufacturing change: {rel}'
    for m in report['model_geometry']:
        assert m['valid'] and digest(ROOT/'3dmodels'/m['file'])==m['sha256'],m['file']
    assembly=ROOT/report['assembly']['file']
    assert report['assembly']['valid'] and report['assembly']['solids']>=31
    assert digest(assembly)==report['assembly']['sha256'],'Stale STEP validation'
    assert set(report['fitted_models'])==set(fitted)
    print('PASS: 30 fitted models, 13 intentional empty footprints, 16 valid STEP models, portable paths, unchanged ECAD/manufacturing, assembly hash.')

if __name__=='__main__':main()
