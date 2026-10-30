# Traspaso del ruteo a Codex — rama `ruteo-agente`

## Cómo retomar

**Entrega de Codex, 2026-10-29. Etapa 3 cerrada en `a881797`; etapa 4 no iniciada.** La autorización del cuello USB ya está aplicada; no queda una propuesta pendiente. Esta sección es el estado vigente; los apartados históricos inferiores describen estados anteriores. Puede continuar el usuario, otro Codex o Claude Code, un agente por turno.

Trabajar exclusivamente en `PCB_INCLI_VA`, rama `ruteo-agente`. Leer `AGENTS.md`, este documento, `docs/PENDIENTES.md` y `git log -5`; comprobar `git status` antes de cambiar nada. **KiCad debe estar cerrado** y sin archivos `~*.lck`, también en `sheets/`. No tocar `PCB_INCLI_VA_manual`, `ruteo-manual` ni sus worktrees. No mover/girar piezas ni cambiar el esquema, reglas o net classes sin nueva autorización. Las autorizaciones aquí documentadas cubren solo los cambios ya aplicados.

### Estado exacto y evidencia

| Etapa | Estado | Commit de cierre |
|---|---|---|
| 0 — reglas/net classes | Cerrada | `36bf77f` |
| 1 — potencia | Cerrada | `b46f185` |
| 2 — CAN | Cerrada y aprobada; auditoría B.Cu posterior en `4bfdfef` | `be5cc7c` |
| 3 — USB/MCU | Cerrada; C404 y movimientos en `802202d`, cuello final autorizado aplicado | `a881797` |
| 4 — sensores/señales | No iniciada; esperar nuevo visto bueno | — |
| 5 — planos | No iniciada | — |
| 6 — fabricación/cierre | No iniciada | — |

Base mecánica: `placement-v1` = `f472680`, más los cambios de ubicación listados abajo. El commit documental posterior a `a881797` solo completa el traspaso; no modifica el PCB.

| Verificación sobre PCB/esquema guardados | Resultado final |
|---|---|
| DRC | **0 errores /57 avisos**: 52 `via_dangling` de masas para etapa 5 +2 `silk_overlap` (Q101/U801) +2 `silk_edge_clearance` y 1 `lib_footprint_mismatch` de U401, conocidos |
| Paridad esquema–PCB | **0 diferencias** |
| ERC total | **0 errores /5 avisos conocidos**: 1 `isolated_pin_label` U101_RTN y 4 `pin_to_pin` SW401/SW402; hoja 40: 0/4 |
| Conexiones sin rutear | **223**: **108 no-GND** para etapa 4 +**107 GND_VEH y 8 GND_CAN** para etapa 5 |
| USB principal J401→U402→U401 | D− **45.9509**, D+ **45.9508 mm**, Δ **0.0001 mm** nominal; sin vías |
| CAN principal J1→U601 | H **22.2139**, L **22.2120 mm**, Δ **0.0019 mm**; incluye 1.6 mm por vía |
| Renders | [Superior](layout/ruteo/etapa3-top.png) y [inferior](layout/ruteo/etapa3-bottom.png), generados y revisados |

Reportes vigentes: [DRC/paridad](layout/ruteo/etapa3-drc.json), [ERC](layout/ruteo/etapa3-erc.json), [medidas y caminos](layout/ruteo/etapa3-medidas.json), [inventario de pendientes](layout/ruteo/etapa3-pendientes.json). La tabla completa USB/EN/desacoples está en «Etapa 3 — cierre final» al final del documento. `etapa3-parcial-*` y `etapa3-propuesta-*` son evidencia histórica. `sch_visual_qa` no estuvo disponible: C404 se revisó visualmente en la hoja 40 exportada por KiCad y en su ampliación; no se cambió de nuevo el esquema en el cierre.

No quedan conexiones pendientes de USB, CC, VBUS, UART, EN/RESET/BOOT ni de las señales CAN. Sí quedan los retornos a planos. **DRC sin errores no significa placa terminada**: las 223 conexiones se informan por separado.

### Siguiente paso: etapa 4 completa, solo tras visto bueno

Cerrar las **108 conexiones no-GND** del inventario siguiente; son airwires del DRC, no número de pads ni número de redes. Preparar retornos locales cortos cuando haga falta; el cierre global de masas corresponde a etapa 5. No volver a rutear RESET/R802 ni la distribución principal MCU/CAN, ya terminadas. Completar los consumidores restantes de +3V3_D (R111/R307), +5V y la distribución analógica.

| Red exacta | Conexiones pendientes | Etapa |
|---|---:|---|
| `+3V3_A` | 16 | 4 |
| `+3V3_D` | 2 | 4 |
| `+5V_VEH` | 7 | 4 |
| `/10_power_input/CAP` | 1 | 4 |
| `/10_power_input/ILIM` | 1 | 4 |
| `/10_power_input/OV` | 2 | 4 |
| `/10_power_input/SW` | 1 | 4 |
| `/10_power_input/TMR` | 1 | 4 |
| `/10_power_input/UVLO` | 2 | 4 |
| `/10_power_input/VS` | 5 | 4 |
| `/30_regulation/PG_3V3D` | 1 | 4 |
| `/50_sensors/SCL_AEXTC` | 1 | 4 |
| `/50_sensors/SCL_DEXTC` | 1 | 4 |
| `/70_output_DO1/EN_5V` | 1 | 4 |
| `/70_output_DO2/EN_5V` | 1 | 4 |
| `/CS_IMU` | 2 | 4 |
| `/CS_INC` | 2 | 4 |
| `/CS_ROT` | 2 | 4 |
| `/DO1_DIAG` | 3 | 4 |
| `/DO1_EN` | 2 | 4 |
| `/DO2_DIAG` | 3 | 4 |
| `/DO2_EN` | 2 | 4 |
| `/IMU_INT1` | 2 | 4 |
| `/IMU_INT2` | 1 | 4 |
| `/LED_G` | 1 | 4 |
| `/LED_R` | 1 | 4 |
| `/PWR_FLT_N` | 3 | 4 |
| `/SPI_MISO` | 4 | 4 |
| `/SPI_MOSI` | 4 | 4 |
| `/SPI_SCK` | 4 | 4 |
| `/VAR_ID0` | 1 | 4 |
| `/VAR_ID1` | 1 | 4 |
| `/VAR_ID2` | 1 | 4 |
| `/VEH_DO1` | 3 | 4 |
| `/VEH_DO2` | 3 | 4 |
| `/VMON_3V3` | 3 | 4 |
| `/VMON_5V` | 3 | 4 |
| `/WDI` | 2 | 4 |
| `GND_CAN` | 8 | 5 |
| `GND_VEH` | 107 | 5 |
| `Net-(C109-Pad1)` | 1 | 4 |
| `Net-(D704-K)` | 3 | 4 |
| `Net-(D754-K)` | 3 | 4 |
| `Net-(D801-A)` | 1 | 4 |
| `Net-(D802-A)` | 1 | 4 |
| `Net-(R108-Pad2)` | 1 | 4 |
| `Net-(R708-Pad2)` | 1 | 4 |
| `Net-(R758-Pad2)` | 1 | 4 |

#### Recorridos y saltos reservados de etapa 4
- **SPI:**
  - SPI_SCK/MOSI/MISO desde U401 hasta U501 (SCL3300), U502 (ASM330) y U503 (AS5147U), con CS_INC, CS_IMU y CS_ROT. TP501–TP503 en B.Cu.
  - **Sin pistas ni vías bajo los sensores. SPI lejos del buck U201 y de L201/L301.**
- **+3V3_A:**
  - Desde C307.1 (154.56, 128.5), salida de U302, hasta U501.4/9, U502.5/8, U503.11/12, C501/C504/C505/C506/C507/C508 y R501–R503. C502 y C503 son de SCL_AEXTC/DEXTC de U501, no de +3V3_A. TP303 (162.5, 135.5) en B.Cu.
  - IMU_INT1/2, SCL_AEXTC/DEXTC.
- **Salidas DO (DO1/DO2):** VEH_DO1/DO2 hasta J2 (net class DO: 0.5 / 0.6 mm), EN_5V, DO*_EN, DO*_DIAG, D704/D754 y R7xx. Nada de DO a menos de 10 mm de U503.
- **Supervisión:** WDI de U801 y VMON_3V3/VMON_5V con R305–R308/C309/C310 (RESET ya cerrado en etapa 3), LED_G/LED_R, VAR_ID0–2 y PG_3V3D (R302.2 → TP305 en (151, 148), B.Cu; U301.6 ya llega a R302.2, esta red no llega a MCU).
- **Periféricos de U101** (todo dentro de `ZONA_U101`; los saltos siguientes son reservas de recorrido, no pistas ya creadas; contrastarlos con el cobre actual antes de ejecutarlos):
  - **SW** (pin 3) → R106.1: F.Cu recto hacia el oeste.
  - **UVLO** (pin 4): va al oeste por el hueco entre R106 y C109 (y ≈ 74.6), sube por x 118.9 y entra a R106.2 por la izquierda. El enlace R106.2 ↔ R107.1 cruza el par Kelvin (y 70.15/70.95, en el hueco R107/R106), así que **salta por B.Cu**: vía junto a R107.1 en (119.0, 69.3) y otra al final de la subida.
  - **OV** (pin 5): baja por x 122.2 hasta R109.1. Desde R109.1, vía en (121.85, 79.7) → B.Cu hacia el sur por x 121.85 hasta y 85.0 → al este hasta una vía en (134.3, 85.0) → F.Cu hasta R112.2 (135.9, 92.28). Falta también R108.2 ↔ R112.1 (Net-(R108-Pad2)).
  - **TMR** (pin 9) → C110.1: recto hacia abajo.
  - **ILIM** (pin 11) → R110.1: por F.Cu, baja por x 126.15 y va al este por y 77.95, al oeste de HGATE.
  - **FLT** (pin 12) → R111.2 y TP104 → MCU: cruza HGATE/OUT (x 128.78 y 129.28), así que salta por B.Cu (vía junto al pin 12, en ≈ (126.95, 77.25); vía en ≈ (130.0, 77.9) y F.Cu hasta R111.2).
  - **EN/MODE** (pines 6/7, unidos a VS):
    - Tramo en la esquina por F.Cu: (123.3, 75.25) → (123.3, 76.2) → pin 7.
    - Vía en (123.3, 76.9), B.Cu hacia el norte por x 123.4 hasta y 69.85, y al este hasta la vía de VS.
  - **CAP** (pin 23) → C108.1: vía en (124.45, 70.55) → B.Cu en "U" por y 71.35 → vía en (126.87, 70.1) → C108.1.
  - **VS** (pin 22) → C108.2: vía en (125.25, 70.25) → B.Cu por y 69.4 → vía en (128.42, 70.1) → C108.2 → C102.1 por F.Cu.
  - **VS → D104.3:** F.Cu desde C108.2 al este por y 69.0 hasta x 133.2, abajo hasta y 84 y a D104.3 (131.0, 84.67). Ya no cruza OUT, que ahora baja por x 129.28.
  - Todas estas vías quedan **dentro** del arco VOUT en B.Cu (x 117.6–129.4, y 66.6–71) y lejos del arco C_ID (x 116.6–130.53, y 65.6).
  - **GND:** pin 13 → vía en (127.75, 76.55); pin 16 → vía en (128.55, 73.4).
  - **Vías GND de la fila R109–R111:** R109.2 → vía en (122.6, 81.5); C110.2 → (125.42, 81.4); R110.2 → (127.97, 81.4). R107.2 y C109.2 llevan vía propia.
  - **R111.1 (+3V3_D):** sale al este por F.Cu (está fuera de los risers de HGATE/OUT).
  - **R105.2 ↔ C109.1** (Net-(C109-Pad1)): enlace corto vertical.
- **Aceptación:**
  - DRC 0 errores. Ninguna pista ni vía bajo U501/U502/U503.
  - Círculo de Ø17.9 mm libre de piezas ajenas.
  - Potencia y DO a ≥ 10 mm del borde del cuerpo de U503; solo se conserva la excepción aprobada del tronco +5V existente a 9.8 mm.
  - SPI a ≥ 10 mm de L201/U201/L301.

Las reservas anteriores son propuestas geométricas heredadas, **no una orden de insertar vías sin revisar obstáculos**. Los enlaces UVLO, OV, FLT, EN/MODE, CAP y VS requieren los saltos B.Cu indicados; conservar Kelvin y arcos VOUT/C_ID. Los saltos CAN y USB ya están implementados, no son pendientes de etapa 4.

**Criterios de cierre de etapa 4:** todas las conexiones no-GND anteriores cerradas (o excepción explícita del usuario), DRC 0 errores, paridad 0, ERC sin regresiones; regresión CAN/USB/EN/desacoples con `verify_etapa3.py`. Nada de pistas/vías bajo U501/U502/U503 en ninguna cara; círculo ROT, apoyo B, arandelas y antena respetados. SPI ≥10 mm de U201/L201/L301 y potencia/DO ≥10 mm del cuerpo de U503, salvo tronco existente +5V a 9.8 mm. Mantener barrera CAN y aislamiento absoluto de U101 pad 25. Renders de ambas caras, tabla de medidas críticas y pendientes restantes, revisar `.kicad_pro`, actualizar documentos, commit con agente y push; esperar visto bueno antes de etapa 5. No generar planos como parte de etapa 4.

### Excepciones y compromisos aprobados: conservar

| Tema | Decisión vigente y obligación posterior |
|---|---|
| C608 | **2.145 mm** entre bordes al pin U601; excepción al objetivo ≤2 mm. Sin moverlo. C601/C604/C607/C610 mantienen ≤2 mm. |
| Desacoples grandes CAN | Pin → pequeño → grande, sin derivación independiente al grande; C602/C603/C606 conservan ubicación. C602 es **100 nF**, C603/C605/C606 son 10 µF. Cada retorno corto a su masa; C606/C610 a **GNDISO_CAN**, antes de FB602, sin puentearla hacia GND_CAN. |
| C605 VIO | Camino de **12.2704 mm**, bulk aceptado condicionado al retorno continuo en etapa 5: vía (144.28,121.9) → C602/C601/U601, con costura local. |
| D601 y CANH | Giro 180° evaluado: traslada el cruce al lado J1; **no se aplicó**, queda r0, DNP PROTO/PROD. Puente CANH B.Cu **3.844 mm** entre (114.45,115.75) y (118.2,116.595), dos vías. CANL sin vías; Δ≤1 mm incluyendo altura. Conservar retorno corto D601.3 a GND_CAN. |
| B.Cu CAN y planos | Inventario completo más abajo; cuatro redes: H 3.8440, V_SOIN 13.5902, GNDISO_CAN 16.3134 y punto medio C609 6.7238 mm. Prueba temporal: **una región GND_CAN, ocho vías y J1.5 conectados, DRC 0**. No es un plano definitivo. Se conserva `ISO_sin_relleno_bajo_U601`: **sin cobre de relleno en su courtyard/cuerpo**. Repetir continuidad y añadir costura en etapa 5. |
| USB B6/B7 | Cuatro vías totales solo en los ramales de J401: D+ (192.2,79.37)/(190,82.5); D− (192.4,81.425)/(190.4,79.6), Ø0.6/0.3. Principal A6/A7→U402→U401 sin vías; ramales no incluidos en su Δ. |
| Cuello D− | **0.15 mm × 1.922754 mm**, F.Cu, autorizado y aplicado. (173,107.5) → (173.2825,107.7825) → (173.6,107.7825) → (174.8,107.9); clearance ≥0.2 mm. Resto USB 0.3/0.2 en tramos acoplados, aperturas de pads y ajuste D+; Δ≤0.5 mm. |
| USB/EN y desacoples MCU | USB Full-Speed 0.3/0.2 aprobado sin impedancia controlada. C402 primero (0.7750 mm al pin entre bordes), C401 detrás en cadena; C404 0.5748 mm a U402. EN≤5 mm se aplica al RC local entre bordes (R401 4.9641, C403 1.5415), no a los ramales RESET remotos documentados. |
| U503 | 10 mm medidos desde **borde del cuerpo**; única excepción de potencia: tronco +5V existente x137.6 a **9.8 mm**. Mantener libre Ø17.9 en ambas caras. |
| U101 | ~11 vías/saltos B.Cu aceptados; coser el retorno en etapa 5. HGATE ~17 mm y DGATE ~25 mm aceptados por trazado paralelo a VA. **RTN pad25 nunca a GND ni a otra red**, tampoco por rellenos. |
| Buck/U301 | C201 a VIN por C202, diagonal 8.6 mm; lazos C202 ~3.9 mm² y C201 ~26.4 mm². U301 GND pin1/C302 con vías propias, lazo ~5 mm². C206 alejado (~12.8 mm del EP) con vía propia: continuidad al plano en etapa 5. TP301 ya retirado de SW: asegurar GND continuo bajo SW. |
| Huellas y fabricación | J401 NPTH–cobre oficial ~0.1944 mm, regla local 0.19 aceptada. Taladros térmicos existentes de 0.2 mm (U101/U201; U401 pad41 conserva 12) no autorizan vías de ruteo menores: usar 0.6/0.3. Courtyards de placement y sus excepciones aceptadas se conservan. SCL3300 DFL-12 tiene pads 0.32 mm más largos que el land pattern para soldadura manual; revisión de huella en producción pendiente, sin cambiarla ahora. C104 debajo exige separadores ≥12 mm y adhesivo. |
| Reglas locales | Conservar excepciones PROT de sensado, zona U101, buck, Vgs y llegada a pads descritas en la tabla de reglas de sección 2. No crear clearance global sin condición. CAN acoplado a mano, sin renombrar redes para autodetección diferencial. |

### Cambios posteriores a placement-v1 para replicar en ruteo-manual

**La réplica no se hizo; corresponde al usuario en su copia manual.** La sección 3 contiene coordenadas originales y finales completas. Resumen (mm absolutos KiCad; rotaciones en grados):

| Pieza | Cambio final autorizado | Tipo |
|---|---|---|
| C104 | F(138.5,75.57) r−90 → **B(106.85,71) r0**, pad1 oeste | Ubicación/cara |
| U301 | (140.4,135.81) r90 → **r270** | Giro |
| C302 | (139.2,139.5) r90 → **(138.1,135.875) r270** | Ubicación/giro |
| TP101 | B(138.5,65.5) → **B(127.6,61.5)** | Ubicación |
| TP301 | B(140,134) → **B(140,131.6) r180**; eliminar bajada anterior bajo SW | Ubicación |
| C401 | F(189.263603,100.013603) r0 → **F(189.2,100.6) r90** | Ubicación/giro |
| C402 | F(189.9,104.2) r0 → **F(189.18,104) r90** | Ubicación/giro |
| R401 | F(162.060355,146.485355) r90 → **F(187,100.1) r270** | Ubicación/giro |
| C404 | **Nuevo**: hoja 40 (365.76,63.5); PCB **F(189.6,81.45) r0**, VBUS–GND_VEH | Esquemático y PCB |

C404: 100 nF, 0603, X7R, **50 V** (cumple ≥16 V), `MPN=GCM188R71H104KA57D`, `Manufacturer=Murata`, `Footprint=Capacitor_SMD:C_0603_1608Metric`, `Datasheet=https://www.murata.com/en-global/products/productdetail?partno=GCM188R71H104KA57D`, `DNP` vacío y nativo `dnp no`. Cambio de esquema registrado en PENDIENTES.md; incorporado con UUID y path de hoja correctos, **no hizo falta F8**, paridad 0. No une VBUS con +5V. No reemplazar hojas completas de la copia manual ni perder su trabajo al replicarlo.

Ajustes de serigrafía asociados: referencia U301 (142.2,132.8); C401 (189.2,97.7) r0; C402 (190.9,104) r90; R401 (185.6,97.8) r0; C403 (185.55,103.5) r90; C404 (189.6,84.1) r0; «SIN BARNIZ» J401 (192,88) r0. **C403 no cambió de ubicación**. D601 tampoco se giró.

### Decisiones abiertas y obligaciones futuras

- Nuevo visto bueno para comenzar etapa 4. No queda autorización de etapa 3 pendiente.
- Lado del imán ROT sin definir: mantener Ø17.9 mm libre en ambas caras, salvo U503 y pasivos previstos.
- Velocidad CAN 250/500 kbps se define en firmware; no bloquea este ruteo.
- R602/R603/C609 montadas en PROTO; montaje de terminación en PROD según instalación.
- Stock de C105 PROD se confirma con el BOM, sin bloquear ruteo. Revisar también MPN «a verificar» de PENDIENTES antes del BOM final; ensamblador/stock de producción se revisarán cuando corresponda.
- Pendientes técnicos previos, sin bloquear este cierre: validar R102 anti-pulso en 2512 contra el pulso documentado (si exige otra huella, consultar); verificar térmica/EMC y fijaciones H1–H5/apoyo B con la futura caja. Se conservan en PENDIENTES.md.
- «Plano bajo U601»: se mantiene la regla vigente sin relleno en todo su courtyard. La auditoría prueba continuidad **hasta sus retornos**, no cobre bajo el cuerpo. Cambiar esa interpretación requiere decisión del usuario y revisión de la regla; no hacerlo por inferencia.
- Etapa 5: continuidad bajo SW de U301, bajo buck y sensores, retorno C605 y distribución 3V3 del MCU, costura alrededor de CAN y saltos de U101; resolver las 52 vías GND colgantes actuales y las nuevas de etapa 4. Etapa 6: teardrops, verificación final y fabricación; no iniciarlas ahora.

### Scripts de scripts/ruteo/ y uso correcto

Usar `/usr/bin/python3` (pcbnew de KiCad 10; matplotlib para auditoría). Ejecutar desde la raíz del proyecto. Los generadores **editan el diseño**; no se usan como pruebas.

| Script | Función y precaución |
|---|---|
| `etapa1_potencia.py INPUT OUTPUT` | Genera potencia/posiciones de etapa 1 desde base etapa 0. No es idempotente sobre la placa actual: duplicaría cobre. Solo reconstrucción deliberada en copia aislada completa. |
| `etapa2_can.py` | Regenera grupo `CODEX_ETAPA2`, fuente/CAN/retornos y TP301. Borra/recrea sus pistas y vías por UUID; perdería ediciones manuales posteriores de ese grupo. |
| `etapa3_mcu.py` | Regenera `CODEX_ETAPA3`, posiciones autorizadas y ruteo MCU/USB con cuello final. Requiere C404 presente y KiCad cerrado; no ejecutarlo para inspeccionar ni sobre ruteo manual posterior. |
| `add_c404.py` | Añade C404 en esquema y PCB con campos/path; detecta si ya está. Ya aplicado. No ejecutarlo sobre la copia manual sin autorización específica. |
| `verify_etapa2.py` | Lee PCB, reconstruye caminos/cadenas, mide desacoples y CAN incluyendo altura, comprueba dos vías H/ninguna L y Δ≤1 mm. Emite JSON. |
| `verify_etapa3.py` | Lee **PCB guardado**, ejecuta también regresión CAN; exige USB principal cerrado/sin vías, cuatro vías de ramales, cuello exacto, Δ≤0.5 mm, EN/desacoples/cadenas y conectividad UART/CC/VBUS/3V3. Emite JSON; nunca usa propuesta temporal. |
| `audit_can_bcu.py` | Copia PCB/.pro/.dru a temporal, rellena GND_CAN B.Cu respetando courtyard y barrera, comprueba una región/8 vías/J1 conectados y DRC 0. Escribe `can-bcu-auditoria.json/png`; no añade planos al PCB guardado. Repetir en etapa 5 y revisar cobertura si cambian retornos. |
| `preview_usb_escape.py` | Propuesta histórica del cuello sobre copia temporal, ahora detecta el cuello existente y sale sin duplicarlo. No usar para verificar cierre; usar `verify_etapa3.py`. |

Comprobación reproducible sin regenerar pistas ni sobrescribir evidencia del cierre (KiCad cerrado; salidas nuevas en /tmp):

```bash
# Desde PCB_INCLI_VA; debe mostrar ruteo-agente y árbol limpio al recibir la entrega.
git branch --show-current
git status --short
git log -5 --oneline
/usr/bin/python3 scripts/ruteo/verify_etapa2.py > /tmp/incli-can-medidas.json
/usr/bin/python3 scripts/ruteo/verify_etapa3.py > /tmp/incli-mcu-medidas.json
# Un solo comando ejecuta DRC y paridad esquema–PCB:
kicad-cli pcb drc --schematic-parity --severity-all --format json -o /tmp/incli-drc.json INCLI-VA.kicad_pcb
kicad-cli sch erc --severity-all --format json -o /tmp/incli-erc.json INCLI-VA.kicad_sch
kicad-cli pcb render --side top --width 1600 --height 1600 --quality basic -o /tmp/incli-top.png INCLI-VA.kicad_pcb
kicad-cli pcb render --side bottom --width 1600 --height 1600 --quality basic -o /tmp/incli-bottom.png INCLI-VA.kicad_pcb
git diff -- INCLI-VA.kicad_pro
```

En DRC JSON contar `violations` por severidad, `schematic_parity` y `unconnected_items` por separado. En ERC recorrer `sheets[].violations`. Para reproducir la auditoría prospectiva CAN: `/usr/bin/python3 scripts/ruteo/audit_can_bcu.py`; revisar el diff de sus artefactos porque escribe en docs. No ejecutar generadores para «comprobar» la placa. Revisar visualmente ambos renders; los planos GND todavía no existen.

### Trampas conocidas antes de continuar

1. **pcbnew y `.kicad_pro`:** cargar un PCB temporal y guardarlo en el proyecto puede sobrescribir `.pro` con defaults, perdiendo clases y patrones. Cargar/guardar la ruta canónica; para pruebas copiar PCB, `.pro` y `.dru` juntos a una carpeta temporal. Nunca restaurar un PCB viejo encima del actual para verificarlo.
2. **Antes de cada commit ejecutar `git diff INCLI-VA.kicad_pro`.** KiCad CLI también puede reordenar clases. En este cierre solo cambió el orden; se comprobó equivalencia JSON ordenando por nombre y se conservó exactamente el archivo anterior. Nunca descartar cambios reales del usuario como si fueran orden.
3. **Clearance sin condición** en `.kicad_dru` anula las separaciones de net classes; piso de fabricación en Board Setup. La última regla coincidente manda. Funciona `A.NetClass`; `A.Track_Width` no. Si dejan de actuar clases, revisar `.pro` antes de tocar reglas.
4. **KiCad cerrado antes de editar**; ningún editor debe guardar una copia antigua encima del trabajo. No eliminar locks para forzar acceso. Usuario confirmó cierre antes de esta sesión.
5. Eliminar grupos con `pcbnew.Remove` puede provocar fallo de SWIG; los generadores eliminan bloques por UUID antes de cargar. Regenerarlos cambia UUID: revisar geometría, no solo IDs. KiCad 10 guarda redes por nombre, no asumir códigos numéricos de versiones anteriores.
6. Medidas CAN incluyen 1.6 mm por vía según configuración existente; USB principal no tiene vías. Separar ramales de terminación/B6/B7 y RESET remoto de recorridos principales/locales. No declarar placa completa por el código de salida 0 del CLI.
7. Respetar siempre barrera CAN, GNDISO_CAN a través de FB602 y **U101 pad25 RTN aislado**. No arreglar avisos conocidos cambiando huellas/reglas sin autorización. No rellenar bajo courtyard U601 para satisfacer una lectura ambigua de «bajo el transceptor».

---

Traspaso original de Claude Code y actualización de Codex, 2026-10-29. Documento de continuidad en `ruteo-agente`; los apartados históricos conservan la evolución del proyecto.

**Actualización de Codex, 2026-10-29:** etapas 0–3 cerradas; etapa 2 aprobada y auditada. El usuario autorizó el cuello D− de 0.15 mm × 1.923 mm y ya está aplicado al PCB guardado. Etapa 3: DRC 0 errores /57 avisos, paridad 0, ERC 0 errores /5 avisos; 223 conexiones pendientes (108 de etapa 4 y 115 de masas para etapa 5). No iniciar etapa 4 sin nuevo visto bueno.

Antes de empezar: leer `AGENTS.md`, `git log -5` y `docs/PENDIENTES.md`. Al terminar cada etapa: DRC, render de las dos caras, commit `[Codex] ruteo etapa N: ...`, `git push origin ruteo-agente`, y **esperar el visto bueno del usuario**.

> **No tocar** la carpeta `../PCB_INCLI_VA_manual` (git worktree, rama `ruteo-manual`). Es la copia que el usuario rutea en paralelo. Tampoco ejecutar `git worktree remove` ni `git worktree prune`.

---

## 1. Estado histórico al cierre de etapa 1

| | |
|---|---|
| Rama / commit de etapa 1 | `ruteo-agente`, `b46f185` |
| Base de ubicación | tag `placement-v1` (f472680) + cambios de la sección 3 |
| DRC | **0 errores**. Avisos: 19 `via_dangling` (vías GND que esperan el plano de la etapa 5), 2 `silk_overlap` (referencias de Q101 y U801, de antes), 2 `silk_edge_clearance` y 1 `lib_footprint_mismatch` de U401 (conocidos, aceptados) |
| Paridad con el esquemático | **0** |
| Conexiones sin rutear | **288** (358 en `placement-v1`) |

### Ruteado (etapa 1, potencia)
- **Entrada (F.Cu, 1.5 mm):**
  - J1.1 → F101 → VBAT_F → tab de Q101, R102, C101, R108 y D101; TP102 por vía.
  - D101 ↔ TVS D102. El GND del TVS va directo a J1.2.
- **Q101/Q102:**
  - VA, la fuente común, va en 1.0 mm por y 82.5. C_ID: tab de Q102 → R103.1. VOUT: R103.2 → tronco de 1.5 mm por x 102.6 → y 60 → L101.1.
  - C104 (B.Cu) se une por 2 vías. C105.1 se une por 3 vías y un tramo en B.Cu.
- **Kelvin de R103:** 2 pistas de 0.25 mm que salen de los pads del shunt y corren paralelas (0.55 mm) por debajo de C105, en y 70.15 (VOUT) y 70.95 (C_ID).
  - C_ID va a R104.2. VOUT va a CS- (pin 19) con un arco por B.Cu.
  - ISCP (pin 18) y C103 se unen a la Kelvin C_ID con otro arco por B.Cu, exterior al anterior.
  - CS+ (pin 20) → R104.1. C (pin 24) → R104.2.
- **Gates:**
  - HGATE (pin 14 → R105 → Q101.1) va paralela a OUT/VA (pin 15), 0.5 mm entre ejes, por x 128.78/129.28 y por y 82.3/82.85.
  - DGATE (pin 1 → Q102.1) va por B.Cu, justo debajo del retorno de A/VA (pin 2 → tronco VA).
- **+VPROT:** L101.2 → C106/C107 → C201 → diagonal → pad de C202 → VIN (pines 2 y 3) de U201. TP101 por vía.
- **Buck U201:**
  - SW de 3.7 × 1.2 mm hasta L201. C202.2 va directo por F.Cu al pin 1 y al pad expuesto. C201.2 → pad expuesto.
  - BOOT con C203. FB: pin 5 → R202 → R201, y la parte alta de R201 toma +5V en el pad de C204.
  - RT → R203. Vía a GND en cada pad de C204, C205 y C206.
- **+5V:**
  - C204 → C206. Tronco de 1.0 mm: C206 → x 147.7 → y 69.5 → x 137.6 → y 110.6 → x 147.3 → y 124.8 → x 143.5 → FB301.1 y y 131.6 → U301.
  - TP201 y TP301 por vía.
- **U301 (girado 180°):** SW (pin 2) al norte, hasta L301 por F.Cu. VIN (pin 3) → C302.1, pegado al oeste. GND (pin 1) por vía. EN, FB y PG salen al sur por F.Cu: nada pasa bajo el nodo SW.
- **3V3_D:** L301.2 → R302.1 → C304.1. FB alto desde C304.1 (→ C303.1 → R303.1). TP302 por vía.
- **U302 (LP5907, 3V3_A):** FB301 → IN/EN con C306, OUT → C307.1. GND del pin 2 por vía.

### Sin rutear, por red (288 en total)
GND_VEH 106 (etapa 5) · +3V3_A 16 · +3V3_D 14 · +5V_VEH 10 · GND_CAN 8 · VS 5 · MCU_RST_N 5 · SPI_MISO/SCK/MOSI 4 c/u · GNDISO_CAN 4 · USB_D+/D- 4 c/u · VEH_DO1/DO2 3 c/u · BUS_CAN_H/L 3 c/u · BOOT 3 · Net-(D704-K)/(D754-K) 3 c/u · VMON_5V/VMON_3V3 3 c/u · V_SOOUT/V_SOIN 3 c/u · PWR_FLT_N 3 · DO1_DIAG/DO2_DIAG 3 c/u · VBUS 3 · y ~45 redes con 1–2 (CAN_RX/TX/SILENT/STBY, CS_*, IMU_INT*, OV, UVLO, TMR, ILIM, CAP, SW, Net-(C109-Pad1), Net-(R108-Pad2), VAR_ID0–2, LED_G/R, WDI, CC1/CC2, U0TXD/RXD, PG_3V3D, EN_5V, CAN_RS, Net-(C609-Pad1), …).

Para regenerar la lista: correr el DRC (sección 8) y agrupar `unconnected_items` por red.

---

## 2. Reglas vigentes

### Net classes (`INCLI-VA.kicad_pro`; se asignan por patrón de nombre de red)
| Clase | Redes | Pista | Separación | Par (ancho / gap) | Vía |
|---|---|---|---|---|---|
| Default | resto | 0.2 | 0.2 | — | 0.6 / 0.3 |
| HV | `/10_power_input/VIN_VEH`, `/10_power_input/VBAT_F` | 1.0 | 1.25 | — | 0.6 / 0.3 |
| PROT | `/10_power_input/VA`, `/10_power_input/C_ID`, `/10_power_input/VOUT`, `+VPROT` | 1.0 | 0.6 | — | 0.6 / 0.3 |
| DO | `/VEH_DO1`, `/VEH_DO2` | 0.5 | 0.6 | — | 0.6 / 0.3 |
| 5V | `+5V_VEH`, `/20_buck_5v/BUCK_SW` | 0.5 | 0.2 | — | 0.6 / 0.3 |
| 3V3 | `+3V3_D`, `+3V3_A` | 0.4 | 0.2 | — | 0.6 / 0.3 |
| CAN | `/BUS_CAN_H`, `/BUS_CAN_L` | 0.3 | 0.2 | 0.3 / 0.3 | 0.6 / 0.3 |
| USB | `/40_mcu/USB_D+`, `/40_mcu/USB_D-` | 0.3 | 0.2 | 0.3 / 0.2 | 0.6 / 0.3 |

- **Board Setup:**
  - Piso cobre-cobre de 0.15 mm (`min_clearance`, JLCPCB).
  - Anchos predefinidos 0.2 / 0.25 / 0.3 / 0.4 / 0.5 / 0.6 / 1.0. Vía 0.6/0.3. Pares 0.3/0.3 y 0.3/0.2.
  - Teardrops activados en vías, pads PTH y SMD (formas redonda y rectangular).
- **El par CAN no se detecta como par diferencial:** KiCad reconoce pares solo por el sufijo `+/-` o `P/N`. **No renombrar las redes** (decisión del usuario). Se rutea acoplado a mano, 0.3/0.3.
- **USB 0.3/0.2:** aprobado. Es Full-Speed; la impedancia no está controlada.

### `INCLI-VA.kicad_dru`, regla por regla (en KiCad, si hay varias que coinciden, manda la última del archivo)
| Regla | Qué hace | Motivo |
|---|---|---|
| `Pads_mismo_encapsulado` | 0.15 mm entre pads de un mismo componente (`A.Parent == B.Parent`) | La separación la fija el encapsulado (QFN 0.5, SOIC, LGA). No hay una clearance general sin condición: anularía las net classes |
| `JLC_ancho_pista` | Pistas de ≥ 0.15 mm | Capacidad de JLCPCB |
| `JLC_via` | Vía con hueco ≥ 0.3, diámetro ≥ 0.6 y anillo ≥ 0.15 | Sin costo extra en JLC |
| `JLC_hueco_min` | Hueco ≥ 0.2 mm | Vías térmicas de U101/U201 |
| `JLC_anillo_PTH`, `JLC_hueco_a_hueco`, `JLC_hueco_a_cobre_via`, `JLC_hueco_a_cobre_PTH` | Mínimos de JLC | Capacidades de JLC |
| `JLC_borde` | Cobre a ≥ 0.5 mm del borde | Margen sobre los 0.2 de JLC |
| `JLC_serigrafia` | Texto de ≥ 0.8 mm, trazo de ≥ 0.15 | JLC |
| `U101_RTN_aislado` | La red `/10_power_input/U101_RTN` (EP de U101, sus vías y la isla en B.Cu) queda a ≥ 0.3 mm de todo y sin conexión a rellenos | TI SNOSDF6, tabla 5-1 y sección 8.3: unirla a GND anula la protección contra polaridad inversa |
| `U101_pad25_nunca_GND` | Error si el pad 25 de U101 cambia de red | Seguro |
| `H_anillo_cobre` / `H_zona_arandela` | Cobre a ≥ 0.5 mm del anillo de H1–H5; pistas y vías a ≥ 0.8 mm del anillo (≥ 4 mm del centro) | Arandela M3, anillo sin red |
| `HV_entrada_202V` | VIN_VEH/VBAT_F a ≥ 1.25 mm de otras redes (no aplica entre pads) | Load dump de 202 V sin suprimir; IPC-2221B B2, 171–250 V |
| `MV_salidas_DO_100V` | VEH_DO1/DO2 a ≥ 0.6 mm (no aplica entre pads) | IPC B2, 51–100 V (pico recortado por D701) |
| `ISO_CAN_barrera` | Dominio CAN (GND_CAN, BUS_CAN_H/L, V_SOIN, V_SOOUT, GNDISO_CAN, CAN_RS, Net-(C609-Pad1), pin 17 de U601) a ≥ 2.5 mm del resto, salvo dentro de U601 y J1 | Aislamiento funcional; IPC B2, 301–500 V |
| `ISO_sin_relleno_bajo_U601` | Sin rellenos dentro del courtyard de U601 | No achicar los 8.3 mm de CLR/CRP del encapsulado |
| `IPC2152_entrada_2A` | Pistas de VIN_VEH, VBAT_F, VA, C_ID, VOUT y +VPROT de ≥ 1.0 mm | IPC-2152, 2 A |
| `IPC2152_salidas_DO` | DO de ≥ 0.5 mm | Relé de ≤ 0.5 A |
| `IPC2152_buck_5V` | +5V y BUCK_SW de ≥ 0.5 mm | ≤ 1 A |
| `PROT_sensado` | Una pista PROT de ≤ 0.3 mm se trata como sensado: mínimo 0.25 mm | Kelvin de R103 y pines A/OUT/C de U101 (µA) |
| `PROT_sensado_entre_PROT` | Sensado PROT contra otra red PROT: 0.3 mm | La Kelvin VOUT/C_ID solo ve la caída del shunt (mV) |
| `PROT_zona_U101` | PROT dentro de `ZONA_U101`: 0.2 mm y pista de ≥ 0.25 (no aplica contra HV ni RTN, ni entre pads de un mismo componente) | Mismas tensiones que entre pines del VQFN, placa con coating (IPC B4) |
| `PROT_zona_buck_U201` | PROT dentro de `ZONA_BUCK_U201`: 0.25 mm (mismas excepciones) | Pedido del usuario: lazo de entrada del buck en F.Cu |
| `VA_compuertas_Vgs` | VA contra HGATE/DGATE: 0.2 mm | Solo hay Vgs (≤ 15 V) |
| `PROT_llegada_U101` | Dentro del courtyard de U101: 0.2 mm y 0.25 mm de pista | VQFN-24 de 0.5 mm |
| `PROT_llegada_U201` | +VPROT puede bajar a 0.6 mm dentro de U201, C202 o `ZONA_BUCK_U201` | Ancho del pin VIN |
| `J401_land_pattern_oficial` | NPTH-cobre de ≥ 0.19 mm dentro de J401 | Huella oficial GCT, aceptada por el usuario |

**Antena:** el keep-out viene en la huella de U401 (rule area de 48 × 21 mm, todas las capas, en x 191.94–212.94, y 91.50–139.50). Lo verifica el DRC nativo.

### Rule areas de la placa
| Nombre | Capas | Restringe | Coordenadas (mm, KiCad) |
|---|---|---|---|
| `BARRERA_CAN` | F + B | sin pistas, vías, pads ni rellenos (huellas sí) | Banda en "C" de 2.5 mm: polígono (99.5,110.37) (131.4,110.37) (131.4,140) (99.5,140) (99.5,137.5) (124.6,137.5) (124.6,112.87) (99.5,112.87). El tramo vertical x 124.6–131.4 pasa bajo el cuerpo de U601 |
| `APOYO_CAJA_B` | B.Cu | sin pistas, vías, pads ni huellas (relleno sí) | Círculo de Ø8 mm con centro en (163.5, 99.0) |
| `ZONA_U101` | F + B | ninguna (solo nombre para `PROT_zona_U101`) | x 113.8–134.4, y 64.2–84.4 |
| `ZONA_BUCK_U201` | F + B | ninguna (solo nombre para `PROT_zona_buck_U201` y `PROT_llegada_U201`) | x 124.0–151.0, y 52.0–69.0 |
| keep-out de antena (huella de U401) | todas | todo | x 191.94–212.94, y 91.50–139.50 |

---

## 3. Cambios de ubicación respecto de `placement-v1`
Todos autorizados por el usuario. Aplicados por los scripts de las etapas 1–3; los movimientos MCU están en `scripts/ruteo/etapa3_mcu.py`.

| Pieza | placement-v1 | Ahora | Motivo |
|---|---|---|---|
| C104 (47 µF, VOUT) | F.Cu (138.5, 75.57) r-90 | **B.Cu** (106.85, 71.0) r0, pad 1 al oeste | En F.Cu no tenía camino a VOUT; ahora queda bajo C105/L101.1. Agrega 10.5 mm de altura abajo: separadores de ≥ 12 mm y adhesivo (requisitos de la caja) |
| U301 | (140.4, 135.81) r90 | (140.4, 135.81) **r270** (girado 180°) | SW sale hacia L301 sin cruzar VIN/EN/FB |
| C302 | (139.2, 139.5) r90 | (138.1, 135.875) r270 | Pegado al pin 3 (VIN) de U301 |
| TP101 (+VPROT, B.Cu) | (138.5, 65.5) | (127.6, 61.5) | Sobre el ramal de +VPROT hacia C202 |
| Referencia de U301 | — | serigrafía en (142.2, 132.8) | Al girar la pieza quedaba sobre R301 |
| TP301 (Codex, etapa 2 parcial) | B.Cu (140.0, 134.0) | B.Cu **(140.0, 131.6)**, r180 | Traslado autorizado al tronco +5V; retirada su bajada B.Cu bajo SW. Aplicado por `scripts/ruteo/etapa2_can.py` |
| C401 (Codex, etapa 3) | F.Cu (189.263603, 100.013603) r0 | F.Cu **(189.2, 100.6) r90** | Bulk detrás de C402 en la cadena de 3V3; movimiento autorizado |
| C402 (Codex, etapa 3) | F.Cu (189.9, 104.2) r0 | F.Cu **(189.18, 104.0) r90** | Primero junto a U401.2; pista entre bordes de 0.775 mm |
| R401 (Codex, etapa 3) | F.Cu (162.060355, 146.485355) r90 | F.Cu **(187.0, 100.1) r270** | Pull-up EN local; pista a U401.3 de 4.964 mm entre bordes |

C404 es un componente nuevo autorizado: F.Cu **(189.6,81.45) r0**. No pertenece a `placement-v1`. También se reubicaron las referencias de C401/C402/R401/C403/C404 y el texto «SIN BARNIZ» de J401 a (192,88), r0, para evitar solapes; C403 conserva su posición y orientación.

**Regla:** no mover ni rotar ningún otro componente sin preguntar al usuario. Si un ruteo lo necesita, anotar la propuesta en `docs/RUTEO_AGENTE.md` y esperar la decisión. El usuario replica los cambios en su copia manual.

---

## 4. Restricciones físicas (todas las etapas)
- **Barrera CAN:** ningún cobre cruza `BARRERA_CAN`, salvo los pads de U601 sobre su cuerpo. El dominio CAN (J1.3–5, D601, R602/R603/C609, R605, C607/C608, C610/C606, FB601, FB602) queda a la izquierda/abajo de la banda. GND_CAN propio, sin unirlo nunca a GND_VEH. Separación ≥ 2.5 mm (`ISO_CAN_barrera`).
- **Antena del ESP32-S3:** nada de cobre en el keep-out de la huella (x ≥ 191.94, y 91.5–139.5). La placa tiene un recorte allí.
- **Sensores:** **sin pistas ni vías bajo U501** (crt 154.96–163.65 × 99.45–106.54), **U502** (165.50–169.09 × 93.45–96.55) **ni U503** (146.10–153.90 × 97.20–102.80), en ninguna capa. El plano GND sí puede pasar por debajo.
- **Imán de ROT:** círculo libre de Ø17.9 mm con centro en el eje de U503 (150.0, 100.0), **en las dos caras**. Adentro solo U503 y sus pasivos: sin tornillería, sin H5 y sin el área B. El lado del imán todavía no está decidido.
- **Fijaciones H1 (105,55), H2 (195,55), H3 (105,145), H4 (195,145), H5 (156,88.5):** M3, anillo de 6.4 mm sin red. Pistas y vías a ≥ 4 mm del centro (`H_zona_arandela`); otro cobre a ≥ 0.5 mm del anillo.
- **Área B (`APOYO_CAJA_B`):** Ø8 mm en (163.5, 99.0), en B.Cu. Sin pistas, vías ni pads; el relleno de GND sí puede pasar.
- **Potencia y DO lejos de U503:** nada de potencia (+5V, VBAT/VIN, buck) ni DO a menos de 10 mm de U503.
  - Decisión del usuario (2026-10-29): medir los 10 mm desde el borde del cuerpo. Se acepta como única excepción el tronco existente de +5V (x 137.6), a 9.8 mm del cuerpo.
- **Conformal coating:** sí. Enmascarar J1, J2, J401 y J402 (zonas en `User.Comments`). Hay rótulos "SIN BARNIZ" en la serigrafía.
- **Fabricación:** JLCPCB, 2 capas, 1.6 mm, 1 oz. El prototipo se arma en la variante CAN + DO + ROT. El usuario suelda el ASM330 (LGA) con aire caliente y stencil, así que hay que pedir el stencil.

---

## 5. Plan de las etapas 2 a 6

### Etapa 2 — CAN
- **Bus (lado aislado, F.Cu):**
  - BUS_CAN_H/L: J1.3/J1.4 → D601 (DNP, huella reservada) → R602/R603 (terminación partida) y C609 → U601, pines 14 (H) y 13 (L).
  - Par acoplado a mano, 0.3/0.3, con aperturas en pads y ajuste local de longitud. Excepción autorizada al cerrar la etapa 2: dos vías en CANH y puente recto B.Cu de 3.844 mm; CANL queda en F.Cu. Diferencia de longitud principal J1→U601 ≤1 mm incluyendo altura de vías, conforme al ajuste existente del proyecto.
  - Hay 3 segmentos de CAN_H/L en F.Cu que dejó el usuario antes de la etapa 0: conservarlos o rehacerlos.
- **Fuente aislada:**
  - V_SOOUT (pin 19) → C610 (220 nF) y C606 (10 µF) → FB601 → V_SOIN (pin 16) con C607 (10 nF) y C608 (100 nF).
  - GNDISO_CAN (pines 18/20) → FB602 → GND_CAN.
  - CAN_RS (pin 12) → R605 (0 Ω) → GND_CAN.
  - **Criterio de ruteo aprobado por el usuario (2026-10-29):** ≤ 2 mm de pista entre el pin y C601, C604, C607 y C610; **C608 a 2.145 mm aceptado como excepción** (límite 2.15 mm). C602/C603 (ubicados a ~4.7 mm) y C606 (~2.9 mm) se aceptan en cadena detrás del capacitor pequeño: pin → pequeño → grande, sin camino independiente desde el pin al grande. No mover estas piezas. Cada capacitor tendrá retorno corto a su propia red de masa.
  - **Valores y masas que se conservan del diseño:** C602 es de 100 nF (no 10 µF); C603, C605 y C606 son de 10 µF. C601–C605 retornan a GND_VEH, C607/C608 a GND_CAN y C606/C610 a GNDISO_CAN, antes de FB602. No unir directamente GNDISO_CAN con GND_CAN puenteando la ferrita.
- **Lado lógico:**
  - +5V (VCC, pin 3) → C604 (100 nF, a 1.1 mm) → C603 (10 µF). Sale del tronco de +5V en y 124.8: de (143.5, 124.8) hacia el oeste, a C603.1 / C604.1 por debajo.
  - +3V3_D (VIO, pin 4) → C601 (10 nF, a 1.1 mm) → C602 → C605. Llega desde la salida de U301 o desde el riel de 3V3 que se tienda en la etapa 3.
  - GND en los pines 1, 2, 9 y 10 con vías propias.
- **Señales a la MCU:**
  - CAN_TX (pin 7 → U401.24), CAN_RX (pin 5 → U401.25), CAN_STBY (pin 8 → U401.23, con pull-up R604) y CAN_SILENT (pin 6 → U401.35, con pull-down R601). TP404 = CAN_TX y TP405 = CAN_RX, en B.Cu.
  - **Salto reservado:** las cuatro cruzan el tronco de +5V (vertical en x 147.3, entre y 110.6 y 124.8). Pasan por B.Cu en ese cruce, con 2 vías cada una y tramos cortos. No mover el tronco.
- **Islas:** GND_CAN en las dos caras se hace en la etapa 5. Acá alcanza con dejar las vías de GND_CAN.
- **Aceptación:**
  - DRC 0 errores. Ningún cobre en `BARRERA_CAN`.
  - Par CAN acoplado de punta a punta, con diferencia de largo de ≤ 1 mm.
  - C601/C604/C607/C610 a ≤ 2 mm de pista al pin; C608 ≤2.15 mm por excepción aprobada; C602/C603/C606 en cadena conforme al criterio aprobado, con retornos cortos. Entregar tabla de distancias reales y diferencia de longitud CANH/CANL.
  - Las 4 señales completas hasta U401. Render de las dos caras.

### Etapa 3 — USB / MCU
- **USB_D+/D-:** J401 (A6/B6, A7/B7) → U402 (ESD) → U401. Par principal 0.3/0.2, **sin vías**, diferencia ≤0.5 mm; excepciones aprobadas: cuatro vías solo en ramales B6/B7 y cuello D− de 0.15 mm × 1.923 mm junto a U401.
- **J401:** VBUS → U402/C404/TP403; CC1/CC2 → R403/R404 a GND. SBU sin conectar.
- **ESP32-S3:**
  - +3V3_D a los pines 2 y otros VDD con C401 (22 µF) y C402 (100 nF) directo al pin.
  - EN (MCU_RST_N) corto, con C403 (a 1.3 mm del pin EN) y la red de U801 (RESET por R802).
  - BOOT (SW402), SW401 (reset).
  - U0TXD/U0RXD → J402 (header UART0).
  - Las VAR_ID (R805/R806/R807), los LED (D801/D802 con R803/R804) y WDI de U801 se pueden dejar para la etapa 4.
- **Riel +3V3_D:** de la salida de U301 (C304.1, en 151.0, 142.5) hasta la MCU (U401.2 en 189.18, 106.75) y hasta U601 (VIO). Usar 0.4–0.6 mm y evitar la zona de sensores.
- **Aceptación:**
  - DRC 0 errores. USB sin vías y acoplado.
  - C402 y C404 a ≤1 mm entre bordes de pads; C401 en cadena detrás de C402. RC local EN a ≤5 mm entre bordes; RESET remoto se mide aparte.
  - Nada en el keep-out de antena.

### Etapa 4 — Sensores y señales (no iniciada)

Plan completo, inventario de las 108 conexiones no-GND, saltos reservados y criterios de aceptación en «Cómo retomar», al inicio de este documento. Ese plan reemplaza las referencias antiguas a PG_3V3D→MCU y C503 como desacople de ROT.

### Etapa 5 — Planos
- **B.Cu:** relleno GND_VEH en toda la placa, salvo la isla CAN, la isla RTN de U101 (la regla ya la aísla) y el keep-out de antena. Prioridad baja; el área B admite relleno.
  - Debe quedar continuo bajo el buck y bajo los sensores.
  - Bajo `ZONA_U101` va a quedar en islas por los saltos: coserlas con vías.
- **F.Cu:** relleno GND_VEH donde haya lugar.
- **Isla GND_CAN** en las dos caras dentro del dominio CAN, cosida, sin relleno bajo U601 (`ISO_sin_relleno_bajo_U601`).
- **Costura:** cada 5–10 mm, alrededor del ESP32 (fuera del keep-out de antena) y en el borde de la isla CAN, del lado CAN.
- **C605 (VIO, bulk):** su camino al pin 4 es de 12.270 mm. Asegurar continuidad de GND_VEH entre su vía en (144.28,121.9), C602/C601 y los retornos de U601, y añadir costura local. Revisar que los saltos de las cuatro señales lógicas no dejen ese retorno en una isla o cuello estrecho.
- **Puente CANH de la etapa 2:** B.Cu recto entre (114.45,115.75) y (118.2,116.595), 3.844 mm, con dos vías. Conservar GND_CAN conectado alrededor de ambos extremos y añadir costura sin invadir la barrera. El pad 3 de D601 tiene retorno corto a la vía GND_CAN (115.4375,117.25).
- **Conexión a pads:** alivios térmicos en los pads (soldadura a mano). Conexión sólida en los pads expuestos (U201 EP y vías del EP).
- **Las 19 vías GND sueltas de la etapa 1 tienen que quedar conectadas al plano:** C101, D102, D103, C103, C106, C107, R203, C204–C206, U301 pin 1, C302, C301, C304, R304, U302 pin 2, C306 y C307.
- **Aceptación:**
  - DRC 0 errores, sin `via_dangling` ni islas sin conectar (`isolated_copper`).
  - GND_VEH sin unir a GND_CAN ni a U101_RTN. Rellenos recalculados.

### Etapa 6 — Cierre
- DRC y paridad en 0. Revisar retornos de corriente: buck, U301, CAN e islas bajo U101.
- **Teardrops:** generarlos (Edit → Edit Teardrops, o por la API) y repetir el DRC.
- **Fabricación de prueba para JLCPCB en `fab/`:** Gerbers, drill, BOM y CPL con kicad-cli (`pcb export gerbers`, `pcb export drill`, `pcb export pos`, `sch export bom`).
  - La BOM sale del campo `DNP` y la variante de prototipo es CAN + DO + ROT.
  - Incluir el stencil.
- **Aceptación:** DRC 0 / paridad 0 / ERC sin cambios. Los archivos de `fab/` se generan sin errores. Renders finales.

---

## 6. Compromisos ya aceptados (no "arreglar" sin preguntar)
- **Zona U101:** ~11 vías y tramos cortos en B.Cu (aceptado). El plano bajo U101 va a quedar en islas cosidas.
- **C201 (4.7 µF):** llega a VIN por la diagonal y el pad de C202 (8.6 mm), porque el retorno directo de C202 ocupa el paso por el oeste del pin 1.
  - Lazo de C202: 3.9 mm² (antes 6.1). Lazo de C201: 26.4 mm² (antes 31.3).
- **U301:** el GND del pin 1 y el de C302 bajan al plano por vías propias. El lazo de entrada mide ~5 mm² (antes 6.1, con VIN cruzando por B.Cu).
- **TP301** (+5V, B.Cu): traslado autorizado y aplicado en la etapa 2 de (140,134) a (140,131.6), fuera de la proyección del SW de U301 y sobre el tronco +5V. Retirada la bajada anterior; registrar el plano continuo bajo SW en la etapa 5.
- **Gates:** HGATE mide ~17 mm y DGATE ~25 mm por la ubicación de U101, pero cada uno va paralelo a su retorno (VA).

---

## 7. Trampas conocidas
1. **pcbnew sobrescribe el `.kicad_pro`.** `LoadBoard()` de un PCB fuera de la carpeta del proyecto, seguido de `Save()` dentro del proyecto, reemplaza `INCLI-VA.kicad_pro` con valores por defecto: se pierden net classes y patrones.
   - Cargar siempre `INCLI-VA.kicad_pcb` del proyecto. Para experimentar con una versión anterior, usar una copia aislada del proyecto completo (PCB, .pro y .dru compatibles). Nunca restaurar una placa antigua sobre el trabajo actual para verificarlo.
2. **Una regla de clearance sin condición** en la `.kicad_dru` anula todas las clearances de las net classes. El piso de fabricación va en Board Setup.
3. **Expresiones DRC en KiCad 10:**
   - Funcionan `A.NetClass == 'PROT'`, `A.Width <= 0.3mm`, `A.insideArea('NOMBRE')` y `A.Parent == B.Parent`.
   - `A.Track_Width` no coincide con nada.
   - Si `A.NetClass` "no funciona", seguramente se perdió el `.kicad_pro` (trampa 1).
4. **Antes de cada commit:** `git diff INCLI-VA.kicad_pro`. KiCad reordena las net classes alfabéticamente, y eso es inofensivo. Cualquier otro cambio hay que revisarlo.
5. **KiCad cerrado** (sin `~INCLI-VA.kicad_pro.lck` ni editores abiertos) antes de editar archivos con scripts. Si estaba abierto, que el usuario recargue.
6. La última regla que coincide manda: las excepciones van **después** de las reglas generales en la `.kicad_dru`.
7. `kicad-cli pcb drc` reescribe a veces el `.kicad_pro` (orden de clases). Ver la trampa 4.

---

## 8. Cómo verificar
```bash
cd PCB_INCLI_VA        # carpeta del proyecto, rama ruteo-agente
# Verificar el PCB actual, sin ejecutar generadores de ruteo:
/usr/bin/python3 scripts/ruteo/verify_etapa3.py
# DRC + paridad (JSON):
kicad-cli pcb drc --schematic-parity --severity-all --format json -o output/drc_report.json INCLI-VA.kicad_pcb
# ERC:
kicad-cli sch erc --severity-all --format json -o output/erc_report.json INCLI-VA.kicad_sch
# Renders:
kicad-cli pcb render --side top    --width 1600 --height 1600 --quality basic -o docs/layout/ruteo/etapaN-top.png    INCLI-VA.kicad_pcb
kicad-cli pcb render --side bottom --width 1600 --height 1600 --quality basic -o docs/layout/ruteo/etapaN-bottom.png INCLI-VA.kicad_pcb
# Vista ampliada de una zona: el PDF tiene el mismo origen que KiCad, así que 1 mm = DPI/25.4 px.
kicad-cli pcb export pdf --layers F.Cu,B.Cu,F.Fab,Edge.Cuts --mode-single -o /tmp/v.pdf INCLI-VA.kicad_pcb
# zona x0..x1, y0..y1 (mm) a 600 dpi: -x = x0*600/25.4, -y = y0*600/25.4, -W = (x1-x0)*600/25.4, -H = (y1-y0)*600/25.4
pdftoppm -png -r 600 -x 2976 -y 1488 -W 850 -H 520 -singlefile /tmp/v.pdf zona   # ejemplo: x 126-162, y 63-85
```
- En el JSON del DRC: `violations` (filtrar `severity == "error"`), `unconnected_items` y `schematic_parity`.
- Script de la etapa 1: `scripts/ruteo/etapa1_potencia.py`. Funciones `T(red, ancho, puntos, capa)` y `V(red, x, y)`, y aplica los cambios de ubicación de la sección 3. Se puede usar de modelo para las etapas siguientes: un script por etapa que parta del commit de la etapa anterior.
- Historial y detalles por etapa: `docs/RUTEO_AGENTE.md`. Estado general: `docs/PENDIENTES.md`.

---

## 9. Decisiones registradas y pendientes (2026-10-29)
1. **U503:** 10 mm desde el borde del cuerpo; excepción aceptada del tronco +5V existente a 9.8 mm.
2. **Imán ROT:** lado sin definir; mantener libre el círculo de Ø17.9 mm en ambas caras, salvo U503 y sus pasivos previstos.
3. **C105 PROD (EEE-FK1H102AV):** confirmar stock en la revisión del BOM; no bloquea el ruteo. La huella J16 antivibración ya acepta EEE-FK1H102AM.
4. **TP301:** traslado ya aplicado y registrado en Cambios de ubicación; asegurar plano continuo bajo SW en etapa 5.
5. **Terminación CAN:** R602/R603/C609 montadas en PROTO; en PROD se definen según instalación.
6. **Desacoples de U601:** criterio y conexiones en cadena aprobados en la sección 5, etapa 2. No cambiar ubicación, valores ni redes.
7. **Alcance al entregar:** etapa 3 cerrada y verificada con todas sus excepciones autorizadas. Esperar nuevo visto bueno antes de etapa 4; no se inició.
8. Cualquier otro movimiento o giro de componentes, cambio de reglas o net classes, renombre de redes o edición del esquemático requiere consulta previa.
9. Los MPN marcados "a verificar" en `docs/PENDIENTES.md` se revisan antes de generar la BOM final.

### Hallazgos de la etapa 2 — resueltos por el usuario
- **C608:** excepción aceptada a 2.145 mm. Es el mínimo geométrico con los pads redondeados actuales; los ~1.99 mm del traspaso ignoraban esas esquinas. Ubicación conservada.
- **D601:** evaluado el giro de 180° sin cambiar redes. H/L pasan a coincidir con U601, pero quedan invertidos respecto de J1 y el pad GND pasa al acceso desde J1. El giro no elimina la inversión del recorrido completo; se conserva r0 y se aplica la alternativa autorizada del puente CANH con dos vías.
- **CAN:** 22.2139 mm H / 22.2120 mm L; diferencia nominal **0.0019 mm**, entre centros de J1.3/4 y U601.14/13, incluyendo 1.6 mm por vía. Las longitudes planares son 19.0139 / 22.2120 mm; el ajuste compensa los 3.2 mm verticales de H. Ramales a terminación separados de esta métrica.
- **Cierre:** DRC 0 errores / 42 avisos (37 vías GND esperan planos + 5 conocidos), paridad 0, 254 conexiones pendientes. Renders de ambas caras y medidas finales en `docs/layout/ruteo/etapa2-*`. Esperar visto bueno antes de etapa 3.


### Auditoría adicional B.Cu CAN — etapa 2 aprobada

El usuario pidió listar los tramos inferiores y comprobar que no fragmenten la futura isla. Se ejecutó `scripts/ruteo/audit_can_bcu.py`: copia temporal de PCB, reglas y proyecto; relleno **solo B.Cu**, clearance y espesor mínimo 0.2 mm, alivios de 0.3 mm, sin eliminar islas. La prueba conserva libre el courtyard completo de U601 y `BARRERA_CAN`, conforme a las reglas vigentes. **No hay cobre bajo el cuerpo aislante de U601**: la continuidad comprobada llega a sus retornos del lado CAN por las pistas cortas existentes. Se pidió confirmar esta interpretación de «bajo U601»; no se modificó la regla.

Resultado: **1 región rellena**, las **8 vías GND_CAN dentro de ella**, **0 conexiones GND_CAN pendientes** y **DRC 0 errores** en la copia temporal. J1.5 queda unido a los retornos de U601.11/15, D601, R605, C607/C608, C609 y FB602. Ninguno de los tramos divide la isla; no se traslada ni acorta ninguno. Hay paso de retorno alrededor del puente CANH y por debajo de los extremos de GNDISO_CAN/V_SOIN. Repetir la prueba al crear los planos definitivos de etapa 5 y añadir la costura prevista. Esto comprueba la continuidad del cobre, no una simulación de impedancia o EMC.

Evidencia: `docs/layout/ruteo/can-bcu-auditoria.json` y `can-bcu-auditoria.png`. Las coordenadas siguientes son absolutas KiCad, en mm. Longitudes planares; no incluyen altura de vías.

| Red | Total B.Cu (mm) |
|---|---:|
| BUS_CAN_H | 3.8440 |
| V_SOIN | 13.5902 |
| GNDISO_CAN | 16.3134 |
| Net-(C609-Pad1), punto medio de terminación | 6.7238 |

| Red | Inicio (x, y) | Fin (x, y) | Longitud (mm) |
|---|---|---|---:|
| /60_can/GNDISO_CAN | (117.8, 128.85) | (117.8, 132.7) | 3.8500 |
| /60_can/GNDISO_CAN | (118.55, 125.325) | (118.55, 128.1) | 2.7750 |
| /60_can/GNDISO_CAN | (118.55, 128.1) | (117.8, 128.85) | 1.0607 |
| /60_can/GNDISO_CAN | (118.725, 123.575) | (118.725, 125.15) | 1.5750 |
| /60_can/GNDISO_CAN | (118.725, 125.15) | (118.55, 125.325) | 0.2475 |
| /60_can/GNDISO_CAN | (119.8, 122.5) | (118.725, 123.575) | 1.5203 |
| /60_can/GNDISO_CAN | (121.325, 122.5) | (119.8, 122.5) | 1.5250 |
| /60_can/GNDISO_CAN | (121.65, 122.4) | (121.325, 122.5) | 0.3400 |
| /60_can/GNDISO_CAN | (121.65, 125.15) | (118.725, 125.15) | 2.9250 |
| /60_can/GNDISO_CAN | (122, 125.5) | (121.65, 125.15) | 0.4950 |
| /60_can/V_SOIN | (121.2, 131.0125) | (123.5, 128.7125) | 3.2527 |
| /60_can/V_SOIN | (123.5, 121.6) | (120.275, 121.6) | 3.2250 |
| /60_can/V_SOIN | (123.5, 128.7125) | (123.5, 121.6) | 7.1125 |
| /BUS_CAN_H | (114.45, 115.75) | (118.2, 116.595) | 3.8440 |
| Net-(C609-Pad1) | (116.5, 122.325) | (116.5, 127.175) | 4.8500 |
| Net-(C609-Pad1) | (116.5, 127.175) | (115.175, 128.5) | 1.8738 |

### Etapa 3 — primer avance y decisiones solicitadas (histórico: 4bfdfef)

Sin movimientos de componentes ni cambios de esquema. KiCad sin archivos de bloqueo antes de editar. Se han ruteado UART J402, BOOT con R402/SW402/TP402, EN local con C403 y TP401, RESET hasta SW401 y U801/R802, alimentación de C605/U601 desde C304, y alimentación/desacople de U801 y pull-up de BOOT. U401 ya incorpora 12 taladros metalizados GND de 0.2 mm en el pad 41; se conservan. Retornos de U401.1/40 y pasivos preparados para el plano de etapa 5. GPIO3/45/46 permanecen NC según la hoja 40; GPIO0 usa R402/SW402.

Solicitudes de aquel avance, posteriormente resueltas y aplicadas (histórico):
- C402 tiene separación geométrica mínima de **1.325 mm** al pin 3V3, frente al ≤1 mm del plan. C401 está a más de 6 mm del pin y R401 a unos 49 mm de EN. Se solicitó acercar C401/C402 y trasladar R401 junto a C403, o conservar posiciones con excepciones documentadas. Registrar coordenadas definitivas en «Cambios de ubicación» si se autorizan.
- VBUS no tiene capacitor en el esquema: solo J401, U402 y TP403. Se solicitó autorización para añadir 100 nF/50 V, 0603, con MPN ya presente, o conservar el esquema sin ese desacople. No se ha añadido componente ni cambiado la conectividad.
- En J401 las patillas son D+/D−/D+/D−. Se propuso una excepción de cuatro vías solo en los dos ramales B6/B7, conservando el par principal en F.Cu; la geometría completa y el ajuste de longitud deben verificarse antes de dar por viable o cerrar USB. No se ha aplicado la excepción ni ruteado USB.

Verificación parcial: **DRC 0 errores, paridad 0, 240 conexiones pendientes**. 49 avisos: 44 vías GND para etapa 5 y los 5 avisos conocidos. EN U401.3→C403.1: **2.8519 mm entre centros / 1.5415 mm entre bordes**, sin vías. La red remota RESET mide más: U401→SW401 **62.8093 mm** y U401→R802 **55.4803 mm**, incluyendo dos vías; el criterio EN ≤5 mm se cumple solo para el RC local, no para estos ramales impuestos por la ubicación de los controles. R401 sigue pendiente. USB y distancias finales de C401/C402 aún no son evaluables porque falta el ruteo. Evidencia parcial en `docs/layout/ruteo/etapa3-parcial-*`.


### Etapa 3 — cierre final, decisiones aplicadas y medidas

**Aplicado con autorización del usuario:**
- Reubicación C401/C402 y R401 en «Cambios de ubicación». Alimentación desde C304 al MCU, en cadena pin → C402 → C401, sin derivación independiente al pin. Cada capacitor tiene vía de retorno GND; el pad 41 de U401 conserva sus 12 taladros metalizados. R401 llega al nodo EN por el este de C403, sin cruzar su pad GND.
- **C404 nuevo en hoja 40:** 100 nF, 0603, X7R, 50 V; MPN `GCM188R71H104KA57D`, Manufacturer `Murata`, Footprint `Capacitor_SMD:C_0603_1608Metric`, Datasheet `https://www.murata.com/en-global/products/productdetail?partno=GCM188R71H104KA57D`, campo DNP vacío y atributo nativo `dnp no`. VBUS-GND_VEH; no alimenta +5V. Es el mismo componente de C402. Especificaciones contrastadas con la [ficha oficial Murata](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GCM188R71H104KA57-01.pdf).
- C404 se incorporó al PCB con UUID propio y vínculo a su símbolo; **paridad 0, no hizo falta F8**. `scripts/ruteo/add_c404.py` reproduce la incorporación. Cambio de esquema posterior a placement-v1, a replicar por el usuario en ruteo-manual; no se tocó esa copia.
- USB principal F.Cu, 0.3/0.2 mm en los tramos acoplados, aperturas en pads y ajuste local de D+. Solo los ramales B6/B7 tienen vías: 2 por red, 4 en total, Ø0.6/taladro 0.3. Ubicaciones: D+ (192.2,79.37) y (190.0,82.5); D− (192.4,81.425) y (190.4,79.6). Los ramales permanecen junto a J401. Ramal B6 hasta su unión al principal: 6.7478 mm planares +3.2 mm verticales; B7: 8.2262 +3.2 mm. No se incluyen esos ramales en la longitud del recorrido principal.
- CC1/CC2 cortos en F.Cu, sin vías; VBUS conectado a ambos grupos de contactos, U402, C404 y TP403. Retornos cortos de U402/C404, CC y J401 preparados para los planos.
- UART, BOOT, RESET y estrapado según hoja 40; GPIO3/45/46 conservados NC. Nada en el keep-out de antena. No se modificaron reglas ni net classes.

**Excepción aprobada y aplicada al PCB guardado:** cuello D− de **0.15 mm × 1.922754 mm** (1.923 mm redondeado), F.Cu, entre (173.0,107.5) → (173.2825,107.7825) → (173.6,107.7825) → (174.8,107.9). Mantiene clearance ≥0.2 mm y el recorrido principal sin vías. La aprobación no reduce el ancho del resto del USB ni cambia las reglas. Se añadieron únicamente esos tres segmentos al grupo CODEX_ETAPA3; ninguna pieza se movió en este cierre. `preview_usb_escape.py` y los archivos `etapa3-propuesta-*` son históricos; el script ya evita duplicar el cuello si está presente.

| Medición | Centro a centro (mm) | Pista entre bordes (mm) | Estado |
|---|---:|---:|---|
| USB D−, J401.A7 → U402 → U401.13 | 45.9509 | 44.6256 | PCB guardado, sin vías |
| USB D+, J401.A6 → U402 → U401.14 | 45.9508 | 44.6258 | PCB guardado |
| Diferencia D± | **0.0001** | — | PCB guardado; sin vías principales |
| EN → C403 | 2.8519 | 1.5415 | PCB guardado, sin vías |
| EN → R401 | 6.2433 | 4.9641 | PCB guardado, sin vías; ≤5 mm de pista entre bordes |
| RESET → SW401 | 62.8093 | 61.1900 | Ramal remoto, incluye dos vías |
| RESET → R802 | 55.4803 | 54.2548 | Ramal remoto, incluye dos vías |
| U401.2 → C402, 100 nF | 1.9750 | **0.7750** | Primero, sin vías |
| U401.2 → C401, 22 µF | 7.0585 | 5.6027 | En cadena detrás de C402, sin vías |
| U402.5 → C404, 100 nF | 1.6875 | **0.5748** | Sin vías |
| U801.5 → C801, 100 nF | 2.4946 | 1.3815 | Sin vías |

Medidas finales extraídas del PCB guardado mediante `verify_etapa3.py`, que también comprueba CAN. `etapa3-medidas.json` contiene `USB_final`, sin sustitución por una copia temporal. Centro a centro incluye 1.6 mm por vía cuando corresponde; pista entre bordes descuenta la parte dentro de los pads. B6/B7 se informan aparte del USB principal. Estas son longitudes nominales de la geometría CAD, no tolerancias de fabricación.

**Verificación final:** DRC **0 errores /57 avisos**: 52 `via_dangling` de masas para etapa 5 y 5 conocidos (2 `silk_overlap`, 2 `silk_edge_clearance`, 1 `lib_footprint_mismatch`). Ya no hay `track_dangling` del escape USB. Paridad **0**. **223 conexiones pendientes**: 108 no-GND de etapa 4, 107 GND_VEH y 8 GND_CAN de etapa 5. Inventario completo en `etapa3-pendientes.json`. ERC total **0 errores /5 avisos conocidos**: 1 `isolated_pin_label` de U101_RTN y 4 `pin_to_pin` de SW401/SW402; hoja 40: 0 errores /4 avisos. No cambió el esquema durante este cierre.

Evidencia final en `docs/layout/ruteo/etapa3-drc.json`, `etapa3-erc.json`, `etapa3-medidas.json`, `etapa3-top.png` y `etapa3-bottom.png`; ambas caras revisadas visualmente. QA del cambio C404 previamente realizada sobre `etapa3-hoja40.png` y `etapa3-c404-esquema.png`; `sch_visual_qa` no estaba disponible, se utilizó exportación KiCad y revisión visual. Los archivos `etapa3-parcial-*` y `etapa3-propuesta-*` conservan solo el historial.

**Etapa 3 cerrada. Etapa 4 no iniciada: esperar el visto bueno del usuario.**
