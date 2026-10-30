# INCLI-VA — BOM con códigos LCSC (sourcing)

Fecha de consulta: **2026-10-30** (Claude Code, rama `bom-sourcing`, PCB `pcb-v1-rc1`). No se hizo ningún pedido.

## Cómo se armó
- Partida: `fab/proto/bom_proto.csv` y `fab/proto/bom_jlc.csv`, más el esquema (solo lectura, `kicad-cli sch export bom`) para los campos `MPN_PROTO` y `DNP`, que definen PROTO y PROD (ver `README.md`).
- Consultas: `jlc_lookup.py` de la skill agentic-sourcing (buscador de piezas de JLCPCB + ficha de lcsc.com), un MPN a la vez. No se creó `sourcing.py`. Cada código LCSC sale de la búsqueda del MPN exacto (o del sustituto) ese día; ninguno es de memoria.
- Stock JLC y stock LCSC son reservas distintas: el stock JLC cuenta para lo que monta JLC; el stock LCSC, para lo que se compra y se suelda a mano.
- «USD a 10 u»: precio unitario de lcsc.com en el escalón de 10 u. Si el pedido mínimo (MOQ) es mayor, se da el precio del MOQ y se indica. En las piezas sin stock en JLC/LCSC se da el precio de lista de LCSC como **referencia** (ref. LCSC); el precio de DigiKey/Mouser **no se consultó** (no hay acceso a sus API desde aquí).
- Estados (convención de la skill): `JLC basic / pref / ext, verified <fecha>`, `... stock N` si no alcanza para 5 placas, `substitute <MPN> for <original> VERIFY`, `not at JLC`.

## Quién monta qué (PROTO)
- **JLC** monta lo que ya estaba en `bom_jlc.csv`/`cpl_jlc.csv`, salvo **L201 y U503**, que JLC no tiene: 63 líneas, 126 piezas en `fab/proto/bom_jlc_lcsc.csv` (C104 sigue en la cara inferior, con el costo extra de ensamblado de dos caras ya anotado en `PENDIENTES.md`).
- **A mano, de LCSC:** J1, J2, J401, J402, U401 (como antes). Carrito: `bom/LCSC_CART_PROTO.csv`.
- **A mano, de DigiKey/Mouser:** L201 (XAL6060-333MEC) y U503 (AS5147U-HTSM). Lista: `bom/DIGIKEY_MOUSER.csv`.

## Antes de subir a JLC (checklist)
1. **Aprobar o rechazar los sustitutos `VERIFY`** (tabla de abajo). Si se rechaza uno, borrar su fila de `bom_jlc_lcsc.csv` y comprar el original de `bom/DIGIKEY_MOUSER.csv` (sección «Respaldo») para soldarlo a mano.
   - Misma pieza, otro sufijo de embalaje: **U501** SCL3300-D01-10 (C3825395; SCL3300-D01 tiene 0 u) y **U601** ADM3055EBRIZ-RL (C658105, 55 u en JLC: reservar pronto). Confirmar el sufijo en la hoja de pedido del fabricante.
   - Mismo valor, encapsulado, tolerancia y tensión ≥ original, distinto fabricante: R108/R112, R109, R110, R303, C102/C103, C106, C110.
   - **Cambian algo de la especificación, revisar con criterio:**
     - C101: X7R 450 V sin AEC-Q200 (original X7T AEC-Q200). Ve hasta 202 V.
     - C201: X7R 100 V sin AEC-Q200 (original X7S AEC-Q200).
     - C104: Lelon VZH 47 µF 100 V D10×L10, 5000 h; confirmar ESR/ripple y si se exige AEC-Q200.
     - F101: AEM MF2410F2.000TM (2 A rápido, 2410, 250 V); confirmar el rating en **DC**, I²t y que los pads coincidan con la huella Bourns propia.
     - **Q101: AOD458** (250 V, 14 A, 280 mΩ; original STD18NF25 165 mΩ). Es el FET de corte del load dump de 202 V: confirmar SOA, VGS y disipación.
     - **Q102: IRLR3110ZTRPBF** (100 V, 14 mΩ, Qg 48 nC; original IPD30N10S3L-34, 24 nC, AEC-Q101). Confirmar el tiempo de encendido con DGATE del LM74930.
     - J402 (a mano): tira 1×3 de 2.54 mm genérica en lugar de Würth 61300311121, que lcsc.com no vende.
2. L201 y U503 están en `cpl_jlc.csv` pero no en la BOM: en la vista previa de JLC quedan sin pieza; marcarlos «no montar».
3. Revisar en la vista previa las rotaciones pendientes (ver `PENDIENTES.md`).
4. Pasivos pasados a Basic: misma huella, valor, tolerancia y dieléctrico, con tensión igual o mayor, pero **sin AEC-Q200**. Para el prototipo no importa; para PROD hay que decidir (ver abajo).

## Pasivos: cambio a JLC Basic/preferred
Solo donde coinciden valor, encapsulado, tolerancia, dieléctrico y tensión (≥ la original); la huella no cambia.
- A Basic: 100 nF 50 V X7R ×20 (C14663), 10 pF C0G (C1634), 10 nF (C57112), 220 nF 25 V (C21120), y las resistencias 0603 1 % de 100 Ω, 49.9 Ω, 470 Ω, 4.7 k, 5.1 k, 10 k, 49.9 k, 100 k y 0 Ω (UNI-ROYAL 0603WAF). En PROD además 220 k (C22961) y 100 k 1206 (C17900).
- A preferred: 68 nF (C31658, que además resuelve el stock 0 del original).
- **No se cambian** (no hay Basic equivalente): 100 nF 100 V (C107, C109, C202) y 4.7 nF 100 V (C609), porque el Basic es de 50 V; 1 µF 16 V X7R, 10 µF 0805 X7R, 22 µF 0805/1206 X7R, porque el Basic es X5R; 24.9 k, 60.4 Ω, 64.9 k, 9.31 k, porque no hay Basic de ese valor; R102 (2512) y R103 (shunt de 10 mΩ).
- Resultado en las 63 líneas que monta JLC: 15 Basic (antes 2, SW401/SW402), 1 preferred y 47 extended.

## Costo de componentes por placa (USD)
Supuestos: precio de lcsc.com en el escalón de (cantidad por placa × N placas); sin repuestos ni sobrante por MOQ; sin cargos de JLC (armado, stencil, cargo por cada extended distinto, ensamblado de dos caras) ni envío; DigiKey/Mouser al precio de referencia de LCSC.

| Variante | 5 placas | 100 placas | JLC (5 / 100) | LCSC a mano (5 / 100) | DigiKey/Mouser (5 / 100) |
|---|---|---|---|---|---|
| PROTO (133 piezas, 70 líneas) | **104.76** | **85.32** | 81.80 / 65.97 | 8.46 / 5.92 | 14.50 / 13.43 |
| PROD (138 piezas, 71 líneas) | **99.45 +** | **83.06 +** | 54.69 / 46.32 | 8.46 / 5.92 | 36.30 / 30.81 |

`+`: falta U701/U751 (SN74AHCT1G126QDBVRQ1), sin precio en JLC/LCSC. Lo más caro por placa: SCL3300 (~19–28), ADM3055E (~15–25), AS5147U (~11), LM74930 (~5.8), ESP32-S3 (~4–4.6).

Carrito LCSC para PROTO (5 placas + 1 repuesto, MOQ respetado): **USD 51.18** (`bom/LCSC_CART_PROTO.csv`).

## PROD (100 placas): diferencias con PROTO
- Usa `MPN` (versiones -Q1) en vez de `MPN_PROTO`: Q701/Q751 DMN10H220LQ-7 (C5260572, en stock), U201, U701/U751 y U801.
- No hay stock en JLC/LCSC para 100 placas de: U201 LMR38010SQDDARQ1, U701/U751 SN74AHCT1G126QDBVRQ1, U801 TPS3828-33QDBVRQ1 (15 u), U601 ADM3055EBRIZ (0 u; -RL 55 u), C105 EEE-FK1H102AV, L201 y U503. Van a DigiKey/Mouser: piezas en consigna a JLC o soldadas a mano.
- Se montan D703/D753, R708–R710, R758–R760 y C105; no se montan D801, D802, R803, R804.
- **Decisión pendiente:** el producto es vehicular y el esquema usa pasivos AEC-Q200 (Murata GCM, TDK CGA, Yageo AC). Los cambios a Basic y varios sustitutos no son AEC-Q200. Si PROD los exige, volver al MPN original (columna «Original» en `bom/BOM_PROD.csv`) o buscar un AEC-Q200 con stock.

## Archivos
- `fab/proto/bom_jlc_lcsc.csv`: BOM de JLC (Comment, Designator, Footprint, LCSC), para subir con `fab/proto/cpl_jlc.csv`.
- `bom/BOM_PROTO.csv`, `bom/BOM_PROD.csv`: BOM completa por variante, con LCSC, tipo, stocks, precio, montaje, estado y MPN/LCSC original.
- `bom/LCSC_CART_PROTO.csv`: carrito de lcsc.com (formato de su BOM tool: «LCSC Part Number», «Quantity»).
- `bom/DIGIKEY_MOUSER.csv`: L201 y U503 (PROTO), las piezas PROD sin stock y los originales de respaldo de los sustitutos, con enlaces de búsqueda.

## Tabla completa — PROTO
| Ref | Valor | Huella | Cant | MPN elegido | LCSC | Tipo JLC | Stock JLC | Stock LCSC | USD a 10 u | Montaje | Estado | Original (MPN / LCSC) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C101 | 100nF | C_1206_3216Metric | 1 | C1206X104K451T | C106025 | ext | 733 | 730 | 0.0671 | JLC | substitute C1206X104K451T for CGA5L4X7T2W104K160AA VERIFY, JLC ext, 2026-10-30 | CGA5L4X7T2W104K160AA / C3887150 |
| C102, C103 | 1uF | C_1206_3216Metric | 2 | CL31B105KCHNNNE | C13832 | ext | 347728 | 261400 | 0.0650 | JLC | substitute CL31B105KCHNNNE for CGA5L2X7R2A105K160AA VERIFY, JLC ext, 2026-10-30 | CGA5L2X7R2A105K160AA / C2168321 |
| C104 | 47uF | CP_Elec_10x10 | 1 | VZH470M2ATR-1010 | C164068 | ext | 1333 | 1330 | 0.2972 | JLC | substitute VZH470M2ATR-1010 for EEE-HA2A470UP VERIFY, JLC ext, 2026-10-30 | EEE-HA2A470UP / C344077 |
| C106 | 10uF | C_1210_3225Metric | 1 | CL32B106KBJNNNE | C138687 | ext | 101468 | 9473 | 0.2610 | JLC | substitute CL32B106KBJNNNE for GCM32ER71H106KA12L VERIFY, JLC ext, 2026-10-30 | GCM32ER71H106KA12L |
| C107, C109, C202 | 100nF | C_0603_1608Metric | 3 | GCM188R72A104KA64D | C415406 | ext | 15215 | 10420 | 0.0637 | JLC | JLC ext, verified 2026-10-30 |  |
| C108, C203, C302, C309, C310, C402, C404, C501, C502, C503, C504, C505, C506, C507, C602, C604, C608, C702, C752, C801 | 100nF | C_0603_1608Metric | 20 | CC0603KRX7R9BB104 | C14663 | basic | 42191376 | 4848800 | 0.0087 (MOQ 100) | JLC | JLC basic (swap from GCM188R71H104KA57D), verified 2026-10-30 | GCM188R71H104KA57D / C85864 |
| C110 | 68nF | C_0603_1608Metric | 1 | CL10B683KB8NNNC | C31658 | pref | 150525 | 115600 | 0.0190 (MOQ 50) | JLC | substitute CL10B683KB8NNNC for GCM188R71H683KA57D VERIFY, JLC pref, 2026-10-30 | GCM188R71H683KA57D / C380380 |
| C201 | 4.7uF | C_1210_3225Metric | 1 | CL32B475KCVZNWE | C17288249 | ext | 435 | 435 | 1.0782 | JLC | substitute CL32B475KCVZNWE for CGA6M3X7S2A475K200AB VERIFY, JLC ext, 2026-10-30 | CGA6M3X7S2A475K200AB / C2168848 |
| C204, C205, C206 | 22uF | C_1206_3216Metric | 3 | GCM31CR71A226KE02L | C126598 | ext | 13053 | 11240 | 0.3296 | JLC | JLC ext, verified 2026-10-30 |  |
| C301, C508, C603, C605, C606 | 10uF | C_0805_2012Metric | 5 | GCM21BR71A106KE22L | C126586 | ext | 9971 | 0 | 0.1029 | JLC | JLC ext, verified 2026-10-30 |  |
| C303 | 10pF | C_0603_1608Metric | 1 | CL10C100JB8NNNC | C1634 | basic | 1212785 | 100 | 0.0061 (MOQ 100) | JLC | JLC basic (swap from GCM1885C1H100JA16D), verified 2026-10-30 | GCM1885C1H100JA16D / C126542 |
| C304, C401 | 22uF | C_0805_2012Metric | 2 | GRM21BZ71A226ME15L | C907991 | ext | 166294 | 140195 | 0.3744 | JLC | JLC ext, verified 2026-10-30 |  |
| C306, C307, C403 | 1uF | C_0603_1608Metric | 3 | GCM188R71C105KA64D | C161212 | ext | 33722 | 18280 | 0.0383 (MOQ 20) | JLC | JLC ext, verified 2026-10-30 |  |
| C601, C607 | 10nF | C_0603_1608Metric | 2 | 0603B103K500NT | C57112 | basic | 5628260 | 28450 | 0.0098 (MOQ 50) | JLC | JLC basic (swap from GCM188R71H103KA37D), verified 2026-10-30 | GCM188R71H103KA37D / C85863 |
| C609 | 4.7nF | C_0603_1608Metric | 1 | GCM188R72A472KA37D | C426631 | ext | 16111 | 16100 | 0.0288 (MOQ 20) | JLC | JLC ext, verified 2026-10-30 |  |
| C610 | 220nF | C_0603_1608Metric | 1 | CL10B224KA8NNNC | C21120 | basic | 1011962 | 394350 | 0.0094 (MOQ 50) | JLC | JLC basic (swap from GCM188R71E224KA55D), verified 2026-10-30 | GCM188R71E224KA55D / C161217 |
| D101 | ES2G | D_SMB | 1 | ES2G-E3/52T | C2927419 | ext | 8924 | 8920 | 0.1781 | JLC | JLC ext, verified 2026-10-30 |  |
| D102 | SMCJ33A | D_SMC | 1 | SMCJ33A | C438109 | ext | 26629 | 26625 | 0.1049 | JLC | JLC ext, verified 2026-10-30 |  |
| D103 | SMAJ51A | D_SMA | 1 | SMAJ51A | C366557 | ext | 5525 | 5520 | 0.0314 (MOQ 20) | JLC | JLC ext, verified 2026-10-30 |  |
| D104 | BAS21 | SOT-23 | 1 | BAS21,215 | C8661 | ext | 41868 | 40880 | 0.0179 (MOQ 20) | JLC | JLC ext, verified 2026-10-30 |  |
| D701, D751 | SMAJ58A | D_SMA | 2 | SMAJ58A | C123816 | ext | 15859 | 15840 | 0.0456 (MOQ 20) | JLC | JLC ext, verified 2026-10-30 |  |
| D704, D754 | 12V | D_SOD-123 | 2 | MMSZ5242B-7-F | C500776 | ext | 97152 | 97150 | 0.0450 | JLC | JLC ext, verified 2026-10-30 |  |
| D801 | verde | LED_0805_2012Metric | 1 | LTST-C171KGKT | C98224 | ext | 152901 | 152900 | 0.0347 (MOQ 20) | JLC | JLC ext, verified 2026-10-30 |  |
| D802 | rojo | LED_0805_2012Metric | 1 | LTST-C171KRKT | C284871 | ext | 69636 | 68740 | 0.0263 (MOQ 20) | JLC | JLC ext, verified 2026-10-30 |  |
| F101 | 2A 250VDC | Fuse_Bourns_SF-2410 | 1 | MF2410F2.000TM | C83797 | ext | 77993 | 77995 | 0.0831 | JLC | substitute MF2410F2.000TM for SF-2410FPA200W-2 VERIFY, JLC ext, 2026-10-30 | SF-2410FPA200W-2 / C3159902 |
| FB301 | 220R@100MHz | L_0603_1608Metric | 1 | BLM18PG221SN1D | C80165 | ext | 243305 | 235750 | 0.0149 (MOQ 50) | JLC | JLC ext, verified 2026-10-30 |  |
| FB601, FB602 | 1.8k@100MHz | L_0603_1608Metric | 2 | BLM18BD182SN1D | C113020 | ext | 5170 | 5160 | 0.0362 (MOQ 20) | JLC | JLC ext, verified 2026-10-30 |  |
| J1 | MSTBV 2,5/5-GF-5,08 | PhoenixContact_MSTBV_2,5_5-G | 1 | 1777109 | C7164734 | ext | 327 | 317 | 0.9724 | mano | JLC ext, verified 2026-10-30 |  |
| J2 | MSTBV 2,5/2-GF-5,08 | PhoenixContact_MSTBV_2,5_2-G | 1 | 1777073 | C480552 | ext | 837 | 835 | 1.1001 | mano | JLC ext, verified 2026-10-30 |  |
| J401 | USB4105-GF-A | USB_C_Receptacle_GCT_USB4105 | 1 | USB4105-GF-A | C3020560 | ext | 3189 | 413 | 1.1001 | mano | JLC ext, verified 2026-10-30 |  |
| J402 | UART0 | PinHeader_1x03_P2.54mm_Verti | 1 | 2.54-1*3PPin | C49257 | ext | 151423 | 151440 | 0.0286 (MOQ 20) | mano | substitute 2.54-1*3PPin for 61300311121 VERIFY, JLC ext, 2026-10-30 | 61300311121 / C2915006 |
| L101 | 10uH | L_Bourns_SRN6045TA | 1 | SRN6045TA-100M | C2046332 | ext | 6156 | 6045 | 0.2544 | JLC | JLC ext, verified 2026-10-30 |  |
| L201 | 33uH | L_Coilcraft_XAL6060-XXX | 1 | XAL6060-333MEC | — | — | — | — | 2.8281 (ref. LCSC) | mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C5119929 |
| L301 | 1uH | L_Coilcraft_XAL4020_HandSold | 1 | XAL4020-102MEC | C4555951 | ext | 7626 | 7626 | 4.2523 | JLC | JLC ext, verified 2026-10-30 |  |
| Q101 | STD18NF25 | TO-252-2 | 1 | AOD458 | C85109 | ext | 2553 | 2526 | 0.5120 | JLC | substitute AOD458 for STD18NF25 VERIFY, JLC ext, 2026-10-30 | STD18NF25 / C183634 |
| Q102 | IPD30N10S3L-34 | TO-252-2 | 1 | IRLR3110ZTRPBF | C67277 | ext | 717 | 689 | 0.8328 | JLC | substitute IRLR3110ZTRPBF for IPD30N10S3L34ATMA1 VERIFY, JLC ext, 2026-10-30 | IPD30N10S3L34ATMA1 / C148263 |
| Q701, Q751 | DMN10H220LQ | SOT-23 | 2 | DMN10H220L-7 | C102615 | ext | 16334 | 16330 | 0.3319 | JLC | JLC ext, verified 2026-10-30 |  |
| R102 | 10k | R_2512_6332Metric | 1 | AC2512FK-0710KL | C469651 | ext | 1508 | 1505 | 0.0933 | JLC | JLC ext, verified 2026-10-30 |  |
| R103 | 10m | R_1206_3216Metric | 1 | ERJ-8BWFR010V | C2076185 | ext | 5332 | 4125 | 0.1219 | JLC | JLC ext, verified 2026-10-30 |  |
| R104 | 49.9 | R_0603_1608Metric | 1 | 0603WAF499JT5E | C23185 | basic | 1388908 | 411400 | 0.0021 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-0749R9L), verified 2026-10-30 | AC0603FR-0749R9L / C144653 |
| R105 | 100 | R_0603_1608Metric | 1 | 0603WAF1000T5E | C22775 | basic | 9522722 | 1107900 | 0.0024 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-07100RL), verified 2026-10-30 | AC0603FR-07100RL / C125923 |
| R106, R201, R301, R302, R304, R305, R307, R308, R703, R711, R753, R761 | 100k | R_0603_1608Metric | 12 | 0603WAF1003T5E | C25803 | basic | 17755977 | 8896900 | 0.0030 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-07100KL), verified 2026-10-30 | AC0603FR-07100KL / C116674 |
| R107 | 9.31k | R_0603_1608Metric | 1 | AC0603FR-079K31L | C144630 | ext | 6619 | 6600 | 0.0058 (MOQ 100) | JLC | JLC ext, verified 2026-10-30 |  |
| R108, R112 | 51k | R_1206_3216Metric | 2 | RC1206FR-0751KL | C114947 | ext | 140795 | 131250 | 0.0113 (MOQ 50) | JLC | substitute RC1206FR-0751KL for AC1206FR-0751KL VERIFY, JLC ext, 2026-10-30 | AC1206FR-0751KL / C144484 |
| R109 | 1.62k | R_0603_1608Metric | 1 | CR0603FA1621G | C100797 | ext | 1100 | 1100 | 0.0014 (MOQ 100) | JLC | substitute CR0603FA1621G for AC0603FR-071K62L VERIFY, JLC ext, 2026-10-30 | AC0603FR-071K62L / C227657 |
| R110 | 60.4k | R_0603_1608Metric | 1 | RC0603FR-0760K4L | C165742 | ext | 48563 | 48500 | 0.0062 (MOQ 100) | JLC | substitute RC0603FR-0760K4L for AC0603FR-0760K4L VERIFY, JLC ext, 2026-10-30 | AC0603FR-0760K4L / C227994 |
| R111, R401, R402, R501, R502, R503, R601, R604 | 10k | R_0603_1608Metric | 8 | 0603WAF1002T5E | C25804 | basic | 40290635 | 1435400 | 0.0022 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-0710KL), verified 2026-10-30 | AC0603FR-0710KL / C116677 |
| R202 | 24.9k | R_0603_1608Metric | 1 | AC0603FR-0724K9L | C227732 | ext | 3945 | 3900 | 0.0064 (MOQ 100) | JLC | JLC ext, verified 2026-10-30 |  |
| R203 | 64.9k | R_0603_1608Metric | 1 | AC0603FR-0764K9L | C228007 | ext | 920 | 900 | 0.0042 (MOQ 100) | JLC | JLC ext, verified 2026-10-30 |  |
| R303 | 453k | R_0603_1608Metric | 1 | CR0603FA4533G | C101055 | ext | 4984 | 4950 | 0.0093 (MOQ 50) | JLC | substitute CR0603FA4533G for AC0603FR-07453KL VERIFY, JLC ext, 2026-10-30 | AC0603FR-07453KL / C227908 |
| R306 | 49.9k | R_0603_1608Metric | 1 | 0603WAF4992T5E | C23184 | basic | 1532153 | 1273400 | 0.0029 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-0749K9L), verified 2026-10-30 | AC0603FR-0749K9L / C144654 |
| R403, R404 | 5.1k | R_0603_1608Metric | 2 | 0603WAF5101T5E | C23186 | basic | 21368680 | 16397700 | 0.0016 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-075K1L), verified 2026-10-30 | AC0603FR-075K1L / C125891 |
| R602, R603 | 60.4 | R_0603_1608Metric | 2 | AC0603FR-0760R4L | C144645 | ext | 14047 | 14000 | 0.0069 (MOQ 100) | JLC | JLC ext, verified 2026-10-30 |  |
| R605, R802, R805, R806 | 0 | R_0603_1608Metric | 4 | 0603WAF0000T5E | C21189 | basic | 20896231 | 11816300 | 0.0022 (MOQ 100) | JLC | JLC basic (swap from AC0603JR-070RL), verified 2026-10-30 | AC0603JR-070RL / C141796 |
| R702, R752 | 4k7 | R_0603_1608Metric | 2 | 0603WAF4701T5E | C23162 | basic | 15672993 | 3249500 | 0.0028 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-074K7L), verified 2026-10-30 | AC0603FR-074K7L / C116697 |
| R803, R804 | 470 | R_0603_1608Metric | 2 | 0603WAF4700T5E | C23179 | basic | 4576407 | 1980200 | 0.0023 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-07470RL), verified 2026-10-30 | AC0603FR-07470RL / C144657 |
| SW401 | RESET | SW-SMD_L3.9-W3.0-P4.45 | 1 | TS-1088-AR02016 | C720477 | basic | 605935 | 363750 | 0.0533 | JLC | JLC basic, verified 2026-10-30 |  |
| SW402 | BOOT | SW-SMD_L3.9-W3.0-P4.45 | 1 | TS-1088-AR02016 | C720477 | basic | 605935 | 363750 | 0.0533 | JLC | JLC basic, verified 2026-10-30 |  |
| U101 | LM74930QRGERQ1 | TI_RGE0024T_VQFN-24-1EP_4x4m | 1 | LM74930QRGERQ1 | C22428070 | ext | 7308 | 7127 | 5.7664 | JLC | JLC ext, verified 2026-10-30 |  |
| U201 | LMR38010SQDDARQ1 | SOIC-8-1EP_3.9x4.9mm_P1.27mm | 1 | LMR38010SDDAR | C5219310 | ext | 2650 | 2650 | 0.7324 | JLC | JLC ext, verified 2026-10-30 |  |
| U301 | TPS62A02QDRLRQ1 | SOT-563 | 1 | TPS62A02QDRLRQ1 | C49259289 | ext | 190 | 190 | 0.5093 | JLC | JLC ext, verified 2026-10-30 |  |
| U302 | LP5907QMFX-3.3Q1 | SOT-23-5 | 1 | LP5907QMFX-3.3Q1 | C130005 | ext | 3282 | 2994 | 0.7792 | JLC | JLC ext, verified 2026-10-30 |  |
| U401 | ESP32-S3-WROOM-1-N8R2 | ESP32-S3-WROOM-1 | 1 | ESP32-S3-WROOM-1-N8R2 | C2913204 | ext | 18179 | 7131 | 4.0407 | mano | JLC ext, verified 2026-10-30 |  |
| U402 | USBLC6-2SC6 | SOT-23-6 | 1 | USBLC6-2SC6 | C2687116 | ext | 119890 | 119900 | 0.0482 | JLC | JLC ext, verified 2026-10-30 |  |
| U501 | SCL3300-D01 | DFL-12_L8.6-W7.0-P1.00-LS7.6 | 1 | SCL3300-D01-10 | C3825395 | ext | 721 | 721 | 27.9106 | JLC | substitute SCL3300-D01-10 for SCL3300-D01 VERIFY, JLC ext, 2026-10-30 | SCL3300-D01 / C22416657 |
| U502 | ASM330LHHTR | LGA-14_3x2.5mm_P0.5mm_Layout | 1 | ASM330LHHTR | C459826 | ext | 7766 | 7527 | 4.6845 | JLC | JLC ext, verified 2026-10-30 |  |
| U503 | AS5147U-HTSM | TSSOP-14_4.4x5mm_P0.65mm | 1 | AS5147U-HTSM | — | — | — | — | 10.8657 (ref. LCSC) | mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C2153628 |
| U601 | ADM3055E | SOIC-20W_7.5x12.8mm_P1.27mm | 1 | ADM3055EBRIZ-RL | C658105 | ext | 55 | 55 | 24.4771 | JLC | substitute ADM3055EBRIZ-RL for ADM3055EBRIZ VERIFY, JLC ext, 2026-10-30 | ADM3055EBRIZ / C658104 |
| U701, U751 | 74AHCT1G126 | SOT-23-5 | 2 | SN74AHCT1G126DBVR | C163712 | ext | 8462 | 8055 | 0.0949 | JLC | JLC ext, verified 2026-10-30 |  |
| U801 | TPS3828-33Q1 | SOT-23-5 | 1 | TPS3828-33DBVR | C20032 | ext | 49770 | 49770 | 0.3771 | JLC | JLC ext, verified 2026-10-30 |  |


## Tabla — PROD (solo las líneas que cambian respecto de PROTO)

Fuera de PROD: D801, D802, R803, R804 (DNP PROD). El resto es igual que en PROTO; la BOM completa está en `bom/BOM_PROD.csv`.

| Ref | Valor | Huella | Cant | MPN elegido | LCSC | Tipo JLC | Stock JLC | Stock LCSC | USD a 10 u | Montaje | Estado | Original (MPN / LCSC) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C105 | 1000uF 50V | CP_Elec_Panasonic_J16_VibPro | 1 | EEE-FK1H102AV | — | — | — | — | 0.8694 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C2164039 |
| D703, D753 | BZX84-C3V3 | SOT-23 | 2 | BZX84-C3V3,215 | C85087 | ext | 28154 | 28150 | 0.0180 (MOQ 50) | JLC | JLC ext, verified 2026-10-30 |  |
| Q701, Q751 | DMN10H220LQ | SOT-23 | 2 | DMN10H220LQ-7 | C5260572 | ext | 4738 | 4595 | 0.2997 | JLC | JLC ext, verified 2026-10-30 |  |
| R708, R709, R758, R759 | 100k | R_1206_3216Metric | 4 | 1206W4F1003T5E | C17900 | basic | 937779 | 315500 | 0.0097 (MOQ 50) | JLC | JLC basic (swap from AC1206FR-07100KL), verified 2026-10-30 | AC1206FR-07100KL / C144522 |
| R710, R760 | 220k | R_0603_1608Metric | 2 | 0603WAF2203T5E | C22961 | basic | 1137879 | 809400 | 0.0015 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-07220KL), verified 2026-10-30 | AC0603FR-07220KL / C144681 |
| U201 | LMR38010SQDDARQ1 | SOIC-8-1EP_3.9x4.9mm_P1.27mm | 1 | LMR38010SQDDARQ1 | — | — | — | — | 2.7991 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C18198885 |
| U601 | ADM3055E | SOIC-20W_7.5x12.8mm_P1.27mm | 1 | ADM3055EBRIZ | — | — | — | — | 15.3791 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C658104 |
| U701, U751 | 74AHCT1G126 | SOT-23-5 | 2 | SN74AHCT1G126QDBVRQ1 | — | — | — | — | s/d | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 |  |
| U801 | TPS3828-33Q1 | SOT-23-5 | 1 | TPS3828-33QDBVRQ1 | — | — | — | — | 1.4158 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C2872895 |
