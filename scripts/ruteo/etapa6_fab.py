#!/usr/bin/python3
"""Etapa 6: fabricación de prueba (JLCPCB) del prototipo CAN + DO + ROT en fab/proto/.

Uso (desde la carpeta del proyecto): /usr/bin/python3 -B scripts/ruteo/etapa6_fab.py
No modifica el PCB ni el esquema: usa los rellenos guardados.
Variante de prototipo = atributo dnp de KiCad, que refleja el campo DNP (contiene PROTO => no se monta).
La única pieza CABIN (R807) es DNP, así que no hace falta filtrar por el campo Variant.

Salida:
  gerbers/      Cu, máscara, serigrafía, pasta (= stencil), Edge.Cuts y drill (PTH/NPTH, mapa en PDF)
  stencil/      solo F.Paste y B.Paste, más Edge.Cuts para alinear
  INCLI-VA_gerbers.zip   lo que se sube a JLCPCB
  bom_proto.csv          BOM agrupada, formato JLC (Comment, Designator, Footprint) + MPN/fabricante
  cpl_proto.csv          pick & place, formato JLC (Designator, Mid X, Mid Y, Layer, Rotation)
  pos_kicad.csv          pick & place tal como lo exporta KiCad
"""
import csv, os, shutil, subprocess, zipfile
from collections import OrderedDict

PCB, SCH = 'INCLI-VA.kicad_pcb', 'INCLI-VA.kicad_sch'
OUT = 'fab/proto'
LAYERS = 'F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts'


def cli(*a):
    subprocess.run(['kicad-cli', *a], check=True, stdout=subprocess.DEVNULL)


shutil.rmtree(OUT, ignore_errors=True)
g, st = f'{OUT}/gerbers', f'{OUT}/stencil'
os.makedirs(g); os.makedirs(st)
cli('pcb', 'export', 'gerbers', '-o', g + '/', '--layers', LAYERS, '--subtract-soldermask', PCB)
cli('pcb', 'export', 'drill', '-o', g + '/', '--format', 'excellon', '--excellon-units', 'mm',
    '--excellon-separate-th', '--generate-map', '--map-format', 'pdf', PCB)
cli('pcb', 'export', 'gerbers', '-o', st + '/', '--layers', 'F.Paste,B.Paste,Edge.Cuts', PCB)
with zipfile.ZipFile(f'{OUT}/INCLI-VA_gerbers.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for n in sorted(os.listdir(g)):
        if not n.endswith('.pdf'): z.write(f'{g}/{n}', n)

# BOM: una fila por referencia, luego se agrupa por valor, huella y MPN efectivo.
raw = f'{OUT}/.bom_raw.csv'
cli('sch', 'export', 'bom', '--exclude-dnp', '--group-by', '', '--ref-range-delimiter', '',
    '--fields', 'Reference,Value,Footprint,MPN,MPN_PROTO,Manufacturer,Variant,${EXCLUDE_FROM_BOM}',
    '--labels', 'Ref,Value,Footprint,MPN,MPN_PROTO,Manufacturer,Variant,Excl', '-o', raw, SCH)
groups = OrderedDict()
for r in csv.DictReader(open(raw)):
    if r['Excl']: continue
    mpn = r['MPN_PROTO'] or r['MPN']
    k = (r['Value'], r['Footprint'].split(':')[-1], mpn, r['Manufacturer'])
    groups.setdefault(k, []).append(r['Ref'])
os.remove(raw)
refs_bom = {x for v in groups.values() for x in v}
with open(f'{OUT}/bom_proto.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Comment', 'Designator', 'Footprint', 'MPN', 'Manufacturer', 'Qty'])
    for (val, fp, mpn, mfr), refs in groups.items():
        w.writerow([val, ','.join(refs), fp, mpn, mfr, len(refs)])

# CPL: solo lo que está en la BOM (los test points y taladros no se montan).
pos = f'{OUT}/pos_kicad.csv'
cli('pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'both', '--exclude-dnp', '-o', pos, PCB)
n_cpl = 0
with open(f'{OUT}/cpl_proto.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for r in csv.DictReader(open(pos)):
        if r['Ref'] not in refs_bom: continue
        w.writerow([r['Ref'], r['PosX'] + 'mm', r['PosY'] + 'mm', 'Top' if r['Side'] == 'top' else 'Bottom', r['Rot']])
        n_cpl += 1
print(f'BOM: {len(groups)} líneas, {len(refs_bom)} piezas; CPL: {n_cpl}; sin posición: {sorted(refs_bom - set(r["Ref"] for r in csv.DictReader(open(pos))))}')
