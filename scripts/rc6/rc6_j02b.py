#!/usr/bin/python3
"""rc6: segunda pasada de J-02 (tramos junto a aberturas de máscara), correr después de rc6_dfm.py.

Uso: /usr/bin/python3 -B scripts/rc6/rc6_j02b.py
rc6_dfm.py elige el lado del desplazamiento por el centro del pad, y eso falla en pads grandes (D102) o cuando el tramo
llega en diagonal. Acá, para cada tramo de F.Cu a < 0.11 mm de la abertura de un pad sin terminar dentro de su cobre
(medido con el contorno interior, el mismo criterio que el análisis de JLC), se prueba correrlo 0.02 mm hacia cada lado
de su normal y se sigue por el que aumenta la distancia, hasta 0.11 mm o 0.2 mm de recorrido. Los vértices
compartidos con otros tramos de la misma red se mueven con él. Excepción: D601.1 (ver rc6_dfm.py).
"""
import math
from pathlib import Path
import pcbnew as k

PCB = str(Path(__file__).resolve().parents[2] / 'INCLI-VA.kicad_pcb')
MM, mm, ERR = k.FromMM, k.ToMM, k.FromMM(0.005)
EXCLUIR = {'D601.1'}
b = k.LoadBoard(PCB)


def poly(it, capa):
    s = k.SHAPE_POLY_SET(); it.TransformShapeToPolygon(s, capa, 0, ERR, k.ERROR_INSIDE); return s


def dist(a, c):
    i = k.SHAPE_POLY_SET(a); i.BooleanIntersection(c)
    if i.OutlineCount(): return 0
    return min(min(math.sqrt(c.SquaredDistance(a.CVertex(j))) for j in range(a.FullPointCount())),
               min(math.sqrt(a.SquaredDistance(c.CVertex(j))) for j in range(c.FullPointCount())))


pads = [p for f in b.GetFootprints() for p in f.Pads() if p.IsOnLayer(k.F_Mask)]
for t in [t for t in b.GetTracks() if t.Type() == k.PCB_TRACE_T and t.GetLayer() == k.F_Cu]:
    for p in pads:
        nom = f'{p.GetParentFootprint().GetReference()}.{p.GetNumber()}'
        if nom in EXCLUIR or not t.GetBoundingBox().Inflate(MM(0.3)).Intersects(p.GetBoundingBox()): continue
        pc, pm = poly(p, k.F_Cu), poly(p, k.F_Mask)
        if pc.Contains(t.GetStart()) or pc.Contains(t.GetEnd()): continue
        d0 = dist(poly(t, k.F_Cu), pm)
        if d0 == 0 or d0 >= MM(0.11): continue
        a, z = (t.GetStart().x, t.GetStart().y), (t.GetEnd().x, t.GetEnd().y)
        n = math.hypot(z[0] - a[0], z[1] - a[1]); nx, ny = -(z[1] - a[1]) / n, (z[0] - a[0]) / n
        yo = t.m_Uuid.AsString()
        vecinos = [u for u in b.GetTracks() if u.Type() == k.PCB_TRACE_T and u.GetNetname() == t.GetNetname()
                   and u.GetLayer() == k.F_Cu and u.m_Uuid.AsString() != yo]

        uniones = [(u, lado, e) for e in (a, z) for u in vecinos for lado in ('ini', 'fin')
                   if ((u.GetStart() if lado == 'ini' else u.GetEnd()).x, (u.GetStart() if lado == 'ini' else u.GetEnd()).y) == e]

        def mover(dx, dy):
            for u, lado, e in uniones:
                q = k.VECTOR2I(int(e[0] + dx), int(e[1] + dy))
                u.SetStart(q) if lado == 'ini' else u.SetEnd(q)
            t.SetStart(k.VECTOR2I(int(a[0] + dx), int(a[1] + dy))); t.SetEnd(k.VECTOR2I(int(z[0] + dx), int(z[1] + dy)))

        mejor = None
        for s in (1, -1):
            for paso in range(1, 11):
                dx, dy = s * nx * MM(0.02 * paso), s * ny * MM(0.02 * paso)
                mover(dx, dy); d = dist(poly(t, k.F_Cu), pm); mover(0, 0)
                if d >= MM(0.11):
                    if not mejor or paso < mejor[0]: mejor = (paso, dx, dy, d)
                    break
        if mejor:
            mover(mejor[1], mejor[2])
            print(f'  {nom} {t.GetNetname()}: {mm(d0):.3f} -> {mm(mejor[3]):.3f} mm (se corre {0.02 * mejor[0]:.2f} mm)')
        else:
            print(f'  {nom} {t.GetNetname()}: {mm(d0):.3f} mm, sin solución en 0.2 mm')
        break
b.Save(PCB)
