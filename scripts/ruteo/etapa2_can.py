"""Etapa 2 CAN sobre b46f185; ejecutar con KiCad cerrado, desde la raiz.

Carga SIEMPRE el PCB del proyecto para conservar las net classes. El grupo
CODEX_ETAPA2 permite regenerar solamente las pistas de esta etapa.
No modifica reglas, esquematicos ni posiciones salvo TP301 (autorizado).
"""
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parents[2]
PCB = ROOT / 'INCLI-VA.kicad_pcb'
assert not list(ROOT.glob('~*.lck')), 'Cerrar KiCad antes de ejecutar'
# Quitar los objetos de la etapa por UUID en el texto: Remove de grupos en
# la API SWIG de KiCad 10.0.7 invalida los iteradores nativos de Tracks.
import re
source = PCB.read_text()
blocks, depth, quoted, escaped, begin = [], 0, False, False, None
for index, char in enumerate(source):
    if quoted:
        if escaped: escaped = False
        elif char == "\\": escaped = True
        elif char == '"': quoted = False
    elif char == '"': quoted = True
    elif char == '(':
        depth += 1
        if depth == 2: begin = index
    elif char == ')':
        if depth == 2: blocks.append((begin,index+1,source[begin:index+1]))
        depth -= 1
old = [x for x in blocks if x[2].startswith('(group "CODEX_ETAPA2"')]
if old:
    assert len(old) == 1
    members = set(re.findall(r'"([0-9a-f-]{36})"', old[0][2].split('(members',1)[1]))
    cuts = []
    for a,z,block in blocks:
        uid = re.search(r'\(uuid "([0-9a-f-]{36})"\)', block)
        if (a,z,block) == old[0] or (block.startswith(('(segment','(via')) and uid and uid[1] in members):
            cuts.append((a,z))
    assert len(cuts) == len(members)+1
    for a,z in reversed(cuts): source = source[:a]+source[z:]
    PCB.write_text(source)
b = k.LoadBoard(str(PCB))
mm = k.FromMM
F, B = k.F_Cu, k.B_Cu
group = k.PCB_GROUP(b)
group.SetName('CODEX_ETAPA2')
b.Add(group)

def pos(xy):
    return k.VECTOR2I(mm(xy[0]), mm(xy[1]))

def T(net, width, points, layer=F):
    n = b.FindNet(net)
    assert n and n.GetNetname() == net, net
    for a, z in zip(points, points[1:]):
        assert a != z
        t = k.PCB_TRACK(b)
        t.SetStart(pos(a)); t.SetEnd(pos(z)); t.SetLayer(layer)
        t.SetWidth(mm(width)); t.SetNet(n)
        b.Add(t); group.AddItem(t)

def V(net, xy):
    v = k.PCB_VIA(b)
    v.SetPosition(pos(xy)); v.SetWidth(mm(.6)); v.SetDrill(mm(.3))
    v.SetNet(b.FindNet(net)); b.Add(v); group.AddItem(v)

G, GC, GI = 'GND_VEH', 'GND_CAN', '/60_can/GNDISO_CAN'
P5, P3 = '+5V_VEH', '+3V3_D'
SO, SI = '/60_can/V_SOOUT', '/60_can/V_SOIN'

# TP301: quitar exclusivamente su antigua bajada B.Cu de la etapa 1.
for t in list(b.GetTracks()):
    if isinstance(t, k.PCB_VIA):
        continue
    ends = {tuple(round(v, 4) for v in k.ToMM(t.GetStart())),
            tuple(round(v, 4) for v in k.ToMM(t.GetEnd()))}
    if t.GetNetname() == P5 and t.GetLayer() == B and ends == {(140.,131.6),(140.,134.)}:
        b.Remove(t)
b.FindFootprintByReference('TP301').SetPosition(pos((140.,131.6)))

# Desacoples del lado logico. Alimentacion a traves de pads, sin bypass.
T(P3,.4,[(132.65,120.905),(135.225,120.91)])
T(P3,.4,[(135.225,120.91),(135.225,121.9),(138.785,121.9),(138.785,120.91)])
T(P3,.4,[(138.785,120.91),(138.785,119.65),(142.38,119.65),(142.38,120.7)])
T(P5,.5,[(132.65,122.175),(134.43,122.175),(135.225,122.97)])
T(P5,.5,[(135.225,122.97),(135.225,124.2),(138.83,124.2),(138.83,123.3)])
T(P5,.5,[(138.83,124.2),(138.83,124.8),(143.5,124.8)])
for net, p, v in [
    (G,(136.775,120.91),(136.775,119.95)),
    (G,(140.335,120.91),(140.335,121.9)),
    (G,(136.775,122.97),(136.775,122.85)),
    (G,(140.73,123.3),(141.65,123.3)),
    (G,(144.28,120.7),(144.28,121.9)),
]:
    T(net,.3,[p,v]); V(net,v)
for y in (124.715,123.445,114.555,113.285):
    T(G,.3,[(132.65,y),(134.0,y)]); V(G,(134.0,y))

# Lado aislado: los dos VISOIN llegan al pin sin cambiar la ubicacion.
T(SI,.3,[(123.35,119.635),(120.275,119.)])
T(SI,.3,[(123.35,119.635),(122.475,119.785),(120.5,121.35),(120.275,121.6)])
T(SO,.4,[(123.35,123.445),(120.275,124.2)])
T(SO,.4,[(120.275,124.2),(120.45,124.375),(120.45,127.)])
T(SO,.4,[(120.45,127.),(120.45,128.35),(118.7125,130.0875),(118.7125,130.1)])
T(SI,.3,[(120.2875,130.1),(121.2,131.0125)])
V(SI,(121.2,131.0125))
T(SI,.3,[(121.2,131.0125),(123.5,128.7125),(123.5,121.6),(120.275,121.6)],B)
V(SI,(120.275,121.6))
for p,v in [((118.725,119.),(117.75,119.)),((118.725,121.6),(117.75,121.6)),
            ((118.655,114.67),(117.75,114.67)),((115.4375,116.7),(116.3,116.7)),
            ((113.625,128.5),(112.6,128.5)),((120.2875,132.7),(121.3,132.7))]:
    T(GC,.3,[p,v]);V(GC,v)
for y in (113.285,118.365):
    T(GC,.3,[(123.35,y),(121.65,y)]);V(GC,(121.65,y))
for p,v in [((118.725,124.2),(118.725,125.15)),((118.55,127.),(118.55,128.1)),
            ((123.35,122.175),(121.65,122.4)),((123.35,124.715),(122.,125.5)),
            ((118.7125,132.7),(117.8,132.7))]:
    T(GI,.3,[p,v]);V(GI,v)
T(GI,.4,[(121.65,122.4),(121.325,122.5),(119.8,122.5),(118.725,123.575),(118.725,125.15),
          (118.55,125.325),(118.55,128.1),(117.8,128.85),(117.8,132.7)],B)
T(GI,.3,[(122.,125.5),(121.65,125.15),(118.725,125.15)],B)
# RS ya tenia el corto tramo final junto a R605.
T('/60_can/CAN_RS',.2,[(123.35,114.555),(120.42,114.555)])

# Senales logicas: cruces cortos B.Cu sobre el tronco de +5V existente.
ST, TX, RX, SL = '/CAN_STBY','/CAN_TX','/CAN_RX','/CAN_SILENT'
T(ST,.2,[(132.65,115.825),(145.8,115.825)])
T(ST,.2,[(135.695,113.2),(135.695,115.825)])
V(ST,(145.8,115.825));T(ST,.2,[(145.8,115.825),(148.8,115.825)],B);V(ST,(148.8,115.825))
T(ST,.2,[(148.8,115.825),(151.65,118.675),(172.69,118.675)])
T(TX,.2,[(132.65,117.095),(145.8,117.095)])
V(TX,(145.8,117.095));T(TX,.2,[(145.8,117.095),(148.8,117.095)],B);V(TX,(148.8,117.095))
T(TX,.2,[(148.8,117.095),(151.65,119.945),(172.69,119.945)])
V(TX,(142.5,117.095));T(TX,.2,[(142.5,117.095),(142.5,114.8)],B)
T(RX,.2,[(132.65,119.635),(134.5,119.635),(135.15,118.985),(144.75,118.985),(145.8,120.035)])
V(RX,(145.8,120.035));T(RX,.2,[(142.5,120.6),(145.235,120.6),(145.8,120.035),(147.735,120.035),(148.3,120.6)],B)
V(RX,(148.3,120.6));T(RX,.2,[(148.3,120.6),(148.915,121.215),(172.69,121.215)])
T(SL,.2,[(132.65,118.365),(145.8,118.365)])
V(SL,(145.8,118.365));T(SL,.2,[(145.8,118.365),(149.6,118.365),(149.6,122.4),(150.4,123.2)],B)
V(SL,(150.4,123.2));T(SL,.2,[(150.4,123.2),(167.,123.2),(170.,126.2),(184.1,126.2),(184.1,124.25)])
V(SL,(138.6,118.365));T(SL,.2,[(138.6,118.365),(138.6,113.2),(139.2,113.2)],B)
V(SL,(139.2,113.2));T(SL,.2,[(139.2,113.2),(139.775,113.2)])
T(G,.3,[(141.425,113.2),(142.3,113.2)]);V(G,(142.3,113.2))
T(P3,.4,[(137.345,113.2),(137.345,112.3)]);V(P3,(137.345,112.3))
T(P3,.4,[(137.345,112.3),(137.345,116.4),(135.225,118.52),(135.225,120.91)],B)
V(P3,(135.225,120.91))

b.Save(str(PCB))
print('Etapa 2 regenerada; CANH/CANL pendientes de resolver cruce autorizado.')
