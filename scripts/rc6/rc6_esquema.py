#!/usr/bin/python3
"""rc6 (grupo A de docs/REVISION_EXTERNA.md + JLCDFM): cambios de esquemático aprobados por el usuario (2026-10-30).

Uso (KiCad cerrado, desde la carpeta del proyecto): /usr/bin/python3 -B scripts/rc6/rc6_esquema.py
Hoja 10_power_input:
  R-01  R1 de UVLO desde VBAT_F (TI SNOSDF6 fig. 8-1), no desde SW (= VA: la placa no arrancaba).
        R113 + R106 de 51 kΩ 1206 en serie (mismo MPN que R108/R112); R107 9.31k -> 9.53k (corte 6.44 V,
        subida 7.02 V); U101.3 (SW) con no-connect.
  R-02  D1 de la fig. 8-1 (VA -> VS) dentro de D104: BAS21 -> BAV23C (doble, cátodo común, SOT-23, misma
        huella), símbolo oficial Diode:BAV70 (mismo pinout: 1 A1, 2 A2, 3 K). A1 = R102/D103, A2 = VA, K = VS.
  R-26  TP105 (VS), TP106 (VA), TP107 (UVLO), cara inferior.
Otras hojas: Notes corregidas (C-3, C-7, C-8, C-9, C-10, C-11 y R-29 del informe externo).
Falla si algo ya está aplicado (no es idempotente: correr sobre el esquema de pcb-v1-rc5).
"""
import re, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
assert not list(ROOT.glob('**/~*.lck')), 'Cerrar KiCad'
H10 = ROOT / 'sheets/10_power_input.kicad_sch'


def bloques(s):
    """(inicio, fin) de los bloques de profundidad 2 (hijos directos de kicad_sch)."""
    depth = 0; q = False; e = False; st = 0
    for i, c in enumerate(s):
        if q:
            if e: e = False
            elif c == '\\': e = True
            elif c == '"': q = False
        elif c == '"': q = True
        elif c == '(':
            depth += 1
            if depth == 2: st = i
        elif c == ')':
            if depth == 2: yield st, i + 1
            depth -= 1


def fin(s, i):
    """Índice del paréntesis que cierra el que abre en s[i]."""
    depth = 0; q = False; e = False
    for j in range(i, len(s)):
        c = s[j]
        if q:
            if e: e = False
            elif c == '\\': e = True
            elif c == '"': q = False
        elif c == '"': q = True
        elif c == '(': depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0: return j
    raise ValueError(i)


def buscar(s, cabeza, *contiene):
    r = [(a, z) for a, z in bloques(s) if s[a:z].startswith(cabeza) and all(c in s[a:z] for c in contiene)]
    assert len(r) == 1, (cabeza, contiene, len(r))
    return r[0]


def simbolo(s, ref):
    return buscar(s, '(symbol\n', f'(property "Reference" "{ref}"')


def prop(t, nombre, valor):
    """Cambia el valor de una propiedad existente o la agrega (oculta) después de la última."""
    v = valor.replace('"', '\\"')
    if f'(property "{nombre}" ' in t:
        return re.sub(r'\(property "%s" "(?:[^"\\]|\\.)*"' % re.escape(nombre), lambda m: f'(property "{nombre}" "{v}"', t, count=1)
    at = re.search(r'\n\t\t\(at ([-\d.]+ [-\d.]+) ', t).group(1)
    nuevo = (f'\t\t(property "{nombre}" "{v}"\n\t\t\t(at {at} 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n'
             f'\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n')
    i = t.index('\t\t(pin "')
    return t[:i] + nuevo + t[i:]


def quitar_prop(t, nombre):
    return re.sub(r'\t\t\(property "%s" .*?\n\t\t\)\n' % re.escape(nombre), '', t, count=1, flags=re.S)


def mover(t, dx, dy):
    return re.sub(r'\(at ([-\d.]+) ([-\d.]+)', lambda m: f'(at {float(m[1]) + dx:g} {float(m[2]) + dy:g}', t)


def uuids(t):
    return re.sub(r'\(uuid "[^"]+"\)', lambda m: f'(uuid "{uuid.uuid4()}")', t)


def reemplazar(s, rango, nuevo):
    a, z = rango
    return s[:a] + nuevo + s[z:]


def wire(x1, y1, x2, y2):
    return (f'(wire\n\t\t(pts\n\t\t\t(xy {x1:g} {y1:g}) (xy {x2:g} {y2:g})\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n'
            f'\t\t\t(type default)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)')


def label(nombre, x, y, ang, just):
    return (f'(label "{nombre}"\n\t\t(at {x:g} {y:g} {ang})\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n'
            f'\t\t\t)\n\t\t\t(justify {just})\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)')


def junction(x, y):
    return f'(junction\n\t\t(at {x:g} {y:g})\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "{uuid.uuid4()}")\n\t)'


def agregar(s, items):
    i = s.rindex('\n\t(sheet_instances') if '\n\t(sheet_instances' in s else s.rstrip().rindex(')')
    return s[:i] + ''.join('\n\t' + it for it in items) + s[i:]


s = H10.read_text()
assert '"R113"' not in s, 'ya aplicado'
nuevos = []

# ---------------- R-01 ----------------
NOTA_R1 = ('R1 de UVLO (TI SNOSDF6 fig. 8-1, R1 a VBAT): R113 + R106 en serie desde VBAT_F (rc6, hallazgo R-01: antes '
           'salía de SW, que es VA, y el LM74930 no podía encender Q101). 1206 por tensión/potencia: ~93 V y 0.19 W cada '
           'una con load dump de 202 V. Cara inferior, junto a TP102. PROTO (2026-10-30): Yageo RC1206FR-0751KL '
           '(LCSC C114947, JLC extended), misma especificación, sin AEC-Q200.')
a, z = simbolo(s, 'R106'); t = s[a:z]
for k, v in (('Value', '51k'), ('Footprint', 'Resistor_SMD:R_1206_3216Metric'), ('MPN', 'AC1206FR-0751KL'),
             ('Manufacturer', 'Yageo'), ('LCSC', 'C144484'), ('MPN_PROTO', 'RC1206FR-0751KL'),
             ('LCSC_PROTO', 'C114947'), ('Notes', NOTA_R1)):
    t = prop(t, k, v)
t = quitar_prop(t, 'Manufacturer_PROTO')
s = reemplazar(s, (a, z), t)
r113 = uuids(mover(t, 0, -7.62)).replace('"R106"', '"R113"')
nuevos.append(r113)
s = reemplazar(s, buscar(s, '(label "SW"', '(at 113.03 129.54 90)'), '')
nuevos.append(label('VBAT_F', 113.03, 121.92, 90, 'left bottom'))

a, z = simbolo(s, 'R107'); t = s[a:z]
for k, v in (('Value', '9.53k'), ('MPN', 'AC0603FR-079K53L'), ('LCSC', 'C228113'),
             ('MPN_PROTO', '0603WAF9531T5E'), ('Manufacturer_PROTO', 'UNI-ROYAL'), ('LCSC_PROTO', 'C23127'),
             ('Notes', 'R2 de UVLO. Con R113 + R106 = 102 kΩ desde VBAT_F: corte 0.55 V x (102k + 9.53k) / 9.53k = '
                       '6.44 V, subida 0.6 V x 111.53k / 9.53k = 7.02 V (SNOSDF6 §6.5: VUVLOF 0.533-0.573 V, VUVLOR '
                       '0.585-0.63 V -> 6.24-6.71 V / 6.85-7.37 V). rc6: 9.31k -> 9.53k. PROTO (2026-10-30): UNI-ROYAL '
                       '0603WAF9531T5E (LCSC C23127), misma especificación, sin AEC-Q200.')):
    t = prop(t, k, v)
s = reemplazar(s, (a, z), t)

a, z = buscar(s, '(label "SW"', '(at 194.31 120.65 180)')
s = reemplazar(s, (a, z), f'(no_connect\n\t\t(at 194.31 120.65)\n\t\t(uuid "{uuid.uuid4()}")\n\t)')

# ---------------- R-02 ----------------
lib = Path('/usr/share/kicad/symbols/Diode.kicad_sym').read_text()
la, lz = next((a, z) for a, z in bloques(lib) if lib[a:z].startswith('(symbol "BAV70"'))
bav70 = lib[la:lz].replace('(symbol "BAV70"', '(symbol "Diode:BAV70"', 1)
bav70 = '\n'.join('\t' + ln for ln in bav70.split('\n')).lstrip('\t')     # profundidad 3 dentro de lib_symbols
i = s.index('\n\t\t(symbol "Diode:BAS21"')
s = s[:i] + '\n\t\t' + bav70 + s[i:]

a, z = simbolo(s, 'D104'); t = s[a:z]
t = t.replace('(lib_id "Diode:BAS21")', '(lib_id "Diode:BAV70")').replace('(at 160.02 88.9 180)', '(at 161.29 83.82 0)', 1)
t = re.sub(r'(\(property "Reference" "D104"\n\t\t\t)\(at [^)]+\)', r'\1(at 170.18 82.55 0)', t)
t = re.sub(r'(\(property "Value" "BAS21"\n\t\t\t)\(at [^)]+\)', r'\1(at 176.53 82.55 0)', t)
t = re.sub(r'\(at 160.02 88.9 0\)', '(at 161.29 83.82 0)', t)
NOTA_D = ('D104 = BAV23C (doble, cátodo común): A1-K bloquea VS en polaridad inversa (como antes el BAS21) y A2-K es el D1 '
          'de TI SNOSDF6 fig. 8-1 (VA -> VS): con Q101 encendido VS = VA - VF, y HGATE-VA llega a ~11-13 V (rc6, hallazgo '
          'R-02: solo por R102 = 10 k, VS quedaba 6.7-7.8 V por debajo de VBAT y HGATE-VA en ~2.5-5.4 V). Nexperia BAV23C '
          'v.8 (2023-04): VR 200 V, VRRM 250 V, IF 225 mA; ve <= ~110 V en el pulso 1 y <= 63 V en el load dump. Símbolo '
          'oficial Diode:BAV70 (mismo pinout 1 A1, 2 A2, 3 K y huella SOT-23). Sin stock en lcsc.com (2026-10-30). '
          'PROTO (2026-10-30): Diodes Inc. BAV23C-7-F (LCSC C150732), DS30042 Rev. 23-2: mismo pinout, VRRM 250 V, '
          'VR 200 V, IFM 400 mA, sin AEC-Q101 (PROD automotriz: BAV23CQ de Diodes, a evaluar).')
for k, v in (('Value', 'BAV23C'), ('MPN', 'BAV23C,215'), ('Manufacturer', 'Nexperia'), ('LCSC', 'C282370'),
             ('Datasheet', 'https://assets.nexperia.com/documents/data-sheet/BAV23C.pdf'),
             ('MPN_PROTO', 'BAV23C-7-F'), ('Manufacturer_PROTO', 'Diodes Incorporated'), ('LCSC_PROTO', 'C150732'),
             ('Notes', NOTA_D)):
    t = prop(t, k, v)
s = reemplazar(s, (a, z), t)
if s.count('"Diode:BAS21"') == 1:                       # solo queda la definición de lib_symbols
    i = s.index('\n\t\t(symbol "Diode:BAS21"') + 1
    s = reemplazar(s, (i, fin(s, i + 2) + 1), '')
s = reemplazar(s, buscar(s, '(wire', '(xy 153.67 88.9) (xy 156.21 88.9)'), '')
s = reemplazar(s, buscar(s, '(wire', '(xy 163.83 88.9) (xy 168.91 88.9)'), '')
s = reemplazar(s, buscar(s, '(junction', '(at 153.67 88.9)'), '')
nuevos += [junction(153.67, 83.82), wire(161.29, 88.9, 168.91, 88.9), wire(168.91, 83.82, 168.91, 81.28),
           label('VA', 168.91, 81.28, 90, 'left bottom')]

# ---------------- R-26: TP105-TP107 ----------------
a, z = simbolo(s, 'TP102'); tp = s[a:z]
for i, (ref, red) in enumerate((('TP105', 'VS'), ('TP106', 'VA'), ('TP107', 'UVLO'))):
    t = uuids(mover(tp, 33.02 + 12.7 * i, 0)).replace('"TP102"', f'"{ref}"').replace('"VBAT_F"', f'"{red}"')
    t = prop(t, 'Notes', f'Punto de prueba de {red} (pad en la cara inferior, no va al BOM). rc6, hallazgo R-26: '
                         'bring-up de la protección de entrada (VS, VA, UVLO).')
    nuevos += [t, label(red, 242.57 + 12.7 * i, 166.37, 270, 'right bottom')]

s = agregar(s, nuevos)
H10.write_text(s)

# ---------------- Notes de otras hojas (C-3, C-7 ... C-11, R-29) ----------------
NOTAS = {
    'sheets/10_power_input.kicad_sch': {
        'C109': (r'Con C105 montado \(~1\.07 mF\): 0\.59 A < breaker 1 A',
                 'Con C105 montado (~1.07 mF): 0.59 A más la carga del buck durante la rampa (~0.15-0.25 A) contra el '
                 'breaker de 0.88-1.07 A (V(SNS_TH) 1.08-1.32 V): margen de ~0.1 A, ensayar en PROD (rev. B: 220-330 nF)'),
        'J2': (r'1777073, VERIFICAR en phoenixcontact\.com', '1777073, confirmado'),
    },
    'sheets/40_mcu_esp32s3.kicad_sch': {
        'TP403': (r'no alimenta la placa salvo con D401 \+ JP401', 'no alimenta la placa: D401 y JP401 se eliminaron'),
        'C401': (r'\(22 uF en C304 \+ 22 uF aquí \+ desacoples\)',
                 '(22 uF en C304 + 22 uF aquí + 10 uF de C605 en la hoja 60 + desacoples = ~54.6 uF nominal; con DC bias '
                 'probablemente < 47 uF: verificar el escalón 0.1 -> 0.6 A en el bring-up)'),
        'U401': (r'NO reemplazar por variantes con PSRAM octal \(R8\)\.',
                 'NO reemplazar por variantes con PSRAM octal (R8) ni con flash de 1.8 V (variantes «V»): IO47/IO48 '
                 '(CAN_TX/CAN_RX) están en el dominio VDD_SPI y quedarían a 1.8 V frente al VIO de 3.3 V del ADM3055E.'),
    },
    'sheets/30_regulation.kicad_sch': {
        'C304': (r'= ~44\.6 uF\.',
                 '= ~44.6 uF, más 10 uF de C605 (hoja 60) = ~54.6 uF nominal; con DC bias probablemente < 47 uF: '
                 'verificar el escalón 0.1 -> 0.6 A en el bring-up.'),
    },
    'sheets/70_output_ch.kicad_sch': {
        'R708': (r'el drenador llega a ~250 V; dos en serie, ~125 V cada una\.',
                 'Q701/Q751 son de 100 V y D701/D751 recortan a <= 93.6 V (lo de ~250 V venía del FDD7N25LZ); el 1206 '
                 'sigue dando margen.'),
        'R709': (r'el drenador llega a ~250 V; dos en serie, ~125 V cada una\.',
                 'Q701/Q751 son de 100 V y D701/D751 recortan a <= 93.6 V (lo de ~250 V venía del FDD7N25LZ); el 1206 '
                 'sigue dando margen.'),
        'D703': (r'limita DIAG a 3\.3 V para el GPIO del ESP32 \(antes 5V1 para el ISO7763\)\.',
                 'protege el GPIO del ESP32. Con ~30 uA (drenador a 12 V) el zener no fija 3.3 V y DIAG puede leer bajo '
                 'con la carga presente (hallazgo R-05): rediseñar en la rev. B.'),
    },
}
for hoja, cambios in NOTAS.items():
    p = ROOT / hoja; s = p.read_text()
    for ref, (viejo, nuevo) in cambios.items():
        a, z = simbolo(s, ref); t = s[a:z]
        t2 = re.sub(viejo, lambda m: nuevo, t, count=1)
        assert t2 != t, (hoja, ref)
        s = reemplazar(s, (a, z), t2)
    p.write_text(s)
print('esquema rc6 aplicado')
