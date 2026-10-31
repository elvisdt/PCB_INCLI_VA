#!/usr/bin/python3
"""rc6: costura GND_VEH junto a la pista UVLO nueva de B.Cu (R-01). Correr después de rc6_pcb.py con las zonas rellenas.

Uso: /usr/bin/python3 -B scripts/rc6/rc6_costura.py
Recorre cada tramo de la ruta cada 0.25 mm y, a cada lado, a 0.8-2.5 mm de la pista, pone una vía de 0.3/0.6 mm donde
el relleno GND_VEH de F.Cu y el de B.Cu la contengan con ≥ 0.35 mm de margen alrededor del anillo (así respeta las clearances de las
zonas), a ≥ 3 mm de la anterior del mismo lado y a ≥ 0.9 mm de cualquier otra vía. Donde F.Cu tiene cobre de otra
red (pad de C105, pista VA, pestaña de Q102) no hay vía posible: queda solo el plano B.Cu. Grupo CLAUDE_RC6.
"""
import math
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parents[2]
PCB = str(ROOT / 'INCLI-VA.kicad_pcb')
MM, mm = k.FromMM, k.ToMM
RUTA = [(115.94, 90.0), (111.0, 90.0), (111.0, 74.5), (118.9, 74.5)]
PASO, MIN_SEP, MARGEN = 0.25, 3.0, 0.35

b = k.LoadBoard(PCB)
grupo = next(g for g in b.Groups() if g.GetName() == 'CLAUDE_RC6')
rell = {}
for z in b.Zones():
    if z.GetNetname() == 'GND_VEH' and not z.IsTeardropArea() and not z.GetIsRuleArea():
        for L in (k.F_Cu, k.B_Cu):
            if z.IsOnLayer(L): rell[L] = z.GetFilledPolysList(L)
vias = [t.GetPosition() for t in b.GetTracks() if t.Type() == k.PCB_VIA_T]


def adentro(xy):
    p = k.VECTOR2I(MM(xy[0]), MM(xy[1]))
    c = k.SHAPE_POLY_SET(); c.NewOutline()
    for i in range(24):
        a = 2 * math.pi * i / 24
        c.Append(int(p.x + MM(0.3 + MARGEN) * math.cos(a)), int(p.y + MM(0.3 + MARGEN) * math.sin(a)))
    for L, s in rell.items():
        r = k.SHAPE_POLY_SET(c); r.BooleanSubtract(s)
        if r.OutlineCount(): return False
    return all((v - p).EuclideanNorm() >= MM(0.9) for v in vias)


nuevas = []
for (x0, y0), (x1, y1) in zip(RUTA, RUTA[1:]):
    largo = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / largo, (y1 - y0) / largo
    for lado in (1, -1):
        ultima = None
        for i in range(int(largo / PASO) + 1):
            cx, cy = x0 + ux * PASO * i, y0 + uy * PASO * i
            if ultima and math.hypot(cx - ultima[0], cy - ultima[1]) < MIN_SEP: continue
            for d in (0.8, 1.0, 1.3, 1.6, 2.0, 2.5):
                xy = (round(cx - uy * d * lado, 2), round(cy + ux * d * lado, 2))
                if adentro(xy):
                    v = k.PCB_VIA(b); v.SetPosition(k.VECTOR2I(MM(xy[0]), MM(xy[1]))); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3))
                    v.SetNet(b.FindNet('GND_VEH')); b.Add(v); grupo.AddItem(v)
                    vias.append(v.GetPosition()); nuevas.append(xy); ultima = (cx, cy)
                    break
b.Save(PCB)
print(len(nuevas), 'vías de costura nuevas:', nuevas)
