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
- Pasivos (R, C, L, ferritas): **0603 por defecto**, salvo que el diseño exija otro tamaño (tensión, potencia, capacitancia, corriente). Si se usa otro, justificarlo.

### Conexiones entre hojas
- Las señales entre hojas van por **pines jerárquicos**, no por etiquetas globales.
- Excepción: los rieles de potencia, que usan símbolos de potencia.

### Verificación al terminar cada hoja
1. Correr ERC y filtrar los resultados a esa hoja.
2. Correr `sch_visual_qa` sobre esa hoja.
3. Reportar ambos resultados al usuario: errores, avisos y qué se corrigió.

## PCB
- **No modificar `INCLI-VA.kicad_pcb`** (ni stackup, reglas, netclasses de placa ni "Update PCB from Schematic") hasta que el usuario lo pida explícitamente.
