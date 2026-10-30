"""Etapa 3 USB/MCU. Regeneracion del grupo CODEX_ETAPA3, con KiCad cerrado.
No cambiar componentes sin autorizacion registrada en RUTEO_TRASPASO.md.
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
old = [x for x in blocks if x[2].startswith('(group "CODEX_ETAPA3"')]
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
group.SetName('CODEX_ETAPA3')
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

# Movimientos autorizados por el usuario al continuar etapa 3.
for ref,point,angle in [('C402',(189.18,104.),90),('C401',(189.2,100.6),90),('R401',(187.,100.1),270)]:
    fp=b.FindFootprintByReference(ref);fp.SetOrientationDegrees(angle);fp.SetPosition(pos(point))
    fp.Reference().SetTextAngle(k.EDA_ANGLE(0,k.DEGREES_T));fp.Reference().SetTextSize(pos((.8,.8)));fp.Reference().SetTextThickness(mm(.15))
    fp.Reference().SetPosition(pos((point[0],point[1]-1.9)))
G, P3 = 'GND_VEH', '+3V3_D'
TX,RX,BOOT='/40_mcu/U0TXD','/40_mcu/U0RXD','/40_mcu/BOOT'
# UART: un cruce corto B.Cu en TX; no pasa por la antena.
T(TX,.2,[(186.64,124.25),(186.64,125.4),(184.4,127.64),(184.4,130.1)])
V(TX,(184.4,130.1));T(TX,.2,[(184.4,130.1),(179.8,134.7)],B);V(TX,(179.8,134.7))
T(TX,.2,[(179.8,134.7),(179.5,135.),(179.5,145.28),(180.12,145.9)])
T(RX,.2,[(185.37,124.25),(185.37,125.55),(183.1,127.82),(183.1,130.7),(182.3,131.5),(182.3,134.8),(182.66,135.16),(182.66,145.9)])
# BOOT: pull-up existente, pulsador y TP inferior. GPIO3/45/46 quedan NC.
T(BOOT,.2,[(173.94,124.25),(173.94,125.5)]);V(BOOT,(173.94,125.5))
T(BOOT,.2,[(173.94,125.5),(173.94,127.2)],B);V(BOOT,(173.94,127.2))
T(BOOT,.2,[(173.94,127.2),(173.94,132.8),(172.005,134.735),(172.005,142.55),(172.005,145.845),(170.65,147.2)])
V(BOOT,(173.94,132.8));T(BOOT,.2,[(173.94,132.8),(171.74,135.),(170.,135.)],B)
# 3V3 desde C304 al bulk VIO C605; conserva la cadena de etapa 2.
T(P3,.6,[(151.,142.5),(157.,142.5)])
V(P3,(157.,142.5));T(P3,.6,[(157.,142.5),(157.,141.5),(155.38,141.5),(142.38,128.5),(142.38,123.8)],B)
V(P3,(142.38,123.8));T(P3,.4,[(142.38,123.8),(142.38,120.7)])
# Alimentacion de BOOT y supervisor; el tronco MCU se completa con sus desacoples.
T(P3,.6,[(157.,142.5),(158.,142.5),(159.,141.5),(159.,139.5)])
T(P3,.4,[(159.,139.5),(159.,148.4),(169.,148.4),(169.,147.2)])
T(P3,.4,[(159.,139.5),(159.,133.7),(168.175,133.7),(169.525,135.05),(168.7,135.05),(168.2,135.55),(167.2375,135.55)])
# Retornos cortos; U401 ya tiene 12 taladros metalizados GND en su pad central.
for a,z in [((190.45,106.75),(190.45,107.8)),((190.45,124.25),(190.45,125.5)),
            ((160.945,142.55),(160.945,141.25)),((167.645,142.55),(167.645,141.25)),
            ((171.075,135.05),(171.075,134.0)),((164.9625,136.5),(165.9,136.5))]:
    T(G,.3,[a,z]);V(G,z)
# EN local y RESET remoto. R401 queda pendiente de la decision de ubicacion.
RST='/MCU_RST_N'
T(RST,.2,[(187.91,106.75),(187.91,105.3),(187.91,105.185),(187.,104.275)])
V(RST,(187.91,105.3));T(RST,.2,[(187.91,105.3),(185.71,107.5),(184.,107.5),(180.,107.5),(170.,117.5),(170.,130.),(166.7,133.3),(160.5,133.3),(160.5,135.7)],B)
V(RST,(160.5,135.7));T(RST,.2,[(160.5,135.7),(161.5,135.7),(162.6,135.7)])
T(RST,.2,[(161.5,135.7),(161.5,138.755),(165.305,142.55)])
T('Net-(U801-~{RESET})',.2,[(164.9625,135.55),(163.7,135.55),(163.7,137.35),(162.6,137.35)])
T(G,.3,[(187.,102.725),(186.4,102.725)]);V(G,(186.4,102.725))
# 3V3: C401 bulk -> C402 pequeno -> pin, sin bypass de la cadena.
T(P3,.4,[(189.18,106.75),(189.18,104.775)])
T(P3,.4,[(189.18,104.775),(190.5,104.775),(190.5,102.85),(189.2,101.55)])
V(P3,(159.,139.5));T(P3,.6,[(159.,139.5),(187.4,139.5),(188.9,138.),(188.9,105.5),(190.3,104.1),(190.3,102.65),(189.2,101.55)],B);V(P3,(189.2,101.55))
T(G,.3,[(189.2,99.65),(190.2,99.65)]);V(G,(190.2,99.65))
V(G,(189.18,103.225))
# R401 junto al RC, por el este de C403. No cruza su pad GND.
T(RST,.2,[(187.,100.925),(188.,101.925),(188.,104.3),(187.91,105.3)])
T(P3,.4,[(187.,99.275),(186.1,99.275)]);V(P3,(186.1,99.275))
T(P3,.4,[(186.1,99.275),(187.,99.275),(189.2,101.55)],B)
# USB-C: par principal F.Cu; cuatro vias solo en ramales B6/B7.
b.FindFootprintByReference('C404').SetPosition(pos((189.6,81.45)))
DM,DP='/40_mcu/USB_D-','/40_mcu/USB_D+'
T(DM,.3,[(193.645,80.27),(190.8,80.27),(190.57,80.5),(187.1375,80.5),(184.8625,80.5),(182.,80.5),(173.,89.5),(173.,107.5)])
# Pendiente de autorizacion: cuello D- de 1.923 mm a 0.15 mm.
# La propuesta se verifica exclusivamente en una copia temporal.
T(DM,.3,[(174.8,107.9),(175.21,107.9),(175.21,106.75)])
T(DP,.3,[(193.645,80.77),(191.8,80.77),(191.3,81.27),(191.3,82.4),(187.1375,82.4),(184.8625,82.4),
         (183.5,82.4),(183.3,82.2),(183.3,81.4),(182.9,81.),(182.207107,81.),(173.5,89.707107),(173.5,96.),(174.,96.5),(174.88,96.5),(175.38,97.),(175.38,98.),(174.88,98.5),(174.,98.5),(173.5,99.),(173.5,105.4),(173.94,105.84),(173.94,106.75)])
T(DP,.3,[(193.645,79.77),(192.6,79.77),(192.2,79.37)]);V(DP,(192.2,79.37))
T(DP,.3,[(192.2,79.37),(191.7,79.87),(191.7,82.5),(190.,82.5)],B);V(DP,(190.,82.5));T(DP,.3,[(190.,82.5),(190.,82.4)])
T(DM,.3,[(193.645,81.27),(192.555,81.27),(192.4,81.425)]);V(DM,(192.4,81.425))
T(DM,.3,[(192.4,81.425),(193.,80.825),(193.,78.65),(191.35,78.65),(190.4,79.6)],B);V(DM,(190.4,79.6));T(DM,.3,[(190.4,79.6),(190.4,80.5)])
T('/40_mcu/VBUS',.4,[(187.1375,81.45),(188.825,81.45)])
T(G,.3,[(184.8625,81.45),(185.9,81.45)]);V(G,(185.9,81.45));V(G,(190.375,81.45))
# CC1/CC2 en F.Cu; VBUS cruza por B.Cu y nunca alimenta +5V.
T('/40_mcu/CC1',.2,[(193.645,81.77),(193.,81.75),(192.7,82.05),(192.45,82.05),(191.6,82.9),(190.55,82.9),(189.5,83.95),(186.525,83.95),(185.175,85.3)])
T('/40_mcu/CC2',.2,[(193.645,78.77),(187.5,78.77),(187.23,78.5),(186.25,78.5),(185.45,77.7),(185.175,77.7)])
VB='/40_mcu/VBUS'
T(VB,.4,[(188.825,81.45),(188.95,81.45)]);V(VB,(188.95,81.45))
T(VB,.4,[(188.95,81.45),(189.25,81.75),(189.25,82.8),(189.75,83.3),(192.55,83.3)],B);V(VB,(192.55,83.3))
T(VB,.4,[(192.55,83.3),(192.93,82.92),(193.645,82.92)])
T(VB,.4,[(188.95,81.45),(189.65,80.75),(189.65,79.3),(190.05,78.9),(190.15,78.9),(190.95,78.1)],B);V(VB,(190.95,78.1))
T(VB,.4,[(190.95,78.1),(193.645,78.12)])
T(VB,.4,[(188.95,81.45),(186.95,81.45),(186.2,82.2),(183.,82.2),(182.3,81.5),(181.5,81.5)],B)
for a,z in [((186.825,85.3),(186.825,86.3)),((186.825,77.7),(186.825,76.7))]:T(G,.3,[a,z]);V(G,z)
T(G,.3,[(193.645,83.72),(193.08,84.285),(192.4,84.285)]);V(G,(192.4,84.285))
T(G,.3,[(193.645,77.32),(192.95,77.32),(192.4,76.87)]);V(G,(192.4,76.87))
# Referencias tras los movimientos; no se modifica la ubicacion de C403.
for ref,point,angle in [('C401',(189.2,97.7),0),('C402',(190.9,104.),90),('R401',(185.6,97.8),0),('C403',(185.55,103.5),90),('C404',(189.6,84.1),0)]:
    text=b.FindFootprintByReference(ref).Reference();text.SetPosition(pos(point));text.SetTextAngle(k.EDA_ANGLE(angle,k.DEGREES_T))
for item in b.GetDrawings():
    if isinstance(item,k.PCB_TEXT) and item.GetText()=='SIN BARNIZ' and 185 < k.ToMM(item.GetPosition().x) < 195:
        item.SetPosition(pos((192.,88.)));item.SetTextAngle(k.EDA_ANGLE(0,k.DEGREES_T))
b.Save(str(PCB))
print('Etapa 3 parcial regenerada; ejecutar DRC y paridad.')
