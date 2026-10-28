# Estudio de tamaño y ubicación — Codex, actualizado 2026-10-28

## Propuesta vigente: 100 × 100 mm — 2026-10-28

El usuario autorizó preparar y reubicar los componentes en el formato cuadrado. La propuesta está en **`layout/INCLI-VA-100x100.kicad_pcb`**, con su `.kicad_pro`, reglas `.kicad_dru` y la tabla de librerías relativa del directorio. Abrir esa copia para revisar la ubicación. El PCB principal y la propuesta de 120 × 80 mm se conservan sin cambios.

Vista por bloques: **`layout/ubicacion-100x100.png`** (también SVG). Exportación nativa de KiCad de cobre frontal, serigrafía y contorno: `layout/placa-100x100.svg`. Son vistas de revisión, no archivos de fabricación.

### Distribución

- Contorno nominal **100 × 100 mm**, esquinas de radio 4 mm y muesca de antena de 8 × 35 mm en el borde derecho. La reserva RF se extiende fuera del contorno; también deberá quedar libre en la caja.
- Entrada y protección arriba a la izquierda; J1 en el borde izquierdo. Se conserva el espacio de C105 y de todos los DNP.
- J2 arriba, con DO1 y DO2 en dos bloques de distribución equivalente debajo del conector.
- CAN a la izquierda, debajo de la entrada; dominio aislado hacia J1 y lógica hacia el interior.
- Buck de 5 V abajo a la izquierda; regulación de 3.3 V en la zona inferior central.
- AS5147U (U503) exactamente en **(50,50) mm** locales. SCL3300 U501 en **(63,49)** y ASM330LHH U502 en **(76,42)**; sus ejes conservan la orientación previa.
- H5 en **(54,60)**, cerca del conjunto de sensores y separado del eje ROT. H1/H2/H3 en (5,5)/(95,5)/(5,95); H4 en (87,95), desplazado hacia dentro para respetar la antena. Posiciones propuestas, pendientes de validar contra la caja.
- ESP32 en el borde derecho, hacia la mitad inferior; USB-C en el borde inferior. UART0 en la zona inferior central y pulsadores accesibles en la parte superior/derecha.
- Coordenadas locales respecto de la esquina superior izquierda del contorno; en KiCad el origen de esa esquina es (100,50) mm.

### Comprobaciones y límites

- **186 huellas**; igualdad con el PCB principal de referencias, UUID, valores, librerías, campos, atributos/DNP y pads/redes. No se cambió ningún componente ni conexión.
- Separación mínima entre envolventes de courtyards/pads: **1.01 mm** (Q102–TP102). El cuerpo de U401 y su reserva RF se verifican por separado.
- **DRC: 0 errores geométricos, 1 aviso** conocido `lib_footprint_mismatch` en U401 por la serigrafía recortada. **396 conexiones sin rutear**, 0 pistas y 0 zonas de placa. El resultado no es un DRC limpio para fabricación.
- Las siete instancias de pad 25 de U101 conservan `/10_power_input/U101_RTN`; su regla de aislamiento está copiada sin cambios. Se conserva el keep-out de antena de U401.
- Reportes persistentes: `layout/reports/drc-100x100.json` e `integridad-100x100.json`. Revisión visual manual de la imagen completada. No se editaron hojas eléctricas ni se repitió ERC.
- Reproducción desde la raíz: `/usr/bin/python3 scripts/layout_100x100.py`, seguido de `/usr/bin/python3 scripts/review_layout_100x100.py`. Los scripts escriben únicamente la propuesta y sus vistas/reportes, no el PCB principal. El DRC se ejecuta por separado con `kicad-cli pcb drc`.

**El encaje geométrico de 100 × 100 mm está comprobado.** Sigue siendo una ubicación preliminar: falta afinar los desacoples y lazos de los bucks/ADM3055E, revisar retornos, fijaciones/caja/imán y la huella definitiva de C105. Las referencias están en F.Fab; la serigrafía final y el ruteo quedan pendientes. No rutear hasta el visto bueno de ubicación.

## Antecedente: evaluación por área — 2026-10-28

El usuario plantea **100 × 100 mm como máximo**. Es una alternativa favorable por área: 10000 mm² nominales, un 4.2 % más que 120 × 80 mm. Aplicando las mismas deducciones del estudio (muesca de 8 × 35 mm y cuatro esquinas de radio 4 mm), quedarían aproximadamente 9706 mm² útiles y una ocupación estimada del 57.0 % para la reserva de 5536 mm².

Esta comparación inicial solo evaluaba área. La propuesta de 100 × 100 mm descrita arriba ya incorpora la redistribución y verificación geométrica; todavía no demuestra ruteabilidad ni comportamiento eléctrico.

## Antecedente: propuesta de 120 × 80 mm (2026-10-27)

Usar **120 × 80 mm** como base de revisión para 186 huellas, dos capas y acceso de soldadura manual. La propuesta es `layout/INCLI-VA-120x80.kicad_pcb`; la vista a escala está en `layout/ubicacion-120x80.png` y `.svg`. El PCB principal conserva su contorno y ubicación previos hasta confirmar el tamaño. No se añadió ruteo.

100 × 70 mm no queda demostrado imposible; con el margen requerido y todos los DNP resulta muy ajustado. El estudio de 120 × 80 mm sí contiene las 186 huellas dentro de la propuesta, salvo la porción del módulo que corresponde intencionalmente a la muesca de antena.

## Estimación de ocupación

Se sumaron envolventes de courtyards/pads de las huellas, ampliadas 0.5 mm por lado para modelar 1 mm entre vecinos. Para U401 se contaron por separado el cuerpo y el keep-out que cae sobre FR4, sin cargar al PCB el área de keep-out que queda fuera. Se descontó del contorno una muesca de 8 × 35 mm y los cuatro redondeos de radio 4 mm.

| Tamaño nominal | Área útil geométrica estimada | Reserva de huellas, RF y acceso | Ocupación estimada |
|---|---:|---:|---:|
| 100 × 70 mm | 6706 mm² | 5536 mm² | 82.6 % |
| 110 × 80 mm | 8506 mm² | 5536 mm² | 65.1 % |
| 120 × 80 mm | 9306 mm² | 5536 mm² | 59.5 % |

Esto es una estimación conservadora mediante envolventes, no la suma del cobre ni un estudio de ruteabilidad. No incluye todas las reservas de disipación, el arnés ni las herramientas de montaje. El caso 110 × 80 mm es solo una comparación de área: no tiene una ubicación verificada. Para 120 × 80 mm se realizó y comprobó la ubicación de las 186 huellas. El aumento de área nominal respecto de 100 × 70 mm es 37.1 %; no se deduce de ello un precio de fabricación.

Los mayores condicionantes son entrada/protección (aprox. 1432 mm² con acceso), conectores J1/J2 (639 mm²), dos salidas completas incluyendo DNP (689 mm²), MCU con periféricos y reserva RF, y cinco fijaciones (316 mm²). C105 se reserva incluso siendo DNP en PROTO.

## Organización visual

- J1 vertical a la izquierda; F101 y protección junto a sus pines de alimentación. C105 arriba a la izquierda; Q101/Q102 y control de entrada en el mismo bloque.
- CAN abajo a la izquierda, con componentes del lado aislado hacia J1 y lógica hacia el centro. No hay plano que puentee FB602.
- J2 arriba, con DO1/DO2 agrupadas debajo y a su derecha; latch y diagnóstico conservan huella.
- LMR38010 y pasivos en el sector central inferior, separados de los sensores. Regulación de 3.3 V a su derecha.
- AS5147U en (60,40) mm locales, centro geométrico reservado para ROT. H5 en (63,73) mm locales, separado del eje y próximo al sector de U501.
- U501/U502 en el sector inferior derecho, con ejes nominales alineados. Su desacople y la rigidez real de la caja requieren afinado.
- ESP32 en el borde derecho, con la muesca y el keep-out trasladados 20 mm en X respecto del proyecto original. USB en el borde superior; UART, BOOT/RESET accesibles por el sector derecho inferior.
- H2 se desplazó hacia dentro para respetar la reserva de antena; las cinco posiciones de fijación son propuestas, no un patrón mecánico aprobado.

## Comprobaciones de la propuesta

- 186 referencias coinciden exactamente con el PCB principal; redes de todos los pads y atributos DNP conservados.
- Separación mínima de envolventes en el modelo: **1.01 mm**. El cuerpo de U401 y su propia reserva RF se tratan como una sola pieza, sin exigir separación entre ambos.
- DRC con `.kicad_pro` y `.kicad_dru` actuales y librerías locales resueltas: **0 errores geométricos, 1 aviso** `lib_footprint_mismatch` de U401, por la modificación de serigrafía conocida.
- **396 conexiones sin rutear**, 0 pistas y 0 zonas de placa. U101 pad 25 conserva `/10_power_input/U101_RTN`.
- Las referencias de la copia se pusieron en F.Fab para revisión; la serigrafía final se hará tras aceptar la ubicación. No se presenta como placa lista para fabricar.
- La imagen se generó con posiciones, dimensiones de pads y envolventes de la propuesta; colores por bloque, líneas discontinuas para DNP. Es una vista de ubicación, no un Gerber.

## Pendiente antes de rutear

1. Confirmar tamaño admisible de la caja y revisar esta distribución por bloques.
2. Afinar posiciones/orientaciones de desacoples contra los pines, especialmente ADM3055E y los dos bucks. El DRC no certifica longitud del lazo de alimentación ni el requisito ADI de recorrido total ≤2 mm.
3. Revisar el retorno de corrientes, espacio térmico, accesibilidad de conectores y altura/adhesivo de C105; verificar su land pattern definitivo.
4. Confirmar eje/altura/cara del imán ROT, fijaciones y distancias al chasis y arnés en la antena.
5. Preparar serigrafía, repetir DRC y obtener el visto bueno final de ubicación. **No rutear hasta ese visto bueno.**

Los reportes de comprobación se generaron en `/tmp/incli-size-check`; los datos de ocupación y posiciones quedan en `docs/layout/` para inspección. No se alteró el esquemático.
