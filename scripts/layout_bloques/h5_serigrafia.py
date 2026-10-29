"""Agujeros M3 metalizados sin red (H1-H5), apoyo opcional en B.Cu y rotulos de serigrafia (pedido 2026-10-29).
1) H1-H4 -> MountingHole_3.2mm_M3_Pad en su lugar; H5 nuevo en (56.0, 38.5).
2) Rule area APOYO_CAJA_B: circulo de 8 mm en B.Cu en (63.5, 49.0), sin pistas/vias/pads/huellas; relleno permitido.
3) Serigrafia 0.8 x 0.8 / 0.15 mm: linea de la barrera CAN (ambas caras), pinout de J1/J2,
   nombre/version/fecha en B.Silkscreen y rotulos de zona donde no saturen. Nunca sobre pads ni vias.
Uso: /usr/bin/python3 h5_serigrafia.py <pcb_entrada> <pcb_salida> <reporte.json>
Coordenadas locales: (0,0) = esquina superior izquierda del contorno = (100,50) mm en KiCad."""
import sys, json, math
sys.path.insert(0, sys.path[0])
import pcbnew
from lay import OX, OY, mm, FMM, court

b = pcbnew.LoadBoard(sys.argv[1])
F = {f.GetReference(): f for f in b.GetFootprints()}
H, T, LW = FMM(0.8), FMM(0.15), FMM(0.15)
CLR = 0.2           # margen de la serigrafia nueva a pads, vias y otra serigrafia
FPLIB = '/usr/share/kicad/footprints/MountingHole.pretty'
rep = {}


def V(x, y):
    return pcbnew.VECTOR2I(FMM(x + OX), FMM(y + OY))


def L(p):
    return round(mm(p.x) - OX, 2), round(mm(p.y) - OY, 2)

# ------------------------------------------------------------------ 1: agujeros
H5_PATH = '/0a0c11dd-824c-4e9c-83c1-d221ce11d604'      # uuid del simbolo H5 en INCLI-VA.kicad_sch
HOLES = {'H1': (5, 5), 'H2': (95, 5), 'H3': (5, 95), 'H4': (95, 95), 'H5': (56.0, 38.5)}
NOTE = ('Agujero de fijacion M3 (3.2 mm) metalizado, anillo de 6.4 mm en ambas caras (huella oficial '
        'MountingHole_3.2mm_M3_Pad). SIN red: el simbolo no tiene pin, el anillo queda flotante y no une GND_VEH '
        'ni GND_CAN. Regla DRC: cobre a >= 0.5 mm del anillo y sin pistas ni vias a menos de 4 mm del centro '
        '(arandela). Posicion: ver docs/LAYOUT_NOTES.md.')
FIELDS = {'Datasheet': 'https://www.kicad.org/libraries/', 'Description': '', 'MPN': 'N/A (agujero PTH sin red)',
          'Manufacturer': 'N/A', 'DNP': '', 'Notes': NOTE}
for ref, (x, y) in HOLES.items():
    old = F.get(ref)
    nf = pcbnew.FootprintLoad(FPLIB, 'MountingHole_3.2mm_M3_Pad')
    nf.SetFPIDAsString('MountingHole:MountingHole_3.2mm_M3_Pad')
    if old is not None:
        nf.SetPath(old.GetPath()); nf.SetSheetname(old.GetSheetname()); nf.SetSheetfile(old.GetSheetfile())
        b.Remove(old)
    else:
        nf.SetPath(pcbnew.KIID_PATH(H5_PATH)); nf.SetSheetname('/'); nf.SetSheetfile('INCLI-VA.kicad_sch')
    nf.SetReference(ref); nf.SetValue('MountingHole_M3')
    for k, v in FIELDS.items():
        nf.SetField(k, v)
        nf.GetField(k).SetVisible(False); nf.GetField(k).SetLayer(pcbnew.F_Fab)
    nf.SetPosition(V(x, y))
    for p in nf.Pads():
        p.SetNetCode(0)
    b.Add(nf)
    F[ref] = nf
    # referencia hacia el interior de la placa
    t = nf.Reference()
    t.SetTextSize(pcbnew.VECTOR2I(H, H)); t.SetTextThickness(T); t.SetLayer(pcbnew.F_SilkS)
    dy = 4.3 if y < 50 else -4.3
    if ref == 'H5':
        dy = -4.3
    t.SetPosition(V(x, y + dy))

# ------------------------------------------------------------------ 2: apoyo de la caja (opcion B)
za = pcbnew.ZONE(b)
za.SetIsRuleArea(True); za.SetZoneName('APOYO_CAJA_B')
za.SetLayer(pcbnew.B_Cu)
za.SetDoNotAllowTracks(True); za.SetDoNotAllowVias(True); za.SetDoNotAllowPads(True)
za.SetDoNotAllowFootprints(True); za.SetDoNotAllowZoneFills(False)
o = za.Outline(); o.NewOutline()
for i in range(48):
    a = 2 * math.pi * i / 48
    o.Append(FMM(63.5 + OX + 4.0 * math.cos(a)), FMM(49.0 + OY + 4.0 * math.sin(a)))
b.Add(za)

# ------------------------------------------------------------------ obstaculos de serigrafia
def rect(x0, y0, x1, y1):
    s = pcbnew.SHAPE_POLY_SET(); s.NewOutline()
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        s.Append(int(px), int(py))
    return s


def bbpoly(bb, c=0.0):
    c = FMM(c)
    return rect(bb.GetLeft() - c, bb.GetTop() - c, bb.GetRight() + c, bb.GetBottom() + c)


def obstacles(side):
    sl = pcbnew.F_SilkS if side == pcbnew.F_Cu else pcbnew.B_SilkS
    hard, crt = [], []
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(side) or p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                s = p.GetEffectivePolygon(side); s2 = pcbnew.SHAPE_POLY_SET(s)
                s2.Inflate(FMM(CLR), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, FMM(0.01)); hard.append(s2)
        for g in f.GraphicalItems():
            if g.GetLayer() == sl:
                if isinstance(g, pcbnew.PCB_TEXT) and not g.IsVisible():
                    continue
                if isinstance(g, pcbnew.PCB_SHAPE):
                    s = pcbnew.SHAPE_POLY_SET()
                    g.TransformShapeToPolygon(s, sl, FMM(CLR), FMM(0.01), pcbnew.ERROR_INSIDE)
                    hard.append(s)
                else:
                    hard.append(bbpoly(g.GetBoundingBox(), CLR))
        for g in f.GetFields():
            if g.GetLayer() == sl and g.IsVisible():
                hard.append(bbpoly(g.GetBoundingBox(), CLR))
        if f.GetLayer() == side and not f.GetReference().startswith('H'):
            k = pcbnew.SHAPE_POLY_SET(court(f))
            k.Deflate(FMM(0.25), pcbnew.CORNER_STRATEGY_CHAMFER_ALL_CORNERS, FMM(0.01))
            crt.append(k)
    for v in b.GetTracks():
        if isinstance(v, pcbnew.PCB_VIA) or v.IsOnLayer(side):
            hard.append(bbpoly(v.GetBoundingBox(), CLR))
    return hard, crt


# La referencia de J1 ocupa el unico hueco junto a los pines (x 11-12.8): pasa debajo de la carcasa
t = F['J1'].Reference(); t.SetTextAngleDegrees(0); t.SetPosition(V(6.0, 83.4))
OB = {s: obstacles(s) for s in (pcbnew.F_Cu, pcbnew.B_Cu)}
SL = {pcbnew.F_Cu: pcbnew.F_SilkS, pcbnew.B_Cu: pcbnew.B_SilkS}
added = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}


def free(poly, side, body_ok=False):
    hard, crt = OB[side]
    bb = poly.BBox()
    if mm(bb.GetLeft()) - OX < 0.8 or mm(bb.GetRight()) - OX > 99.2 or mm(bb.GetTop()) - OY < 0.8 or mm(bb.GetBottom()) - OY > 99.2:
        return False
    if any(poly.Collide(h, 0) for h in hard + added[side]):
        return False
    if not body_ok and any(poly.Collide(c, 0) for c in crt):
        return False
    return True

# ------------------------------------------------------------------ 3a: linea de la barrera CAN
# Centro de la banda BARRERA_CAN (rule area existente): y 61.62 (borde -> U601), x 28.0 (debajo de U601) e y 88.75.
BARRIER = [(0.9, 61.62), (28.0, 61.62), (28.0, 88.75), (0.9, 88.75)]
DASH, GAP = 1.0, 0.5
rep['barrera_tramos'] = {}
for side in (pcbnew.F_Cu, pcbnew.B_Cu):
    kept = drop = 0
    for (x0, y0), (x1, y1) in zip(BARRIER, BARRIER[1:]):
        n = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / n, (y1 - y0) / n
        s = 0.0
        while s < n - 0.05:
            e = min(s + DASH, n)
            seg = pcbnew.PCB_SHAPE(b); seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
            seg.SetStart(V(x0 + ux * s, y0 + uy * s)); seg.SetEnd(V(x0 + ux * e, y0 + uy * e))
            seg.SetLayer(SL[side]); seg.SetWidth(LW)
            p = pcbnew.SHAPE_POLY_SET(); seg.TransformShapeToPolygon(p, SL[side], 0, FMM(0.01), pcbnew.ERROR_INSIDE)
            if free(p, side, body_ok=True):     # la barrera cruza el cuerpo de U601 a proposito
                b.Add(seg); kept += 1
            else:
                drop += 1
            s = e + GAP
    rep['barrera_tramos'][b.GetLayerName(SL[side])] = {'trazos': kept, 'omitidos': drop}

# ------------------------------------------------------------------ textos
def text(s, side, ang=0):
    t = pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(SL[side])
    t.SetTextSize(pcbnew.VECTOR2I(H, H)); t.SetTextThickness(T)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetMirrored(side == pcbnew.B_Cu); t.SetKeepUpright(False); t.SetTextAngleDegrees(ang)
    return t


def place(s, side, cands, ang=0, body_ok=False):
    """Primer candidato libre (lista ordenada por preferencia). Devuelve la posicion o None."""
    t = text(s, side, ang)
    for x, y in cands:
        t.SetPosition(V(x, y))
        # trazo real del texto (la caja de KiCad suma el interlineado y sobra ~0.5 mm por lado)
        p = pcbnew.SHAPE_POLY_SET(); t.TransformShapeToPolygon(p, SL[side], 0, FMM(0.01), pcbnew.ERROR_INSIDE)
        if free(p, side, body_ok):
            q = pcbnew.SHAPE_POLY_SET(); t.TransformShapeToPolygon(q, SL[side], FMM(CLR), FMM(0.01), pcbnew.ERROR_INSIDE)
            b.Add(t); added[side].append(q)
            return (round(x, 2), round(y, 2))
    return None


def grid(cx, cy, x0, y0, x1, y1, step=0.25):
    pts = [(x0 + i * step, y0 + j * step) for i in range(int((x1 - x0) / step) + 1) for j in range(int((y1 - y0) / step) + 1)]
    return sorted(pts, key=lambda q: math.hypot(q[0] - cx, q[1] - cy))


rep['textos'] = {}

# 3b: pinout de J1 (vertical, junto a cada pin, del lado de la placa) y J2 (debajo de la carcasa)
J1 = [('VIN', 1), ('GND', 2), ('CANH', 3), ('CANL', 4), ('GND_CAN', 5)]
for side in (pcbnew.F_Cu, pcbnew.B_Cu):
    for lab, pn in J1:
        py = L(F['J1'].FindPadByNumber(str(pn)).GetPosition())[1]
        # hueco de 1.4 mm entre la carcasa (x 10.97) y D102/D601 (x 12.43): texto vertical centrado en x 11.7
        c = [(x, py + dy) for x in (11.7, 11.6, 11.8, 12.3, 12.55) for dy in (0, 0.25, -0.25, 0.5, -0.5, 1.0, -1.0, 1.5, 1.8, 2.0)]
        rep['textos'][f'J1.{pn} {lab} {b.GetLayerName(SL[side])}'] = place(lab, side, c, 90, body_ok=True)
    for lab, pn in (('DO1', 1), ('DO2', 2)):
        px = L(F['J2'].FindPadByNumber(str(pn)).GetPosition())[0]
        # franja libre de 1.8 mm entre la carcasa (y 10.47) y D701/Q701/Q751 (y 12.29); DO1 a la derecha del triangulo del pin 1
        c = [(px + dx, y) for y in (11.38, 11.3, 11.45, 11.9) for dx in (0, 0.5, -0.5, 1.0, 1.5, 2.0, -1.0, -1.5)]
        rep['textos'][f'J2.{pn} {lab} {b.GetLayerName(SL[side])}'] = place(lab, side, c, 0, body_ok=True)

# 3c: rotulo de la barrera, dentro del dominio CAN, en ambas caras
for side in (pcbnew.F_Cu, pcbnew.B_Cu):
    rep['textos'][f'CAN AISLADO {b.GetLayerName(SL[side])}'] = place('CAN AISLADO', side, grid(19.0, 86.6, 13.0, 84.0, 24.0, 87.3))

# 3d: nombre, version y fecha en la cara inferior
rep['textos']['placa B.Silkscreen'] = place('INCLI-VA  Rev A  2026-10-29', pcbnew.B_Cu, grid(45.0, 76.0, 30.0, 68.0, 62.0, 82.0))

# 3e: rotulos de zona (solo si hay lugar libre cerca del bloque; si no, se omiten)
ZONES = [('ENTRADA', 10.0, 36.5, 0.0, 32.5, 24.0, 46.0),
         ('BUCK 5V', 45.0, 19.0, 36.0, 17.0, 54.0, 21.0),
         ('SALIDAS DO', 75.0, 30.0, 58.0, 26.0, 88.0, 34.0),
         ('SENSORES', 52.0, 62.5, 44.0, 58.5, 62.0, 66.0)]
for lab, cx, cy, x0, y0, x1, y1 in ZONES:
    rep['textos'][f'zona {lab}'] = place(lab, pcbnew.F_Cu, grid(cx, cy, x0, y0, x1, y1))

b.Save(sys.argv[2])
json.dump(rep, open(sys.argv[3], 'w'), indent=1, ensure_ascii=False)
print(json.dumps(rep, indent=1, ensure_ascii=False))
