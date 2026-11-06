"""Original representative inductor envelope for solar charger Rev B.
SPDX-License-Identifier: CC0-1.0
Run using FreeCAD's Python environment, optionally passing an output STEP path.
Envelope follows the board's 6.6 x 6.2 mm fabrication outline; 2.8 mm height is
representative. This is not a vendor model or a qualified clearance envelope.
"""
"""Representative inductor envelope for presentation; NOT a vendor mechanical model.
Body envelope 6.6 x 6.2 mm follows the project's F.Fab outline; height 2.8 mm
is a series-envelope assumption. Contact centres +/-2.35 mm match the land pattern.
No electrical properties or exact purchased-part geometry are asserted.
Requires the FreeCAD Python modules. Geometry is original primitive CAD data.
"""
from pathlib import Path
import sys,re
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as App,Part
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]/'3dmodels/Inductor_SMD.3dshapes/L_Bourns-SRN6028_Envelope.step'
OUT.parent.mkdir(parents=True,exist_ok=True)
doc=App.newDocument('InductorEnvelope')
points=[(-2.8,-3.1),(2.8,-3.1),(3.3,-2.6),(3.3,2.6),(2.8,3.1),(-2.8,3.1),(-3.3,2.6),(-3.3,-2.6)]
v=[App.Vector(x,y,.15) for x,y in points];v.append(v[0])
body=doc.addObject('Part::Feature','BodyEnvelope');body.Shape=Part.Face(Part.makePolygon(v)).extrude(App.Vector(0,0,2.65))
objects=[body]
for x,name in [(-2.35,'Contact1'),(2.35,'Contact2')]:
 o=doc.addObject('Part::Feature',name);o.Shape=Part.makeBox(1.6,5.7,.15,App.Vector(x-.8,-2.85,0));objects.append(o)
Part.export(objects,str(OUT))
# Add AP214 face material styles; no GUI or geometry alteration is required.
s=OUT.read_text();entities={int(m[1]):m[2] for m in re.finditer(r'#(\d+)\s*=\s*(.*?);',s,re.S)}
context=next(n for n,x in entities.items() if 'GEOMETRIC_REPRESENTATION_CONTEXT(3)' in x)
solids=[]
for n,x in entities.items():
 m=re.match(r"MANIFOLD_SOLID_BREP\([^,]*,#(\d+)\)",x.strip())
 if m:
  shell=entities[int(m[1])];faces=[int(x) for x in re.findall(r'#(\d+)',shell)];solids.append(faces)
assert len(solids)==3,len(solids)
nextid=max(entities)+1;added=[];styled=[]
def add(s):
 global nextid
 n=nextid;nextid+=1;added.append(f'#{n} = '+s+';');return n
for faces,color in zip(solids,[(.12,.13,.14),(.73,.75,.77),(.73,.75,.77)]):
 c=add("COLOUR_RGB('',"+','.join(map(str,color))+")")
 fa=add(f"FILL_AREA_STYLE_COLOUR('',#{c})");fs=add(f"FILL_AREA_STYLE('',(#{fa}))")
 fill=add(f'SURFACE_STYLE_FILL_AREA(#{fs})');side=add(f"SURFACE_SIDE_STYLE('',(#{fill}))");usage=add(f'SURFACE_STYLE_USAGE(.BOTH.,#{side})');assignment=add(f'PRESENTATION_STYLE_ASSIGNMENT((#{usage}))')
 for face in faces:styled.append(add(f"STYLED_ITEM('',(#{assignment}),#{face})"))
add("MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',("+','.join('#'+str(n) for n in styled)+f'),#{context})')
pos=s.rfind('ENDSEC;');s=s[:pos]+'\n'.join(added)+'\n'+s[pos:];OUT.write_text(s)
shape=Part.read(str(OUT));assert shape.isValid() and len(shape.Solids)==3
print('Inductor envelope created:',shape.BoundBox,'volume',shape.Volume)
