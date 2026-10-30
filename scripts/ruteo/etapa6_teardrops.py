#!/usr/bin/python3
"""Etapa 6: habilita teardrops en todos los pads y vías y los genera rellenando zonas con kicad-cli.

Uso (KiCad cerrado, desde la carpeta del proyecto): /usr/bin/python3 -B scripts/ruteo/etapa6_teardrops.py [PCB]
Parámetros: los de cada pad/vía por defecto (KiCad 10) y "preferir conexión a zona", así que
los pads ya unidos a un plano no reciben teardrop. Idempotente: kicad-cli recrea las zonas teardrop.
"""
import subprocess, sys
import pcbnew as k

pcb = sys.argv[1] if len(sys.argv) > 1 else 'INCLI-VA.kicad_pcb'
b = k.LoadBoard(pcb)
n = 0
for f in b.GetFootprints():
    for p in f.Pads():
        p.SetTeardropsEnabled(True); n += 1
for t in b.GetTracks():
    if t.Type() == k.PCB_VIA_T:
        t.SetTeardropsEnabled(True); n += 1
b.Save(pcb)
print(f'teardrops habilitados en {n} pads/vías')
# El relleno de zonas de kicad-cli regenera los teardrops y guarda la placa.
subprocess.run(['kicad-cli', 'pcb', 'drc', '--refill-zones', '--save-board', '--format', 'json',
                '-o', '/dev/null', pcb], check=True)
print('zonas teardrop:', sum(1 for z in k.LoadBoard(pcb).Zones() if z.IsTeardropArea()))
