# Estudio de tamaño y ubicación — Codex, actualizado 2026-10-28

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
