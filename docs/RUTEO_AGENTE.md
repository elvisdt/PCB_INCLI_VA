# Ruteo del agente (rama `ruteo-agente`)

Parte del tag `placement-v1`. El usuario rutea en paralelo una copia en `PCB_INCLI_VA_manual` (rama `ruteo-manual`): no tocarla.

## Reglas de trabajo
- No mover ni rotar componentes respecto de `placement-v1`. Si alguno lo necesita, se anota abajo y se espera la decisión del usuario.
- Al final de cada etapa: DRC, render de las dos caras, commit, `git push origin ruteo-agente`, y esperar el visto bueno del usuario.

## Cambios de ubicación
Aplicados en `ruteo-agente`, con autorización del usuario. Repetirlos en la copia manual para comparar.
- **C104 (47 µF, VOUT) → B.Cu, en (106.85, 71.0), eje horizontal y pad 1 al oeste** (2026-10-29). En F.Cu no tenía camino a VOUT: al norte el nodo SW de U201, al oeste la zona de U101 y al sur el lazo de HGATE. Ahora queda debajo de C105/L101.1 y se une al tronco VOUT con 2 vías y a C105.1 con 3 vías y un tramo en B.Cu. Agrega 10.5 mm de altura en la cara inferior.

- **U301 girado 180° (r90 → r270) y C302 a (138.1, 135.875) r270**, junto al pin 3 (VIN). Hicieron falta las dos cosas: con el giro solo, C302 quedaba a 4 mm; moviendo solo C302, EN y FB seguían cruzando el nodo SW. Referencia de U301 en (142.2, 132.8).
- **TP101 a (127.6, 61.5)**, B.Cu, conectado por vía al ramal de +VPROT (C201 → C202).
- **TP301 de (140.0, 134.0) a (140.0, 131.6)**, B.Cu, r180 conservada (Codex, 2026-10-29; autorizado por el usuario). Queda directamente sobre la vía existente del tronco +5V. Retirada la pista B.Cu de (140,131.6) a (140,134), fuera de la proyección del SW de U301. El plano continuo se hará en la etapa 5.

## Etapas
| Etapa | Estado | Commit |
|---|---|---|
| 0. Reglas | aprobada (2026-10-29) | 36bf77f |
| 1. Potencia | cerrada (2026-10-29) | 4c8b1f8 + cierre |
| 2. CAN | terminada; espera visto bueno del usuario | cierre `[Codex]` de 2026-10-29 |
| 3. USB/MCU | | |
| 4. Sensores y señales | | |
| 5. Planos | | |
| 6. Cierre y fabricación de prueba | | |

## Etapa 0 — reglas (2026-10-29)
Sin cobre nuevo: los renders son idénticos a `docs/layout/placement-v1-*.png`.

### Net classes (`.kicad_pro`)
| Clase | Redes | Pista | Separación | Par (ancho / gap) |
|---|---|---|---|---|
| Default (señal) | resto | 0.2 | 0.2 | — |
| HV | VIN_VEH, VBAT_F, VOUT, +VPROT, **VA, C_ID** | 1.0 | 1.25 | — |
| DO | VEH_DO1, VEH_DO2 | 0.5 | 0.6 | — |
| 5V | +5V_VEH, **BUCK_SW** | 0.5 | 0.2 | — |
| 3V3 | +3V3_D, +3V3_A | 0.4 | 0.2 | — |
| CAN | BUS_CAN_H, BUS_CAN_L | 0.3 | 0.2 | 0.3 / 0.3 |
| USB | USB_D+, USB_D- | 0.3 | 0.2 | 0.3 / 0.2 |

- Todas las clases: vía de 0.3/0.6 mm. Board Setup: piso de 0.15 mm cobre-cobre (JLCPCB), anchos predefinidos 0.2–1.0 mm, vía 0.6/0.3 y pares 0.3/0.3 y 0.3/0.2.
- **Teardrops:** activados en vías, pads PTH y pads SMD (forma redonda y rectangular). Los genera el editor al rutear de forma interactiva. Con ruteo por script se agregan en el cierre (Edit → Edit Teardrops, o por la API si responde) y se verifican en el DRC final.
- VA y C_ID entran en HV: son la cadena de potencia entre Q101, Q102 y R103, y la `.kicad_dru` ya les exigía 1.0 mm. BUCK_SW entra en 5V por la misma razón (0.5 mm en la `.kicad_dru`).

### Cambios en `INCLI-VA.kicad_dru`
- **Se quitó `JLC_espacio_cobre` (clearance de 0.15 mm sin condición).** Una regla sin condición anula todas las clearances de las net classes. Comprobado con DRC: con HV en 1.25 mm no aparecía ningún error.
  - El piso de 0.15 mm pasa a Board Setup (`min_clearance`).
  - En su lugar, `Pads_mismo_encapsulado` (0.15 mm) deja que la separación entre pads de un mismo componente la fije el encapsulado.
- `MV_entrada_protegida_40V` → `MV_entrada_protegida_40V_pads`. Entre conductores de VA/C_ID/VOUT/+VPROT manda la clase HV (1.25 mm). Cuando interviene un pad se aplica 0.6 mm (IPC-2221B B2, 31–50 V).
- `HV_llegada_U101`: dentro del courtyard de U101 (QFN de 0.5 mm) las pistas HV pueden bajar a 0.25 mm con 0.2 mm de separación. Son entradas de sensado. Excluye la red U101_RTN, que mantiene sus 0.3 mm.
- `HV_llegada_U201`: dentro del courtyard de U201, +VPROT puede bajar a 0.6 mm (el ancho del pin).

### Prueba de las reglas (pistas de prueba en una copia)
| Caso | Esperado | DRC |
|---|---|---|
| +VPROT 1.0 mm a 1.20 mm de GND_VEH | error (HV 1.25) | error ✓ |
| +VPROT 1.0 mm a 1.30 mm de GND_VEH | pasa | pasa ✓ |
| VEH_DO1 a 0.5 mm de DO1_EN | error (0.6) | error ✓ |
| USB_D+ / USB_D- a 0.2 mm | pasa | pasa ✓ |
| Señal a 0.18 mm de otra señal | error (0.2) | error ✓ |

### Decisiones del usuario (2026-10-29)
1. **Aprobado:** VIN_VEH y VBAT_F con 1.25 mm en todo. VOUT y +VPROT con 1.25 mm entre pistas, vías y rellenos, y 0.6 mm junto a pads: están después del corte de Q101 (≤ 38.4 V).
2. **Par CAN:** no se renombran las redes; se rutea acoplado a mano.
3. **USB 0.3/0.2 mm:** aprobado.

### Planteo original
1. **HV en VOUT/+VPROT:** se usa 1.25 mm entre pistas, vías y rellenos, y 0.6 mm cuando hay un pad de por medio. Con 1.25 mm literal no se pueden conectar el pin VIN de U201 (GND a 0.67 mm), C202/C107 (0603) ni la ubicación aprobada (C202.2 a 1.15 mm de U201.2). VIN_VEH/VBAT_F (202 V) mantienen 1.25 mm en todo, salvo entre pads de un mismo encapsulado.
2. **Par CAN:** KiCad reconoce pares solo por el sufijo (`+`/`-` o `P`/`N`), así que `BUS_CAN_H/L` no se detecta. La clase CAN fija ancho y gap, y el agente las rutea acopladas por script. Si quieres el router interactivo de pares en tu copia manual, habría que renombrar las redes en el esquemático (por ejemplo `BUS_CAN_P/N`). No se hizo.
3. **USB:** 0.3/0.2 mm cabe en el paso de 0.5 mm de J401. En 2 capas de 1.6 mm la impedancia no queda en 90 Ω, pero para Full-Speed (12 Mbit/s) con menos de 30 mm de pista alcanza.

### Verificación
- DRC: 0 errores; 5 avisos conocidos (3 de U401, y las referencias de Q101 y U801). Paridad 0; 358 sin rutear.

## Etapa 1 — potencia (2026-10-29)
Script: `scripts/ruteo/etapa1_potencia.py`. Parte del PCB de la etapa 0 (36bf77f) y se aplica sobre el archivo del proyecto. Renders: `docs/layout/ruteo/etapa1-top.png` y `etapa1-bottom.png`.

### Ruteado
- **Entrada (F.Cu, 1.5 mm):** J1.1 → F101 → VBAT_F → tab de Q101, R102, C101, R108 y D101; TP102 por vía. D101 ↔ TVS D102, y el GND del TVS va directo al pin 2 de J1.
- **FETs:**
  - VA, la fuente común de Q101/Q102, tiene 1.0 mm y pasa entre C105.1 (0.7 mm) y los gates (0.5 mm).
  - C_ID: tab de Q102 → R103.1.
- **VOUT:** R103.2 → tronco de 1.5 mm por el borde oeste → L101.1. C104 (B.Cu) se une por vías y C105.1 por vías y B.Cu.
- **Kelvin de R103:** dos pistas de 0.25 mm salen de los pads del shunt y corren paralelas, separadas 0.55 mm, por debajo de C105 hasta la zona de U101.
  - C_ID va a R104 (CS+, pin 20).
  - VOUT va a CS- (pin 19) con un arco por B.Cu.
  - ISCP (pin 18) y C103 se unen a la Kelvin C_ID con otro arco por B.Cu, por fuera del anterior.
- **Gates:**
  - Q101.1 ↔ R105, pegados.
  - HGATE va hasta el pin 14 en F.Cu (~17 mm). DGATE va hasta el pin 1 en B.Cu (~25 mm).
  - El largo lo impone la ubicación: U101 está a ~12 mm de los FETs.
  - Los pines A y OUT de U101 (VA) llegan con pistas de sensado y saltos por B.Cu.
- **+VPROT:** L101.2 → C106, C107 → C201 → ramal por el pad de C202 → pines 2 y 3 de U201.
- **Buck U201:**
  - Nodo SW: pin 8 → L201.1, vertical de 3.7 × 1.2 mm.
  - BOOT con C203 junto al pin.
  - FB: pin 5 → R202 → R201, y la parte alta de R201 toma +5V en el pad de C204 (FB desde el capacitor de salida).
  - RT corto. Vía a GND en cada pad de C204, C205 y C206. El pad expuesto ya trae 8 vías térmicas.
- **+5V:**
  - C204 → C206.
  - Tronco de 1.0 mm por x 137.6. Queda a 12.4 mm del centro de U503 y a 9.8 mm de su cuerpo; lo vemos en la etapa 4.
  - Llega a FB301/U302 y a U301. TP201 y TP301 por vía.
- **U301:** SW en F.Cu hasta L301. VIN, EN y FB cruzan por B.Cu. 3V3_D: L301.2 → R302 → C304, y el FB alto se toma en C304.1. TP302 por vía.
- **U302:** IN y EN filtrados por FB301/C306, OUT a C307. GND del pin 2 por vía.

### Reglas agregadas (`INCLI-VA.kicad_dru`)
- **En KiCad 10 hay que escribir `A.NetClass`.** El nombre de propiedad se probó en este turno.
- `HV_sensado`: una pista HV de ≤ 0.3 mm se trata como sensado. Mínimo 0.25 mm, 0.6 mm contra otras redes y 0.3 mm entre redes protegidas (`HV_sensado_entre_protegidas`).
- `HV_zona_U101`: 0.2 mm dentro de `ZONA_U101`. Es un rule area sin restricciones (x 113.8–134.4, y 64.2–84.4), con las mismas tensiones que entre los pines del VQFN, y la placa lleva coating. No aplica a VIN_VEH/VBAT_F ni a la red RTN.
- `VA_compuertas_Vgs`: VA contra HGATE/DGATE a 0.2 mm (Vgs ≤ 15 V).
- `HV_llegada_U201`: ahora incluye el paso por el pad de C202.

### Compromisos (para revisar)
- **Retorno del lazo de entrada de U201:** con 1.25 mm entre pistas +VPROT y GND (decisión aprobada), C202.2 y el pin 1 no pueden unirse por pista. Cada uno baja al plano con su vía, a ~4.5 mm de las vías del pad expuesto. Si se aceptara 0.6 mm dentro del área del buck, igual que en la zona de U101, el retorno iría por F.Cu directo.
- **C201 (4.7 µF):** llega a VIN dando la vuelta por el ramal de C202, unos 13 mm. C202 (100 nF) sí está pegado a los pines.
- **Zona U101:** 11 vías y tramos cortos en B.Cu (aceptado por el usuario). El plano GND de la etapa 5 va a quedar en islas cosidas bajo el controlador.

### Queda para otras etapas
- **Etapa 2 (CAN) y etapa 3 (MCU):**
  - CAN_RX/TX/SILENT/STBY cruzan el tronco de +5V (x 147.3, y 110.6–124.8) y saltan por B.Cu.
  - +5V hacia C603/C604 de U601 sale del tronco en y 124.8.
- **Etapa 4:** periféricos de U101 (SW, UVLO, OV, TMR, ILIM, FLT, EN/MODE, CAP, VS y VS → D104), con el plan de saltos ya reservado. También PG de U301, +3V3_A hacia los sensores, R111/+3V3_D, TP104, TP303 y TP305.
- **Etapa 5:** las 20 vías GND que quedan sueltas hasta el plano.

### Verificación
- DRC: 0 errores. Avisos: 20 `via_dangling` (vías GND esperando el plano) y los 5 conocidos.
- Paridad: 0. Sin rutear: 291 (antes 358).
- **Incidente corregido:** guardar el PCB con `pcbnew` después de cargarlo desde el scratchpad sobrescribió `INCLI-VA.kicad_pro` con valores por defecto, y se perdieron las net classes. Se restauró desde git. Desde entonces el script se corre sobre el archivo del proyecto.

## Cierre de la etapa 1 (2026-10-29, pedido del usuario)
- **Net classes:** HV queda solo para VIN_VEH/VBAT_F (1.25 mm). Clase nueva **PROT** para VA, C_ID, VOUT y +VPROT, con 0.6 mm (≤ 38.4 V; IPC-2221B B2, placa con coating).
  - Se quitó `MV_entrada_protegida_40V_pads`, porque la cubre la net class.
  - Las reglas `HV_sensado*` y `HV_zona_U101` pasan a llamarse `PROT_*`.
- **`ZONA_BUCK_U201`** (x 124.0–151.0, y 52.0–69.0): 0.25 mm para PROT (`PROT_zona_buck_U201`) y +VPROT de 0.6 mm (`PROT_llegada_U201`). Las dos reglas de zona excluyen los pares de pads de un mismo componente.
- **Lazo de entrada de U201:**

  | | Antes | Después |
  |---|---|---|
  | Retorno de C202 | 2 vías + plano (~2.8 mm) | F.Cu directo al pin 1 y al pad expuesto (1.7 mm) |
  | Área del lazo de C202 | 6.1 mm² | **3.9 mm²** |
  | C201 → VIN | 11.3 mm | **8.6 mm** (diagonal → pad de C202) |
  | Área del lazo de C201 | 31.3 mm² | **26.4 mm²** |
- **U301:**
  - SW (pin 2) va al norte hasta L301 por F.Cu. VIN (pin 3) → C302.1 (1.8 mm).
  - GND (pin 1) y C302.2 bajan por vías al plano. EN, FB y PG salen al sur por F.Cu, sin nada bajo el nodo SW.
  - Área del lazo de entrada: ~5.1 mm² (antes 6.1 mm², con VIN cruzando por B.Cu y 2 vías).
  - PG_3V3D ruteado hasta R302.2.
- **Gates:**
  - HGATE y OUT/VA (pin 15) van paralelas, a 0.5 mm entre ejes: por el pasillo U101–C103 (x 128.78 / 129.28), por el sur de la fila R109–R111 (y 82.3 / 82.85) y hasta Q101/R105.
  - DGATE va por B.Cu justo debajo del retorno de A/VA (pin 2 → tronco VA, x 117.3 e y 82.5) hasta Q102.1.
  - Las dos quedan lejos de los nodos SW.
- **C104** queda en B.Cu: no hay lugar en F.Cu sin alargar el lazo. Requisitos de la caja: separadores de ≥ 12 mm y adhesivo en C104.
- **Verificación:** DRC 0 errores (19 `via_dangling` GND, que esperan el plano), paridad 0, 288 sin rutear.
- **Traspaso a Codex:** `docs/RUTEO_TRASPASO.md`.

## Etapa 2 — avance parcial de Codex (2026-10-29)

**Estado histórico del avance parcial `5613d67`; ver cierre abajo.** KiCad cerrado, sin archivos de bloqueo, antes de editar. Base de placa: `b46f185`; decisiones: `a6ba59d`.

Hecho:
- Fuente aislada: VISOOUT → C610 → C606 → FB601 → VISOIN; C607 y C608 al pin 16. GNDISO_CAN une pines 18/20, C610/C606 y FB602; su salida conserva GND_CAN. CAN_RS completo.
- Alimentación VCC desde el tronco +5V y cadena pin 3 → C604 → C603. VIO: pin 4 → C601 → C602 → C605; alimentación desde U301 pendiente de la etapa 3, como permite el traspaso.
- Retornos locales a sus masas mediante vías. GND_VEH/GND_CAN esperan los planos de la etapa 5.
- CAN_TX/RX/STBY/SILENT completos hasta U401, con pull-up/pull-down y TP404/TP405. Saltos por B.Cu sobre +5V; tronco conservado.
- TP301 trasladado según «Cambios de ubicación». Ningún otro componente movido; esquemáticos intactos.

Verificación del avance:
- DRC: **0 errores**, **42 avisos** (37 `via_dangling` de masas pendientes de plano, 2 `silk_overlap`, 2 `silk_edge_clearance`, 1 `lib_footprint_mismatch` conocido).
- Paridad: **0 diferencias**. Conexiones pendientes: **262** (incluyen el bus CAN, la terminación, los planos y las etapas siguientes).
- Revisados renders `docs/layout/ruteo/etapa2-parcial-{top,bottom}.png`; reporte DRC y medidas JSON en la misma carpeta.
- `.kicad_pro`: solo había reordenamiento de clases; se comprobó equivalencia JSON y se conservó el contenido original. `.kicad_dru` intacto.
- Comprobadas las posiciones/rotaciones/capas/redes de todas las huellas contra la base: solo cambia TP301. Solo se retira una pista previa (su bajada); se agregan 135 pistas/vías en el grupo `CODEX_ETAPA2`.

### Medidas reales de desacoples

Longitud a lo largo del camino de cobre desde el borde del pad del pin hasta el borde del pad del capacitor (incluye el recorrido por el capacitor previo en las cadenas). Se consideran las esquinas redondeadas de los pads; muestreo de 0.001 mm. No son distancias rectas de ubicación. `scripts/ruteo/verify_etapa2.py` reconstruye el camino desde el PCB y comprueba que las cadenas pasen por el capacitor anterior.

| Capacitor | Valor | Pin U601 | Pista entre bordes (mm) | Retorno | Estado |
|---|---|---|---:|---|---|
| C601 | 10 nF | 4, VIO | 1.101 | GND_VEH | ≤2 mm |
| C602 | 100 nF | 4, VIO | 6.616 | GND_VEH | detrás de C601 |
| C605 | 10 µF | 4, VIO | 12.270 | GND_VEH | detrás de C602 |
| C604 | 100 nF | 3, VCC | 1.318 | GND_VEH | ≤2 mm |
| C603 | 10 µF | 3, VCC | 6.889 | GND_VEH | detrás de C604 |
| C607 | 10 nF | 16, VISOIN | 1.646 | GND_CAN | ≤2 mm |
| C608 | 100 nF | 16, VISOIN | **2.145** | GND_CAN | **excepción pendiente** |
| C610 | 220 nF | 19, VISOOUT | 1.682 | GNDISO_CAN | ≤2 mm |
| C606 | 10 µF | 19, VISOOUT | 4.292 | GNDISO_CAN | detrás de C610 |

### Decisiones solicitadas en el avance parcial (histórico; resueltas en el cierre)

1. **Cruce CANH/CANL:** J1.3/H y D601.1/H están por encima de J1.4/L y D601.2/L; U601.13/L está por encima de U601.14/H. Se propone un salto corto de una señal por B.Cu con dos vías junto a D601 para invertir el orden y conservar un recorrido compacto. Cambia el criterio «sin vías»; no se ha aplicado. Alternativa solicitada: revisar ubicación si el usuario mantiene el criterio sin vías. No se movieron D601 ni las terminaciones.
2. **C608:** el mínimo entre el cobre real de los dos pads redondeados es `hypot(1.975, 1.565) - 0.15 - 0.225 = 2.145 mm`. Los ~1.99 mm previos corresponden a las esquinas de los rectángulos envolventes, que no tienen cobre. El trazado alcanza el mínimo real; se solicita aceptar **≤2.15 mm** solo para C608. No se presenta como cumplimiento del límite de 2 mm.

**CANH/CANL:** sin trazado completo, por lo que sus longitudes y diferencia aún no se pueden informar como resultado de aceptación. Pendientes también la conexión del punto medio R602/R603/C609, revisión final de la etapa, nuevos renders, commit de cierre y visto bueno.

Scripts: `etapa2_can.py` regenera solo las pistas de su grupo, conserva la etapa 1 y aplica TP301. La eliminación nativa de grupos mediante SWIG falló en KiCad 10.0.7; se sustituyó por eliminación de los bloques de pistas/vías por sus UUID antes de cargar el archivo del proyecto. No cargar una copia externa y guardarla sobre el proyecto.

## Cierre de la etapa 2 — Codex, 2026-10-29

**Etapa 2 terminada; esperar visto bueno antes de la etapa 3.** Base del turno: `5613d67`. KiCad cerrado y ausencia de bloqueos comprobada antes de editar.

### CAN y decisiones aplicadas
- Evaluado primero el giro de D601 a 180° en memoria, conservando sus redes. Pad 1/H pasa a (115.4375,117.65), pad 2/L a (115.4375,115.75), pad 3/GND_CAN a (113.5625,116.7). Aunque H/L coinciden entonces con U601, la inversión queda entre J1 y D601 y el pad de masa ocupa el acceso de J1. Se conserva la orientación **r0**, y se aplica la alternativa autorizada del puente; **D601 no tiene cambio de ubicación ni de orientación aplicado**.
- CANH: puente B.Cu recto de **3.844 mm**, ancho 0.3 mm, de (114.45,115.75) a (118.2,116.595), con dos vías Ø0.6/taladro0.3. Es el único tramo B.Cu del par. CANL completo en F.Cu. Paso directo para limitar el corte del futuro plano GND_CAN.
- Pistas CAN de 0.3 mm; segmentos acoplados con gap de 0.3 mm, aperturas en pads y ajuste local de L. J1→D601→U601 completo, sin renombrar redes ni intercambiar pines en el esquemático.
- Terminación partida R602/R603/C609 completa. Punto medio por B.Cu con sus propias dos vías, sin mezclarse con GND_CAN. R602/R603/C609 se montan en PROTO; PROD según instalación.
- Retorno de D601.3 a GND_CAN mediante vía en (115.4375,117.25), a 0.55 mm del centro del pad. Las vías GND de C607/C608 se colocan en (118.725,119.95) y (118.725,122.55), dejando paso a CANH. No se movieron capacitores.
- **C608 = 2.145 mm: excepción aceptada**, límite 2.15 mm. Los otros cuatro desacoples cercanos siguen por debajo de 2 mm.
- **Cambios de ubicación:** solo TP301, ya registrado arriba. El giro evaluado de D601 no se aplicó.

### Longitudes del par

Recorrido principal **J1.3/4 → D601 → U601.14/13**, entre centros de pads, excluyendo ramales de terminación. El proyecto ya tiene `use_height_for_length_calcs = true`; se conserva. La compensación incluye el espesor nominal de 1.6 mm por vía (3.2 mm en H). Esta inclusión de la altura corresponde al [criterio de longitud de KiCad 10](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#length-tuning).

| Métrica | CANH | CANL | Diferencia |
|---|---:|---:|---:|
| Pista planar principal | 19.0139 mm | 22.2120 mm | 3.1981 mm |
| Altura de vías | 3.2000 mm (2 vías) | 0 | — |
| **Total nominal principal** | **22.2139 mm** | **22.2120 mm** | **0.0019 mm (≤1 mm)** |
| Entre bordes de pads, incluyendo vías | 19.7612 mm | 19.7593 mm | 0.0019 mm |

No confundir estas longitudes con la suma de todo el cobre de cada red: los ramales desde la bifurcación hasta R602/R603 miden 11.7498 / 2.7407 mm y no forman parte del camino J1→U601. Las cifras son geométricas nominales, no una medición de retardo sobre la placa fabricada.

### Tabla final de desacoples

Pista desde borde real del pad del pin hasta borde real del pad del capacitor. Los recorridos en cadena incluyen el paso por el capacitor anterior; no son distancias rectas de ubicación.

| Ref. | Valor | Pin U601 | Longitud | Criterio / retorno |
|---|---|---|---:|---|
| C601 | 10 nF | 4, VIO | 1.101 mm | ≤2 mm; GND_VEH |
| C602 | 100 nF | 4, VIO | 6.616 mm | cadena detrás de C601; GND_VEH |
| C605 | 10 µF | 4, VIO | 12.270 mm | cadena detrás de C602; continuidad y costura GND en etapa 5 |
| C604 | 100 nF | 3, VCC | 1.318 mm | ≤2 mm; GND_VEH |
| C603 | 10 µF | 3, VCC | 6.889 mm | cadena detrás de C604; GND_VEH |
| C607 | 10 nF | 16, VISOIN | 1.646 mm | ≤2 mm; GND_CAN |
| C608 | 100 nF | 16, VISOIN | **2.145 mm** | **excepción aceptada ≤2.15 mm**; GND_CAN |
| C610 | 220 nF | 19, VISOOUT | 1.682 mm | ≤2 mm; GNDISO_CAN |
| C606 | 10 µF | 19, VISOOUT | 4.292 mm | cadena detrás de C610; GNDISO_CAN |

### Verificación y pendientes para otras etapas
- **DRC: 0 errores**, 42 avisos: 37 `via_dangling` de masas pendientes de los planos, 2 `silk_overlap`, 2 `silk_edge_clearance`, 1 `lib_footprint_mismatch` conocido. **Paridad: 0**. Quedan **254 conexiones** para las etapas posteriores (288 al cierre de la etapa 1, 262 en el avance parcial).
- Ninguna conexión pendiente de BUS_CAN_H/L, CAN_TX/RX/STBY/SILENT, V_SOIN, V_SOOUT, GNDISO_CAN, CAN_RS o punto medio de C609. GND_CAN/GND_VEH y alimentación desde U301 al conjunto VIO esperan sus etapas previstas.
- Barrera CAN, U101_RTN, reserva de antena y sensores conservadas; ningún componente nuevo movido. Esquemáticos y `.kicad_dru` intactos. `.kicad_pro` revisado: únicamente orden de clases, contenido original conservado.
- Renders finales de ambas caras generados y revisados: `docs/layout/ruteo/etapa2-top.png`, `etapa2-bottom.png`. Reportes `etapa2-drc.json` y `etapa2-medidas.json`.
- `verify_etapa2.py` reconstruye caminos desde el PCB y comprueba límites de desacople, cadenas, continuidad de las cuatro señales lógicas, diferencia total ≤1 mm y exactamente dos vías en H / ninguna en L.
- **Etapa 5, C605:** conectar sin interrupciones su vía GND_VEH (144.28,121.9) con C602/C601 y GND de U601; añadir costura en esa zona y revisar cuellos/islas producidos por los saltos lógicos. No afirmar continuidad de plano antes de generarlo.
- **Etapa 5, CAN:** conservar continuidad GND_CAN alrededor de ambos extremos del puente H y coser la isla. No unir GNDISO_CAN directamente con GND_CAN: conservar FB602. Mantener libre la barrera y sin rellenos bajo U601.
- **Etapa 5, TP301:** plano continuo bajo el SW de U301, ya libre del antiguo pad/pista de prueba.


## Codex — etapa 2 aprobada, auditoría CAN y avance parcial de etapa 3

Inventario B.Cu y prueba de relleno temporal documentados en `RUTEO_TRASPASO.md`: una región GND_CAN, J1 y ocho vías conectados, DRC 0 errores, sin modificaciones de pistas CAN ni de reglas. No se agregaron planos al proyecto. `audit_can_bcu.py` reproduce la prueba y su figura.

Etapa 3 parcial mediante `etapa3_mcu.py`: UART, BOOT, EN local/C403, RESET remoto/TP401/U801/R802, 3V3 desde C304 al CAN y supervisor, retornos preparados. C401/C402/R401 y USB/VBUS quedan pendientes de las decisiones solicitadas y del ruteo final. No hubo movimientos ni cambios de esquemático. DRC 0 errores / 49 avisos, paridad 0, 240 conexiones pendientes. EN local 2.8519 mm entre centros; los ramales RESET remotos se informan aparte (62.8093 mm a SW401; 55.4803 mm a R802). Renders y mediciones parciales guardados. No se declara terminada la etapa 3; no iniciar etapa 4.


## Codex — etapa 3: decisiones aplicadas, escape USB pendiente

Aplicados los movimientos autorizados de C401/C402/R401 y C404 en esquema/PCB; coordenadas y MPN completos en `RUTEO_TRASPASO.md`. C404 debe replicarse en la copia manual, que no fue modificada. ERC sin errores; paridad 0, no fue necesario F8. QA visual del esquema exportado completa; `sch_visual_qa` no está disponible en esta sesión.

Ruteo y medidas completados salvo el cuello final de D− junto a U401. La prueba con 0.3 mm infringe clearance entre pads 14/15; se solicitó autorizar 0.15 mm por 1.923 mm. La copia temporal con ese cuello da DRC 0 errores, USB principal sin vías y diferencia nominal 0.0001 mm. El proyecto conserva ese enlace abierto hasta la respuesta: DRC 0 errores /59 avisos /224 conexiones pendientes. Los JSON distinguen medidas reales y propuesta. Renders de ambas caras actualizados. Etapa 3 sigue abierta; no se avanza a etapa 4.


## Codex — cierre final de etapa 3 (2026-10-29)

Aplicada la autorización del cuello D− de 0.15 mm durante 1.922754 mm, únicamente tres segmentos F.Cu del escape junto a U401. Ningún movimiento ni cambio de esquema adicional. El generador reproduce la solución y el verificador exige el USB completo en la placa guardada, sin usar la antigua propuesta temporal.

DRC 0 errores /57 avisos (52 vías GND de etapa 5 +5 conocidos), paridad 0, ERC 0 errores /5 avisos conocidos. Quedan 223 conexiones: 108 para etapa 4 y 115 de masas para etapa 5. USB D−/D+ 45.9509/45.9508 mm, diferencia 0.0001 mm, sin vías principales. C402 0.7750 mm, C404 0.5748 mm, EN–C403 1.5415 mm y EN–R401 4.9641 mm entre bordes. Tabla completa en RUTEO_TRASPASO.md y JSON final.

Renders finales de ambas caras generados y revisados. `.kicad_pro` revisado: solo orden de clases, se conserva el original después de comprobar equivalencia. Etapa 4 no iniciada; retoma sujeta a nuevo visto bueno. La tabla de componentes y C404 posterior a placement-v1 siguen pendientes de replicar por el usuario en ruteo-manual.
