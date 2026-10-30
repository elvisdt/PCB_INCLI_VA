#!/usr/bin/python3
"""Consolidación de pasivos flexibles (aprobada por el usuario el 2026-10-30; análisis en docs/BOM_SOURCING.md).

Uso (KiCad cerrado, desde la carpeta del proyecto): /usr/bin/python3 -B scripts/bom/consolidar_pasivos.py
Cambia solo valor y campos (MPN/Manufacturer/LCSC y sus *_PROTO, Notes); la huella no cambia. Edita los símbolos
del esquemático (agrega los campos *_PROTO que falten, ocultos) y copia los mismos campos a las huellas del PCB.
Idempotente.
  1. R702/R752 (gate en serie de Q701/Q751, hoja 70 instanciada dos veces): 4k7 -> 2.2k, el mismo MPN que R803/R804.
  2. 100 nF 0603 (los 23): un solo MPN de 100 V X7R. PROD Murata GCM188R72A104KA64D (AEC-Q200); PROTO FH 0603B104K101NT.
  3. 1 uF 0603 (C306, C307, C403): PROTO Yageo CC0603KRX7R9BB105 (50 V X7R); PROD sin cambio.
  4. 10 uF 0805 (C301, C508, C603, C605, C606): PROTO Samsung CL21B106KAYQNNE (25 V X7R); PROD sin cambio.
"""
import glob, re
import pcbnew as k

PCB = 'INCLI-VA.kicad_pcb'
NOTA = 'PROTO (2026-10-30, consolidacion): '
REGLAS = [  # (condición sobre las propiedades del símbolo, campos nuevos, nota PROTO)
    (lambda p, refs: refs & {'R702', 'R752'},
     {'Value': '2.2k', 'MPN': 'AC0603FR-072K2L', 'Manufacturer': 'Yageo', 'LCSC': 'C125931',
      'MPN_PROTO': '0603WAF2201T5E', 'Manufacturer_PROTO': 'UNI-ROYAL', 'LCSC_PROTO': 'C4190'},
     'Gate en serie desde el 74AHCT1G126 (5 V): 2.2k, el mismo valor que R803/R804 (una linea de BOM). Con el '
     'pull-down de 100k, Vgs = 4.89 V (antes 4.78 V con 4k7); pico de carga 2.3 mA (el buffer da 8 mA). '
     + NOTA + 'UNI-ROYAL 0603WAF2201T5E (LCSC C4190), sin AEC-Q200.'),
    (lambda p, refs: p.get('Value') == '100nF' and 'C_0603' in p.get('Footprint', ''),
     {'MPN': 'GCM188R72A104KA64D', 'Manufacturer': 'Murata', 'LCSC': 'C415406',
      'MPN_PROTO': '0603B104K101NT', 'Manufacturer_PROTO': 'FH', 'LCSC_PROTO': 'C88219'},
     NOTA + 'un solo MPN para los 100 nF 0603: 100 V X7R (FH 0603B104K101NT, LCSC C88219), sin AEC-Q200. '
     'PROD: Murata GCM188R72A104KA64D (100 V, AEC-Q200). Mismo valor y tolerancia.'),
    (lambda p, refs: p.get('Value') == '1uF' and 'C_0603' in p.get('Footprint', ''),
     {'MPN_PROTO': 'CC0603KRX7R9BB105', 'Manufacturer_PROTO': 'Yageo', 'LCSC_PROTO': 'C559769'},
     NOTA + 'Yageo CC0603KRX7R9BB105 (50 V X7R, LCSC C559769), sin AEC-Q200: mas stock y menos perdida por DC bias.'),
    (lambda p, refs: p.get('Value') == '10uF' and 'C_0805' in p.get('Footprint', ''),
     {'MPN_PROTO': 'CL21B106KAYQNNE', 'Manufacturer_PROTO': 'Samsung', 'LCSC_PROTO': 'C3039694'},
     NOTA + 'Samsung CL21B106KAYQNNE (25 V X7R, LCSC C3039694), sin AEC-Q200: el original no tiene stock en lcsc.com.'),
]
PROP = '''		(property "{k}" "{v}"
			(at {x} {y} 0)
			(hide yes)
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
'''


def nota_nueva(vieja, nota):
    base = re.split(r' ?PROTO \(2026-10-30', vieja)[0].rstrip()
    if nota.startswith(NOTA):
        return (base + ' ' + nota).strip()
    return nota                                    # R702/R752: la nota se reescribe entera


cambios = {}                                       # referencia -> campos finales
for F in sorted(glob.glob('sheets/*.kicad_sch')):
    if 'kw45' in F: continue
    s = open(F).read()

    def editar(m):
        blk = m.group(0)
        refs = set(re.findall(r'\(reference "([^"]+)"\)', blk))
        props = dict(re.findall(r'\(property "([^"]+)" "([^"]*)"', blk))
        for cond, campos, nota in REGLAS:
            if not cond(props, refs): continue
            x, y = re.search(r'\n\t\t\(at (-?[\d.]+) (-?[\d.]+)', blk).groups()
            fin = dict(campos); fin['Notes'] = nota_nueva(props.get('Notes', ''), nota)
            for kk, v in fin.items():
                v = v.replace('"', "'")
                if kk in props:
                    blk = re.sub(r'(\(property "%s" )"[^"]*"' % re.escape(kk), lambda mm: mm.group(1) + '"%s"' % v, blk, count=1)
                else:
                    i = blk.index('\t\t(pin ') if '\t\t(pin ' in blk else blk.index('\t\t(instances')
                    blk = blk[:i] + PROP.format(k=kk, v=v, x=x, y=y) + blk[i:]
            for r in refs: cambios[r] = fin
            break
        return blk

    s2 = re.sub(r'\n\t\(symbol\n.*?\n\t\)(?=\n)', editar, s, flags=re.S)
    if s2 != s: open(F, 'w').write(s2)

b = k.LoadBoard(PCB)
for ref, campos in sorted(cambios.items()):
    f = b.FindFootprintByReference(ref)
    for kk, v in campos.items():
        v = v.replace('"', "'")
        if kk == 'Value': f.SetValue(v); continue
        fld = f.GetField(kk)
        if fld is None:
            fld = k.PCB_FIELD(f, k.FIELD_T_USER, kk); fld.SetLayer(k.F_Fab); fld.SetVisible(False); f.Add(fld)
        fld.SetText(v)
b.Save(PCB)
print(len(cambios), 'referencias:', ' '.join(sorted(cambios, key=lambda r: (r[0], int(r[1:])))))
