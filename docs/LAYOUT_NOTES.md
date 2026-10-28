# Estudio de tamaño y ubicación — Codex, 2026-10-27

## Recomendación

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
