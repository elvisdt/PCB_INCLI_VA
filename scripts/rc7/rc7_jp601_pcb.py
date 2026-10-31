#!/usr/bin/python3
"""rc7: JP601 (puente de soldadura de la terminación CAN, abierto) en la cara inferior, en serie con R602.

Uso: /usr/bin/python3 -B scripts/rc7/rc7_jp601_pcb.py [PCB] [--prueba]
  Sin --prueba: KiCad cerrado; toma ruta/campos de JP601 de la netlist del esquemático (sincronización tipo F8).
  Con --prueba: sobre una copia (render previo a la aprobación), sin netlist.
Geometría (sin mover componentes):
  - Se corta la pista CANH de F.Cu que llegaba a R602.1 desde (116.8, 123.5).
  - CANH: (116.8, 123.5) -> vía V1 (115.25, 123.5) -> B.Cu -> JP601 (pad este).
  - CAN_TERM_H: R602.1 (113.3, 122.325) -> (113.3, 122.9) -> vía V2 (114.3, 123.9) -> B.Cu -> JP601 (pad oeste).
  - JP601 SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm en B.Cu, centro (114.6, 125.3), pads horizontales.
  - «TERM CAN» en B.Silkscreen (0.8/0.15 mm, espejado) debajo de los pads; referencia JP601 en B.Fab.
Grupo CLAUDE_RC7. No rellena zonas.
"""
import subprocess, sys, tempfile, xml.etree.ElementTree as ET
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parents[2]
args = [a for a in sys.argv[1:] if not a.startswith('--')]
PRUEBA = '--prueba' in sys.argv
PCB = args[0] if args else str(ROOT / 'INCLI-VA.kicad_pcb')
if not PRUEBA:
    assert not list(ROOT.glob('~*.lck')), 'Cerrar KiCad'
MM = k.FromMM
P = lambda x, y: k.VECTOR2I(MM(x), MM(y))
CANH, TERM = '/BUS_CAN_H', '/60_can/CAN_TERM_H'
JPXY = (114.6, 125.3)
V1, V2 = (115.25, 123.5), (114.3, 123.9)   # V2 entre los rótulos de R602 y R603 (sin serigrafía sobre el agujero)

b = k.LoadBoard(PCB)
assert not b.FindFootprintByReference('JP601'), 'ya aplicado'
grupo = k.PCB_GROUP(b); grupo.SetName('CLAUDE_RC7'); b.Add(grupo)


def red(nombre):
    n = b.FindNet(nombre)
    if n is None:
        n = k.NETINFO_ITEM(b, nombre); b.Add(n)
    return n


def pista(pts, w, capa, nombre):
    for a, z in zip(pts, pts[1:]):
        t = k.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*z)); t.SetWidth(MM(w)); t.SetLayer(capa); t.SetNet(red(nombre))
        b.Add(t); grupo.AddItem(t)


def via(xy, nombre):
    v = k.PCB_VIA(b); v.SetPosition(P(*xy)); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3)); v.SetNet(red(nombre))
    v.SetLayerPair(k.F_Cu, k.B_Cu); b.Add(v); grupo.AddItem(v)


def borrar_pistas(nombre, tramos):
    """Borra en una sola pasada (borrar y volver a listar en el mismo script corrompe la lista de SWIG)."""
    cerca = lambda a, q: abs(a[0] - k.ToMM(q.x)) < 0.02 and abs(a[1] - k.ToMM(q.y)) < 0.02
    pend = list(tramos); quitar = []
    for t in b.GetTracks():
        if t.Type() != k.PCB_TRACE_T or t.GetNetname() != nombre: continue
        for a, z in pend:
            if (cerca(a, t.GetStart()) and cerca(z, t.GetEnd())) or (cerca(z, t.GetStart()) and cerca(a, t.GetEnd())):
                pend.remove((a, z)); quitar.append(t); break
    if pend: raise SystemExit(f'no encontré las pistas {nombre} {pend}')
    for t in quitar: b.Remove(t)


# ---------------- corte de CANH en R602.1 ----------------
r602 = b.FindFootprintByReference('R602')
r602.FindPadByNumber('1').SetNet(red(TERM))

# ---------------- JP601 ----------------
f = k.FootprintLoad('/usr/share/kicad/footprints/Jumper.pretty', 'SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm')
b.Add(f)
f.SetReference('JP601'); f.SetValue('TERM_CAN')
f.SetFPIDAsString('Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm')
f.SetPosition(P(*JPXY)); f.Flip(f.GetPosition(), k.FLIP_DIRECTION_LEFT_RIGHT); f.SetOrientationDegrees(0)
if not PRUEBA:
    tmp = tempfile.mkdtemp(prefix='rc7_')
    subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', tmp + '/n.xml',
                    str(ROOT / 'INCLI-VA.kicad_sch')], check=True, stdout=subprocess.DEVNULL)
    net = ET.parse(tmp + '/n.xml').getroot()
    c = next(c for c in net.iter('comp') if c.get('ref') == 'JP601')
    sp = c.find('sheetpath')
    f.SetPath(k.KIID_PATH(sp.get('tstamps') + c.findtext('tstamps').split()[0]))
    f.SetSheetfile('sheets/60_can.kicad_sch'); f.SetSheetname(sp.get('names'))
    f.SetValue(c.findtext('value'))
    datos = {x.get('name'): (x.text or '') for x in c.find('fields')}; datos['Datasheet'] = c.findtext('datasheet') or ''
    for nombre, texto in datos.items():
        if nombre in ('Reference', 'Value', 'Footprint'): continue
        fld = f.GetField(nombre)
        if fld is None:
            fld = k.PCB_FIELD(f, k.FIELD_T_USER, nombre); f.Add(fld); fld.SetLayer(k.B_Fab); fld.SetVisible(False)
        fld.SetText(texto)
    pinnet = {(nd.get('ref'), nd.get('pin')): n.get('name') for n in net.iter('net') for nd in n.iter('node')}
    assert pinnet[('R602', '1')] == TERM, pinnet[('R602', '1')]
    nets = {p.GetNumber(): pinnet[('JP601', p.GetNumber())] for p in f.Pads()}
else:
    nets = None
# pad oeste -> TERM (R602), pad este -> CANH
oeste, este = sorted(f.Pads(), key=lambda p: p.GetPosition().x)
if nets is None:
    oeste.SetNet(red(TERM)); este.SetNet(red(CANH))
else:
    # el esquema manda: el pad que lleva TERM queda al oeste (si no, se gira 180°)
    if nets[oeste.GetNumber()] != TERM:
        f.SetOrientationDegrees(180); oeste, este = este, oeste
    assert nets[oeste.GetNumber()] == TERM and nets[este.GetNumber()] == CANH, nets
    oeste.SetNet(red(TERM)); este.SetNet(red(CANH))
f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
f.Reference().SetLayer(k.B_Fab); f.Reference().SetTextSize(P(0.8, 0.8)); f.Reference().SetTextThickness(MM(0.15))
f.Reference().SetPosition(P(JPXY[0], JPXY[1] - 1.6))
f.Value().SetVisible(False)
grupo.AddItem(f)
po = (k.ToMM(oeste.GetPosition().x), k.ToMM(oeste.GetPosition().y))
pe = (k.ToMM(este.GetPosition().x), k.ToMM(este.GetPosition().y))

# ---------------- pistas y vías ----------------
pista([(116.8, 123.5), V1], 0.3, k.F_Cu, CANH)
via(V1, CANH)
pista([V1, (pe[0], pe[1])], 0.3, k.B_Cu, CANH)
pista([(113.3, 122.325), (113.3, 122.9), V2], 0.3, k.F_Cu, TERM)
via(V2, TERM)
pista([V2, po], 0.3, k.B_Cu, TERM)

# ---------------- rótulo ----------------
t = k.PCB_TEXT(b); t.SetText('TERM CAN'); t.SetLayer(k.B_SilkS)
t.SetTextSize(P(0.8, 0.8)); t.SetTextThickness(MM(0.15)); t.SetMirrored(True)
t.SetPosition(P(JPXY[0] + 1.1, JPXY[1] + 1.75))
b.Add(t); grupo.AddItem(t)

# Al final: después de b.Remove() los wrappers SWIG de la placa dejan de funcionar (KiCad 10 + Python 3.14).
borrar_pistas(CANH, [((116.8, 123.5), (114.0, 123.5)), ((114.0, 123.5), (113.3, 122.8)), ((113.3, 122.8), (113.3, 122.32))])
b.Save(PCB)
print('JP601', JPXY, 'oeste', po, 'este', pe)
