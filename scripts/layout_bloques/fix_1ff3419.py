"""Correcciones sobre la ubicacion del usuario (commit 1ff3419), pedido del 2026-10-29.
1) C403 junto al EN de U401; 2) lazos del buck U201; 3) J401 hacia adentro;
4) courtyards a 1 mm (0.5 mm para pasivos del propio IC); 5) referencias 0.8/0.8/0.15 en serigrafia.
Uso: /usr/bin/python3 fix_1ff3419.py <pcb_entrada> <pcb_salida> <reporte.json> [dx_J401]
Coordenadas locales: (0,0) = esquina superior izquierda del contorno = (100,50) mm en KiCad."""
import sys, json, math, itertools
sys.path.insert(0, sys.path[0])
import pcbnew
from lay import OX, OY, mm, FMM, court, poly_dist

b = pcbnew.LoadBoard(sys.argv[1])
DX_J401 = float(sys.argv[4]) if len(sys.argv) > 4 else -0.4
F = {f.GetReference(): f for f in b.GetFootprints()}


def put(ref, x, y, rot=None):
    f = F[ref]
    if rot is not None:
        f.SetOrientationDegrees(rot)
    f.SetPosition(pcbnew.VECTOR2I(FMM(x + OX), FMM(y + OY)))


def pos(ref):
    p = F[ref].GetPosition()
    return mm(p.x) - OX, mm(p.y) - OY

# ------------------------------------------------------------------ 1-3: movimientos explicitos
# U201 (34.25, 13.85): pines 1 GND / 2 EN / 3 VIN a la izquierda (x 31.69), 8 SW / 7 BOOT a la derecha.
MOVES = {
    'C202': (29.27, 13.20, 90),    # pad1 +VPROT abajo (pines 2/3), pad2 GND arriba (pin 1)
    'C201': (32.34, 7.90, 0),      # detras de C202, en el lugar que dejo libre
    'C102': (25.20, 15.60, 180),   # 1.4 mm a la izquierda para dar lugar a C202
    'C204': (42.60, 13.20, -90),   # columna a la derecha de C203: pad1 +5V arriba (hacia L201 pad 2)
    'C205': (46.00, 13.20, -90),
    'C206': (49.40, 13.20, -90),
    'R201': (42.90, 17.45, 180),   # +5V a la derecha (Cout), FB a la izquierda (R202)
    'C403': (87.00, 53.50, 90),    # pad1 MCU_RST_N abajo, hacia el pin 3 de U401
    'R805': (84.50, 53.53, -90),   # VAR_ID: se corren para dar lugar a C403
    'R806': (81.90, 53.53, -90),
    # U101: columna izquierda subida a paso 4.05 mm (libre sobre R107) y fila inferior a paso 2.55 mm
    'R107': (20.30, 18.52, 90),
    'R106': (20.30, 22.57, 90),
    'C109': (20.30, 26.62, 90),
    'R105': (20.30, 30.67, 90),
    'R109': (22.875, 29.56, -90),
    'C110': (25.425, 29.56, -90),
    'R110': (27.975, 29.56, -90),
    'R111': (30.525, 29.56, 90),
}
for r, (x, y, a) in MOVES.items():
    put(r, x, y, a)
jx, jy = pos('J401')
put('J401', jx + DX_J401, jy)
FIXED = set(MOVES) | {'J401'}

# ------------------------------------------------------------------ 4: courtyards
GND = {'GND_VEH', 'GND_CAN', 'GNDISO_CAN'}
NUDGE_OK = ('R', 'C', 'D', 'FB')          # piezas que se pueden correr un poco
MAXD = 1.0


def nets(f):
    return {p.GetNetname().split('/')[-1] for p in f.Pads()} - GND - {''}


def target(a, c):
    fa, fc = F[a], F[c]
    for ic, ps in ((fa, fc), (fc, fa)):
        if ic.GetReference().startswith('U') and ps.GetReference()[:1] in 'RC' and nets(ic) & nets(ps):
            return 0.5
    return 1.0


def is_rule_area_ok(f):
    for z in b.Zones():
        if z.GetIsRuleArea() and f.GetReference() != 'U601':
            for p in f.Pads():
                if z.Outline().Collide(p.GetEffectivePolygon(pcbnew.F_Cu), 0):
                    return False
    ko = [z for z in F['U401'].Zones()][0].Outline()
    if f.GetLayer() == pcbnew.F_Cu and court(f).Collide(ko, 0):
        return False
    bp = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(bp, True)
    c = court(f)
    for i in range(c.OutlineCount()):
        o = c.Outline(i)
        for k in range(o.PointCount()):
            if not bp.Contains(o.CPoint(k)):
                return False
    return True


def neighbours(ref, rad=8.0):
    f = F[ref]; x, y = pos(ref)
    out = []
    for o, g in F.items():
        if o == ref or g.GetLayer() != f.GetLayer():
            continue
        ox, oy = pos(o)
        bb = g.GetBoundingBox(False)
        if abs(ox - x) < rad + mm(bb.GetWidth()) / 2 and abs(oy - y) < rad + mm(bb.GetHeight()) / 2:
            out.append(o)
    return out


def gaps(ref):
    c = court(F[ref])
    return {o: poly_dist(c, court(F[o])) for o in neighbours(ref)}


def conn_len(ref):
    """suma de distancias de los pads de ref a los pads mas cercanos de su misma red (sin GND)"""
    s = 0.0
    for p in F[ref].Pads():
        n = p.GetNetCode(); nn = p.GetNetname().split('/')[-1]
        if nn in GND or n <= 0:
            continue
        best = 1e9
        for q in b.GetPads():
            if q.GetNetCode() == n and q.GetParentFootprint() is not F[ref]:
                best = min(best, mm((p.GetPosition() - q.GetPosition()).EuclideanNorm()))
        s += 0 if best == 1e9 else best
    return s


def all_pairs():
    fps = list(F.values()); cs = {f.GetReference(): court(f) for f in fps}; out = []
    for f, g in itertools.combinations(fps, 2):
        if f.GetLayer() != g.GetLayer():
            continue
        a, c = f.GetReference(), g.GetReference()
        ba, bc = cs[a].BBox(), cs[c].BBox(); m = FMM(1.01)
        if ba.GetRight() + m < bc.GetLeft() or bc.GetRight() + m < ba.GetLeft() or ba.GetBottom() + m < bc.GetTop() or bc.GetBottom() + m < ba.GetTop():
            continue
        d = poly_dist(cs[a], cs[c])
        if d < 1.0:
            out.append((a, c, d))
    return out


def try_nudge(mov, other, tgt):
    x0, y0 = pos(mov); g0 = gaps(mov); L0 = conn_len(mov); best = None
    dirs = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in range(0, 360, 45)]
    for k in range(1, int(MAXD / 0.05) + 1):
        s = k * 0.05
        for ux, uy in dirs:
            put(mov, x0 + ux * s, y0 + uy * s)
            g = gaps(mov)
            if g.get(other, 9) < tgt - 1e-3:
                continue
            if any(v < min(target(mov, o), g0.get(o, 9)) - 1e-3 for o, v in g.items() if o != other):
                continue
            if not is_rule_area_ok(F[mov]):
                continue
            cost = s + 0.5 * max(0.0, conn_len(mov) - L0)
            if best is None or cost < best[0]:
                best = (cost, x0 + ux * s, y0 + uy * s)
        if best is not None and best[0] < s + 0.05:
            break
    put(mov, *(best[1:] if best else (x0, y0)))
    return best is not None


nudged = {}
for _ in range(3):
    for a, c, d in sorted(all_pairs(), key=lambda t: t[2]):
        tgt = target(a, c)
        d = poly_dist(court(F[a]), court(F[c]))
        if d >= tgt - 1e-3:
            continue
        cands = [r for r in (a, c) if r not in FIXED and r.startswith(NUDGE_OK) and not r.startswith('U')]
        cands.sort(key=lambda r: F[r].GetBoundingBox(False).GetArea())
        for mv in cands:
            x0, y0 = pos(mv)
            if try_nudge(mv, c if mv == a else a, tgt):
                x1, y1 = pos(mv); nudged[mv] = round(math.hypot(x1 - x0, y1 - y0) + nudged.get(mv, 0), 2)
                break
rest = [(a, c, round(d, 2), target(a, c)) for a, c, d in all_pairs()]

# ------------------------------------------------------------------ 5: referencias en serigrafia
H, W, T = FMM(0.8), FMM(0.8), FMM(0.15)
CLR = 0.15                                   # mm de aire alrededor del texto
bp = pcbnew.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(bp, True)
edge_in = pcbnew.SHAPE_POLY_SET(bp); edge_in.Deflate(FMM(0.4), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, FMM(0.01)) if hasattr(pcbnew, 'CORNER_STRATEGY_ROUND_ALL_CORNERS') else None


def rect_poly(x0, y0, x1, y1):
    s = pcbnew.SHAPE_POLY_SET(); s.NewOutline()
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        s.Append(int(px), int(py))
    return s


def obstacles(side):
    pads, silk, crt = [], [], {}
    silk_layer = pcbnew.F_SilkS if side == pcbnew.F_Cu else pcbnew.B_SilkS
    for f in F.values():
        for p in f.Pads():
            if p.IsOnLayer(side) or p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                pads.append(p.GetEffectivePolygon(side))
        for g in f.GraphicalItems():
            if g.GetLayer() == silk_layer and not isinstance(g, pcbnew.PCB_TEXT):
                bb = g.GetBoundingBox(); silk.append((f.GetReference(), rect_poly(bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())))
        # textos visibles que no son la referencia (p. ej. RESET/BOOT de SW401/SW402): obstaculo para todos
        for g in list(f.GetFields()) + [g for g in f.GraphicalItems() if isinstance(g, pcbnew.PCB_TEXT)]:
            if g.GetLayer() == silk_layer and g.IsVisible() and not (isinstance(g, pcbnew.PCB_FIELD) and g.IsReference()):
                bb = g.GetBoundingBox(); c = FMM(CLR)
                silk.append(('', rect_poly(bb.GetLeft() - c, bb.GetTop() - c, bb.GetRight() + c, bb.GetBottom() + c)))
        if f.GetLayer() == side:
            crt[f.GetReference()] = court(f)
    for v in b.GetTracks():
        if isinstance(v, pcbnew.PCB_VIA):
            pads.append(rect_poly(*[c for c in (v.GetBoundingBox().GetLeft(), v.GetBoundingBox().GetTop(), v.GetBoundingBox().GetRight(), v.GetBoundingBox().GetBottom())]))
    return pads, silk, crt


placed, fab_only = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}, []


def text_box(t):
    bb = t.GetBoundingBox(); c = FMM(CLR)
    return rect_poly(bb.GetLeft() - c, bb.GetTop() - c, bb.GetRight() + c, bb.GetBottom() + c)


def deflate(c, d):
    k = pcbnew.SHAPE_POLY_SET(c); k.Deflate(FMM(d), pcbnew.CORNER_STRATEGY_CHAMFER_ALL_CORNERS, FMM(0.01)); return k


def place_ref(f, body=False):
    side = f.GetLayer(); t = f.Reference()
    t.SetLayer(pcbnew.F_SilkS if side == pcbnew.F_Cu else pcbnew.B_SilkS)
    t.SetTextSize(pcbnew.VECTOR2I(W, H)); t.SetTextThickness(T); t.SetVisible(True)
    t.SetMirrored(side == pcbnew.B_Cu)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    pads, silk, crt = OB[side]
    if body:   # segunda pasada: solo el cuerpo ajeno (courtyard - 0.25 mm) bloquea el texto
        crt = {r: deflate(c, 0.25) for r, c in crt.items()}
    cb = court(f).BBox(); ref = f.GetReference()
    best = None
    for ang in (0, 90):
        t.SetKeepUpright(False); t.SetTextAngleDegrees(ang)
        t.SetPosition(pcbnew.VECTOR2I(0, 0)); bb = t.GetBoundingBox()
        hw, hh = bb.GetWidth() / 2, bb.GetHeight() / 2
        for off in (-0.2, 0.05, 0.3, 0.6, 1.0, 1.5, 2.0, 2.5):
            o = FMM(off)
            ring = []
            n = 17
            for i in range(n):
                fx = cb.GetLeft() + (cb.GetWidth()) * i / (n - 1)
                fy = cb.GetTop() + (cb.GetHeight()) * i / (n - 1)
                ring += [(fx, cb.GetTop() - o - hh), (fx, cb.GetBottom() + o + hh),
                         (cb.GetLeft() - o - hw, fy), (cb.GetRight() + o + hw, fy)]
            for px, py in ring:
                t.SetPosition(pcbnew.VECTOR2I(int(px), int(py)))
                tb = text_box(t)
                tbb = t.GetBoundingBox()
                inside = all(bp.Contains(pcbnew.VECTOR2I(int(x), int(y))) and
                             bp.Contains(pcbnew.VECTOR2I(int(x), int(y))) for x, y in
                             ((tbb.GetLeft() - FMM(0.3), tbb.GetTop() - FMM(0.3)), (tbb.GetRight() + FMM(0.3), tbb.GetTop() - FMM(0.3)),
                              (tbb.GetLeft() - FMM(0.3), tbb.GetBottom() + FMM(0.3)), (tbb.GetRight() + FMM(0.3), tbb.GetBottom() + FMM(0.3))))
                if not inside:
                    continue
                if any(tb.Collide(p, 0) for p in pads):
                    continue
                if any(tb.Collide(q, 0) for q in placed[side]):
                    continue
                if any(tb.Collide(s, 0) for r, s in silk):   # tambien la serigrafia propia (el DRC la marca)
                    continue
                if any(r != ref and t.GetBoundingBox().Intersects(c.BBox()) and rect_poly(tbb.GetLeft(), tbb.GetTop(), tbb.GetRight(), tbb.GetBottom()).Collide(c, 0) for r, c in crt.items()):
                    continue
                cx, cy = cb.GetCenter().x, cb.GetCenter().y
                cost = off * 3 + mm(int(math.hypot(px - cx, py - cy))) * 0.2
                tall = cb.GetHeight() > cb.GetWidth() * 1.3
                if (ang == 90) != tall:
                    cost += 0.4
                if any(s.Collide(tb, 0) for r, s in silk if r == ref):
                    cost += 1.0
                if best is None or cost < best[0]:
                    best = (cost, ang, px, py)
        if best and best[0] < 1.0:
            break
    if best is None and not body:
        return place_ref(f, True)
    if best is None:
        t.SetLayer(pcbnew.F_Fab if side == pcbnew.F_Cu else pcbnew.B_Fab)
        t.SetTextAngleDegrees(0); t.SetPosition(cb.GetCenter())
        fab_only.append(ref); return
    _, ang, px, py = best
    t.SetTextAngleDegrees(ang); t.SetPosition(pcbnew.VECTOR2I(int(px), int(py)))
    placed[side].append(text_box(t))


# R103 trae un ${REFERENCE} propio en F.Silkscreen (0.8/0.12): duplica la referencia, pasa a F.Fab
for g in F['R103'].GraphicalItems():
    if isinstance(g, pcbnew.PCB_TEXT) and g.GetText() == '${REFERENCE}' and g.GetLayer() == pcbnew.F_SilkS:
        g.SetLayer(pcbnew.F_Fab)
OB = {s: obstacles(s) for s in (pcbnew.F_Cu, pcbnew.B_Cu)}
order = sorted(F.values(), key=lambda f: court(f).BBox().GetArea())
for f in order:
    place_ref(f)

b.Save(sys.argv[2])
json.dump({'movidos': {r: list(map(lambda v: round(v, 2), pos(r))) for r in FIXED},
           'empujados_mm': nudged, 'courtyards_bajo_1mm': rest, 'solo_fab': fab_only},
          open(sys.argv[3], 'w'), indent=1)
print('empujados', nudged); print('bajo 1 mm', rest); print('solo F.Fab', fab_only)
