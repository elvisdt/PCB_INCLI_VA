# INCLI-VA — reglas para Claude

Proyecto KiCad 10 jerárquico. Estructura y convenciones de redes/rieles: ver `README.md`.

## Esquemático

### Librerías
- Usar primero las librerías oficiales de KiCad: `Device`, `Connector*`, `Regulator_*`, `Interface_CAN_LIN`, `Sensor_*`, `Package_*`, etc.
- Si un componente no existe en las oficiales, **no dibujar el símbolo ni la huella a mano**. Avisar al usuario y darle el código LCSC (`Cxxxxx`) para que lo importe a `lib/easyeda2kicad` con:
  ```
  easyeda2kicad --full --lcsc_id=Cxxxxx --output lib/easyeda2kicad/easyeda2kicad
  ```
- Los símbolos de potencia (rieles y masas) salen de la librería propia `INCLI-VA`, como indica el `README.md`.

### Campos obligatorios
- Todo componente lleva `Footprint`, `MPN`, `Manufacturer` y `Datasheet` (además de `Alt_MPN` y `Variant` cuando aplique, según el `README.md`).

### Versión prototipo (soldadura a mano)
Esta revisión es un demo que se va a soldar a mano. Hasta que el usuario indique que pasamos a producción:
- Pasivos (R, C, ferritas): **0603 por defecto**, con las huellas estándar de las librerías oficiales (no hace falta la variante _HandSolder).
- Subir a 0805 o más solo por razones eléctricas o mecánicas: lado vehicular (tensión ≥ 50 V, pérdida de capacitancia por DC bias, flexión cerca del conector), potencia disipada o capacitancia alta. Justificarlo en el campo "Notes" del símbolo.
- LEDs en 0805 o 1206, diodos en SOD-123 o más grandes, transistores en SOT-23 o más grandes.
- ICs: preferir encapsulados con pines visibles (SOIC, TSSOP, MSOP, SOT). Si no hay alternativa a QFN, DFN o LGA, avisar al usuario antes de elegirlo.
- En QFN y DFN con pad expuesto, poner vías en el pad para poder soldar con cautín desde abajo.
- Para el MCU, preferir módulo con pads castellados antes que el chip desnudo.
- Marcar polaridad y pin 1 en la serigrafía, y dejar al menos 1 mm entre courtyards para que entre la punta del cautín.
- Añadir test points en los rieles de potencia y en las señales clave (CAN, SPI, reset).
- Si un componente se elige por ser fácil de soldar y en producción convendría otro, dejarlo anotado en el campo "Notes" del símbolo.

### Conexiones entre hojas
- Las señales entre hojas van por **pines jerárquicos**, no por etiquetas globales.
- Excepción: los rieles de potencia, que usan símbolos de potencia.

### Verificación al terminar cada hoja
1. Correr ERC y filtrar los resultados a esa hoja.
2. Correr `sch_visual_qa` sobre esa hoja.
3. Reportar ambos resultados al usuario: errores, avisos y qué se corrigió.

## PCB
- **No modificar `INCLI-VA.kicad_pcb`** (ni stackup, reglas, netclasses de placa ni "Update PCB from Schematic") hasta que el usuario lo pida explícitamente.
