# INCLI-VA — estado y pendientes

Leer al empezar cada turno y actualizar al terminarlo (ver "Trabajo entre agentes" en `AGENTS.md`).

Última actualización: 2026-10-29, Claude Code (H1–H5 metalizados sin red, apoyo B reservado, serigrafía de barrera CAN, pinout y nombre de placa).

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
- Las DO no tienen latch de sobrecorriente (retirado el 2026-10-28): un corto de la carga a +V no está limitado por hardware.

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

## Cierre del esquemático (2026-10-27)
- **El PCB (ubicación y ruteo) lo hace Codex.** Claude Code no toca `INCLI-VA.kicad_pcb`.
- H1–H4 agregados en la raíz: `Mechanical:MountingHole`, huella `MountingHole:MountingHole_3.2mm_M3` (NPTH, sin cobre, courtyard de Ø 6.9 mm), fuera del BOM. La posición la define el layout.
- La revisión final (ERC, campos, huellas, ESP32, DNP, BOM y PENDIENTES) se entregó al usuario como reporte. **Los cambios que propone esperan su aprobación.** Después vienen los BOM de PROTO y PROD, el PDF, `docs/LAYOUT_NOTES.md`, el commit "esquemático congelado para layout" y el tag `schematic-v1`.

## Estado previo al layout — Codex, 2026-10-27
- Turno cedido por el usuario: Claude terminó. Se incorporan sus cambios locales de cierre junto con la sincronización del PCB.
- PCB sincronizado: 186 huellas, H1–H5 añadidos (NPTH, posiciones pendientes), F101 actualizado a `Fuse_Bourns_SF-2410`, D401/JP401 retirados; campos y DNP transferidos. Paridad CLI: **0 diferencias**.
- ERC: **0 errores y 1 aviso** intencional `isolated_pin_label` en U101_RTN. Todas las hojas eléctricas sin errores.
- Revisión visual manual de las diez páginas exportadas: completada. Valores de H1–H5 y TP201 ocultados para evitar solapes; notas de TPS3828, alimentación USB y pull-up de FLT corregidas.
- `sch_visual_qa`: no disponible en el perfil MCP `analysis`; la revisión manual no equivale a ejecutar esa herramienta. Repetir cuando esté disponible.
- DRC previo a ubicación: **29 errores de separación CAN**, **1 aviso de U401** por serigrafía recortada intencional y **396 conexiones sin rutear**. Sin pistas ni zonas.
- U101 pad 25 y vías conservan `/10_power_input/U101_RTN`; contorno, reglas y keep-out de U401 conservados.
- La información histórica anterior describe etapas previas y no sustituye este estado.

## Propuesta visual de tamaño — Codex, 2026-10-27
- Se recomienda **120 × 80 mm** para la revisión de ubicación; 100 × 70 mm queda ajustado (ocupación estimada 82.6 % frente a 59.5 %). No se afirma que 100 × 70 sea imposible de rutear.
- Propuesta separada: `docs/layout/INCLI-VA-120x80.kicad_pcb`; vista `docs/layout/ubicacion-120x80.png`; metodología y límites en `docs/LAYOUT_NOTES.md`.
- Las 186 huellas están ubicadas en la propuesta, con margen geométrico de 1.01 mm entre envolventes, redes/DNP conservados y ningún ruteo. El PCB principal no se cambió.
- DRC de la copia: 0 errores geométricos, 1 aviso conocido de U401, 396 conexiones pendientes. Referencias en F.Fab; falta serigrafía final.
- **Falta confirmar tamaño y revisar bloques**, luego afinar desacoples/retornos y mecánica antes del visto bueno final para rutear.

## Retoma y tamaño objetivo — Codex, 2026-10-28
- El usuario consulta si el diseño puede entrar en **100 × 100 mm como máximo**. Se toma como objetivo para la siguiente revisión de ubicación; todavía no hay una propuesta verificada de ese tamaño.
- Evaluación preliminar: 10000 mm² nominales frente a 9600 mm² de 120 × 80 mm (**4.2 % más**). Con las mismas deducciones geométricas y reserva de huellas del estudio anterior, la ocupación estimada sería **57.0 %**. Es favorable por área, pero no demuestra encaje ni ruteabilidad.
- Estado recuperado: propuesta de 120 × 80 mm con 186 huellas y sin ruteo, guardada en `docs/layout/`; último commit previo `1bb7e6a`. El árbol de trabajo estaba limpio.
- Próximo paso: redistribuir en una copia de 100 × 100 mm y comprobar antena, aislamiento CAN, fijaciones, reserva ROT, acceso para soldar y lazos de alimentación. Mantener las huellas DNP. Presentar ubicación antes de rutear.
- En esta retoma solo se actualizó documentación: no se modificaron esquemáticos ni PCB y no se repitieron ERC/DRC.

## Propuesta de 100 × 100 mm preparada — Codex, 2026-10-28
- Autorización del usuario: preparar el formato cuadrado y reubicar componentes. Hecho en **`docs/layout/INCLI-VA-100x100.kicad_pcb`**, con proyecto y reglas adjuntos; principal y propuesta 120 × 80 conservados.
- **186 huellas ubicadas**, incluyendo DNP. Entrada/CAN a la izquierda, dos DO arriba, bucks abajo, sensores en la zona central, ESP32 en el borde derecho y USB abajo.
- U503 en (50,50) mm locales; H5 en (54,60), próximo a los sensores; cinco fijaciones NPTH. Muesca RF de 8 × 35 mm y esquinas de radio 4 mm.
- **DRC de la propuesta: 0 errores geométricos, 1 aviso intencional de U401 y 396 conexiones sin rutear**. Sin pistas ni zonas. Separación mínima de envolventes: 1.01 mm.
- Verificada igualdad de UUID/referencias, valores, campos, DNP, geometría básica de pads y redes frente al PCB principal. U101 pad 25 conserva su red y reglas; keep-out de U401 conservado.
- Imagen revisada: `docs/layout/ubicacion-100x100.png`; exportación nativa: `placa-100x100.svg`. Reportes en `docs/layout/reports/`; scripts reproducibles en `scripts/`.
- No se editaron esquemáticos; no correspondió repetir ERC ni QA de hojas. Falta ajuste eléctrico de detalle, validación mecánica y visto bueno antes de rutear.

## Revisión: TP en Bottom y cuatro fijaciones — Codex, 2026-10-28
- El usuario prefiere 100 × 100 mm, propone TP en la cara inferior y cuatro agujeros de sujeción. Aplicado en la copia `docs/layout/INCLI-VA-100x100.kicad_pcb`.
- **19 TP en B.Cu**, pads Ø 1.5 mm sin taladro. Catorce cambiaron de cara; TP401–TP405 ya estaban abajo. Referencias legibles desde abajo en B.Silkscreen, 1 mm/0.15 mm, sin colisiones detectadas por DRC.
- **H5 retirado de la propuesta**; quedan H1–H4 NPTH M3. Se conservan las posiciones XY de las otras 185 huellas y todas sus redes/campos/DNP. La rigidez con cuatro apoyos requiere validación mecánica.
- Vistas separadas por cara: `ubicacion-100x100.png` y `ubicacion-100x100-bottom.png`. Corregida la ilustración anterior, que mostraba juntos los pads de ambas caras. Exportaciones SVG nativas actualizadas; revisión visual inferior completada.
- DRC repetido: **0 errores geométricos, 1 aviso conocido de U401, 396 conexiones sin rutear**. U101_RTN y reserva RF conservados.
- **Pendiente H5 en esquemático/PCB base:** hay un archivo de bloqueo del proyecto. Se preguntó si KiCad está cerrado, como exige AGENTS.md; sin respuesta aún al documentar este turno. No se editaron esquemáticos ni PCB principal, ni se repitió ERC/QA de hojas. La comparación de integridad excluye H5 explícitamente; no afirmar paridad completa hasta sincronizar.

## Cierre para revisión del usuario — Codex, 2026-10-28
- El usuario respondió afirmativamente a la consulta pendiente y pidió retirar H5 del esquemático. Se eliminó únicamente su símbolo/instancia en `INCLI-VA.kicad_sch` y se actualizó la nota a cuatro agujeros H1–H4. Las conexiones y hojas eléctricas no cambian.
- ERC repetido, reporte persistente `docs/layout/reports/erc-sin-h5.json`: **0 errores y 1 aviso intencional `isolated_pin_label` en U101_RTN**. El JSON agrupa ese aviso bajo `/`; las hojas eléctricas restantes tienen 0 incidencias.
- Hoja raíz exportada por KiCad y revisada visualmente: H1–H4 y nota correctos, sin solapes nuevos. **`sch_visual_qa` no está disponible** en el catálogo de herramientas ni como ejecutable; esta revisión manual no equivale a ejecutar esa herramienta.
- El usuario solicita commit final y push para revisar en detalle esquemático y PCB. Comparar la raíz con **`docs/layout/INCLI-VA-100x100.kicad_pcb`**, que ya tiene 185 huellas, cuatro fijaciones y TP en Bottom. La placa principal y la propuesta 120 × 80 siguen siendo referencias previas, con H5; no se cambiaron en este cierre del esquemático.

## Reacomodo por bloques — Claude Code, 2026-10-28
- El usuario hizo F8 en KiCad tras retirar el latch: commit aparte `30380cc`, paridad 0.
- **H5 agregado** en el esquemático raíz (M3, sin cobre, UUID a7c615b1…) y en el PCB en (68.2, 53) mm locales. Queda junto a U501/U502 y a 18 mm del eje de ROT.
- **Reubicación por bloques según `docs/reference/`** (UG-230 e INCLIMAX). Detalle, tablas antes/después y límites en `LAYOUT_NOTES.md`; imagen en `docs/layout/reacomodo-antes-despues.png`.
- **Barrera `BARRERA_CAN`** (rule area en las dos caras). Solo la cruza U601. **FB602 no cruza:** sus dos redes (GNDISO_CAN y GND_CAN) son del lado aislado.
- `INCLI-VA.kicad_dru`: el pin 17 de U601 (AUXOUT, sin conexión) cuenta como dominio CAN en `ISO_CAN_barrera`.
- DRC 0 errores / 1 aviso U401 / paridad 0. ERC 0 / 1 aviso conocido. `sch_visual_qa` raíz: PASS.
- **Sin ruteo ni zonas de cobre.**

## PCB principal = propuesta 100 × 100 — Claude Code, 2026-10-28
- Pedido explícito del usuario: pasar la propuesta al layout principal. `docs/layout/INCLI-VA-100x100.kicad_pcb` se copió sobre `INCLI-VA.kicad_pcb`. El principal no tenía cambios desde `17a9676`, así que no se perdió nada.
- Borrada la copia `docs/layout/INCLI-VA-100x100.{kicad_pcb,kicad_pro,kicad_dru,kicad_prl}` y su `fp-lib-table`. `.kicad_dru` y las reglas de `.kicad_pro` eran idénticas a las del principal. Vistas, posiciones y reportes se quedan en `docs/layout/`. Los scripts `layout_100x100.py` y `review_layout_100x100.py` quedan como históricos.
- DRC del principal: 0 errores, 1 aviso conocido de U401 y 396 conexiones sin rutear. **Paridad: 22 diferencias** por el latch retirado. **No se hizo "Update PCB from Schematic"**: espera el pedido del usuario.

## Latch de DO retirado y 120 × 80 borrada — Claude Code, 2026-10-28
Decisiones del usuario en este turno:
- **Aislamiento:** el usuario preguntó por la etapa aislada. Se recordó la decisión 3 (opción B, commit `5030862`); no cambia nada.
- **Salidas DO: se quita el latch de sobrecorriente** (antes `DNP = PROTO,PROD`), en las dos instancias:
  - Borrados: Q702/Q752, Q703/Q753, D702/D752, R704–R707/R754–R757, C701/C751 y sus 3 GND_VEH por canal. Etiquetas TRIG, LATCH y SENSE, y las dos EN_5V del latch.
  - **R701/R751 (1 Ω) también salen:** la fuente de Q701/Q751 va directo a GND_VEH.
  - `PWR_FLT_N` ya no entra en la hoja 70 (solo lo usaba D702): se quitaron el pin jerárquico y sus dos conexiones en la raíz. Sigue entre las hojas 10 y 40.
  - **El diagnóstico se conserva** (R708–R710, D703: DNP en PROTO, montado en PROD).
  - Textos de la hoja, Notes de R702 y README actualizados. **Limitación:** un corto de la carga a +V no queda limitado por hardware.
- ERC: 0 errores / 1 aviso conocido (U101_RTN). `sch_visual_qa`: raíz PASS; hoja 70 con 10 avisos `symbol_overlap` de símbolos que ya estaban y se tocan en un pin compartido (no son solapes visibles).
- **Paridad con `docs/layout/INCLI-VA-100x100.kicad_pcb`: 22 diferencias esperadas** (18 huellas que sobran, red SENSE → GND_VEH en el pad 2 de Q701/Q751 y la Note de R702/R752). Hace falta "Update PCB from Schematic" sobre la propuesta (Codex o el usuario). Se libera el espacio del latch en el bloque DO.
- **Propuesta 120 × 80 borrada** de `docs/layout/` (pcb/pro/dru/prl, posiciones, vistas). Se recupera de `aa0a41b`. `scripts/layout_100x100.py` partía de ella; se anotó en su cabecera.

## Revisión del cierre de Codex — Claude Code, 2026-10-28
Solo verificación; no se editó esquemático ni PCB.
- **Esquemático:** ERC 0 errores / 1 aviso conocido (`isolated_pin_label` U101_RTN). `sch_visual_qa` raíz: PASS (solo INFO: falta "company" en el cajetín). 0 etiquetas globales; KW45 fuera de la jerarquía. Footprint/MPN/Manufacturer/Datasheet completos en los 162 componentes de BOM. Todo pasivo que no es 0603 tiene justificación en Notes. El commit `53115ad` solo quita H5 y cambia la nota.
- **Propuesta 100 × 100:** DRC 0 errores, 1 aviso U401, 396 sin rutear. **Paridad con el esquemático: 0** (probada en una copia con la propuesta como PCB del proyecto). Courtyards ≥ 1 mm en la misma cara. U101 pad 25 = U101_RTN; `.kicad_dru` y reglas de `.kicad_pro` iguales a las del principal.
- **Observaciones de ubicación para la siguiente iteración** (distancia borde de pad a pin):
  - U101: C108 (CAP) 12 mm, C102 (VS) 7 mm, C103 23 mm, C110 (TMR) 20 mm → acercarlos al QFN.
  - U201 LMR38010: C202 a VIN 3.1 mm, C201 4.5 mm, L201 a SW 3.8 mm → cerrar el lazo caliente (C202 pegado a VIN/GND).
  - U601 ADM3055E: C601–C610 entre 1.6 y 7 mm por lado → no cumple el ≤ 2 mm de ADI (ya listado).
  - Sensores U501/U502/U503 en el centro de la luz de 90 mm entre H1–H4 (sin H5): es la zona de mayor flexión bajo vibración. Evaluar rigidez o un apoyo cercano que no choque con el eje ROT.
  - SW402 (pulsador) junto a U502: los golpes al pulsar llegan a la IMU; conviene alejarlo.
  - J401 queda ~1 mm dentro del borde; definir si el USB debe asomar fuera de la caja (pregunta 18).
  - H4 (tornillo M3) junto al keep-out de antena; preferir separador plástico o alejarlo.
  - TP: faltan los CS de SPI y el lado bus del CAN (medible en J1); TP201 y TP301 están ambos en +5V_VEH.
- **Notas desactualizadas:** R708/R709/R758/R759 dicen "el drenador llega a ~250 V" (hoy Q701 de 100 V y recorte ≤ 93.6 V). En "Pendientes de BOM" sigue la línea de 20_isolation y la pregunta 14 menciona PS201.

## Fijaciones H1–H5 y serigrafía — Claude Code, 2026-10-29
Pedido explícito del usuario (esquemático raíz, PCB y `.kicad_dru`). Detalle en `LAYOUT_NOTES.md`, sección "Fijaciones H1–H5, apoyo opcional y serigrafía". **Sin ruteo.** No hizo falta F8: H5 se agregó al PCB con la ruta de su símbolo, y la paridad da 0.
- Se conservaron los 5 segmentos de CAN_H/CAN_L en F.Cu que el usuario había borrado sin commit.
- Hecho:
  - H1–H4 cambiados a `MountingHole_3.2mm_M3_Pad`, y H5 nuevo en (56.0, 38.5). Metalizados, con anillo de 6.4 mm (huella oficial) y **sin red**.
  - Reglas `H_anillo_cobre` (≥ 0.5 mm) y `H_zona_arandela` (pistas/vías a ≥ 4 mm del centro).
  - Rule area `APOYO_CAJA_B`: Ø8 mm en B.Cu en (63.5, 49.0); sin pistas, vías, pads ni huellas; relleno permitido.
  - Serigrafía: línea de la barrera CAN y "CAN AISLADO" en las dos caras, pinout de J1/J2 en las dos caras, nombre/Rev/fecha abajo, rótulos ENTRADA, BUCK 5V, SALIDAS DO y SENSORES. Las marcas de polaridad y pin 1 ya estaban todas.
  - C206 a 12.8 mm aceptado: cada C204–C206 con su vía a GND y plano continuo hasta el EP de U201 (anotado para el ruteo).
- Verificación: DRC 0 errores (3 avisos conocidos de U401), paridad 0, 358 sin rutear. ERC 0 errores. `sch_visual_qa` de la raíz: PASS.
- ERC: 4 avisos `pin_to_pin` nuevos en `40_mcu`. Vienen del símbolo de SW401/SW402 que cambió el usuario (pines "Unspecified"). Son inofensivos y quedan para cuando se revise ese símbolo.
- **Decisiones abiertas:**
  - Lado del imán de ROT: sigue sin definir. Se dejan libres las dos caras; H5 y B dejan libre un círculo de Ø17.9 mm alrededor del eje.
  - Visto bueno a la ubicación para empezar el ruteo.

## Correcciones sobre `1ff3419` — Claude Code, 2026-10-29
Pedido explícito del usuario (editar el PCB). Detalle y tablas en `LAYOUT_NOTES.md`, sección "Correcciones aplicadas sobre `1ff3419`". **Sin ruteo.**
- Al empezar seguía abierto el gestor de proyectos de KiCad (`~INCLI-VA.kicad_pro.lck`); el editor de PCB estaba cerrado. No se tocó `.kicad_pro`.
- Hecho:
  - C403 sobre el pin EN (1.3 mm).
  - C202 a 1.06 mm de VIN y de GND de U201; C201 detrás.
  - C204–C206 en columna junto a C203: 6.0 / 9.4 / 12.8 mm al EP (antes 11.6–13.9).
  - J401 −0.4 mm: sin errores de borde.
- Referencias: todas en 0.8 / 0.8 / 0.15 mm, a 0°/90°. Regla `JLC_serigrafia` → 0.8 / 0.15 mm. Ocho quedan solo en F.Fab: U101, R106, R202, C607, C610, R602, R303 y Q701.
- Courtyards: un solo par por debajo de su criterio, C403–C402 (0.7 mm). El resto queda en ≥ 0.5 mm por ser pasivos del IC.
- DRC: 0 errores y los 3 avisos conocidos de U401. Paridad 0; 356 sin rutear.
- **Decisiones abiertas:**
  - Rigidez de los sensores: opción A, agujero M3 en (56.0, 38.5); u opción B, apoyo inferior de Ø8 mm en (63.5, 49.0).
  - Aprobar los rótulos de zona, el pinout de J1/J2 y la línea de barrera CAN en serigrafía.
  - Visto bueno a la ubicación para empezar el ruteo.

## Revisión de la ubicación del usuario (`1ff3419`) — Claude Code, 2026-10-28
Solo verificación y documentación; no se tocó el PCB (KiCad estaba abierto). Detalle en `LAYOUT_NOTES.md`, sección "Revisión de la ubicación del usuario".
- DRC: paridad 0; 2 errores de borde en J401 (ranuras SH a 0.3 mm); 92 referencias en 0.7 / 0.12 mm (regla de 1.0 / 0.15); 37 pares de courtyards a menos de 1 mm.
- A corregir antes de rutear: C403 vuelve al pin EN de U401; C202/C201 pegados a VIN/GND de U201; GND de C204–C206 cerca del EP; J401 0.3–0.5 mm hacia adentro.
- Propuestos: rótulos de zona, pinout de J1/J2, línea de barrera CAN en serigrafía y flechas de ejes en los sensores. Se colocan cuando el usuario lo apruebe, con KiCad cerrado.
- Decisión abierta: apoyo de los sensores sin H5 (zona de máxima flexión).

## Falta
- [x] Sincronizar `INCLI-VA.kicad_pcb` con el esquemático (F8 del usuario, `30380cc`); paridad 0 también tras agregar H5.
- [x] Retirar H5 y actualizar la nota de fijaciones en la raíz; repetir ERC y revisión visual manual.
- [x] Ejecutar `sch_visual_qa` de la raíz: PASS (Claude Code, 2026-10-28).
- [x] Propuesta 100 × 100 adoptada como PCB principal (2026-10-28). Falta la paridad completa (ver el ítem siguiente).
- [x] Preparar y presentar distribución preliminar de **100 × 100 mm máximo** con todos los componentes y H1–H5, separación CAN y acceso de soldadura comprobados geométricamente. Ver `LAYOUT_NOTES.md`.
- [~] Desacoples/lazos afinados en el reacomodo por bloques (tablas en LAYOUT_NOTES). Faltan C601 (10 nF VIO, 4.8 mm), L201/C203 y el visto bueno del usuario a la ubicación **antes de rutear**.
- [ ] Ruteo: plano GND_VEH continuo en B.Cu (sin cortes bajo el buck ni los sensores), GND_CAN propio en la isla, costura de vías.
- [ ] Ruteo y planos, únicamente después del visto bueno a la ubicación; luego DRC completo.
- [ ] Confirmar land pattern de C105 EEE-FK1H102AM contra J16 de Panasonic; la alternativa antivibración requiere otra huella. Reservar espacio y adhesivo.
- [ ] Verificación térmica en dos capas y ensayos eléctricos/EMC; ERC no certifica transitorios ni disipación.
- [ ] Validar H5 (56.0, 38.5), el apoyo B (63.5, 49.0) y H1–H4 contra la caja y el portaimán de ROT (Ø ≤ 17.9 mm libre); ensayo de vibración.
- [ ] Ruteo del buck: vía a GND junto al pad de C204, C205 y C206, y plano continuo hasta las vías del EP de U201.
- [x] Supervisión con TPS3828 aplicada. WD_EN/TPS3431 quedaron obsoletos.
- [x] F101: nueva huella documentada en librería e incorporada al PCB; sustituye la importación antigua.
- [x] Regla e isla lógica U101_RTN implementadas; las vías del EP comparten una sola red.
- [x] Opción de banco D401/JP401 eliminada del esquemático y del PCB.

## Decisiones del usuario aún abiertas
Preguntas anteriores que siguen sin respuesta (las de 60_can y BOM ya están resueltas arriba).

### 60_can
1. **Variantes:** ¿el CAN se monta en todas las variantes, o es DNP en la base (`Variant=CAN`)? ¿Qué variantes existen en total y cuáles se combinan?
7. **Velocidad del bus:** ¿250 kbit/s (J1939) o 500 kbit/s? Define si R605 queda en 0 Ω o en 47 k (control de pendiente).

### 80_supervision — preguntas históricas, resueltas por TPS3828 y tabla VAR_ID vigente
9. **Timeout del watchdog TPS3431:** ¿el valor de fábrica (pin CWD sin conectar) o uno programado con un capacitor en CWD? Si es programado, ¿qué tiempo quieres (el firmware patea por WDI)?
10. **Tabla de ID de variante (VAR_ID1, VAR_ID0):** la hoja propone 00 base | 01 CAN | 10 CAN+OUT | 11 grúa (CAN+OUT+ROT). ¿La confirmas? ¿Alcanzan 2 bits si se suma CABIN, o hace falta un tercer bit (o un divisor leído por ADC1)?
11. **Implementación del ID:** ¿resistencias de 0 Ω / DNP **(rec.)** o solder jumpers?
12. **LED de estado:** ¿bicolor verde/rojo en un solo encapsulado (0805 o 1206) **(rec.)** o dos LED separados? ¿Se ve a través de la caja ABS, o hace falta un light pipe o una ventana?
13. **Variante CABIN (buzzer + LEDs):** ¿entra en esta revisión o queda para más adelante?

### PCB — decisiones mecánicas pendientes; ubicación autorizada, ruteo requiere visto bueno
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
    - D401 eliminado junto con JP401; ya no aplica.
  - 50_sensors:
    - C508 GCM21BR71A106KE22L

## Notas para el próximo turno
- Variante ROT: U503, C507 y R503 tienen `dnp yes` y el campo `Variant = ROT`. En la variante ROT la placa va centrada sobre el eje del pivote.
- Huella del SCL3300 (easyeda2kicad DFL-12): pads 0.32 mm más largos que el land pattern de Murata, para soldar a mano; en producción volver al de Murata.
- Pines del ESP32-S3: la tabla aprobada y sus criterios están en un texto de la hoja 40. No mover señales críticas a GPIO1–14/17/18 (glitch de encendido) ni a strapping.
- Opción de banco D401/JP401 eliminada. USB no alimenta +5V_VEH; usar la entrada vehicular para energizar la placa.
- Firmware: los requisitos están en `README.md` ("Requisitos para el firmware").
- KiCad: antes de editar archivos `.kicad_sch` a mano o con scripts, confirmar que KiCad está cerrado. Si estaba abierto, recargar las hojas antes de guardar.
