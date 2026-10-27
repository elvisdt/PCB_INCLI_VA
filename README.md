# INCLI-VA — Inclinómetro de chasis CAN/BLE

Proyecto KiCad 10 jerárquico. Hoja raíz: `INCLI-VA.kicad_sch` (00_top).

## Estructura
| Ruta | Contenido |
|---|---|
| `sheets/10_power_input` | Conectores MSTB (J1, J2), fusible, LM74930-Q1 (corte OV 38.4 V, breaker), TVS, filtro LC → +VPROT |
| `sheets/20_isolation` | DC-DC aislado PS1 ≥ 5 W, 9–72 V (barrera 1), LDO +5V_VEH, aislador ISO77xx |
| `sheets/30_regulation` | Desde +5V_ISO: buck +3V3_D, LDO +3V3_A, divisores VMON |
| `sheets/40_mcu_esp32s3` | MCU ESP32-S3-WROOM-1 (único MCU del diseño) |
| `sheets/40_mcu_kw45` | Solo referencia: no está en la jerarquía |
| `sheets/50_sensors` | SCL3300, ASM330LHH, AS5147U |
| `sheets/60_can` | ADM3055E (barrera 2) desde el TWAI del ESP32-S3 (CAN clásico, J1939), terminación, ESD — reutiliza TP DCI |
| `sheets/70_output_ch` | 1 canal low-side (drenador abierto, relé externo), instanciado 2 veces (DO1, DO2) |
| `sheets/80_supervision` | TPS3431, ID de variante, LED |
| `lib/` | Librería propia: símbolos (`INCLI-VA.kicad_sym`), huellas (`.pretty`), 3D |
| `docs/` | Propuestas ESP32-S3 (vigente) y KW45 (descartada), datasheets |
| `fab/` | Gerbers, BOM por variante, pick & place |

## Convenciones
- Rieles/masas: símbolos de potencia de la lib `INCLI-VA`: `+VPROT +5V_VEH +5V_ISO +3V3_D +3V3_A GND_VEH GND_ISO GND_CAN`. Nunca `GND` genérico.
- Señales entre hojas: pines jerárquicos; en el top se unen por etiquetas del mismo nombre.
- Prefijos de red por dominio: `VEH_`, `ISO_`, `BUS_`.
- Campos por componente: `MPN`, `Manufacturer`, `Alt_MPN`, `Variant` (CAN, OUT, ROT, CABIN).

## MCU
El diseño usa solo el **ESP32-S3-WROOM-1** (`sheets/40_mcu_esp32s3`). La KW45 queda descartada; su hoja se conserva como referencia, fuera de la jerarquía.
CAN: TWAI nativo (CAN clásico, J1939) directo al ADM3055E; no hay controlador CAN FD.

## Requisitos para el firmware
- Salidas DO1/DO2 (`70_output_ch`): tras un disparo del latch de sobrecorriente (DIAG alto con EN=1), bajar EN para rearmarlo y **no reintentar antes de 100 ms**.
- Arranque del motor en vehículos de 12 V: la tensión puede caer bajo los 9 V mínimos de PS1 y la placa reiniciarse. El firmware debe arrancar limpio tras un brownout (sin estado corrupto, salidas abiertas hasta reinicializar).
- Radio: stack BLE **NimBLE**; WiFi desactivado en operación normal (solo para OTA en taller). El hardware se dimensiona igual con WiFi activo.
