#!/usr/bin/python3
"""Etapa 6: puntos de prueba de la cara inferior (antes de rc5).

Uso (KiCad cerrado, desde la carpeta del proyecto): /usr/bin/python3 -B scripts/ruteo/etapa6_tp.py
1. TP406 y TP505: GND_VEH con agujero (TestPoint_THTPad_D2.5mm_Drill1.2mm) para el caimán del osciloscopio, en la
   cara inferior. Los símbolos están en las hojas 40_mcu y 50_sensors (con su GND_VEH); los campos se copian del
   esquemático para que la paridad dé 0. Fuera del BOM y de la posición.
   Posiciones (búsqueda en rejilla de 0.5 mm): pad libre en las dos caras con ≥ 0.35–0.5 mm a pistas de otras redes,
   pads y vías, ≥ 1 mm a courtyards, fuera del círculo del imán (Ø17.9 mm en U503), de las áreas de regla (APOYO_CAJA_B,
   BARRERA_CAN...), del keep-out de la antena de U401 y de las arandelas de H1–H5; sobre el plano GND_VEH inferior.
2. Rótulos en B.Silkscreen (0.8 mm, trazo 0.15 mm, en espejo: se leen desde abajo) con el nombre de la señal junto a
   cada TP; el script verifica la red de cada uno. Los GND llevan un recuadro. Primero se ubican los nombres (arriba,
   abajo, derecha o izquierda del pad, el primero libre) y después las referencias «TPxxx» en otro lado libre; si no
   entra, la referencia pasa a B.Fab (no se imprime).
3. Nota de medición del CAN en B.Silkscreen, encima de «CAN AISLADO»: el bus se mide contra GND_CAN (J1 pin 5),
   no contra GND_VEH. Posición elegida con una búsqueda en rejilla (≥ 0.3 mm de pads, vías y serigrafía).
4. Rellena las zonas con kicad-cli (regenera teardrops).
Grupo CLAUDE_ETAPA6_TP, idempotente.
"""
import re, subprocess
import pcbnew as k

PCB = 'INCLI-VA.kicad_pcb'
GRUPO = 'CLAUDE_ETAPA6_TP'
NUEVOS = {'TP406': ('sheets/40_mcu_esp32s3.kicad_sch', '/40_mcu/', (166.5, 131.0)),
          'TP505': ('sheets/50_sensors.kicad_sch', '/50_sensors/', (162.5, 86.5))}
FP_THT = ('/usr/share/kicad/footprints/TestPoint.pretty', 'TestPoint_THTPad_D2.5mm_Drill1.2mm')
NOMBRES = {'TP101': ('+VPROT', '+VPROT'), 'TP102': ('VBAT_F', '/10_power_input/VBAT_F'),
           'TP103': ('GND', 'GND_VEH'), 'TP104': ('FLT', '/PWR_FLT_N'), 'TP201': ('+5V', '+5V_VEH'),
           'TP301': ('+5V', '+5V_VEH'), 'TP302': ('3V3_D', '+3V3_D'), 'TP303': ('3V3_A', '+3V3_A'),
           'TP304': ('GND', 'GND_VEH'), 'TP305': ('PG_3V3D', '/30_regulation/PG_3V3D'),
           'TP401': ('EN', '/MCU_RST_N'), 'TP402': ('BOOT', '/40_mcu/BOOT'), 'TP403': ('VBUS', '/40_mcu/VBUS'),
           'TP404': ('CAN_TX', '/CAN_TX'), 'TP405': ('CAN_RX', '/CAN_RX'), 'TP406': ('GND', 'GND_VEH'),
           'TP501': ('SCK', '/SPI_SCK'), 'TP502': ('MOSI', '/SPI_MOSI'), 'TP503': ('MISO', '/SPI_MISO'),
           'TP504': ('INT1', '/IMU_INT1'), 'TP505': ('GND', 'GND_VEH')}
TXT, TRAZO, CAJA, MARGEN = 0.8, 0.15, 0.3, 0.15
REF_EN_FAB = {'TP406'}      # su «TPxxx» quedaba pegado a «TP303» y confundía; el recuadro GND ya lo identifica
CAMPOS = ('Datasheet', 'Description', 'MPN', 'Manufacturer', 'DNP', 'Notes')
MM, ERR = k.FromMM, k.FromMM(0.005)
P = lambda x, y: k.VECTOR2I(MM(x), MM(y))

b = k.LoadBoard(PCB)
for g in list(b.Groups()):
    if g.GetName() == GRUPO:
        for it in list(g.GetItems()): b.Delete(it)
        b.Delete(g)
grupo = k.PCB_GROUP(b); grupo.SetName(GRUPO); b.Add(grupo)
red_gnd = b.FindNet('GND_VEH')

# 1. TP406 / TP505
for ref, (sch, hoja, (x, y)) in NUEVOS.items():
    s = open(sch).read()
    blk = re.search(r'\t\(symbol\n\t\t\(lib_id "Connector:TestPoint"\)(?:(?!\n\t\)\n).)*?\(reference "%s"\)' % ref, s, re.S).group(0)
    props = dict(re.findall(r'\(property "([^"]+)" "([^"]*)"', blk))
    uuid = re.search(r'\n\t\t\(uuid "([^"]+)"\)', blk).group(1)
    ruta = re.search(r'\(path "/[^/"]+(/[^"]+)"', blk).group(1)
    f = b.FindFootprintByReference(ref)
    if f: b.Delete(f)
    f = k.FootprintLoad(*FP_THT)
    b.Add(f)
    f.SetReference(ref); f.SetValue(props['Value'])
    f.SetFPIDAsString(props['Footprint'])
    f.SetPath(k.KIID_PATH(ruta + '/' + uuid))
    f.SetSheetfile(sch); f.SetSheetname(hoja)
    f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
    for c in CAMPOS:
        fld = f.GetField(c)
        if fld is None:
            fld = k.PCB_FIELD(f, k.FIELD_T_USER, c); f.Add(fld)
        fld.SetText(props.get(c, '')); fld.SetLayer(k.F_Fab); fld.SetVisible(False)
    f.SetPosition(P(x, y))
    f.Flip(f.GetPosition(), k.FLIP_DIRECTION_LEFT_RIGHT)
    for p in f.Pads(): p.SetNet(red_gnd)
    f.Value().SetVisible(False)

tps = {f.GetReference(): f for f in b.GetFootprints() if f.GetReference() in NOMBRES}
assert len(tps) == len(NOMBRES), sorted(set(NOMBRES) - set(tps))
for ref, (_, red) in NOMBRES.items():
    assert [p.GetNetname() for p in tps[ref].Pads()] == [red], (ref, red)

# 2. Rótulos: obstáculos en B.Silkscreen (sin las referencias de los TP, que se reubican)
obs = k.SHAPE_POLY_SET()
def poly(it, capa, c):
    ps = k.SHAPE_POLY_SET(); it.TransformShapeToPolygon(ps, capa, MM(c), ERR, k.ERROR_OUTSIDE); return ps
for f in b.GetFootprints():
    for p in f.Pads():
        if p.IsOnLayer(k.B_Mask): obs.Append(poly(p, k.B_Mask, MARGEN + 0.1))
        elif p.GetAttribute() == k.PAD_ATTRIB_NPTH: obs.Append(poly(p, k.F_Cu, MARGEN + 0.1))
    texts = [f.Value()] + ([] if f.GetReference() in NOMBRES else [f.Reference()])
    for g in list(f.GraphicalItems()) + texts:
        if g.GetLayer() == k.B_SilkS and (not hasattr(g, 'IsVisible') or g.IsVisible()):
            obs.Append(poly(g, k.B_SilkS, MARGEN))
for t in b.GetTracks():
    if t.Type() == k.PCB_VIA_T: obs.Append(poly(t, k.B_Cu, MARGEN))
for d in b.GetDrawings():
    if d.GetLayer() == k.B_SilkS: obs.Append(poly(d, k.B_SilkS, MARGEN))
    elif d.GetLayer() == k.Edge_Cuts: obs.Append(poly(d, k.Edge_Cuts, 0.5))
    elif d.GetLayer() == k.Cmts_User and d.GetClass() == 'PCB_SHAPE' and d.GetParentGroup() \
            and d.GetParentGroup().GetName() == 'CLAUDE_RESERVA_HUNTER':
        obs.Append(poly(d, k.Cmts_User, 0.3))
        r = k.SHAPE_POLY_SET(); bb = d.GetBoundingBox(); r.NewOutline()
        for x, y in ((bb.GetX(), bb.GetY()), (bb.GetRight(), bb.GetY()), (bb.GetRight(), bb.GetBottom()), (bb.GetX(), bb.GetBottom())):
            r.Append(x, y)
        obs.Append(r)
obs.Simplify()


def texto(t, x, y, capa=k.B_SilkS):
    tx = k.PCB_TEXT(b); tx.SetText(t); tx.SetLayer(capa); tx.SetPosition(P(x, y))
    tx.SetTextSize(P(TXT, TXT)); tx.SetTextThickness(MM(TRAZO)); tx.SetMirrored(capa == k.B_SilkS)
    return tx


def medida(t):
    bb = texto(t, 0, 0).GetEffectiveShape().BBox()
    return bb.GetWidth() / 1e6, bb.GetHeight() / 1e6


def libre(ps):
    i = k.SHAPE_POLY_SET(obs); i.BooleanIntersection(ps); return i.OutlineCount() == 0


def caja(x, y, w, h, m):
    r = k.SHAPE_POLY_SET(); r.NewOutline()
    for cx, cy in ((x - w / 2 - m, y - h / 2 - m), (x + w / 2 + m, y - h / 2 - m), (x + w / 2 + m, y + h / 2 + m), (x - w / 2 - m, y + h / 2 + m)):
        r.Append(MM(cx), MM(cy))
    return r


def candidatos(f, w, h, extra):
    p = f.GetPosition(); x, y = p.x / 1e6, p.y / 1e6
    rp = max(pd.GetSize(k.B_Cu).x for pd in f.Pads()) / 2e6
    c = {}
    for paso in (0, 0.5, 1.0):         # pegado al pad y, si no entra, un poco más lejos
        dy, dx = rp + 0.35 + h / 2 + extra + paso, rp + 0.45 + w / 2 + extra + paso
        c.update({f'arriba+{paso}': (x, y - dy), f'abajo+{paso}': (x, y + dy),
                  f'derecha+{paso}': (x + dx, y), f'izquierda+{paso}': (x - dx, y)})
        for sx in (1, -1):             # en diagonal: el texto empieza a la altura del borde del pad
            for sy in (1, -1):
                c[f'diag{sx:+d}{sy:+d}+{paso}'] = (x + sx * (w / 2 + extra + 0.2), y + sy * dy)
    return c


lado_nombre, informe = {}, {}
for ref in sorted(NOMBRES):
    f, (nom, _) = tps[ref], NOMBRES[ref]
    w, h = medida(nom); extra = CAJA if nom == 'GND' else 0
    for lado, (x, y) in candidatos(f, w, h, extra).items():
        if libre(caja(x, y, w, h, extra)):
            t = texto(nom, x, y); b.Add(t); grupo.AddItem(t)
            obs.Append(caja(x, y, w, h, extra + MARGEN)); obs.Simplify()
            if nom == 'GND':
                r = k.PCB_SHAPE(b, k.SHAPE_T_RECT); r.SetLayer(k.B_SilkS); r.SetWidth(MM(TRAZO))
                r.SetStart(P(x - w / 2 - CAJA + 0.1, y - h / 2 - CAJA + 0.1)); r.SetEnd(P(x + w / 2 + CAJA - 0.1, y + h / 2 + CAJA - 0.1))
                b.Add(r); grupo.AddItem(r)
            lado_nombre[ref] = lado
            break
    else:
        raise SystemExit(f'{ref}: no hay lugar para «{nom}»')
for ref in sorted(NOMBRES):
    f = tps[ref]; rt = f.Reference()
    w, h = medida(ref)
    for lado, (x, y) in ([] if ref in REF_EN_FAB else candidatos(f, w, h, 0).items()):
        if lado.split('+')[0] != lado_nombre[ref].split('+')[0] and libre(caja(x, y, w, h, 0)):
            rt.SetLayer(k.B_SilkS); rt.SetVisible(True); rt.SetMirrored(True); rt.SetTextAngleDegrees(0)
            rt.SetTextSize(P(TXT, TXT)); rt.SetTextThickness(MM(TRAZO)); rt.SetPosition(P(x, y))
            obs.Append(caja(x, y, w, h, MARGEN)); obs.Simplify()
            informe[ref] = (NOMBRES[ref][0], lado_nombre[ref], lado)
            break
    else:
        rt.SetLayer(k.B_Fab); rt.SetMirrored(True)
        informe[ref] = (NOMBRES[ref][0], lado_nombre[ref], 'B.Fab')
nota = texto('CAN: medir vs GND_CAN (J1-5)', 118.0, 134.0)
assert libre(nota.GetEffectiveShape().BBox() and caja(118.0, 134.0, *medida('CAN: medir vs GND_CAN (J1-5)'), 0))
b.Add(nota); grupo.AddItem(nota)
b.Save(PCB)
for ref, (nom, ln, lr) in sorted(informe.items()):
    print(f'{ref:6} {nom:8} nombre {ln:9} ref {lr}')
subprocess.run(['kicad-cli', 'pcb', 'drc', '--refill-zones', '--save-board', '--format', 'json',
                '-o', '/dev/null', PCB], check=True, stdout=subprocess.DEVNULL)
print('zonas teardrop:', sum(1 for z in k.LoadBoard(PCB).Zones() if z.IsTeardropArea()))
