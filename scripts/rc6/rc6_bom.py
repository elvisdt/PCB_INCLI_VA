#!/usr/bin/python3
"""rc6: actualiza bom/BOM_PROTO.csv y bom/BOM_PROD.csv con los cambios de R-01/R-02 (2026-10-30).

Uso: /usr/bin/python3 -B scripts/rc6/rc6_bom.py   (después: scripts/bom/lcsc_bom_completo.py y scripts/ruteo/etapa6_fab.py)
- R106 sale de la línea de 100 kΩ 0603 y, con R113, pasa a la de 51 kΩ 1206 (R108/R112): mismo MPN.
- R107: 9.31 kΩ -> 9.53 kΩ.
- D104: BAS21 -> BAV23C (PROTO Diodes BAV23C-7-F; PROD Nexperia BAV23C,215, sin stock en LCSC/JLC el 2026-10-30).
Stock y precios: jlc_lookup.py de agentic-sourcing (solo consulta), 2026-10-30.
TP105-TP107 son pads de prueba: fuera del BOM, como el resto de los TP.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R107 = {
    'PROTO': dict(Comment='9.53k', MPN='0603WAF9531T5E', Manufacturer='UNI-ROYAL', LCSC='C23127', JLC_Type='ext',
                  JLC_Stock='108494', LCSC_Stock='108500', Price_10_USD='0.0017 (MOQ 100)',
                  Status='substitute 0603WAF9531T5E for AC0603FR-079K53L accepted 2026-10-30 (rc6), JLC ext',
                  Orig_MPN='AC0603FR-079K53L', Orig_LCSC='C228113', Notes='9.53k 1% 0603; rc6 R-01 (UVLO 6.44 V)'),
    'PROD': dict(Comment='9.53k', MPN='AC0603FR-079K53L', Manufacturer='Yageo', LCSC='C228113', JLC_Type='ext',
                 JLC_Stock='3289', LCSC_Stock='3200', Price_10_USD='0.0067 (MOQ 100)',
                 Status='JLC ext, verified 2026-10-30 (rc6)', Orig_MPN='', Orig_LCSC='', Notes='rc6 R-01 (UVLO 6.44 V)'),
}
D104 = {
    'PROTO': dict(Comment='BAV23C', MPN='BAV23C-7-F', Manufacturer='Diodes Incorporated', LCSC='C150732', JLC_Type='ext',
                  JLC_Stock='5477', LCSC_Stock='5450', Price_10_USD='0.77',
                  Status='substitute BAV23C-7-F for BAV23C,215 accepted 2026-10-30 (rc6), JLC ext',
                  Orig_MPN='BAV23C,215', Orig_LCSC='C282370',
                  Notes='Original sin stock (LCSC y JLC 0); DS30042 Rev. 23-2: mismo pinout (1 A1, 2 A2, 3 K), 250/200 V, 400 mA; sin AEC-Q101'),
    'PROD': dict(Comment='BAV23C', MPN='BAV23C,215', Manufacturer='Nexperia', LCSC='C282370', JLC_Type='ext',
                 JLC_Stock='0', LCSC_Stock='0', Price_10_USD='0.1158 (ref. LCSC, MOQ 5)', Supplier='DigiKey/Mouser',
                 Assembly='consigna JLC o mano', Status='not at JLC/LCSC (stock 0), DigiKey/Mouser, checked 2026-10-30',
                 Orig_MPN='', Orig_LCSC='', Notes='rc6 R-02 (D1 de TI fig. 8-1 dentro de D104); PROD automotriz: evaluar BAV23CQ'),
}

for var, nombre in (('PROTO', 'BOM_PROTO.csv'), ('PROD', 'BOM_PROD.csv')):
    p = ROOT / 'bom' / nombre
    filas = list(csv.DictReader(p.open(newline='')))
    campos = list(filas[0].keys())
    hechos = set()
    for f in filas:
        refs = [r.strip() for r in f['Designator'].split(',')]
        if 'R106' in refs and f['Footprint'] == 'R_0603_1608Metric':
            refs.remove('R106'); hechos.add('100k')
        if refs == ['R108', 'R112']:
            refs = ['R106', 'R108', 'R112', 'R113']; hechos.add('51k')
        if refs == ['R107']:
            f.update(R107[var]); hechos.add('R107')
        if refs == ['D104']:
            f.update(D104[var]); hechos.add('D104')
        f['Designator'] = ','.join(refs); f['Qty'] = str(len(refs))
    assert hechos == {'100k', '51k', 'R107', 'D104'}, (nombre, hechos)
    with p.open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=campos); w.writeheader(); w.writerows(filas)
    print(nombre, 'actualizado')
