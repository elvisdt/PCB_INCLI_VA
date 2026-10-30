#!/usr/bin/python3
"""BOM completa del prototipo para "Upload a BOM" de lcsc.com: bom/LCSC_BOM_COMPLETO_PROTO.csv.

Uso (desde la carpeta del proyecto): /usr/bin/python3 -B scripts/bom/lcsc_bom_completo.py [JUEGOS] [--solo-costo]
  JUEGOS: placas + 1 de repuesto (por defecto 6 = 5 + 1). --solo-costo: calcula el costo sin escribir el archivo.
Compra principal (desde 2026-10-30): JLC solo fabrica la PCB y el stencil; todo se compra en LCSC y se suelda a mano.
Entrada: bom/BOM_PROTO.csv (variante PROTO, ya sin DNP). Solo las líneas con código LCSC; lo de DigiKey/Mouser
queda en bom/DIGIKEY_MOUSER.csv.
Cantidad = piezas por placa × JUEGOS; en pasivos 0402/0603 (R, C, FB) al menos 20 por la
merma al soldar a mano; después se sube al pedido mínimo (minBuyNumber) y al múltiplo (split) de lcsc.com.
MOQ, múltiplo, descripción y stock se leen en vivo del endpoint público que usa lcsc.com (el mismo de
jlc_lookup.py de agentic-sourcing, solo consulta). Las líneas con stock de lcsc.com menor a la cantidad se avisan.
"""
import csv, json, math, sys, time, urllib.request

args = [a for a in sys.argv[1:] if not a.startswith('--')]
PLACAS = int(args[0]) if args else 6
SOLO_COSTO = '--solo-costo' in sys.argv
MIN_PASIVO_CHICO = 20
# Sustitutos solo para la compra en lcsc.com (el original no tiene stock en lcsc.com; JLC sigue montando el
# original, que sí tiene stock en JLC). Estado «substitute ... VERIFY» en docs/BOM_SOURCING.md.
SUST_LCSC = {'C1634': ('C106245', 'CC0603JRNPO9BN100'),     # C303: 10 pF 50 V C0G ±5 % 0603, YAGEO (2026-10-30)
             'C57112': ('C100042', 'CC0603KRX7R9BB103')}    # C601, C607: 10 nF 50 V X7R ±10 % 0603, YAGEO (2026-10-30)
URL = 'https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={}'


def detalle(code, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(URL.format(code), headers={'User-Agent': 'Mozilla/5.0'})
            r = json.load(urllib.request.urlopen(req, timeout=30)).get('result')
            if r: return r
        except Exception:
            pass
        time.sleep(2 + 2 * i)   # el endpoint devuelve 592 de vez en cuando
    raise SystemExit(f'{code}: sin respuesta de lcsc.com')


def pasivo_chico(row):
    fp, ref = row['Footprint'], row['Designator'].split(',')[0]
    return ('_0402_' in fp or '_0603_' in fp) and ref.rstrip('0123456789') in ('R', 'C', 'FB')


filas, avisos, por_codigo, costo = [], [], {}, 0.0
for row in csv.DictReader(open('bom/BOM_PROTO.csv')):
    code = row['LCSC'].strip()
    if not code or row['Supplier'] == 'DigiKey/Mouser': continue
    if code in SUST_LCSC: code, row['MPN'] = SUST_LCSC[code]
    if code in por_codigo:          # mismo código en dos líneas (SW401, SW402): una sola línea en el carrito
        r = por_codigo[code]
        r['Qty'] = str(int(r['Qty']) + int(row['Qty'])); r['Designator'] += ',' + row['Designator']
    else:
        por_codigo[code] = dict(row)
for code, row in por_codigo.items():
    d = detalle(code); time.sleep(0.5)
    q = int(row['Qty']) * PLACAS
    if pasivo_chico(row): q = max(q, MIN_PASIVO_CHICO)
    moq, mult = int(d.get('minBuyNumber') or 1), int(d.get('split') or 1)
    q = max(q, moq)
    q = math.ceil(q / mult) * mult
    stock = d.get('stockNumber') or 0
    if stock < q: avisos.append(f'{code} {row["MPN"]} ({row["Designator"]}): stock lcsc.com {stock} < {q}')
    escalones = sorted((p['ladder'], p['usdPrice']) for p in d.get('productPriceList') or [])
    unit = ([u for n, u in escalones if n <= q] or [escalones[0][1] if escalones else 0])[-1]
    costo += unit * q
    filas.append([code, q, row['MPN'], d.get('productDescEn') or d.get('productNameEn') or row['Comment'],
                  row['Designator']])

if not SOLO_COSTO:
    with open('bom/LCSC_BOM_COMPLETO_PROTO.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['LCSC Part Number', 'Quantity', 'Manufacturer Part Number', 'Description', 'Designator'])
        w.writerows(filas)
print(f'{PLACAS} juegos: {len(filas)} líneas, {sum(r[1] for r in filas)} piezas, '
      f'USD {costo:.2f} en lcsc.com (precio del escalón de cada cantidad, sin envío)')
for a in avisos: print('AVISO', a)
