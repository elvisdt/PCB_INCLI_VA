#!/usr/bin/python3
"""rc6: pasa al PCB los cambios de esquemático de rc6_esquema.py (R-01, R-02, R-26) sin mover componentes.

Uso (KiCad cerrado, desde la carpeta del proyecto, sobre el PCB de pcb-v1-rc5): /usr/bin/python3 -B scripts/rc6/rc6_pcb.py
1. Sincronización tipo F8 desde la netlist del esquemático (kicadxml): campos de todas las huellas; R106 pasa de 0603
   (F.Cu) a 1206 en la cara inferior; R113, TP105, TP106 y TP107 nuevos (cara inferior); redes de D104.2 (VA) y U101.3
   (sin conexión). Footprints oficiales de /usr/share/kicad/footprints.
2. R-01: R113 (vertical, VBAT_F abajo, a TP102) y R106 (horizontal) debajo de Q101. La UVLO va por B.Cu por el borde
   norte del plano entre J1/D102 y Q101/Q102: y = 90.0 hacia el oeste, x = 111.0 hacia el norte (por fuera del DGATE),
   y = 74.5 hacia el este y una vía sobre la UVLO existente (118.9, 74.4). Se borran la pista de SW y el tramo que iba
   al pad del R106 viejo. Vías de costura GND_VEH a ambos lados de la pista nueva, cada ~4 mm donde haya lugar.
3. R-02: pista VA de 0.25 mm desde (129.28, 82.85) por x = 132.1 hasta D104.2.
4. R-26: TP105 VS (123.0, 83.25) sobre la pista VS de B.Cu; TP106 VA (118.3, 85.0) con tramo desde la vía (118.3, 82.6);
   TP107 UVLO (113.0, 90.0) sobre la pista nueva. Rótulos en B.Silkscreen (0.8 mm, trazo 0.15 mm, espejados).
Grupo CLAUDE_RC6. No rellena zonas (lo hace rc6_cierre.py).
"""
import re, subprocess, sys, tempfile, xml.etree.ElementTree as ET
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parents[2]
assert not list(ROOT.glob('**/~*.lck')), 'Cerrar KiCad'
PCB = str(ROOT / 'INCLI-VA.kicad_pcb')
FPLIB = '/usr/share/kicad/footprints/'
GRUPO = 'CLAUDE_RC6'
MM, ERR = k.FromMM, k.FromMM(0.005)
P = lambda x, y: k.VECTOR2I(MM(x), MM(y))
H = '/10_power_input/'
VBAT, UVLO, VA, VS, MID, SWNC = H + 'VBAT_F', H + 'UVLO', H + 'VA', H + 'VS', 'Net-(R106-Pad1)', 'unconnected-(U101-SW-Pad3)'

# ---------------- netlist ----------------
tmp = tempfile.mkdtemp(prefix='rc6_')
subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', tmp + '/n.xml',
                str(ROOT / 'INCLI-VA.kicad_sch')], check=True, stdout=subprocess.DEVNULL)
net = ET.parse(tmp + '/n.xml').getroot()
comps = {}
for c in net.iter('comp'):
    f = {x.get('name'): (x.text or '') for x in c.find('fields')} if c.find('fields') is not None else {}
    sp = c.find('sheetpath')
    comps[c.get('ref')] = dict(value=c.findtext('value'), footprint=c.findtext('footprint'), datasheet=c.findtext('datasheet') or '',
                               fields=f, path=sp.get('tstamps') + c.findtext('tstamps').split()[0],
                               sheetname=sp.get('names'))
pinnet = {}
for n in net.iter('net'):
    for nd in n.iter('node'):
        pinnet[(nd.get('ref'), nd.get('pin'))] = n.get('name')

b = k.LoadBoard(PCB)
assert not b.FindFootprintByReference('R113'), 'ya aplicado'
grupo = k.PCB_GROUP(b); grupo.SetName(GRUPO); b.Add(grupo)


def red(nombre):
    n = b.FindNet(nombre)
    if n is None:
        n = k.NETINFO_ITEM(b, nombre); b.Add(n)
    return n


def campos(f, ref):
    c = comps[ref]
    f.SetValue(c['value'])
    datos = dict(c['fields']); datos['Datasheet'] = c['datasheet']
    for nombre, texto in datos.items():
        if nombre in ('Reference', 'Value', 'Footprint'): continue
        fld = f.GetField(nombre)
        if fld is None:
            fld = k.PCB_FIELD(f, k.FIELD_T_USER, nombre); f.Add(fld)
            fld.SetLayer(k.B_Fab if f.IsFlipped() else k.F_Fab); fld.SetVisible(False)
        if fld.GetText() != texto: fld.SetText(texto)


def huella(ref, lib, nombre, xy, rot, abajo=True):
    c = comps[ref]
    vieja = b.FindFootprintByReference(ref)
    if vieja: b.Remove(vieja)
    f = k.FootprintLoad(FPLIB + lib + '.pretty', nombre)
    b.Add(f)
    f.SetReference(ref); f.SetFPIDAsString(c['footprint'])
    f.SetPath(k.KIID_PATH(c['path'])); f.SetSheetfile('sheets/10_power_input.kicad_sch'); f.SetSheetname(c['sheetname'])
    f.SetPosition(P(*xy))
    if abajo: f.Flip(f.GetPosition(), k.FLIP_DIRECTION_LEFT_RIGHT)
    f.SetOrientationDegrees(rot)
    for p in f.Pads(): p.SetNet(red(pinnet[(ref, p.GetNumber())]))
    campos(f, ref)
    rt = f.Reference(); rt.SetTextSize(P(0.8, 0.8)); rt.SetTextThickness(MM(0.15))
    f.Value().SetVisible(False)
    grupo.AddItem(f)
    return f


def pista(pts, w, capa, nombre):
    n = red(nombre)
    for a, z in zip(pts, pts[1:]):
        t = k.PCB_TRACK(b); t.SetStart(P(*a)); t.SetEnd(P(*z)); t.SetWidth(MM(w)); t.SetLayer(capa); t.SetNet(n)
        b.Add(t); grupo.AddItem(t)


def via(xy, nombre):
    v = k.PCB_VIA(b); v.SetPosition(P(*xy)); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3)); v.SetNet(red(nombre))
    v.SetLayerPair(k.F_Cu, k.B_Cu); b.Add(v); grupo.AddItem(v); return v


def borrar_pista(nombre, a, z):
    for t in list(b.GetTracks()):
        if t.Type() != k.PCB_TRACE_T or t.GetNetname() != nombre: continue
        s, e = (round(k.ToMM(t.GetStart().x), 2), round(k.ToMM(t.GetStart().y), 2)), (round(k.ToMM(t.GetEnd().x), 2), round(k.ToMM(t.GetEnd().y), 2))
        if {s, e} == {a, z}:
            b.Remove(t); return
    raise SystemExit(f'no encontré la pista {nombre} {a}-{z}')


# ---------------- 1. campos, redes ----------------
for f in b.GetFootprints():
    r = f.GetReference()
    if r in comps: campos(f, r)
b.FindFootprintByReference('D104').FindPadByNumber('2').SetNet(red(VA))
b.FindFootprintByReference('U101').FindPadByNumber('3').SetNet(red(SWNC))

# ---------------- 2. R-01 ----------------
borrar_pista(H + 'SW', (123.38, 73.75), (120.4, 73.75))
borrar_pista(UVLO, (118.9, 71.75), (120.4, 71.75))
r113 = huella('R113', 'Resistor_SMD', 'R_1206_3216Metric', (122.0, 92.4), 90)
if r113.FindPadByNumber('1').GetPosition().y < r113.GetPosition().y: r113.SetOrientationDegrees(270)
r106 = huella('R106', 'Resistor_SMD', 'R_1206_3216Metric', (117.4, 90.0), 0)
if r106.FindPadByNumber('1').GetPosition().x < r106.GetPosition().x: r106.SetOrientationDegrees(180)
pos = lambda f, n: (k.ToMM(f.FindPadByNumber(n).GetPosition().x), k.ToMM(f.FindPadByNumber(n).GetPosition().y))
p13v, p13m, p06m, p06u = pos(r113, '1'), pos(r113, '2'), pos(r106, '1'), pos(r106, '2')
pista([p13v, (122.0, 97.0)], 1.0, k.B_Cu, VBAT)                      # a TP102 (pad y vía VBAT_F)
pista([p06m, (p13m[0] - 1.0, p06m[1]), p13m], 0.3, k.B_Cu, MID)
RUTA = [p06u, (111.0, 90.0), (111.0, 74.5), (118.9, 74.5), (118.9, 74.4)]
pista(RUTA, 0.2, k.B_Cu, UVLO)
via((118.9, 74.4), UVLO)

# Costura GND_VEH a ambos lados de la pista nueva (cada ~4 mm donde haya lugar en F.Cu y B.Cu)
def libre_via(xy):
    v = k.PCB_VIA(b); v.SetPosition(P(*xy)); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3))
    for capa in (k.F_Cu, k.B_Cu):
        vs = k.SHAPE_POLY_SET(); v.TransformShapeToPolygon(vs, capa, 0, ERR, k.ERROR_OUTSIDE)
        for t in b.GetTracks():
            if not t.IsOnLayer(capa) or t.GetNetname() == 'GND_VEH': continue
            c = 1.3 if t.GetNetname() in (VBAT, H + 'VIN_VEH') else 0.65 if t.GetNetClassName() == 'PROT' else 0.3
            ts = k.SHAPE_POLY_SET(); t.TransformShapeToPolygon(ts, capa, MM(c), ERR, k.ERROR_OUTSIDE)
            ts.BooleanIntersection(vs)
            if ts.OutlineCount(): return False
        for f in b.GetFootprints():
            for p in f.Pads():
                if not p.IsOnLayer(capa) or p.GetNetname() == 'GND_VEH': continue
                if (p.GetPosition() - v.GetPosition()).EuclideanNorm() > MM(8): continue
                c = 1.3 if p.GetNetname() in (VBAT, H + 'VIN_VEH') else 0.65 if p.GetNetClassName() == 'PROT' else 0.3
                ps = k.SHAPE_POLY_SET(); p.TransformShapeToPolygon(ps, capa, MM(c), ERR, k.ERROR_OUTSIDE)
                ps.BooleanIntersection(vs)
                if ps.OutlineCount(): return False
    for t in b.GetTracks():                                           # no amontonar con vías GND existentes
        if t.Type() == k.PCB_VIA_T and (t.GetPosition() - v.GetPosition()).EuclideanNorm() < MM(1.2): return False
    return True


costura = []
for (x0, y0), (x1, y1) in zip(RUTA[:-2], RUTA[1:-1]):
    largo = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5; ux, uy = (x1 - x0) / largo, (y1 - y0) / largo
    n = max(1, round(largo / 4.0))
    for i in range(n + 1):
        cx, cy = x0 + ux * largo * i / n, y0 + uy * largo * i / n
        for lado in (1, -1):
            for d in (0.95, 1.3, 1.7):
                xy = (round(cx - uy * d * lado, 2), round(cy + ux * d * lado, 2))
                if libre_via(xy):
                    via(xy, 'GND_VEH'); costura.append(xy); break

# ---------------- 3. R-02 ----------------
d2 = pos(b.FindFootprintByReference('D104'), '2')
pista([(129.28, 82.85), (132.1, 82.85), (132.1, 86.6), d2], 0.25, k.F_Cu, VA)

# ---------------- 4. R-26: TP ----------------
TPS = {'TP105': ((123.0, 83.25), 'VS'), 'TP106': ((118.3, 85.0), 'VA'), 'TP107': ((113.0, 90.0), 'UVLO')}
for ref, (xy, _) in TPS.items():
    f = huella(ref, "TestPoint", "TestPoint_Pad_D1.5mm", xy, 0); f.SetExcludedFromBOM(True)
pista([(123.0, 83.25), (123.4, 83.25)], 0.25, k.B_Cu, VS)
pista([(118.3, 82.6), (118.3, 85.0)], 0.25, k.B_Cu, VA)

b.Save(PCB)
print('R113', p13v, p13m, 'R106', p06m, p06u)
print('costura', len(costura), costura)
