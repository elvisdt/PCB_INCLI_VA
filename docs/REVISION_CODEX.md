# Revisión independiente del esquemático — Codex

Fecha: 2026-10-27. Alcance: `10_power_input`, `20_isolation`, `30_regulation`, `40_mcu_esp32s3` y las dos instancias de `70_output_ch` (DO1/DO2). Revisión de lectura, sin cambios de diseño ni commits. Se leyeron AGENTS.md, README.md, docs/PENDIENTES.md y los últimos commits. No se actualiza PENDIENTES por instrucción expresa del usuario.

**Resultado: no dar por validada todavía la protección de las salidas del demo.** Hay dos hallazgos críticos: el mantenimiento del latch y la especificación del conjunto TVS–MOSFET. Los restantes hallazgos distinguen errores documentales de márgenes que requieren demostración; no se presenta una estimación típica como un límite garantizado.

## Base y método

- Base inicial: `55c95ea`. Durante la revisión Claude Code integró `50_sensors` (`8b8c68c`) y actualizó pendientes (`1811b3b`). Se reexportó el netlist al final para incluir las cargas de esa hoja. Las cinco hojas objeto de esta revisión conservaron sus hashes durante la comprobación final. No se auditan aquí los circuitos internos de 50/60/80.
- KiCad CLI 10.0.7: exportación XML del netlist jerárquico, lectura de campos y notas, cruce de números de pin con las tablas de fabricantes y revisión visual de SVG renderizados. Archivos auxiliares en `/tmp`.
- ERC ejecutado durante la revisión: **0 errores y 0 avisos en cada una de las cinco hojas** (también 0 en ambas instancias de 70). En ese instante: 66 violaciones totales, 39 raíz, 25 CAN y 2 supervisión. Es una medición de ese instante, no una certificación del trabajo paralelo posterior.
- `sch_visual_qa`: **no ejecutado**; no está expuesto entre las herramientas disponibles y tampoco existe como comando. La revisión visual manual no lo sustituye. Se observaron referencias superpuestas en la zona Q101/Q102 y conexiones muy fragmentadas por etiquetas en 10/70; sin un error adicional de conectividad identificado visualmente.
- No se abrió ni modificó el PCB. Courtyards, cobre térmico, keepouts de antena, separación de barreras y acceso real del cautín quedan fuera de la evidencia de esta revisión.

## Críticos

### C1 — El latch de sobrecorriente no tiene margen para mantenerse tras cortar

**Hoja / referencias:** `70_output_ch`, Q701/Q702/Q703, R705=10 kΩ, R706=1 kΩ, R707=10 kΩ; equivalentes Q751/Q752/Q753, R755/R756/R757.

En el netlist, R706 une SENSE con TRIG, R705 lleva la realimentación del colector de Q703 a TRIG y R707 descarga TRIG a GND_VEH. Al apagar Q701, SENSE vuelve aproximadamente a cero por R701. Incluso suponiendo un colector ideal de Q703 a 5 V y corriente de base nula:

`VTRIG máximo = 5 × (1k || 10k) / (10k + (1k || 10k)) = 0,417 V`.

Con VOH real del aislador y VCE(sat) del PNP resulta aún menor. A VBE=0,6 V, R706 y R707 demandarían 0,66 mA, pero R705 aportaría como máximo 0,44 mA. No queda corriente para sostener la base del NPN. El circuito puede entrar en regulación/oscilación o reintentos autónomos en lugar de esperar EN=0. El requisito de firmware de esperar 100 ms no impide estos reintentos de hardware. El frío empeora el margen de VBE. Es una conclusión del circuito, pendiente de validación transitoria, no una medición de oscilación.

**Acción:** recalcular realimentación y umbral con corrientes de base y extremos térmicos; demostrar que el corte permanece hasta EN=0, incluyendo corto permanente a 32 V y el estado durante load dump. No aceptar el límite anotado de ≤3 µs sin evidencia transitoria.

**Fuentes:** [Nexperia BC817, tabla 8 y curvas de VBE](https://assets.nexperia.com/documents/data-sheet/BC817_SER.pdf), [BC807](https://assets.nexperia.com/documents/data-sheet/BC807_SER.pdf); netlist de 70 y requisito de rearme en README.md.

### C2 — TVS de salida sin MPN respaldado y margen de VDS sin garantía

**Hoja / referencias:** `70_output_ch`, D701/D751 `SMCJ188A`, fabricante Littelfuse; Q701/Q751 `FDD7N25LZTM`, 250 V.

La tabla oficial Littelfuse SMCJ consultada enumera 180 y 200 V, pero **no SMCJ188A**. Sí aparece SMAJ188A en la familia SMAJ, de otro tamaño/potencia. No es admisible intercambiarlos implícitamente: falta un datasheet del MPN exacto del BOM. Esto no demuestra que ningún fabricante ofrezca SMCJ188A; demuestra que la atribución y fuente actuales no lo respaldan.

Además, las Notes estiman un clamp de hasta 252 V y lo justifican con un aumento típico del breakdown del MOSFET a temperatura. FDD7N25LZ especifica VDSS máximo de 250 V; sus curvas térmicas típicas no autorizan aumentar ese máximo absoluto. En frío disminuye el breakdown. Tampoco puede garantizarse el clamp a 0,5 A interpolando linealmente VBR y VC sin una especificación que cubra corriente, tolerancia y temperatura. Falta añadir el overshoot de cableado.

**Acción:** identificar fabricante/MPN exactos y demostrar `VDS pico < límite permitido`, con margen en todo −40…85 °C, energía de bobina y carga externa definidas. Si se recurre a avalancha, calcular explícitamente energía, repetición y temperatura inicial: no basta con la cifra de avalancha única de 115 mJ del MOSFET.

**Fuentes:** [Littelfuse SMCJ, tabla eléctrica p. 2 y curvas pp. 3–4](https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smcj_datasheet.pdf.pdf), [Littelfuse SMAJ, tabla p. 2](https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smaj_datasheet.pdf.pdf); [FDD7N25LZ local](datasheets/FDD7N25LZ.pdf), Rev. 1.5, máximos p. 1, características p. 2 y curvas/SOA; [fabricante onsemi](https://www.onsemi.com/download/data-sheet/pdf/fdd7n25lz-d.pdf).

## Importantes

### I1 — La compuerta de salida no recibe los 5 V usados en el cálculo térmico

**Hoja / referencias:** `20_isolation` U202; `70_output_ch` Q701/Q751, R702/R752=4,7 kΩ, R703/R753=100 kΩ, R701/R751=1 Ω.

La especificación de RDS(on) de 0,57 Ω está dada a VGS=5 V. A 0,5 A, la fuente está a 0,5 V sobre masa. Aun con EN ideal a 5 V, la compuerta queda a `5×100/104,7=4,776 V`: VGS≈4,28 V. Con VOH mínimo de U202=VCCO−0,4 V y VCCO=4,9 V, VGS≈3,80 V. Las curvas típicas sugieren funcionamiento, pero no garantizan el RDS(on) anotado a esa excitación.

**Acción:** justificar conducción, disipación y umbral de disparo con el VGS realmente disponible y la temperatura de unión, o cambiar la excitación/selección. La corrección del latch debe considerar también este efecto.

**Fuentes:** [ISO776x-Q1 SLLSEU7E, condiciones de salida y VOH](https://www.ti.com/lit/ds/symlink/iso7763-q1.pdf), [FDD7N25LZ](datasheets/FDD7N25LZ.pdf), tabla RDS(on) y curvas de salida.

### I2 — R102 sigue sin demostración de sobrecarga de pulso a 85 °C

**Hoja / referencias:** `10_power_input`, R102 `AC2512FK-0710KL`, D103, U101.

Para 202 V de entrada y un clamp de 57–63 V, `P(R102)≈1,93–2,10 W`; el caso rectangular conservador de 350 ms equivale a 0,68–0,74 J. La energía real depende de la forma de onda. El campo Notes dice expresamente «Verificar curva de pulso». El tamaño 2512 no prueba por sí solo capacidad para esa sobrecarga con temperatura inicial de 85 °C y repetición. Abrirse R102 deshabilita la alimentación del controlador; cambiar de valor altera VS y la respuesta.

**Acción:** cerrar la curva de pulso del código exacto, derating y repetición, o seleccionar una resistencia de pulso documentada. No basta la potencia nominal a 70 °C.

**Fuentes:** [TI LM74930-Q1 SNOSDF6, §8.2.2.1, ecuación 11](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf); [datasheet Yageo indicado en el esquema](https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-AC_51_RoHS_L_12.pdf). Este último no pudo recuperarse en esta sesión: la capacidad de pulso del MPN queda explícitamente sin verificar.

### I3 — El clamp de VS no está limitado a 63 V en todo el intervalo térmico

**Hoja / referencias:** `10_power_input`, D103 `SMAJ51A`, D104 `BAS21`, R102, U101 pin 22 VS.

SMAJ51A tiene VBR=56,7–62,7 V a 1 mA y 25 °C. El fabricante publica coeficiente térmico típico positivo de 0,1 %/°C: el extremo superior estimado a 85 °C es 66,46 V antes de incluir resistencia dinámica a ~14 mA y calentamiento. D104 resta su caída, pero no demuestra por sí solo VS≤65 V de operación ni margen robusto al máximo absoluto de 70 V. El cálculo típico no prueba que vaya a destruirse U101; sí invalida tratar «57–63 V» como cota en temperatura.

**Acción:** evaluar I–V y temperatura de unión de D103 durante el pulso de 350 ms; especificar un clamp cuyo máximo quede documentado con margen, incluyendo corriente y tolerancias.

**Fuentes:** [Littelfuse SMAJ, pp. 1–2](https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smaj_datasheet.pdf.pdf), [LM74930-Q1, §§6.1/6.5/8.2.2.1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf).

### I4 — Falta cerrar capacitancia efectiva y total de los reguladores

**Hoja / referencias:** `30_regulation` U301/C301/C304/U302/C306/C307, `40_mcu_esp32s3` C401; carga de `50_sensors` C501/C504–C508.

Los valores impresos no incluyen tolerancia, temperatura ni DC bias. Para U301, 22+22 µF nominales (C304/C401) no prueban ni reserva efectiva para TX ni cumplimiento del criterio usado de 47 µF. Dos piezas de ±20 % pueden sumar 52,8 µF antes de los restantes desacoples; TI permite más de 47 µF con validación de Bode. No se demuestra inestabilidad: falta comprobar el criterio, incluida la capacitancia interna del módulo.

Para U302, TI especifica COUT=0,7–10 µF en §6.6 y aclara un mínimo >0,5 µF en condiciones completas. La integración actual conecta a +3V3_A 1 µF de C307, 10 µF de C508 y cinco de 100 nF: **11,5 µF nominales**. El DC bias puede reducirlos a menos de 10 µF, pero el extremo superior tampoco está demostrado. No corresponde revisar solo C307. En la misma selección, C306/C307 de 1 µF requieren demostrar su mínimo efectivo, no exigir erróneamente 1 µF efectivo como dice Notes.

**Acción:** usar curvas de los MPN exactos para extremos de capacitancia de entrada y salida y medir respuesta de carga/estabilidad. No aumentar bulk sin revisar ambos reguladores.

**Fuentes:** [TPS62A02-Q1 SLUSFG7, §§6.3 y 9.2.2.2–9.2.2.5](https://www.ti.com/lit/ds/symlink/tps62a02-q1.pdf), [LP5907-Q1 SNVSA34E, §6.6](https://www.ti.com/lit/ds/symlink/lp5907-q1.pdf); valores/MPN y netlist integrado del proyecto. No se obtuvieron curvas de DC bias de todos los MLCC: este margen queda abierto.

### I5 — El margen de potencia anunciado no se conserva a 85 °C

**Hoja / referencias:** `20_isolation` PS201; `30_regulation` presupuesto; `40_mcu_esp32s3` U401.

EC4AW8-48S05 es **5 V × 1 A = 5 W**, aunque la familia se anuncie hasta 6 W. La curva de convección natural permite aproximadamente 80 % a 85 °C: 4 W, con Vin nominal. El presupuesto anotado de 3,35 W cabe, pero deja 0,65 W (factor disponible/carga ≈1,19), no el factor 1,5 mostrado en hoja 30 (5 W). La curva no garantiza esa capacidad a Vin=9 V ni dentro de la caja instalada.

**Acción:** cerrar presupuesto máximo incluyendo CAN dominante, consumos internos, pérdidas del buck y sensores; verificar a entrada mínima, 85 °C y en caja. No se afirma insuficiencia para WiFi: el nominal cabe; el margen anunciado y el caso térmico completo siguen pendientes.

**Fuente:** [EC4AW8 local, V10 agosto 2025, pp. 1–2 y curva térmica p. 4](datasheets/EC4AW8-48S05.pdf), notas de presupuesto en 20/30. U301 de 2 A no convierte PS201 en una fuente de 2 A a 5 V.

### I6 — BOM aún no permite construir y verificar la entrada con trazabilidad completa

**Hoja / referencias:** `10_power_input` F101/J2 y MPN marcados «a verificar» en 10/20/30/40.

F101 no tiene huella ni MPN de pedido completo ni datasheet; J2 carece de MPN del header y datasheet. C105 está DNP y puede permanecer pendiente, pero F101 no. El texto «2 A / 250 VDC» no demuestra poder de corte DC del fusible frente a la batería ni selectividad durante pulsos. Las tensiones de los MLCC no pueden darse por certificadas a partir del campo Notes si el propio MPN sigue pendiente de especificación.

**Acción:** cerrar F101 y J2 antes de fabricar; confirmar tensión DC, capacidad de interrupción e I²t del fusible. Verificar fichas de pedido de los MPN pendientes, sin sustituirlos implícitamente. LP5907QMFX-3.3Q1 sí figura en el addendum TI consultado: ese código queda respaldado documentalmente.

**Fuentes:** campos del esquema y docs/PENDIENTES.md; [LP5907-Q1, addendum de pedidos](https://www.ti.com/lit/ds/symlink/lp5907-q1.pdf); [referencia de fusible del fabricante para cerrar selección](https://www.bourns.com/products/circuit-protection/fuses). No se valida un fusible definitivo porque todavía no está seleccionado.

## Sugerencias

### S1 — Reservar ajuste de USB y puntos de prueba SPI

**Hoja / referencias:** `40_mcu_esp32s3`, U401 pines 13/14, U402/J401; SPI_SCK/MOSI/MISO.

USB D+/D− van directos al módulo. Espressif recomienda reservar resistencias serie de 22/33 Ω y posiciones de capacitores DNP para ajuste; el circuito periférico del propio módulo muestra enlaces de 0 Ω, por lo que la conexión directa no se clasifica como error funcional. Reservarlos reduce el riesgo de retrabajo. Hay TP de reset y CAN, pero no de SPI en esta hoja; añadir cobertura accesible al cerrar integración, según AGENTS.md.

**Fuentes:** [Espressif Hardware Design Guidelines, USB](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html#usb), WROOM-1 v1.8 §9; AGENTS.md, versión prototipo.

### S2 — Documentar explícitamente interrupción durante load dump y comprobar recuperación

**Hoja / referencias:** `10_power_input` U101/Q101/C105 DNP; `20_isolation` PS201; `40_mcu_esp32s3` EN/U401.

La topología corta por OV a ~38,4 V: protege mediante desconexión, no mantiene la lógica durante todo el pulso. La capacidad instalada de decenas de µF no sostiene cientos de ms. Es esperable reinicio durante load dump, además del brownout de arranque ya documentado. Para 3,35 W, 350 ms, eficiencia 0,8 y descarga de 38,4 a 9 V se requieren aproximadamente 2,1 mF ideales aguas arriba de PS201; 1000 µF DNP no resolvería por sí solo ese caso.

**Acción:** declarar aceptable el reinicio para el demo y verificar recuperación, salidas abiertas y EN; si se exige continuidad, redimensionar desde un requisito de energía y tensión inicial. No se pide cambiar el diseño sin ese requisito.

**Fuentes:** [LM74930-Q1, §8.2](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf), [EC4AW8, entrada mínima](datasheets/EC4AW8-48S05.pdf), netlist/C105 DNP y README.md.

### S3 — Cerrar térmica y soldabilidad con el layout real

**Hoja / referencias:** U101, U201, U301, U401, Q101/Q102/Q701/Q751, R108/R112, R701/R751.

Se respeta el módulo castellado y la mayoría de los pasivos son 0603. U101 tiene huella con vías aisladas del EP; U201 selecciona huella con vías térmicas. Su presencia en la huella no prueba acceso ni aislamiento del cobre de placa. U301 SOT-563 tiene terminales visibles pero paso 0,5 mm: prever lupa y acceso. Los DPAK requieren calentar la aleta; las resistencias de shunt también requieren cobre térmico.

R108/R112 disipan cerca de 0,194 W cada una en la cresta de 202 V; si se usa una variante 1206 de 0,25 W a 70 °C, el margen térmico es reducido a 85 °C y debe cerrarse junto al pulso. R701/R751 disipan 0,25 W continuos a 0,5 A, más el pulso de corto; no confundir ese caso con potencia nominal en ambiente frío. Los cálculos térmicos definitivos requieren cobre, montaje y condiciones reales.

**Fuentes:** [LM74930-Q1, layout y tabla de pines del EP](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf), [TPS7A16-Q1, térmica/layout](https://www.ti.com/lit/ds/symlink/tps7a16-q1.pdf), [FDD7N25LZ, RθJA y máximos](datasheets/FDD7N25LZ.pdf), campos de huella y AGENTS.md. La curva del resistor exacto pendiente de I2 también limita la validación de R108/R112.

## Comprobaciones de pines y circuitos de referencia

No se detectó una permuta de pines de IC en las cinco hojas. Esta tabla registra lo comprobado; «coincide» se refiere a conexión, no resuelve los márgenes indicados arriba.

| Hoja / IC | Conexiones contrastadas con el fabricante | Resultado / fuente |
|---|---|---|
| 10 / U101 | 1 DGATE→Q102.G; 2 A y 15 OUT→fuentes comunes Q101/Q102; 24 C y 18 ISCP→drenador Q102; 20 CS+ por 49,9 Ω antes del shunt; 19 CS− después; 14 HGATE→Q101.G; 22 VS y 23 CAP con C108 entre ambos; 13→GND_VEH; 16 OVCLAMP→masa; 6 EN/7 MODE→VS; 3 SW→divisor UVLO; 5 OV→divisor de entrada; 9 TMR/11 ILIM a sus redes; 12 FLT→VEH_PWR_FLT_N | Coincide con topología common-source de 200 V; **no invertir Q101 para copiar una topología common-drain**. [SNOSDF6 tabla 5-1 y figura 8-1](https://www.ti.com/lit/ds/symlink/lm74930-q1.pdf). |
| 20 / PS201 | 22/23 +Vin→+VPROT; 2/3 −Vin→GND_VEH; 14 +Vout→+5V_ISO; 16 −Vout→GND_ISO | Coincide, versión sin sufijo P. [Cincon V10 p. 7, vista inferior y tabla Single](datasheets/EC4AW8-48S05.pdf). |
| 20 / U201 | 8 IN y 5 EN→+VPROT; 1 OUT→+5V_VEH; 4 GND y 9 EP→GND_VEH; desacoples entrada/salida | Coincide, salida fija 5 V; EP a masa recomendado. [SBVS188E tabla 5-1 y aplicación fija](https://www.ti.com/lit/ds/symlink/tps7a16-q1.pdf). |
| 20 / U202 | 1 VCC1=+5V_VEH, 8 GND1=GND_VEH; 16 VCC2=+3V3_D, 9 GND2=GND_ISO; 2→15 DIAG1, 3→14 DIAG2, 4→13 FLT; 12→5 EN1, 11→6 EN2; 10 INF→GND_ISO | Coincide con ISO7763, 3 canales por sentido. Sufijo F proporciona default bajo al perder la entrada alimentada; los pull-downs locales cubren alta impedancia al faltar alimentación del lado de salida. [SLLSEU7E pinout y tabla funcional](https://www.ti.com/lit/ds/symlink/iso7763-q1.pdf). |
| 30 / U301 | 1 GND→GND_ISO; 2 SW→L301; 3 VIN→+5V_ISO; 4 EN por 100 kΩ a entrada; 5 FB→divisor 453k/100k y CFF=10 pF; 6 PG con pull-up 100 kΩ a +3V3_D | Coincide. Vout nominal=3,318 V; con ±1,5 % FB y resistores ±1 %, aproximadamente 3,215–3,423 V antes de transitorios: dentro de 3,0–3,6 V del módulo. [SLUSFG7 tabla 5-1, §§9.2.2.1–2](https://www.ti.com/lit/ds/symlink/tps62a02-q1.pdf). |
| 30 / U302 | 1 IN y 3 EN tras FB301 desde +5V_ISO; 2 GND→GND_ISO; 5 OUT→+3V3_A; 4 NC abierto | Coincide con SOT-23-5. Pérdida a 25 mA ≈42,5 mW, ΔT≈8,3 °C usando RθJA=195,1 °C/W: margen razonable para esa carga, condicionado al consumo integrado. [SNVSA34E pinout y térmica](https://www.ti.com/lit/ds/symlink/lp5907-q1.pdf). |
| 40 / U401 | 2 3V3→+3V3_D; 1/40/41→GND_ISO; 3 EN RC/reset; 27 IO0 BOOT; 13 IO19 D− y 14 IO20 D+; 37 TXD0/36 RXD0 a UART; IO35/36 EN1/2, IO37/38 DIAG1/2, IO39 FLT; IO47/48 CAN TX/RX; IO21 STBY e IO42 SILENT; IO1/2 VMON | Coincide con tabla de pines y §9. N8R2 tiene PSRAM quad, IO35–37 utilizables y rango ambiente −40…85 °C. [WROOM-1 v1.8 tablas 1-1/3-1](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf). |
| 40 / U402 | 1/6 a D−, 3/4 a D+, 2 GND_ISO, 5 VBUS del USB; CC1/CC2 con Rd separados de 5,1 kΩ; SBU sin uso | Coincide con USBLC6-2SC6, sin cruce D+/D−. [ST DS4260 diagrama p. 1](https://www.st.com/resource/en/datasheet/usblc6-2.pdf). |
| 70 / discretos | MOSFET 1 G, 2 D, 3 S; BC817/BC807 1 B, 2 E, 3 C; BAT54A pin 3 ánodo común al gate, cátodos 1 FLT y 2 LATCH | Numeración compatible con las funciones pretendidas. La topología no tiene circuito de referencia completo de un fabricante: el latch debe validarse por cálculo/simulación/ensayo (C1). [BC817](https://assets.nexperia.com/documents/data-sheet/BC817_SER.pdf), [BC807](https://assets.nexperia.com/documents/data-sheet/BC807_SER.pdf), [BAT54](https://assets.nexperia.com/documents/data-sheet/BAT54_SER.pdf), [FDD](datasheets/FDD7N25LZ.pdf). |

## Pines sin conectar

| Hoja / componente | Pines abiertos | Justificación |
|---|---|---|
| 10 / U101 | 8/17/21 NC; 10 IMON; 25 EP/RTN | Tabla 5-1: NC flotantes; IMON sin uso abierto; **EP flotante, nunca a GND**. El netlist no une EP a otra red. La isla/vías deben mantener esa condición en PCB. |
| 20 / PS201 | 1 NP; 9/11 NC | Tabla Single: 1 no está poblado en versión sin P; 9/11 sin función. No confundir NC con masa. |
| 20 / U201 | 2 FB/NC, 3 PG, 6 NC, 7 DELAY | Versión fija; tabla 5-1 autoriza no usar PG/DELAY y dejar estos pines abiertos. |
| 20 / U202 | 7 OUTF | Salida del canal no utilizado abierta; su entrada INF=0, no flotante. |
| 30 / U302 | 4 NC | Sin conexión interna según tabla de pines. |
| 40 / U401 | 8 IO15, 9 IO16, 12 IO8; 15 IO3; 16 IO46; 26 IO45 | GPIO sin función asignada; IO45/46 con pulls internos para straps por defecto. IO3 requiere conservar la configuración de eFuses prevista para JTAG. No hay pines de alimentación abiertos. |
| 40 / J401 | A8/B8 SBU | USB 2.0 sin alternate mode. |
| 10/70 / BAS21 y BZX84 | pin 2 NC | Terminal sin conexión interna del encapsulado seleccionado. |

Fuentes de esta tabla: los datasheets enlazados en la tabla anterior; [BAS21](https://assets.nexperia.com/documents/data-sheet/BAS19_BAS20_BAS21.pdf) y [BZX84](https://assets.nexperia.com/documents/data-sheet/BZX84_SER.pdf). Las fichas de discretos enlazadas como referencia que no se recuperaron íntegramente no se consideran una verificación adicional de curvas o ratings.

## Valores, tensiones y dominios: balance de evidencia

| Grupo / referencias | Comprobación y límite de la conclusión |
|---|---|
| Q101 250 V y C101 declarado 450 V, entrada 202 V | Tensiones nominales superiores a la cresta; Q101 tiene margen estático de 48 V a 25 °C, no un margen certificado para overshoot/frío. Pinout DPAK G1/D2/S3 coincide con [ST DS6601 Rev. 6](https://www.st.com/resource/en/datasheet/std18nf25.pdf). Falta validar completamente MPN/curvas de C101, aún marcado a verificar. |
| Q102 100 V, D101 ES2G y D102 SMCJ33A | Q102 es el FET posterior al corte, no el que debe soportar 202 V. Para pulso negativo importan tensión positiva previa más clamp negativo y overshoot, no solo los 33 V de standoff. No se certifica ese pulso por el nombre del TVS; requiere forma de onda y curva a temperatura. D101 debe bloquear la cresta positiva. |
| R103 10 mΩ, R104 49,9 Ω, R110 60,4 kΩ | Breaker nominal≈0,99 A con la fórmula de TI; corto nominal de 20 mV/10 mΩ=2 A. Potencia continua del shunt≈10 mW a 1 A. Son umbrales nominales; incluir tolerancias de comparadores/shunt al cerrar selectividad. |
| R106/R107=100k/9,31k; R108/R112/R109=51k/51k/1,62k | UVLO nominal≈6,46 V; OV≈38,38 V. UVLO del módulo aislado domina antes de alcanzar ese mínimo. OV no es una cota instantánea rígida de +VPROT: hay tolerancia y retardo de corte. |
| C102/C103 100 V, C104 100 V; C106 50 V; C107 100 V | Las clases nominales corresponden a VS limitado, salida protegida y filtro. C106 a ~40 V tiene 20 % de margen estático: verificar sobretensión transitoria y capacidad efectiva. C105 50 V permanece DNP. |
| C108 100 nF/50 V entre CAP–VS; C109 10 nF/100 V; C110 68 nF/50 V | C108 soporta tensión diferencial de bomba, no el VS completo; ubicación correcta. C109 limita rampa y C110 temporiza: revisar sus tolerancias con la SOA, no inferir tiempos exactos del valor nominal. |
| L101 10 µH y PS201 | Corriente debe cubrir entrada a Vin mínimo y arranque. El máximo típico de entrada de Cincon es 0,81 A a 9 V/plena carga; la nota «lógica ≤0,5 A» de L101 no abarca todo ese extremo. No se verificaron curvas Isat/temperatura del MPN exacto: pendiente de cierre de BOM. |
| C201/C204 2,2 µF/100 V; C202/C205 100 nF/100 V; C203/C206 10 µF/10 V; C207/C208 100 nF/50 V | Tensiones nominales razonables para +VPROT y rieles 5/3,3 V. C206 debe superar el mínimo efectivo de 2,2 µF de TPS7A16, incluyendo bias/tolerancia. La etiqueta 10 µF nominal no lo demuestra sola. |
| U201 +5V_VEH | Conexión y rango de entrada de 60 V adecuados para salida protegida. La disipación es `(VPROT−5)×I`, no 100 mA utilizables a cualquier entrada: a 38,4 V y 20 mA son 0,668 W, ΔT≈44 °C con 66,2 °C/W. Cerrar I real y PCB a 85 °C. |
| U301/L301/FB301 y divisores VMON | L301=1 µH, Isat anotada 8,7 A, muy por encima del límite de U301; el datasheet local Coilcraft está disponible para el MPN. Divisores VMON dan 1,664 V y 1,659 V; corriente de decenas de µA, disipación sub-mW; C309/C310 filtran ADC. Comprobar firmware/atenuación ADC, no asumir precisión sin calibración. |
| R201–R204, R111, resistores de EN/PG/BOOT y CC | Sus corrientes y potencias a 3,3/5 V son pequeñas frente a una resistencia 0603 corriente; Rd separados de 5,1 kΩ y pulls de 100k/10k consistentes con las funciones descritas. |
| R708/R709/R710 y réplica, D703/D753 | Divisor 100k+100k/220k, zener 5,1 V a entrada U202. A 250 V y DIAG≈5 V: corriente≈1,225 mA y ~0,150 W por cada 100k. Verificar ratings de tensión/pulso y clamp a baja corriente; no usar la tolerancia de zener a su corriente de ensayo como precisión a cualquier corriente. |
| C401/C402/C403, USB y banco | 22 µF+100 nF sigue referencia del módulo; RC EN=10 ms nominal. Banco D401/JP401 está DNP; alimentación USB exige respetar corriente del puerto. El modo reducido y CAN no garantizado ya están advertidos. |

No se encontró unión eléctrica directa GND_VEH–GND_ISO ni GND genérico en las redes revisadas. PS201 y U202 cruzan la barrera en el sentido esperado. +5V_VEH alimenta solo el lado vehicular; +5V_ISO/+3V3_D/+3V3_A se referencian a GND_ISO. GND_CAN permanece separado. Los nombres y conexiones jerárquicas EN/DIAG/FLT, VMON, SPI y CAN coinciden con el top; no se detectaron señales globales usadas para eludir la jerarquía en estas cinco hojas.

La revisión documental no reemplaza ensayos de corto, carga inductiva, RF en TX, arranque y load dump a temperatura. No se han ejecutado simulaciones ni ensayos físicos y no se afirma cumplimiento ISO/EMC del conjunto. Las fichas locales de sensores/ADM3055E se consideran contexto de cargas; sus hojas no son objeto de esta revisión. Las curvas de MLCC, pulso de resistencias y carga externa exacta permanecen como límites expresos de la conclusión.
