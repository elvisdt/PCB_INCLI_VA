"""Medidas de la etapa 2 desde el cobre guardado, sin modificar el proyecto.
Longitudes de pista entre bordes REALES de pads; vias = espesor 1.6 mm.
"""
from pathlib import Path
import pcbnew as k
import math, heapq, json
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[2]
b=k.LoadBoard(str(ROOT/'INCLI-VA.kicad_pcb'))
F,B=k.F_Cu,k.B_Cu
VIA_HEIGHT = k.ToMM(b.GetDesignSettings().GetBoardThickness())
assert abs(VIA_HEIGHT-1.6)<1e-6, 'Revisar la metrica al cambiar el espesor de placa'
assert json.loads((ROOT/'INCLI-VA.kicad_pro').read_text())['board']['design_settings']['rules']['use_height_for_length_calcs']

def xy(p): return tuple(round(x,6) for x in k.ToMM(p))
def node(p,layer): return (round(p[0],6),round(p[1],6),layer)
def pv(p): return k.VECTOR2I(k.FromMM(p[0]),k.FromMM(p[1]))
def pad(ref,n): return next(p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber()==str(n))
def inside(p,point,layer): return p.IsOnLayer(layer) and p.GetEffectiveShape(layer).Collide(pv(point))

def graph(net):
    tracks=[t for t in b.GetTracks() if t.GetNetname()==net]
    pts=set(); segs=[]; graph=defaultdict(dict)
    def link(a,z,length):
        graph[a][z]=min(graph[a].get(z,float('inf')),length)
        graph[z][a]=graph[a][z]
    for t in tracks:
        if isinstance(t,k.PCB_VIA):
            p=xy(t.GetPosition());a,z=node(p,F),node(p,B);pts.update([a,z]);link(a,z,VIA_HEIGHT)
        else:
            a,z=node(xy(t.GetStart()),t.GetLayer()),node(xy(t.GetEnd()),t.GetLayer());pts.update([a,z]);segs.append((a,z))
    for a,z in segs:
        dx,dy=z[0]-a[0],z[1]-a[1];d2=dx*dx+dy*dy;split=[]
        for p in pts:
            if p[2]!=a[2]:continue
            u=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d2
            if -.000001<=u<=1.000001 and abs((p[0]-a[0])*dy-(p[1]-a[1])*dx)/math.sqrt(d2)<.00001:split.append((u,p))
        split.sort()
        for (_,p),(_,q) in zip(split,split[1:]):link(p,q,math.dist(p[:2],q[:2]))
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname()!=net:continue
            for layer in (F,B):
                if not p.IsOnLayer(layer):continue
                center=node(xy(p.GetPosition()),layer)
                for q in pts:
                    if q[2]==layer and inside(p,q,layer):link(center,q,math.dist(center[:2],q[:2]))
    return graph

def route(p,q):
    assert p.GetNetname()==q.GetNetname()
    g=graph(p.GetNetname());start=node(xy(p.GetPosition()),F);finish=node(xy(q.GetPosition()),F)
    todo=[(0,start)];dist={start:0};prev={}
    while todo:
        d,u=heapq.heappop(todo)
        if d!=dist[u]:continue
        if u==finish:break
        for v,w in g[u].items():
            nd=d+w
            if nd<dist.get(v,float('inf')):
                dist[v]=nd;prev[v]=u;heapq.heappush(todo,(nd,v))
    if finish not in dist:return None
    path=[finish]
    while path[-1]!=start:path.append(prev[path[-1]])
    path.reverse();exposed=0;via=0
    for a,z in zip(path,path[1:]):
        if a[2]!=z[2]:via+=VIA_HEIGHT;continue
        d=math.dist(a[:2],z[:2]);n=max(1,math.ceil(d/.001))
        for i in range(n):
            t=(i+.5)/n;point=(a[0]+t*(z[0]-a[0]),a[1]+t*(z[1]-a[1]))
            if not inside(p,point,a[2]) and not inside(q,point,a[2]):exposed+=d/n
    return {'centerline_mm':round(dist[finish],4),'pad_edge_path_mm':round(exposed+via,4),
            'via_vertical_mm':round(via,4),'path':path}

out={'basis':'PCB actual; bordes de cobre redondeados; muestreo 1 um; vias de 1.6 mm','decoupling':[]}
for ref,pin,small in [('C601',4,None),('C602',4,'C601'),('C605',4,'C602'),('C604',3,None),('C603',3,'C604'),('C607',16,None),('C608',16,None),('C610',19,None),('C606',19,'C610')]:
    r=route(pad('U601',pin),pad(ref,1));assert r,ref
    if small:
        r['via_small_cap']=any(inside(pad(small,1),point,point[2]) for point in r['path'])
        assert r['via_small_cap'],(ref,small)
    r.update({'reference':ref,'value':b.FindFootprintByReference(ref).GetValue(),'pin':pin,'ground':pad(ref,2).GetNetname()})
    if ref in ('C601','C604','C607','C610'):assert r['pad_edge_path_mm'] <= 2, ref
    if ref == 'C608':assert r['pad_edge_path_mm'] <= 2.15, ref  # excepcion aprobada
    out['decoupling'].append(r)
for net,jpin,upin in [('CANH',3,14),('CANL',4,13)]:out[net]=route(pad('J1',jpin),pad('U601',upin))
if out['CANH'] and out['CANL']:
    out['CAN_delta_total_mm']=round(abs(out['CANH']['centerline_mm']-out['CANL']['centerline_mm']),4)
    out['CAN_delta_planar_mm']=round(abs(out['CANH']['centerline_mm']-out['CANH']['via_vertical_mm']-out['CANL']['centerline_mm']+out['CANL']['via_vertical_mm']),4)
    assert out['CAN_delta_total_mm'] <= 1
    out['CAN_vias']={n:sum(isinstance(t,k.PCB_VIA) and t.GetNetname()==net for t in b.GetTracks()) for n,net in [('CANH','/BUS_CAN_H'),('CANL','/BUS_CAN_L')]}
    assert out['CAN_vias']=={'CANH':2,'CANL':0}
    out['termination_branches_mm']={}
    for name,ref,rpin,upin in [('CANH','R602',1,14),('CANL','R603',2,13)]:
        path=route(pad(ref,rpin),pad('U601',upin))['path']
        main=set(out[name]['path']);length=0
        for a,z in zip(path,path[1:]):
            if a in main:break
            length += VIA_HEIGHT if a[2]!=z[2] else math.dist(a[:2],z[:2])
        out['termination_branches_mm'][name]=round(length,4)
else:
    raise AssertionError('Completar CANH/CANL antes del cierre')
out['logical_signals']={}
for name,a,z in [('CAN_TX',7,24),('CAN_RX',5,25),('CAN_STBY',8,23),('CAN_SILENT',6,35)]:
    path=route(pad('U601',a),pad('U401',z));assert path,name
    out['logical_signals'][name]=path['centerline_mm']
print(json.dumps(out,indent=2))
