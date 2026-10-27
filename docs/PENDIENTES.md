# INCLI-VA — estado y pendientes

Leer al empezar cada turno y actualizar al terminarlo (ver "Trabajo entre agentes" en `AGENTS.md`).

Última actualización: 2026-10-27, Claude Code (fase 4: 40_mcu_esp32s3).

## Fases terminadas (esquemático)
Las cinco hojas tienen 0 violaciones de ERC.

| Hoja | Contenido | Commit |
|---|---|---|
| `10_power_input` | Protección de entrada LM74930-Q1, Q101, filtro LC y conectores J1 y J2 | `e0f28df`, `aa0e1f2` |
| `20_isolation` | PS201 EC4AW8-48S05, LDO U201 (+5V_VEH), aislador U202 ISO7763FQDWRQ1 | `ed48ece` |
| `30_regulation` | Buck U301 TPS62A02-Q1 (+3V3_D), LDO U302 LP5907-Q1 (+3V3_A), VMON | `37b5b09`, `ed48ece` |
| `40_mcu_esp32s3` | U401 ESP32-S3-WROOM-1-N8R2, EN (RC + WDO), BOOT/RESET, USB-C nativo con ESD, UART0, opción de banco DNP | fase 4 |
| `70_output` (DO1 y DO2) | Salida low-side con latch y PWR_FLT_N | `d256e24` |

## Falta
- [ ] **`50_sensors`:** pendiente.
  - Pull-ups de 10 k a **+3V3_A** en CS_INC, CS_IMU y CS_ROT (aprobado en la fase 4): mantienen los sensores deseleccionados mientras arranca el MCU.
  - IMU_INT1/INT2 llegan a IO40/IO41 (sin glitch): dejar las salidas del ASM330LHH en push-pull.
- [ ] **`60_can`:** ADM3055E pendiente; hoy tiene 25 violaciones de ERC, sobre todo pines sin conectar.
  - CAN_TX ← IO47, CAN_RX → IO48, CAN_STBY ← IO21, CAN_SILENT ← IO42. Test points TP404/TP405 en la hoja 40.
- [ ] **`80_supervision`:** pendiente.
  - **Requisito:** pull-down en **WD_EN** (IO18), para que el watchdog no corra durante el boot ni el flasheo.
  - WDO del TPS3431 → MCU_RST_N: drenador abierto, sin pull-up propio. R401 (10 k, hoja 40) es el pull-up y C403 (1 µF) el retardo de EN.
  - VAR_ID0/1 → IO4/IO5; LED_G/LED_R ← IO6/IO7.
- [ ] **Integración:** cuando estén todas las hojas:
  - Las 71 violaciones de la raíz son label_dangling e isolated_pin_label de señales de 50, 60 y 80, que todavía no usan sus pines.
  - ERC del proyecto completo en 0.
  - Revisión del netlist entre hojas.
- [ ] **PCB:** no empezar hasta que el usuario lo pida. Al empezar, crear la regla `.kicad_dru` para la red del pad 25 de U101 (ver `AGENTS.md`).

Estado del ERC al 2026-10-27 (fase 4): 100 violaciones en total.

| Hoja | Violaciones |
|---|---|
| Raíz | 71 |
| 50_sensors | 2 |
| 60_can | 25 |
| 80_supervision | 2 |
| 10, 20, 30, 40, 70 | 0 |

## Pendientes de BOM
- [ ] **F101** (10_power_input):
  - MPN pendiente; candidato: Bourns SF-2410FPA-W, 2 A, ≥ 250 VDC.
  - Falta la huella 2410: no está en las librerías oficiales. Es un pasivo de 2 terminales, así que se puede crear en `lib/INCLI-VA.pretty` desde el datasheet de Bourns.
- [ ] **J2, header** (10_power_input): falta el MPN del header MSTB 2,5/2-GF-5,08. El enchufe ya está identificado: MSTB 2,5/2-STF-5,08 (1777989).
- [ ] **C105** (10_power_input): hold-up de 1000 µF / 50 V, no montado en el demo. MPN pendiente.
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

## Notas para el próximo turno
- Pines del ESP32-S3: la tabla aprobada y sus criterios están en un texto de la hoja 40. No mover señales críticas a GPIO1–14/17/18 (glitch de encendido) ni a strapping.
- Opción de banco (D401 + JP401, DNP): con JP401 cerrado, +5V_ISO queda en ~4.6 V y el CAN no está garantizado. Abrir JP401 antes de instalar en el vehículo.
- Firmware: los requisitos están en `README.md` ("Requisitos para el firmware").
- KiCad: antes de editar archivos `.kicad_sch` a mano o con scripts, confirmar que KiCad está cerrado. Si estaba abierto, recargar las hojas antes de guardar.
