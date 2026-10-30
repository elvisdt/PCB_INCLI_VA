#!/usr/bin/python3
"""Etapa 6: rótulo «USB» junto a J401 (USB-C) en F.Silkscreen.

Uso (KiCad cerrado, desde la carpeta del proyecto): /usr/bin/python3 -B scripts/ruteo/etapa6_serigrafia_usb.py
Texto de 0.8 mm y trazo de 0.15 mm arriba a la izquierda de J401, fuera del rectángulo SIN BARNIZ de User.Comments
(192.15–199.82 × 74.78–86.27). Posición elegida con una búsqueda en rejilla de 0.25 mm: ≥ 0.25 mm de pads, vías,
serigrafía y de ese rectángulo. Grupo CLAUDE_ETAPA6_USB, idempotente.
"""
import pcbnew as k

PCB = 'INCLI-VA.kicad_pcb'
GRUPO = 'CLAUDE_ETAPA6_USB'
POS = (190.5, 75.4)

b = k.LoadBoard(PCB)
for g in list(b.Groups()):
    if g.GetName() == GRUPO:
        for it in list(g.GetItems()): b.Delete(it)
        b.Delete(g)
grupo = k.PCB_GROUP(b); grupo.SetName(GRUPO); b.Add(grupo)
t = k.PCB_TEXT(b); t.SetText('USB'); t.SetLayer(k.F_SilkS)
t.SetPosition(k.VECTOR2I(k.FromMM(POS[0]), k.FromMM(POS[1])))
t.SetTextSize(k.VECTOR2I(k.FromMM(0.8), k.FromMM(0.8))); t.SetTextThickness(k.FromMM(0.15))
b.Add(t); grupo.AddItem(t)
b.Save(PCB)
print(GRUPO, POS)
