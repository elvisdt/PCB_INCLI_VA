"""Etapa 4 sensores y senales. Regenera el grupo CLAUDE_ETAPA4, con KiCad cerrado.
Uso: etapa4_senales.py [PCB]  (por defecto INCLI-VA.kicad_pcb del proyecto).
Cambios de ubicacion y desvio de RESET autorizados por el usuario (2026-10-29),
registrados en RUTEO_TRASPASO.md. No ejecutarlo sobre ruteo manual posterior.
"""
import re, sys
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parents[2]
PCB = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'INCLI-VA.kicad_pcb'
assert not list(PCB.parent.glob('~*.lck')), 'Cerrar KiCad antes de ejecutar'
GROUP = 'CLAUDE_ETAPA4'

# Quitar el grupo anterior y sus pistas/vias por UUID en el texto (igual que
# etapa3_mcu.py: Remove de grupos en SWIG invalida iteradores).
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
        if depth == 2: blocks.append((begin, index + 1, source[begin:index + 1]))
        depth -= 1
old = [x for x in blocks if x[2].startswith(f'(group "{GROUP}"')]
if old:
    assert len(old) == 1
    members = set(re.findall(r'"([0-9a-f-]{36})"', old[0][2].split('(members', 1)[1]))
    cuts = []
    for a, z, block in blocks:
        uid = re.search(r'\(uuid "([0-9a-f-]{36})"\)', block)
        if (a, z, block) == old[0] or (block.startswith(('(segment', '(via')) and uid and uid[1] in members):
            cuts.append((a, z))
    assert len(cuts) == len(members) + 1
    for a, z in reversed(cuts): source = source[:a] + source[z:]
    PCB.write_text(source)

b = k.LoadBoard(str(PCB))
mm = k.FromMM
F, B = k.F_Cu, k.B_Cu
group = k.PCB_GROUP(b)
group.SetName(GROUP)
b.Add(group)

def pos(xy):
    return k.VECTOR2I(mm(xy[0]), mm(xy[1]))

def T(net, width, points, layer=F):
    n = b.FindNet(net)
    assert n and n.GetNetname() == net, net
    for a, z in zip(points, points[1:]):
        assert a != z, (net, a)
        t = k.PCB_TRACK(b)
        t.SetStart(pos(a)); t.SetEnd(pos(z)); t.SetLayer(layer)
        t.SetWidth(mm(width)); t.SetNet(n)
        b.Add(t); group.AddItem(t)

def V(net, xy):
    n = b.FindNet(net)
    assert n and n.GetNetname() == net, net
    v = k.PCB_VIA(b)
    v.SetPosition(pos(xy)); v.SetWidth(mm(.6)); v.SetDrill(mm(.3))
    v.SetNet(n); b.Add(v); group.AddItem(v)

G = 'GND_VEH'
def GV(a, z, w=.3):
    """Retorno local corto a una via GND (el plano llega en etapa 5)."""
    T(G, w, [a, z]); V(G, z)

# ---------------------------------------------------------------- U101 ----
# Saltos B.Cu reservados en el traspaso, contrastados con el cobre de etapa 1.
P = '/10_power_input/'
# SW: pin 3 -> R106.1 recto al oeste.
T(P+'SW', .2, [(123.375, 73.75), (120.4, 73.75)])
# UVLO: pin 4 -> oeste por el hueco R106/C109 -> x118.9 -> R106.2; salto B.Cu
# bajo la Kelvin C_ID (y70.95) hasta R107.1.
T(P+'UVLO', .2, [(123.375, 74.25), (121.6, 74.25), (121.25, 74.6), (118.9, 74.6), (118.9, 71.745), (120.4, 71.745)])
V(P+'UVLO', (118.9, 71.745))
T(P+'UVLO', .2, [(118.9, 71.745), (118.9, 69.345)], B)
V(P+'UVLO', (118.9, 69.345))
T(P+'UVLO', .2, [(118.9, 69.345), (120.4, 69.345)])
# OV: pin 5 -> x122.2 -> R109.1 -> via -> B.Cu x121.85 / y85 -> F.Cu a R112.2
# rodeando por debajo la via de TP104.
T(P+'OV', .2, [(123.375, 74.75), (122.2, 74.75), (122.2, 78.735), (122.875, 78.735)])
T(P+'OV', .2, [(122.2, 78.735), (122.2, 79.35), (121.85, 79.7)])
V(P+'OV', (121.85, 79.7))
T(P+'OV', .2, [(121.85, 79.7), (121.85, 85.0), (134.6, 85.0)], B)
V(P+'OV', (134.6, 85.0))
T(P+'OV', .2, [(134.6, 85.0), (134.6, 91.4), (135.475, 92.275), (135.9, 92.275)])
# R108.2 <-> R112.1 (divisor OV).
T('Net-(R108-Pad2)', .2, [(132.575, 100.0), (134.4, 98.2), (134.4, 96.7), (135.9, 95.2)])
# TMR, ILIM.
T(P+'TMR', .2, [(125.15, 76.025), (125.15, 77.4), (125.425, 77.675), (125.425, 78.785)])
T(P+'ILIM', .2, [(126.15, 76.025), (126.15, 77.95), (127.975, 77.95), (127.975, 78.735)])
# FLT: pin 12 -> via -> B.Cu bajo HGATE/VA -> R111.2 -> TP104.
FLT = '/PWR_FLT_N'
T(FLT, .2, [(126.65, 76.025), (126.65, 76.95), (126.95, 77.25)])
V(FLT, (126.95, 77.25))
T(FLT, .2, [(126.95, 77.25), (130.0, 77.9)], B)
V(FLT, (130.0, 77.9))
T(FLT, .2, [(130.0, 77.9), (130.525, 78.425), (130.525, 78.735)])
T(FLT, .2, [(130.525, 78.735), (135.5, 78.735), (135.5, 90.5)])
V(FLT, (135.5, 90.5))  # via en el pad de TP104 (B.Cu)
# +3V3_D a R111.1: F.Cu al este, B.Cu bajo el enlace R108-R112 hasta la via
# que dejo la etapa 3 en (137.345,112.3).
P3D = '+3V3_D'
T(P3D, .4, [(130.525, 80.385), (130.9, 80.8), (133.6, 80.8), (133.6, 89.0)])
V(P3D, (133.6, 89.0))
T(P3D, .4, [(133.6, 89.0), (133.6, 108.5), (137.345, 112.245), (137.345, 112.3)], B)
# VS: esquina pines 6/7, via, B.Cu x123.4 al norte hasta la via de pin 22 y al
# sur hasta D104.3; pin 22 -> C108.2 por B.Cu y C108.2 -> C102.1 por F.Cu.
VS = P+'VS'
T(VS, .2, [(123.375, 75.25), (123.3, 75.25), (123.3, 76.2), (124.15, 76.2), (124.15, 76.025)])
T(VS, .2, [(123.3, 76.2), (123.3, 76.9)])
V(VS, (123.3, 76.9))
T(VS, .25, [(123.3, 76.9), (123.4, 76.8), (123.4, 69.85), (124.85, 69.85), (125.25, 70.25)], B)
T(VS, .25, [(123.3, 76.9), (123.4, 77.0), (123.4, 84.2), (131.0, 84.2), (131.0, 83.9)], B)
V(VS, (131.0, 83.9))
T(VS, .25, [(131.0, 83.9), (131.0, 85.4125)])
T(VS, .2, [(125.15, 71.975), (125.15, 70.35), (125.25, 70.25)])
V(VS, (125.25, 70.25))
T(VS, .25, [(125.25, 70.25), (125.25, 69.4), (128.42, 69.4), (128.42, 70.1)], B)
V(VS, (128.42, 70.1))
T(VS, .25, [(128.42, 70.1), (128.425, 69.0)])
T(VS, .25, [(128.425, 69.0), (128.425, 68.2), (126.675, 66.45), (126.675, 65.6)])
# CAP: pin 23 -> via -> U por B.Cu y71.35 -> via -> C108.1.
CAP = P+'CAP'
T(CAP, .2, [(124.65, 71.975), (124.65, 70.75), (124.45, 70.55)])
V(CAP, (124.45, 70.55))
T(CAP, .2, [(124.45, 70.55), (124.45, 71.35), (126.87, 71.35), (126.87, 70.1)], B)
V(CAP, (126.87, 70.1))
T(CAP, .2, [(126.87, 70.1), (126.875, 69.0)])
# R105.2 <-> C109.1.
T('Net-(C109-Pad1)', .2, [(120.4, 77.395), (120.4, 79.845)])
# Retornos locales GND reservados en el traspaso.
GV((127.425, 75.25), (127.75, 76.55), .25)
T(G, .25, [(127.425, 73.75), (128.3, 73.75)]); GV((128.3, 73.75), (128.6, 73.45), .25)
GV((122.875, 80.385), (122.6, 81.5))
GV((125.425, 80.335), (125.42, 81.4))
GV((127.975, 80.385), (127.97, 81.4))
# C109.2: sin hueco para via (VA B.Cu en y76); lo toma el plano F.Cu en etapa 5.
GV((120.4, 67.695), (119.5, 67.7))

# ------------------------------------------------- RESET (desvio autorizado) ----
# El tramo B.Cu diagonal de etapa 3 pasaba bajo las salidas SPI. Se quitan esos
# tres tramos y RESET baja por un carril B.Cu bajo el modulo (x186.3); TP401,
# C403 y R401 siguen igual. Autorizado por el usuario el 2026-10-29.
RST = '/MCU_RST_N'
quitar = {((184.0, 107.5), (180.0, 107.5)), ((180.0, 107.5), (170.0, 117.5)), ((170.0, 117.5), (170.0, 130.0))}
for t in list(b.GetTracks()):
    if t.GetClass() == 'PCB_TRACK' and t.GetNetname() == RST and t.GetLayer() == B:
        ends = (round(k.ToMM(t.GetStart().x), 3), round(k.ToMM(t.GetStart().y), 3)), (round(k.ToMM(t.GetEnd().x), 3), round(k.ToMM(t.GetEnd().y), 3))
        if ends in quitar or ends[::-1] in quitar:
            g = t.GetParentGroup()
            if g: g.RemoveItem(t)
            b.Remove(t)
T(RST, .2, [(185.71, 107.5), (186.3, 108.09), (186.3, 128.6), (171.0, 128.6), (170.0, 129.6), (170.0, 130.0)], B)

# ------------------------------------------------------------ WDI y VAR_ID ----
WDI = '/WDI'
T(WDI, .2, [(179.02, 106.75), (179.02, 108.15)])
V(WDI, (179.02, 108.15))
# WDI cruza sobre RESET con un puente F.Cu corto en x175.5.
T(WDI, .2, [(179.02, 108.15), (179.02, 109.6), (185.6, 109.6), (185.6, 127.9), (175.5, 127.9)], B)
V(WDI, (175.5, 127.9))
T(WDI, .2, [(175.5, 127.9), (175.5, 129.3)])
V(WDI, (175.5, 129.3))
T(WDI, .2, [(175.5, 129.3), (175.5, 137.0), (172.0, 137.0), (171.4, 136.4)], B)
V(WDI, (171.4, 136.4))
T(WDI, .2, [(171.4, 136.4), (170.0, 136.4), (169.475, 136.925), (169.475, 137.5)])
T(WDI, .2, [(169.475, 137.5), (167.2375, 137.45)])
T('/VAR_ID2', .2, [(176.48, 106.75), (176.48, 105.5), (176.5, 104.3)])
T('/VAR_ID0', .2, [(186.64, 106.75), (186.64, 105.5), (185.6, 105.5), (185.6, 102.705), (184.5, 102.705)])
T('/VAR_ID1', .2, [(185.37, 106.75), (185.37, 108.2)])
V('/VAR_ID1', (185.37, 108.2))
T('/VAR_ID1', .2, [(185.37, 108.2), (184.85, 108.72), (180.8, 108.72), (180.8, 102.7)], B)
V('/VAR_ID1', (180.8, 102.7))
T('/VAR_ID1', .2, [(180.8, 102.7), (181.9, 102.705)])

# ---------------------------------------------- Bus bajo el modulo y USB ----
# Pines 28-32 (DO1_EN, DO2_EN, DO1_DIAG, DO2_DIAG, PWR_FLT_N) bajan a B.Cu en el
# lado interior del pad y suben por carriles x175.9-177.5; LED_G/LED_R se suman
# en el bolsillo norte. Todos cruzan el par USB una sola vez, por B.Cu.
bus = [('/DO1_EN', 175.21), ('/DO2_EN', 176.48), ('/DO1_DIAG', 177.75), ('/DO2_DIAG', 179.02), (FLT, 180.29)]
fin = {'/DO1_EN': 75.6, '/DO2_EN': 79.6, '/DO1_DIAG': 78.0, '/DO2_DIAG': 80.4, FLT: 82.8}
for i, (net, x) in enumerate(bus):
    lane, wide = 175.9 + .4 * i, 175.9 + .7 * i  # se abren a 0.7 mm en el bolsillo para las vias
    T(net, .2, [(x, 124.25), (x, 122.75)])
    V(net, (x, 122.75))
    jog = 104.5 + .3 * i  # inicio escalonado: diagonales paralelas a >=0.49 mm
    pts = [(x, 122.75), (lane, 122.75 - abs(x - lane)), (lane, jog)]
    if wide != lane: pts.append((wide, jog - (wide - lane)))
    T(net, .2, pts + [(wide, fin[net])], B)
    if net != '/DO1_DIAG': V(net, (wide, fin[net]))
LG, LR = '/LED_G', '/LED_R'
T(LR, .2, [(182.83, 106.75), (182.83, 105.4), (182.9, 105.3), (182.9, 100.9)])
V(LR, (182.9, 100.9))
T(LR, .2, [(182.9, 100.9), (180.1, 100.9), (180.1, 81.4)], B)
V(LR, (180.1, 81.4))
T(LG, .2, [(184.1, 106.75), (184.1, 105.6), (183.6, 105.1), (183.6, 101.8)])
V(LG, (183.6, 101.8))
T(LG, .2, [(183.6, 101.8), (179.4, 101.8), (179.4, 82.1)], B)
V(LG, (179.4, 82.1))
# LEDs al oeste y al norte hasta R803/R804; FLT al oeste hasta TP104 (salto
# B.Cu bajo el tronco +5V).
T(LR, .2, [(180.1, 81.4), (174.2, 81.4), (173.0, 82.6), (158.1, 82.6), (158.1, 58.55)])
T(LG, .2, [(179.4, 82.1), (174.1, 82.1), (172.9, 83.3), (154.6, 83.3), (154.6, 58.55)])
T(FLT, .2, [(178.7, 82.8), (174.0, 82.8), (172.8, 84.0), (139.0, 84.0)])
V(FLT, (139.0, 84.0))
T(FLT, .2, [(139.0, 84.0), (136.5, 86.5), (136.5, 89.6), (136.0, 90.1)], B)
T('Net-(D801-A)', .2, [(154.6, 54.5), (154.6, 56.9)])
T('Net-(D802-A)', .2, [(158.1, 54.5), (158.1, 56.9)])

# ------------------------------------------------------------ Salidas DO ----
D1, D2 = '/VEH_DO1', '/VEH_DO2'
T(D1, .5, [(178.0, 55.5), (178.51, 64.0), (182.11, 64.0)])
T(D1, .5, [(182.11, 64.0), (182.11, 61.6), (189.54, 61.6), (189.54, 64.0)])
K1 = 'Net-(D704-K)'
T(K1, .2, [(176.6325, 63.05), (175.5, 63.05), (175.5, 66.3), (187.82, 66.3), (187.82, 68.1)])
T(K1, .2, [(176.34, 66.3), (176.34, 68.1)])
T(K1, .2, [(182.105, 66.3), (182.105, 68.1)])
T('Net-(R708-Pad2)', .2, [(192.4625, 64.0), (190.4175, 68.1)])
DG1 = '/DO1_DIAG'
T(DG1, .2, [(193.3425, 68.1), (193.3425, 69.6), (194.4375, 70.7), (194.4375, 72.3)])
T(DG1, .2, [(193.3425, 69.6), (188.6, 69.6), (188.155, 70.05), (188.155, 72.3), (188.155, 73.6)])
V(DG1, (188.155, 73.6))
T(DG1, .2, [(177.3, 78.0), (179.5, 75.8), (186.8, 75.8), (188.155, 74.45), (188.155, 73.6)], B)
E1 = '/70_output_DO1/EN_5V'
T(E1, .2, [(178.8275, 73.25), (179.95, 73.25)])
V(E1, (179.95, 73.25))
T(E1, .2, [(179.95, 73.25), (183.85, 69.35), (186.175, 69.35)], B)
V(E1, (186.175, 69.35))
T(E1, .2, [(186.175, 69.35), (186.175, 68.1)])
DE1 = '/DO1_EN'
T(DE1, .2, [(176.5525, 72.3), (175.5, 72.3), (175.5, 74.6), (185.9, 74.6), (185.9, 73.125)])
T(DE1, .2, [(175.9, 75.6), (175.9, 74.6)])
P5 = '+5V_VEH'
T(P5, .5, [(171.5, 70.4), (181.555, 70.4), (181.555, 72.3)])
T(P5, .5, [(176.5525, 70.4), (176.5525, 71.35)])
T(P5, .5, [(178.8275, 70.4), (178.8275, 71.35)])
# DO2
T(D2, .5, [(172.92, 55.5), (171.42, 61.6), (171.4175, 64.0)])
T(D2, .5, [(171.42, 61.6), (161.95, 61.6), (161.95, 64.0), (159.6, 66.35), (159.6, 71.4), (160.5, 72.3), (161.2675, 72.3)])
K2 = 'Net-(D754-K)'
T(K2, .2, [(169.5425, 63.05), (168.3, 63.05), (168.3, 66.3), (161.14, 66.3), (161.14, 68.1)])
T(K2, .2, [(166.905, 66.3), (166.905, 68.1)])
T(K2, .2, [(168.3, 66.3), (172.635, 66.3), (172.635, 68.1)])
T('Net-(R758-Pad2)', .2, [(164.1925, 72.3), (166.9375, 72.3)])
E2 = '/70_output_DO2/EN_5V'
T(E2, .2, [(163.6275, 77.55), (164.7, 77.5)])
V(E2, (164.7, 77.5))
T(E2, .2, [(164.7, 77.5), (170.985, 69.3)], B)
V(E2, (170.985, 69.3))
T(E2, .2, [(170.985, 69.3), (170.985, 68.1)])
DE2 = '/DO2_EN'
T(DE2, .2, [(161.3525, 76.6), (160.3, 76.6), (160.3, 78.5), (170.2, 78.5), (170.46, 78.24), (170.46, 77.425)])
T(DE2, .2, [(170.46, 78.24), (171.82, 79.6), (176.6, 79.6)])
DG2 = '/DO2_DIAG'
T(DG2, .2, [(178.0, 80.4), (167.3875, 80.4), (167.3875, 81.0)])
T(DG2, .2, [(167.3875, 81.0), (167.3875, 79.3), (161.105, 79.3), (161.105, 81.0)])
V(DG2, (170.0, 80.4))
T(DG2, .2, [(170.0, 80.4), (169.8625, 73.85)], B)
V(DG2, (169.8625, 73.85))
T(DG2, .2, [(169.8625, 73.85), (169.8625, 72.3)])
# +5V a U751/C752 desde el tronco (147.7,69.5); salto B.Cu bajo los LED.
T(P5, .5, [(147.7, 69.5), (152.4, 74.2), (153.4, 74.2)])
V(P5, (153.4, 74.2))
T(P5, .5, [(153.4, 74.2), (159.4, 74.2)], B)
V(P5, (159.4, 74.2))
T(P5, .5, [(159.4, 74.2), (166.37, 74.2), (166.37, 76.6)])
T(P5, .5, [(161.3525, 74.2), (161.3525, 75.65)])
T(P5, .5, [(163.6275, 74.2), (163.6275, 75.65)])
T(P5, .5, [(166.37, 74.2), (167.0, 74.8), (171.5, 74.8), (171.5, 70.4)])

# ------------------------------------------------ Supervision VMON, R305/R307 ----
VM3, VM5 = '/VMON_3V3', '/VMON_5V'
T(VM3, .2, [(187.91, 124.25), (187.91, 125.0), (187.4, 125.51), (187.4, 133.92), (186.14, 133.92)])
T(VM3, .2, [(187.4, 129.27), (186.14, 129.27)])
V(VM3, (186.9, 129.3))
T(VM3, .2, [(186.9, 129.3), (181.0, 129.3), (181.0, 131.0)], B)
V(VM3, (181.0, 131.0))
T(VM3, .2, [(181.0, 131.0), (181.0, 132.27)])
T(VM5, .2, [(189.18, 124.25), (189.18, 125.0), (189.7, 125.52), (189.7, 133.92), (188.71, 133.92)])
T(VM5, .2, [(189.7, 129.27), (188.71, 129.27)])
T(VM5, .2, [(188.71, 133.92), (188.71, 135.0), (184.6, 135.0), (184.6, 132.27), (183.57, 132.27)])
T(P3D, .4, [(181.0, 133.92), (181.0, 139.0)])
V(P3D, (181.0, 139.0))
# +5V al divisor R305: tronco -> F.Cu y125.3 -> B.Cu x156.5 / y138 -> R305.1.
T(P5, .5, [(147.3, 124.8), (147.8, 125.3), (156.5, 125.3)])
V(P5, (156.5, 125.3))
T(P5, .5, [(156.5, 125.3), (156.5, 138.0), (183.57, 138.0), (183.57, 135.0)], B)
V(P5, (183.57, 135.0))
T(P5, .5, [(183.57, 135.0), (183.57, 133.92)])
# PG_3V3D: R302.2 -> via -> B.Cu -> TP305.
PG = '/30_regulation/PG_3V3D'
T(PG, .2, [(151.0, 138.45), (149.8, 138.45)])
V(PG, (149.8, 138.45))
T(PG, .2, [(149.8, 138.45), (149.8, 147.3), (150.5, 148.0), (151.0, 148.0)], B)

b.Save(str(PCB))
print('OK', PCB)
