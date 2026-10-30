#!/usr/bin/python3
"""Etapa 6: sistema de ejes de la placa en F.Silkscreen (rc4).

Uso (KiCad cerrado, desde la carpeta del proyecto): /usr/bin/python3 -B scripts/ruteo/etapa6_ejes.py [X Y]
X Y: origen de las flechas en mm (por defecto 143.0, 87.5). Idempotente: rehace el grupo CLAUDE_ETAPA6_EJES.

Sistema de la placa (decisión del usuario, 2026-10-30): dextrógiro, mirando la cara superior +X a la derecha
(+x de KiCad), +Y hacia arriba (−y de KiCad) y +Z sale de la cara superior (⊙).
- U502 (ASM330LHH, ST DocID031239 Rev 4, fig. 1; F.Cu a 0°, pin 1 arriba a la izquierda): +X derecha, +Y arriba,
  +Z sale. X/Y/Z_placa = X/Y/Z_U502.
- U501 (SCL3300-D01, Murata Doc. 4921 Rev. 2, fig. 8, tabla 9 y fig. 10; F.Cu a 0°, pines 1–6 abajo): +X_U501
  hacia la fila 7–12 (arriba), +Y_U501 del pin 1 al 6 (derecha), +Z_U501 sale; triedro levógiro tal como lo dibuja
  Murata. X_placa = Y_U501, Y_placa = X_U501, Z_placa = Z_U501.
Transformaciones para firmware y prueba de 6 posiciones: docs/PENDIENTES.md.
"""
import sys
import pcbnew as k

PCB = 'INCLI-VA.kicad_pcb'
GRUPO = 'CLAUDE_ETAPA6_EJES'
L, PUNTA, ANCHO = 7.0, 1.0, 0.5      # largo de flecha, largo y semiancho de la punta (mm)
TRAZO, TEXTO = 0.15, 1.0
ox, oy = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (143.0, 87.5)

b = k.LoadBoard(PCB)
for g in list(b.Groups()):
    if g.GetName() == GRUPO:
        for it in list(g.GetItems()): b.Delete(it)
        b.Delete(g)
grupo = k.PCB_GROUP(b); grupo.SetName(GRUPO); b.Add(grupo)
P = lambda x, y: k.VECTOR2I(k.FromMM(x), k.FromMM(y))


def poner(it):
    it.SetLayer(k.F_SilkS); b.Add(it); grupo.AddItem(it)


def seg(x0, y0, x1, y1):
    s = k.PCB_SHAPE(b, k.SHAPE_T_SEGMENT); s.SetStart(P(x0, y0)); s.SetEnd(P(x1, y1)); s.SetWidth(k.FromMM(TRAZO))
    poner(s)


def flecha(dx, dy):                  # desde el origen, dirección unitaria (dx, dy) en coordenadas de KiCad
    ex, ey = ox + dx * L, oy + dy * L
    seg(ox, oy, ex, ey)
    bx, by = ex - dx * PUNTA, ey - dy * PUNTA
    seg(ex, ey, bx - dy * ANCHO, by + dx * ANCHO); seg(ex, ey, bx + dy * ANCHO, by - dx * ANCHO)


def texto(t, x, y):
    tx = k.PCB_TEXT(b); tx.SetText(t); tx.SetPosition(P(x, y))
    tx.SetTextSize(P(TEXTO, TEXTO)); tx.SetTextThickness(k.FromMM(TRAZO))
    poner(tx)


flecha(1, 0); texto('X', ox + L + 1.0, oy)             # +X: hacia la derecha
flecha(0, -1); texto('Y', ox, oy - L - 1.05)           # +Y: hacia arriba
cz = (ox + 1.8, oy - 1.8)                               # +Z: sale de la placa (⊙)
c = k.PCB_SHAPE(b, k.SHAPE_T_CIRCLE); c.SetCenter(P(*cz)); c.SetEnd(P(cz[0] + 0.6, cz[1]))
c.SetWidth(k.FromMM(TRAZO)); poner(c)
d = k.PCB_SHAPE(b, k.SHAPE_T_CIRCLE); d.SetCenter(P(*cz)); d.SetEnd(P(cz[0] + 0.2, cz[1]))
d.SetWidth(k.FromMM(TRAZO)); d.SetFilled(True); poner(d)
texto('Z', cz[0] + 1.4, cz[1])
b.Save(PCB)
print(f'{GRUPO}: origen ({ox}, {oy}), {len(list(grupo.GetItems()))} elementos')
