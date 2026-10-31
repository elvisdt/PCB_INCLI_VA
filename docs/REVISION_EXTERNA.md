# INCLI-VA — Revisión externa de hardware (`pcb-v1-rc5`)

Revisor: Claude Code (revisión independiente, solo informe). Fecha: 2026-10-30.
Base revisada: `main` en `d0d5f7c`. `git diff --stat pcb-v1-rc5 HEAD` solo muestra cambios en `docs/PENDIENTES.md`: el esquemático, el PCB, las reglas y `fab/` son los del tag. No se modificó ningún archivo del proyecto; este informe es el único archivo nuevo.

**Método**
- ERC y DRC con `kicad-cli` 10.0.7: ERC 0 errores / 5 avisos (los 5 conocidos: SW401/SW402 «Unspecified–Passive/Power» y la etiqueta `U101_RTN`). DRC con paridad: 0 errores, 3 avisos (U401 `lib_footprint_mismatch` y 2 `silk_edge_clearance`), 0 sin rutear, 0 problemas de paridad. Coincide con lo que declara `docs/PENDIENTES.md`.
- Netlist exportada (`kicadxml`) y analizada pin por pin; geometría del PCB leída con `pcbnew` (solo lectura, sin guardar); renders por capa (`kicad-cli pcb export pdf` + `pdftoppm`).
- Datasheets: los de `docs/datasheets/` y los de TI descargados de ti.com: LM74930-Q1 (SNOSDF6, oct. 2023), LMR38010-Q1 (SNVSC72B), TPS62A02-Q1 (SLUSFG7), TPS3828, LP5907-Q1 y SN74AHCT1G126.
- kicad-happy no está instalada en esta sesión; `sch_visual_qa` tampoco se usó. Las cifras marcadas «calc.» son cálculos propios a partir de los datasheets, no mediciones.

---

## A. Resumen ejecutivo

**¿Se puede fabricar el prototipo así?** El **PCB sí**. Pasa el DRC con las capacidades de JLCPCB (2 capas, 1.6 mm, 1 oz, ENIG), los Gerbers y el stencil son coherentes, y la geometría (planos, barrera CAN, recorte bajo la antena, HV) está bien resuelta para un prototipo. **La placa armada, en cambio, no va a arrancar tal como está dibujada**: hay un error de esquemático en la protección de entrada que se arregla con un retrabajo pequeño en el prototipo. No hace falta otro PCB para el prototipo, pero sí corregirlo en la rev. B.

**Riesgos principales (por orden):**
1. **[R-01, bloqueante funcional] El LM74930 no puede encender Q101.** El divisor de UVLO (R106/R107) toma la tensión del pin SW, que internamente es el nodo A = VA (fuente común de Q101/Q102). Al conectar la batería, VA está a 0 V: los diodos de cuerpo de Q101 y Q102 apuntan hacia afuera de VA, así que nada lo carga. UVLO queda en 0 V, por debajo de V(UVLOR), y el LM74930 mantiene HGATE unido a OUT (SNOSDF6 §7.3.2.1): Q101 no conduce nunca. En la Fig. 8-1 de TI, R1 (UVLO) va a **VBAT**. Retrabajo: §B, R-01.
2. **[R-02, importante] VS se alimenta solo a través de R102 = 10 kΩ.** Con IQ = 665 µA típ. / 780 µA máx. (SNOSDF6 §6.5), la caída es de 6.7–7.8 V. Con batería de 12 V, VS queda en ≈ 3.5–4.7 V (calc.): por debajo del mínimo de operación de 4 V en el peor caso, y la bomba de carga se especifica solo con VS ≥ 6 V. La Fig. 8-1 de TI incluye **D1 (85 V) de VA a VS**, que alimenta VS una vez que Q101 conduce; en este diseño falta. En vehículos de 12 V, el arranque con batería baja y el cold crank quedan en riesgo.
3. **[R-04, importante para PROD] Las salidas DO no tienen protección contra cortocircuito.** Con un corto de la carga a +24 V, el DMN10H220L (SOT-23) se destruye en milisegundos, y el firmware no puede reaccionar a tiempo. Ya está documentado como limitación, pero para un producto de mina es un riesgo de campo.
4. **[R-08, importante para la homologación] EMC del ADM3055E:** su isoPower usa una portadora de 180 MHz, dentro de la banda DAB III / TV de CISPR 25 (171–245 MHz). ADI solo declara EN 55022 clase B con placa de 2 capas y ferritas. En 2 capas no se puede hacer la capacidad de costura embebida. Hay que hacer un pre-escaneo pronto.
5. **[R-10, importante] El retorno de los DO cruza toda la placa:** J2 está en el borde superior, a ~80 mm de J1 (único GND externo). La corriente del relé, el pico inductivo de D701/D751 y los pulsos ISO 7637 en las líneas DO vuelven por el plano, por debajo del buck, del MCU y de los sensores.
6. **[R-11, importante para PROD] Térmica y grado del MCU:** el ESP32-S3-WROOM-1-N8R2 no es AEC-Q100 y llega solo a 85 °C. En una caja ABS sobre el chasis, al sol, la temperatura interna puede superar ese valor.
7. Varios márgenes que solo el ensayo confirma: pulso 1 de ISO 7637-2 contra los máximos absolutos C–A (85 V) y OUT–VS (−65 V) del LM74930 (R-03), arranque en PROD con C105 contra el breaker de 1 A (R-06) y amortiguamiento del filtro de entrada (R-07).

**Recomendación:** fabricar el rc5 tal como está (ya está pedido) y aplicar en las placas los retrabajos R-01 (obligatorio) y R-02 (recomendado) **antes de la primera energización**. Hacer el bring-up con fuente limitada en corriente según el plan de §E. La rev. B debe corregir R-01/R-02 en el esquema y abordar R-04, R-08, R-10 y R-11.

---

## B. Tabla de hallazgos

Severidad: **Bloq.** = bloqueante (aquí, funcional: el PCB se puede fabricar, pero la placa no funciona sin el retrabajo) · **Imp.** = importante · **Men.** = menor · **Sug.** = sugerencia.
Coordenadas: PCB en mm (KiCad); la placa ocupa (100, 50)–(200, 150).

| ID | Área | Sev. | Ubicación | Descripción | Evidencia | Acción propuesta |
|---|---|---|---|---|---|---|
| R-01 | Esq. 10 (entrada) | **Bloq.** | R106 (120.4, 72.57), R107 (120.4, 68.52), U101 pin 3 (SW), red `/10_power_input/SW` = {R106.1, U101.3} | El divisor de UVLO sale de SW, que es el nodo A = VA a través del interruptor interno. En la topología common-source con el FET de HGATE a la entrada, VA vale 0 V hasta que Q101 conduce: UVLO = 0 < V(UVLOR) = 0.585 V mín., HGATE queda en OUT y la placa nunca arranca (deadlock). | SNOSDF6 §7.3.2.1 (condiciones para habilitar HGATE: «UVLO pin voltage must be higher than VUVLOR»); tabla 5-1, SW («A and SW are internally connected through a switch»); Fig. 8-1 (R1 de 100 k a **VBAT**, SW sin conectar). Netlist: Q101 D = VBAT_F, S = VA; Q102 S = VA, D = C_ID; los dos diodos de cuerpo bloquean la entrada a VA. | **Prototipo (opción preferida):** retirar R106 y soldar 100 kΩ (THT de 1/4 W o 1206, ≥ 200 V) entre el pad de R106 del lado UVLO (pin 2, unido a R107.1) y VBAT_F (pad 1 de R108, C101.1 o TP102 en la cara inferior, (122, 97)). Así se conservan los umbrales de diseño: 6.46 V de caída y 7.04 V de subida, sobre VBAT_F. **Opción rápida sin UVLO:** retirar R106 **y** R107 y puentear UVLO (R107.1) a VS (C102.1, a ~5 mm). **Rev. B:** R1 desde VBAT_F con 2 × 1206 en serie (como R108/R112), SW sin conectar. Verificarlo en el bring-up midiendo UVLO, HGATE–VA y FLT. |
| R-02 | Esq. 10 | **Imp.** | R102 (125.9, 92.5), D104 (131.0, 86.35), C102 (125.2, 65.6), red VS | VS solo se alimenta por R102 = 10 kΩ y D104. Calc.: VS = VBAT − IQ·10 k − VF(D104) → con 12 V, 4.7 V típ. / 3.5 V peor caso; con 9 V, 0.5–1.7 V (por debajo del POR de 2.4–2.9 V); con 13.8 V, 5.3–6.5 V; con 24 V, sin problema. V(VS) mín. = 4 V; I(CAP) se especifica para 6 V ≤ VS. Falta D1 (VA → VS) de la Fig. 8-1. | SNOSDF6 §6.5 (I(Q) 665/780 µA, V(VS) 4–65 V, I(CAP) «6 V ≤ VS»); Fig. 8-1 (D1 85 V de VA a VS); §8.2.1, tabla 8-1 (diseño de ejemplo de 24 V). | **Prototipo:** agregar un diodo de ≥ 100 V (BAS21 o BAV21W) con el ánodo en VA (pata de fuente de Q101 o Q102) y el cátodo en VS (D104 pin 3 o C102.1). Medir VS con 9, 12, 16 y 24 V antes y después del retrabajo. **Rev. B:** huella de D1 según TI. Evaluar bajar R102 a 3.3–4.7 kΩ anti-pulso 2512, que solo es viable si se renuncia a sobrevivir el load dump sin suprimir de 202 V (ver R-25). |
| R-03 | Esq. 10, transitorios | **Imp.** (verificar) | D101, D102, Q101/Q102, U101 | Pulso 1 de ISO 7637-2 (24 V: −600 V / 50 Ω, ~12 A). Calc.: C–A ≈ VOUT (≤ 32 V) + VC(D102 a 12 A, ≈ 45–47 V) + VF(D101, ≈ 1.2 V) + ~0.5 V ≈ 79–81 V, frente a 85 V máx. abs.: unos 4 V de margen. OUT–VS ≈ −48 V − 30 V (VS retenido por C102) ≈ −78 V, frente a **−65 V** máx. abs. La Fig. 8-1 de TI tiene la misma topología y TI muestra el pulso 1 superado (Fig. 8-5), así que el límite probablemente no se alcanza de esa forma, pero no está demostrado. | SNOSDF6 §6.1 (C to A: −5/85 V; OUT to VS: −65/16.5 V); §8.4.3 («clamping voltage of the TVS− must not exceed 85 V − 32 V = 53 V»). SMCJ33A: VC = 53.3 V a 28 A. | Consultar a TI (E2E) sobre OUT–VS durante el pulso 1. En el ensayo, medir A, C, OUT y VS con una sonda diferencial. Si C–A supera ~82 V, cambiar D102 por un TVS− de 28 V (TI recomienda SMBJ28A, VC 45.4 V para 24 V). |
| R-04 | Esq. 70 (DO) | **Imp.** (PROD) | Q701 (177.57, 64.0), Q751 (170.48, 64.0) | Sin limitación de corriente: un corto de la carga a +24/+28 V lleva Q701 a saturación a VGS = 4.9 V, con decenas de W en un SOT-23, y lo destruye en ms (falla abierta o en corto). El latch se retiró el 2026-10-28. Con batería invertida, D701/Q701 conducen en directo y el relé externo se energiza. | README («un corto de la carga a +V no queda limitado por hardware»); DMN10H220L SOT-23 (RθJA de cientos de °C/W). | **Rev. B (esq. + layout):** low-side protegido AEC-Q100 con clamp ≥ 60 V y limitación térmica/de corriente (tipo HITFET para 24 V; verificar la VDS(AZ) contra el load dump suprimido de 58 V), o un limitador discreto con R de sensado, validado. Documentar el comportamiento con batería invertida. |
| R-05 | Esq. 70 (DIAG) | **Imp.** (PROD; DNP en PROTO) | R708–R710, D703 (193.5, 72.3); R758–R760, D753 (166.45, 81.0) | Divisor de 200 k / 220 k con zener BZX84-C3V3. Con el drenador a 12 V circulan ~30 µA por el zener (calc.). Un zener de 3.3 V a decenas de µA conduce muy por debajo de 3.3 V: DIAG puede quedar bajo V(IH) = 0.75·VDD ≈ 2.5 V y leer «bajo» con la carga presente. Con 58 V funciona. | BZX84 especifica VZ a 5 mA; ESP32-S3 V(IH) = 0.75 VDD. | Rev. B: entrada con transistor (por ejemplo 100 k a la base de un NPN, 22 k B–E, colector a 3V3 con pull-up: umbral ~4 V para todo el rango 9–58 V) o divisor hacia un canal ADC con diodo de clamp a 3V3 en lugar del zener. |
| R-06 | Esq. 10 (arranque) | **Imp.** (PROD) | C109 (120.4, 76.62), C105, R110 | Con C105 (1 mF), la corriente de inrush es 1.07 mF × 55 µA / 100 nF = 0.59 A (Notes de C109). A eso se suma la carga del buck, que arranca con VPROT ≈ 4 V (el EN de U201 está en VIN): ≈ 0.15–0.25 A durante la rampa. El breaker queda en 0.88–1.07 A (calc. con V(SNS_TH) 1.08–1.32 V): margen de ~0.1 A. Si el firmware activa WiFi o CAN durante la rampa, se dispara el breaker y entra en reintentos. | SNOSDF6 Ec. 2 y 15; §6.5 V(SNS_TH). | PROD: subir C109 a 220–330 nF, o retrasar el EN del buck con un divisor (~8–9 V) o con FLT. Ensayar el arranque con C105 a −40 °C y a 7, 12 y 24 V. |
| R-07 | Esq. 10/20, estabilidad | **Imp.** (verificar) | L101 (119.1, 55.2); C106/C201 (cerámicos) del lado del buck; C104/C105 del lado de la fuente | El filtro LC de entrada (10 µH, ~8 µF efectivos del lado del buck) solo se amortigua con la ESR de C104/C105, que están del lado de la fuente. Calc.: Zo ≈ 1.1 Ω, f ≈ 18 kHz. Con un electrolítico de baja ESR (o C105 de 1 mF en PROD), Q ≈ 20–35. Con 7 V de entrada y plena carga, la resistencia negativa del buck es ≈ V²/P ≈ 11 Ω, del orden del pico: no se cumple el criterio de Middlebrook. | LMR38010-Q1 §9 (input supply): «use an aluminum or tantalum input capacitor… 22 µF to 68 µF… to damp the input resonant circuit» y AN-2162. | Prototipo: escalón de carga en +5V con 7–8 V de entrada y medir la respuesta de +VPROT (o un Bode con inyección). Rev. B: electrolítico de 22–47 µF / 50 V (o un RC amortiguador) en +VPROT junto a U201. |
| R-08 | EMC / CAN | **Imp.** (PROD) | U601 (128.0, 119.0) | La portadora del isoPower (180 MHz) cae en la banda DAB III / TV de CISPR 25 (171–245 MHz). ADI solo garantiza EN 55022 clase B (−6 dB) en 2 capas con ferritas; CISPR 25 de clase 3 a 5 es más estricta en esas bandas. | ADM3055E Rev. D, «Radiated Emissions and PCB Layout» (180 MHz, ferritas de ~2 kΩ, EN 55022 en 2 capas). | Pre-escaneo ALSE en cuanto haya placa. Para la rev. B: 4 capas con planos solapados (capacidad de costura embebida, ADI AN-0971), o CAN no aislado (por ejemplo TCAN1044A-Q1) si el aislamiento no es un requisito, o un aislador digital con DC-DC aislado de baja EMI. |
| R-09 | EMC / buck | **Imp.** (PROD) | U201 (134.25, 63.85), U301 (140.4, 135.81) | LMR38010 con RT = 64.9 k: 320–480 kHz, y ±8 % de spread → 294–518 kHz. El extremo inferior entra en LW (150–300 kHz), y el modo PFM de carga liviana baja todavía más la frecuencia. Los armónicos 2.º a 4.º caen en MW (0.53–1.8 MHz). TPS62A02 en PSM: frecuencia variable con carga liviana (solo BLE). | LMR38010-Q1 §6.5 (FOSC 320/400/480 kHz, FSPREAD ±8 %); TPS62A02-Q1 (existe la variante FPWM **TPS62A02A-Q1**). | Medición conducida (método de tensión, CISPR 25) con carga BLE y con carga máxima. Si falla: LMR38010**FS**QDDARQ1 (FPWM + spread) y TPS62A02**A**-Q1, misma huella. Hay más consumo en reposo, a evaluar contra el presupuesto de corriente del vehículo. |
| R-10 | Layout / EMC | **Imp.** | J2 (178.0, 55.5), D701 (184.11, 64.0), D751 (163.95, 64.0), J1 pin 2 (~106, 109) | J2 está en el borde superior y J1 (único GND externo), en el borde izquierdo. La corriente de los relés, la energía inductiva que absorben D701/D751 y los pulsos ISO 7637 acoplados por las bobinas vuelven por GND_VEH en diagonal (~80 mm), cerca del buck y del MCU. | Geometría del PCB (posiciones en `INCLI-VA.kicad_pcb`). | Rev. B (layout + mecánica): J2 contiguo a J1, o un solo conector, con los TVS de DO junto a los pines GND de J1. Si J2 se queda donde está, dejarle una ruta de retorno ancha y dedicada hasta J1.2. |
| R-11 | Térmico / BOM | **Imp.** (PROD) | U401 | El ESP32-S3-WROOM-1-N8R2 opera de −40 a +85 °C y no es AEC-Q100. En una caja ABS en el chasis, al sol, el interior puede superar los 85 °C. | Notes de U401 (la PSRAM octal llega solo a 65 °C; N8R2 hasta 85 °C). | Definir la temperatura ambiente máxima del producto y hacer el ensayo térmico de §E. Si supera 85 °C, evaluar variantes de alta temperatura de Espressif (sin PSRAM; verificar en la guía de selección vigente) y revisar el uso de IO35–IO37. |
| R-12 | Esq. 60 (CAN) | Men. | J1 pin 5, GND_CAN | Si el arnés no lleva CAN_GND (J1939-15 no tiene hilo de masa), el dominio aislado queda flotante en DC y se referencia solo por el modo común del bus (C609). | J1939-11/-15 (práctica habitual). | Definir el arnés. En la rev. B, dejar una huella opcional de 1 MΩ ‖ 4.7 nF (≥ 1 kV) entre GND_CAN y GND_VEH (DNP por defecto). |
| R-13 | Esq. 60 | Men. | R602/R603 (113.3 y 115.9, 121.5) | La terminación partida está en 0603 (0.1 W). Con fallas de bus (CANH a batería con otro nodo en dominante) se puede superar esa potencia durante el timeout de dominante. | Práctica habitual en terminaciones partidas automotrices (≥ 0.25 W). | Rev. B: 1206 (≥ 0.25 W). Mismo valor. |
| R-14 | Esq. 60, ESD | Sug. | D601 (114.5, 116.7), DNP `PROTO,PROD` | Maquinaria de mina: ISO 10605 de hasta ±15 kV en aire en el conector. El ADM3055E garantiza ±8 kV de contacto (IEC 61000-4-2). | ADM3055E Rev. D, especificaciones de ESD. | Montar D601 en PROD (y en una placa de PROTO para comparar en el ensayo ESD). |
| R-15 | Esq. 40 | Sug. | J401, D401/JP401 retirados | USB no alimenta la placa: para programar en el banco hace falta la fuente de 12/24 V. La masa del PC queda unida a GND_VEH (documentado). | README, Notes de J401. | Rev. B: opción de alimentación desde VBUS con un diodo OR hacia +5V_VEH (DNP en PROD), para el banco y el taller. |
| R-16 | Layout 30 | Men. | U301 (140.4, 135.81), C301 (136.0, 139.3), C304 (151.0, 143.45), R303/R304 (145.0, 143.5/147.45) | TPS62A02 a 2.2 MHz: el Cin principal (C301, 10 µF) está a ~4–5 mm de VIN/GND (solo C302 queda pegado). C304 está a ~7–10 mm de L301 y del GND del CI. El divisor de FB está a ~9 mm del pin FB: la red de alta impedancia `U301-FB` mide 16.9 mm. | TPS62A02-Q1 §11 (layout): Cin y Cout lo más cerca posible, FB corto. | Rev. B (solo layout): Cin ≤ 1–2 mm de VIN/GND, Cout junto a L301 y al GND del CI, divisor junto al pin FB (el tramo largo, del lado de baja impedancia, desde VOUT). |
| R-17 | Esq. 30/40/60 | Men. | C304, C401 (Notes), C605 (143.33, 120.7) | El «presupuesto de 47 µF» en +3V3_D (Notes de C304/C401) no cuenta C605 (10 µF, hoja 60). Total nominal: 22 + 22 + 10 + ~0.6 ≈ 54.6 µF. TI admite hasta 47 µF «per default». | TPS62A02-Q1 §9.2.2.5. | Verificar la respuesta a un escalón (0.1 → 0.6 A) en el prototipo. Corregir las Notes. Con DC bias, el efectivo probablemente sea < 47 µF. |
| R-18 | Esq. 30 | Men. | Divisor VMON | No se mide la tensión de batería ni la corriente de entrada: IMON (U101 pin 10) está sin conectar y no hay divisor en VOUT/+VPROT. El firmware no puede registrar 12/24 V, huecos ni sobrecargas. | SNOSDF6 §8.2.2.6 (IMON). | Rev. B: divisor de VOUT a un ADC1 libre (o ADC2: con solo BLE no hay conflicto con WiFi) y R_IMON hacia el ADC. Elegir el GPIO fuera de los de strapping. |
| R-19 | Esq. 10 | Sug. | R107 | UVLO de caída en 6.46 V (6.26–6.73 V). La cadena 5 V → 3.3 V funciona hasta VPROT ≈ 5.5 V (el buck sale de regulación), y el LP5907/TPS62A02 siguen dando 3.3 V con +5V ≈ 3.6 V. Con el UVLO más bajo, el MCU sobrevive a la meseta de 6–6.5 V del cold crank de 12 V (ISO 16750-2 §4.6.3); el CAN (VCC ≥ 4.5 V) no. | SNOSDF6 §6.5 (V(UVLOF) 0.533/0.55/0.573 V). | Rev. B (solo valor): UVLO de caída ~5.5 V (TI usa 5.5 V en §8.2.2.4). Combinar con R-02. |
| R-20 | Layout | Men. | Ranura de B.Cu bajo U401 (x 173.5–184.1, y 77.9–124.7) | Haz de 46.9 mm en B.Cu bajo el módulo, cosido parcialmente por F.Cu. Ya aceptado; los tramos abiertos más largos miden ~10 mm (no resuenan en 2.4 GHz). | `docs/layout/ruteo/etapa6-ranura-u401.json`. | Rev. B: rutear el haz por F.Cu o alrededor del módulo. |
| R-21 | DFA | Men. | ~55 pares de courtyards a < 1 mm (cálculo con cajas envolventes; excluye U401) | AGENTS.md pide ≥ 1 mm entre courtyards para la punta del cautín. Muchos pares están aceptados como excepción (C402–U401, C404–U402, C507–U503, C505/C506–U502, desacoples de U601). | Medición en el PCB. | Prototipo: orden de soldadura de §6. Rev. B: recuperar 1 mm donde el reruteo lo permita. |
| R-22 | DFM | Men. | Serigrafía (regla `JLC_serigrafia`) | Texto mínimo de 0.8 mm; JLCPCB recomienda ≥ 1.0 mm (lo cita la propia cabecera del `.kicad_dru`). | `INCLI-VA.kicad_dru`. | Aceptable para el prototipo. En PROD, ≥ 1.0 mm en rótulos funcionales (pinout de J1/J2, TP). |
| R-23 | DFM | Men. | EP de U101 (vías de 0.2/0.4 mm) y de U201 (0.2/0.5 mm) | Vías en el pad sin rellenar: absorben estaño al soldar con aire caliente o en reflujo, y el agujero de 0.2 mm tiene costo extra en JLC. | Cabecera del `.kicad_dru`. | Prototipo: poner estaño desde abajo (para eso están, AGENTS.md). PROD: vías rellenas y tapadas (via-in-pad con epoxi) o tented del lado inferior. |
| R-24 | Mecánica | Men. | C104 (106.85, 71.0), B.Cu | Electrolítico de 10 × 10.5 mm en la cara inferior, a 1.6 mm del borde, en una placa con vibración. Ya documentado (adhesivo, separadores de 12 mm). | `docs/PENDIENTES.md`, «Requisitos para la caja». | Rev. B: pasarlo a la cara superior o reemplazarlo por un banco cerámico + polímero de perfil bajo. Mientras tanto: adhesivo y staking. |
| R-25 | Esq. 10 | Men. (abierto) | R102 (2512) | No se demostró que soporte el pulso del load dump sin suprimir (~2 W durante 350 ms). Sigue abierto desde REVISION_CODEX I2. | `docs/REVISION_CODEX.md` I2. | Decidir si el requisito de 202 V sigue en pie. Si sigue, elegir una 2512 anti-pulso con curva de pulso único a 85 °C. Si no, R102 puede bajar (ver R-02). |
| R-26 | Bring-up | Men. | Hoja 10 | No hay TP en VS, HGATE, VA, VOUT ni UVLO, justo las redes que hacen falta para diagnosticar R-01/R-02. | Netlist (TP101–TP104: +VPROT, VBAT_F, GND, FLT). | Prototipo: medir en los pads de C102 (VS), R105 (HGATE), Q101 pin 3 (VA) y C104 (VOUT). Rev. B: agregar TP en esas redes. |
| R-27 | Esq. 20/30 | Sug. | +5V_VEH | Si U201 falla con el high-side en corto, +5V_VEH sube a VPROT (hasta ~38 V) y destruye U301, U302, U601, U701/U751 (todos de ≤ 6 V). | — | Rev. B: TVS de 6–7 V o crowbar con fusible en +5V_VEH, si el análisis de fallas (FMEA) lo pide. |
| R-28 | Mecánica | Sug. | J1, J2 (MSTBV verticales) | La brida GF fija el enchufe al header, pero el header queda soldado solo por sus pines: la fuerza del cable con vibración llega a las soldaduras. | — | Caja: amarre del arnés junto a J1/J2 (en el interior, antes del conector circular). |
| R-29 | Firmware / HW | Men. | U401, IO47/IO48 (CAN_TX/RX) | IO47/IO48 están en el dominio VDD_SPI. En los módulos con flash de 1.8 V (variantes «V»), trabajan a 1.8 V y el ADM3055E (VIO = 3.3 V) no los leería bien. Con N8R2 (3.3 V) no hay problema. | ESP32-S3-WROOM-1, tabla de pines (dominio VDD_SPI); verificar en la revisión vigente. | Anotar en las Notes de U401: no sustituir por variantes de flash de 1.8 V ni de PSRAM octal (IO35–IO37 también lo impiden). |
| R-30 | Esq. 60 | Men. | C602 (139.56, 120.91) | ADI pide desacoples a ≤ 2 mm de VCC/VIO/VISOIN/VISOOUT. C602 (100 nF de VIO) está a ~6 mm, en cadena detrás de C601. Ya aceptado. | ADM3055E Rev. D (≤ 2 mm). | Rev. B: acercarlo. Sin efecto previsible en funcionamiento; posible efecto en emisiones. |

Ningún hallazgo contradice el DRC/ERC: todos son de diseño (valores, topología, ubicación), no de reglas.

### Lo que está bien (verificado)
- **Topología de entrada:** el LM74930 en common-source con Q101 (250 V) del lado de la batería, igual que la Fig. 8-1 de TI. RSET = 49.9 Ω, RILIM = 60.4 k → 0.99 A; ISCP a C → 20 mV / 10 mΩ = 2 A; CTMR = 68 nF → 0.99 ms; OV de 38.4 V nominal (37.4–40.3 V con la tolerancia del comparador; el jump start de 36 V queda por debajo con ~1 V de margen); CCAP = 100 nF ≥ 10 × (Ciss Q101 + Ciss Q102); OVCLAMP a GND; IMON abierto (permitido). El pad 25 (RTN) está aislado, con regla DRC propia.
- **TVS de pulso 1:** D101 (ES2G, 400 V) en serie con D102 (SMCJ33A), como el D2/D3 de la Fig. 8-1. D102 soporta la batería invertida de 24–28 V (standoff de 33 V).
- **LMR38010:** L = 33 µH y Cout = 3 × 22 µF según la tabla 8-1 (400 kHz, 5 V); RT = 64.9 k; FB 100 k / 24.9 k → 5.02 V; ton a 38.4 V ≈ 325 ns > tON-MIN de 131 ns; EN a VIN (máx. abs. VIN + 0.3 V). Lazo caliente de entrada corto: C202 pegado a VIN/GND, nodo SW de ~4 mm hasta L201 y BOOT junto al CI.
- **TPS62A02:** 453 k / 100 k + 10 pF → 3.318 V (SLUSFG7 §9.2.2.2). LP5907 desde 5 V con FB301: disipa 43 mW.
- **ESP32-S3:** strapping libre (IO0 con pull-up; IO3, IO45 e IO46 sin conectar); IO35–IO37 válidos con PSRAM quad (N8R2); RC de EN 10 k / 1 µF; TPS3828 de drenador abierto en wired-OR con EN; WDI en alta impedancia = watchdog deshabilitado durante el flasheo (buena decisión); USB-C con Rd de 5.1 k y USBLC6 junto al conector; ADC1 (IO1/IO2) para VMON.
- **Antena:** la placa tiene un recorte bajo la parte de antena del módulo (borde en x ≈ 192 entre y 99 y 134). El keep-out de la huella oficial se respeta y H2/H4 quedan a ≥ 17 mm de la zona de antena.
- **Sensores:** SCL3300 con RESERVED y EMC_GND a GND (Doc. 4921, tabla de pines) y los cuatro desacoples de 100 nF; ASM330 con RES a GND, INT1 sin pull-up y VDD con 100 nF + 10 µF (fig. 14); AS5147U en modo 3.3 V con VDD = VDD3V3 y 100 nF (fig. 13); TEST a GND; MISO compartido (los tres pasan a alta Z con CS alto); pull-ups de CS.
- **CAN:** desacoples de la tabla 10 (0.01 + 0.1 µF en VIO/VISOIN, 0.22 + 10 µF en VISOOUT, 10 + 0.1 µF en VCC), FB601/FB602 de ~1.8 kΩ a 100 MHz, RS a GND2 (velocidad completa), STBY con pull-up (arranca en silencio), terminación partida con 4.7 nF, ningún cobre bajo U601 y barrera ≥ 2.5 mm por regla.
- **DO:** buffer 74AHCT (VIH TTL de 2 V con entrada de 3.3 V), pull-downs en EN y en gate, zener de gate de 12 V y SMAJ58A (VBR 64.4 V mín. > 58 V; VC 93.6 V < 100 V).
- **Planos:** B.Cu casi continuo, 384 vías GND, GND_CAN en una sola isla por cara, teardrops, alivios térmicos para soldar a mano y conexión sólida en EP, D102 y J1.
- **Anchos (IPC-2152, 1 oz, ΔT 10 °C):** entrada de 1.5 mm, VA/C_ID/VOUT de potencia ≥ 1.0 mm (sensado de 0.25 mm), +5V ≥ 0.5 mm, DO de 0.5 mm. Con 1 A en la entrada (breaker) y ≤ 0.5 A por DO hay margen amplio.
- **Clearances:** HV (VIN_VEH/VBAT_F) a 1.25 mm (IPC-2221B B2, 171–250 V); PROT a 0.6 mm; DO a 0.6 mm. Correctos, con conformal coating.

---

## C. Discrepancias entre la documentación y el diseño

| # | Documento | Lo que dice | Lo que hay en el diseño |
|---|---|---|---|
| C-1 | `docs/REVISION_CODEX.md`, tabla de pines, fila «10 / U101» | «3 SW→divisor UVLO … Coincide con topología common-source de 200 V [SNOSDF6 figura 8-1]» | En la Fig. 8-1, R1 (UVLO) va a **VBAT** y SW queda sin conectar; además está D1 (VA → VS), que aquí falta. Ver R-01/R-02. |
| C-2 | `docs/PENDIENTES.md`, «Máximos de la entrada» | Tabla de tensiones por componente | No incluye C–A ni OUT–VS del LM74930 (R-03), ni la caída de VS en R102 (R-02). |
| C-3 | Notes de C109 | «Con C105 montado (~1.07 mF): 0.59 A < breaker 1 A» | Falta sumar la carga del buck durante la rampa y la tolerancia del breaker (0.88–1.07 A). Ver R-06. |
| C-4 | `docs/PENDIENTES.md`, «Notas para el próximo turno» | «Variante ROT: U503, C507 y R503 tienen `dnp yes`» | Tienen `DNP` vacío y `Variant = ROT`; están en `fab/proto/bom_proto.csv` y en la posición. El prototipo los monta (coincide con «CAN + DO + ROT»). La nota quedó vieja. |
| C-5 | `docs/PENDIENTES.md`, «Decisiones del usuario aún abiertas» | «Lado del imán de ROT» abierto | Decidido el 2026-10-30: imán arriba (F.Cu). |
| C-6 | `README.md`, tabla, fila `10_power_input` | «C105 (hold-up) es huella DNP» | `DNP = PROTO`: se monta en PROD. |
| C-7 | Notes de TP403 | «no alimenta la placa salvo con D401 + JP401» | D401 y JP401 se eliminaron. |
| C-8 | Notes de R708/R709 y R758/R759 | «el drenador llega a ~250 V» | Eso venía del FDD7N25LZ. Hoy Q701/Q751 son de 100 V y D701 recorta a ≤ 93.6 V. El 1206 sigue siendo adecuado. |
| C-9 | Notes de D703/D753 | «limita DIAG a 3.3 V … (antes 5V1 para el ISO7763)» | Con la corriente real del divisor, el zener no fija 3.3 V (R-05); la referencia al ISO7763 es vieja. |
| C-10 | Notes de C304 y C401 | Presupuesto de +3V3_D: «22 + 22 + 0.5 ≈ 44.6 µF; no agregar más bulk» | C605 (10 µF, hoja 60) también está en +3V3_D (R-17). |
| C-11 | Notes de J2 | «1777073, VERIFICAR en phoenixcontact.com» | `docs/PENDIENTES.md` («Conectores J1 y J2») lo da por confirmado. |
| C-12 | `docs/PENDIENTES.md`, «Hecho en este turno (2026-10-27)» | «R701 (1 Ω) se monta igual» | R701 ya no existe: el latch se retiró el 2026-10-28 (histórico, solo puede confundir). |
| C-13 | `README.md`, «Requisitos para el firmware» | Brownout: «sin C105 la placa se reinicia» | Tal como está dibujada, la placa no arranca (R-01). Después del retrabajo, la afirmación vale. |
| C-14 | Requisitos de firmware (`README.md` y `docs/PENDIENTES.md`) | Lista de SPI, ejes, ZPOS, watchdog y VAR_ID | Falta el bit **NOISESET** del AS5147U, obligatorio en modo 3.3 V (DS000639 v1-04, fig. 8), y el TLH ≥ 10 µs entre tramas del SCL3300 (Doc. 4921, tabla de tiempos SPI). Ver §D-8. |

Coinciden con el diseño (verificado): DRC 0 / 3 avisos y ERC 0 / 5 avisos; F101 de 2 A / 250 VDC; R803/R804 de 2.2 k; FID1–FID3; ejes en la serigrafía; TP406/TP505 con agujero; posiciones de H1–H5; J1 = VIN, GND_VEH, CAN_H, CAN_L, GND_CAN; VAR_ID R805/R806 = 0 Ω (CAN + DO → 00).

---

## D. Mejoras para la revisión B (priorizadas)

Tipo: **[E]** cambia el esquemático (y por lo tanto el layout), **[L]** solo layout, **[V]** solo valor o BOM, **[M]** mecánica.

**Prioridad 1: robustez y funcionamiento**
1. **[E]** UVLO desde VBAT_F con 2 × 1206 en serie; SW sin conectar (R-01).
2. **[E]** D1 (VA → VS, ≥ 100 V, SOD-123) según la Fig. 8-1 de TI (R-02).
3. **[E]** DO con protección de cortocircuito: low-side protegido AEC-Q100 apto para 24 V (R-04). DIAG con etapa de transistor (R-05).
4. **[V]** UVLO de caída en ~5.5 V para sobrevivir al cold crank de 12 V (R-19). C109 de 220–330 nF o EN del buck retrasado, para el arranque en PROD con C105 (R-06).
5. **[E]** Electrolítico o RC amortiguador en +VPROT junto a U201 (R-07).
6. **[V]** Si sigue el requisito de 202 V, R102 anti-pulso calificada (R-25).

**Prioridad 2: EMC**
7. **[E/L]** Decisión de arquitectura para CAN: ADM3055E en 4 capas con capacidad de costura, o transceptor no aislado (TCAN1044A-Q1, ~USD 0.6 contra ~USD 8–10, y además elimina el riesgo de 180 MHz) (R-08). Si la placa pasa a 4 capas, también mejoran el plano GND, la ranura bajo U401 (R-20) y el retorno de los DO.
8. **[L/M]** J2 junto a J1, o un solo conector de 7 vías, con los TVS de los DO pegados al GND de entrada (R-10).
9. **[V]** Variantes FPWM (LMR38010FSQDDARQ1, TPS62A02A-Q1) si el ensayo conducido lo pide (R-09).
10. **[V]** Montar D601 en PROD (R-14). **[V]** R602/R603 en 1206 (R-13).

**Prioridad 3: costo, tamaño y BOM**
11. Revisar si hacen falta los dos sensores de inclinación: el SCL3300 cuesta ~USD 20–30 y el ASM330 ~USD 5–6. Si el ASM330 solo sirve para vibración y fusión, se puede evaluar sacarlo de alguna variante. Decisión de producto.
12. **[V]** Pasar a `MPN` los pasivos Basic de igual especificación (`bom/BOM_PROD.csv`), si se mantiene AEC-Q200.
13. **[V]** L201: decidir entre XAL6060-333MEC (sin disponibilidad) y XGL6060-333MEC (misma huella, mejor DCR e Irms).
14. **[V]** Grado automotriz en PROD, a confirmar uno por uno: U402 → USBLC6-2SC6**Y**; D102/D103/D701/D751 → versiones AEC-Q101 de las mismas series; D101 → versión automotriz (HE3/«-Q»); D704/D754 → MMSZ5242B-Q; SW401/SW402 sin grado (solo servicio). U401 y SCL3300: comprobar su calificación (R-11).

**Prioridad 4: fabricación y prueba**
15. **[E/L]** TP en VS, HGATE, VA, VOUT y UVLO (R-26), y TP para CANH/CANL del lado aislado, junto a un TP de GND_CAN.
16. **[L]** TPS62A02: Cin, Cout y divisor de FB pegados al CI (R-16). C602 a ≤ 2 mm (R-30).
17. **[L]** Courtyards ≥ 1 mm (R-21); serigrafía ≥ 1.0 mm (R-22); via-in-pad rellenas para PROD (R-23).
18. **[E]** Medición de VBAT e IMON por ADC (R-18); opción de alimentación desde VBUS en el banco (R-15).
19. **[M/L]** C104 a la cara superior o banco de perfil bajo (R-24).

---

## E. Plan de pruebas para el primer prototipo

### E.0 Antes de energizar (con la placa armada)
1. **Aplicar los retrabajos R-01** (obligatorio) **y R-02** (recomendado). Anotar en la placa qué se hizo.
2. Inspección visual: polaridad de D101–D104, D701/D751, C104, C105 (si se monta) y LEDs; orientación de U101, U201, U301, U501–U503 y U601; puentes en el QFN, el SOT-563 y el LGA.
3. Resistencia contra GND_VEH (sin alimentar): VBAT_F, VOUT, +VPROT, +5V_VEH, +3V3_D y +3V3_A; ninguna debe estar en corto. Aislamiento GND_CAN–GND_VEH > 10 MΩ.

### E.1 Bring-up escalonado (fuente de laboratorio con límite de corriente)
| Paso | Condición | Medir | Criterio |
|---|---|---|---|
| 1 | 12 V, límite 100 mA; sin U401 si es posible (o con R802 abierta y EN a GND) | VS (C102), UVLO, HGATE–VA, VA, VOUT, FLT (TP104) | VS ≥ 6 V (con R-02); HGATE − VA ≈ 10–13 V; VOUT ≈ VBAT; FLT alto |
| 2 | Rampa lenta de 0 a 16 V (1 V/s) | Umbral de encendido y apagado (UVLO) | ~7.0 V de subida y ~6.5 V de bajada (con R-01, opción preferida) |
| 3 | 12 y 24 V | +VPROT, +5V_VEH (TP201/TP301), +3V3_D (TP302), +3V3_A (TP303), PG_3V3D (TP305) | 5.02 V ±2 %, 3.32 V ±2 %, 3.3 V; ripple de +5V < 50 mVpp y de +3V3_A < 5 mVpp |
| 4 | Barrido de 9 a 36 V | Corriente de entrada; arranque con 9 V | Arranca con 9 V; corriente de entrada coherente con ~1.5–4 W |
| 5 | 40 V → OV | Corte de HGATE y reconexión | Corte en 37.4–40.3 V; recupera al bajar |
| 6 | Batería invertida de −28 V durante 60 s | Corriente de entrada y temperatura de D102/Q102 | ~0 mA; sin daño (relés externos: ver R-04) |
| 7 | Breaker | Carga electrónica en +VPROT o en VOUT hasta disparar | Disparo en 0.88–1.07 A después de ~1 ms; reintento con FLT |
| 8 | MCU | Flasheo por USB, consola UART0 (J402), EN/BOOT, watchdog (dejar de patear WDI → reset a los 0.9–2.5 s) | Reset en la ventana del datasheet |
| 9 | Sensores | WHOAMI de los tres por SPI (con el modo SPI de cada uno), prueba de 6 posiciones (±1 g por eje, tabla de ejes de PENDIENTES), ZPOS de U503 con imán | Signos según la tabla; ruido del SCL3300 dentro de la hoja de datos |
| 10 | Estabilidad de potencia | Escalón de carga en +5V (0.1 → 0.7 A) con 7 V y con 24 V de entrada; escalón en +3V3_D (0.1 → 0.6 A, simulando un TX de WiFi) | Sin oscilación en +VPROT (R-07); caída de +3V3_D < 3 % (R-17) |

### E.2 Transitorios (ISO 7637-2 / ISO 16750-2, niveles a confirmar con el cliente)
- **Pulso 1** (12 V: −150 V / 10 Ω; 24 V: −600 V / 50 Ω): medir A, C, OUT y VS de U101 con sonda diferencial (R-03). Estado C admitido (reinicio).
- **Pulso 2a** (+112 V / 2 Ω / 50 µs en 24 V) y **2b**: corte por OV o SCP sin daño. Verificar que el contador de reintentos (32) no deje la placa bloqueada después de la serie completa.
- **Pulsos 3a/3b** (±300 V, 150 ns): en VIN y, con pinza capacitiva (ISO 7637-3), en el arnés de CAN y de DO.
- **ISO 16750-2:** sobretensión de 36 V (jump start) durante 60 s sin corte; load dump suprimido de 58 V / 350 ms (corte por OV, reinicio limpio); perfil de arranque de 12 V (§4.6.3; con R-19 aplicado, objetivo de estado A para el MCU); caída y subida lenta de 0 a VBAT (sin bloqueos); micro-cortes de 100 µs (C105 en PROD).
- **DO:** relé real de 12 V y de 24 V; medir el pico en el drenador (≤ 93.6 V) y la temperatura de D701; ensayar el pulso 1 a través de la bobina. El corto a batería es destructivo: hacerlo solo para confirmar el modo de falla, con una placa sacrificable (R-04).
- **ESD (ISO 10605):** ±8 kV de contacto y ±15 kV en aire en los pines de J1/J2 y en la caja, con D601 montado y sin montar.

### E.3 CAN
- 250 y 500 kbit/s (J1939) con una red de 2 a 3 nodos y 30–40 m de cable; terminación partida montada en un extremo.
- Recuperación de bus-off; TXD en dominante permanente → timeout de dominante del ADM3055E.
- Offset de masa: GND_CAN contra GND_VEH a ±(VBAT) sin errores de trama. Medir CANH/CANL **contra GND_CAN (J1 pin 5)**, nunca contra GND_VEH.
- Corriente de VCC del ADM3055E y temperatura de U601 con 50 % y 100 % de carga de bus.
- Emisiones con el CAN activo (R-08): pre-escaneo de 150 kHz a 1 GHz, con atención a 171–245 MHz.

### E.4 BLE / RF
- RSSI y alcance con la placa dentro de la caja ABS montada sobre una placa de acero (simulando el chasis), con 4 orientaciones; NimBLE con el intervalo de conexión de producción.
- Picos de corriente con WiFi (OTA) para confirmar el margen de +5V y del breaker.
- Emisiones conducidas (CISPR 25, método de tensión, LISN de 5 µH) en modo BLE (PFM/PSM) y con carga máxima (R-09).

### E.5 Vibración y mecánica
- Barrido de resonancia sinusoidal de 10 a 1000 Hz con acelerómetro de referencia, en la placa montada en H1–H5 con el apoyo B. Registrar las frecuencias propias cerca de U501/U502.
- Vibración aleatoria según ISO 16750-3 (perfil de vehículo comercial, montaje en chasis), 8 h por eje, con ensayo funcional durante la vibración: lectura continua de SPI y CAN sin errores; ruido del inclinómetro con la placa en reposo antes y después.
- Inspección posterior: soldaduras de J1/J2, L201, L301, C104 (cara inferior), C105 (PROD) y castellados de U401 (el módulo sobresale ~6 mm sobre el recorte).
- ROT: verificar el air gap de 0.5–3 mm con el portaimán real y la linealidad de ±1° en 360°.

### E.6 Térmica
- Cámara térmica a 25 °C, 24 V, WiFi en TX continuo, CAN al 50 % y los dos DO a 0.5 A. Puntos calientes esperados: U601, U201, L201, U301 y el módulo.
- Cámara climática a +85 °C (o a la temperatura ambiente máxima que se defina) dentro de la caja cerrada: temperatura interna del aire y de la carcasa de U401 (R-11); deriva de offset del SCL3300 y del ASM330 de −40 a +85 °C.
- Arranque en frío a −40 °C con 9 V (12 V) y con 18 V (24 V); en PROD, con C105 (R-06).

---

## Anexo 1 — Notas por bloque (para los puntos 1 a 8 del pedido)

### 1. Esquemático por hoja (complemento de la tabla B)
- **10_power_input:** ver R-01, R-02, R-03, R-06, R-07, R-19 y R-25. F101 (2 A / 250 VDC) coordina con el breaker de 1 A y con la SCP de ~2 A. R103 (10 mΩ, 1206, ERJ-8BW de 0.5 W): 10 mW a 1 A. Q101 (STD18NF25, RDS(on) ≈ 0.14–0.165 Ω): ~60 mW a 0.6 A, despreciable; en la rampa de arranque con C105 disipa del orden de W durante decenas de ms, dentro de un SOA típico de DPAK (verificar con la curva de ST). Q102 (IPD30N10S3L-34, 100 V, VGS de ±16 V ≥ 15 V que pide TI).
- **20_buck_5v:** presupuesto de +5V calc. ≈ 0.37 A (ESP32 con TX de WiFi, 0.5 A a 3.3 V) + ≤ 0.26 A (ADM3055E, picos) + 25 mA (LDO) ≈ 0.66 A, frente a 1 A / ILS-LIMIT de 0.9 A mín. Margen aceptable para el prototipo. Con el pico de WiFi y el CAN en dominante a la vez queda justo: medir (E.1, paso 10).
- **30_regulation:** ver R-16 y R-17. El LP5907 tiene margen de dropout (5.0 → 3.3 V). FB301 (BLM18PG221) aguanta 1.4 A, sin problema.
- **40_mcu:** ver R-11, R-15 y R-29. El EN con wired-OR (SW401, TPS3828 y RC) es correcto. IO39–IO42 (JTAG por pads) están libres con la configuración por defecto de eFuse (JTAG por USB). No cambiar el eFuse `STRAP_JTAG_SEL`.
- **50_sensors:** completo según los datasheets. Para firmware, ver §8.
- **60_can:** ver R-08, R-12, R-13, R-14 y R-30.
- **70_output_ch:** ver R-04 y R-05. La protección inductiva con SMAJ58A es correcta para relés estándar (≤ algunos mJ).
- **80_supervision:** TPS3828 de drenador abierto (tabla de variantes de SGLS143E), VIT− de 2.93 V típ., reset de 200 ms y timeout de 0.9/1.6/2.5 s. R801 está DNP para que la alta impedancia deshabilite el watchdog. Bien. LEDs a ~0.6–0.7 mA.

### 2. Ubicación
- El flujo de potencia es claro: J1 → F101 → D101/D102 → Q101/Q102 → U101 → R103 → C104/C105 → L101 → U201 (arriba), de izquierda a derecha. CAN aislado abajo a la izquierda, junto a J1. MCU y antena a la derecha, con recorte. Sensores en el centro, junto a H5, sobre el apoyo B. Bien agrupado.
- Mejorable: J2 lejos de J1 (R-10); C304 y el divisor del TPS62A02 lejos del CI (R-16); C602 (R-30). U601 (0.4–0.9 W) queda a ~25 mm de U503/U501: gradiente térmico sobre el inclinómetro. Conviene medirlo (E.6).
- Accesibilidad: los TP de la cara inferior están rotulados y hay GND con agujero para el caimán (TP406/TP505). Bien. Courtyards < 1 mm: ver R-21.

### 3. Ruteo y planos
- Lazo de entrada del buck chico y nodo SW corto. La costura alrededor del EP de U201 está documentada (plano B.Cu bajo U201/L201 al 99.6 %).
- Barrera GND_CAN: sin cobre bajo U601 y ≥ 2.5 mm por regla; los teardrops entre las filas de pads están verificados (0). Clearance HV de 1.25 mm en VIN_VEH/VBAT_F.
- Pares: USB D±, 45.95 mm cada uno sin vías en el tramo principal; cruza la ranura de B.Cu con GND en F.Cu al costado (aceptado). CAN asimétrico de 3.8 mm (sin efecto en CAN clásico).
- Anchos según IPC-2152: correctos (ver «Lo que está bien»).

### 4. EMC, ESD y transitorios
- **Ruta del pulso 1:** J1.1 → F101 → D101 → D102 → GND (pad de D102 con conexión sólida) → J1.2. Corta y en el borde izquierdo: bien.
- Positivos (2a, 3b): sin TVS+, los bloquean Q101 (250 V) y D101 (400 V), con corte por OV o SCP en ≤ 7 µs. C101 de 100 nF / 450 V absorbe los 3a/3b.
- Riesgos de CISPR 25: R-08 (180 MHz), R-09 (LW/MW) y R-10 (retorno de los DO). El filtro de entrada solo es diferencial: sin choque de modo común ni capacitores Y; en 2 capas, con caja ABS, el modo común del arnés puede dominar las emisiones radiadas de 30 a 200 MHz. Reservar huella para un choque de modo común en la rev. B si el pre-escaneo lo pide.

### 5. Térmica y mecánica
- Calc. con Ta = 25 °C: U201 ≈ 0.5–0.6 W × ~45–55 °C/W (2 capas) → +25–30 °C; U601 ≈ 0.4–0.6 W con 50 % de bus × ~60–70 °C/W → +30–40 °C; R102 y Q101/Q102 despreciables en régimen. A Ta = 85 °C, U601 llega a ~125 °C (Tj máx. 150 °C), aceptable. El límite real es U401 (R-11).
- H1–H4 en las esquinas y H5 junto a los sensores, más el apoyo B: buena rigidez local. H5 no magnético (documentado).
- C105 en PROD (J16, 17.3 mm) con terminales de soporte antivibración: bien. C104 en la cara inferior: ver R-24.

### 6. DFM/DFA y prueba
- JLCPCB: vía de 0.3/0.6 mm; las de 0.2 mm de los EP tienen costo extra; borde a 0.5 mm; puente de máscara ≥ 0.15 mm medido (U502/U301), contra 0.10 mm mínimo para máscara roja con 1 oz. Para pasar a 2 oz habría que revisar U502 y U301 (documentado).
- Stencil superior sin aperturas en los DNP (verificado en la documentación). C104 se suelda a mano en la cara inferior.
- Fiduciales: 3, no alineados. Bien.
- **Orden de soldadura sugerido (a mano):** (1) U502 (LGA) y U101 (QFN) con pasta y aire caliente, antes que sus vecinos (C505/C506, C108/C102); (2) U301 (SOT-563), U201 (EP) y U601; (3) pasivos de 0603/0805 por zonas, de los más bajos a los más altos; (4) U501, U503 y U401 (castellado; los pads de GND al final, con el EP desde abajo); (5) L201, L301, Q101/Q102 y F101; (6) C104 (cara inferior), J402, J401, J1 y J2; (7) los retrabajos R-01/R-02; (8) limpieza y, después del bring-up, el conformal coating con J1, J2, J401 y J402 enmascarados.

### 7. BOM
- Sustitutos de PROTO aceptados: coherentes con el criterio «PROTO = PROD salvo calificación». Q101, Q102 y F101 se mantienen originales (correcto para validar la protección).
- Riesgo de suministro: L201 XAL6060-333MEC (no disponible; la alternativa XGL6060 está bien argumentada); AS5147U, STD18NF25, IPD30N10S3L-34 y SF-2410 sin stock en LCSC; U601 con stock bajo en JLC; SCL3300 (costo y plazo). STD18NF25: confirmar con ST el estado del ciclo de vida antes de PROD.
- AEC en PROD: ver §D-14. Además, U401 no es AEC-Q100 (R-11).
- Costo (según `docs/BOM_SOURCING.md`): ~USD 90 por placa a 100 u. Las palancas principales son la arquitectura de CAN (§D-7) y los dos inclinómetros (§D-11).

### 8. Requisitos firmware–hardware (consolidado)
Ya documentados (y verificados contra el esquema): un `spi_device` por sensor (SCL3300 en modo 0, 2–4 MHz; ASM330 en modo 3, ≤ 10 MHz; AS5147U en modo 1, ≤ 10 MHz); ASM330 con `I2C_disable = 1`, `DEVICE_CONF = 1` e INT push-pull; transformación de ejes de U501 y U502 y prueba de 6 posiciones; U503 a 180° → ZPOS; WDI cada ≤ 0.5 s, sin alta impedancia salvo antes de dormir más de 0.9 s; VAR_ID con pull-ups internos (IO4/IO5/IO8); LEDs por PWM; DO apagadas hasta inicializar; arranque limpio tras un brownout.

**Faltan (agregar a «Requisitos para el firmware»):**
1. **AS5147U:** poner a 1 el bit **NOISESET** (registro de configuración) porque el sensor trabaja en modo 3.3 V (DS000639 v1-04, fig. 8: «3.3V operation mode… Noiseset bit has to set»). Usar CRC/paridad en todas las tramas. La programación OTP necesita 3.3–3.5 V: se puede hacer en la placa, pero LP5907 = 3.3 V es el mínimo.
2. **SCL3300:** protocolo fuera de trama (la respuesta llega en la trama siguiente); **TLH ≥ 10 µs** con CSB alto entre tramas (Doc. 4921, tiempos de SPI); comprobar el CRC de cada respuesta; secuencia de arranque (SW reset, selección de modo, espera, lectura de STATUS hasta quedar limpio); modo 1 o 2 para el rango completo (los modos 3 y 4 limitan la inclinación a ±10°).
3. **ASM330:** INT1 no debe tener pull-up activo en IO40 durante el arranque (ya documentado); habilitar el pull interno solo después de configurar el sensor.
4. **CAN:** bajar CAN_STBY (IO21) y mantener CAN_SILENT (IO42) en 0 para transmitir; recuperar el bus-off; tener en cuenta el timeout de dominante del ADM3055E.
5. **PWR_FLT_N (IO39):** interrupción o lectura periódica; registrar los eventos de OV, UV, OC y SCP del LM74930.
6. **VMON (IO1/IO2):** ADC1 con calibración eFuse; escalas 149.9/49.9 (5 V) y 2 (3.3 V); el muestreo se apoya en C309/C310.
7. **Watchdog:** en la OTA, el borrado de flash puede bloquear más de 0.9 s; patear WDI desde un contexto que no quede bloqueado, o pasar IO17 a alta impedancia de forma explícita durante la escritura.
8. **Brownout:** habilitar el detector de brownout del ESP32-S3 y llevar las DO a estado seguro en el reset.
9. **Módulo:** no cambiar a variantes de flash de 1.8 V ni de PSRAM octal (IO35–IO37 e IO47/IO48; R-29).
