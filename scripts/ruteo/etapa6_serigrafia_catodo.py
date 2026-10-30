#!/usr/bin/python3
"""Etapa 6: «K» de cátodo en F.Silkscreen junto al pad 1 (cátodo) de los diodos SMx.

Uso (KiCad cerrado): /usr/bin/python3 -B scripts/ruteo/etapa6_serigrafia_catodo.py [PCB]
Texto de placa (no de la huella, para no generar lib_footprint_mismatch), 0.8 mm / 0.15 mm.
Busca la posición libre más cercana al pad 1, del lado del cátodo y fuera del cuerpo (F.Fab), rejilla de 0.1 mm, ≤ 3.5 mm.
Libre = a ≥ HOLG (forma real) de pads, de otra serigrafía y a 0.5 mm del borde. Grupo CLAUDE_ETAPA6_SILK:
se borra y se recrea (idempotente). Verificar después con el DRC (silk_*).
"""
import os, sys
import pcbnew as k

pcb = sys.argv[1] if len(sys.argv) > 1 else 'INCLI-VA.kicad_pcb'
DIODOS = ('D101', 'D102', 'D103', 'D701', 'D751')
GRUPO, H, TH, HOLG = 'CLAUDE_ETAPA6_SILK', 0.8, 0.15, 0.2
HOLG_TXT = 0.4                  # extra frente a otros textos: que la K no se lea como parte de un rótulo
iu = k.FromMM

b0 = k.LoadBoard(pcb)
viejos = [g for g in b0.Groups() if g.GetName() == GRUPO]
for g in viejos:
    for it in list(g.GetItems()): b0.Remove(it)
    b0.Remove(g)
if viejos:
    # Tras Remove, una segunda LoadBoard en el mismo proceso devuelve un objeto SWIG inválido:
    # se guarda sin el grupo y se relanza el script en un proceso nuevo.
    b0.Save(pcb)
    os.execv(sys.executable, [sys.executable, '-B'] + sys.argv)
b = b0

ERR = iu(0.005)
obst = k.SHAPE_POLY_SET()       # pads (cobre o máscara) y serigrafía F, por forma real
for f in b.GetFootprints():
    for p in f.Pads():
        for L in (k.F_Cu, k.F_Mask):
            if p.IsOnLayer(L): p.TransformShapeToPolygon(obst, L, 0, ERR, k.ERROR_OUTSIDE)
    for g in list(f.GraphicalItems()) + [f.Reference(), f.Value()]:
        if g.GetLayer() == k.F_SilkS and (g.Type() != k.PCB_FIELD_T or g.IsVisible()):
            es_texto = g.Type() in (k.PCB_FIELD_T, k.PCB_TEXT_T)
            g.TransformShapeToPolygon(obst, k.F_SilkS, iu(HOLG_TXT) if es_texto else 0, ERR, k.ERROR_OUTSIDE)
for d in b.GetDrawings():
    if d.GetLayer() == k.F_SilkS:
        d.TransformShapeToPolygon(obst, k.F_SilkS, iu(HOLG_TXT) if d.Type() == k.PCB_TEXT_T else 0, ERR, k.ERROR_OUTSIDE)
obst.Simplify()
borde = b.GetBoardEdgesBoundingBox()


def libre(t):
    bb = t.GetBoundingBox()
    if not (borde.GetLeft() + iu(0.5) < bb.GetLeft() and bb.GetRight() < borde.GetRight() - iu(0.5)
            and borde.GetTop() + iu(0.5) < bb.GetTop() and bb.GetBottom() < borde.GetBottom() - iu(0.5)):
        return False
    ps = k.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ps, k.F_SilkS, iu(HOLG), ERR, k.ERROR_OUTSIDE)
    ps.BooleanIntersection(obst)
    return ps.OutlineCount() == 0


g = k.PCB_GROUP(b); g.SetName(GRUPO); b.Add(g)
for ref in DIODOS:
    f = b.FindFootprintByReference(ref)
    pads = {p.GetNumber(): p for p in f.Pads()}
    c1, c2 = pads['1'].GetPosition(), pads['2'].GetPosition()
    x1, y1, x2, y2 = c1.x / 1e6, c1.y / 1e6, c2.x / 1e6, c2.y / 1e6
    ux, uy = x1 - x2, y1 - y2; n = (ux * ux + uy * uy) ** .5; ux, uy = ux / n, uy / n   # ánodo -> cátodo
    # Rejilla de 0.1 mm a ≤ 3.5 mm del centro del pad 1, del lado del cátodo y más cerca del pad 1
    # que del pad 2 (sin ambigüedad); se toma la más cercana al pad 1.
    cuerpo = k.BOX2I()                                                   # contorno F.Fab: la K debe verse con la pieza puesta
    for gi in f.GraphicalItems():
        if gi.GetLayer() == k.F_Fab and gi.Type() != k.PCB_TEXT_T: cuerpo.Merge(gi.GetBoundingBox())
    cands = []
    for i in range(-35, 36):
        for j in range(-35, 36):
            x, y = x1 + i / 10, y1 + j / 10
            d1 = ((x - x1) ** 2 + (y - y1) ** 2) ** .5; d2 = ((x - x2) ** 2 + (y - y2) ** 2) ** .5
            if d1 <= 3.5 and d1 < d2 - 1.0 and (x - (x1 + x2) / 2) * ux + (y - (y1 + y2) / 2) * uy > 0:
                cands.append((d1, x, y))
    for _, x, y in sorted(cands):
        t = k.PCB_TEXT(b); t.SetText('K'); t.SetLayer(k.F_SilkS)
        t.SetTextSize(k.VECTOR2I(iu(H), iu(H))); t.SetTextThickness(iu(TH))
        t.SetPosition(k.VECTOR2I(iu(x), iu(y)))
        tb = t.GetBoundingBox()
        if cuerpo.GetWidth() and cuerpo.Intersects(tb): continue
        if libre(t):
            b.Add(t); g.AddItem(t)
            t.TransformShapeToPolygon(obst, k.F_SilkS, iu(HOLG_TXT), ERR, k.ERROR_OUTSIDE)
            print(ref, 'K en', round(x, 2), round(y, 2), 'a', round(_, 2), 'mm del centro del cátodo')
            break
    else:
        print(ref, 'SIN LUGAR LIBRE')
b.Save(pcb)
