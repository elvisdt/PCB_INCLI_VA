#!/usr/bin/python3
"""Etapa 6: mide la ranura que abre en el plano B.Cu GND_VEH el haz de pistas bajo U401.

Uso: /usr/bin/python3 -B scripts/ruteo/verify_ranura_u401.py [PCB] > ranura.json
Usa los rellenos guardados. Rejilla de 0.1 mm en la ventana VENTANA.
Salida: extensión y ancho de la ranura, pistas F.Cu que la cruzan (con cobertura GND en F.Cu
encima del cruce), puentes F.Cu GND sobre la ranura, y la región B.Cu a la que llega el pad
central de U401.
"""
import json, sys
from collections import deque
import pcbnew as k

pcb = sys.argv[1] if len(sys.argv) > 1 else 'INCLI-VA.kicad_pcb'
b = k.LoadBoard(pcb)
F, B = k.F_Cu, k.B_Cu
NET = 'GND_VEH'
VENTANA = (168.0, 72.0, 200.0, 132.0)
SEMILLA = (177.0, 90.0)          # entre pistas del haz
G = 0.1
mm, iu = (lambda v: round(v / 1e6, 2)), k.FromMM

fills = {L: [z.GetFilledPolysList(L) for z in b.Zones()
             if not z.GetIsRuleArea() and z.GetNetname() == NET and z.IsOnLayer(L)] for L in (F, B)}
edge = k.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(edge, True)
x0, y0, x1, y1 = VENTANA
nx, ny = int((x1 - x0) / G) + 1, int((y1 - y0) / G) + 1


def lleno(L, x, y):
    p = k.VECTOR2I(iu(x), iu(y))
    return any(s.Contains(p) for s in fills[L])


def xy(i, j): return x0 + i * G, y0 + j * G


void = [[False] * nx for _ in range(ny)]
for j in range(ny):
    for i in range(nx):
        x, y = xy(i, j)
        void[j][i] = edge.Contains(k.VECTOR2I(iu(x), iu(y))) and not lleno(B, x, y)

# Ranura: en cada fila, el tramo continuo de vacío que contiene el haz (x = SEMILLA[0]).
# (Una componente conexa no sirve: los canales de holgura de todas las pistas B.Cu se tocan.)
si = round((SEMILLA[0] - x0) / G)
filas = {}
for j in range(ny):
    if not void[j][si]: continue
    a = c = si
    while a > 0 and void[j][a - 1]: a -= 1
    while c < nx - 1 and void[j][c + 1]: c += 1
    filas[j] = (a, c)
# Tramo vertical continuo que contiene la semilla
sj = round((SEMILLA[1] - y0) / G)
assert sj in filas, 'la semilla no cae en vacío B.Cu'
ja = jc = sj
while ja - 1 in filas: ja -= 1
while jc + 1 in filas: jc += 1
filas = {j: filas[j] for j in range(ja, jc + 1)}
comp = {(i, j) for j, (a, c) in filas.items() for i in range(a, c + 1)}
toca_ventana = any(i in (0, nx - 1) or j in (0, ny - 1) for i, j in comp)
filas = {j: list(v) for j, v in filas.items()}
anchos = {round(y0 + j * G, 1): round((max(v) - min(v) + 1) * G, 2) for j, v in sorted(filas.items())}
xs = [x0 + i * G for i, _ in comp]; ys = [y0 + j * G for _, j in comp]

# Puentes: filas de la ranura con GND F.Cu continuo de borde a borde de la ranura
puentes = []
for j, v in sorted(filas.items()):
    y = y0 + j * G
    if all(lleno(F, x0 + i * G, y) for i in range(min(v), max(v) + 1)): puentes.append(round(y, 1))

# Pistas F.Cu que cruzan la ranura
cruces = {}
for t in b.GetTracks():
    if t.Type() != k.PCB_TRACE_T or t.GetLayer() != F: continue
    s, e = t.GetStart(), t.GetEnd()
    L = ((e.x - s.x) ** 2 + (e.y - s.y) ** 2) ** .5 / 1e6
    n = max(2, int(L / (G / 2)))
    dentro = []
    for m in range(n + 1):
        x = (s.x + (e.x - s.x) * m / n) / 1e6; y = (s.y + (e.y - s.y) * m / n) / 1e6
        if (round((x - x0) / G), round((y - y0) / G)) in comp: dentro.append((x, y))
    if not dentro: continue
    c = cruces.setdefault(t.GetNetname(), {'largo_sobre_ranura_mm': 0.0, 'tramos': []})
    c['largo_sobre_ranura_mm'] = round(c['largo_sobre_ranura_mm'] + len(dentro) * L / (n + 1), 2)
    c['tramos'].append([mm(s.x), mm(s.y), mm(e.x), mm(e.y)])
for net, c in cruces.items():
    # GND F.Cu a ambos lados de la pista (0.5 mm del eje): retorno coplanar disponible
    lados = 0; tot = 0
    for x1_, y1_, x2_, y2_ in c['tramos']:
        dx, dy = x2_ - x1_, y2_ - y1_; L = (dx * dx + dy * dy) ** .5 or 1
        nxv, nyv = -dy / L * .5, dx / L * .5
        for m in range(11):
            x = x1_ + dx * m / 10; y = y1_ + dy * m / 10
            if (round((x - x0) / G), round((y - y0) / G)) not in comp: continue
            tot += 1; lados += lleno(F, x + nxv, y + nyv) and lleno(F, x - nxv, y - nyv)
    c['gnd_FCu_ambos_lados_frac'] = round(lados / tot, 2) if tot else None

# Pad central de U401: área de la región B.Cu GND a la que llegan sus vías
u = b.FindFootprintByReference('U401')
vias_ep = [p for p in u.Pads() if p.GetNumber() == '41' and p.IsOnLayer(B)]
reg = None
for s in fills[B]:
    for o in range(s.OutlineCount()):
        if any(s.Contains(p.GetPosition(), o) for p in vias_ep):
            a = s.Outline(o).Area() / 1e12
            for h in range(s.HoleCount(o)): a -= s.Hole(o, h).Area() / 1e12
            reg = max(reg or 0, round(a, 1))

print(json.dumps({
    'ranura': {'bbox_mm': [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)],
               'largo_mm': round(max(ys) - min(ys) + G, 1), 'area_mm2': round(len(comp) * G * G, 1),
               'ancho_max_mm': max(anchos.values()), 'ancho_mediano_mm': sorted(anchos.values())[len(anchos) // 2],
               'toca_borde_ventana': toca_ventana},
    'anchos_por_y_cada_2mm': {y: w for y, w in anchos.items() if round(y * 10) % 20 == 0},
    'bordes_por_y': {round(y0 + j * G, 1): (round(x0 + min(v) * G, 2), round(x0 + max(v) * G, 2)) for j, v in sorted(filas.items())},
    'puentes_FCu_gnd_filas': len(puentes), 'puentes_FCu_gnd_y': puentes[:: max(1, len(puentes) // 40)],
    'cruces_FCu': cruces,
    'pad_central_U401': {'vias_BCu': len(vias_ep), 'region_BCu_mm2': reg},
}, indent=1))
