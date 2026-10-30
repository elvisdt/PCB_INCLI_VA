#!/usr/bin/python3
"""Etapa 6: rótulos de J402 (UART0) en F.Silkscreen y B.Silkscreen.

Uso (KiCad cerrado, desde la carpeta del proyecto): /usr/bin/python3 -B scripts/ruteo/etapa6_serigrafia_j402.py
Rótulos desde el punto de vista del ESP32 (U401): pad 1 TX (/40_mcu/U0TXD, pin 37 TXD0), pad 2 RX (/40_mcu/U0RXD,
pin 36 RXD0), pad 3 GND (GND_VEH); el script verifica las redes antes de escribir. Texto de 0.8 mm y trazo de 0.15 mm
encima de cada pad, en las dos caras (THT), más «UART0 / 3V3» entre J402 y H4 (adaptador de 3.3 V, no 5 V).
La referencia J402 pasa a vertical a la izquierda del pin 1 para liberar la franja de arriba de los pads.
En B.Silkscreen se repite la marca de pin 1 en L de la huella. Grupo CLAUDE_ETAPA6_J402, idempotente.
"""
import pcbnew as k

PCB = 'INCLI-VA.kicad_pcb'
GRUPO = 'CLAUDE_ETAPA6_J402'
ROTULOS = {'1': ('TX', '/40_mcu/U0TXD'), '2': ('RX', '/40_mcu/U0RXD'), '3': ('GND', 'GND_VEH')}
Y_ROT = 143.8                      # centro de los rótulos: entre las vías GND de y = 143.0 y el contorno (144.46)
DX = {'1': -0.15}                 # TX se corre 0.15 mm a la izquierda: vía GND tapada en (181.0, 143.0)
X_INFO, Y_INFO = 188.9, (145.3, 146.5)
TXT, TRAZO = 0.8, 0.15

b = k.LoadBoard(PCB)
P = lambda x, y: k.VECTOR2I(k.FromMM(x), k.FromMM(y))
for g in list(b.Groups()):
    if g.GetName() == GRUPO:
        for it in list(g.GetItems()): b.Delete(it)
        b.Delete(g)
grupo = k.PCB_GROUP(b); grupo.SetName(GRUPO); b.Add(grupo)
f = b.FindFootprintByReference('J402')
pads = {p.GetNumber(): p for p in f.Pads()}
for n, (_, red) in ROTULOS.items():
    assert pads[n].GetNetname() == red, (n, pads[n].GetNetname(), red)


def texto(t, x, y, capa):
    tx = k.PCB_TEXT(b); tx.SetText(t); tx.SetPosition(P(x, y)); tx.SetLayer(capa)
    tx.SetTextSize(P(TXT, TXT)); tx.SetTextThickness(k.FromMM(TRAZO))
    tx.SetMirrored(capa == k.B_SilkS)
    b.Add(tx); grupo.AddItem(tx)


for capa in (k.F_SilkS, k.B_SilkS):
    for n, (t, _) in ROTULOS.items():
        texto(t, pads[n].GetPosition().x / 1e6 + DX.get(n, 0), Y_ROT, capa)
    for t, y in zip(('UART0', '3V3'), Y_INFO):
        texto(t, X_INFO, y, capa)
# Marca de pin 1 en la cara inferior: copia de la L de F.Silkscreen de la huella (esquina inferior izquierda del pad 1).
for g in f.GraphicalItems():
    if g.GetLayer() == k.F_SilkS and g.GetClass() == 'PCB_SHAPE':
        s, e = g.GetStart(), g.GetEnd()
        if max(s.x, e.x) <= pads['1'].GetPosition().x + k.FromMM(0.1):        # solo los dos tramos de la L
            l = k.PCB_SHAPE(b, k.SHAPE_T_SEGMENT); l.SetStart(s); l.SetEnd(e); l.SetWidth(g.GetWidth())
            l.SetLayer(k.B_SilkS); b.Add(l); grupo.AddItem(l)
# Referencia J402: vertical, a la izquierda del pin 1.
r = f.Reference(); r.SetPosition(P(177.6, 145.9)); r.SetTextAngleDegrees(90)
b.Save(PCB)
print(GRUPO, len(list(grupo.GetItems())), 'elementos')
