#!/usr/bin/python3
"""Etapa 6: fiduciales globales FID1–FID3 en F.Cu (equivale a F8 solo para ellos) y relleno de zonas.

Uso (KiCad cerrado, desde la carpeta del proyecto): /usr/bin/python3 -B scripts/ruteo/etapa6_fiduciales.py
Huella oficial Fiducial:Fiducial_1mm_Mask2mm (cobre 1 mm, abertura de máscara 2 mm). Sin red, fuera del BOM y de
los archivos de posición (JLC los toma de los Gerbers), referencia oculta y en F.Fab: sin serigrafía encima.
Los símbolos están en la hoja raíz; los campos se copian del esquemático para que la paridad dé 0.
Posiciones: tres esquinas no alineadas, a ≥ 5.4 mm del borde y ≥ 1.4 mm libres de cobre F.Cu, courtyards y
serigrafía alrededor de la abertura, fuera del keep-out de la antena de U401 (búsqueda en rejilla de 0.5 mm).
Idempotente: si ya existen, solo los recoloca. El relleno de zonas de kicad-cli regenera los teardrops.
"""
import re, subprocess
import pcbnew as k

PCB, SCH = 'INCLI-VA.kicad_pcb', 'INCLI-VA.kicad_sch'
POS = {'FID1': (112.0, 55.5), 'FID2': (124.0, 144.5), 'FID3': (189.0, 57.0)}
LIB = '/usr/share/kicad/footprints/Fiducial.pretty'
CAMPOS = ('Datasheet', 'Description', 'MPN', 'Manufacturer', 'DNP', 'Notes')

sch = open(SCH).read()
b = k.LoadBoard(PCB)
for ref, (x, y) in POS.items():
    m = re.search(r'\t\(symbol\n\t\t\(lib_id "Mechanical:Fiducial"\)(?:(?!\n\t\)\n).)*?\(reference "%s"\)' % ref, sch, re.S)
    blk = m.group(0)
    uuid = re.search(r'\n\t\t\(uuid "([^"]+)"\)', blk).group(1)
    props = dict(re.findall(r'\(property "([^"]+)" "([^"]*)"', blk))
    f = b.FindFootprintByReference(ref)
    if f is None:
        f = k.FootprintLoad(LIB, 'Fiducial_1mm_Mask2mm')
        b.Add(f)
    f.SetReference(ref); f.SetValue(props['Value'])
    f.SetPath(k.KIID_PATH('/' + uuid)); f.SetSheetname('/'); f.SetSheetfile(SCH)
    f.SetFPIDAsString(props['Footprint'])
    f.SetPosition(k.VECTOR2I(k.FromMM(x), k.FromMM(y)))
    f.SetBoardOnly(False); f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True)
    f.Reference().SetLayer(k.F_Fab); f.Reference().SetVisible(False)
    f.Value().SetVisible(False)
    for c in CAMPOS:
        fld = f.GetField(c)
        if fld is None:
            fld = k.PCB_FIELD(f, k.FIELD_T_USER, c); f.Add(fld)
        fld.SetText(props.get(c, '')); fld.SetLayer(k.F_Fab); fld.SetVisible(False)
    print(ref, x, y)
b.Save(PCB)
subprocess.run(['kicad-cli', 'pcb', 'drc', '--refill-zones', '--save-board', '--format', 'json',
                '-o', '/dev/null', PCB], check=True, stdout=subprocess.DEVNULL)
print('zonas teardrop:', sum(1 for z in k.LoadBoard(PCB).Zones() if z.IsTeardropArea()))
