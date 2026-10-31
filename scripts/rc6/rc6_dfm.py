#!/usr/bin/python3
"""rc6: correcciones del informe JLCDFM (docs/reference/dfm/JLCDFM_INCLI-VA_rc.pdf) sin mover componentes.

Uso: /usr/bin/python3 -B scripts/rc6/rc6_dfm.py [--solo-informe]
J-01 «Via to pad»: vías a < 0.10 mm (cobre) de un pad de F.Cu. Se alejan a lo largo de su tramo de conexión hasta
     0.15 mm; con las vías tapadas, esa es también la franja de máscara. Las pistas que llegan a la vía se estiran.
J-02 «Solder mask opening exposing trace»: tramos de F.Cu que pasan a < 0.10 mm de la abertura de un pad sin entrar
     en él. Se desplaza el tramo en perpendicular hasta 0.12 mm (y los vértices compartidos con sus vecinos).
     Excepción: D601.1 (CAN_H, misma red que el pad; correrlo lo acerca a la vía GND_CAN de la barrera).
J-03 «Silkscreen to hole / to pad»: textos de serigrafía (referencias, rótulos de placa) que pisan agujeros de vías,
     aberturas de pads u orificios. Se mueve solo el texto (espiral de hasta 2.5 mm, misma orientación; si no
     entra, girado 90°) a ≥ 0.15 mm de agujeros y aberturas, ≥ 0.10 mm de otra serigrafía y ≥ 0.5 mm del borde.
     Altura 0.8 mm y trazo 0.15 mm como mínimo (regla JLC_serigrafia). Los contornos de huella no se tocan (B).
Rótulos nuevos de TP105-TP107 (VS, VA, UVLO) en B.Silkscreen con el mismo buscador.
"""
import json, math, sys
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parents[2]
PCB = str(ROOT / 'INCLI-VA.kicad_pcb')
MM, mm, ERR = k.FromMM, k.ToMM, k.FromMM(0.005)
P = lambda x, y: k.VECTOR2I(MM(x), MM(y))
INFORME = '--solo-informe' in sys.argv
PASADA2 = '--pasada2' in sys.argv          # 2.ª pasada: abanico de direcciones (J-01), radio 4 mm y borde 0.3 mm (J-03)
RADIO, BORDE = (4.0, 0.3) if PASADA2 else (2.5, 0.5)
b = k.LoadBoard(PCB)
grupo = next(g for g in b.Groups() if g.GetName() == 'CLAUDE_RC6')
FS, BS = k.F_SilkS, k.B_SilkS


def poly(it, capa, c=0):
    s = k.SHAPE_POLY_SET(); it.TransformShapeToPolygon(s, capa, MM(c), ERR, k.ERROR_OUTSIDE); return s


def dist(a, b_):
    """Distancia mínima entre dos SHAPE_POLY_SET (0 si se tocan)."""
    i = k.SHAPE_POLY_SET(a); i.BooleanIntersection(b_)
    if i.OutlineCount(): return 0
    d = min(math.sqrt(b_.SquaredDistance(a.CVertex(j))) for j in range(a.FullPointCount()))
    return min(d, min(math.sqrt(a.SquaredDistance(b_.CVertex(j))) for j in range(b_.FullPointCount())))


pads_F = [p for f in b.GetFootprints() for p in f.Pads() if p.IsOnLayer(k.F_Cu)]

# ---------------- J-01 ----------------
CAN = {'GND_CAN', '/BUS_CAN_H', '/BUS_CAN_L', '/60_can/V_SOIN', '/60_can/V_SOOUT', '/60_can/GNDISO_CAN', '/60_can/CAN_RS',
       'Net-(C609-Pad1)'}
HVN = {'/10_power_input/VBAT_F', '/10_power_input/VIN_VEH'}


_pro = json.load(open(ROOT / 'INCLI-VA.kicad_pro'))['net_settings']
_cls = {c['name']: c['clearance'] for c in _pro['classes']}
NC = {pt['pattern']: _cls[pt['netclass']] for pt in _pro['netclass_patterns']}   # patrones = nombres exactos


def clr(n1, n2):
    if (n1 in CAN) != (n2 in CAN): return 2.5
    if n1 in HVN or n2 in HVN: return 1.25
    return max(NC.get(n1, 0.2), NC.get(n2, 0.2))


def via_libre(v, pos, ignorar):
    """La vía en pos respeta clearances contra el cobre de otras redes en F y B (y 0.45 mm entre agujeros)."""
    n = v.GetNetname(); fuera = {v.m_Uuid.AsString()} | {t.m_Uuid.AsString() for t in ignorar}
    for t in b.GetTracks():
        if t.m_Uuid.AsString() in fuera: continue
        if t.Type() == k.PCB_VIA_T and (t.GetPosition() - pos).EuclideanNorm() < MM(0.3 + 0.15 + 0.45): return False
        if t.GetNetname() == n: continue
        for capa in (k.F_Cu, k.B_Cu):
            if not t.IsOnLayer(capa): continue
            ts = poly(t, capa, clr(n, t.GetNetname()))
            if ts.Contains(pos) or math.sqrt(ts.SquaredDistance(pos)) < MM(0.3): return False
    for f in b.GetFootprints():
        for p in f.Pads():
            if (p.GetPosition() - pos).EuclideanNorm() > MM(6): continue
            for capa in (k.F_Cu, k.B_Cu):
                if not p.IsOnLayer(capa): continue
                c = 0.15 if p.GetNetname() == n else clr(n, p.GetNetname())
                ps = poly(p, capa, c)
                if ps.Contains(pos) or math.sqrt(ps.SquaredDistance(pos)) < MM(0.3): return False
    return True


print('J-01')
j01 = []
for v in [t for t in b.GetTracks() if t.Type() == k.PCB_VIA_T]:
    vs = poly(v, k.F_Cu)
    for p in pads_F:
        if (p.GetPosition() - v.GetPosition()).EuclideanNorm() > MM(4) or p.GetNetname() != v.GetNetname(): continue
        ps = poly(p, k.F_Cu)
        d = dist(vs, ps)
        if d >= MM(0.10): continue
        if ps.Contains(v.GetPosition()) and not any(ps.Contains(v.GetPosition() + k.VECTOR2I(int(MM(0.3) * math.cos(a)), int(MM(0.3) * math.sin(a))))
                                                     is False for a in [i * math.pi / 8 for i in range(16)]):
            continue                                                    # vía entera dentro del pad: no la toca
        trk = [t for t in b.GetTracks() if t.Type() == k.PCB_TRACE_T and v.GetPosition() in (t.GetStart(), t.GetEnd())]
        sale = next((t for t in trk if t.GetLayer() == k.F_Cu and (ps.Contains(t.GetStart()) or ps.Contains(t.GetEnd()))), None)
        o = (sale.GetStart() if ps.Contains(sale.GetStart()) else sale.GetEnd()) if sale else p.GetPosition()
        dx, dy = v.GetPosition().x - o.x, v.GetPosition().y - o.y; nrm = math.hypot(dx, dy)
        if nrm == 0: continue
        nueva = None
        for giro in ((0, 30, -30, 60, -60, 90, -90) if PASADA2 else (0,)):
            g = math.radians(giro); ux = (dx * math.cos(g) - dy * math.sin(g)) / nrm; uy = (dx * math.sin(g) + dy * math.cos(g)) / nrm
            for paso in [i * 0.05 for i in range(1, 30)]:
                cand = k.VECTOR2I(int(v.GetPosition().x + ux * MM(paso)), int(v.GetPosition().y + uy * MM(paso)))
                c = k.PCB_VIA(b); c.SetPosition(cand); c.SetWidth(v.GetWidth(k.F_Cu)); c.SetDrill(v.GetDrillValue())
                if dist(poly(c, k.F_Cu), ps) >= MM(0.15):
                    nueva = cand if via_libre(v, cand, trk) else None
                    break
            if nueva is not None: break
        nom = f'{p.GetParentFootprint().GetReference()}.{p.GetNumber()}'
        if nueva is None:
            print(f'  {nom}: vía ({mm(v.GetPosition().x):.2f}, {mm(v.GetPosition().y):.2f}) {mm(d):.3f} mm -> SIN LUGAR'); break
        print(f'  {nom}: vía ({mm(v.GetPosition().x):.2f}, {mm(v.GetPosition().y):.2f}) {mm(d):.3f} mm -> '
              f'({mm(nueva.x):.2f}, {mm(nueva.y):.2f}){"" if sale else " + tramo nuevo"}')
        j01.append(nom)
        if INFORME: break
        viejo = v.GetPosition()
        for t in trk:
            if t.GetStart() == viejo: t.SetStart(nueva)
            if t.GetEnd() == viejo: t.SetEnd(nueva)
        v.SetPosition(nueva)
        if not sale:                                                   # tramo pad -> vía
            t = k.PCB_TRACK(b); t.SetStart(p.GetPosition()); t.SetEnd(nueva); t.SetLayer(k.F_Cu); t.SetNet(v.GetNet())
            t.SetWidth(MM(min(0.3, mm(min(p.GetSize(k.F_Cu).x, p.GetSize(k.F_Cu).y)) * 0.8)))
            b.Add(t); grupo.AddItem(t)
        break

# ---------------- J-02 ----------------
# D601.1: el tramo de CAN_H (misma red que el pad) no se puede correr: queda a < 0.2 mm de la vía GND_CAN (111.9, 115.5).
J02_EXCLUIR = {'D601.1'}
print('J-02')
for t in [t for t in b.GetTracks() if t.Type() == k.PCB_TRACE_T and t.GetLayer() == k.F_Cu]:
    for p in pads_F:
        if not p.IsOnLayer(k.F_Mask) or not t.GetBoundingBox().Inflate(MM(0.3)).Intersects(p.GetBoundingBox()): continue
        pc = poly(p, k.F_Cu)
        if pc.Contains(t.GetStart()) or pc.Contains(t.GetEnd()): continue
        ts, pm = poly(t, k.F_Cu), poly(p, k.F_Mask)
        d = dist(ts, pm)
        if d == 0 or d >= MM(0.10): continue
        if f'{p.GetParentFootprint().GetReference()}.{p.GetNumber()}' in J02_EXCLUIR: continue
        # normal del tramo, hacia el lado opuesto al pad
        a, z = k.VECTOR2I(t.GetStart().x, t.GetStart().y), k.VECTOR2I(t.GetEnd().x, t.GetEnd().y)
        ux, uy = z.x - a.x, z.y - a.y; n = math.hypot(ux, uy)
        nx, ny = -uy / n, ux / n
        c = p.GetPosition(); m = k.VECTOR2I((a.x + z.x) // 2, (a.y + z.y) // 2)
        if (m.x - c.x) * nx + (m.y - c.y) * ny < 0: nx, ny = -nx, -ny
        paso = MM(0.12) - d
        print(f'  {p.GetParentFootprint().GetReference()}.{p.GetNumber()} {t.GetNetname()}: tramo '
              f'({mm(a.x):.2f}, {mm(a.y):.2f})-({mm(z.x):.2f}, {mm(z.y):.2f}) a {mm(d):.3f} mm, se corre {mm(paso):.3f} mm')
        if INFORME: break
        dv = k.VECTOR2I(int(nx * paso), int(ny * paso))
        yo = t.m_Uuid.AsString()
        vecinos = [u for u in b.GetTracks() if u.Type() == k.PCB_TRACE_T and u.GetNetname() == t.GetNetname()
                   and u.GetLayer() == k.F_Cu and u.m_Uuid.AsString() != yo]
        for e in (a, z):
            ne = k.VECTOR2I(e.x + dv.x, e.y + dv.y)
            for u in vecinos:
                if (u.GetStart().x, u.GetStart().y) == (e.x, e.y): u.SetStart(ne)
                if (u.GetEnd().x, u.GetEnd().y) == (e.x, e.y): u.SetEnd(ne)
        t.SetStart(k.VECTOR2I(a.x + dv.x, a.y + dv.y)); t.SetEnd(k.VECTOR2I(z.x + dv.x, z.y + dv.y))
        break

# ---------------- J-03 y rótulos de TP ----------------
def circulo(c, r, n=24):
    s = k.SHAPE_POLY_SET(); s.NewOutline()
    for i in range(n):
        s.Append(int(c.x + r * math.cos(2 * math.pi * i / n)), int(c.y + r * math.sin(2 * math.pi * i / n)))
    return s


def obstaculos(capa):
    o = k.SHAPE_POLY_SET()
    mask = k.F_Mask if capa == FS else k.B_Mask
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(mask): o.Append(poly(p, mask, 0.15))
            if p.GetDrillSize().x > 0:
                h = k.SHAPE_POLY_SET(); p.TransformHoleToPolygon(h, MM(0.15), ERR, k.ERROR_OUTSIDE); o.Append(h)
    for t in b.GetTracks():
        if t.Type() == k.PCB_VIA_T:
            o.Append(circulo(t.GetPosition(), t.GetDrillValue() / 2 + MM(0.15)))
    for d in b.GetDrawings():
        if d.GetLayer() == k.Edge_Cuts: o.Append(poly(d, k.Edge_Cuts, 0.5))
    o.Simplify(); return o


def silk(capa, excluir):
    o = k.SHAPE_POLY_SET()
    for f in b.GetFootprints():
        for g in list(f.GraphicalItems()) + list(f.GetFields()):
            if g.GetLayer() == capa and g not in excluir and (not hasattr(g, 'IsVisible') or g.IsVisible()):
                o.Append(poly(g, capa, 0.10))
    for d in b.GetDrawings():
        if d.GetLayer() == capa and d not in excluir: o.Append(poly(d, capa, 0.10))
    o.Simplify(); return o


OBS = {FS: obstaculos(FS), BS: obstaculos(BS)}
PLACA = k.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(PLACA, True)
PLACA.Deflate(MM(BORDE), k.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)


def choca(t, capa, otros):
    s = poly(t, capa)
    fuera = k.SHAPE_POLY_SET(s); fuera.BooleanSubtract(PLACA)
    if fuera.OutlineCount(): return True
    for o in (OBS[capa], otros):
        i = k.SHAPE_POLY_SET(s); i.BooleanIntersection(o)
        if i.OutlineCount(): return True
    return False


def ubicar(t, capa, radio=None):
    radio = radio or RADIO
    """Busca la posición más cercana sin choques; devuelve el desplazamiento en mm o None."""
    otros = silk(capa, [t])
    if not choca(t, capa, otros): return 0.0
    p0, a0 = t.GetPosition(), t.GetTextAngleDegrees()
    for ang in (a0, a0 + 90):
        t.SetTextAngleDegrees(ang)
        r = 0.1
        while r <= radio + 1e-6:
            for i in range(max(8, int(2 * math.pi * r / 0.1))):
                th = 2 * math.pi * i / max(8, int(2 * math.pi * r / 0.1))
                t.SetPosition(k.VECTOR2I(int(p0.x + MM(r * math.cos(th))), int(p0.y + MM(r * math.sin(th)))))
                if not choca(t, capa, otros): return round(r, 2)
            r += 0.1
    t.SetPosition(p0); t.SetTextAngleDegrees(a0); return None


print('J-03')
textos = []
for f in b.GetFootprints():
    for fld in f.GetFields():
        if fld.IsVisible() and fld.GetLayer() in (FS, BS): textos.append((f.GetReference() + ':' + fld.GetName(), fld))
    for g in f.GraphicalItems():
        if g.Type() == k.PCB_TEXT_T and g.GetLayer() in (FS, BS) and g.IsVisible(): textos.append((f.GetReference() + ':txt', g))
for d in b.GetDrawings():
    if d.Type() == k.PCB_TEXT_T and d.GetLayer() in (FS, BS): textos.append(('placa:' + d.GetText(), d))
movidos, fallas = [], []
for nombre, t in textos:
    capa = t.GetLayer()
    if not choca(t, capa, k.SHAPE_POLY_SET()): continue                # solo los que pisan agujeros o aberturas
    if mm(t.GetTextSize().y) < 0.8: t.SetTextSize(P(0.8, 0.8))
    if mm(t.GetTextThickness()) < 0.15: t.SetTextThickness(MM(0.15))
    p0 = t.GetPosition()
    r = ubicar(t, capa)
    (fallas if r is None else movidos).append(nombre)
    print(f'  {nombre:40s} {"B" if capa == BS else "F"} ({mm(p0.x):.2f}, {mm(p0.y):.2f}) -> '
          + ('SIN LUGAR' if r is None else f'({mm(t.GetPosition().x):.2f}, {mm(t.GetPosition().y):.2f}) [{r} mm]'))

print('Rótulos TP')
ya = set()
for d in list(b.GetDrawings()):
    if d.Type() == k.PCB_TEXT_T and d.GetParentGroup() and d.GetParentGroup().GetName() == 'CLAUDE_RC6':
        if choca(d, BS, silk(BS, [d])): b.Remove(d)                     # rótulo de una pasada anterior que no entró
        else: ya.add(d.GetText())
for ref, nom in (('TP105', 'VS'), ('TP106', 'VA'), ('TP107', 'UVLO')):
    if nom in ya: continue
    f = b.FindFootprintByReference(ref); c = f.GetPosition()
    tx = k.PCB_TEXT(b); tx.SetText(nom); tx.SetLayer(BS); tx.SetTextSize(P(0.8, 0.8)); tx.SetTextThickness(MM(0.15))
    tx.SetMirrored(True); tx.SetPosition(k.VECTOR2I(c.x, c.y + MM(1.6)))
    b.Add(tx); grupo.AddItem(tx)
    r = ubicar(tx, BS, 3.0 if PASADA2 else 2.0)
    print(f'  {ref} «{nom}»', 'SIN LUGAR' if r is None else f'({mm(tx.GetPosition().x):.2f}, {mm(tx.GetPosition().y):.2f})')
    if r is None: b.Remove(tx)
    rt = f.Reference()
    if ubicar(rt, BS, 2.0) is None:
        rt.SetLayer(k.B_Fab); print(f'  {ref}: referencia a B.Fab')

print('movidos', len(movidos), 'sin lugar', fallas)
if not INFORME: b.Save(PCB)
