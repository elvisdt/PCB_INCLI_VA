# INCLI-VA — estado y pendientes

Leer al empezar cada turno y actualizar al terminarlo (ver "Trabajo entre agentes" en `AGENTS.md`).

Última actualización: 2026-10-27, Claude Code (criterio de producción, decisiones del usuario, 60_can, 70_output, 10_power_input, campo DNP).

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
   - El usuario pidió dejar huella DNP para un TVS de entrada más grande, por si hay vehículos sin supresión. **No se agregó; queda a confirmar.** La entrada ya bloquea 202 V sin TVS: Q101 es de 250 V, D101 de 400 V y C101 de 450 V. Un TVS que recorte un load dump sin suprimir necesita encapsulado DO-218 (SM8S) y unos 150 mm² de placa. Detalle en "Máximos de la entrada".
2. **R109 = 1.82 k (corte por OV a 34.2 V): aprobado, pero no aplicado. Pendiente de confirmar** (ver "Abierto").
3. **Opción B, no aislada: aprobada.** Se quitan PS201, U202 (ISO7763) y U201 (TPS7A1650), y entra un buck de 60–100 V de +VPROT a 5 V. El aislamiento queda solo en el CAN (ADM3055E).
   - El LMR16010 se descarta (sin stock, 12 semanas).
   - Candidatos en "Abierto"; falta confirmar el stock antes de rehacer la hoja 20.
4. **60_can: aprobado y aplicado** (ver "Hecho en este turno").
5. **DO mínima: aprobada y aplicada.** El latch y el diagnóstico quedan como huellas DNP.
6. **J1 y J2:** Phoenix MSTB 2,5 de 5.08 mm con brida roscada (GF). **Aplicado.**
7. **C105:** se queda como huella DNP (función en "Hecho en este turno").

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

## Abierto (necesito respuesta)
- **A1. Buck de la opción B (hoja 20).** No pude leer el stock en vivo: las páginas de LCSC y DigiKey lo cargan con JavaScript. Las cifras de abajo son capturas de buscadores. Hay que confirmarlas en las páginas:
  - **TI LM5164** (100 V, 1 A, HSOIC-8 PowerPAD, COT):
    - LCSC C477928 (LM5164DDAR): el listado existe; una captura muestra 12 318 unidades.
    - DigiKey LM5164DDAR: sin stock, con backorder. La versión Q1 (LM5164QDDARQ1) muestra datos contradictorios.
  - **TI LMR38010** (80 V, 1 A, HSOIC-8 PowerPAD, compensación interna, spread spectrum, PG):
    - DigiKey LMR38010SQDDARQ1 (Q1): captura con 4 307 unidades, US$ 4.73 la unidad.
    - Mouser LMR38010FDDAR: ~2 300 unidades.
    - LCSC: no encontré el listado.
  - Los dos usan la misma huella (8-HSOIC PowerPAD, DDA), pero **no tienen el mismo pinout**: no se pueden intercambiar sin tocar el esquemático.
  - Recomendación: LMR38010-Q1 como principal (automotriz, menos pasivos, spread spectrum para CISPR 25) y LM5164 como alternativa de LCSC.
- **A2. R109.** El corte a 34.2 V se pidió por el máximo de 36 V del URB2405 (opción A). Con la opción B, el buck aguanta 80–100 V, así que conviene **dejar R109 = 1.62 k (38.4 V)**:
  - La placa sigue funcionando en la prueba de sobretensión de 36 V (24 V) y en el load dump suprimido de 12 V (35 V).
  - Solo corta en el load dump de 24 V (58 V).
  - C106 (50 V) mantiene margen.
- **A3. TVS de entrada grande DNP:** ¿se agrega igual (DO-218, ~150 mm²), sabiendo que la entrada ya bloquea 202 V? Ver la decisión 1.

## Falta
- [ ] **Hoja 20 → opción B** (cuando se resuelvan A1 y A2):
  - Quitar PS201, U202, U201 y sus pasivos.
  - Buck de +VPROT a 5 V.
  - Unificar masas y rieles en toda la jerarquía: GND_ISO → GND_VEH y +5V_ISO → +5V_VEH (el +5V_VEH del LDO desaparece).
  - DO1_EN y DO2_EN del MCU directo a las hojas 70 (entrada EN de 3.3 V). DIAG directo al MCU.
  - VEH_PWR_FLT_N directo al MCU. R111 (pull-up de FLT, hoja 10) pasa de +5V_VEH a +3V3_D.
  - Quitar R201–R204: ya los reemplazan R711 y R703 en la hoja 70.
  - Actualizar el texto de las hojas 10, 30 y 40 que mencionan el aislamiento y la barrera 1.
- [ ] **`80_supervision`:** pendiente.
  - **Requisito:** pull-down en **WD_EN** (IO18), para que el watchdog no corra durante el boot ni el flasheo.
  - WDO del TPS3431 → MCU_RST_N: drenador abierto, sin pull-up propio. R401 (10 k, hoja 40) es el pull-up y C403 (1 µF) el retardo de EN.
  - VAR_ID0/1 → IO4/IO5; LED_G/LED_R ← IO6/IO7.
- [ ] **Huellas importadas sin revisar** (regla de `AGENTS.md`): FUSE-SMD_L6.1-W2.5-1 (F101), PWRM-TH_URBXXXXYMD_10WR3 (PS201; sale con la opción B) y HVSSOP-8 (TPS7A1650; sale con la opción B).
  - Las tres están en `lib/INCLI-VA.pretty` sin descripción de fuente.
  - F101: comparar con el land pattern de Bourns y documentar la fuente.
- [ ] **Limpieza del repositorio:** `fp-lib-table.bak` y `lib/Connector_Phoenix_MSTB.pretty.bak/`.
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

Estado del ERC al 2026-10-27 (después de este turno):

| Hoja | Violaciones |
|---|---|
| Raíz | 7 errores (label_dangling de 80) + 18 avisos |
| 20_isolation | 4 avisos (pines "unspecified" de PS201; desaparecen con la opción B) |
| 60_can | 1 error: +5V_ISO sin fuente declarada (PS201 tiene pines "unspecified"); se resuelve con el buck |
| 80_supervision | 2 errores (hoja vacía) |
| 10, 30, 40, 50, 70 | 0 |

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

## Pendientes de BOM
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
