# Estudio de tamaño y ubicación — Codex, actualizado 2026-10-28 (últimas secciones: Claude Code, 2026-10-29)

## Fijaciones H1–H5, apoyo opcional y serigrafía — Claude Code, 2026-10-29

Pedido del usuario (KiCad cerrado del todo, sin `.lck`). **Sin ruteo.** Script: `scripts/layout_bloques/h5_serigrafia.py` (se aplica sobre el PCB de `358ac73` más los 5 segmentos de CAN_H/CAN_L que el usuario borró sin commit). Reporte: `layout/reports/h5-serigrafia.json`. Vistas: `layout/h5-serigrafia-top.png` y `-bottom.png`.

**Verificación:**
- DRC (`layout/reports/drc-h5-serigrafia.json`): 0 errores; solo los 3 avisos conocidos de U401. Paridad 0; 358 conexiones sin rutear (356 + las 2 de CAN que borró el usuario).
- ERC (`layout/reports/erc-h5.json`): 0 errores. Avisos: el conocido `isolated_pin_label` U101_RTN y 4 `pin_to_pin` en `40_mcu`. Estos 4 vienen del símbolo de SW401/SW402 que cambió el usuario (pines "Unspecified" contra GND_VEH y TP401/TP402). Son inofensivos y no se tocaron.
- `sch_visual_qa` de la raíz: PASS (solo INFO, cajetín sin "company").

**1. Agujeros de fijación.**
- H1–H4 (sin mover) y H5 nuevo en (56.0, 38.5), todos con `MountingHole:MountingHole_3.2mm_M3_Pad`.
- Agujero metalizado de 3.2 mm. La huella oficial trae un anillo de **6.4 mm** (no 6.0) en ambas caras. Se usa tal cual, sin modificar la librería.
- Símbolo `Mechanical:MountingHole` sin pin: el pad queda **sin red** (flotante), así que no une GND_VEH ni GND_CAN. Se actualizaron MPN, Notes y la nota de la raíz.
- H5 es opcional: sirve si la caja lleva un poste con inserto M3 en ese punto.
- Reglas nuevas en `INCLI-VA.kicad_dru`:
  - `H_anillo_cobre`: pads y rellenos a ≥ 0.5 mm del anillo.
  - `H_zona_arandela`: pistas y vías a ≥ 0.8 mm del anillo, es decir, a ≥ 4 mm del centro, en ambas caras.
- Margen actual al courtyard más cercano:

| Agujero | Cara superior | Cara inferior |
|---|---|---|
| H1 | C105, 2.6 mm | — |
| H2 | R708, 4.6 mm | — |
| H3 | J1, 9.1 mm | — |
| H4 | U401, 2.1 mm | — |
| H5 | C507, 3.1 mm | TP504, 3.0 mm |

**2. Apoyo opcional (opción B).**
- Rule area `APOYO_CAJA_B`: círculo de Ø8 mm en B.Cu, en (63.5, 49.0).
- Prohíbe pistas, vías, pads y huellas. El relleno (plano de masa) sí puede pasar.
- Sirve si la caja lleva un apoyo con buje y pad de goma.

**3. Eje de ROT (U503 en 50, 50).**
- El lado del imán **sigue sin definir** (el pedido traía la plantilla sin elegir), así que se dejan libres las dos caras.
- Distancias desde el eje: H5 a 12.97 mm (borde de la zona de arandela a 8.97 mm) y área B a 13.54 mm (borde a 9.54 mm).
- Entonces queda libre de H5 y de B un círculo de **Ø17.9 mm** alrededor del eje, en las dos caras.
- En la cara inferior no hay ningún pad a menos de 12 mm del eje (los TP más cercanos son TP504 y TP503, a 16.8 y 18 mm).
- En la cara superior el imán va sobre U503: lo limita la altura de las piezas vecinas (C507, R503, U501, U502), no H5 ni el área B.
- Un portaimán de más de Ø17.9 mm chocaría con la arandela de H5. En ese caso, H5 queda sin montar.

**4. C206 (aceptado por el usuario: 12.8 mm al EP).** En el ruteo:
- C204, C205 y C206 llevan cada uno su vía a GND junto al pad de GND.
- Plano GND_VEH continuo en B.Cu desde esas vías hasta las vías térmicas del pad expuesto de U201, sin cortes.

**5. Serigrafía** (toda en 0.8 × 0.8 mm con trazo de 0.15 mm, a ≥ 0.2 mm de pads, vías y otra serigrafía):
- **Barrera CAN, en las dos caras.** Línea de trazos (1.0 / 0.5 mm) por el centro de la banda `BARRERA_CAN`: y = 61.62 (del borde a U601), x = 28.0 (bajo el cuerpo de U601) e y = 88.75. Rótulo "CAN AISLADO" dentro del dominio CAN, en (19.0, 86.5).
  - Cara superior: 48 trazos; se omiten 9 donde pisarían la carcasa de J1 o la referencia de U601.
  - Cara inferior: 57 trazos, sin omisiones.
- **Pinout de J1**, en vertical en x = 11.7 junto a cada pin y en las dos caras: VIN, GND, CANH, CANL y GND_CAN.
  - Arriba, VIN se corre a y = 55.5 para no pisar el triángulo del pin 1.
  - La referencia J1 pasa debajo de la carcasa, a (6.0, 83.4).
- **Pinout de J2**, en las dos caras, en la franja libre bajo la carcasa (y = 11.38): DO1 y DO2.
  - Arriba, DO1 queda en x = 80.0, a la derecha del triángulo del pin 1.
- **Polaridad y pin 1:** se revisaron todas las huellas polarizadas (diodos, LEDs, Q, U, C104/C105 con "+", J1, J2 y J402). Todas traen la marca en su serigrafía; no hizo falta agregar nada.
- **Nombre de la placa**, cara inferior: "INCLI-VA  Rev A  2026-10-29" en (45.0, 76.0).
- **Rótulos de zona** (cara superior, solo donde había lugar libre): ENTRADA (10.0, 32.75), BUCK 5V (46.25, 20.5), SALIDAS DO (75.25, 30.0) y SENSORES (52.0, 62.5). Se omitió "MCU": el módulo ya se identifica solo y no había hueco junto a él.

## Correcciones aplicadas sobre `1ff3419` — Claude Code, 2026-10-29

Pedido del usuario: puntos 1–3 de la revisión (C104 se deja como está), referencias de 0.8 / 0.8 / 0.15 mm, courtyards a 1 mm (0.5 mm para pasivos pegados a su IC) y propuesta de rigidez para los sensores. **Sin ruteo.** Script: `scripts/layout_bloques/fix_1ff3419.py` (se aplica sobre el PCB de `1ff3419`). Vistas: `layout/correcciones-1ff3419-top.png` y `-bottom.png`.

**Verificación** (`layout/reports/drc-correcciones-1ff3419.json`): 0 errores; avisos solo los 3 conocidos de U401 (2 de serigrafía en el borde y `lib_footprint_mismatch`). Paridad 0 y 356 conexiones sin rutear. Ninguna pieza en el keep-out de antena ni en la barrera CAN.

**1–3. Movimientos** (distancia borde de pad a pin, antes → ahora):

| Pieza | Cambio | Antes → ahora |
|---|---|---|
| C403 (1 µF, EN) | (87.0, 53.5) vertical, sobre el pin 3 de U401. R805/R806 (VAR_ID) se corren a x 84.5 / 81.9 | 43.9 → **1.3 mm** |
| C202 (100 nF, VIN) | (29.27, 13.2) vertical, a la izquierda de U201: +VPROT junto a los pines 2/3 y GND junto al pin 1. C102 se corre 1.4 mm a la izquierda | VIN 4.7 → **1.06**, GND 3.2 → **1.06 mm** |
| C201 (4.7 µF) | (32.34, 7.9), detrás de C202 | VIN 7.6 → 3.7, GND 6.1 → 2.2 mm |
| C204/C205/C206 | Columna vertical a la derecha de C203 (x 42.6 / 46.0 / 49.4, y 13.2), +5V arriba hacia el pad 2 de L201. R201 a (42.9, 17.45) | GND al EP: 13.9 / 12.3 / 11.6 → **6.0 / 9.4 / 12.8 mm** |
| J401 | −0.4 mm en x (97.32, 30.52). Las ranuras SH quedan a 0.7 mm del borde y la boca asoma ~1.5 mm | 2 errores `copper_edge_clearance` → 0 |

- **C206 no mejora:** L201 está entre U201 y la salida, y C104 (que se deja quieto) cierra la zona de abajo. Para acercar las tres habría que rotar U201/L201 y rehacer el bloque. Para el ruteo: vías a B.Cu en el GND de cada C20x y en el EP, y el plano GND_VEH continuo entre ellos, sin cortes.
- MCU_RST_N sigue largo (54 mm de árbol), porque SW401 y R401 quedan abajo por decisión del usuario. El RC ya está en el pin.

**4. Courtyards.** Se corrigieron los 37 pares salvo los de abajo.
- A mano: columna R107/R106/C109/R105 subida a paso de 4.05 mm (había lugar libre sobre R107) y fila R109/C110/R110/R111 a paso de 2.55 mm.
- Empuje automático (≤ 1.45 mm): R202 0.7, C401 1.45, R304 0.55, C801 0.45, FB301 0.4, R301/R108 0.35, C108 0.3, R302 0.25, R803/R804 0.2, D104 0.15, y D101/R401/C303 0.05 mm.
- Efectos: R107 queda a 5.0 mm de UVLO (antes 3.0; divisor, no crítico) y C401 (bulk de +3V3_D) a 5.3 mm (antes 4.1).

| Par | Separación (mm) | Por qué queda así |
|---|---:|---|
| C403–C402 | 0.70 | Desacoples de U401 (EN y 3V3) entre R805 y el keep-out de antena; no hay más lugar sin alejar uno de los dos del pin. **Único par fuera del criterio** |
| C202–U201 | 0.56 | Desacople del IC (≥ 0.5) |
| C402–U401 | 0.57 | Desacople del IC (≥ 0.5) |
| C306–U302 | 0.62 | Pasivo del IC (≥ 0.5) |
| C801, R801, R802–U801 | 0.68 / 0.68 / 0.73 | Pasivos del IC (≥ 0.5) |
| R805, R806, R807–U401 | 0.75 / 0.75 / 0.81 | Puentes de VAR_ID conectados al IC (≥ 0.5) |
| C403–U401 | 0.78 | Desacople del IC (≥ 0.5) |
| R202, C203–U201 | 0.93 / 0.93 | Pasivos del IC (≥ 0.5) |
| C401–U401 | 0.99 | Desacople del IC (≥ 0.5) |

**5. Serigrafía.** Todas las referencias en 0.8 × 0.8 mm con trazo de 0.15 mm, a 0° o 90°.
- Arriba van en F.Silkscreen; los TP en B.Silkscreen, espejadas.
- Nunca sobre pads ni sobre la serigrafía de otra pieza (ni de la propia), ni sobre el cuerpo de otra pieza. No hay vías todavía.
- `INCLI-VA.kicad_dru` → `JLC_serigrafia`: alto mínimo 0.8 mm y trazo 0.15 mm.
- El `${REFERENCE}` propio de R103 (0.8 / 0.12 en F.Silkscreen) pasó a F.Fab, porque duplicaba la referencia.
- Los valores RESET/BOOT de SW401/SW402 quedan como estaban (1.0 / 0.15).
- **Solo en F.Fab (no entran junto a su pieza sin pisar pads ni cuerpos vecinos):**
  - U101: rodeado por sus pasivos a ≤ 1.3 mm.
  - R106: columna del UVLO.
  - R202: entre U201, C203 y R201.
  - C607, C610 y R602: columna de la isla CAN.
  - R303: junto a L301.
  - Q701: entre J2, D701 y D704.
- Los rótulos de zona, el pinout de J1/J2 y la línea de barrera CAN **no** se agregaron (propuesta sin aprobar).

**Rigidez de los sensores sin H5 (propuesta, no aplicada).** Distancias desde el centro de cada pieza; eje de ROT en U503 (50, 50).
- **Opción A, agujero M3 en (56.0, 38.5):** `MountingHole_3.2mm_M3`, NPTH, sin cobre.
  - Distancias: 14.9 mm de U501, 13.0 mm de U502 y 13.0 mm del eje de ROT.
  - Margen libre: 2.8 mm al courtyard más cercano en las dos caras (pasan el courtyard de Ø6.9 mm y la arandela).
  - Requiere agregar el símbolo en el esquemático (H5) y un separador plástico.
  - Queda entre los sensores y el bloque DO, sin cortar el camino del SPI hacia el ESP32.
- **Opción B, apoyo de la caja en B.Cu en (63.5, 49.0), Ø8 mm:** prácticamente en el centroide de U501/U502, a 13.5 mm del eje de ROT y con 3.7 mm de margen a los TP inferiores (TP503/TP504).
  - Se reserva con una rule area en B.Cu (sin vías, pistas de señal ni piezas). El plano GND puede pasar.
  - La caja apoya un buje con pad de goma.
  - No necesita cambios en el esquemático, pero depende del diseño de la caja.
- En las dos opciones, confirmar de qué lado queda el imán de ROT (pregunta 17), para no invadir su zona.

## Revisión de la ubicación del usuario (commit `1ff3419`) y reglas para el ruteo — Claude Code, 2026-10-28

Cambios del usuario: SW401/SW402 a `SW-SMD_L3.9-W3.0-P4.45`, H5 retirado (quedan H1–H4 en las esquinas), reubicación de entrada, buck, 3,3 V, CAN, MCU y supervisión, y referencias pasadas a F.Silkscreen. Sin revisar todavía: USB, salidas DO y sensores.

**Verificación** (`kicad-cli` 10.0.7, solo lectura; KiCad estaba abierto):
- Paridad con el esquemático: 0. Sin rutear: 356.
- Errores: 2 `copper_edge_clearance` en J401 (ver USB).
- Avisos: 92 + 92 `text_height`/`text_thickness`; las referencias en F.Silkscreen miden 0.7 / 0.12 mm y la regla `JLC_serigrafia` pide 1.0 / 0.15 mm. Además, 2 avisos de serigrafía de U401 en el borde y 1 `lib_footprint_mismatch` de U401, todos conocidos.
- Courtyards: ninguno se superpone, pero 37 pares quedan a menos de 1 mm (regla de soldadura a mano de AGENTS.md). Los peores: R202–C203 0.30, C401–U401 0.35, R109–C110, C110–R110 y R110–R111 0.38, R304–R303 y R805–R806 0.45 mm.

**Lo que mejoró** (distancia del borde del pad al pin, antes → ahora):
- U101: R106 4.7 → 2.4, R110 3.3 → 1.9, C110 3.2 → 1.9, C103 2.4 → 1.8 mm. El flujo J1 → F101 → D102/D101 → Q101/Q102 → U101 → L101 queda corto y en orden.
- C203 (BOOT) 3.1 → 1.4 mm, L201 → SW 5.3 → 3.4 mm.
- C402 → U401 1.3 mm; C801 → U801 1.2 mm.
- SW402 (BOOT) ya no está junto a la IMU. RESET y BOOT quedan juntos en el borde inferior y rotulados.

**Lo que empeoró y hay que corregir antes de rutear:**
1. **C403 (1 µF del EN)** se fue con el pulsador: está a 44 mm del pin 3 de U401, y MCU_RST_N pasa de 18 a 52 mm de árbol. El RC de EN tiene que quedar en el pin (Espressif: R 10 k + C 1 µF junto a CHIP_PU). SW401 y R401 pueden quedar abajo; **C403 vuelve junto al pin 3**.
2. **Lazos del buck U201:**
   - C202 (100 nF de VIN) 1.6 → 4.7 mm y C201 4.2 → 7.6 mm. El lazo caliente es C202 → VIN (3) → GND/EP: tiene que quedar pegado a los pines 3 y 1.
   - C204–C206 (salida) quedan a 12–14 mm del GND de U201 (antes 4.4). Su GND tiene que volver al EP por cobre corto y no por el plano bajo L201.
   - Propuesta: C202 junto a los pines 3/1, C201 detrás, y C204–C206 en fila al lado de L201 con su GND hacia U201.
3. **C104** (VOUT del LM74930) 6 → 10.5 mm del pin 19. Es bulk, así que es aceptable; acercarlo si queda espacio.

**USB (J401), sin revisar por el usuario:**
- Las ranuras traseras del blindaje (SH, x = 98.8 mm) llegan a 99.7 mm, a 0.3 mm del borde. Por eso salen los errores de `JLC_borde` (0.5 mm). **Correr J401 0.3–0.5 mm hacia −x**: el frente del receptáculo sigue asomando ~1.5 mm, que es lo que conviene para que entre el cable a ras de la caja.
- Reglas: conector en el borde con la boca hacia afuera; U402 (ESD) entre el conector y el MCU, a ≤ 5 mm de J401 y antes que cualquier derivación; D+/D- en par diferencial (90 Ω), sin vías, por encima de un plano GND continuo, y sin cruzar SPI ni el buck; resistencias de CC junto a J401; J401 fuera del keep-out de antena (hoy a 13 mm, bien).

**Sensores: por qué están en el centro y qué reglas seguir:**
- **Por qué esa zona:**
  1. La variante ROT exige U503 (AS5147U) sobre el eje del pivote, con la placa centrada en él (decisión de esquemático). Por eso U503 está en (50, 50).
  2. U501 (SCL3300) y U502 (ASM330) van junto a U503 para que los tres midan el mismo cuerpo rígido.
  3. Lejos de las fuentes de calor y de campo (L101, L201, L301, U101, U201, C105) y de los conectores, donde el cable tira y flexiona la placa.
- **Contra:** sin H5, el centro es el punto de máxima flexión entre H1–H4 (90 mm de luz). En un chasis con vibración, la IMU y el inclinómetro ven el modo propio de la placa. Opciones: (a) volver a poner un apoyo intermedio cerca de los sensores que no choque con el eje ROT; (b) fijar la placa por más puntos en la caja; (c) aceptarlo y validarlo en el ensayo de vibración. **Decisión del usuario.**
- **Reglas:**
  - Los ejes de U501 y U502 alineados con los bordes de la placa (rotación 0/90/180/270), con la misma orientación entre ellos, y con flechas X/Y en la serigrafía.
  - Sin vías ni pistas bajo el LGA del ASM330 ni bajo el DFL del SCL3300; plano GND continuo debajo, en B.Cu.
  - A más de 10 mm de los pulsadores, de los TP con punta y de cualquier pieza que se golpee.
  - El retorno de +3V3_A (U302) llega por su propia pista, sin compartir camino con el buck.
  - Para ROT: zona libre de cobre y de piezas altas en la cara del imán (pendiente, pregunta 17).

**Serigrafía propuesta** (F.Silkscreen, 1.0 mm / 0.15 mm como mínimo):
- **Rótulos de zona:** "ENTRADA 12/24 V", "BUCK 5 V", "3V3", "CAN AISLADO", "DO1 / DO2", "ESP32-S3", "SENSORES", "USB", cada uno en un lugar libre de su bloque.
- **Pinout en los conectores:** J1 "V+ GND CANH CANL CGND" y J2 "DO1 DO2", junto a cada pin.
- **Barrera CAN:** línea discontinua sobre el borde de la rule area `BARRERA_CAN` en F.Silkscreen y en B.Silkscreen, con "AISLADO — NO PUENTEAR" del lado del bus y el símbolo de aislamiento. Hoy la barrera no se ve en la placa.
- **Sensores:** flechas X/Y (y Z con un punto) junto a U501 y U502, y la marca del eje del pivote en U503.
- **Placa:** nombre, revisión y fecha ("INCLI-VA rev A 2026-10").
- **Referencias:** hoy miden 0.7 / 0.12 mm, por debajo de la regla del proyecto. Opciones: (a) subirlas a 1.0 / 0.15 donde quepan y mover a F.Fab las que no; (b) bajar la regla a 0.8 / 0.15 si JLCPCB lo acepta. Faltan pasar a F.Silkscreen las de USB, DO y sensores (56 todavía en F.Fab).

## Reacomodo por bloques (referencia UG-230 / INCLIMAX) — Claude Code, 2026-10-28

Pedido del usuario: cada conector en el borde con su circuito pegado, en el orden en que fluye la potencia o la señal (fotos en `docs/reference/`). Aplicado sobre **`INCLI-VA.kicad_pcb`**. Sin ruteo. Vista: **`layout/reacomodo-antes-despues.png`** (coloreada por hoja; los TP de la cara inferior en línea punteada). Las vistas `ubicacion-100x100*` y `placa-100x100*` quedan como históricas.

**Bloques**
- **Entrada y buck (arriba a la izquierda):** J1 pines 1–2 → F101 → D101/D102 (TVS con su GND junto al pin 2 de J1) → Q101 → Q102 → R103 → C105 (esquina) / C104 (junto al pin VOUT de U101) → L101 → C106/C107 → buck U201 (C202/C201 sobre VIN, L201, C204–C206 bajo U201). Pasivos de U101 alrededor de sus pines.
- **CAN aislado (izquierda, bajo la entrada):** U601 sobre la barrera, con el lado aislado (pines 11–20) hacia los pines 3–5 de J1. En la isla solo hay piezas del bus: D601, R602/R603/C609, R605, C607/C608, C610/C606, FB601 y FB602.
  - **FB602 no cruza la barrera:** une GNDISO_CAN con GND_CAN, y las dos redes son del lado aislado. **Solo U601 cruza.**
- **Barrera:** rule area `BARRERA_CAN` en F.Cu y B.Cu, sin pistas, vías, rellenos ni pads.
  - Forma: franja entre los pines 2 y 3 de J1 (y 60.4–62.9), franja vertical bajo el cuerpo de U601 (x 24.6–31.4) y franja inferior (y 87.5–90).
  - En `INCLI-VA.kicad_dru`, el pin 17 de U601 (AUXOUT, sin conexión) pasa a contar como dominio aislado, porque está en ese lado del encapsulado.
- **Salidas (arriba, bajo J2):** se corrigió el cruce. El bloque DO2 queda bajo el pin 2 (izquierda) y el DO1 bajo el pin 1 (derecha). J2 se corrió 6 mm a la derecha y conserva su orientación (cable hacia el borde).
- **MCU:**
  - USB-C J401 al borde derecho, sobre la muesca, con U402 en línea. D+/D- bajan a los pines 13/14 por un pasillo libre a su izquierda, así no cruzan ninguna otra señal.
  - SW401 junto al EN, con la zona libre de antena a su derecha.
  - C402 sobre los pines 1/2 y C401 detrás. C403/R401 junto al EN.
  - Supervisor, LED y VAR_ID en filas sobre el borde superior del módulo.
  - SW402 (BOOT) y J402 (UART) en el borde inferior. C309/C310 bajo los pines ADC.
- **Sensores:** U501 (SCL3300) a ~9 mm de **H5** (68.2, 53) y U502 (ASM330) arriba de H5. Distancia al eje de ROT (U503 en 50, 50, sin mover): 18 mm. U501 queda a más de 35 mm de L201, L301, C105 y de cualquier conector.
- **3,3 V:** U301/L301 abajo al centro, lejos de los sensores; U302 (LDO de +3V3_A) entre los dos.

**Verificación:** DRC 0 errores, 1 aviso conocido (U401), 362 conexiones sin rutear y **paridad 0**, ya con H5 (`layout/reports/drc-reacomodo.json`). ERC 0 errores / 1 aviso conocido (`erc-con-h5.json`). `sch_visual_qa` de la raíz: PASS. Courtyards ≥ 1 mm en cada cara (verificador propio). Ninguna pieza en el keep-out de antena ni en la barrera.

**Longitudes aproximadas** (árbol mínimo entre los pads de cada red, en línea recta; no son longitudes de ruteo):

| Red | Nodos | Antes (mm) | Después (mm) |
|---|---:|---:|---:|
| ILIM | 2 | 41.2 | 4.2 |
| SW | 2 | 41.8 | 5.7 |
| +VPROT | 7 | 117.0 | 26.3 |
| BUCK_SW | 3 | 11.4 | 9.2 |
| MCU_RST_N | 6 | 93.8 | 18.3 |
| BUS_CAN_H | 4 | 34.7 | 24.2 |
| BUS_CAN_L | 4 | 31.2 | 20.4 |
| USB_D+ | 3 | 41.1 | 33.9 |
| USB_D- | 3 | 40.5 | 35.2 |

**Desacoples y pasivos clave:** separación borde a borde entre el pad de la pieza y el pin del IC en la red indicada. Para los de salida del buck se mide el retorno a GND.

| Pieza → pin | Red | Antes (mm) | Después (mm) |
|---|---|---:|---:|
| R106 → U101 (3) | SW | 40.87 | 4.74 |
| R110 → U101 (11) | ILIM | 40.37 | 3.31 |
| R107 → U101 (4) | UVLO | 5.88 | 4.38 |
| R109 → U101 (5) | OV | 29.38 | 4.64 |
| C102 → U101 (22) | VS | 7.23 | 4.64 |
| C103 → U101 (18) | C_ID | 22.77 | 2.35 |
| C108 → U101 (23) | CAP | 12.02 | 1.89 |
| C110 → U101 (9) | TMR | 19.98 | 3.21 |
| C104 → U101 (19) | VOUT | 20.16 | 6.09 |
| R104 → U101 (20) | CSP | 18.7 | 2.51 |
| C107 → L101 (2) | +VPROT | 33.51 | 1.62 |
| C106 → L101 (2) | +VPROT | 14.54 | 2.06 |
| C202 → U201 (2) | +VPROT | 3.11 | 1.62 |
| C201 → U201 (3) | +VPROT | 4.53 | 4.22 |
| C203 → U201 (7) | BUCK_BOOT | 2.43 | 3.13 |
| L201 → U201 (8) | BUCK_SW | 3.81 | 5.25 |
| C204 → U201 (9) | GND_VEH | 13.43 | 4.38 |
| C205 → U201 (9) | GND_VEH | 13.64 | 4.38 |
| C206 → U201 (9) | GND_VEH | 14.64 | 4.54 |
| C302 → U301 (3) | +5V_VEH | 4.47 | 4.44 |
| C301 → U301 (3) | +5V_VEH | 4.4 | 3.1 |
| L301 → U301 (2) | Net-(U301-SW) | 4.39 | 2.93 |
| C307 → U302 (5) | +3V3_A | 2.04 | 2.21 |
| C306 → U302 (1) | Net-(U302-EN) | 3.57 | 3.6 |
| C402 → U401 (2) | +3V3_D | 4.28 | 1.7 |
| C401 → U401 (2) | +3V3_D | 6.47 | 4.28 |
| C403 → U401 (3) | MCU_RST_N | 9.62 | 3.09 |
| C309 → U401 (39) | VMON_5V | 29.08 | 3.17 |
| C310 → U401 (38) | VMON_3V3 | 41.03 | 3.23 |
| C501 → U501 (4) | +3V3_A | 1.75 | 2.15 |
| C504 → U501 (9) | +3V3_A | 2.25 | 0.59 |
| C502 → U501 (2) | SCL_AEXTC | 2.39 | 2.15 |
| C503 → U501 (10) | SCL_DEXTC | 3.45 | 1.09 |
| C505 → U502 (5) | +3V3_A | 4.12 | 2.44 |
| C506 → U502 (8) | +3V3_A | 1.85 | 1.65 |
| C508 → U502 (5) | +3V3_A | 2.76 | 3.46 |
| C507 → U503 (12) | +3V3_A | 1.98 | 3.29 |
| C601 → U601 (4) | +3V3_D | 1.67 | 4.81 |
| C602 → U601 (4) | +3V3_D | 3.65 | 1.6 |
| C605 → U601 (4) | +3V3_D | 7.76 | 5.78 |
| C603 → U601 (3) | +5V_VEH | 2.76 | 5.84 |
| C604 → U601 (3) | +5V_VEH | 4.55 | 1.81 |
| C606 → U601 (19) | V_SOOUT | 3.88 | 3.18 |
| C610 → U601 (19) | V_SOOUT | 4.25 | 1.64 |
| C607 → U601 (16) | V_SOIN | 3.8 | 2.15 |
| C608 → U601 (16) | V_SOIN | 5.94 | 1.62 |
| C702 → U701 (5) | +5V_VEH | 3.57 | 1.69 |
| C752 → U751 (5) | +5V_VEH | 3.57 | 1.7 |
| C801 → U801 (5) | +3V3_D | 4.32 | 4.1 |


**Lo que no se logró (y por qué)**
- **ADM3055E:** los de 100 nF/220 nF/10 nF quedan a ≤ 2.2 mm (C602, C604, C608, C610, C607). C601 (10 nF en VIO) queda a 4.8 mm y los de 10 µF a 3–6 mm. Con 1 mm entre courtyards (soldadura a mano) no entran más de dos o tres capacitores a ≤ 2 mm por lado sin tapar las señales RX/TX/STBY/SILENT.
- **Buck de 5 V:** el lazo de entrada (C202) mejoró, pero L201 (5.3 mm) y C203 (3.1 mm) quedaron un poco más lejos que antes, para dejar el retorno de C204–C206 a ~4.4 mm (antes 13–15 mm).
- **USB:** baja de ~41 a ~34–35 mm. El pinout del módulo (D+/D- en la esquina superior izquierda) y la antena a la derecha no dejan un recorrido más corto sin cruzar SPI/CAN.
- **Pendiente para el ruteo:** plano GND_VEH continuo en B.Cu, sin cortes bajo el buck ni bajo los sensores. En la isla CAN, GND_CAN propio fuera de la franja. Costura de vías.

**Reproducción:** `scripts/layout_bloques/`. `plan.py` tiene la intención de ubicación; `legal.py` la separa a 1 mm; `barrier.py` crea la franja; `lay.py` hace check/metrics/render. Uso:
`/usr/bin/python3 legal.py <pcb_entrada> <pcb_salida> plan.py && /usr/bin/python3 barrier.py <pcb> <pcb>`

## Propuesta vigente: 100 × 100 mm — 2026-10-28

**Adoptada como PCB principal (2026-10-28, pedido del usuario, Claude Code):** `INCLI-VA.kicad_pcb` es ahora esta placa. La copia `layout/INCLI-VA-100x100.*` se borró para no tener dos placas; se recupera del commit `20b862e`. Las rutas a `layout/INCLI-VA-100x100.kicad_pcb` de abajo son históricas, igual que `scripts/layout_100x100.py` y `scripts/review_layout_100x100.py`, que todavía apuntan a esa copia.

**Revisión posterior del usuario:** se mantiene la propuesta cuadrada, se dejan **cuatro fijaciones H1–H4** y los **19 puntos de prueba en Bottom (B.Cu)**. H5 está retirado de esta propuesta y, tras la confirmación del usuario, también del esquemático raíz. El PCB base anterior conserva H5 hasta que se adopte la propuesta vigente como principal.

El usuario autorizó preparar y reubicar los componentes en el formato cuadrado. La propuesta está en **`layout/INCLI-VA-100x100.kicad_pcb`**, con su `.kicad_pro`, reglas `.kicad_dru` y la tabla de librerías relativa del directorio. Abrir esa copia para revisar la ubicación. El PCB principal se conserva sin cambios. La propuesta de 120 × 80 mm se retiró del repositorio el 2026-10-28 (decisión del usuario); se recupera del commit `aa0a41b`.

Vistas por cara: **`layout/ubicacion-100x100.png`** (superior) y **`layout/ubicacion-100x100-bottom.png`** (inferior, mirada desde abajo, espejada), también en SVG. Exportaciones nativas de KiCad: `layout/placa-100x100.svg` y `layout/placa-100x100-bottom.svg`. Son vistas de revisión, no archivos de fabricación. La ilustración anterior combinaba las caras: TP401–TP405 ya estaban en B.Cu; ahora cada imagen solo muestra los pads de su propia cara.

### Distribución

- Contorno nominal **100 × 100 mm**, esquinas de radio 4 mm y muesca de antena de 8 × 35 mm en el borde derecho. La reserva RF se extiende fuera del contorno; también deberá quedar libre en la caja.
- Entrada y protección arriba a la izquierda; J1 en el borde izquierdo. Se conserva el espacio de C105 y de todos los DNP.
- J2 arriba, con DO1 y DO2 en dos bloques de distribución equivalente debajo del conector.
- CAN a la izquierda, debajo de la entrada; dominio aislado hacia J1 y lógica hacia el interior.
- Buck de 5 V abajo a la izquierda; regulación de 3.3 V en la zona inferior central.
- AS5147U (U503) exactamente en **(50,50) mm** locales. SCL3300 U501 en **(63,49)** y ASM330LHH U502 en **(76,42)**; sus ejes conservan la orientación previa.
- Cuatro agujeros M3 NPTH sin cobre: H1/H2/H3 en (5,5)/(95,5)/(5,95); H4 en (87,95), desplazado hacia dentro para respetar la antena. H5 eliminado por decisión del usuario. Posiciones propuestas, pendientes de validar contra la caja; la rigidez/vibración con cuatro apoyos sigue pendiente de ensayo.
- ESP32 en el borde derecho, hacia la mitad inferior; USB-C en el borde inferior. UART0 en la zona inferior central y pulsadores accesibles en la parte superior/derecha.
- Todos los TP son pads de prueba de Ø 1.5 mm en **B.Cu/B.Mask**, sin taladro; los identificadores están en **B.Silkscreen**, espejados para leerse desde abajo (altura 1 mm, trazo 0.15 mm). Catorce TP cambiaron de cara y cinco ya estaban en Bottom. Se mantienen sus posiciones XY y sus redes. La tapa inferior deberá ser accesible durante las mediciones; las vías de conexión se resolverán al rutear.
- Coordenadas locales respecto de la esquina superior izquierda del contorno; en KiCad el origen de esa esquina es (100,50) mm.

### Comprobaciones y límites

- **185 huellas**; igualdad de UUID, valores, librerías, campos, atributos/DNP y pads/redes de las referencias conservadas respecto del PCB principal. La única referencia retirada es H5, todavía presente en el PCB principal anterior, pero ya eliminada del esquemático. Ninguna posición XY de las otras 185 huellas cambió respecto de la propuesta anterior; solo cambian la cara y serigrafía de los TP.
- Separación mínima entre envolventes de courtyards/pads: **1.01 mm** (Q102–TP102). El cuerpo de U401 y su reserva RF se verifican por separado.
- **DRC: 0 errores geométricos, 1 aviso** conocido `lib_footprint_mismatch` en U401 por la serigrafía recortada. **396 conexiones sin rutear**, 0 pistas y 0 zonas de placa. El resultado no es un DRC limpio para fabricación.
- Las siete instancias de pad 25 de U101 conservan `/10_power_input/U101_RTN`; su regla de aislamiento está copiada sin cambios. Se conserva el keep-out de antena de U401.
- Reportes persistentes: `layout/reports/drc-100x100.json` e `integridad-100x100.json` (incluye mapa TP → red y exclusión explícita de H5 al comparar con el PCB base). Revisión visual manual por caras y de la exportación nativa inferior completada. Tras retirar H5 del esquemático se repitió ERC: 0 errores/1 aviso conocido en U101_RTN (`layout/reports/erc-sin-h5.json`). La raíz exportada se revisó visualmente; `sch_visual_qa` no está disponible en esta sesión.
- Reproducción desde la raíz: `/usr/bin/python3 scripts/layout_100x100.py`, seguido de `/usr/bin/python3 scripts/review_layout_100x100.py`. Los scripts escriben únicamente la propuesta y sus vistas/reportes, no el PCB principal. El DRC se ejecuta por separado con `kicad-cli pcb drc`.

**El encaje geométrico de 100 × 100 mm está comprobado.** Sigue siendo una ubicación preliminar: falta afinar los desacoples y lazos de los bucks/ADM3055E, revisar retornos, fijaciones/caja/imán y la huella definitiva de C105. Las referencias de componentes están en F.Fab y las de TP en B.Silkscreen; el resto de la serigrafía final y el ruteo quedan pendientes. No rutear hasta el visto bueno de ubicación.

## Antecedente: evaluación por área — 2026-10-28

El usuario plantea **100 × 100 mm como máximo**. Es una alternativa favorable por área: 10000 mm² nominales, un 4.2 % más que 120 × 80 mm. Aplicando las mismas deducciones del estudio (muesca de 8 × 35 mm y cuatro esquinas de radio 4 mm), quedarían aproximadamente 9706 mm² útiles y una ocupación estimada del 57.0 % para la reserva de 5536 mm².

Esta comparación inicial solo evaluaba área. La propuesta de 100 × 100 mm descrita arriba ya incorpora la redistribución y verificación geométrica; todavía no demuestra ruteabilidad ni comportamiento eléctrico.

## Antecedente: propuesta de 120 × 80 mm (2026-10-27, retirada)

Fue la primera ubicación verificada (186 huellas). Se descartó a favor de 100 × 100 mm y sus archivos (`INCLI-VA-120x80.*`, `posiciones-120x80.json`, `ubicacion-120x80.*`) se borraron el 2026-10-28; están en el commit `aa0a41b`. `scripts/layout_100x100.py` partía de ella.

## Estimación de ocupación

Se sumaron envolventes de courtyards/pads de las huellas, ampliadas 0.5 mm por lado para modelar 1 mm entre vecinos. Para U401 se contaron por separado el cuerpo y el keep-out que cae sobre FR4, sin cargar al PCB el área de keep-out que queda fuera. Se descontó del contorno una muesca de 8 × 35 mm y los cuatro redondeos de radio 4 mm.

| Tamaño nominal | Área útil geométrica estimada | Reserva de huellas, RF y acceso | Ocupación estimada |
|---|---:|---:|---:|
| 100 × 70 mm | 6706 mm² | 5536 mm² | 82.6 % |
| 110 × 80 mm | 8506 mm² | 5536 mm² | 65.1 % |
| 120 × 80 mm | 9306 mm² | 5536 mm² | 59.5 % |

Esto es una estimación conservadora mediante envolventes, no la suma del cobre ni un estudio de ruteabilidad. No incluye todas las reservas de disipación, el arnés ni las herramientas de montaje. El caso 110 × 80 mm es solo una comparación de área: no tiene una ubicación verificada. Para 120 × 80 mm se realizó y comprobó la ubicación de las 186 huellas. El aumento de área nominal respecto de 100 × 70 mm es 37.1 %; no se deduce de ello un precio de fabricación.

Los mayores condicionantes son entrada/protección (aprox. 1432 mm² con acceso), conectores J1/J2 (639 mm²), dos salidas completas incluyendo DNP (689 mm²), MCU con periféricos y reserva RF, y cinco fijaciones (316 mm²). C105 se reserva incluso siendo DNP en PROTO.

## Organización visual

- J1 vertical a la izquierda; F101 y protección junto a sus pines de alimentación. C105 arriba a la izquierda; Q101/Q102 y control de entrada en el mismo bloque.
- CAN abajo a la izquierda, con componentes del lado aislado hacia J1 y lógica hacia el centro. No hay plano que puentee FB602.
- J2 arriba, con DO1/DO2 agrupadas debajo y a su derecha; latch y diagnóstico conservan huella.
- LMR38010 y pasivos en el sector central inferior, separados de los sensores. Regulación de 3.3 V a su derecha.
- AS5147U en (60,40) mm locales, centro geométrico reservado para ROT. H5 en (63,73) mm locales, separado del eje y próximo al sector de U501.
- U501/U502 en el sector inferior derecho, con ejes nominales alineados. Su desacople y la rigidez real de la caja requieren afinado.
- ESP32 en el borde derecho, con la muesca y el keep-out trasladados 20 mm en X respecto del proyecto original. USB en el borde superior; UART, BOOT/RESET accesibles por el sector derecho inferior.
- H2 se desplazó hacia dentro para respetar la reserva de antena; las cinco posiciones de fijación son propuestas, no un patrón mecánico aprobado.

## Comprobaciones de la propuesta

- 186 referencias coinciden exactamente con el PCB principal; redes de todos los pads y atributos DNP conservados.
- Separación mínima de envolventes en el modelo: **1.01 mm**. El cuerpo de U401 y su propia reserva RF se tratan como una sola pieza, sin exigir separación entre ambos.
- DRC con `.kicad_pro` y `.kicad_dru` actuales y librerías locales resueltas: **0 errores geométricos, 1 aviso** `lib_footprint_mismatch` de U401, por la modificación de serigrafía conocida.
- **396 conexiones sin rutear**, 0 pistas y 0 zonas de placa. U101 pad 25 conserva `/10_power_input/U101_RTN`.
- Las referencias de la copia se pusieron en F.Fab para revisión; la serigrafía final se hará tras aceptar la ubicación. No se presenta como placa lista para fabricar.
- La imagen se generó con posiciones, dimensiones de pads y envolventes de la propuesta; colores por bloque, líneas discontinuas para DNP. Es una vista de ubicación, no un Gerber.

## Pendiente antes de rutear

1. Confirmar tamaño admisible de la caja y revisar esta distribución por bloques.
2. Afinar posiciones/orientaciones de desacoples contra los pines, especialmente ADM3055E y los dos bucks. El DRC no certifica longitud del lazo de alimentación ni el requisito ADI de recorrido total ≤2 mm.
3. Revisar el retorno de corrientes, espacio térmico, accesibilidad de conectores y altura/adhesivo de C105; verificar su land pattern definitivo.
4. Confirmar eje/altura/cara del imán ROT, fijaciones y distancias al chasis y arnés en la antena.
5. Preparar serigrafía, repetir DRC y obtener el visto bueno final de ubicación. **No rutear hasta ese visto bueno.**

Los reportes de comprobación se generaron en `/tmp/incli-size-check`; los datos de ocupación y posiciones quedan en `docs/layout/` para inspección. No se alteró el esquemático.
