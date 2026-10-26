# INCLI-VA — Inclinómetro de chasis CAN/BLE

Proyecto KiCad 10 jerárquico. Hoja raíz: `INCLI-VA.kicad_sch` (00_top).

## Estructura
| Ruta | Contenido |
|---|---|
| `sheets/10_power_input` | M12, PTC, LM74700-Q1, TVS, filtro LC → +VPROT |
| `sheets/20_isolation` | DC-DC aislado (barrera 1), aislador ISO77xx |
| `sheets/30_regulation` | Buck +3V3_D, LDO +3V3_A, divisores VMON |
| `sheets/40_mcu_kw45` / `40_mcu_esp32s3` | MCU (interfaz idéntica, intercambiables) |
| `sheets/50_sensors` | SCL3300, ASM330LHH, AS5147U |
| `sheets/60_can` | ADM3055E (barrera 2), terminación, ESD, MCP2518FD opcional — reutiliza TP DCI |
| `sheets/70_output_ch` | 1 canal high-side, instanciado 2 veces (DO1, DO2) |
| `sheets/80_supervision` | TPS3431, ID de variante, LED |
| `lib/` | Librería propia: símbolos (`INCLI-VA.kicad_sym`), huellas (`.pretty`), 3D |
| `docs/` | Propuestas KW45 y ESP32-S3 |
| `fab/` | Gerbers, BOM por variante, pick & place |

## Convenciones
- Rieles/masas: símbolos de potencia de la lib `INCLI-VA`: `+VPROT +5V_VEH +5V_ISO +3V3_D +3V3_A GND_VEH GND_ISO GND_CAN`. Nunca `GND` genérico.
- Señales entre hojas: pines jerárquicos; en el top se unen por etiquetas del mismo nombre.
- Prefijos de red por dominio: `VEH_`, `ISO_`, `BUS_`.
- Campos por componente: `MPN`, `Manufacturer`, `Alt_MPN`, `Variant` (CAN, CANFD, OUT, ROT, CABIN).

## Cambiar de MCU
En el top: clic derecho en el bloque `40_mcu` → Properties → Sheetfile → `sheets/40_mcu_esp32s3.kicad_sch`.
Con KW45, las líneas `CANFD_*`, `CS_CAN`, `INT_CAN` quedan sin uso (poner No-Connect dentro de la hoja).
