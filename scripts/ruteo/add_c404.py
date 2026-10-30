"""C404 autorizado: 100 nF/50 V X7R 0603, VBUS-GND en hoja 40.
Agrega una instancia de Device:C y copia la huella oficial existente de C402,
con UUID propios y path de simbolo para verificar paridad sin F8. Idempotente.
"""
from pathlib import Path
import re,uuid
ROOT=Path(__file__).resolve().parents[2]
assert not list(ROOT.glob('~*.lck')), 'Cerrar KiCad'
SCH=ROOT/'sheets/40_mcu_esp32s3.kicad_sch';PCB=ROOT/'INCLI-VA.kicad_pcb'
UID='768784e5-04bc-49ec-a241-330e74269057'
NOTE='Desacople VBUS del USBLC6-2SC6: 100 nF, X7R, 50 V, 0603; no alimenta el riel +5V. Agregado despues de placement-v1, autorizado en etapa 3.'
def blocks(s):
    depth=0;quoted=False;escaped=False;start=0
    for i,c in enumerate(s):
        if quoted:
            if escaped:escaped=False
            elif c=='\\':escaped=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c=='(':
            depth+=1
            if depth==2:start=i
        elif c==')':
            if depth==2:yield s[start:i+1]
            depth-=1

def shift(s,dx,dy):
    return re.sub(r'\(at ([\d.-]+) ([\d.-]+)',lambda m:f'(at {float(m[1])+dx:.4f} {float(m[2])+dy:.4f}',s)
def uuids(s):return re.sub(r'\(uuid "[^"]+"\)',lambda m:f'(uuid "{uuid.uuid4()}")',s)
s=SCH.read_text()
if '(property "Reference" "C404"' not in s:
    cap=next(x for x in blocks(s) if x.startswith('(symbol') and '(property "Reference" "C402"' in x)
    cap=uuids(shift(cap,185.42,-31.75)).replace('"C402"','"C404"')
    cap=re.sub(r'\(uuid "[^"]+"\)',f'(uuid "{UID}")',cap,count=1)
    cap=re.sub(r'\(property "Notes" "[^"]*"',f'(property "Notes" "{NOTE}"',cap)
    g=next(x for x in blocks(s) if x.startswith('(symbol') and '(property "Reference" "#PWR403"' in x)
    g=uuids(shift(g,185.42,-27.94)).replace('"#PWR403"','"#PWR416"')
    extra=[cap,g]
    for a,z in [((365.76,55.88),(365.76,59.69)),((365.76,67.31),(365.76,73.66))]:
        extra.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {z[0]} {z[1]})) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))')
    extra.append(f'(label "VBUS" (at 365.76 55.88 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uuid.uuid4()}"))')
    s=s.rstrip()[:-1]+'\n\t'+'\n\t'.join(extra)+'\n)\n';SCH.write_text(s)
s=PCB.read_text()
if '(property "Reference" "C404"' not in s:
    fp=next(x for x in blocks(s) if x.startswith('(footprint') and '(property "Reference" "C402"' in x)
    oldpath=re.search(r'\(path "([^"]+)"\)',fp)[1]
    fp=uuids(fp).replace('"C402"','"C404"')
    fp=re.sub(r'\(at [^)]+\)', '(at 189.8 81.45)',fp,count=1)
    fp=fp.replace(oldpath,oldpath.rsplit('/',1)[0]+'/'+UID)
    fp=re.sub(r'\(property "Notes" "[^"]*"',f'(property "Notes" "{NOTE}"',fp)
    fp=fp.replace('(net "+3V3_D")','(net "/40_mcu/VBUS")')
    s=s.rstrip()[:-1]+'\n\t'+fp+'\n)\n';PCB.write_text(s)
print('C404 agregado; ejecutar ERC, QA visual y paridad.')
