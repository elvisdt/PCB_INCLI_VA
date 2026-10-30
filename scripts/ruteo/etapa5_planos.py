"""Etapa 5 planos. Regenera zonas E5_* y el grupo CLAUDE_ETAPA5 (costura), con KiCad cerrado.
Uso: etapa5_planos.py [PCB]  (por defecto INCLI-VA.kicad_pcb del proyecto).
Criterios del usuario (2026-10-30), registrados en RUTEO_TRASPASO.md:
- GND_VEH en B.Cu (toda la placa) y F.Cu donde quepa; GND_CAN en ambas caras solo en el dominio
  aislado y U101_RTN en isla propia, ambas con mayor prioridad.
- Alivio termico (rayos 0.5 mm) salvo las conexiones solidas de INCLI-VA.kicad_dru.
- Costura cada 5-10 mm, mas densa en el borde y alrededor del ESP32; ninguna via nueva dentro
  del circulo del iman ni del area B; islas sin conexion eliminadas, astillas < 0.25 mm fuera.
"""
import math, re, sys
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parents[2]
PCB = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'INCLI-VA.kicad_pcb'
assert not list(PCB.parent.glob('~*.lck')), 'Cerrar KiCad antes de ejecutar'
GROUP = 'CLAUDE_ETAPA5'

# Quitar zonas E5_* y el grupo anterior con sus vias, por texto (como etapa3/4).
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
members = set()
if old:
    assert len(old) == 1
    members = set(re.findall(r'"([0-9a-f-]{36})"', old[0][2].split('(members', 1)[1]))
cuts = []
for a, z, block in blocks:
    uid = re.search(r'\(uuid "([0-9a-f-]{36})"\)', block)
    if (old and (a, z, block) == old[0]) or (block.startswith(('(via', '(segment')) and uid and uid[1] in members) \
            or (block.startswith('(zone') and re.search(r'\(name "E5_', block)):
        cuts.append((a, z))
for a, z in reversed(cuts): source = source[:a] + source[z:]
PCB.write_text(source)

b = k.LoadBoard(str(PCB))
mm, tm = k.FromMM, k.ToMM
F, B = k.F_Cu, k.B_Cu
group = k.PCB_GROUP(b); group.SetName(GROUP); b.Add(group)
G, GC, RTN = 'GND_VEH', 'GND_CAN', '/10_power_input/U101_RTN'

# ------------------------------------------------------------------ zonas ----
# Dominio CAN: interior de BARRERA_CAN (x <= 124.6, y 112.87-137.5).
CAN = (99.5, 112.87, 124.6, 137.5)
E = (99.0, 49.0, 201.0, 151.0)  # mas grande que el borde: el relleno respeta JLC_borde
U601 = k.SHAPE_POLY_SET(b.FindFootprintByReference('U601').GetCourtyard(k.F_CrtYd))
U601.Inflate(mm(.05), k.CORNER_STRATEGY_ROUND_ALL_CORNERS, mm(.01))
def zone(name, net, layer, pts, prio):
    z = k.ZONE(b); z.SetZoneName(name); z.SetLayer(layer); z.SetNet(b.FindNet(net))
    z.SetAssignedPriority(prio)
    o = z.Outline(); o.NewOutline()
    for x, y in pts: o.Append(mm(x), mm(y))
    o.BooleanSubtract(U601)  # ISO_sin_relleno_bajo_U601 rechaza zonas cuyo contorno toca su courtyard
    z.SetLocalClearance(mm(.25)); z.SetMinThickness(mm(.25))
    z.SetPadConnection(k.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(.3)); z.SetThermalReliefSpokeWidth(mm(.5))
    z.SetIslandRemovalMode(k.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z); return z
veh = [(E[0], E[1]), (E[2], E[1]), (E[2], E[3]), (E[0], E[3]), (E[0], CAN[3]), (CAN[2], CAN[3]),
       (CAN[2], CAN[1]), (E[0], CAN[1])]
can = [(E[0], CAN[1]), (CAN[2], CAN[1]), (CAN[2], CAN[3]), (E[0], CAN[3])]
for L, s in ((B, 'B'), (F, 'F')):
    zone(f'E5_GND_VEH_{s}', G, L, veh, 0)
    zone(f'E5_GND_CAN_{s}', GC, L, can, 2)
# Isla RTN en B.Cu bajo el EP de U101 (pad 25, flotante): solo su red, aislada por U101_RTN_aislado.
zone('E5_U101_RTN_B', RTN, B, [(124.0, 72.6), (126.8, 72.6), (126.8, 75.4), (124.0, 75.4)], 3)

# ------------------------------------------------------------- costura ----
def P(x, y): return k.VECTOR2I(mm(x), mm(y))
CANNETS = {'GND_CAN', '/BUS_CAN_H', '/BUS_CAN_L', '/60_can/V_SOIN', '/60_can/V_SOOUT', '/60_can/GNDISO_CAN',
           '/60_can/CAN_RS', 'Net-(C609-Pad1)', 'unconnected-(U601-AUX_{OUT}-Pad17)'}
def clr(net, cls, mine):
    c = {'HV': 1.25, 'PROT': .6, 'DO': .6}.get(cls, .25)
    if net in ('/VEH_DO1', '/VEH_DO2'): c = max(c, .6)
    if (net in CANNETS) != (mine in CANNETS): c = 2.5
    return c
def dseg(px, py, a, z):
    ax, ay = a; dx, dy = z[0] - ax, z[1] - ay; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)
segs, vias, pads, crt = [], [], [], []
def xy(v): return (tm(v.x), tm(v.y))
for t in b.GetTracks():
    n, cl = t.GetNetname(), t.GetNetClassName()
    if t.Type() == k.PCB_VIA_T:
        vias.append((*xy(t.GetPosition()), tm(t.GetWidth(F)) / 2, n, cl))
    elif t.Type() == k.PCB_ARC_T:
        pts = [xy(t.GetStart()), xy(t.GetMid()), xy(t.GetEnd())]
        for a, z in zip(pts, pts[1:]): segs.append((a, z, tm(t.GetWidth()) / 2, n, cl))
    else:
        segs.append((xy(t.GetStart()), xy(t.GetEnd()), tm(t.GetWidth()) / 2, n, cl))
for f in b.GetFootprints():
    for p in f.Pads():
        bb = p.GetBoundingBox()
        pads.append((tm(bb.GetLeft()), tm(bb.GetTop()), tm(bb.GetRight()), tm(bb.GetBottom()),
                     p.GetNetname(), p.GetNetClassName(), p.GetAttribute() == k.PAD_ATTRIB_PTH))
    # Vias tapadas permitidas bajo el modulo (ya hay de etapa 4), los electroliticos C104/C105 y J2.
    if f.GetReference() in ('U401', 'C104', 'C105', 'J2'): continue
    for L in (k.F_CrtYd, k.B_CrtYd):
        c = f.GetCourtyard(L)
        if c.OutlineCount(): crt.append(c)
outline = k.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(outline, True)
HOLES = [(105, 55), (195, 55), (105, 145), (195, 145), (156, 88.5)]
added = []
def ok(x, y, net):
    if net == G and CAN[0] - 3 < x < CAN[2] + 3 and CAN[1] - 3 < y < CAN[3] + 3: return False
    if net == GC and not (CAN[0] + .9 < x < CAN[2] - 1.2 and CAN[1] + 1.2 < y < CAN[3] - 1.2): return False
    if 99.5 - .5 < x < 131.4 + .5 and 110.37 - .5 < y < 140 + .5 and not (x < CAN[2] - 1.2 and CAN[1] + 1.2 < y < CAN[3] - 1.2):
        return False  # banda de la barrera
    if x > 191.94 - .8 and 91.5 - .8 < y < 139.5 + .8: return False  # antena
    if math.hypot(x - 163.5, y - 99) < 4.4 or math.hypot(x - 150, y - 100) < 9.3: return False  # area B, iman
    if any(math.hypot(x - hx, y - hy) < 4.6 for hx, hy in HOLES): return False
    for i in range(8):
        a = i * math.pi / 4
        if not outline.Contains(P(x + 1.2 * math.cos(a), y + 1.2 * math.sin(a))): return False
    for c in crt:
        if c.Contains(P(x, y)): return False
    for a, z, w, n, cl in segs:
        need = .3 + w + (clr(n, cl, net) if n != net else .25)
        if dseg(x, y, a, z) < need: return False
    for vx, vy, r, n, cl in vias + added:
        need = .3 + r + (clr(n, cl, net) if n != net else .45)
        if math.hypot(x - vx, y - vy) < need: return False
    for x0, y0, x1, y1, n, cl, th in pads:
        d = math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1))
        if d < .3 + (clr(n, cl, net) if n != net else .3): return False
    return True
def V(x, y, net=G):
    v = k.PCB_VIA(b); v.SetPosition(P(x, y)); v.SetWidth(mm(.6)); v.SetDrill(mm(.3))
    v.SetNet(b.FindNet(net)); b.Add(v); group.AddItem(v)
    added.append((x, y, .3, net, 'Default')); return v
def near(x, y, net=G, r=1.6, step=.2):
    """Primer punto valido en espiral alrededor de (x, y)."""
    for i in range(int(r / step) + 1):
        d = i * step
        for j in range(max(1, int(2 * math.pi * d / step))):
            a = 2 * math.pi * j / max(1, int(2 * math.pi * d / step))
            px, py = round(x + d * math.cos(a), 2), round(y + d * math.sin(a), 2)
            if ok(px, py, net): return px, py
    return None
def tryV(x, y, net=G, r=1.6):
    p = near(x, y, net, r)
    if p: V(*p, net)
    return p
def T(net, w, pts, layer=F):
    for a, z in zip(pts, pts[1:]):
        t = k.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*z)); t.SetLayer(layer); t.SetWidth(mm(w))
        t.SetNet(b.FindNet(net)); b.Add(t); group.AddItem(t)
        segs.append((a, z, w / 2, net, 'Default'))
# C404 (desacople de VBUS, etapa 3): su GND (pad 2 y via (190.375,81.45)) quedaba encerrado en ambas
# caras por los ramales D+/D- y la rama sur de VBUS en B.Cu (via (188.95,81.45) -> (192.55,83.3)). Esa rama se
# reemplaza por un enlace B.Cu entre las dos vias VBUS de J401 (norte (190.95,78.1) y sur), por el este de los
# ramales y bajo la fila de pads de J401, y una pista GND B.Cu sale hasta la via GND existente (192.4,84.285).
VB = '/40_mcu/VBUS'
OLD_VB = {((188.95, 81.45), (189.25, 81.75)), ((189.25, 81.75), (189.25, 82.8)), ((189.25, 82.8), (189.75, 83.3)),
          ((189.75, 83.3), (192.55, 83.3))}
for t in list(b.GetTracks()):
    if t.Type() == k.PCB_TRACE_T and t.GetNetname() == VB and t.GetLayer() == B:
        e = tuple(sorted((tuple(round(c, 3) for c in xy(t.GetStart())), tuple(round(c, 3) for c in xy(t.GetEnd())))))
        if e in {tuple(sorted(x)) for x in OLD_VB}:
            g = t.GetParentGroup()
            if g: g.RemoveItem(t)
            b.Remove(t)
            segs[:] = [q for q in segs if not (q[3] == VB and tuple(sorted(tuple(round(c, 3) for c in p) for p in q[:2])) == e)]
T(VB, .4, [(190.95, 78.1), (191.2, 77.85), (193.35, 77.85), (193.6, 78.1), (193.6, 82.6), (192.9, 83.3), (192.55, 83.3)], B)
T(G, .3, [(190.375, 81.45), (189.7, 81.75), (189.3, 82.15), (189.3, 83.0), (189.8, 83.5), (191.6, 83.5),
          (192.4, 84.285)], B)
# 0) Retornos encerrados entre VMON_3V3/VMON_5V (F.Cu) y el tronco +3V3_D (B.Cu x188.9):
#    via a 0.25 mm de ambos, en el hueco de 0.55 mm entre bordes.
for pad, via in (((188.71, 127.72), (188.05, 126.55)), ((188.71, 132.27), (188.05, 130.95))):
    T(G, .3, [pad, (188.05, pad[1] - .6), via]); V(*via)
# 1) Retorno del tramo INT1/INT2 bajo el modulo: vias a ambos lados de los carriles B.Cu.
for (ax, ay), (zx, zy) in [((181.56, 123.9), (174.35, 123.9)), ((182.83, 124.4), (173.85, 124.4)),
                           ((174.35, 123.9), (174.35, 108.5)), ((173.85, 124.4), (173.85, 109.8))]:
    L = math.hypot(zx - ax, zy - ay); ux, uy = (zx - ax) / L, (zy - ay) / L
    for f in [i / max(1, int(L / 3)) for i in range(int(L / 3) + 1)]:
        for s in (1, -1):
            tryV(ax + ux * L * f - s * uy * 1.0, ay + uy * L * f + s * ux * 1.0, r=.8)
# Tramos horizontales (y123.9/y124.4) bajo la fila inferior de pads del modulo: al norte solo hay vias de
# senal; al sur, vias GND en el hueco de 0.5 mm entre los pads (y125.0) y CAN_SILE F.Cu (y126.2).
for x in (176.0, 178.0, 180.0, 182.0):
    V(x, 125.58)
# 2) Costura junto a C605 (via de retorno en (144.28, 121.9)).
for dx, dy in ((1.6, 0), (0, 1.6), (-1.6, 0), (0, -1.6)):
    tryV(144.28 + dx, 121.9 + dy, r=.6)
# 3) Anillo alrededor del ESP32 (fuera de la antena), cada ~3 mm.
u = b.FindFootprintByReference('U401').GetCourtyard(k.F_CrtYd).BBox()
x0, y0, x1, y1 = tm(u.GetLeft()) - 1.2, tm(u.GetTop()) - 1.2, tm(u.GetRight()) + 1.2, tm(u.GetBottom()) + 1.2
ring = [(x0 + i * 3, y0) for i in range(int((x1 - x0) / 3) + 1)] + [(x0 + i * 3, y1) for i in range(int((x1 - x0) / 3) + 1)] \
     + [(x0, y0 + i * 3) for i in range(int((y1 - y0) / 3) + 1)] + [(x1, y0 + i * 3) for i in range(int((y1 - y0) / 3) + 1)]
for x, y in ring: tryV(x, y, r=1.2)
# 4) Borde de la placa cada ~4 mm (1.8 mm hacia adentro).
for x in [102 + 4 * i for i in range(25)]:
    for y in (51.8, 148.2): tryV(x, y, GC if CAN[0] < x < CAN[2] and CAN[1] < y < CAN[3] else G, r=1.0)
for y in [52 + 4 * i for i in range(25)]:
    for x in (101.8, 198.2):
        tryV(x, y, GC if CAN[0] < x < CAN[2] and CAN[1] < y < CAN[3] else G, r=1.0)
# 5) Retícula general cada 6 mm; dominio CAN con GND_CAN cada 5 mm.
for gx in [103 + 6 * i for i in range(17)]:
    for gy in [53 + 6 * j for j in range(17)]:
        tryV(gx, gy, r=1.8)
for gx in [102.5 + 5 * i for i in range(5)]:
    for gy in [115.5 + 5 * j for j in range(5)]:
        tryV(gx, gy, GC, r=1.8)

# --------------------------------------------- relleno e islas iterativo ----
filler = k.ZONE_FILLER(b)
zones = [z for z in b.Zones() if z.GetZoneName().startswith('E5_')]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_etapa5 import componentes
def inside(f, net, L, x, y):
    return any(s.Contains(P(x, y)) for s in f.get((net, L), []))
for it in range(5):
    for z in zones: z.SetIslandRemovalMode(k.ISLAND_REMOVAL_MODE_NEVER)
    filler.Fill(zones)
    f = {}
    for z in zones:
        for L in (F, B):
            if z.IsOnLayer(L): f.setdefault((z.GetNetname(), L), []).append(z.GetFilledPolysList(L))
    # Quitar vias de costura que no quedaron con cobre en ambas caras.
    gone = 0
    for v in list(group.GetItems()):
        if v.Type() != k.PCB_VIA_T: continue
        x, y = xy(v.GetPosition()); n = v.GetNetname()
        if not (inside(f, n, F, x, y) and inside(f, n, B, x, y)):
            group.RemoveItem(v); b.Remove(v); gone += 1
            added[:] = [a for a in added if (a[0], a[1]) != (round(x, 2), round(y, 2))]
    # Grupos separados del plano principal (islas o cadenas isla-via-isla): una via hacia el
    # cobre principal de la otra cara. Islas sin ningun elemento las quita el relleno final.
    new = 0
    for net, comps in componentes(b, (G, GC)).items():
        main = comps[0][4]
        for area, info, nitems, its, ps in comps[1:]:
            if area < .5 or not nitems: continue
            done = False
            for _, z, L, s, i in sorted(ps, key=lambda q: -abs(q[3].Outline(q[4]).Area())):
                other = B if L == F else F
                bb = s.Outline(i).BBox()
                gx0, gy0, gx1, gy1 = tm(bb.GetLeft()), tm(bb.GetTop()), tm(bb.GetRight()), tm(bb.GetBottom())
                for gy in [gy0 + .2 * j for j in range(int((gy1 - gy0) / .2) + 1)]:
                    for gx in [gx0 + .2 * q for q in range(int((gx1 - gx0) / .2) + 1)]:
                        px, py = round(gx, 2), round(gy, 2)
                        if s.Contains(P(px, py), i) and any(m[2] == other and m[3].Contains(P(px, py), m[4]) for m in main) and ok(px, py, net):
                            V(px, py, net); new += 1; done = True; break
                    if done: break
                if done: break
            if not done: print('  sin via posible:', net, [x[:2] + x[4:] for x in info][:3], nitems, 'items')
    print(f'iteracion {it}: vias quitadas {gone}, vias nuevas {new}')
    if not gone and not new: break
for z in zones: z.SetIslandRemovalMode(k.ISLAND_REMOVAL_MODE_ALWAYS)
filler.Fill(zones)
print('vias de costura', sum(1 for v in group.GetItems() if v.Type() == k.PCB_VIA_T))
b.Save(str(PCB))
print('OK', PCB)
