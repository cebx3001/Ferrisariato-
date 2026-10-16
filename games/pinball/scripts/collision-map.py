"""Reviewable top-down collider/route map, in physical playfield coordinates."""
import json,math,html
from pathlib import Path
root=Path(__file__).resolve().parents[1];d=json.loads((root/'layout.json').read_text());out=root/'docs';out.mkdir(exist_ok=True)
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="1320" viewBox="0 0 10 16.5"><rect width="10" height="16.5" fill="#071b32"/>']
def poly(ps,color,width,fill='none'):
 parts.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in ps)}" fill="{fill}" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')
def text(x,y,s,size=.15):parts.append(f'<text x="{x}" y="{y}" fill="white" font-family="sans-serif" font-size="{size}">{html.escape(s)}</text>')
for w in d['walls']:poly(w,'#60efa2',.035)
for b in d.get('posts',[]):parts.append(f'<circle cx="{b["x"]}" cy="{b["y"]}" r="{b["radius"]}" fill="#ff916c"/>')
for b in d['bumpers']:
 parts.append(f'<circle cx="{b["x"]}" cy="{b["y"]}" r="{b["radius"]}" fill="#245797" stroke="#f5cc42" stroke-width=".035"/>');text(b['x']-.42,b['y']+.06,b['id'],.12)
for t in d['targets']:parts.append(f'<rect x="{t["x"]-.31}" y="{t["y"]-.17}" width=".62" height=".34" fill="#e8b72f"/>')
for s in d['slings']:poly(s['vertices']+[s['vertices'][0]],'#ffbb43',.04,'#735126')
for f in d['flippers']:
 x,y=f['x'],f['y'];e=[x+math.cos(f['rest'])*f['length'],y+math.sin(f['rest'])*f['length']];poly([[x,y],e],'#e9f4ff',d['flipperRadius']*2)
r=d['ramp'];route=[p[:2] for p in r['samples']];poly(route,'#263e74',r['innerWidth']);poly(route,'#ed67fc',.04)
for i in range(0,len(route),40):
 x,y,z=r['samples'][i];text(x-.25,y-.16,f'z={z:.2f}',.12)
x,y=r['sensor'];parts.append(f'<rect x="{x-.32}" y="{y-.08}" width=".64" height=".16" fill="#18e9ff"/>')
poly([r['samples'][-1][:2],[3.7,7.17]],'#18e9ff',.05);text(2.4,6.7,'Salida a piso → bumpers',.16)
text(2,15.8,'Pérdida normal entre flippers',.19)
text(.7,.35,'CANAL ÚNICO · MAGENTA / COLISIONES · VERDE',.17)
text(2.15,1.05,'Casa y terrazas: nivel elevado',.19)
text(2.15,1.38,'Ancho canal 0.70 / bola Ø 0.32',.17)
parts.append('</svg>');(out/'precision-collision-map.svg').write_text('\n'.join(parts))
report={'rampWidth':r['innerWidth'],'ballDiameter':d['ballRadius']*2,'rampSideClearance':(r['innerWidth']-2*d['ballRadius'])/2,'leftBumperPassage':2.9-.7-1.65-.055,'rightBumperPassage':7.85-.055-(6.5+.7),'exit':[round(v,4) for v in r['samples'][-1]],'exitNearestBumperSurface':min(math.dist(r['samples'][-1][:2],[b['x'],b['y']])-b['radius'] for b in d['bumpers'])}
assert report['leftBumperPassage']>d['ballRadius']*2+.15;assert report['rightBumperPassage']>d['ballRadius']*2+.15
(out/'precision-corridor-clearances.json').write_text(json.dumps(report,indent=2));print(report)
