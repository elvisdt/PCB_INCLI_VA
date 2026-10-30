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
for a,z in [((190.45,106.75),(190.45,105.5)),((190.45,124.25),(190.45,125.5)),
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
T(G,.3,[(187.,102.725),(187.,101.8)]);V(G,(187.,101.8))
b.Save(str(PCB))
print('Etapa 3 parcial regenerada; ejecutar DRC y paridad.')
