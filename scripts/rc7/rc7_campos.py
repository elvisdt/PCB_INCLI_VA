#!/usr/bin/python3
"""rc7: copia al PCB los campos de las huellas desde la netlist del esquemático (parte de F8 que toca campos).
Idempotente. Uso (KiCad cerrado): /usr/bin/python3 -B scripts/rc7/rc7_campos.py
En rc7 cambian los Notes de R602 y R603 (terminación activada con JP601)."""
import subprocess, tempfile, xml.etree.ElementTree as ET
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parents[2]
assert not list(ROOT.glob('~*.lck')), 'Cerrar KiCad'
PCB = str(ROOT / 'INCLI-VA.kicad_pcb')
tmp = tempfile.mkdtemp(prefix='rc7_')
subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', tmp + '/n.xml',
                str(ROOT / 'INCLI-VA.kicad_sch')], check=True, stdout=subprocess.DEVNULL)
comps = {c.get('ref'): c for c in ET.parse(tmp + '/n.xml').getroot().iter('comp')}
b = k.LoadBoard(PCB)
cambios = []
for f in b.GetFootprints():
    c = comps.get(f.GetReference())
    if c is None or c.find('fields') is None: continue
    datos = {x.get('name'): (x.text or '') for x in c.find('fields')}
    for nombre, texto in datos.items():
        if nombre in ('Reference', 'Value', 'Footprint', 'Datasheet'): continue
        fld = f.GetField(nombre)
        if fld is not None and fld.GetText() != texto:
            fld.SetText(texto); cambios.append((f.GetReference(), nombre))
b.Save(PCB)
print('campos actualizados:', cambios)
