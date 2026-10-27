# INCLI-VA — estado y pendientes

Leer al empezar cada turno y actualizar al terminarlo (ver "Trabajo entre agentes" en `AGENTS.md`).

Última actualización: 2026-10-27, Claude Code (después del commit `ed48ece`).

## Fases terminadas (esquemático)
Las cuatro hojas tienen 0 violaciones de ERC.

| Hoja | Contenido | Commit |
|---|---|---|
| `10_power_input` | Protección de entrada LM74930-Q1, Q101, filtro LC y conectores J1 y J2 | `e0f28df`, `aa0e1f2` |
| `20_isolation` | PS201 EC4AW8-48S05, LDO U201 (+5V_VEH), aislador U202 ISO7763FQDWRQ1 | `ed48ece` |
| `30_regulation` | Buck U301 TPS62A02-Q1 (+3V3_D), LDO U302 LP5907-Q1 (+3V3_A), VMON | `37b5b09`, `ed48ece` |
| `70_output` (DO1 y DO2) | Salida low-side con latch y PWR_FLT_N | `d256e24` |

## Falta
- [ ] **`40_mcu_esp32s3`:** todavía es plantilla.
  - Conectar los pines jerárquicos que ya llegan desde la raíz:
    - Desde 20: DO1_EN, DO2_EN, DO1_DIAG, DO2_DIAG y PWR_FLT_N.
    - Desde 30: VMON_5V y VMON_3V3, que van al ADC1.
    - SPI, CAN y supervisión.
  - Reemplazar los símbolos de alimentación provisorios.
  - Dimensionar con WiFi activo.
- [ ] **`50_sensors`:** pendiente.
- [ ] **`60_can`:** ADM3055E pendiente; hoy tiene 25 violaciones de ERC, sobre todo pines sin conectar.
- [ ] **`80_supervision`:** pendiente.
- [ ] **Integración:** cuando estén todas las hojas:
  - Las 97 violaciones de la raíz son label_dangling e isolated_pin_label, de hojas que todavía no usan sus pines.
  - ERC del proyecto completo en 0.
  - Revisión del netlist entre hojas.
- [ ] **PCB:** no empezar hasta que el usuario lo pida. Al empezar, crear la regla `.kicad_dru` para la red del pad 25 de U101 (ver `AGENTS.md`).

Estado del ERC al 2026-10-27: 129 violaciones en total.

| Hoja | Violaciones |
|---|---|
| Raíz | 97 |
| 40_mcu | 3 |
| 50_sensors | 2 |
| 60_can | 25 |
| 80_supervision | 2 |
| 10, 20, 30, 70 | 0 |

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

## Notas para el próximo turno
- Firmware: los requisitos están en `README.md` ("Requisitos para el firmware").
- KiCad: antes de editar archivos `.kicad_sch` a mano o con scripts, confirmar que KiCad está cerrado. Si estaba abierto, recargar las hojas antes de guardar.
