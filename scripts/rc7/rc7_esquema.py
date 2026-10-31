#!/usr/bin/python3
"""rc7: JP601, puente de soldadura de la terminación CAN (abierto por defecto), en serie con R602. Hoja 60_can.

Uso (KiCad cerrado, desde la carpeta del proyecto, sobre el esquema de pcb-v1-rc6/459a6df):
    /usr/bin/python3 -B scripts/rc7/rc7_esquema.py
- Símbolo oficial Jumper:SolderJumper_2_Open, horizontal en (279.4, 101.6): pin 1 = BUS_CAN_H (la etiqueta
  jerárquica se corre de x 281.94 a 274.32), pin 2 = esquina del cable que baja a R602.1.
- Etiqueta local CAN_TERM_H en la esquina JP601.2-R602.1 (284.48, 101.6) (red /60_can/CAN_TERM_H).
- Fuera del BOM y de posiciones (no lleva componente; es cobre de la placa).
- Notes de JP601, R602, R603 y C609 y el bloque de texto de la hoja: la terminación se monta siempre y se
  activa con JP601.
"""
import re, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
assert not list(ROOT.glob('**/~*.lck')), 'Cerrar KiCad'
H60 = ROOT / 'sheets/60_can.kicad_sch'
s = H60.read_text()
assert 'JP601' not in s, 'ya aplicado'
U = lambda: str(uuid.uuid4())

NOTA = ('Selector de terminacion CAN (puente de soldadura, ABIERTO por defecto), en serie con R602, cara inferior. '
        'Abierto = sin terminacion. Unido con estano = terminacion partida de 120 ohm activa (nodo en el extremo del bus). '
        'Se configura en banco, antes de montar la placa en la caja. Sin componente: fuera del BOM y del CPL. '
        'Con JP601 abierto, CANL sigue viendo R603 + C609 a GND_CAN (carga de modo comun asimetrica, sin carga en DC).')


def reemplazar(viejo, nuevo, n=1):
    global s
    assert s.count(viejo) == n, (s.count(viejo), viejo[:80])
    s = s.replace(viejo, nuevo)


# ---------------- lib_symbols: Jumper:SolderJumper_2_Open ----------------
lib = Path('/usr/share/kicad/symbols/Jumper.kicad_sym').read_text()
i = lib.index('\t(symbol "SolderJumper_2_Open"')
depth = 0
for j in range(i, len(lib)):
    if lib[j] == '(': depth += 1
    elif lib[j] == ')':
        depth -= 1
        if depth == 0: break
sym = lib[i:j + 1].replace('(symbol "SolderJumper_2_Open"', '(symbol "Jumper:SolderJumper_2_Open"', 1)
sym = '\n'.join('\t' + l for l in sym.split('\n'))
reemplazar('\t(lib_symbols\n', '\t(lib_symbols\n' + sym + '\n')

# ---------------- cables y etiquetas ----------------
# Cable BUS_CAN_H (281.94 -> 284.48, y 101.6): lo reemplaza JP601 (pines en 274.32 y 284.48).
m = re.search(r'\t\(wire\s*\(pts\s*\(xy 284\.48 101\.6\)\s*\(xy 281\.94 101\.6\)\s*\)(?:(?!\t\(wire).)*?\n\t\)\n', s, re.S)
assert m, 'cable BUS_CAN_H -> R602'
s = s[:m.start()] + s[m.end():]
reemplazar('(hierarchical_label "BUS_CAN_H"\n\t\t(shape bidirectional)\n\t\t(at 281.94 101.6 180)',
           '(hierarchical_label "BUS_CAN_H"\n\t\t(shape bidirectional)\n\t\t(at 274.32 101.6 180)')

f = lambda txt, x, y, hide=True, ang=0: f'''		(property "{txt[0]}" "{txt[1]}"
			(at {x} {y} {ang})
			{'(hide yes)' if hide else ''}
			(show_name no)
			(do_not_autoplace no)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
'''
props = ''.join([
    f(('Reference', 'JP601'), 279.4, 99.06, False),
    f(('Value', 'TERM_CAN'), 279.4, 104.14, False),
    f(('Footprint', 'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'), 279.4, 101.6),
    f(('Datasheet', '~'), 279.4, 101.6),
    f(('Description', 'Solder Jumper, 2-pole, open'), 279.4, 101.6),
    f(('MPN', 'N/A (puente de soldadura en el PCB)'), 279.4, 101.6),
    f(('Manufacturer', 'N/A (cobre de la placa)'), 279.4, 101.6),
    f(('Notes', NOTA), 279.4, 101.6),
    f(('Variant', 'CAN'), 279.4, 101.6),
])
path = re.search(r'\(property "Reference" "R602".*?\(path "([^"]+)"', s, re.S).group(1)
simbolo = f'''	(symbol
		(lib_id "Jumper:SolderJumper_2_Open")
		(at 279.4 101.6 0)
		(unit 1)
		(body_style 1)
		(exclude_from_sim no)
		(in_bom no)
		(on_board yes)
		(in_pos_files no)
		(dnp no)
		(uuid "{U()}")
{props}		(pin "1"
			(uuid "{U()}")
		)
		(pin "2"
			(uuid "{U()}")
		)
		(instances
			(project "INCLI-VA"
				(path "{path}"
					(reference "JP601")
					(unit 1)
				)
			)
		)
	)
'''
label = f'''	(label "CAN_TERM_H"
		(at 284.48 101.6 0)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify left bottom)
		)
		(uuid "{U()}")
	)
	(text "JP601 TERM CAN (cara inferior): abierto = sin terminacion;\\nunido con estano = 120 ohm (nodo en el extremo del bus).\\nConfigurar en banco, antes de la caja."
		(exclude_from_sim no)
		(at 260.35 91.44 0)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify left bottom)
		)
		(uuid "{U()}")
	)
'''
k = s.index('\t(symbol\n\t\t(lib_id')          # antes del primer símbolo colocado
s = s[:k] + label + simbolo + s[k:]

# ---------------- Notes y bloque de texto ----------------
reemplazar('Terminacion partida 2 x 60.4 ohm + C609. Montar solo en nodos de extremo del bus (si el nodo no termina, R602/R603/C609 DNP).',
           'Terminacion partida 2 x 60.4 ohm + C609, siempre montada; se activa uniendo JP601 (en serie con R602). JP601 abierto = sin terminacion.',
           s.count('Terminacion partida 2 x 60.4 ohm + C609. Montar solo en nodos de extremo del bus (si el nodo no termina, R602/R603/C609 DNP).'))
reemplazar('"Terminacion partida 2 x 60.4 ohm + C609. Montar solo en nodos de extremo del bus."',
           '"Terminacion partida 2 x 60.4 ohm + C609, siempre montada; se activa uniendo JP601 (en serie con R602). JP601 abierto = sin terminacion."')
reemplazar('Terminacion partida R602 + R603 + C609: montar solo en nodos de extremo del bus.',
           'Terminacion partida R602 + R603 + C609 (siempre montada) con JP601 en serie con R602: abierto = sin terminacion,\\n  unido con estano = 120 ohm (nodo en el extremo del bus). JP601 en la cara inferior; se configura en banco, antes de la caja.')
H60.write_text(s)
print('JP601 agregado; path', path)
