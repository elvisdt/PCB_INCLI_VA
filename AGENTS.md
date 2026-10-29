El ruteo del PCB lo continúa Codex en la rama ruteo-agente. Leer docs/RUTEO_TRASPASO.md antes de empezar.

# INCLI-VA — reglas para los agentes (Claude Code y Codex)

Proyecto KiCad 10 jerárquico. Estructura y convenciones de redes/rieles: ver `README.md`.

## Alcance
- MCU único: **ESP32-S3-WROOM-1** (`sheets/40_mcu_esp32s3`). La KW45 está descartada: `sheets/40_mcu_kw45.kicad_sch` se conserva solo como referencia, fuera de la jerarquía. No editarla ni volver a enlazarla desde la raíz.
- Dimensionar la alimentación para el ESP32-S3 con WiFi activo (picos de TX).

## Esquemático

### Librerías
- Usar primero las librerías oficiales de KiCad: `Device`, `Connector*`, `Regulator_*`, `Interface_CAN_LIN`, `Sensor_*`, `Package_*`, etc.
- Si un símbolo o huella no está en las librerías oficiales ni en `lib/`: **no buscarlo en el disco ni dibujarlo a mano**. Detenerse y pedírselo al usuario, indicando el **MPN exacto** y el **encapsulado**.
  - El usuario lo consigue y lo deja en `lib/`: en `lib/easyeda2kicad/` si viene de easyeda2kicad, o en `lib/vendor/<MPN>/` si viene del fabricante.
  - Cuando el usuario avise:
    1. Registrar la librería en `sym-lib-table` y `fp-lib-table` con rutas `${KIPRJMOD}`.
    2. Comparar la huella con el land pattern del datasheet y reportar cualquier diferencia.
    3. Seguir con el diseño.
- Excepción: las huellas de **pasivos de 2 terminales** (fusibles, resistencias, inductores) sí se pueden crear a partir de las dimensiones del datasheet. Se guardan en `lib/INCLI-VA.pretty` y su descripción indica la fuente (fabricante, documento y revisión).
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
- **Pad 25 de U101 (LM74930-Q1, EP/RTN):** su red (pad expuesto, vías e isla en B.Cu) **nunca** se une a GND ni a otra red. Los rellenos de cobre deben respetar su separación. Fuente: datasheet TI SNOSDF6, tabla 5-1 y sección 8.3 (conectarlo a GND anula la protección de polaridad inversa).
  - Al empezar el PCB: crear una regla DRC personalizada (`.kicad_dru`) para esa red que aísle la red de U101 pad 25 de cualquier otra red y de los rellenos.

## Trabajo entre agentes
Este proyecto lo trabajan dos agentes, Claude Code y Codex, por turnos. Estas reglas valen para los dos (`CLAUDE.md` solo importa este archivo).
- Nunca editar el mismo archivo en paralelo: un agente por turno.
- Al empezar el turno: leer `git log` (los últimos commits) y `docs/PENDIENTES.md`.
- Al terminar el turno:
  1. Actualizar `docs/PENDIENTES.md`: lo que se cerró, lo que quedó a medias y los pendientes nuevos.
  2. Hacer commit indicando el agente en el mensaje, por ejemplo `[Claude Code] 40_mcu: ...` o `[Codex] 50_sensors: ...`.
