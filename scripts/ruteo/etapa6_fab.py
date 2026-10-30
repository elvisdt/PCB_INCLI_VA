#!/usr/bin/python3
"""Etapa 6: fabricación de prueba (JLCPCB) del prototipo CAN + DO + ROT en fab/proto/.

Uso (desde la carpeta del proyecto): /usr/bin/python3 -B scripts/ruteo/etapa6_fab.py
No modifica el PCB ni el esquema: usa los rellenos guardados.
Variante de prototipo = atributo dnp de KiCad, que refleja el campo DNP (contiene PROTO => no se monta).
La única pieza CABIN (R807) es DNP, así que no hace falta filtrar por el campo Variant.

Salida:
  gerbers/      Cu, máscara, serigrafía, pasta, Edge.Cuts y drill (PTH/NPTH, mapa en PDF)
  stencil/      solo F.Paste y B.Paste, más Edge.Cuts para alinear
  INCLI-VA_gerbers.zip   lo que se sube a JLCPCB (no se versiona)
  bom_proto.csv          BOM completa del prototipo (compra), agrupada
  bom_jlc.csv, cpl_jlc.csv   lo que ensambla JLC: sin THT, sin U401 ni lo de MANO
  pos_kicad.csv          pick & place tal como lo exporta KiCad (referencia)

Pasta (gerbers/ y stencil/): sin aperturas en los pads de las piezas DNP. Se plotea desde una copia
temporal del PCB, fuera del proyecto, a la que se le quitan las capas de pasta de esos pads.
CPL JLC: rotación corregida por familia (tabla de JLCKicadTools, cpl_rotations_db.csv, más la regla
propia VQFN) y posición en el centro de los pads (no el origen de la huella). Confirmar en la vista
previa de JLC antes de pagar: las familias sin regla quedan en la rotación de KiCad.
"""
import csv, os, re, shutil, subprocess, tempfile, zipfile
from collections import OrderedDict
import pcbnew as k

PCB, SCH = 'INCLI-VA.kicad_pcb', 'INCLI-VA.kicad_sch'
OUT = 'fab/proto'
LAYERS = 'F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts'  # la pasta se reemplaza abajo (sin DNP)
MANO = {'U401', 'F101', 'Q101', 'Q102', 'L201', 'U503'}  # SMD a mano (además de todo lo THT). F101, Q101, Q102: originales de DigiKey/Mouser (sustitutos rechazados); L201, U503: sin stock en JLC. Ver docs/BOM_SOURCING.md
# Rotación JLC = rotación KiCad + corrección. Fuente: matthewlai/JLCKicadTools, cpl_rotations_db.csv
# (consultado 2026-10-30); solo las familias de esta placa. Primera coincidencia manda.
ROT = [(r'^SOT-23', -90), (r'^SOIC-', 270), (r'^TSSOP-', 270), (r'^CP_Elec_10x10', 180),
       (r'^(.*?_|V)?QFN-(16|20|24|28|40)(-|_|$)', 270),
       (r'^TI_RGE0024T_VQFN-24', 270)]   # propia: la regla QFN de la tabla no reconoce el prefijo "TI_..._V"


def cli(*a):
    subprocess.run(['kicad-cli', *a], check=True, stdout=subprocess.DEVNULL)


# Solo se borran las carpetas generadas: bom_jlc_lcsc.csv se mantiene a mano (docs/BOM_SOURCING.md); el resto se sobrescribe.
for d in ('gerbers', 'stencil'):
    shutil.rmtree(f'{OUT}/{d}', ignore_errors=True)
g, st = f'{OUT}/gerbers', f'{OUT}/stencil'
os.makedirs(g); os.makedirs(st)
cli('pcb', 'export', 'gerbers', '-o', g + '/', '--layers', LAYERS, '--subtract-soldermask', PCB)
cli('pcb', 'export', 'drill', '-o', g + '/', '--format', 'excellon', '--excellon-units', 'mm',
    '--excellon-separate-th', '--generate-map', '--map-format', 'pdf', PCB)

# Pasta sin DNP, desde una copia temporal fuera del proyecto (no toca INCLI-VA.kicad_pro). Sobrescribe los
# archivos de pasta del juego principal; su .gbrjob (que lista todas las capas) es el del PCB del proyecto.
b = k.LoadBoard(PCB)
sin_pasta = []
for f in b.GetFootprints():
    if not f.IsDNP(): continue
    for p in f.Pads():
        ls = p.GetLayerSet()
        if ls.Contains(k.F_Paste) or ls.Contains(k.B_Paste):
            ls.RemoveLayer(k.F_Paste); ls.RemoveLayer(k.B_Paste); p.SetLayerSet(ls)
    sin_pasta.append(f.GetReference())
tmp = tempfile.mkdtemp(prefix='incli_pasta_')
tpcb = os.path.join(tmp, 'pasta.kicad_pcb')
b.Save(tpcb)
# gerbers/: solo se reemplazan los archivos de pasta. stencil/: pasta + Edge.Cuts con su propio job.
for d, capas in ((g, 'F.Paste,B.Paste'), (st, 'F.Paste,B.Paste,Edge.Cuts')):
    cli('pcb', 'export', 'gerbers', '-o', d + '/', '--layers', capas, tpcb)
    for n in os.listdir(d):         # pasta-F_Paste.gtp -> INCLI-VA-F_Paste.gtp, como el resto del juego
        if not n.startswith('pasta-'): continue
        if n.endswith('.gbrjob') and d == g:
            os.remove(f'{d}/{n}'); continue
        dst = f'{d}/INCLI-VA-' + n[len('pasta-'):]
        if n.endswith('.gbrjob'):
            open(dst, 'w').write(open(f'{d}/{n}').read().replace('pasta-', 'INCLI-VA-')); os.remove(f'{d}/{n}')
        else:
            os.rename(f'{d}/{n}', dst)
shutil.rmtree(tmp)
with zipfile.ZipFile(f'{OUT}/INCLI-VA_gerbers.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for n in sorted(os.listdir(g)):
        if not n.endswith('.pdf'): z.write(f'{g}/{n}', n)

# BOM: una fila por referencia, luego se agrupa por valor, huella y MPN efectivo.
raw = f'{OUT}/.bom_raw.csv'
cli('sch', 'export', 'bom', '--exclude-dnp', '--group-by', '', '--ref-range-delimiter', '',
    '--fields', 'Reference,Value,Footprint,MPN,MPN_PROTO,Manufacturer,Variant,${EXCLUDE_FROM_BOM}',
    '--labels', 'Ref,Value,Footprint,MPN,MPN_PROTO,Manufacturer,Variant,Excl', '-o', raw, SCH)
filas = [r for r in csv.DictReader(open(raw)) if not r['Excl']]
os.remove(raw)
fps = {f.GetReference(): f for f in b.GetFootprints()}
# THT = algún taladro > 0.5 mm (pines, patas de blindaje); las vías térmicas de 0.2 mm de U101/U201 no cuentan.
tht = {r for r, f in fps.items()
       if any(p.GetAttribute() in (k.PAD_ATTRIB_PTH, k.PAD_ATTRIB_NPTH) and p.GetDrillSize().x > k.FromMM(0.5) for p in f.Pads())}
mano = (tht | MANO) & {r['Ref'] for r in filas}


def bom(nombre, refs):
    groups = OrderedDict()
    for r in filas:
        if r['Ref'] not in refs: continue
        key = (r['Value'], r['Footprint'].split(':')[-1], r['MPN_PROTO'] or r['MPN'], r['Manufacturer'])
        groups.setdefault(key, []).append(r['Ref'])
    with open(f'{OUT}/{nombre}', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Comment', 'Designator', 'Footprint', 'MPN', 'Manufacturer', 'Qty'])
        for (val, fp, mpn, mfr), rr in groups.items():
            w.writerow([val, ','.join(rr), fp, mpn, mfr, len(rr)])
    return len(groups)


refs_bom = {r['Ref'] for r in filas}
refs_jlc = refs_bom - mano
n_bom, n_jlc = bom('bom_proto.csv', refs_bom), bom('bom_jlc.csv', refs_jlc)

pos = f'{OUT}/pos_kicad.csv'
cli('pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'both', '--exclude-dnp', '-o', pos, PCB)
rot_aplicada, movidos = {}, {}
with open(f'{OUT}/cpl_jlc.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for r in csv.DictReader(open(pos)):
        ref = r['Ref']
        if ref not in refs_jlc: continue
        fp = fps[ref]; nombre = fp.GetFPID().GetLibItemName().wx_str()
        corr = next((c for pat, c in ROT if re.search(pat, nombre)), 0)
        if corr: rot_aplicada[nombre] = corr
        rot = (float(r['Rot']) + corr) % 360
        bb = k.BOX2I()
        for p in fp.Pads(): bb.Merge(p.GetBoundingBox())
        cx, cy = bb.Centre().x / 1e6, -bb.Centre().y / 1e6        # mismo sistema que pos (Y hacia arriba)
        if abs(cx - float(r['PosX'])) > .05 or abs(cy - float(r['PosY'])) > .05:
            movidos[ref] = round(((cx - float(r['PosX'])) ** 2 + (cy - float(r['PosY'])) ** 2) ** .5, 2)
        w.writerow([ref, f'{cx:.4f}mm', f'{cy:.4f}mm', 'Top' if r['Side'] == 'top' else 'Bottom', f'{rot:g}'])
print(f'BOM proto: {n_bom} líneas, {len(refs_bom)} piezas. JLC: {n_jlc} líneas, {len(refs_jlc)} piezas; '
      f'a mano: {sorted(mano)}')
print(f'pasta quitada (DNP): {sorted(sin_pasta)}')
print(f'rotaciones corregidas: {rot_aplicada}; posición al centro de pads: {movidos}')
