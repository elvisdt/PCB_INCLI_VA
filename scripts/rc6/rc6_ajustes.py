#!/usr/bin/python3
"""rc6: ajuste puntual de J-03 que no resuelve rc6_dfm.py (correr después de él).

Uso: /usr/bin/python3 -B scripts/rc6/rc6_ajustes.py
El rótulo «SIN BARNIZ» de (182.66, 149.0) no entra en otro lado (está dentro de su recuadro, junto al borde): se corre
la vía de costura GND_VEH sin pistas que tenía debajo, de (180.65, 148.8) a (180.65, 147.5).
El rótulo «VA» de TP106 quedaba pegado a la referencia R106 (se leía «VAR106»): pasa a la izquierda del pad, (116.5, 85.0).
Idempotente.
"""
from pathlib import Path
import pcbnew as k

PCB = str(Path(__file__).resolve().parents[2] / 'INCLI-VA.kicad_pcb')
MM, mm = k.FromMM, k.ToMM
b = k.LoadBoard(PCB)
v = [t for t in b.GetTracks() if t.Type() == k.PCB_VIA_T and abs(mm(t.GetPosition().x) - 180.65) < 0.01
     and abs(mm(t.GetPosition().y) - 148.8) < 0.01]
if v:
    assert len(v) == 1 and v[0].GetNetname() == 'GND_VEH'
    assert not [t for t in b.GetTracks() if t.Type() == k.PCB_TRACE_T and v[0].GetPosition() in (t.GetStart(), t.GetEnd())]
    v[0].SetPosition(k.VECTOR2I(MM(180.65), MM(147.5)))
    print('vía de costura movida a (180.65, 147.5)')
va = [d for d in b.GetDrawings() if d.Type() == k.PCB_TEXT_T and d.GetText() == 'VA' and d.GetLayer() == k.B_SilkS]
assert len(va) == 1
va[0].SetPosition(k.VECTOR2I(MM(116.5), MM(85.0)))
b.Save(PCB)
print('rótulo VA en (116.5, 85.0)')
