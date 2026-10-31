# INCLI-VA — Inclinómetro de chasis CAN/BLE

Proyecto KiCad 10 jerárquico. Hoja raíz: `INCLI-VA.kicad_sch` (00_top).

## Estructura
| Ruta | Contenido |
|---|---|
| `sheets/10_power_input` | Conectores Phoenix MSTB 2,5 de 5.08 mm GF (J1, J2), fusible F101 SF-2410FPA200W-2, LM74930-Q1 (diodo ideal, corte por OV, breaker de 1 A), TVS, filtro LC → +VPROT. C105 (hold-up): `DNP = PROTO`, se monta en PROD. Desde rc6: UVLO desde VBAT_F (R113 + R106) y D104 = BAV23C (D1 de VA a VS, TI fig. 8-1) |
| `sheets/20_buck_5v` | Buck no aislado U201 LMR38010SQDDARQ1 (PROTO: LMR38010SDDAR): +VPROT → +5V_VEH, 5.02 V / 1 A a 400 kHz. Sin pines jerárquicos |
| `sheets/30_regulation` | Desde el riel de 5 V: buck TPS62A02-Q1 → +3V3_D, LDO LP5907-Q1 → +3V3_A, divisores VMON |
| `sheets/40_mcu_esp32s3` | MCU ESP32-S3-WROOM-1-N8R2 (único MCU), USB-C nativo con ESD, UART0, BOOT/RESET |
| `sheets/40_mcu_kw45` | Solo referencia: no está en la jerarquía |
| `sheets/50_sensors` | SCL3300-D01 (inclinómetro), ASM330LHH (IMU), AS5147U (ángulo de pluma, solo variante ROT) en SPI compartido |
| `sheets/60_can` | ADM3055E (CAN aislado con isoPower, único aislamiento de la placa) desde el TWAI del ESP32-S3 (CAN clásico, J1939). Terminación partida 2 × 60.4 Ω + 4.7 nF. ESD externo ESD2CAN24-Q1 como DNP |
| `sheets/70_output_ch` | 1 canal low-side (drenador abierto, relé externo), instanciado 2 veces (DO1, DO2): buffer 74AHCT1G126 (3.3 → 5 V), DMN10H220LQ 100 V, zener de gate y SMAJ58A. Sin latch de sobrecorriente (retirado); diagnóstico como huella DNP en PROTO |
| `sheets/80_supervision` | U801 TPS3828-33-Q1 (supervisor de +3V3_D + watchdog, WDI ← IO17), LED verde/rojo (DNP en PROD), VAR_ID0/1/2 por 0 Ω a GND |
| `lib/` | Librería propia: símbolos (`INCLI-VA.kicad_sym`), huellas (`.pretty`), 3D |
| `docs/` | Propuestas ESP32-S3 (vigente) y KW45 (descartada), datasheets |
| `fab/` | Gerbers, BOM por variante, pick & place |

## Convenciones
- Rieles/masas: símbolos de potencia de la lib `INCLI-VA`: `+VPROT +5V_VEH +3V3_D +3V3_A GND_VEH GND_CAN`. Nunca `GND` genérico.
  - Opción B (no aislada): toda la placa usa GND_VEH. GND_CAN (lado bus del ADM3055E) es el único dominio aislado.
  - `GND_ISO` y `+5V_ISO` siguen en la librería, pero ya no se usan.
- Señales entre hojas: pines jerárquicos; en el top se unen por etiquetas del mismo nombre.
- Prefijos de red por dominio: `VEH_`, `ISO_`, `BUS_`.
- Campos por componente: `MPN`, `Manufacturer`, `LCSC`, `Datasheet`, `Alt_MPN`, `Variant` (CAN, OUT, ROT, CABIN), `Notes` y `DNP`. `LCSC` es el código LCSC/JLC del `MPN` (vacío si LCSC no lo lista).
- `MPN_PROTO`, `Manufacturer_PROTO` y `LCSC_PROTO`: solo cuando el prototipo usa un equivalente distinto del MPN de producción (por ejemplo, la versión comercial de una pieza -Q1, un pasivo JLC Basic o un sustituto aceptado; ver `docs/BOM_SOURCING.md`). `Manufacturer_PROTO` solo si cambia el fabricante. El BOM de prototipo usa el campo `_PROTO` si existe y, si no, el de producción.
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
- Salidas DO1/DO2 (`70_output_ch`): no hay latch de sobrecorriente (retirado el 2026-10-28); un corto de la carga a +V no queda limitado por hardware. El diagnóstico (DIAG) es DNP en PROTO y se monta en PROD.
- Arranque del motor en vehículos de 12 V y load dump de 24 V (corte por OV del LM74930, ≤ 350 ms): sin C105 (DNP en PROTO) la placa se reinicia (vale desde rc6; en rc5 la placa no arrancaba por el UVLO, hallazgo R-01). El firmware debe arrancar limpio tras un brownout (sin estado corrupto, salidas abiertas hasta reinicializar).
- Watchdog externo (U801): patear WDI (IO17) cada ≤ 0.5 s (timeout mínimo 0.9 s). Una vez inicializado, no dejar IO17 en alta impedancia (eso deshabilita el watchdog), salvo antes de dormir más de 0.9 s.
- VAR_ID (IO4 = ID0, IO5 = ID1, IO8 = ID2): activar los pull-ups internos y leer al arrancar. ID1 ID0: 11 base | 10 CAN | 01 solo DO | 00 CAN + DO. ID2 reservado para CABIN. ROT se detecta por SPI (AS5147U responde).
- AS5147U (modo 3.3 V): poner a 1 el bit **NOISESET** (DS000639 v1-04, fig. 8) y usar CRC/paridad en todas las tramas.
- SCL3300: protocolo fuera de trama (la respuesta llega en la trama siguiente), **TLH ≥ 10 µs** con CSB alto entre tramas (Doc. 4921, tiempos SPI), CRC en cada respuesta y secuencia de arranque (SW reset, modo, espera, STATUS limpio). Modos 1 o 2 para el rango completo.
- No reemplazar U401 por variantes de flash de 1.8 V ni de PSRAM octal (IO35–IO37 e IO47/IO48).
- Radio: stack BLE **NimBLE**; WiFi desactivado en operación normal (solo para OTA en taller). El hardware se dimensiona igual con WiFi activo.
