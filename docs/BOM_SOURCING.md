# INCLI-VA — BOM con códigos LCSC (sourcing)

Consulta: **2026-10-30**. Decisiones del usuario sobre los sustitutos: **2026-10-30**. Claude Code, rama `bom-sourcing`, PCB `pcb-v1-rc1`. No se hizo ningún pedido. El esquema no se modificó: el paso de los sustitutos aceptados a `MPN_PROTO`/LCSC queda para otra sesión.

## Plan de compra vigente (usuario, 2026-10-30) — RESUMEN
**JLC solo fabrica la PCB y el stencil Top; todos los componentes se compran en LCSC y se sueldan a mano.** Los archivos de ensamblado de JLC (`fab/proto/bom_jlc_lcsc.csv` + `fab/proto/cpl_jlc.csv`, 58 líneas, 123 piezas) se mantienen al día como alternativa, pero no se compara el costo de ensamblado.

| Compra | Archivo | 6 juegos (5 placas + 1) | 3 juegos (2 placas + 1) |
|---|---|---|---|
| **LCSC** (todo lo que está en lcsc.com) | `bom/LCSC_BOM_COMPLETO_PROTO.csv` («Upload a BOM»: LCSC Part Number, Quantity, Manufacturer Part Number, Description, Designator) | 62 líneas, 2509 piezas, **USD 552.43** | 2312 piezas, **USD 286.65** |
| **DigiKey/Mouser** (sin stock en LCSC) | `bom/DIGIKEY_MOUSER.csv` (`Uso` = PROTO mano + PROD) | 5 líneas × 6 u, **≈ USD 99.54** | ≈ USD 49.77 |
| **Total componentes** | | **≈ USD 651.97** | **≈ USD 336.42** |
| por juego | | ≈ USD 108.66 | ≈ USD 112.14 |
| **por placa armada** (repuesto incluido) | | **≈ USD 130.39** (÷ 5) | ≈ USD 168.21 (÷ 2) |

- LCSC: precio de lcsc.com en el escalón de cada cantidad (consulta en vivo del 2026-10-30), sin envío ni impuestos. Cantidad = por placa × juegos; pasivos 0402/0603 al menos 20 por la merma al soldar a mano; después se sube al pedido mínimo y al múltiplo de lcsc.com. Regenerar con `/usr/bin/python3 -B scripts/bom/lcsc_bom_completo.py [JUEGOS]` (`--solo-costo` para no escribir el archivo). Sin avisos de stock.
- **DigiKey/Mouser: precios estimados, a verificar** en sus sitios antes de comprar (no se pudieron leer en vivo):
  - U503 AS5147U-HTSM ≈ 8.44 (Mouser)
  - Q101 STD18NF25 ≈ 2.79 (DigiKey)
  - Q102 IPD30N10S3L34ATMA1 ≈ 1.50 (Farnell como referencia)
  - F101 SF-2410FPA200W-2 ≈ 1.03 (otra corriente de la misma familia)
  - **L201 XAL6060-333MEC ≈ 2.83 (lista de LCSC): DigiKey lo marca «Not Available» y sugiere XGL6060-333MEC; hay que pedir cotización a Coilcraft o buscarlo en Mouser.** Cambiar L201 por otra serie es una decisión de diseño (buck de U201), pendiente.
- Los cinco **siguen sin stock en lcsc.com** (consulta 2026-10-30: XAL6060-333MEC C5119929, AS5147U-HTSM C38675951, STD18NF25 C183634, IPD30N10S3L34ATMA1 C148263, SF-2410FPA200W-2 C3159902, todos con 0).
- No incluye la PCB, el stencil ni el envío. `bom/A_MANO_PROTO.csv` y `bom/LCSC_CART_PROTO.csv` quedan como historia (lista a mano cuando JLC montaba).

### Consolidación de pasivos (aprobada, aplicada el 2026-10-30)
Solo cambian valor y campos; ninguna huella cambia. Script: `scripts/bom/consolidar_pasivos.py`.

| Referencias | Antes | Ahora | Por qué no afecta |
|---|---|---|---|
| R702, R752 (gate en serie de Q701/Q751) | 4k7 | **2.2k**, la misma línea que R803/R804 (PROTO C4190; PROD AC0603FR-072K2L) | Con el pull-down de 100k, Vgs sube de 4.78 a 4.89 V; pico de carga 2.3 mA (el 74AHCT da 8 mA); consumo fijo igual (~49 µA); τ = 2.2k × Ciss < 2.2 µs |
| 23 × 100 nF 0603 (C107–C109, C202, C203, C302, C309, C310, C402, C404, C501–C507, C602, C604, C608, C702, C752, C801) | 2 MPN (100 V y 50 V) | **un solo MPN 100 V X7R**: PROTO FH 0603B104K101NT (C88219); PROD Murata GCM188R72A104KA64D (AEC-Q200) | Mismo valor, tolerancia y dieléctrico; más tensión y menos pérdida por DC bias. C109 (C_dVdT) mantiene la corriente de arranque |
| C306, C307, C403 (1 µF 0603) | GCM 16 V | PROTO **Yageo CC0603KRX7R9BB105, 50 V X7R** (C559769); PROD sin cambio | Más stock y DC bias; τ de EN (R401 × C403 = 10 ms) igual |
| C301, C508, C603, C605, C606 (10 µF 0805) | GCM 10 V (0 en lcsc.com) | PROTO **Samsung CL21B106KAYQNNE, 25 V X7R** (C3039694); PROD sin cambio | Más tensión, mismo dieléctrico; a 5 V conserva más capacidad |

Resultado: BOM PROTO de 70 a **68 líneas**; JLC de 60 a **58 líneas**. Los cargos de ensamblado no cambian (ya no aplican al plan de compra).

## Estado en el esquema y el PCB (`pcb-v1-rc2`, 2026-10-30)
- Todos los componentes llevan `LCSC` = código del `MPN` (producción; vacío en C106 y U701/U751, que LCSC no lista). `MPN` no cambió: sigue siendo el original (AEC-Q200 / -Q1).
- PROTO: `MPN_PROTO`, `LCSC_PROTO` y, si cambia el fabricante, `Manufacturer_PROTO`, con los sustitutos aceptados (pasivos Basic/preferred, igual especificación, C101/C201/C104 sin AEC-Q200, SCL3300-D01-10, ADM3055EBRIZ-RL y tira genérica de J402). `Notes` indica PROTO/PROD, compra y montaje a mano donde corresponde.
- Q101, Q102 y F101 no tienen campos PROTO: el prototipo usa el original (DigiKey/Mouser, a mano).
- `scripts/ruteo/etapa6_fab.py` genera `fab/proto/bom_jlc_lcsc.csv` desde esos campos; sale idéntico al que se armó a mano.
- **PROD:** el esquema conserva en `MPN`/`LCSC` los originales de todas las piezas. `bom/BOM_PROD.csv` propone además los pasivos Basic y los sustitutos de igual especificación para PROD; pasarlos a `MPN` queda para cuando se cierre la BOM de producción.

## Cómo se armó
- Partida: `fab/proto/bom_proto.csv` y `fab/proto/bom_jlc.csv`, más el esquema (solo lectura, `kicad-cli sch export bom`) para los campos `MPN_PROTO` y `DNP`, que definen PROTO y PROD (ver `README.md`).
- Consultas: `jlc_lookup.py` de la skill agentic-sourcing (buscador de piezas de JLCPCB y ficha de lcsc.com), un MPN a la vez. No se creó `sourcing.py`. Cada código LCSC sale de la búsqueda del MPN exacto (o del sustituto) ese día; ninguno es de memoria.
- Stock JLC y stock LCSC son reservas distintas: el de JLC cuenta para lo que monta JLC; el de LCSC, para lo que se compra y se suelda a mano.
- «USD a 10 u»: precio unitario de lcsc.com en el escalón de 10 u. Si el pedido mínimo (MOQ) es mayor, se da el precio del MOQ y se indica. Para las piezas sin stock en JLC/LCSC se da el precio de lista de LCSC como **referencia** (ref. LCSC). El precio de DigiKey/Mouser **no se consultó**.
- Estados: `JLC basic / pref / ext, verified <fecha>`, `... stock N` si no alcanza para 5 placas, `substitute <MPN> for <original> accepted <fecha>` (aprobado por el usuario), `not at JLC, DigiKey/Mouser`.
- `fab/proto/bom_jlc.csv` (sin LCSC) queda como estaba, como referencia histórica. Para el pedido se usa `bom_jlc_lcsc.csv`.

## Decisiones sobre sustitutos (usuario, 2026-10-30)
| Pieza | Propuesta | Decisión |
|---|---|---|
| Q101 STD18NF25 | AOD458 (C85109) | **Rechazado.** Protección de entrada: el prototipo debe validar el diseño de producción. Original de DigiKey/Mouser, a mano. |
| Q102 IPD30N10S3L-34 | IRLR3110ZTRPBF (C67277) | **Rechazado.** Ídem. |
| F101 Bourns SF-2410FPA200W-2 | AEM MF2410F2.000TM (C83797) | **Rechazado.** Ídem. |
| C101, C201, C104 | C1206X104K451T, CL32B475KCVZNWE, Lelon VZH470M2ATR-1010 (sin AEC-Q200) | **Aceptados solo en PROTO.** PROD mantiene CGA5L4X7T2W104K160AA, CGA6M3X7S2A475K200AB y EEE-HA2A470UP (sin stock en JLC/LCSC: DigiKey/Mouser). |
| U501 SCL3300-D01 | SCL3300-D01-10 (C3825395) | **Aceptado.** Murata Doc. 4921 Rev. 2, §9 «Order Information»: `-004` bulk de 4 u, `-1` carrete de 100 u, `-10` carrete de 1000 u, con la misma descripción. Solo cambia el embalaje. |
| U601 ADM3055EBRIZ | ADM3055EBRIZ-RL (C658105) | **Aceptado** (mismo CI en carrete; JLC tiene 55 u, alcanza para PROTO pero no para 100 placas). |
| Pasivos a Basic/preferred | ver «Pasivos» | **Aceptados.** |
| Igual especificación (mismo dieléctrico, tensión ≥, tolerancia y huella) | R108/R112, R109, R110, R303, C102/C103, C106, C110; J402 (tira 1×3 de 2.54 mm genérica por Würth 61300311121, misma huella) | **Aceptados.** |

## Pasivos: cambio a JLC Basic/preferred (aceptado)
Solo donde coinciden valor, encapsulado, tolerancia y dieléctrico, con tensión ≥ la original; la huella no cambia.
- A Basic: 100 nF 50 V X7R ×20 (C14663), 10 pF C0G (C1634), 10 nF (C57112), 220 nF 25 V (C21120), y las resistencias 0603 1 % de 100 Ω, 49.9 Ω, 470 Ω, 4.7 k, 5.1 k, 10 k, 49.9 k, 100 k y 0 Ω (UNI-ROYAL 0603WAF). En PROD, además, 220 k (C22961) y 100 k 1206 (C17900).
- A preferred: 68 nF (C31658, que además resuelve el stock 0 del original).
- **No se cambian**, porque no hay Basic equivalente: 100 nF 100 V (C107, C109, C202) y 4.7 nF 100 V (C609), cuyo Basic es de 50 V; 1 µF 16 V X7R, 10 µF 0805 X7R y 22 µF 0805/1206 X7R, cuyo Basic es X5R; 24.9 k, 60.4 Ω, 64.9 k y 9.31 k, que no tienen Basic de ese valor; R102 (2512) y R103 (shunt de 10 mΩ).
- En las 60 líneas que monta JLC quedan 15 Basic (antes 2: SW401 y SW402), 1 preferred y 44 extended.

## Las dos listas (PROTO)
### 1. Lo que monta JLC: `fab/proto/bom_jlc_lcsc.csv` + `fab/proto/cpl_jlc.csv`

60 líneas, 123 piezas. Las designaciones de la BOM y del CPL coinciden una a una (verificado). C104 va en la cara inferior: ensamblado de dos caras, con costo extra.

| Ref | Valor | LCSC |
|---|---|---|
| C101 | 100nF | C106025 |
| C102, C103 | 1uF | C13832 |
| C104 | 47uF | C164068 |
| C106 | 10uF | C138687 |
| C107, C108, C109, C202, C203, C302, C309, C310, C402, C404, C501, C502, C503, C504, C505, C506, C507, C602, C604, C608, C702, C752, C801 | 100nF | C88219 |
| C110 | 68nF | C31658 |
| C201 | 4.7uF | C17288249 |
| C204, C205, C206 | 22uF | C126598 |
| C301, C508, C603, C605, C606 | 10uF | C3039694 |
| C303 | 10pF | C1634 |
| C304, C401 | 22uF | C907991 |
| C306, C307, C403 | 1uF | C559769 |
| C601, C607 | 10nF | C57112 |
| C609 | 4.7nF | C426631 |
| C610 | 220nF | C21120 |
| D101 | ES2G | C2927419 |
| D102 | SMCJ33A | C438109 |
| D103 | SMAJ51A | C366557 |
| D104 | BAS21 | C8661 |
| D701, D751 | SMAJ58A | C123816 |
| D704, D754 | 12V | C500776 |
| D801 | verde | C98224 |
| D802 | rojo | C284871 |
| FB301 | 220R@100MHz | C80165 |
| FB601, FB602 | 1.8k@100MHz | C113020 |
| L101 | 10uH | C2046332 |
| L301 | 1uH | C4555951 |
| Q701, Q751 | DMN10H220LQ | C102615 |
| R102 | 10k | C469651 |
| R103 | 10m | C2076185 |
| R104 | 49.9 | C23185 |
| R105 | 100 | C22775 |
| R106, R201, R301, R302, R304, R305, R307, R308, R703, R711, R753, R761 | 100k | C25803 |
| R107 | 9.31k | C144630 |
| R108, R112 | 51k | C114947 |
| R109 | 1.62k | C100797 |
| R110 | 60.4k | C165742 |
| R111, R401, R402, R501, R502, R503, R601, R604 | 10k | C25804 |
| R202 | 24.9k | C227732 |
| R203 | 64.9k | C228007 |
| R303 | 453k | C101055 |
| R306 | 49.9k | C23184 |
| R403, R404 | 5.1k | C23186 |
| R602, R603 | 60.4 | C144645 |
| R605, R802, R805, R806 | 0 | C21189 |
| R702, R752, R803, R804 | 2.2k | C4190 |
| SW401 | RESET | C720477 |
| SW402 | BOOT | C720477 |
| U101 | LM74930QRGERQ1 | C22428070 |
| U201 | LMR38010SQDDARQ1 | C5219310 |
| U301 | TPS62A02QDRLRQ1 | C49259289 |
| U302 | LP5907QMFX-3.3Q1 | C130005 |
| U402 | USBLC6-2SC6 | C2687116 |
| U501 | SCL3300-D01 | C3825395 |
| U502 | ASM330LHHTR | C459826 |
| U601 | ADM3055E | C658105 |
| U701, U751 | 74AHCT1G126 | C163712 |
| U801 | TPS3828-33Q1 | C20032 |

### 2. Lo que sueldo a mano: `bom/A_MANO_PROTO.csv` (5 placas + 1 de repuesto)

| Ref | MPN | Fabricante | Proveedor | LCSC | Cant. (5 + 1) | A comprar | USD a 10 u | Motivo |
|---|---|---|---|---|---|---|---|---|
| F101 | SF-2410FPA200W-2 | Bourns | DigiKey/Mouser | — | 6 | 6 | 1.0524 (ref. LCSC) | JLC/LCSC stock 0; sustituto AEM MF2410 rechazado (proteccion de entrada, el prototipo valida el diseno de produccion) |
| J1 | 1777109 | Phoenix Contact | LCSC | C7164734 | 6 | 6 | 0.9724 | THT |
| J2 | 1777073 | Phoenix Contact | LCSC | C480552 | 6 | 6 | 1.1001 | THT |
| J401 | USB4105-GF-A | GCT | LCSC | C3020560 | 6 | 6 | 1.1001 | THT |
| J402 | 2.54-1*3PPin | BOOMELE | LCSC | C49257 | 6 | 20 | 0.0286 (MOQ 20) | THT |
| L201 | XAL6060-333MEC | Coilcraft | DigiKey/Mouser | — | 6 | 6 | 2.8281 (ref. LCSC) | JLC/LCSC stock 0; sin equivalente 33uH en la misma huella |
| Q101 | STD18NF25 | STMicroelectronics | DigiKey/Mouser | — | 6 | 6 | 5.3743 (ref. LCSC) | JLC/LCSC stock 0; sustituto AOD458 rechazado (proteccion de entrada) |
| Q102 | IPD30N10S3L34ATMA1 | Infineon | DigiKey/Mouser | — | 6 | 6 | 1.2069 (ref. LCSC) | JLC/LCSC stock 0; sustituto IRLR3110Z rechazado (proteccion de entrada) |
| U401 | ESP32-S3-WROOM-1-N8R2 | Espressif Systems | LCSC | C2913204 | 6 | 6 | 4.0407 | modulo castellado, soldar a mano |
| U503 | AS5147U-HTSM | ams OSRAM | DigiKey/Mouser | — | 6 | 6 | 10.8657 (ref. LCSC) | JLC/LCSC stock 0 |

Carrito de lcsc.com (solo las líneas de LCSC de la lista 2): `bom/LCSC_CART_PROTO.csv`, **USD 51.18**. DigiKey/Mouser: `bom/DIGIKEY_MOUSER.csv` (columna `Uso`: «PROTO mano + PROD» o «PROD»), con enlaces de búsqueda.

## Antes de subir a JLC
1. Subir `fab/proto/bom_jlc_lcsc.csv` con `fab/proto/cpl_jlc.csv`. F101, Q101, Q102, L201 y U503 ya no están en ninguno de los dos. **Ojo:** si se vuelve a correr `scripts/ruteo/etapa6_fab.py`, regenera `cpl_jlc.csv` con esas cinco piezas. Antes de regenerar, hay que agregarlas a su lista de piezas a mano (pendiente en `PENDIENTES.md`).
2. Revisar en la vista previa las rotaciones pendientes (ver `PENDIENTES.md`).
3. U601 ADM3055EBRIZ-RL: JLC tiene 55 u. Hacer el pedido antes de que se agote.

## Costo de componentes por placa (USD), recalculado
Supuestos: precio de lcsc.com en el escalón de (cantidad por placa × N placas); sin repuestos ni sobrante por MOQ; sin cargos de JLC (armado, stencil, cargo por cada extended distinto, ensamblado de dos caras) ni envío; DigiKey/Mouser al precio de referencia de LCSC.

| Variante | 5 placas | 100 placas | JLC (5 / 100) | LCSC a mano (5 / 100) | DigiKey/Mouser (5 / 100) |
|---|---|---|---|---|---|
| PROTO (133 piezas, 70 líneas) | **111.48** | **90.88** | 80.06 / 64.87 | 8.46 / 5.92 | 22.95 / 20.09 |
| PROD (138 piezas, 71 líneas) | **107.84 +** | **89.62 +** | 51.31 / 44.08 | 8.46 / 5.92 | 48.07 / 39.61 |

`+`: falta U701/U751 (SN74AHCT1G126QDBVRQ1), sin precio en JLC/LCSC. Frente a la primera versión: PROTO +6.72 / +5.56 (originales de Q101, Q102 y F101) y PROD +8.39 / +6.56 (además, C101, C201 y C104 AEC-Q200). Lo más caro por placa: SCL3300 (~27), ADM3055E (~15–25), AS5147U (~11), LM74930 (~5.8), STD18NF25 (~5.4) y ESP32-S3 (~4–4.6).

## PROD (100 placas): diferencias con PROTO
- Usa `MPN` (versiones -Q1) en vez de `MPN_PROTO`: Q701/Q751 DMN10H220LQ-7 (C5260572, en stock), U201, U701/U751 y U801.
- C101, C201 y C104 mantienen los AEC-Q200 originales.
- Sin stock en JLC/LCSC para 100 placas, a DigiKey/Mouser (en consigna a JLC o soldados a mano): F101, Q101, Q102, L201, U503, C101, C104, C105, C201, U201, U601, U701/U751 y U801.
- Se montan D703/D753, R708–R710, R758–R760 y C105; no se montan D801, D802, R803 ni R804.
- Los pasivos a Basic y los sustitutos de igual especificación (aceptados) valen también para PROD.

## Sustitutos solo para la compra en lcsc.com (`bom/LCSC_BOM_COMPLETO_PROTO.csv`)
Los originales tienen stock en JLC (allí siguen montándose), pero 0 en lcsc.com (consulta 2026-10-30). Mismos huella 0603, dieléctrico, tensión y tolerancia. No cambian el esquemático, el PCB, `bom/BOM_PROTO.csv` ni `fab/proto/bom_jlc_lcsc.csv`.

| Ref | Original (LCSC) | Sustituto (LCSC) | Especificación | Stock lcsc.com | Estado |
|---|---|---|---|---|---|
| C303 | CL10C100JB8NNNC (C1634), Samsung | CC0603JRNPO9BN100 (C106245), YAGEO | 10 pF 50 V C0G/NP0 ±5 % 0603 | 4 768 800 | substitute CC0603JRNPO9BN100 for CL10C100JB8NNNC (lcsc.com only), VERIFY, 2026-10-30 |
| C601, C607 | 0603B103K500NT (C57112), FH | CC0603KRX7R9BB103 (C100042), YAGEO | 10 nF 50 V X7R ±10 % 0603 | 4 000 | substitute CC0603KRX7R9BB103 for 0603B103K500NT (lcsc.com only), VERIFY, 2026-10-30 |

## Archivos
- `fab/proto/bom_jlc_lcsc.csv` + `fab/proto/cpl_jlc.csv`: lo que monta JLC.
- `bom/A_MANO_PROTO.csv`: lo que se suelda a mano, con proveedor y cantidad.
- `bom/LCSC_CART_PROTO.csv`: carrito de lcsc.com (formato de su BOM tool: «LCSC Part Number», «Quantity»).
- `bom/LCSC_BOM_COMPLETO_PROTO.csv`: todo lo de PROTO que está en LCSC (sin DNP ni DigiKey/Mouser), para «Upload a BOM» de lcsc.com. Cantidad = por placa × 6, mínimo 20 en pasivos 0402/0603, subida al MOQ y al múltiplo de lcsc.com. Se regenera con `scripts/bom/lcsc_bom_completo.py` (consulta en vivo).
- `bom/DIGIKEY_MOUSER.csv`: PROTO a mano y PROD sin stock en JLC/LCSC.
- `bom/BOM_PROTO.csv`, `bom/BOM_PROD.csv`: BOM completa por variante, con LCSC, tipo, stocks, precio, montaje, estado y MPN/LCSC original.

## Tabla completa — PROTO
| Ref | Valor | Huella | Cant | MPN elegido | LCSC | Tipo JLC | Stock JLC | Stock LCSC | USD a 10 u | Montaje | Estado | Original (MPN / LCSC) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C101 | 100nF | C_1206_3216Metric | 1 | C1206X104K451T | C106025 | ext | 733 | 730 | 0.0671 | JLC | substitute C1206X104K451T for CGA5L4X7T2W104K160AA accepted 2026-10-30, JLC ext | CGA5L4X7T2W104K160AA / C3887150 |
| C102, C103 | 1uF | C_1206_3216Metric | 2 | CL31B105KCHNNNE | C13832 | ext | 347728 | 261400 | 0.0650 | JLC | substitute CL31B105KCHNNNE for CGA5L2X7R2A105K160AA accepted 2026-10-30, JLC ext | CGA5L2X7R2A105K160AA / C2168321 |
| C104 | 47uF | CP_Elec_10x10 | 1 | VZH470M2ATR-1010 | C164068 | ext | 1333 | 1330 | 0.2972 | JLC | substitute VZH470M2ATR-1010 for EEE-HA2A470UP accepted 2026-10-30, JLC ext | EEE-HA2A470UP / C344077 |
| C106 | 10uF | C_1210_3225Metric | 1 | CL32B106KBJNNNE | C138687 | ext | 101468 | 9473 | 0.2610 | JLC | substitute CL32B106KBJNNNE for GCM32ER71H106KA12L accepted 2026-10-30, JLC ext | GCM32ER71H106KA12L |
| C107, C108, C109, C202, C203, C302, C309, C310, C402, C404, C501, C502, C503, C504, C505, C506, C507, C602, C604, C608, C702, C752, C801 | 100nF | C_0603_1608Metric | 23 | 0603B104K101NT | C88219 | ext | 1825125 | 1684850 | 0.0117 (MOQ 50) | JLC | consolidado 2026-10-30: un solo MPN de 100 nF, 100 V X7R (PROTO, sin AEC-Q200) | GCM188R72A104KA64D / C415406 |
| C110 | 68nF | C_0603_1608Metric | 1 | CL10B683KB8NNNC | C31658 | pref | 150525 | 115600 | 0.0190 (MOQ 50) | JLC | substitute CL10B683KB8NNNC for GCM188R71H683KA57D accepted 2026-10-30, JLC pref | GCM188R71H683KA57D / C380380 |
| C201 | 4.7uF | C_1210_3225Metric | 1 | CL32B475KCVZNWE | C17288249 | ext | 435 | 435 | 1.0782 | JLC | substitute CL32B475KCVZNWE for CGA6M3X7S2A475K200AB accepted 2026-10-30, JLC ext | CGA6M3X7S2A475K200AB / C2168848 |
| C204, C205, C206 | 22uF | C_1206_3216Metric | 3 | GCM31CR71A226KE02L | C126598 | ext | 13053 | 11240 | 0.3296 | JLC | JLC ext, verified 2026-10-30 |  |
| C301, C508, C603, C605, C606 | 10uF | C_0805_2012Metric | 5 | CL21B106KAYQNNE | C3039694 | ext | 239941 | 126510 | 0.1051 | JLC | consolidado 2026-10-30: 25 V X7R (PROTO, sin AEC-Q200) | GCM21BR71A106KE22L / C126586 |
| C303 | 10pF | C_0603_1608Metric | 1 | CL10C100JB8NNNC | C1634 | basic | 1212785 | 100 | 0.0061 (MOQ 100) | JLC | JLC basic (swap from GCM1885C1H100JA16D), verified 2026-10-30 | GCM1885C1H100JA16D / C126542 |
| C304, C401 | 22uF | C_0805_2012Metric | 2 | GRM21BZ71A226ME15L | C907991 | ext | 166294 | 140195 | 0.3744 | JLC | JLC ext, verified 2026-10-30 |  |
| C306, C307, C403 | 1uF | C_0603_1608Metric | 3 | CC0603KRX7R9BB105 | C559769 | ext | 844148 | 700160 | 0.0569 (MOQ 20) | JLC | consolidado 2026-10-30: 50 V X7R (PROTO, sin AEC-Q200) | GCM188R71C105KA64D / C161212 |
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
| F101 | 2A 250VDC | Fuse_Bourns_SF-2410 | 1 | SF-2410FPA200W-2 | — | — | — | — | 1.0524 (ref. LCSC) | mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C3159902 |
| FB301 | 220R@100MHz | L_0603_1608Metric | 1 | BLM18PG221SN1D | C80165 | ext | 243305 | 235750 | 0.0149 (MOQ 50) | JLC | JLC ext, verified 2026-10-30 |  |
| FB601, FB602 | 1.8k@100MHz | L_0603_1608Metric | 2 | BLM18BD182SN1D | C113020 | ext | 5170 | 5160 | 0.0362 (MOQ 20) | JLC | JLC ext, verified 2026-10-30 |  |
| J1 | MSTBV 2,5/5-GF-5,08 | PhoenixContact_MSTBV_2,5_5-G | 1 | 1777109 | C7164734 | ext | 327 | 317 | 0.9724 | mano | JLC ext, verified 2026-10-30 |  |
| J2 | MSTBV 2,5/2-GF-5,08 | PhoenixContact_MSTBV_2,5_2-G | 1 | 1777073 | C480552 | ext | 837 | 835 | 1.1001 | mano | JLC ext, verified 2026-10-30 |  |
| J401 | USB4105-GF-A | USB_C_Receptacle_GCT_USB4105 | 1 | USB4105-GF-A | C3020560 | ext | 3189 | 413 | 1.1001 | mano | JLC ext, verified 2026-10-30 |  |
| J402 | UART0 | PinHeader_1x03_P2.54mm_Verti | 1 | 2.54-1*3PPin | C49257 | ext | 151423 | 151440 | 0.0286 (MOQ 20) | mano | substitute 2.54-1*3PPin for 61300311121 accepted 2026-10-30, JLC ext | 61300311121 / C2915006 |
| L101 | 10uH | L_Bourns_SRN6045TA | 1 | SRN6045TA-100M | C2046332 | ext | 6156 | 6045 | 0.2544 | JLC | JLC ext, verified 2026-10-30 |  |
| L201 | 33uH | L_Coilcraft_XAL6060-XXX | 1 | XAL6060-333MEC | — | — | — | — | 2.8281 (ref. LCSC) | mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C5119929 |
| L301 | 1uH | L_Coilcraft_XAL4020_HandSold | 1 | XAL4020-102MEC | C4555951 | ext | 7626 | 7626 | 4.2523 | JLC | JLC ext, verified 2026-10-30 |  |
| Q101 | STD18NF25 | TO-252-2 | 1 | STD18NF25 | — | — | — | — | 5.3743 (ref. LCSC) | mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C183634 |
| Q102 | IPD30N10S3L-34 | TO-252-2 | 1 | IPD30N10S3L34ATMA1 | — | — | — | — | 1.2069 (ref. LCSC) | mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C148263 |
| Q701, Q751 | DMN10H220LQ | SOT-23 | 2 | DMN10H220L-7 | C102615 | ext | 16334 | 16330 | 0.3319 | JLC | JLC ext, verified 2026-10-30 |  |
| R102 | 10k | R_2512_6332Metric | 1 | AC2512FK-0710KL | C469651 | ext | 1508 | 1505 | 0.0933 | JLC | JLC ext, verified 2026-10-30 |  |
| R103 | 10m | R_1206_3216Metric | 1 | ERJ-8BWFR010V | C2076185 | ext | 5332 | 4125 | 0.1219 | JLC | JLC ext, verified 2026-10-30 |  |
| R104 | 49.9 | R_0603_1608Metric | 1 | 0603WAF499JT5E | C23185 | basic | 1388908 | 411400 | 0.0021 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-0749R9L), verified 2026-10-30 | AC0603FR-0749R9L / C144653 |
| R105 | 100 | R_0603_1608Metric | 1 | 0603WAF1000T5E | C22775 | basic | 9522722 | 1107900 | 0.0024 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-07100RL), verified 2026-10-30 | AC0603FR-07100RL / C125923 |
| R106, R201, R301, R302, R304, R305, R307, R308, R703, R711, R753, R761 | 100k | R_0603_1608Metric | 12 | 0603WAF1003T5E | C25803 | basic | 17755977 | 8896900 | 0.0030 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-07100KL), verified 2026-10-30 | AC0603FR-07100KL / C116674 |
| R107 | 9.31k | R_0603_1608Metric | 1 | AC0603FR-079K31L | C144630 | ext | 6619 | 6600 | 0.0058 (MOQ 100) | JLC | JLC ext, verified 2026-10-30 |  |
| R108, R112 | 51k | R_1206_3216Metric | 2 | RC1206FR-0751KL | C114947 | ext | 140795 | 131250 | 0.0113 (MOQ 50) | JLC | substitute RC1206FR-0751KL for AC1206FR-0751KL accepted 2026-10-30, JLC ext | AC1206FR-0751KL / C144484 |
| R109 | 1.62k | R_0603_1608Metric | 1 | CR0603FA1621G | C100797 | ext | 1100 | 1100 | 0.0014 (MOQ 100) | JLC | substitute CR0603FA1621G for AC0603FR-071K62L accepted 2026-10-30, JLC ext | AC0603FR-071K62L / C227657 |
| R110 | 60.4k | R_0603_1608Metric | 1 | RC0603FR-0760K4L | C165742 | ext | 48563 | 48500 | 0.0062 (MOQ 100) | JLC | substitute RC0603FR-0760K4L for AC0603FR-0760K4L accepted 2026-10-30, JLC ext | AC0603FR-0760K4L / C227994 |
| R111, R401, R402, R501, R502, R503, R601, R604 | 10k | R_0603_1608Metric | 8 | 0603WAF1002T5E | C25804 | basic | 40290635 | 1435400 | 0.0022 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-0710KL), verified 2026-10-30 | AC0603FR-0710KL / C116677 |
| R202 | 24.9k | R_0603_1608Metric | 1 | AC0603FR-0724K9L | C227732 | ext | 3945 | 3900 | 0.0064 (MOQ 100) | JLC | JLC ext, verified 2026-10-30 |  |
| R203 | 64.9k | R_0603_1608Metric | 1 | AC0603FR-0764K9L | C228007 | ext | 920 | 900 | 0.0042 (MOQ 100) | JLC | JLC ext, verified 2026-10-30 |  |
| R303 | 453k | R_0603_1608Metric | 1 | CR0603FA4533G | C101055 | ext | 4984 | 4950 | 0.0093 (MOQ 50) | JLC | substitute CR0603FA4533G for AC0603FR-07453KL accepted 2026-10-30, JLC ext | AC0603FR-07453KL / C227908 |
| R306 | 49.9k | R_0603_1608Metric | 1 | 0603WAF4992T5E | C23184 | basic | 1532153 | 1273400 | 0.0029 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-0749K9L), verified 2026-10-30 | AC0603FR-0749K9L / C144654 |
| R403, R404 | 5.1k | R_0603_1608Metric | 2 | 0603WAF5101T5E | C23186 | basic | 21368680 | 16397700 | 0.0016 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-075K1L), verified 2026-10-30 | AC0603FR-075K1L / C125891 |
| R602, R603 | 60.4 | R_0603_1608Metric | 2 | AC0603FR-0760R4L | C144645 | ext | 14047 | 14000 | 0.0069 (MOQ 100) | JLC | JLC ext, verified 2026-10-30 |  |
| R605, R802, R805, R806 | 0 | R_0603_1608Metric | 4 | 0603WAF0000T5E | C21189 | basic | 20896231 | 11816300 | 0.0022 (MOQ 100) | JLC | JLC basic (swap from AC0603JR-070RL), verified 2026-10-30 | AC0603JR-070RL / C141796 |
| R702, R752, R803, R804 | 2.2k | R_0603_1608Metric | 4 | 0603WAF2201T5E | C4190 | basic | 5498979 | 2790900 | 0.0018 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-072K2L), verified 2026-10-30; R803/R804 antes 470 Ω (LED ~0.6–0.7 mA); R702/R752 antes 4k7 (consolidación) | AC0603FR-072K2L / C125931 |
| SW401 | RESET | SW-SMD_L3.9-W3.0-P4.45 | 1 | TS-1088-AR02016 | C720477 | basic | 605935 | 363750 | 0.0533 | JLC | JLC basic, verified 2026-10-30 |  |
| SW402 | BOOT | SW-SMD_L3.9-W3.0-P4.45 | 1 | TS-1088-AR02016 | C720477 | basic | 605935 | 363750 | 0.0533 | JLC | JLC basic, verified 2026-10-30 |  |
| U101 | LM74930QRGERQ1 | TI_RGE0024T_VQFN-24-1EP_4x4m | 1 | LM74930QRGERQ1 | C22428070 | ext | 7308 | 7127 | 5.7664 | JLC | JLC ext, verified 2026-10-30 |  |
| U201 | LMR38010SQDDARQ1 | SOIC-8-1EP_3.9x4.9mm_P1.27mm | 1 | LMR38010SDDAR | C5219310 | ext | 2650 | 2650 | 0.7324 | JLC | JLC ext, verified 2026-10-30 |  |
| U301 | TPS62A02QDRLRQ1 | SOT-563 | 1 | TPS62A02QDRLRQ1 | C49259289 | ext | 190 | 190 | 0.5093 | JLC | JLC ext, verified 2026-10-30 |  |
| U302 | LP5907QMFX-3.3Q1 | SOT-23-5 | 1 | LP5907QMFX-3.3Q1 | C130005 | ext | 3282 | 2994 | 0.7792 | JLC | JLC ext, verified 2026-10-30 |  |
| U401 | ESP32-S3-WROOM-1-N8R2 | ESP32-S3-WROOM-1 | 1 | ESP32-S3-WROOM-1-N8R2 | C2913204 | ext | 18179 | 7131 | 4.0407 | mano | JLC ext, verified 2026-10-30 |  |
| U402 | USBLC6-2SC6 | SOT-23-6 | 1 | USBLC6-2SC6 | C2687116 | ext | 119890 | 119900 | 0.0482 | JLC | JLC ext, verified 2026-10-30 |  |
| U501 | SCL3300-D01 | DFL-12_L8.6-W7.0-P1.00-LS7.6 | 1 | SCL3300-D01-10 | C3825395 | ext | 721 | 721 | 27.9106 | JLC | substitute SCL3300-D01-10 for SCL3300-D01 accepted 2026-10-30, JLC ext | SCL3300-D01 / C22416657 |
| U502 | ASM330LHHTR | LGA-14_3x2.5mm_P0.5mm_Layout | 1 | ASM330LHHTR | C459826 | ext | 7766 | 7527 | 4.6845 | JLC | JLC ext, verified 2026-10-30 |  |
| U503 | AS5147U-HTSM | TSSOP-14_4.4x5mm_P0.65mm | 1 | AS5147U-HTSM | — | — | — | — | 10.8657 (ref. LCSC) | mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C2153628 |
| U601 | ADM3055E | SOIC-20W_7.5x12.8mm_P1.27mm | 1 | ADM3055EBRIZ-RL | C658105 | ext | 55 | 55 | 24.4771 | JLC | substitute ADM3055EBRIZ-RL for ADM3055EBRIZ accepted 2026-10-30, JLC ext | ADM3055EBRIZ / C658104 |
| U701, U751 | 74AHCT1G126 | SOT-23-5 | 2 | SN74AHCT1G126DBVR | C163712 | ext | 8462 | 8055 | 0.0949 | JLC | JLC ext, verified 2026-10-30 |  |
| U801 | TPS3828-33Q1 | SOT-23-5 | 1 | TPS3828-33DBVR | C20032 | ext | 49770 | 49770 | 0.3771 | JLC | JLC ext, verified 2026-10-30 |  |


## Tabla — PROD (solo las líneas que cambian respecto de PROTO)

Fuera de PROD: D801, D802, R803, R804 (DNP PROD). El resto es igual que en PROTO; la BOM completa está en `bom/BOM_PROD.csv`.

| Ref | Valor | Huella | Cant | MPN elegido | LCSC | Tipo JLC | Stock JLC | Stock LCSC | USD a 10 u | Montaje | Estado | Original (MPN / LCSC) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C101 | 100nF | C_1206_3216Metric | 1 | CGA5L4X7T2W104K160AA | — | — | — | — | 0.7901 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C3887150 |
| C104 | 47uF | CP_Elec_10x10 | 1 | EEE-HA2A470UP | — | — | — | — | 0.3957 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C344077 |
| C105 | 1000uF 50V | CP_Elec_Panasonic_J16_VibPro | 1 | EEE-FK1H102AV | — | — | — | — | 0.8694 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C2164039 |
| C107, C108, C109, C202, C203, C302, C309, C310, C402, C404, C501–C507, C602, C604, C608, C702, C752, C801 | 100nF | C_0603_1608Metric | 23 | GCM188R72A104KA64D | C415406 | ext | 15215 | 10480 | 0.0637 | JLC | consolidado 2026-10-30: un solo MPN de 100 nF, 100 V X7R AEC-Q200 (PROTO: FH 0603B104K101NT) |  |
| C201 | 4.7uF | C_1210_3225Metric | 1 | CGA6M3X7S2A475K200AB | — | — | — | — | 1.5766 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C2168848 |
| C301, C508, C603, C605, C606 | 10uF | C_0805_2012Metric | 5 | GCM21BR71A106KE22L | C126586 | ext | 9971 | 0 | 0.1029 | JLC | PROD conserva el AEC-Q200 (PROTO: Samsung CL21B106KAYQNNE) |  |
| C306, C307, C403 | 1uF | C_0603_1608Metric | 3 | GCM188R71C105KA64D | C161212 | ext | 33722 | 18280 | 0.0383 (MOQ 20) | JLC | PROD conserva el AEC-Q200 (PROTO: Yageo CC0603KRX7R9BB105) |  |
| R702, R752 | 2.2k | R_0603_1608Metric | 2 | 0603WAF2201T5E | C4190 | basic | 5498979 | 2790900 | 0.0018 (MOQ 100) | JLC | consolidado 2026-10-30 desde 4k7 (en PROTO comparte línea con R803/R804) | AC0603FR-072K2L / C125931 |
| D703, D753 | BZX84-C3V3 | SOT-23 | 2 | BZX84-C3V3,215 | C85087 | ext | 28154 | 28150 | 0.0180 (MOQ 50) | JLC | JLC ext, verified 2026-10-30 |  |
| Q701, Q751 | DMN10H220LQ | SOT-23 | 2 | DMN10H220LQ-7 | C5260572 | ext | 4738 | 4595 | 0.2997 | JLC | JLC ext, verified 2026-10-30 |  |
| R708, R709, R758, R759 | 100k | R_1206_3216Metric | 4 | 1206W4F1003T5E | C17900 | basic | 937779 | 315500 | 0.0097 (MOQ 50) | JLC | JLC basic (swap from AC1206FR-07100KL), verified 2026-10-30 | AC1206FR-07100KL / C144522 |
| R710, R760 | 220k | R_0603_1608Metric | 2 | 0603WAF2203T5E | C22961 | basic | 1137879 | 809400 | 0.0015 (MOQ 100) | JLC | JLC basic (swap from AC0603FR-07220KL), verified 2026-10-30 | AC0603FR-07220KL / C144681 |
| U201 | LMR38010SQDDARQ1 | SOIC-8-1EP_3.9x4.9mm_P1.27mm | 1 | LMR38010SQDDARQ1 | — | — | — | — | 2.7991 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C18198885 |
| U601 | ADM3055E | SOIC-20W_7.5x12.8mm_P1.27mm | 1 | ADM3055EBRIZ | — | — | — | — | 15.3791 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C658104 |
| U701, U751 | 74AHCT1G126 | SOT-23-5 | 2 | SN74AHCT1G126QDBVRQ1 | — | — | — | — | s/d | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 |  |
| U801 | TPS3828-33Q1 | SOT-23-5 | 1 | TPS3828-33QDBVRQ1 | — | — | — | — | 1.4158 (ref. LCSC) | consigna JLC o mano | not at JLC, DigiKey/Mouser, checked 2026-10-30 | C2872895 |
