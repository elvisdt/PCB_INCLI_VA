"""Aplica plan.py: rota, ubica y separa (>= GAP entre cajas de courtyard), luego guarda."""
import sys, importlib.util, pcbnew
sys.path.insert(0, sys.path[0])
from lay import OX, OY, mm, FMM

GAP = 1.02
spec = importlib.util.spec_from_file_location('plan', sys.argv[3])
plan = importlib.util.module_from_spec(spec); spec.loader.exec_module(plan)
b = pcbnew.LoadBoard(sys.argv[1])

# zonas prohibidas para piezas de la cara superior (x0, y0, x1, y1)
FORBID = [
    (91.69, 46.25, 112.69, 94.25),        # keep-out de antena
    (71.5, 60.5, 91.7, 80.0),             # cuerpo de U401 (su courtyard es una L con la antena)
    (0.0, 60.37, 31.4, 62.87),            # barrera: franja superior
    (24.6, 60.37, 31.4, 90.0),            # barrera: franja vertical (U601 exenta)
    (0.0, 87.5, 31.4, 90.0),              # barrera: franja inferior
    (71.9, 40.6, 73.9, 60.3),             # pasillo de USB D+/D- a la izquierda de los pines 13/14 (virtual)
    (73.0, 36.9, 84.0, 40.6),             # pasillo de USB desde U402 (virtual)
]
ZGAP = [0.3, GAP, GAP, GAP, GAP, 0.2, 0.2]
EXEMPT = {'U601': {2, 3, 4}, 'J1': {2, 3, 4}}
LIM = (0.4, 0.4, 99.6, 99.6)

boxes = {}   # ref -> [x, y, dx0, dy0, dx1, dy1, fixed]
for f in b.GetFootprints():
    ref = f.GetReference()
    if f.GetLayer() != pcbnew.F_Cu or ref == 'U401':
        continue
    if ref in plan.P:
        x, y, r, fx = plan.P[ref]
    else:
        x, y = mm(f.GetPosition().x) - OX, mm(f.GetPosition().y) - OY
        r, fx = f.GetOrientationDegrees(), True
        print('sin plan (queda fija):', ref)
    f.SetOrientationDegrees(r)
    f.SetPosition(pcbnew.VECTOR2I(FMM(x + OX), FMM(y + OY)))
    c = f.GetCourtyard(pcbnew.F_Cu); bb = c.BBox() if c.OutlineCount() else f.GetBoundingBox(False)
    px, py = mm(f.GetPosition().x) - OX, mm(f.GetPosition().y) - OY
    boxes[ref] = [x, y, mm(bb.GetLeft()) - OX - px, mm(bb.GetTop()) - OY - py,
                  mm(bb.GetRight()) - OX - px, mm(bb.GetBottom()) - OY - py, fx]

def rect(ref):
    x, y, a, c, d, e, _ = boxes[ref]
    return (x + a, y + c, x + d, y + e)

def push(r1, r2, GAP=GAP):
    """desplazamiento minimo (dx, dy) para alejar r1 de r2 hasta GAP; None si ya cumple."""
    if r1[2] + GAP <= r2[0] or r2[2] + GAP <= r1[0] or r1[3] + GAP <= r2[1] or r2[3] + GAP <= r1[1]:
        return None
    opts = [(r2[0] - GAP - r1[2], 0), (r2[2] + GAP - r1[0], 0), (0, r2[1] - GAP - r1[3]), (0, r2[3] + GAP - r1[1])]
    return min(opts, key=lambda v: abs(v[0]) + abs(v[1]))

for ent in getattr(plan, 'ROWS', []):
    lst, x, y, rot, d = ent
    for ref in lst:
        r_ = rot if not isinstance(ref, tuple) else ref[1]
        ref = ref if not isinstance(ref, tuple) else ref[0]
        f = b.FindFootprintByReference(ref)
        f.SetOrientationDegrees(r_)
        f.SetPosition(pcbnew.VECTOR2I(FMM(OX), FMM(OY)))
        c = f.GetCourtyard(pcbnew.F_Cu); bb = c.BBox()
        x0, x1 = mm(bb.GetLeft()) - OX, mm(bb.GetRight()) - OX
        y0, y1 = mm(bb.GetTop()) - OY, mm(bb.GetBottom()) - OY
        cy = y - (y0 + y1) / 2
        if d == 'L':      # x es el borde derecho; se avanza hacia la izquierda
            px = x - x1; x = px + x0 - GAP
        else:             # x es el borde izquierdo
            px = x - x0; x = px + x1 + GAP
        boxes[ref] = [px, cy, x0, y0, x1, y1, True]
refs = sorted(boxes)
for it in range(1500):
    moved = 0
    for i, r in enumerate(refs):
        if boxes[r][6]:
            continue
        R = rect(r)
        obst = [(rect(o), boxes[o][6]) for o in refs if o != r]
        obst = [(o, f, GAP) for o, f in obst]
        obst += [(z, True, ZGAP[k]) for k, z in enumerate(FORBID) if not (r in EXEMPT and k in EXEMPT[r])]
        for o, ofx, g in obst:
            v = push(R, o, g)
            if v is None:
                continue
            k = 1.0 if ofx else 0.55
            boxes[r][0] += v[0] * k; boxes[r][1] += v[1] * k
            R = rect(r); moved += 1
        # limites de placa
        x0, y0, x1, y1 = R
        if x0 < LIM[0]: boxes[r][0] += LIM[0] - x0
        if y0 < LIM[1]: boxes[r][1] += LIM[1] - y0
        if x1 > LIM[2]: boxes[r][0] -= x1 - LIM[2]
        if y1 > LIM[3]: boxes[r][1] -= y1 - LIM[3]
    if moved == 0:
        break
print('iteraciones', it, 'movimientos en la ultima', moved)

for ref, (x, y, *_ ) in boxes.items():
    f = b.FindFootprintByReference(ref)
    f.SetPosition(pcbnew.VECTOR2I(FMM(round(x, 2) + OX), FMM(round(y, 2) + OY)))
    if ref in plan.P and not plan.P[ref][3] and not boxes[ref][6]:
        d = ((x - plan.P[ref][0]) ** 2 + (y - plan.P[ref][1]) ** 2) ** 0.5
        if d > 1.5:
            print(f'  {ref} se movio {d:.1f} mm -> ({x:.1f},{y:.1f})')
for ref, (x, y) in plan.TP.items():
    f = b.FindFootprintByReference(ref)
    f.SetPosition(pcbnew.VECTOR2I(FMM(x + OX), FMM(y + OY)))
b.Save(sys.argv[2])
