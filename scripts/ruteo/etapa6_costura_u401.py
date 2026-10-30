#!/usr/bin/python3
"""Etapa 6: costura GND_VEH a ambos lados del haz B.Cu bajo U401 (DO/PWR_FLT/LED).

Uso (KiCad cerrado): /usr/bin/python3 -B scripts/ruteo/etapa6_costura_u401.py [PCB]
Después: rellenar zonas (etapa6_teardrops.py lo hace) y repetir el DRC.
Usa la ranura medida por verify_ranura_u401.py (rellenos guardados). En cada lado, si dos vías GND
existentes (a ≤ 2.5 mm del borde de la ranura) quedan a más de PASO_MAX, intercala vías nuevas.
Una vía solo va donde hay GND_VEH relleno en F.Cu y en B.Cu y respeta holguras al resto del cobre.
Grupo CLAUDE_ETAPA6_COSTURA: se borra y se recrea (idempotente).
"""
import json, subprocess, sys
import pcbnew as k

pcb = sys.argv[1] if len(sys.argv) > 1 else 'INCLI-VA.kicad_pcb'
GRUPO, NET = 'CLAUDE_ETAPA6_COSTURA', 'GND_VEH'
VIA_D, VIA_H = 0.6, 0.3
HOLG = 0.25                     # cobre-cobre (regla general 0.2 + margen)
PASO_MAX, PASO = 4.0, 3.5
iu = k.FromMM

b = k.LoadBoard(pcb)
for g in list(b.Groups()):
    if g.GetName() == GRUPO:
        for it in list(g.GetItems()): b.Remove(it)
        b.Remove(g)
b.Save(pcb)
r = json.loads(subprocess.run(['/usr/bin/python3', '-B', 'scripts/ruteo/verify_ranura_u401.py', pcb],
                              capture_output=True, text=True, check=True).stdout)
b = k.LoadBoard(pcb)
net = b.FindNet(NET)
F, B = k.F_Cu, k.B_Cu
fills = {L: [z.GetFilledPolysList(L) for z in b.Zones()
             if not z.GetIsRuleArea() and z.GetNetname() == NET and z.IsOnLayer(L)] for L in (F, B)}
reglas = [z for z in b.Zones() if z.GetIsRuleArea()]
bordes = {float(y): w for y, w in r['bordes_por_y'].items()}   # y -> (x_izq, x_der)


def lleno(L, x, y): return any(s.Contains(k.VECTOR2I(iu(x), iu(y))) for s in fills[L])


def dseg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return ((px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2) ** .5


obst = []   # (tipo, datos)
for t in b.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    if t.Type() == k.PCB_VIA_T:
        obst.append(('via', s.x / 1e6, s.y / 1e6, t.GetWidth(F) / 2e6, t.GetNetname()))
    elif t.GetLayer() in (F, B) and t.GetNetname() != NET:
        obst.append(('trk', s.x / 1e6, s.y / 1e6, e.x / 1e6, e.y / 1e6, t.GetWidth() / 2e6))
pads, cys = [], []
for f in b.GetFootprints():
    for p in f.Pads():
        bb = p.GetBoundingBox()
        pads.append((bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6,
                     p.GetNetname(), p.HasHole()))
    if f.GetReference() != 'U401':
        for L in (k.F_CrtYd, k.B_CrtYd):
            c = f.GetCourtyard(L)
            if c.OutlineCount(): cys.append(c)


def valida(x, y):
    if not (lleno(F, x, y) and lleno(B, x, y)): return False
    p = k.VECTOR2I(iu(x), iu(y))
    if any(c.Contains(p) for c in cys): return False
    if any(z.GetLayerSet().Contains(F) or z.GetLayerSet().Contains(B) for z in reglas if z.Outline().Contains(p)):
        return False
    rv = VIA_D / 2
    for o in obst:
        if o[0] == 'via':
            if ((x - o[1]) ** 2 + (y - o[2]) ** 2) ** .5 < (1.0 if o[4] == NET else rv + o[3] + HOLG): return False
        elif dseg(x, y, *o[1:5]) < rv + o[5] + HOLG: return False
    for l, t_, rr, bo, n, hole in pads:
        dx = max(l - x, 0, x - rr); dy = max(t_ - y, 0, y - bo)
        # pad ajeno: holgura; pad GND: nada de vía en pad (soldadura a mano); con taladro: 0.5 mm
        lim = rv + (0.5 if hole else HOLG if n != NET else 0.1)
        if (dx * dx + dy * dy) ** .5 < lim: return False
    return True


ys = sorted(bordes)
y_ini, y_fin = ys[0] + 1.0, ys[-1] - 1.0
nuevas = []
for lado in (0, 1):
    sg = -1 if lado == 0 else 1
    def borde(y): return bordes[min(ys, key=lambda v: abs(v - y))][lado]
    exist = sorted(o[2] for o in obst if o[0] == 'via' and o[4] == NET and y_ini - 3 <= o[2] <= y_fin + 3
                   and 0 <= sg * (o[1] - borde(o[2])) <= 2.5)
    marcas = [y_ini - PASO_MAX / 2] + exist + [y_fin + PASO_MAX / 2]
    for a, c in zip(marcas, marcas[1:]):
        if c - a <= PASO_MAX: continue
        n = int((c - a) / PASO)
        for m in range(1, n + 1):
            y0 = a + (c - a) * m / (n + 1)
            hecho = False
            for dy in (0, .3, -.3, .6, -.6, .9, -.9):
                for d in [i / 10 for i in range(5, 26)]:
                    y = round(y0 + dy, 2); x = round(borde(y) + sg * d, 2)
                    if valida(x, y):
                        nuevas.append((x, y, lado)); obst.append(('via', x, y, VIA_D / 2, NET)); hecho = True
                        break
                if hecho: break

g = k.PCB_GROUP(b); g.SetName(GRUPO); b.Add(g)
for x, y, _ in nuevas:
    v = k.PCB_VIA(b); v.SetPosition(k.VECTOR2I(iu(x), iu(y)))
    v.SetWidth(iu(VIA_D)); v.SetDrill(iu(VIA_H)); v.SetNet(net); v.SetTeardropsEnabled(True)
    b.Add(v); g.AddItem(v)
b.Save(pcb)
print(json.dumps({'vias_nuevas': len(nuevas),
                  'oeste': [(x, y) for x, y, l in nuevas if l == 0], 'este': [(x, y) for x, y, l in nuevas if l == 1]}))
