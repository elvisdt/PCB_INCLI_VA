# INCLI-VA — estado y pendientes

Leer al empezar cada turno y actualizar al terminarlo (ver "Trabajo entre agentes" en `AGENTS.md`).

Última actualización: 2026-10-27, Claude Code (PCB actualizado por el usuario, J1/J2 confirmados en Phoenix, regla para J401, DRC).

## Criterio general (decisión del usuario, 2026-10-27)
- **El prototipo es el mismo diseño que irá a producción.** Entre prototipo y producción solo cambia qué se monta.
- Requisitos de producción: vehículos de 12 V y 24 V, chasis con vibración, transitorios ISO 7637-2 / ISO 16750-2 y CAN robusto.
- Lo opcional va con huella en la placa y marcado DNP. La placa funciona igual con o sin esas piezas (0 Ω donde haga falta).
- **Campo `DNP`** en todos los símbolos, para sacar los dos BOM del mismo esquemático:
  - vacío: se monta en prototipo y en producción.
  - `PROTO`: no se monta en el prototipo (sí en producción).
  - `PROD`: no se monta en producción.
  - `PROTO,PROD`: huella reservada; no se monta en ninguno.
  - El atributo nativo `dnp` de KiCad refleja el BOM de prototipo (`dnp yes` si el campo contiene `PROTO`).
  - Las variantes (CAN, OUT, ROT, CABIN) siguen en el campo `Variant`; no se mezclan con `DNP`.

## Decisiones del usuario (2026-10-27)
1. **Load dump:** se diseña para load dump **suprimido** (ISO 16750-2 prueba B; 24 V: ≤ 58 V). Se mantiene el TVS de entrada D102 para ISO 7637 (pulso 1).
   - **Sin TVS de entrada grande** (decisión final del usuario): la entrada ya bloquea 202 V (Q101 250 V, D101 400 V, C101 450 V). Detalle en "Máximos de la entrada".
2. **R109 queda en 1.62 k** (corte por OV a 38.4 V). Decisión final del usuario: con el buck de 80 V ya no hace falta bajarlo.
3. **Opción B, no aislada: aprobada.** Se quitan PS201, U202 (ISO7763) y U201 (TPS7A1650), y entra un buck de +VPROT a 5 V. El aislamiento queda solo en el CAN (ADM3055E).
   - **Buck: TI LMR38010SQDDARQ1** (80 V, 1 A, PFM + spread spectrum, AEC-Q100, HSOIC-8 PowerPAD DDA). El usuario confirma el stock.
   - **Prototipo: LMR38010SDDAR** (LCSC C5219310), equivalente comercial. En el símbolo: `MPN = LMR38010SQDDARQ1` (PROD) y `MPN_PROTO = LMR38010SDDAR` (ver "Equivalencia LMR38010").
   - Si la producción termina en JLCPCB, se revisa la disponibilidad más adelante.
   - Huella: pad expuesto con vías térmicas, soldable con aire caliente.
8. **C105:** DNP en PROTO y montado en PROD (hold-up para load dump y arranque en frío). De acuerdo, con dos condiciones (ver "Hoja 20: diseño listo").
4. **60_can: aprobado y aplicado** (ver "Hecho en este turno").
5. **DO mínima: aprobada y aplicada.** El latch y el diagnóstico quedan como huellas DNP.
6. **J1 y J2:** Phoenix MSTB 2,5 de 5.08 mm con brida roscada (GF). **Aplicado.**
7. **C105:** reemplazada por la decisión 8.

## Hecho en este turno (2026-10-27)
- **`60_can`** (ADM3055E, datasheet ADI Rev. D, tablas 10 y 12):
  - FB602 estaba en corto (sus dos pines en GND_CAN). Ahora GNDISO (pines 18 y 20) va a GND2 a través de FB602, como pide el datasheet.
  - Desacople corregido según la tabla 10:
    - VISOOUT: C610 de 0.22 µF + C606 de 10 µF a GNDISO.
    - El 10 µF que estaba en VISOIN (C11) pasó a VISOOUT.
    - Se quitó el 10 µF duplicado en VCC (C6).
  - **C601 y C607 (0.01 µF) se mantienen**, aunque se había aprobado quitarlos: el datasheet los exige en VIO y VISOIN ("requires 0.01 µF and 0.1 µF").
  - RS (pin 12) → R605 de 0 Ω a GND2: velocidad completa. Con 47 k pasa a control de pendiente.
  - AUXIN (pin 9) → GND1, porque es una entrada sin uso. AUXOUT (pin 17) sin conexión.
  - STBY: pull-up R604 de 10 k a +3V3_D. STBY y SILENT tienen pull-down interno; con R604 el transceiver arranca en standby.
  - D601 ESD2CAN24-Q1 (SOT-23) en CANH/CANL, DNP en prototipo y en producción. Símbolo genérico `D_TVS_Dual_AAC`, pin 3 = GND.
  - Referencias renumeradas a 6xx. Footprint, MPN, Manufacturer, Datasheet y Notes completos en los 18 componentes.
  - Los símbolos de potencia `power:VCC` y `power:GND` con el Value editado se cambiaron por los de la librería `INCLI-VA`.
  - PWR_FLAG en V_SOIN (alimentado por VISOOUT a través de FB601).
- **`70_output`** (DO1 y DO2), diseñado para load dump suprimido:
  - Q701: FDD7N25LZ (250 V, DPAK) → **DMN10H220LQ-7** (100 V, SOT-23, AEC-Q101).
  - D701: SMCJ188A → **SMAJ58A**. No conduce con 58 V; recorta el pico inductivo a ≤ 93.6 V, por debajo de los 100 V de Q701.
  - **U701 74AHCT1G126** (nuevo): lleva EN de 3.3 V (MCU) a EN_5V, porque el DMN10H220LQ especifica su RDS a 4.5 V. R711 de 100 k es el pull-down de la entrada. C702 desacopla.
  - **D704** (nuevo): zener de 12 V, MMSZ5242B, como protección de gate (VGS máx ±16 V).
  - Latch de sobrecorriente (Q702, Q703, D702, R704–R707, C701): `DNP = PROTO,PROD` hasta validar el disparo (REVISION_CODEX I1). R701 (1 Ω) se monta igual.
  - Diagnóstico (R708–R710, D703): `DNP = PROTO`. D703 pasa a BZX84-C3V3 porque DIAG irá directo a un GPIO del ESP32.
  - **Limitación:** en vehículos sin supresión de load dump, las salidas DO no quedan protegidas. Con 202 V a través de la bobina, D701 tendría que absorber ~8 J.
- **`10_power_input`:**
  - J1 y J2 con huellas MSTB 2,5 de 5.08 mm GF. J2 = 1776508.
  - F101 = Bourns SF-2410FPA200W-2: 2 A, 250 VDC, AEC-Q200, LCSC C3159902.
  - C105 queda con `DNP = PROTO,PROD`. Es un hold-up opcional:
    - Mantiene la lógica durante el corte por OV del LM74930 (load dump de 24 V, ≤ 350 ms) y durante los huecos de arranque en frío de 12 V (4.5–6 V, 15–40 ms).
    - No hace falta para los pulsos ISO 7637.
    - Sin C105, la placa se reinicia en esos eventos (estado funcional C).
  - Se quitó un PWR_FLAG suelto en GND_CAN (#FLG125 + #PWR126), que chocaba con GND2 del ADM3055E.
- **Campo `DNP`** agregado a todos los símbolos del proyecto. D401 (opción de banco) = `PROTO,PROD`.

## Máximos de la entrada (load dump suprimido, 24 V)
Pulsos según ISO 7637-2 (anexo A, 24 V): pulso 1 −600 V / 50 Ω; 2a hasta +112 V / 2 Ω / 50 µs; 3a/3b ±300 V / 50 Ω / 0.15 µs. Load dump suprimido de ISO 16750-2: 58 V durante ≤ 350 ms. Hay que verificar los niveles con la edición de la norma que pida el cliente.

| Componente | Máximo que ve | Valor nominal | Condición |
|---|---|---|---|
| F101, J1, VBAT_F | +58 V / ~+140 V (50 µs) / −55 V | 250 VDC | load dump / pulso 2a sobre 28 V / pulso 1 recortado |
| C101 | ~140 V | 450 V | pulso 2a |
| Q101 (VDS) | ~140 V | 250 V | apagado por OV durante 2a; 58 V en el load dump |
| D101 ES2G (inversa) | ~140 V | 400 V | pulso 2a |
| D102 SMCJ33A | ~11 A, VC ~53 V | Ipp 28 A | pulso 1 |
| R102 10 k (2512) | 0.64 W durante 50 µs; ~0 W en el load dump | — | D103 casi no conduce a 58 V |
| D103 SMAJ51A (VS) | recorta a 57–63 V | VS máx. abs. 70 V | pulso 2a |
| R108, R112 51 k (1206) | ~70 V cada una | 200 V | pulso 2a |
| Q102 (VDS) | ~85 V | 100 V | pulso 1 (VOUT + recorte) |
| +VPROT y lo que cuelga de él | ≤ umbral de OV (38.4 o 34.2 V) | C106 de 50 V | corte del LM74930 |

- Con load dump **sin suprimir** (202 V), la entrada sigue dentro de valores (Q101 250 V, D101 400 V, C101 450 V, R108/R112 ~101 V).
- La única duda abierta con 202 V es la sobrecarga de pulso de R102: 2 W durante 350 ms (REVISION_CODEX I2).

## Limitaciones conocidas
- **Salidas DO1/DO2 con load dump sin suprimir (24 V, 202 V): no quedan protegidas.**
  - La bobina del relé externo queda conectada a la batería. Con Q701 apagado, el drenador sigue a la batería.
  - D701 (SMAJ58A) tendría que absorber ~8 J (≈ 0.34 A × 66 V × 350 ms) y fallaría en corto, lo que deja el relé activado.
  - Para esos vehículos haría falta un MOSFET de ≥ 250 V (otra huella) o supresión en el propio relé.
- El latch de sobrecorriente de las DO está como DNP: en el prototipo, un corto de la carga a +V no está limitado.

## Equivalencia LMR38010 (prototipo y producción)
Fuentes: TI SNVSC73B (LMR38010, sept. 2023), sección 5 "Device Comparison Table", y TI SNVSC72B (LMR38010-Q1), sección 4.

| Orderable | Datasheet | FPWM | Spread spectrum | Modo en carga liviana |
|---|---|---|---|---|
| LMR38010SDDAR (LCSC C5219310) | SNVSC73B | No | Sí | PFM |
| LMR38010FDDAR (LCSC C5219308) | SNVSC73B | Sí | No | PWM forzado |
| LMR38010FSDDAR (LCSC C5219309) | SNVSC73B | Sí | Sí | PWM forzado |
| **LMR38010SQDDARQ1** | SNVSC72B | No | Sí | PFM |
| LMR38010FSQDDARQ1 | SNVSC72B | Sí | Sí | PWM forzado |

- **F** = FPWM (PWM forzado: frecuencia fija también sin carga, más consumo). Sin F = PFM en carga liviana (IQ 40 µA, "PFM variant only").
- **S** = spread spectrum (±8 %, FSPREAD).
- **Q / Q1** = AEC-Q100.
- **LMR38010SDDAR ≡ LMR38010SQDDARQ1.** Coinciden en:
  - Modo (PFM + spread spectrum).
  - Pinout (1 GND, 2 EN, 3 VIN, 4 RT/SYNC, 5 FB, 6 PG, 7 BOOT, 8 SW, EP).
  - Encapsulado DDA0008B.
  - Parámetros revisados: VREF 1 V ±1.5 %, IHS-LIMIT 1.3/1.6/1.9 A, ILS-LIMIT 0.9/1.2/1.5 A, tON-MIN 80/131 ns, IPEAK-MIN 0.25 A, TJ −40 a 150 °C, RθJA 42.9 °C/W.
  - La única diferencia es la calificación AEC-Q100.
  - El -Q1 especifica FOSC con RT = 64.9 kΩ: 320/400/480 kHz. Es el RT elegido.
- No usar las variantes F en el prototipo: cambian el comportamiento en carga liviana (consumo con solo BLE) y no representan a producción.
- **Campo nuevo `MPN_PROTO`:** se usa solo cuando el prototipo lleva otro número de parte, equivalente al de producción. El BOM de prototipo toma `MPN_PROTO` si existe y, si no, `MPN`.

## Hoja 20 (`20_buck_5v`): aplicada (2026-10-27)
- Opción B aplicada en toda la jerarquía:
  - `sheets/20_isolation.kicad_sch` → `sheets/20_buck_5v.kicad_sch` (`git mv`), sin pines jerárquicos.
  - Se quitaron PS201, U202 (ISO7763), U201 (TPS7A1650) y sus pasivos.
  - U201 nuevo: LMR38010 con los componentes de la tabla de abajo.
  - Todas las hojas: GND_ISO → GND_VEH y +5V_ISO → +5V_VEH.
  - Raíz: DO1_EN, DO2_EN, DO1_DIAG, DO2_DIAG y PWR_FLT_N van directo entre las hojas 40, 70 y 10 (las etiquetas `VEH_*` de esas señales se renombraron).
  - Hoja 10: R111 → +3V3_D, C109 = 100 nF, C105 `DNP = PROTO`.
- **Símbolo U201:** `INCLI-VA_easyeda:LMR38010SDDAR` (easyeda2kicad, LCSC C5219310), registrado en `sym-lib-table`.
  - Coincide pin por pin con la tabla 6-1 del datasheet.
  - Ajustes sobre el import:
    - Tipos de pin: GND/VIN/EP power_in, EN/FB input, RT/BOOT passive, PG open_collector, SW output.
    - Huella → la oficial con vías térmicas.
    - Fabricante → "Texas Instruments".
- **Campos de U201:** `MPN = LMR38010SQDDARQ1`, `MPN_PROTO = LMR38010SDDAR`, `LCSC_PROTO = C5219310`.
- **Se quitó un PWR_FLAG suelto en GND_VEH** (#FLG123 + #PWR124, hoja 10): chocaba con GND1 del ADM3055E, ahora en la misma masa.
- **Textos actualizados** en las hojas 30, 40, 50 y 80 y en la raíz.
  - Hoja 40, J402/USB: ahora dice que no hay aislamiento. **En el vehículo, la PC comparte masa con la placa:** usar un aislador USB/UART o una laptop a batería.
- Los cambios de layout del usuario en `70_output_ch` (hechos en KiCad, 21:24) entran en el mismo commit.

**Huella:** `Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.95x4.9mm_Mask2.71x3.4mm_ThermalVias` (oficial). Comparada con el DDA0008B del datasheet:
- Cobre del EP: 2.95 × 4.9 mm. Máscara: 2.71 × 3.4 mm. Vías: 6 × 0.2 mm, igual que TI.
- Pads: 1.775 × 0.6 mm centrados a ±2.5625 mm; TI pide 1.55 × 0.6 mm a ±2.7 mm. El borde exterior es igual (~3.45 mm); los pads de la huella llegan 0.25 mm más hacia el centro. Sirve para soldar a mano.
- Con aire caliente: estañar el EP y calentar desde abajo; las vías dejan llegar el calor y el estaño.

**Componentes** (TI SNVSC73B, tablas 8-1 y 9-1, sección 9.2): +VPROT (6.5–38.4 V) → 5.02 V / 1 A a 400 kHz.

| Ref. | Valor | MPN | Notas |
|---|---|---|---|
| U201 | LMR38010SQDDARQ1 (PROD) / LMR38010SDDAR (PROTO, LCSC C5219310) | TI | EN y VIN → +VPROT; PG sin uso. Pin a pin con el LMR38020 (2 A) |
| C201 | 4.7 µF 100 V 1210 | CGA6M3X7S2A475K200AB (TDK) | C_IN (TI: ≥ 4.7 µF). A verificar |
| C202 | 100 nF 100 V 0603 | GCM188R72A104KA64D | Bypass de VIN, pegado a los pines 3 y 1 |
| C203 | 100 nF 0603 | GCM188R71H104KA57D | C_BOOT (pines 7 y 8) |
| L201 | 33 µH | XAL6060-333MEC (Coilcraft) | Isat 3.7 A > 1.9 A (límite HS máx.); DCR 105 mΩ; AEC-Q200; huella oficial `L_Coilcraft_XAL6060-XXX` |
| C204–C206 | 3 × 22 µF 10 V 1206 | GCM31CR71A226KE02L | C_OUT (TI: 3 × 22 µF a 5 V / 400 kHz). A verificar |
| R201 / R202 | 100 k / 24.9 k | AC0603FR-07100KL / AC0603FR-0724K9L | VOUT = 1 V × (1 + 100k/24.9k) = 5.02 V |
| R203 | 64.9 k | AC0603FR-0764K9L | RT → 400 kHz. Con D = 0.13 a 38.4 V, el tON es 325 ns > tON-min 131 ns |
| TP201 | +5V_VEH | — | Más un PWR_FLAG en +5V_VEH |

- Pico de carga en +5V_VEH: unos 0.7 A, sumando TPS62A02 (WiFi), ADM3055E (180–260 mA), LP5907 y los buffers.
- Disipación de U201: ~0.4 W, que con θJA de 42.9 °C/W da unos +17 °C.

**Cambios en las demás hojas al aplicar la opción B:**
- **Hoja 20:** se renombra a `20_buck_5v` (archivo y nombre de hoja) y se quitan todos sus pines jerárquicos.
- **Raíz:**
  - Etiquetas `VEH_DO1_EN`, `VEH_DO2_EN`, `VEH_DO1_DIAG`, `VEH_DO2_DIAG` y `VEH_PWR_FLT_N` → `DO1_EN`, `DO2_EN`, `DO1_DIAG`, `DO2_DIAG` y `PWR_FLT_N` (directo entre las hojas 40, 70 y 10).
  - Se quitan los cables y etiquetas de los pines de la hoja 20.
- **Todas las hojas:** GND_ISO → GND_VEH y +5V_ISO → +5V_VEH (símbolos, caché y textos).
- **Hoja 10:**
  - R111 (pull-up de FLT) pasa de +5V_VEH a +3V3_D.
  - **C109 (C_dVdT) pasa de 10 nF a 100 nF** (GCM188R72A104KA64D).
  - C105 queda con `DNP = PROTO`.

**C105 en producción: de acuerdo, con dos condiciones.**
1. **Inrush (obligatorio).** Con C105 montado, la capacidad en VOUT es ~1.07 mF. Con C109 en 10 nF: Iinrush = 1.07 mF × 55 µA / 10 nF ≈ **5.9 A**. El breaker (1 A, TMR ~1 ms con C110 de 68 nF) dispararía en cada arranque y la placa no encendería nunca.
   - Con C109 = 100 nF: 0.59 A con C105 y ~34 mA sin C105. Arranque de ~60 ms. Funciona igual con o sin C105.
2. **Mecánica y MPN.** Un electrolítico radial de 16 mm en un chasis con vibración necesita adhesivo (o un encapsulado con base antivibración) y ser automotriz (105–125 °C, AEC-Q200). El MPN sigue pendiente.
- Hold-up con 1000 µF (de 28 a 6 V): 0.37 J. Alcanza ~0.7 s a 0.5 W (solo BLE), suficiente para los 350 ms del load dump. Con WiFi a 1.5 W alcanza ~0.25 s.
- Arranque en frío de 12 V (de 12 a 6 V): 54 mJ, que dan ~36 ms a 1.5 W o ~108 ms a 0.5 W.

## Reglas de diseño (`INCLI-VA.kicad_dru`) y red del pad 25 (2026-10-27)
- **Fabricante: JLCPCB**, 2 capas, 1.6 mm, 1 oz. Fuente: https://jlcpcb.com/capabilities/pcb-capabilities (consultado el 2026-10-27).

  | Regla | Valor del proyecto | Mínimo de JLCPCB |
  |---|---|---|
  | Pista / espacio | 0.15 / 0.15 mm | 0.10 / 0.10 mm |
  | Vía | hueco 0.3 mm / Ø 0.6 mm | 0.15 mm (preferido 0.2 mm) |
  | Hueco de pad | ≥ 0.2 mm | — |
  | Anillo PTH (hueco > 0.35 mm) | 0.18 mm | 0.18 mm absoluto (0.25 recomendado) |
  | Hueco a hueco | 0.45 mm | 0.45 mm |
  | Hueco a cobre | vías 0.2 mm, PTH 0.28 mm | — |
  | Cobre a borde | 0.5 mm | 0.2 mm |
  | Serigrafía | texto ≥ 1.0 mm, trazo ≥ 0.15 mm | — |

  - El puente de máscara (0.10 mm) va en Board Setup; no se puede expresar en el `.kicad_dru`.
- **Reglas especiales:**
  - **HV de entrada:** VIN_VEH y VBAT_F → 1.25 mm al resto (IPC-2221B tabla 6-1, B2, 171–250 V; pad contra pad excluido).
  - **Salidas DO** (VEH_DO1/2) → 0.6 mm (B2, 51–100 V).
  - **+VPROT, VA, C_ID y VOUT** → 0.6 mm entre conductores (B2, 31–50 V); los pads quedan fuera porque U101 es QFN de 0.5 mm.
  - **Barrera del ADM3055E:** dominio CAN (GND_CAN, BUS_CAN_H/L, V_SOIN, V_SOOUT, GNDISO_CAN, CAN_RS, centro de la terminación) → 2.5 mm al resto.
    - El aislamiento es funcional, no de seguridad. Con J1 (MSTB de 5.08 mm) no se puede llegar a los 8.3 mm del encapsulado (CLR/CRP del datasheet Rev. D).
    - Además, ningún relleno puede cruzar el courtyard de U601.
  - **Anchos (IPC-2152, 1 oz, ΔT 10 °C;** 2 A → 30 mil y 1 A → 10 mil, según la tabla de ejemplo de Altium):
    - Entrada (VIN_VEH … +VPROT): 1.0 mm.
    - DO y SENSE: 0.5 mm.
    - +5V_VEH y BUCK_SW: 0.5 mm.
  - **Antena:** la huella oficial `RF_Module:ESP32-S3-WROOM-1` ya trae un rule area de keep-out de 48 × 21 mm en todas las capas de cobre (15 mm alrededor de la antena), que el DRC nativo hace cumplir.
    - Espressif (Hardware Design Guidelines): antena fuera de la placa o en el borde; si no, recortar la placa debajo y a los costados.
    - El documento oficial **no** da una cifra en mm para la placa base; los 15 mm que cita son para la carcasa.
- **Red del pad 25 de U101: `/10_power_input/U101_RTN`.**
  - En el símbolo (`easyeda2kicad:LM74930QRGERQ1`, librería y caché), el pin 25 (EP) pasó de `no_connect` a `passive`.
  - Con `no_connect`, KiCad le daba a cada pad 25 de la huella su propia red `unconnected-…_N` (7 redes que se superponían).
  - Se agregó la etiqueta `U101_RTN` en la hoja 10 (ERC sigue en 0).
  - En el PCB se renombraron las 7 redes de los pads 25 a `/10_power_input/U101_RTN`. Es la única edición al `.kicad_pcb`; no hubo "Update PCB from Schematic".
  - Reglas:
    - `U101_RTN_aislado`: 0.3 mm a cualquier otra red y `zone_connection none`.
    - `U101_pad25_nunca_GND`: si el pad 25 tiene otra red, es un error.
  - **Probado** en una copia: con un pad 25 en GND_VEH, el DRC marca `items_not_allowed` con esa regla.
- **DRC actual** (PCB viejo, sin actualizar):
  - Las 6 violaciones de `ISO_CAN_barrera` son pads de "U1" sin conectar (RS, AUX_OUT); se resuelven con la actualización (U601, RS a GND2).
  - De antes de este turno:
    - Contorno inválido: dos rectángulos superpuestos en Edge.Cuts.
    - J401 (USB-C): pad a NPTH a 0.194 mm (< 0.25 mm del proyecto; JLCPCB pide NPTH a pista 0.2 mm). Es de la huella.
    - U401: serigrafía recortada por el borde.
    - PS201: huella borrada (sale con la actualización).
    - Los agujeros H2–H4 no coinciden con la librería.
  - **Costo en JLCPCB:** las vías del EP de U101 (hueco 0.2 mm, Ø 0.4 mm) tienen recargo ("0.2mm or 0.25mm hole size with via diameter less than 0.45mm, will cost more"). Para evitarlo hay que subir el Ø a ≥ 0.45 mm en `TI_RGE0024T_..._IsolatedVias`. Pendiente de decisión.

## Hoja 80 y cierre del esquemático (aplicado, 2026-10-27)
- **Hoja 80 aprobada y aplicada.**
  - U801 TPS3828-33QDBVRQ1, C801, R802 (0 Ω en serie con RESET).
  - R801 (1 k de WDI a GND): DNP en PROTO y PROD.
  - MR sin conexión.
- **WD_EN eliminado:** se quitó de las hojas 40 y 80 y de la raíz, e IO18 quedó libre (con marca de no-conexión).
  - El pin que ocupaba en las hojas se reutilizó para **VAR_ID2 (IO8)**.
- **VAR_ID**, tabla del usuario (ID1 ID0): **11 base | 10 CAN | 01 solo DO | 00 CAN + DO**.
  - R805 (IO4): `Variant = CAN`. R806 (IO5): `Variant = OUT`.
  - R807 (IO8, tercer bit, CABIN): `DNP = PROTO,PROD`.
  - La variante **ROT se detecta por SPI**, sin bit de VAR_ID (decisión del usuario).
- **LED:** la caja ABS es opaca. D801 (verde, LTST-C171KGKT), D802 (rojo, LTST-C171KRKT), R803 y R804 (470 Ω): montados en PROTO, `DNP = PROD`. MPN de los LED a verificar.
- **Barrera CAN de 2.5 mm:** aprobada por el usuario (aislamiento funcional).
- **J1 y J2 pasan a verticales**, MSTBV 2,5 GF de 5.08 mm (decisión del usuario: el cable entra por un conector circular de 8 hilos en la caja).
  - J1 = MSTBV 2,5/5-GF-5,08 (1777109).
  - J2 = MSTBV 2,5/2-GF-5,08 (1777073, **verificar** en phoenixcontact.com).
  - Los enchufes STF no cambian.
- **Librería:** se borraron los símbolos `URB2405YMD-10WR3_C5369754` y `TPS7A1650QDGNRQ1` de `lib/INCLI-VA.kicad_sym`.
- **U101:** las vías del EP pasan a Ø 0.45 mm (hueco 0.2 mm), en la huella de `lib/INCLI-VA.pretty` y en la instancia del PCB. Ya no tienen recargo en JLCPCB.
- **ERC del proyecto: 0 errores y 1 aviso.** El aviso es `isolated_pin_label` en `U101_RTN`, y es intencional: la etiqueta sobre un solo pin es la que mantiene unida la red del pad 25.

## PCB (2026-10-27)
- **Contorno:**
  - Los dos rectángulos superpuestos eran la placa (100 × 70 mm, radio 4) y un **recorte para la antena** (x 192–200, y 65–100, bajo el área de antena de U401, que apunta a +x).
  - Se reemplazaron por un solo contorno cerrado (líneas y arcos) con una muesca de 8 × 35 mm (Espressif: recortar la placa bajo la antena y a los costados).
  - `invalid_outline` resuelto.
- **Serigrafía de U401:** se recortaron los dos laterales del módulo en x = 191.8 y se quitó la línea frontal, que caía sobre la muesca.
  - Ahora U401 figura como `lib_footprint_mismatch`. **No usar "Update footprints from library" en U401**: se perdería el recorte.
- **J401 (USB-C):** huella oficial `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`. El pad GND (A1/B12) queda a **0.194 mm** del NPTH de la espiga.
  - Eso es menos que el mínimo de JLCPCB para NPTH a cobre (0.2 mm) y que el `hole_clearance` del proyecto (0.25 mm).
  - Pendiente de decisión del usuario.
- **Update PCB from Schematic:** lo hizo el usuario en KiCad (F8, por UUID, con reemplazo de huellas, sin actualizar desde la librería). Commit `1859b79`.
  - Entraron 39 huellas y salieron PS201, U202, C207, C208, R204 y las referencias viejas U1 y R1.
  - Huellas que cambiaron: J1/J2 → MSTBV, Q701/Q751 → SOT-23, D701/D751 → SMA, U201 → HSOIC-8 con vías, C203–C206.
  - **Se borraron los agujeros de montaje H1–H4**: solo existían en el PCB. Conviene agregarlos al esquemático (`Mechanical:MountingHole`) para que no vuelva a pasar.
- **J401:** se acepta la violación (decisión del usuario). Se implementó como regla `J401_land_pattern_oficial` en `INCLI-VA.kicad_dru`: hole_clearance ≥ 0.19 mm, solo dentro de J401, con la nota.
  - Una exclusión del DRC (`drc_exclusions` en `.kicad_pro`) necesita la posición exacta del marcador, que solo da la interfaz; `kicad-cli` no la exporta y la API de Python no funciona sin la interfaz.
  - Si se prefiere la exclusión nativa: en KiCad, clic derecho en el marcador → Exclude, con la misma nota.
- **DRC después de la actualización** (`kicad-cli`, 2026-10-27):
  - Paridad con el esquemático: 0.
  - Sin rutear: 399 conexiones (todavía no hay pistas).
  - **29 errores de `ISO_CAN_barrera`:** los pasivos nuevos de la hoja 60 quedaron apilados por la actualización, mezclando el lado CAN y el lado de la placa. Se resuelven al ubicar los componentes (pendiente; el usuario pidió no moverlos todavía).
  - 1 aviso `lib_footprint_mismatch` en U401: intencional (serigrafía recortada en la muesca).

## Falta
- [ ] **Ubicación de componentes y ruteo** (cuando el usuario lo pida). Corregir la barrera CAN al ubicar.
- [ ] **Agujeros de montaje H1–H4:** agregarlos al esquemático (Mechanical:MountingHole + huella) y volver a ubicarlos. Hay que decidir el tipo (con o sin cobre; ver la pregunta 15 de PCB).
- [ ] **`80_supervision`:** pendiente.
  - **Requisito:** pull-down en **WD_EN** (IO18), para que el watchdog no corra durante el boot ni el flasheo.
  - WDO del TPS3431 → MCU_RST_N: drenador abierto, sin pull-up propio. R401 (10 k, hoja 40) es el pull-up y C403 (1 µF) el retardo de EN.
  - VAR_ID0/1 → IO4/IO5; LED_G/LED_R ← IO6/IO7.
- [ ] **Huella importada sin revisar** (regla de `AGENTS.md`): FUSE-SMD_L6.1-W2.5-1 (F101). Comparar con el land pattern de Bourns y documentar la fuente en su descripción.
  - Las tres están en `lib/INCLI-VA.pretty` sin descripción de fuente.
  - F101: comparar con el land pattern de Bourns y documentar la fuente.
- [x] **Limpieza del repositorio:** se borraron `fp-lib-table.bak`, `lib/Connector_Phoenix_MSTB.pretty.bak/` y las huellas y modelos 3D de URB2405 y HVSSOP-8 (2026-10-27).
  - La librería local `Phoenix_MSTB_local` duplica la oficial y ya no se usa (J1 y J2 usan `Connector_Phoenix_MSTB`).
- [ ] **Integración:** cuando estén todas las hojas:
  - ERC del proyecto completo en 0.
  - Revisión del netlist entre hojas.
- [ ] **PCB:** el usuario ya colocó huellas (commits `81c5d45`, `22dc6d2`, `2cabf1d`), pero falta "Update PCB from Schematic" con estos cambios.
  - **No tocar el PCB** hasta que el usuario lo pida.
  - Al retomarlo:
    - Crear la regla `.kicad_dru` para el pad 25 de U101.
    - Unir las 7 redes `unconnected-(U101-EP-Pad25)` en una sola.
    - Ver la estimación de espacio (100 × 70 mm).

Estado del ERC al 2026-10-27 (después de la opción B):

| Hoja | Violaciones |
|---|---|
| Raíz | 7 errores `label_dangling` + 18 avisos `isolated_pin_label`: señales de 80_supervision (WDI, WD_EN, MCU_RST_N, VAR_ID0/1, LED_G/R), que esa hoja todavía no usa |
| 80_supervision | 2 errores (hoja vacía: símbolos de potencia sin conectar) |
| 10, 20, 30, 40, 50, 60, 70 (DO1 y DO2) | 0 |

`sch_visual_qa` en 20_buck_5v: 1 aviso menor (TP201 junto a su símbolo de potencia).

## Decisiones del usuario aún abiertas
Preguntas anteriores que siguen sin respuesta (las de 60_can y BOM ya están resueltas arriba).

### 60_can
1. **Variantes:** ¿el CAN se monta en todas las variantes, o es DNP en la base (`Variant=CAN`)? ¿Qué variantes existen en total y cuáles se combinan?
7. **Velocidad del bus:** ¿250 kbit/s (J1939) o 500 kbit/s? Define si R605 queda en 0 Ω o en 47 k (control de pendiente).

### 80_supervision
9. **Timeout del watchdog TPS3431:** ¿el valor de fábrica (pin CWD sin conectar) o uno programado con un capacitor en CWD? Si es programado, ¿qué tiempo quieres (el firmware patea por WDI)?
10. **Tabla de ID de variante (VAR_ID1, VAR_ID0):** la hoja propone 00 base | 01 CAN | 10 CAN+OUT | 11 grúa (CAN+OUT+ROT). ¿La confirmas? ¿Alcanzan 2 bits si se suma CABIN, o hace falta un tercer bit (o un divisor leído por ADC1)?
11. **Implementación del ID:** ¿resistencias de 0 Ω / DNP **(rec.)** o solder jumpers?
12. **LED de estado:** ¿bicolor verde/rojo en un solo encapsulado (0805 o 1206) **(rec.)** o dos LED separados? ¿Se ve a través de la caja ABS, o hace falta un light pipe o una ventana?
13. **Variante CABIN (buzzer + LEDs):** ¿entra en esta revisión o queda para más adelante?

### PCB (no empiezo hasta que lo pidas)
14. **Caja y contorno:** ¿modelo o MPN de la caja ABS? ¿Dimensiones máximas de la placa, forma y altura máxima de componentes (lo limitan PS201, de 10.2 mm, y C105)?
15. **Fijaciones:** ¿cuántos agujeros, qué diámetro y en qué posición? ¿Separadores metálicos o plásticos? Con separadores metálicos, ¿a qué masa se conectan los agujeros (ninguna, GND_VEH o chasis)? Recomiendo **agujeros sin cobre y separadores plásticos**, para no puentear las barreras.
16. **Cara de montaje y orientación:** ¿qué cara de la caja va contra el chasis de acero? ¿Cómo queda la placa respecto del vehículo (qué eje de la placa es el eje longitudinal o lateral del vehículo)? Lo necesito para la antena y para la serigrafía de los ejes de los sensores.
17. **Variante ROT:** la placa va centrada sobre el eje del pivote. ¿El imán queda del lado de los componentes o del lado opuesto? ¿A qué distancia? ¿Hace falta un agujero o una zona libre para el eje?
18. **Conectores:** ¿J1 (MSTB de 5 pines) y J2 (MSTB de 2 pines) en el mismo borde? ¿El USB-C tiene que ser accesible desde afuera de la caja, o es solo para el banco con la caja abierta? ¿Dónde va el header UART0?
19. **Capas y espesor:** 4 capas (señal / GND / alimentación / señal), 1.6 mm, cobre de 1 oz **(rec.)**: da plano de masa para RF, sensores y barreras. ¿O tiene que ser de 2 capas por costo?
20. **Fabricante:** ¿JLCPCB, PCBWay u otro? Define las reglas mínimas (pista, separación, vías) y si se pide stencil.
21. **Montaje:** ¿todo de un solo lado **(rec.)**, para soldar a mano? ¿El ASM330LHH (LGA) lo sueldas tú con aire caliente o lo monta el fabricante?
22. **Barniz o conformal coating:** ¿sí o no? Cambia el grado de contaminación supuesto (PD2) para la fuga de las barreras.

## Requisitos para el firmware (SPI de 50_sensors)
Bus SPI compartido (SPI2/FSPI: SCK IO12, MOSI IO11, MISO IO13). Un `spi_device` por sensor, cada uno con su modo y su frecuencia:

| Sensor | CS | Modo SPI | f máx. | Fuente |
|---|---|---|---|---|
| U501 SCL3300-D01 | CS_INC → IO10 | 0 (CPOL=0, CPHA=0) | 8 MHz (recomendado 2–4 MHz) | Murata Doc. 4921 Rev. 4 |
| U502 ASM330LHH | CS_IMU → IO9 | 3 (CPOL=1, CPHA=1) | 10 MHz | ST DocID031239 Rev 4, tabla 6 |
| U503 AS5147U (solo ROT) | CS_ROT → IO14 | 1 (CPOL=0, CPHA=1) | 10 MHz | ams DS000639 v1-04 |

- ASM330LHH: configurar `I2C_disable = 1` (CTRL4_C) y `DEVICE_CONF = 1` (CTRL9_XL); INT1/INT2 en push-pull (IO40/IO41).
- Variante estándar: U503 no está montado; no inicializarlo (leer VAR_ID antes de tocar CS_ROT).

## Conectores J1 y J2 (confirmado por el usuario, 2026-10-27)
Phoenix Contact COMBICON **MSTBV 2,5**, **vertical**, paso **5.08 mm** y **brida roscada (GF)**.
- Se eligió vertical porque el cable externo entra por un conector circular de 8 hilos en la caja. J1 y J2 son conexiones internas; quedan 7 hilos de 8 en uso.
- Confirmado en phoenixcontact.com (fichas "PCB header"; el sitio bloquea el acceso automático, así que se leyeron indexadas):
  - **1777109** = MSTBV 2,5/ 5-GF-5,08: 5 polos, 12 A / 320 V (III/2), brida roscada, soldadura por ola, Sn.
  - **1777073** = MSTBV 2,5/ 2-GF-5,08: 2 polos, 12 A / 320 V (III/2), brida roscada, agujero de 1.4 mm, Sn.

| Ref. | Función | Header en placa (MPN) | Enchufe del arnés (no va en la placa) |
|---|---|---|---|
| J1 | 1 V+, 2 GND_VEH, 3 CAN_H, 4 CAN_L, 5 CAN_GND | MSTBV 2,5/5-GF-5,08 (**1777109**) | MSTB 2,5/5-STF-5,08 (**1778014**), tornillo |
| J2 | 1 DO1, 2 DO2 | MSTBV 2,5/2-GF-5,08 (**1777073**) | MSTB 2,5/2-STF-5,08 (**1777989**), tornillo |

- Los enchufes STF se atornillan a la brida del header, lo que sirve contra la vibración. Son de 12 A / 320 V, para cable de 0.2–2.5 mm².
- Phoenix también lista como compatibles con estos headers otras familias STF de 5.08 mm: FKC 2,5 (push-in), QC 1 (desplazamiento de aislante) y TMSTBP 2,5. Sirven si se prefiere otra forma de cablear el arnés.
- Huellas oficiales: `Connector_Phoenix_MSTB:PhoenixContact_MSTBV_2,5_{5,2}-GF-5,08_..._Vertical_ThreadedFlange`. Ya están en el PCB.
- **BOM del arnés:** los enchufes no salen del BOM de la placa. Si se quiere, se pueden agregar como ítems mecánicos.

## Pendientes de BOM
- [ ] **C105 (PROD)** (pedido del usuario, 2026-10-27): electrolítico **SMD** automotriz **AEC-Q200**, **≥ 50 V**, 1000–2200 µF, 105–125 °C, en versión **resistente a vibración** (con terminales extra de anclaje), con MPN.
  - Hoy: huella `Capacitor_SMD:CP_Elec_16x17.5` y MPN pendiente.
  - Al elegirlo, revisar que la huella coincida con su land pattern y que las terminales de anclaje tengan pads.
  - Revisar el inrush con C109 = 100 nF y la ESR/ripple.
- [ ] **R102** (pedido del usuario, 2026-10-27): resistencia **anti-pulso en el mismo encapsulado 2512**, si aguanta el pulso del load dump sin suprimir.
  - Pulso: ~2 W durante 350 ms (0.68–0.74 J rectangular) con 85 °C de temperatura inicial (REVISION_CODEX I2).
  - Comparar con la curva de pulso único del fabricante, por ejemplo series anti-surge 2512.
  - Si ninguna 2512 alcanza, proponer otra opción antes de cambiar la huella.
- [ ] **Compra de sensores:**
  - SCL3300-D01 y AS5147U-HTSM: sin stock en LCSC → comprar en DigiKey o Mouser.
  - ASM330LHHTR: con stock en LCSC (C459826).
- [ ] **MPN marcados "a verificar" en Notes** (disponibilidad y especificación, antes de congelar el BOM):
  - 10_power_input:
    - Q101 STD18NF25
    - L101 SRN6045TA-100M
    - C101 CGA5L4X7T2W104K160AA
    - C102 y C103 CGA5L2X7R2A105K160AA
    - C106 GCM32ER71H106KA12L
    - C107 GCM188R72A104KA64D
    - C110 GCM188R71H683KA57D
    - D101 ES2G-E3/52T
  - 20_isolation: se rehace con la opción B (no aislada); sus MPN dejan de aplicar.
  - 30_regulation:
    - C301 GCM21BR71A106KE22L
    - C304 GRM21BZ71A226ME15L
    - FB301 BLM18PG221SN1D
    - U302 LP5907QMFX-3.3Q1 (confirmar el código de pedido exacto)
  - 40_mcu_esp32s3:
    - C401 GRM21BZ71A226ME15L
    - C403 GCM188R71C105KA64D
    - D401 PMEG3020EH (DNP, opción de banco)
  - 50_sensors:
    - C508 GCM21BR71A106KE22L

## Notas para el próximo turno
- Variante ROT: U503, C507 y R503 tienen `dnp yes` y el campo `Variant = ROT`. En la variante ROT la placa va centrada sobre el eje del pivote.
- Huella del SCL3300 (easyeda2kicad DFL-12): pads 0.32 mm más largos que el land pattern de Murata, para soldar a mano; en producción volver al de Murata.
- Pines del ESP32-S3: la tabla aprobada y sus criterios están en un texto de la hoja 40. No mover señales críticas a GPIO1–14/17/18 (glitch de encendido) ni a strapping.
- Opción de banco (D401 + JP401, DNP): con JP401 cerrado, +5V_ISO queda en ~4.6 V y el CAN no está garantizado. Abrir JP401 antes de instalar en el vehículo. Revisar al pasar a la opción B (el buck y el USB comparten el riel de 5 V).
- Firmware: los requisitos están en `README.md` ("Requisitos para el firmware").
- KiCad: antes de editar archivos `.kicad_sch` a mano o con scripts, confirmar que KiCad está cerrado. Si estaba abierto, recargar las hojas antes de guardar.
