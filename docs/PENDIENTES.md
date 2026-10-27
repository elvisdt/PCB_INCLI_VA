# INCLI-VA — estado y pendientes

Leer al empezar cada turno y actualizar al terminarlo (ver "Trabajo entre agentes" en `AGENTS.md`).

Última actualización: 2026-10-27, Claude Code (fase 5: 50_sensors; preguntas para el usuario).

## Fases terminadas (esquemático)
Las seis hojas tienen 0 violaciones de ERC.

| Hoja | Contenido | Commit |
|---|---|---|
| `10_power_input` | Protección de entrada LM74930-Q1, Q101, filtro LC y conectores J1 y J2 | `e0f28df`, `aa0e1f2` |
| `20_isolation` | PS201 EC4AW8-48S05, LDO U201 (+5V_VEH), aislador U202 ISO7763FQDWRQ1 | `ed48ece` |
| `30_regulation` | Buck U301 TPS62A02-Q1 (+3V3_D), LDO U302 LP5907-Q1 (+3V3_A), VMON | `37b5b09`, `ed48ece` |
| `40_mcu_esp32s3` | U401 ESP32-S3-WROOM-1-N8R2, EN (RC + WDO), BOOT/RESET, USB-C nativo con ESD, UART0, opción de banco DNP | fase 4 |
| `50_sensors` | U501 SCL3300-D01, U502 ASM330LHHTR, U503 AS5147U-HTSM (solo ROT), pull-ups de CS, TP de SPI | fase 5 |
| `70_output` (DO1 y DO2) | Salida low-side con latch y PWR_FLT_N | `d256e24` |

## Falta
- [ ] **`60_can`:** ADM3055E pendiente; hoy tiene 25 violaciones de ERC, sobre todo pines sin conectar.
  - CAN_TX ← IO47, CAN_RX → IO48, CAN_STBY ← IO21, CAN_SILENT ← IO42. Test points TP404/TP405 en la hoja 40.
- [ ] **`80_supervision`:** pendiente.
  - **Requisito:** pull-down en **WD_EN** (IO18), para que el watchdog no corra durante el boot ni el flasheo.
  - WDO del TPS3431 → MCU_RST_N: drenador abierto, sin pull-up propio. R401 (10 k, hoja 40) es el pull-up y C403 (1 µF) el retardo de EN.
  - VAR_ID0/1 → IO4/IO5; LED_G/LED_R ← IO6/IO7.
- [ ] **Integración:** cuando estén todas las hojas:
  - Las 39 violaciones de la raíz son label_dangling e isolated_pin_label de señales de 60 y 80, que todavía no usan sus pines.
  - ERC del proyecto completo en 0.
  - Revisión del netlist entre hojas.
- [ ] **PCB:** no empezar hasta que el usuario lo pida. Al empezar, crear la regla `.kicad_dru` para la red del pad 25 de U101 (ver `AGENTS.md`).

Estado del ERC al 2026-10-27 (fase 5): 66 violaciones en total.

| Hoja | Violaciones |
|---|---|
| Raíz | 39 |
| 60_can | 25 |
| 80_supervision | 2 |
| 10, 20, 30, 40, 50, 70 | 0 |

## Decisiones del usuario
Preguntas que necesito que respondas para terminar 60_can y 80_supervision y empezar el PCB. Donde tengo una recomendación, va marcada con **(rec.)**; si estás de acuerdo, basta con "ok".

### 60_can (ADM3055E, barrera 2)
1. **Variantes:** ¿el CAN se monta en todas las variantes, o es DNP en la variante base (`Variant=CAN`)? ¿Qué variantes existen en total (base, CAN, OUT, ROT, CABIN) y cuáles se combinan?
2. **Terminación de 120 Ω:** ¿solder jumper **(rec.)**, header con jumper o terminación partida (2 × 60 Ω + 4.7 nF a GND_CAN)? ¿Por defecto conectada o abierta?
3. **ESD en CAN_H/CAN_L:** ¿aceptas un TVS doble para CAN apto para sistemas de 24 V (p. ej., ESD2CAN24-Q1 o PESD2CAN24, SOT-23) **(rec.)**?
4. **Choke de modo común** (p. ej., ACT45B-510): ¿se monta, se deja como DNP con puentes de 0 Ω **(rec.)**, o se omite?
5. **CAN_STBY al arrancar:** ¿standby (pull-up, el bus queda en silencio hasta que el firmware lo habilite) **(rec.)** o modo normal (pull-down)?
6. **CAN_GND (J1, pin 5):** ¿va directo a GND_CAN (masa aislada del bus) **(rec.)**, a través de una resistencia o queda sin conexión?
7. **Velocidad del bus:** ¿250 kbit/s (J1939 estándar) o 500 kbit/s? Afecta la elección del ESD y del choke (capacitancia).
8. **"Reutilizar el TP de DCI":** ¿tienes los archivos de ese diseño (esquemático o layout del EVAL-ADM3055E) para copiar la disposición de la barrera 2? ¿Dónde los dejo, o los dejas tú en `docs/`?

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

### BOM
23. **F101:** ¿confirmas el Bourns SF-2410FPA-W (2 A, ≥ 250 VDC)? Si sí, creo la huella 2410 en `lib/INCLI-VA.pretty` a partir del datasheet de Bourns (pásame el PDF).
24. **Header de J2:** ¿confirmas el Phoenix MSTB 2,5/2-GF-5,08? Necesito el número de pedido del header, por ejemplo de tu proveedor.
25. **C105 (hold-up, DNP):** ¿definimos ahora el MPN (radial de 1000 µF / 50 V, alto ≤ X mm) o lo dejamos sin MPN mientras no se monte?

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
- [ ] **F101** (10_power_input):
  - MPN pendiente; candidato: Bourns SF-2410FPA-W, 2 A, ≥ 250 VDC.
  - Falta la huella 2410: no está en las librerías oficiales. Es un pasivo de 2 terminales, así que se puede crear en `lib/INCLI-VA.pretty` desde el datasheet de Bourns.
- [ ] **J2, header** (10_power_input): falta el MPN del header MSTB 2,5/2-GF-5,08. El enchufe ya está identificado: MSTB 2,5/2-STF-5,08 (1777989).
- [ ] **C105** (10_power_input): hold-up de 1000 µF / 50 V, no montado en el demo. MPN pendiente.
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
  - 20_isolation:
    - C201 y C204 GCM32ER72A225KA64L
    - C202 y C205 GCM188R72A104KA64D
    - C203 y C206 GCM21BR71A106KE22L
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
- Opción de banco (D401 + JP401, DNP): con JP401 cerrado, +5V_ISO queda en ~4.6 V y el CAN no está garantizado. Abrir JP401 antes de instalar en el vehículo.
- Firmware: los requisitos están en `README.md` ("Requisitos para el firmware").
- KiCad: antes de editar archivos `.kicad_sch` a mano o con scripts, confirmar que KiCad está cerrado. Si estaba abierto, recargar las hojas antes de guardar.
