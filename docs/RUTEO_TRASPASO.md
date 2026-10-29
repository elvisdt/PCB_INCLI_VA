# Traspaso del ruteo a Codex — rama `ruteo-agente`

Claude Code, 2026-10-29. Este documento se lee solo, sin otros archivos. Codex sigue con las **etapas 2 a 6** en la misma rama (`ruteo-agente`). La etapa 1 está cerrada.

Antes de empezar: leer `AGENTS.md`, `git log -5` y `docs/PENDIENTES.md`. Al terminar cada etapa: DRC, render de las dos caras, commit `[Codex] ruteo etapa N: ...`, `git push origin ruteo-agente`, y **esperar el visto bueno del usuario**.

> **No tocar** la carpeta `../PCB_INCLI_VA_manual` (git worktree, rama `ruteo-manual`). Es la copia que el usuario rutea en paralelo. Tampoco ejecutar `git worktree remove` ni `git worktree prune`.

---

## 1. Estado actual (fin de la etapa 1)

| | |
|---|---|
| Rama / último commit | `ruteo-agente`, ver `git log -1` (etapa 1 cerrada) |
| Base de ubicación | tag `placement-v1` (f472680) + cambios de la sección 3 |
| DRC | **0 errores**. Avisos: 19 `via_dangling` (vías GND que esperan el plano de la etapa 5), 2 `silk_overlap` (referencias de Q101 y U801, de antes), 2 `silk_edge_clearance` y 1 `lib_footprint_mismatch` de U401 (conocidos, aceptados) |
| Paridad con el esquemático | **0** |
| Conexiones sin rutear | **288** (358 en `placement-v1`) |

### Ruteado (etapa 1, potencia)
- **Entrada (F.Cu, 1.5 mm):**
  - J1.1 → F101 → VBAT_F → tab de Q101, R102, C101, R108 y D101; TP102 por vía.
  - D101 ↔ TVS D102. El GND del TVS va directo a J1.2.
- **Q101/Q102:**
  - VA, la fuente común, va en 1.0 mm por y 82.5. C_ID: tab de Q102 → R103.1. VOUT: R103.2 → tronco de 1.5 mm por x 102.6 → y 60 → L101.1.
  - C104 (B.Cu) se une por 2 vías. C105.1 se une por 3 vías y un tramo en B.Cu.
- **Kelvin de R103:** 2 pistas de 0.25 mm que salen de los pads del shunt y corren paralelas (0.55 mm) por debajo de C105, en y 70.15 (VOUT) y 70.95 (C_ID).
  - C_ID va a R104.2. VOUT va a CS- (pin 19) con un arco por B.Cu.
  - ISCP (pin 18) y C103 se unen a la Kelvin C_ID con otro arco por B.Cu, exterior al anterior.
  - CS+ (pin 20) → R104.1. C (pin 24) → R104.2.
- **Gates:**
  - HGATE (pin 14 → R105 → Q101.1) va paralela a OUT/VA (pin 15), 0.5 mm entre ejes, por x 128.78/129.28 y por y 82.3/82.85.
  - DGATE (pin 1 → Q102.1) va por B.Cu, justo debajo del retorno de A/VA (pin 2 → tronco VA).
- **+VPROT:** L101.2 → C106/C107 → C201 → diagonal → pad de C202 → VIN (pines 2 y 3) de U201. TP101 por vía.
- **Buck U201:**
  - SW de 3.7 × 1.2 mm hasta L201. C202.2 va directo por F.Cu al pin 1 y al pad expuesto. C201.2 → pad expuesto.
  - BOOT con C203. FB: pin 5 → R202 → R201, y la parte alta de R201 toma +5V en el pad de C204.
  - RT → R203. Vía a GND en cada pad de C204, C205 y C206.
- **+5V:**
  - C204 → C206. Tronco de 1.0 mm: C206 → x 147.7 → y 69.5 → x 137.6 → y 110.6 → x 147.3 → y 124.8 → x 143.5 → FB301.1 y y 131.6 → U301.
  - TP201 y TP301 por vía.
- **U301 (girado 180°):** SW (pin 2) al norte, hasta L301 por F.Cu. VIN (pin 3) → C302.1, pegado al oeste. GND (pin 1) por vía. EN, FB y PG salen al sur por F.Cu: nada pasa bajo el nodo SW.
- **3V3_D:** L301.2 → R302.1 → C304.1. FB alto desde C304.1 (→ C303.1 → R303.1). TP302 por vía.
- **U302 (LP5907, 3V3_A):** FB301 → IN/EN con C306, OUT → C307.1. GND del pin 2 por vía.

### Sin rutear, por red (288 en total)
GND_VEH 106 (etapa 5) · +3V3_A 16 · +3V3_D 14 · +5V_VEH 10 · GND_CAN 8 · VS 5 · MCU_RST_N 5 · SPI_MISO/SCK/MOSI 4 c/u · GNDISO_CAN 4 · USB_D+/D- 4 c/u · VEH_DO1/DO2 3 c/u · BUS_CAN_H/L 3 c/u · BOOT 3 · Net-(D704-K)/(D754-K) 3 c/u · VMON_5V/VMON_3V3 3 c/u · V_SOOUT/V_SOIN 3 c/u · PWR_FLT_N 3 · DO1_DIAG/DO2_DIAG 3 c/u · VBUS 3 · y ~45 redes con 1–2 (CAN_RX/TX/SILENT/STBY, CS_*, IMU_INT*, OV, UVLO, TMR, ILIM, CAP, SW, Net-(C109-Pad1), Net-(R108-Pad2), VAR_ID0–2, LED_G/R, WDI, CC1/CC2, U0TXD/RXD, PG_3V3D, EN_5V, CAN_RS, Net-(C609-Pad1), …).

Para regenerar la lista: correr el DRC (sección 8) y agrupar `unconnected_items` por red.

---

## 2. Reglas vigentes

### Net classes (`INCLI-VA.kicad_pro`; se asignan por patrón de nombre de red)
| Clase | Redes | Pista | Separación | Par (ancho / gap) | Vía |
|---|---|---|---|---|---|
| Default | resto | 0.2 | 0.2 | — | 0.6 / 0.3 |
| HV | `/10_power_input/VIN_VEH`, `/10_power_input/VBAT_F` | 1.0 | 1.25 | — | 0.6 / 0.3 |
| PROT | `/10_power_input/VA`, `/10_power_input/C_ID`, `/10_power_input/VOUT`, `+VPROT` | 1.0 | 0.6 | — | 0.6 / 0.3 |
| DO | `/VEH_DO1`, `/VEH_DO2` | 0.5 | 0.6 | — | 0.6 / 0.3 |
| 5V | `+5V_VEH`, `/20_buck_5v/BUCK_SW` | 0.5 | 0.2 | — | 0.6 / 0.3 |
| 3V3 | `+3V3_D`, `+3V3_A` | 0.4 | 0.2 | — | 0.6 / 0.3 |
| CAN | `/BUS_CAN_H`, `/BUS_CAN_L` | 0.3 | 0.2 | 0.3 / 0.3 | 0.6 / 0.3 |
| USB | `/40_mcu/USB_D+`, `/40_mcu/USB_D-` | 0.3 | 0.2 | 0.3 / 0.2 | 0.6 / 0.3 |

- **Board Setup:**
  - Piso cobre-cobre de 0.15 mm (`min_clearance`, JLCPCB).
  - Anchos predefinidos 0.2 / 0.25 / 0.3 / 0.4 / 0.5 / 0.6 / 1.0. Vía 0.6/0.3. Pares 0.3/0.3 y 0.3/0.2.
  - Teardrops activados en vías, pads PTH y SMD (formas redonda y rectangular).
- **El par CAN no se detecta como par diferencial:** KiCad reconoce pares solo por el sufijo `+/-` o `P/N`. **No renombrar las redes** (decisión del usuario). Se rutea acoplado a mano, 0.3/0.3.
- **USB 0.3/0.2:** aprobado. Es Full-Speed; la impedancia no está controlada.

### `INCLI-VA.kicad_dru`, regla por regla (en KiCad, si hay varias que coinciden, manda la última del archivo)
| Regla | Qué hace | Motivo |
|---|---|---|
| `Pads_mismo_encapsulado` | 0.15 mm entre pads de un mismo componente (`A.Parent == B.Parent`) | La separación la fija el encapsulado (QFN 0.5, SOIC, LGA). No hay una clearance general sin condición: anularía las net classes |
| `JLC_ancho_pista` | Pistas de ≥ 0.15 mm | Capacidad de JLCPCB |
| `JLC_via` | Vía con hueco ≥ 0.3, diámetro ≥ 0.6 y anillo ≥ 0.15 | Sin costo extra en JLC |
| `JLC_hueco_min` | Hueco ≥ 0.2 mm | Vías térmicas de U101/U201 |
| `JLC_anillo_PTH`, `JLC_hueco_a_hueco`, `JLC_hueco_a_cobre_via`, `JLC_hueco_a_cobre_PTH` | Mínimos de JLC | Capacidades de JLC |
| `JLC_borde` | Cobre a ≥ 0.5 mm del borde | Margen sobre los 0.2 de JLC |
| `JLC_serigrafia` | Texto de ≥ 0.8 mm, trazo de ≥ 0.15 | JLC |
| `U101_RTN_aislado` | La red `/10_power_input/U101_RTN` (EP de U101, sus vías y la isla en B.Cu) queda a ≥ 0.3 mm de todo y sin conexión a rellenos | TI SNOSDF6, tabla 5-1 y sección 8.3: unirla a GND anula la protección contra polaridad inversa |
| `U101_pad25_nunca_GND` | Error si el pad 25 de U101 cambia de red | Seguro |
| `H_anillo_cobre` / `H_zona_arandela` | Cobre a ≥ 0.5 mm del anillo de H1–H5; pistas y vías a ≥ 0.8 mm del anillo (≥ 4 mm del centro) | Arandela M3, anillo sin red |
| `HV_entrada_202V` | VIN_VEH/VBAT_F a ≥ 1.25 mm de otras redes (no aplica entre pads) | Load dump de 202 V sin suprimir; IPC-2221B B2, 171–250 V |
| `MV_salidas_DO_100V` | VEH_DO1/DO2 a ≥ 0.6 mm (no aplica entre pads) | IPC B2, 51–100 V (pico recortado por D701) |
| `ISO_CAN_barrera` | Dominio CAN (GND_CAN, BUS_CAN_H/L, V_SOIN, V_SOOUT, GNDISO_CAN, CAN_RS, Net-(C609-Pad1), pin 17 de U601) a ≥ 2.5 mm del resto, salvo dentro de U601 y J1 | Aislamiento funcional; IPC B2, 301–500 V |
| `ISO_sin_relleno_bajo_U601` | Sin rellenos dentro del courtyard de U601 | No achicar los 8.3 mm de CLR/CRP del encapsulado |
| `IPC2152_entrada_2A` | Pistas de VIN_VEH, VBAT_F, VA, C_ID, VOUT y +VPROT de ≥ 1.0 mm | IPC-2152, 2 A |
| `IPC2152_salidas_DO` | DO de ≥ 0.5 mm | Relé de ≤ 0.5 A |
| `IPC2152_buck_5V` | +5V y BUCK_SW de ≥ 0.5 mm | ≤ 1 A |
| `PROT_sensado` | Una pista PROT de ≤ 0.3 mm se trata como sensado: mínimo 0.25 mm | Kelvin de R103 y pines A/OUT/C de U101 (µA) |
| `PROT_sensado_entre_PROT` | Sensado PROT contra otra red PROT: 0.3 mm | La Kelvin VOUT/C_ID solo ve la caída del shunt (mV) |
| `PROT_zona_U101` | PROT dentro de `ZONA_U101`: 0.2 mm y pista de ≥ 0.25 (no aplica contra HV ni RTN, ni entre pads de un mismo componente) | Mismas tensiones que entre pines del VQFN, placa con coating (IPC B4) |
| `PROT_zona_buck_U201` | PROT dentro de `ZONA_BUCK_U201`: 0.25 mm (mismas excepciones) | Pedido del usuario: lazo de entrada del buck en F.Cu |
| `VA_compuertas_Vgs` | VA contra HGATE/DGATE: 0.2 mm | Solo hay Vgs (≤ 15 V) |
| `PROT_llegada_U101` | Dentro del courtyard de U101: 0.2 mm y 0.25 mm de pista | VQFN-24 de 0.5 mm |
| `PROT_llegada_U201` | +VPROT puede bajar a 0.6 mm dentro de U201, C202 o `ZONA_BUCK_U201` | Ancho del pin VIN |
| `J401_land_pattern_oficial` | NPTH-cobre de ≥ 0.19 mm dentro de J401 | Huella oficial GCT, aceptada por el usuario |

**Antena:** el keep-out viene en la huella de U401 (rule area de 48 × 21 mm, todas las capas, en x 191.94–212.94, y 91.50–139.50). Lo verifica el DRC nativo.

### Rule areas de la placa
| Nombre | Capas | Restringe | Coordenadas (mm, KiCad) |
|---|---|---|---|
| `BARRERA_CAN` | F + B | sin pistas, vías, pads ni rellenos (huellas sí) | Banda en "C" de 2.5 mm: polígono (99.5,110.37) (131.4,110.37) (131.4,140) (99.5,140) (99.5,137.5) (124.6,137.5) (124.6,112.87) (99.5,112.87). El tramo vertical x 124.6–131.4 pasa bajo el cuerpo de U601 |
| `APOYO_CAJA_B` | B.Cu | sin pistas, vías, pads ni huellas (relleno sí) | Círculo de Ø8 mm con centro en (163.5, 99.0) |
| `ZONA_U101` | F + B | ninguna (solo nombre para `PROT_zona_U101`) | x 113.8–134.4, y 64.2–84.4 |
| `ZONA_BUCK_U201` | F + B | ninguna (solo nombre para `PROT_zona_buck_U201` y `PROT_llegada_U201`) | x 124.0–151.0, y 52.0–69.0 |
| keep-out de antena (huella de U401) | todas | todo | x 191.94–212.94, y 91.50–139.50 |

---

## 3. Cambios de ubicación respecto de `placement-v1`
Todos autorizados por el usuario. Los aplica `scripts/ruteo/etapa1_potencia.py`.

| Pieza | placement-v1 | Ahora | Motivo |
|---|---|---|---|
| C104 (47 µF, VOUT) | F.Cu (138.5, 75.57) r-90 | **B.Cu** (106.85, 71.0) r0, pad 1 al oeste | En F.Cu no tenía camino a VOUT; ahora queda bajo C105/L101.1. Agrega 10.5 mm de altura abajo: separadores de ≥ 12 mm y adhesivo (requisitos de la caja) |
| U301 | (140.4, 135.81) r90 | (140.4, 135.81) **r270** (girado 180°) | SW sale hacia L301 sin cruzar VIN/EN/FB |
| C302 | (139.2, 139.5) r90 | (138.1, 135.875) r270 | Pegado al pin 3 (VIN) de U301 |
| TP101 (+VPROT, B.Cu) | (138.5, 65.5) | (127.6, 61.5) | Sobre el ramal de +VPROT hacia C202 |
| Referencia de U301 | — | serigrafía en (142.2, 132.8) | Al girar la pieza quedaba sobre R301 |
| TP301 (Codex, etapa 2 parcial) | B.Cu (140.0, 134.0) | B.Cu **(140.0, 131.6)**, r180 | Traslado autorizado al tronco +5V; retirada su bajada B.Cu bajo SW. Aplicado por `scripts/ruteo/etapa2_can.py` |

**Regla:** no mover ni rotar ningún otro componente sin preguntar al usuario. Si un ruteo lo necesita, anotar la propuesta en `docs/RUTEO_AGENTE.md` y esperar la decisión. El usuario replica los cambios en su copia manual.

---

## 4. Restricciones físicas (todas las etapas)
- **Barrera CAN:** ningún cobre cruza `BARRERA_CAN`, salvo los pads de U601 sobre su cuerpo. El dominio CAN (J1.3–5, D601, R602/R603/C609, R605, C607/C608, C610/C606, FB601, FB602) queda a la izquierda/abajo de la banda. GND_CAN propio, sin unirlo nunca a GND_VEH. Separación ≥ 2.5 mm (`ISO_CAN_barrera`).
- **Antena del ESP32-S3:** nada de cobre en el keep-out de la huella (x ≥ 191.94, y 91.5–139.5). La placa tiene un recorte allí.
- **Sensores:** **sin pistas ni vías bajo U501** (crt 154.96–163.65 × 99.45–106.54), **U502** (165.50–169.09 × 93.45–96.55) **ni U503** (146.10–153.90 × 97.20–102.80), en ninguna capa. El plano GND sí puede pasar por debajo.
- **Imán de ROT:** círculo libre de Ø17.9 mm con centro en el eje de U503 (150.0, 100.0), **en las dos caras**. Adentro solo U503 y sus pasivos: sin tornillería, sin H5 y sin el área B. El lado del imán todavía no está decidido.
- **Fijaciones H1 (105,55), H2 (195,55), H3 (105,145), H4 (195,145), H5 (156,88.5):** M3, anillo de 6.4 mm sin red. Pistas y vías a ≥ 4 mm del centro (`H_zona_arandela`); otro cobre a ≥ 0.5 mm del anillo.
- **Área B (`APOYO_CAJA_B`):** Ø8 mm en (163.5, 99.0), en B.Cu. Sin pistas, vías ni pads; el relleno de GND sí puede pasar.
- **Potencia y DO lejos de U503:** nada de potencia (+5V, VBAT/VIN, buck) ni DO a menos de 10 mm de U503.
  - Decisión del usuario (2026-10-29): medir los 10 mm desde el borde del cuerpo. Se acepta como única excepción el tronco existente de +5V (x 137.6), a 9.8 mm del cuerpo.
- **Conformal coating:** sí. Enmascarar J1, J2, J401 y J402 (zonas en `User.Comments`). Hay rótulos "SIN BARNIZ" en la serigrafía.
- **Fabricación:** JLCPCB, 2 capas, 1.6 mm, 1 oz. El prototipo se arma en la variante CAN + DO + ROT. El usuario suelda el ASM330 (LGA) con aire caliente y stencil, así que hay que pedir el stencil.

---

## 5. Plan de las etapas 2 a 6

### Etapa 2 — CAN
- **Bus (lado aislado, F.Cu):**
  - BUS_CAN_H/L: J1.3/J1.4 → D601 (DNP, huella reservada) → R602/R603 (terminación partida) y C609 → U601, pines 14 (H) y 13 (L).
  - Par acoplado a mano, 0.3/0.3, sin vías y con largos iguales.
  - Hay 3 segmentos de CAN_H/L en F.Cu que dejó el usuario antes de la etapa 0: conservarlos o rehacerlos.
- **Fuente aislada:**
  - V_SOOUT (pin 19) → C610 (220 nF) y C606 (10 µF) → FB601 → V_SOIN (pin 16) con C607 (10 nF) y C608 (100 nF).
  - GNDISO_CAN (pines 18/20) → FB602 → GND_CAN.
  - CAN_RS (pin 12) → R605 (0 Ω) → GND_CAN.
  - **Criterio de ruteo aprobado por el usuario (2026-10-29):** ≤ 2 mm de pista entre el pin y los desacoples cercanos C601, C604, C607, C608 y C610. C602/C603 (ubicados a ~4.7 mm) y C606 (~2.9 mm) se aceptan en cadena detrás del capacitor pequeño: pin → pequeño → grande, sin camino independiente desde el pin al grande. No mover estas piezas. Cada capacitor tendrá retorno corto a su propia red de masa.
  - **Valores y masas que se conservan del diseño:** C602 es de 100 nF (no 10 µF); C603, C605 y C606 son de 10 µF. C601–C605 retornan a GND_VEH, C607/C608 a GND_CAN y C606/C610 a GNDISO_CAN, antes de FB602. No unir directamente GNDISO_CAN con GND_CAN puenteando la ferrita.
- **Lado lógico:**
  - +5V (VCC, pin 3) → C604 (100 nF, a 1.1 mm) → C603 (10 µF). Sale del tronco de +5V en y 124.8: de (143.5, 124.8) hacia el oeste, a C603.1 / C604.1 por debajo.
  - +3V3_D (VIO, pin 4) → C601 (10 nF, a 1.1 mm) → C602 → C605. Llega desde la salida de U301 o desde el riel de 3V3 que se tienda en la etapa 3.
  - GND en los pines 1, 2, 9 y 10 con vías propias.
- **Señales a la MCU:**
  - CAN_TX (pin 7 → U401.24), CAN_RX (pin 5 → U401.25), CAN_STBY (pin 8 → U401.23, con pull-up R604) y CAN_SILENT (pin 6 → U401.35, con pull-down R601). TP404 = CAN_TX y TP405 = CAN_RX, en B.Cu.
  - **Salto reservado:** las cuatro cruzan el tronco de +5V (vertical en x 147.3, entre y 110.6 y 124.8). Pasan por B.Cu en ese cruce, con 2 vías cada una y tramos cortos. No mover el tronco.
- **Islas:** GND_CAN en las dos caras se hace en la etapa 5. Acá alcanza con dejar las vías de GND_CAN.
- **Aceptación:**
  - DRC 0 errores. Ningún cobre en `BARRERA_CAN`.
  - Par CAN acoplado de punta a punta, con diferencia de largo de ≤ 1 mm.
  - C601/C604/C607/C608/C610 a ≤ 2 mm de pista al pin; C602/C603/C606 en cadena conforme al criterio aprobado, con retornos cortos. Entregar tabla de distancias reales y diferencia de longitud CANH/CANL.
  - Las 4 señales completas hasta U401. Render de las dos caras.

### Etapa 3 — USB / MCU
- **USB_D+/D-:** J401 (A6/B6, A7/B7) → U402 (ESD) → U401. Par 0.3/0.2, **sin vías**, con diferencia de largo de ≤ 0.5 mm.
- **J401:** VBUS → protección y R403/R404 (CC1/CC2 a GND). SBU sin conectar.
- **ESP32-S3:**
  - +3V3_D a los pines 2 y otros VDD con C401 (22 µF) y C402 (100 nF) directo al pin.
  - EN (MCU_RST_N) corto, con C403 (a 1.3 mm del pin EN) y la red de U801 (RESET por R802).
  - BOOT (SW402), SW401 (reset).
  - U0TXD/U0RXD → J402 (header UART0).
  - Las VAR_ID (R805/R806/R807), los LED (D801/D802 con R803/R804) y WDI de U801 se pueden dejar para la etapa 4.
- **Riel +3V3_D:** de la salida de U301 (C304.1, en 151.0, 142.5) hasta la MCU (U401.2 en 189.18, 106.75) y hasta U601 (VIO). Usar 0.4–0.6 mm y evitar la zona de sensores.
- **Aceptación:**
  - DRC 0 errores. USB sin vías y acoplado.
  - Desacoples a ≤ 1 mm del pin. EN de ≤ 5 mm.
  - Nada en el keep-out de antena.

### Etapa 4 — Sensores y señales
- **SPI:**
  - SPI_SCK/MOSI/MISO desde U401 hasta U501 (SCL3300), U502 (ASM330) y U503 (AS5147U), con CS_INC, CS_IMU y CS_ROT. TP501–TP503 en B.Cu.
  - **Sin pistas ni vías bajo los sensores. SPI lejos del buck U201 y de L201/L301.**
- **+3V3_A:**
  - Desde C307.1 (154.56, 128.5), salida de U302, hasta C501/C504 (U501), C505/C506 (U502), C503 (U503) y R501–R503. TP303 (162.5, 135.5) en B.Cu.
  - IMU_INT1/2, SCL_AEXTC/DEXTC.
- **Salidas DO (DO1/DO2):** VEH_DO1/DO2 hasta J2 (net class DO: 0.5 / 0.6 mm), EN_5V, DO*_EN, DO*_DIAG, D704/D754 y R7xx. Nada de DO a menos de 10 mm de U503.
- **Supervisión:** U801 (WDI, RESET, VMON_3V3/VMON_5V con R305–R308), LED_G/LED_R, VAR_ID0–2 y PG_3V3D (R302.2 → TP305 en (151, 148), B.Cu → MCU).
- **Periféricos de U101** (todo dentro de `ZONA_U101`; los saltos ya están reservados):
  - **SW** (pin 3) → R106.1: F.Cu recto hacia el oeste.
  - **UVLO** (pin 4): va al oeste por el hueco entre R106 y C109 (y ≈ 74.6), sube por x 118.9 y entra a R106.2 por la izquierda. El enlace R106.2 ↔ R107.1 cruza el par Kelvin (y 70.15/70.95, en el hueco R107/R106), así que **salta por B.Cu**: vía junto a R107.1 en (119.0, 69.3) y otra al final de la subida.
  - **OV** (pin 5): baja por x 122.2 hasta R109.1. Desde R109.1, vía en (121.85, 79.7) → B.Cu hacia el sur por x 121.85 hasta y 85.0 → al este hasta una vía en (134.3, 85.0) → F.Cu hasta R112.2 (135.9, 92.28). Falta también R108.2 ↔ R112.1 (Net-(R108-Pad2)).
  - **TMR** (pin 9) → C110.1: recto hacia abajo.
  - **ILIM** (pin 11) → R110.1: por F.Cu, baja por x 126.15 y va al este por y 77.95, al oeste de HGATE.
  - **FLT** (pin 12) → R111.2 y TP104 → MCU: cruza HGATE/OUT (x 128.78 y 129.28), así que salta por B.Cu (vía junto al pin 12, en ≈ (126.95, 77.25); vía en ≈ (130.0, 77.9) y F.Cu hasta R111.2).
  - **EN/MODE** (pines 6/7, unidos a VS):
    - Tramo en la esquina por F.Cu: (123.3, 75.25) → (123.3, 76.2) → pin 7.
    - Vía en (123.3, 76.9), B.Cu hacia el norte por x 123.4 hasta y 69.85, y al este hasta la vía de VS.
  - **CAP** (pin 23) → C108.1: vía en (124.45, 70.55) → B.Cu en "U" por y 71.35 → vía en (126.87, 70.1) → C108.1.
  - **VS** (pin 22) → C108.2: vía en (125.25, 70.25) → B.Cu por y 69.4 → vía en (128.42, 70.1) → C108.2 → C102.1 por F.Cu.
  - **VS → D104.3:** F.Cu desde C108.2 al este por y 69.0 hasta x 133.2, abajo hasta y 84 y a D104.3 (131.0, 84.67). Ya no cruza OUT, que ahora baja por x 129.28.
  - Todas estas vías quedan **dentro** del arco VOUT en B.Cu (x 117.6–129.4, y 66.6–71) y lejos del arco C_ID (x 116.6–130.53, y 65.6).
  - **GND:** pin 13 → vía en (127.75, 76.55); pin 16 → vía en (128.55, 73.4).
  - **Vías GND de la fila R109–R111:** R109.2 → vía en (122.6, 81.5); C110.2 → (125.42, 81.4); R110.2 → (127.97, 81.4). R107.2 y C109.2 llevan vía propia.
  - **R111.1 (+3V3_D):** sale al este por F.Cu (está fuera de los risers de HGATE/OUT).
  - **R105.2 ↔ C109.1** (Net-(C109-Pad1)): enlace corto vertical.
- **Aceptación:**
  - DRC 0 errores. Ninguna pista ni vía bajo U501/U502/U503.
  - Círculo de Ø17.9 mm libre de piezas ajenas.
  - Potencia y DO a ≥ 10 mm de U503 (con la métrica que fije el usuario).
  - SPI a ≥ 10 mm de L201/U201/L301.

### Etapa 5 — Planos
- **B.Cu:** relleno GND_VEH en toda la placa, salvo la isla CAN, la isla RTN de U101 (la regla ya la aísla) y el keep-out de antena. Prioridad baja; el área B admite relleno.
  - Debe quedar continuo bajo el buck y bajo los sensores.
  - Bajo `ZONA_U101` va a quedar en islas por los saltos: coserlas con vías.
- **F.Cu:** relleno GND_VEH donde haya lugar.
- **Isla GND_CAN** en las dos caras dentro del dominio CAN, cosida, sin relleno bajo U601 (`ISO_sin_relleno_bajo_U601`).
- **Costura:** cada 5–10 mm, alrededor del ESP32 (fuera del keep-out de antena) y en el borde de la isla CAN, del lado CAN.
- **Conexión a pads:** alivios térmicos en los pads (soldadura a mano). Conexión sólida en los pads expuestos (U201 EP y vías del EP).
- **Las 19 vías GND sueltas de la etapa 1 tienen que quedar conectadas al plano:** C101, D102, D103, C103, C106, C107, R203, C204–C206, U301 pin 1, C302, C301, C304, R304, U302 pin 2, C306 y C307.
- **Aceptación:**
  - DRC 0 errores, sin `via_dangling` ni islas sin conectar (`isolated_copper`).
  - GND_VEH sin unir a GND_CAN ni a U101_RTN. Rellenos recalculados.

### Etapa 6 — Cierre
- DRC y paridad en 0. Revisar retornos de corriente: buck, U301, CAN e islas bajo U101.
- **Teardrops:** generarlos (Edit → Edit Teardrops, o por la API) y repetir el DRC.
- **Fabricación de prueba para JLCPCB en `fab/`:** Gerbers, drill, BOM y CPL con kicad-cli (`pcb export gerbers`, `pcb export drill`, `pcb export pos`, `sch export bom`).
  - La BOM sale del campo `DNP` y la variante de prototipo es CAN + DO + ROT.
  - Incluir el stencil.
- **Aceptación:** DRC 0 / paridad 0 / ERC sin cambios. Los archivos de `fab/` se generan sin errores. Renders finales.

---

## 6. Compromisos ya aceptados (no "arreglar" sin preguntar)
- **Zona U101:** ~11 vías y tramos cortos en B.Cu (aceptado). El plano bajo U101 va a quedar en islas cosidas.
- **C201 (4.7 µF):** llega a VIN por la diagonal y el pad de C202 (8.6 mm), porque el retorno directo de C202 ocupa el paso por el oeste del pin 1.
  - Lazo de C202: 3.9 mm² (antes 6.1). Lazo de C201: 26.4 mm² (antes 31.3).
- **U301:** el GND del pin 1 y el de C302 bajan al plano por vías propias. El lazo de entrada mide ~5 mm² (antes 6.1, con VIN cruzando por B.Cu).
- **TP301** (+5V, B.Cu, originalmente en (140, 134)): traslado autorizado por el usuario (2026-10-29), fuera de la proyección del SW de U301 y sobre el tronco +5V, para permitir GND continuo bajo SW. Aplicarlo en la etapa 2 y registrar coordenadas antes/después en «Cambios de ubicación».
- **Gates:** HGATE mide ~17 mm y DGATE ~25 mm por la ubicación de U101, pero cada uno va paralelo a su retorno (VA).

---

## 7. Trampas conocidas
1. **pcbnew sobrescribe el `.kicad_pro`.** `LoadBoard()` de un PCB fuera de la carpeta del proyecto, seguido de `Save()` dentro del proyecto, reemplaza `INCLI-VA.kicad_pro` con valores por defecto: se pierden net classes y patrones.
   - Cargar siempre `INCLI-VA.kicad_pcb` del proyecto. Para partir de una versión anterior: `git show <rev>:INCLI-VA.kicad_pcb > INCLI-VA.kicad_pcb` y después correr el script sobre ese archivo.
2. **Una regla de clearance sin condición** en la `.kicad_dru` anula todas las clearances de las net classes. El piso de fabricación va en Board Setup.
3. **Expresiones DRC en KiCad 10:**
   - Funcionan `A.NetClass == 'PROT'`, `A.Width <= 0.3mm`, `A.insideArea('NOMBRE')` y `A.Parent == B.Parent`.
   - `A.Track_Width` no coincide con nada.
   - Si `A.NetClass` "no funciona", seguramente se perdió el `.kicad_pro` (trampa 1).
4. **Antes de cada commit:** `git diff INCLI-VA.kicad_pro`. KiCad reordena las net classes alfabéticamente, y eso es inofensivo. Cualquier otro cambio hay que revisarlo.
5. **KiCad cerrado** (sin `~INCLI-VA.kicad_pro.lck` ni editores abiertos) antes de editar archivos con scripts. Si estaba abierto, que el usuario recargue.
6. La última regla que coincide manda: las excepciones van **después** de las reglas generales en la `.kicad_dru`.
7. `kicad-cli pcb drc` reescribe a veces el `.kicad_pro` (orden de clases). Ver la trampa 4.

---

## 8. Cómo verificar
```bash
cd PCB_INCLI_VA        # carpeta del proyecto, rama ruteo-agente
# Regenerar la etapa 1 desde la etapa 0 (solo si hace falta rehacerla):
git show 36bf77f:INCLI-VA.kicad_pcb > INCLI-VA.kicad_pcb
/usr/bin/python3 scripts/ruteo/etapa1_potencia.py INCLI-VA.kicad_pcb INCLI-VA.kicad_pcb
# DRC + paridad (JSON):
kicad-cli pcb drc --schematic-parity --severity-all --format json -o output/drc_report.json INCLI-VA.kicad_pcb
# ERC:
kicad-cli sch erc --severity-all --format json -o output/erc_report.json INCLI-VA.kicad_sch
# Renders:
kicad-cli pcb render --side top    --width 1600 --height 1600 --quality basic -o docs/layout/ruteo/etapaN-top.png    INCLI-VA.kicad_pcb
kicad-cli pcb render --side bottom --width 1600 --height 1600 --quality basic -o docs/layout/ruteo/etapaN-bottom.png INCLI-VA.kicad_pcb
# Vista ampliada de una zona: el PDF tiene el mismo origen que KiCad, así que 1 mm = DPI/25.4 px.
kicad-cli pcb export pdf --layers F.Cu,B.Cu,F.Fab,Edge.Cuts --mode-single -o /tmp/v.pdf INCLI-VA.kicad_pcb
# zona x0..x1, y0..y1 (mm) a 600 dpi: -x = x0*600/25.4, -y = y0*600/25.4, -W = (x1-x0)*600/25.4, -H = (y1-y0)*600/25.4
pdftoppm -png -r 600 -x 2976 -y 1488 -W 850 -H 520 -singlefile /tmp/v.pdf zona   # ejemplo: x 126-162, y 63-85
```
- En el JSON del DRC: `violations` (filtrar `severity == "error"`), `unconnected_items` y `schematic_parity`.
- Script de la etapa 1: `scripts/ruteo/etapa1_potencia.py`. Funciones `T(red, ancho, puntos, capa)` y `V(red, x, y)`, y aplica los cambios de ubicación de la sección 3. Se puede usar de modelo para las etapas siguientes: un script por etapa que parta del commit de la etapa anterior.
- Historial y detalles por etapa: `docs/RUTEO_AGENTE.md`. Estado general: `docs/PENDIENTES.md`.

---

## 9. Decisiones registradas y pendientes (2026-10-29)
1. **U503:** 10 mm desde el borde del cuerpo; excepción aceptada del tronco +5V existente a 9.8 mm.
2. **Imán ROT:** lado sin definir; mantener libre el círculo de Ø17.9 mm en ambas caras, salvo U503 y sus pasivos previstos.
3. **C105 PROD (EEE-FK1H102AV):** confirmar stock en la revisión del BOM; no bloquea el ruteo. La huella J16 antivibración ya acepta EEE-FK1H102AM.
4. **TP301:** traslado autorizado fuera de la proyección del SW y sobre el tronco +5V; anotar el cambio de ubicación al aplicarlo.
5. **Terminación CAN:** R602/R603/C609 montadas en PROTO; en PROD se definen según instalación.
6. **Desacoples de U601:** criterio y conexiones en cadena aprobados en la sección 5, etapa 2. No cambiar ubicación, valores ni redes.
7. **Alcance autorizado:** solo etapa 2. Al cerrarla: DRC, paridad, renders de ambas caras, tabla de distancias de desacoples y diferencia CANH/CANL, commit `[Codex]`, `git push origin ruteo-agente` y esperar visto bueno antes de la etapa 3.
8. Cualquier otro movimiento o giro de componentes, cambio de reglas o net classes, renombre de redes o edición del esquemático requiere consulta previa.
9. Los MPN marcados "a verificar" en `docs/PENDIENTES.md` se revisan antes de generar la BOM final.

### Hallazgos durante la etapa 2 — pendientes de decisión
- **Estado parcial:** fuente aislada, desacoples y cuatro señales lógicas completos; TP301 trasladado. DRC 0 errores / paridad 0 / 262 conexiones pendientes. Detalle, medidas y renders en `docs/RUTEO_AGENTE.md`. La etapa 2 no está cerrada.
- **C608:** el trazado mide 2.145 mm entre bordes reales del cobre. Es el mínimo geométrico con los pads redondeados actuales; los ~1.99 mm del traspaso ignoraban las esquinas redondeadas. Solicitada excepción ≤2.15 mm, todavía no aprobada. No mover el capacitor ni declarar cumplidos los 2 mm.
- **CANH/CANL:** orden H/L invertido entre D601 y U601. Solicitado puente corto B.Cu con dos vías de una señal; todavía no aprobado ni aplicado. Si se exige conservar «sin vías», revisar propuesta de ubicación antes de mover cualquier componente. Longitudes del bus pendientes de ruteo completo.
