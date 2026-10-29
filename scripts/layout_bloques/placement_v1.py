"""Ultimas correcciones antes de placement-v1 (pedido del usuario, 2026-10-29).
1) Desacoples del ADM3055E (U601): ADI Rev. D, "PCB Layout": la pista entre el capacitor y VCC/VIO/VISOIN/VISOOUT
   no debe superar 2 mm. C601 (10 nF VIO) pasa a la fila del pin 4; C604 (100 nF VCC) a la del pin 3;
   C607 (10 nF VISOIN) al lugar de C608, el mas cercano al pin 16.
2) Buck: L201 0.6 mm hacia U201 (nodo SW mas corto) y C203 0.3 mm hacia el pin BOOT.
3) C105: huella Panasonic J16 (land antivibracion) en lugar de CP_Elec_16x17.5 (Vishay), misma posicion y giro.
4) Coating: zonas a enmascarar (J1, J2, J401, J402) en User.Comments y rotulo "SIN BARNIZ" en F.Silkscreen.
Uso: /usr/bin/python3 placement_v1.py <pcb_entrada> <pcb_salida>
Coordenadas absolutas de KiCad (mm)."""
import sys
import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
F = {f.GetReference(): f for f in b.GetFootprints()}
FMM = pcbnew.FromMM


def put(ref, x, y, rot):
    f = F[ref]
    f.SetOrientationDegrees(rot)
    f.SetPosition(pcbnew.VECTOR2I(FMM(x), FMM(y)))


# ------------------------------------------------------------------ 1-2: movimientos
# U601 (128.0, 119.0) r180: pin 4 VIO y = 120.91, pin 3 VCC y = 122.17, borde de pad x = 133.675.
# Las filas superiores a y 119.6 quedan libres para la salida de los pines 5-8 hacia el ESP32.
MOVES = {
    'C601': (136.00, 120.91, 0),     # VIO 10 nF: 1.1 mm de pad a pin 4
    'C602': (139.56, 120.91, 0),     # VIO 100 nF: segundo en la fila
    'C605': (143.33, 120.70, 0),     # VIO 10 uF: reserva local
    'C604': (136.00, 122.97, 0),     # VCC 100 nF: 1.1 mm en x y 0.8 mm en y al pin 3
    'C603': (139.78, 123.30, 0),     # VCC 10 uF
    'C607': (119.50, 119.00, 180),   # VISOIN 10 nF: fila del pin 16
    'C608': (119.50, 121.60, 180),   # VISOIN 100 nF
    'L201': (139.40, 56.10, 0),      # SW: pad 1 de L201 a ~2.8 mm del pin 8 (antes 3.4)
    'C203': (139.30, 62.42, 90),     # BOOT: 1.15 mm de pad a pin 7 (antes 1.45)
}
for r, (x, y, a) in MOVES.items():
    put(r, x, y, a)

# ------------------------------------------------------------------ 3: C105
old = F['C105']
lib = sys.argv[0].rsplit('/scripts/', 1)[0] + '/lib/INCLI-VA.pretty'
new = pcbnew.FootprintLoad(lib, 'CP_Elec_Panasonic_J16_VibProof')
new.SetFPID(pcbnew.LIB_ID('INCLI-VA', 'CP_Elec_Panasonic_J16_VibProof'))
new.SetParent(b)
new.SetPosition(old.GetPosition())
new.SetOrientation(old.GetOrientation())
new.SetPath(old.GetPath())
new.SetSheetname(old.GetSheetname())
new.SetSheetfile(old.GetSheetfile())
new.SetReference(old.GetReference())
new.SetValue(old.GetValue())
new.SetAttributes(old.GetAttributes())
new.SetDNP(old.IsDNP())
for fld in old.GetFields():
    if fld.GetName() in ('Reference', 'Value', 'Footprint'):
        continue
    nf = new.GetField(fld.GetName()) if new.HasField(fld.GetName()) else None
    if nf is None:
        nf = pcbnew.PCB_FIELD(new, new.GetNextFieldOrdinal(), fld.GetName())
        new.Add(nf)
    nf.SetText(fld.GetText())
    nf.SetVisible(False)
    nf.SetLayer(pcbnew.F_Fab)
for lyr, fld in ((pcbnew.F_SilkS, new.Reference()), (pcbnew.F_Fab, new.Value())):
    src = old.Reference() if fld.IsReference() else old.Value()
    fld.SetLayer(src.GetLayer())
    fld.SetPosition(src.GetPosition())
    fld.SetTextAngle(src.GetTextAngle())
    fld.SetTextSize(src.GetTextSize())
    fld.SetTextThickness(src.GetTextThickness())
    fld.SetVisible(src.IsVisible())
nets = {p.GetNumber(): p.GetNet() for p in old.Pads()}
for p in new.Pads():
    p.SetNet(nets[p.GetNumber()])
b.Remove(old)
b.Add(new)

# ------------------------------------------------------------------ 4: zonas sin barniz
# Caja = courtyard del conector + su pinout en serigrafia + 0.3 mm, en User.Comments (plano de
# enmascarado para el coating). En serigrafia no entra la caja completa sin pisar D102, Q701, Q751 y
# sus pads, asi que en F.Silkscreen va solo el rotulo "SIN BARNIZ" junto a cada conector.
BOXES = {   # x0, y0, x1, y1, rotulo (x, y, angulo)
    'J1': (100.25, 95.53, 112.73, 132.79, (100.90, 128.00, 90)),
    'J2': (164.45, 50.25, 186.48, 62.41, (163.90, 55.50, 90)),
    'J401': (192.22, 74.86, 199.75, 86.19, (191.30, 80.50, 90)),
    'J402': (178.01, 143.79, 187.31, 148.02, (182.66, 149.00, 0)),
}


def text(x, y, ang, layer):
    t = pcbnew.PCB_TEXT(b)
    t.SetText('SIN BARNIZ')
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(FMM(0.8), FMM(0.8)))
    t.SetTextThickness(FMM(0.15))
    t.SetPosition(pcbnew.VECTOR2I(FMM(x), FMM(y)))
    t.SetTextAngle(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T))
    b.Add(t)


for ref, (x0, y0, x1, y1, (lx, ly, la)) in BOXES.items():
    r = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_RECT)
    r.SetStart(pcbnew.VECTOR2I(FMM(x0), FMM(y0)))
    r.SetEnd(pcbnew.VECTOR2I(FMM(x1), FMM(y1)))
    r.SetLayer(pcbnew.Cmts_User)
    r.SetWidth(FMM(0.15))
    b.Add(r)
    text(lx, ly, la, pcbnew.F_SilkS)
    text((x0 + x1) / 2, (y0 + y1) / 2, 0, pcbnew.Cmts_User)

# ------------------------------------------------------------------ 5: referencias de los movidos
REF_AT = {'C604': (136.00, 124.30)}
for r, (x, y) in REF_AT.items():
    F[r].Reference().SetPosition(pcbnew.VECTOR2I(FMM(x), FMM(y)))

b.Save(sys.argv[2])
print('ok')
