# INCLI-VA — Inclinómetro de chasis CAN/BLE

Proyecto KiCad 10 jerárquico. Hoja raíz: `INCLI-VA.kicad_sch` (00_top).

## Estructura
| Ruta | Contenido |
|---|---|
| `sheets/10_power_input` | Conectores Phoenix MSTB 2,5 de 5.08 mm GF (J1, J2), fusible F101 SF-2410FPA200W-2, LM74930-Q1 (diodo ideal, corte por OV, breaker de 1 A), TVS, filtro LC → +VPROT. C105 (hold-up) es huella DNP |
| `sheets/20_buck_5v` | Buck no aislado U201 LMR38010SQDDARQ1 (PROTO: LMR38010SDDAR): +VPROT → +5V_VEH, 5.02 V / 1 A a 400 kHz. Sin pines jerárquicos |
| `sheets/30_regulation` | Desde el riel de 5 V: buck TPS62A02-Q1 → +3V3_D, LDO LP5907-Q1 → +3V3_A, divisores VMON |
| `sheets/40_mcu_esp32s3` | MCU ESP32-S3-WROOM-1-N8R2 (único MCU), USB-C nativo con ESD, UART0, BOOT/RESET |
| `sheets/40_mcu_kw45` | Solo referencia: no está en la jerarquía |
| `sheets/50_sensors` | SCL3300-D01 (inclinómetro), ASM330LHH (IMU), AS5147U (ángulo de pluma, solo variante ROT) en SPI compartido |
| `sheets/60_can` | ADM3055E (CAN aislado con isoPower, único aislamiento de la placa) desde el TWAI del ESP32-S3 (CAN clásico, J1939). Terminación partida 2 × 60.4 Ω + 4.7 nF. ESD externo ESD2CAN24-Q1 como DNP |
| `sheets/70_output_ch` | 1 canal low-side (drenador abierto, relé externo), instanciado 2 veces (DO1, DO2): buffer 74AHCT1G126 (3.3 → 5 V), DMN10H220LQ 100 V, zener de gate y SMAJ58A. Latch de sobrecorriente y diagnóstico como huellas DNP |
| `sheets/80_supervision` | TPS3431, ID de variante, LED |
| `lib/` | Librería propia: símbolos (`INCLI-VA.kicad_sym`), huellas (`.pretty`), 3D |
| `docs/` | Propuestas ESP32-S3 (vigente) y KW45 (descartada), datasheets |
| `fab/` | Gerbers, BOM por variante, pick & place |

## Convenciones
- Rieles/masas: símbolos de potencia de la lib `INCLI-VA`: `+VPROT +5V_VEH +3V3_D +3V3_A GND_VEH GND_CAN`. Nunca `GND` genérico.
  - Opción B (no aislada): toda la placa usa GND_VEH. GND_CAN (lado bus del ADM3055E) es el único dominio aislado.
  - `GND_ISO` y `+5V_ISO` siguen en la librería, pero ya no se usan.
- Señales entre hojas: pines jerárquicos; en el top se unen por etiquetas del mismo nombre.
- Prefijos de red por dominio: `VEH_`, `ISO_`, `BUS_`.
- Campos por componente: `MPN`, `Manufacturer`, `Datasheet`, `Alt_MPN`, `Variant` (CAN, OUT, ROT, CABIN), `Notes` y `DNP`.
- `MPN_PROTO`: solo cuando el prototipo usa un equivalente distinto del MPN de producción (por ejemplo, la versión comercial de una pieza -Q1). El BOM de prototipo usa `MPN_PROTO` si existe y, si no, `MPN`.
- **Prototipo = producción:** es el mismo esquemático; solo cambia qué se monta. El campo `DNP` define los dos BOM:
  - vacío: se monta siempre.
  - `PROTO`: no se monta en el prototipo.
  - `PROD`: no se monta en producción.
  - `PROTO,PROD`: huella reservada.
  - El atributo `dnp` de KiCad refleja el BOM de prototipo.

## Entorno
- Vehículos de 12 V y 24 V nominales. Transitorios: ISO 7637-2 e ISO 16750-2, con load dump **suprimido** (24 V: ≤ 58 V). La entrada también bloquea un load dump sin suprimir (202 V); las salidas DO no.

## MCU
El diseño usa solo el **ESP32-S3-WROOM-1** (`sheets/40_mcu_esp32s3`). La KW45 queda descartada; su hoja se conserva como referencia, fuera de la jerarquía.
CAN: TWAI nativo (CAN clásico, J1939) directo al ADM3055E; no hay controlador CAN FD.

## Requisitos para el firmware
- Salidas DO1/DO2 (`70_output_ch`): el latch de sobrecorriente y el diagnóstico son huellas DNP. Si se montan: tras un disparo del latch (DIAG alto con EN=1), bajar EN para rearmarlo y **no reintentar antes de 100 ms**.
- Arranque del motor en vehículos de 12 V y load dump de 24 V (corte por OV del LM74930, ≤ 350 ms): sin C105 (DNP) la placa se reinicia. El firmware debe arrancar limpio tras un brownout (sin estado corrupto, salidas abiertas hasta reinicializar).
- Radio: stack BLE **NimBLE**; WiFi desactivado en operación normal (solo para OTA en taller). El hardware se dimensiona igual con WiFi activo.
