# INCLI-VA — estado y pendientes

Leer al empezar cada turno y actualizar al terminarlo (ver "Trabajo entre agentes" en `AGENTS.md`).

Última actualización: 2026-10-30, Claude Code (TP de la cara inferior rotulados, TP406/TP505 GND con agujero, R803/R804 2.2 kΩ; antes: rótulos de J402 y J401; después de rc4, sin tag; **tag `pcb-v1-rc4`**: logo Volnyx en B.Silkscreen, ejes de la placa en F.Silkscreen, zona reservada para Hunter (rc5); rc3: fiduciales FID1–FID3, máscara roja; `bom/LCSC_BOM_COMPLETO_PROTO.csv`; sustitutos en el esquema y el PCB, tag `pcb-v1-rc2`; BOM con LCSC; **PCB integrado en `main`, tag `pcb-v1-rc1`**; ver «RETOMAR AQUÍ»).

## RETOMAR AQUÍ — PCB integrado en main (`pcb-v1-rc1`)
**2026-10-30:** el usuario aprobó el PCB. `ruteo-agente` (a7a2b9b) se integró en `main` con merge `--no-ff` (88860c5, sin conflictos; `origin/main` no tenía commits propios). Tag **`pcb-v1-rc1`** en ese commit. En `main`: árbol idéntico a `ruteo-agente`; DRC 0 errores / 3 avisos aceptados, 0 sin rutear, paridad 0; ERC sin cambios; `verify_etapa3/5` OK y con la misma salida. Después, la rama `ruteo-agente` se eliminó (local y en `origin`, con `-d`: estaba integrada). **El trabajo continúa en `main`.** `ruteo-manual` y `PCB_INCLI_VA_manual` siguen sin tocar; el worktree `PCB_INCLI_VA_bom` (`bom-sourcing`) se actualizó a `main` con fast-forward.

Estado del PCB (igual que en `ruteo-agente`): ruteo completo, con teardrops, planos rellenos y costura. DRC 0 errores / 3 avisos aceptados (abajo), 0 sin rutear, paridad 0. ERC 0 errores / 5 avisos conocidos (sin cambios). Fabricación de prueba en `fab/proto/`.

**Pedido a JLCPCB (prototipo, `pcb-v1-rc1`):**
- Archivo de placa: `fab/proto/INCLI-VA_gerbers.zip` (no versionado; idéntico byte a byte a `fab/proto/gerbers/` del tag `pcb-v1-rc1`, comprobado el 2026-10-30). Si falta, regenerarlo con `/usr/bin/python3 -B scripts/ruteo/etapa6_fab.py`.
- Opciones: **2 capas, FR4, 1.6 mm, cobre 1 oz, máscara roja (desde `pcb-v1-rc3`), acabado ENIG, sin panel (placa individual 100 × 100 mm), sin V-cut (fresado), con stencil.**
- Stencil: capas de pasta en `fab/proto/stencil/` (`INCLI-VA-F_Paste.gtp`, `INCLI-VA-B_Paste.gbp`, `INCLI-VA-Edge_Cuts.gm1`); son las mismas que van en el zip. Sin aperturas en los 12 DNP. La cara inferior solo tiene los 2 pads de C104: alcanza con stencil superior, y C104 se suelda a mano.

**Quedan:**
- [x] Hallazgo 2 (imán): resuelto, imán arriba con portaimán restringido. Ver «Revisión independiente», abajo.
- [x] Hallazgo 4 (courtyards): C401 y C508 movidos; C402–U401, C404, C507, C506 y 16 pares más aceptados como excepción. Ver «Revisión independiente», abajo.
- [x] **BOM con códigos LCSC** (Claude Code, 2026-10-30, rama `bom-sourcing`; agentic-sourcing solo para consultar con `jlc_lookup.py`, sin `sourcing.py`; no se hizo ningún pedido). Ver `docs/BOM_SOURCING.md`.
  - Sustitutos decididos por el usuario: Q101, Q102 y F101 **rechazados** (se compran los originales en DigiKey/Mouser y se sueldan a mano). C101, C201 y C104 sin AEC-Q200 **solo en PROTO**; PROD mantiene los originales. SCL3300-D01-10 aceptado: según Murata (Doc. 4921 Rev. 2, §9) es el carrete de 1000 u. ADM3055EBRIZ-RL, pasivos a Basic/preferred y sustitutos de igual especificación (incluida la tira 1×3 de J402, confirmada por el usuario): aceptados.
  - Lo que monta JLC: `fab/proto/bom_jlc_lcsc.csv` + `fab/proto/cpl_jlc.csv`, 60 líneas, 123 piezas (coinciden una a una). Se quitaron del CPL F101, Q101, Q102, L201 y U503.
  - A mano (5 placas + 1): `bom/A_MANO_PROTO.csv`. De LCSC: J1, J2, J401, J402 y U401 (carrito `bom/LCSC_CART_PROTO.csv`, USD 51.18). De DigiKey/Mouser: F101, Q101, Q102, L201 y U503 (`bom/DIGIKEY_MOUSER.csv`).
  - Componentes por placa: PROTO USD 111.48 (5 placas) / 90.88 (100); PROD 107.84 / 89.62, sin U701/U751.
- [x] **Sustitutos aceptados pasados al esquema y al PCB** (Claude Code, 2026-10-30, tag `pcb-v1-rc2`). Solo campos: `LCSC` en todos los componentes; `MPN_PROTO`, `LCSC_PROTO` y `Manufacturer_PROTO` (si cambia el fabricante) en los sustitutos de PROTO; `Notes` con compra y montaje. `MPN` (PROD) no cambió. `LCSC Part` (SW401, SW402) pasó a `LCSC`.
  - ERC por hoja idéntico al de antes: 0 errores, 5 avisos conocidos. `sch_visual_qa` no está disponible; la revisión semántica muestra que todos los campos nuevos están ocultos y no cambió nada fuera de las propiedades.
  - PCB: los campos se insertaron como texto en las 145 huellas (equivale a F8, solo campos). Antes de sincronizar, la paridad daba 145 `footprint_symbol_field_mismatch`; después, 0. No se usó `pcbnew.Save()`, porque reescribía todas las zonas y reordenaba `INCLI-VA.kicad_pro`. Fuera de las huellas, el archivo es idéntico. DRC 0 errores / 3 avisos aceptados, 0 sin rutear.
  - `etapa6_fab.py` usa los campos `_PROTO` y genera `bom_jlc_lcsc.csv`. Regenerado: `bom_jlc_lcsc.csv` y `cpl_jlc.csv` salen byte a byte iguales (60 líneas, 123 piezas). `bom_proto.csv` y `bom_jlc.csv` muestran ahora los MPN de PROTO, que coinciden con `bom/BOM_PROTO.csv`. Gerbers, drill y stencil: solo cambió la fecha (se conservan los de `pcb-v1-rc1`); el zip es idéntico a `fab/proto/gerbers/`.
- [ ] PROD: decidir si los pasivos Basic y los sustitutos de igual especificación de `bom/BOM_PROD.csv` pasan a `MPN` (hoy `MPN` conserva los originales AEC-Q200).
- [x] `scripts/ruteo/etapa6_fab.py` (Claude Code, 2026-10-30): `MANO` incluye F101, Q101, Q102, L201 y U503, y el script ya no borra `fab/proto/` entero, solo `gerbers/` y `stencil/`. Así conserva `bom_jlc_lcsc.csv`, que se mantiene a mano. Regenerado: `bom_jlc.csv`, `bom_jlc_lcsc.csv` y `cpl_jlc.csv` con 60 líneas, 123 piezas y las mismas designaciones. Gerbers, drill y stencil: solo cambió la fecha de creación de KiCad, así que se dejaron las versiones del commit anterior; los mapas de taladros salen iguales en texto y en render. `INCLI-VA_gerbers.zip` se rearmó con esos archivos y es idéntico byte a byte a `fab/proto/gerbers/`.
- [x] **`bom/LCSC_BOM_COMPLETO_PROTO.csv`** (Claude Code, 2026-10-30): BOM de PROTO para «Upload a BOM» de lcsc.com (LCSC Part Number, Quantity, Manufacturer Part Number, Description, Designator). 64 líneas, 2629 piezas. Cantidad = por placa × 6 (5 + 1 repuesto); pasivos 0402/0603 con un mínimo de 20; después se sube al MOQ (`minBuyNumber`) y al múltiplo (`split`) de lcsc.com. SW401 y SW402 van en una sola línea. Sin DNP y sin lo de DigiKey/Mouser. Script: `scripts/bom/lcsc_bom_completo.py` (consulta en vivo, solo lectura).
  - [x] Sin stock en lcsc.com (JLC sí tiene; son stocks separados): para la compra en LCSC se reemplazan C303 → C106245 CC0603JRNPO9BN100 (10 pF 50 V NP0 ±5 %) y C601/C607 → C100042 CC0603KRX7R9BB103 (10 nF 50 V X7R ±10 %), ambos de YAGEO. Estado «substitute … VERIFY» en `docs/BOM_SOURCING.md`. No cambian el esquema, el PCB ni la BOM de JLC. 64 líneas, 2679 piezas.
  - [ ] VERIFY: el usuario confirma los dos sustitutos de lcsc.com.
- [x] **`pcb-v1-rc3`** (Claude Code, 2026-10-30), sobre «update serigrafia» del usuario (b35e2bb):
  - Ese commit tenía DRC con 1 error nuevo (teardrop de USB_D+ contra la zona GND_VEH, 0.2488 < 0.25 mm): faltaban 5 teardrops (USB D±, +3V3_D, +3V3_A y SPI_SCK) y el relleno estaba viejo. Se resolvió volviendo a rellenar las zonas: 697 teardrops, los mismos de rc2. Las serigrafías del usuario se conservan.
  - **Fiduciales FID1–FID3** (`scripts/ruteo/etapa6_fiduciales.py`, idempotente): huella oficial `Fiducial_1mm_Mask2mm` en F.Cu, en (112.0, 55.5), (124.0, 144.5) y (189.0, 57.0): tres esquinas no alineadas, a ≥ 5.4 mm del borde y con ≥ 1.4 mm libres de cobre F.Cu, courtyards y serigrafía alrededor de la abertura, fuera del keep-out de la antena. Sin red, fuera del BOM y de la posición (JLC no los pide en el CPL: los toma de los Gerbers), referencia oculta en F.Fab. Símbolos `Mechanical:Fiducial` en la hoja raíz, con MPN/Manufacturer/Datasheet/Notes, para que F8 no los borre.
  - **Máscara roja:** JLCPCB (capacidades, 2026-10-30), cobre 1 oz: puente mínimo 0.10 mm para verde/rojo/amarillo/azul/morado (0.13 mm negro/blanco), abertura 1:1. Puentes medidos entre pads de distinta red (expansión 0): U502 0.15 mm, U301 0.15, J401 0.195, U101 0.25, U503 0.25, U401 0.37 mm. **Ninguno queda sin puente.** El más justo: U502 (margen 0.05 mm). Para pasar a 2 oz (mínimo 0.20 mm) habría que revisar U502 y U301.
  - DRC 0 errores / 3 avisos aceptados, 0 sin rutear, paridad 0; ERC 0 errores / 5 avisos conocidos; `verify_etapa3/5` OK. `fab/proto/` regenerado: cambian Gerbers, taladros y stencil (fiduciales y serigrafía del usuario); BOM y CPL quedan iguales (60 líneas, 123 piezas en JLC, sin FID). El zip coincide con `gerbers/`.
- [x] **`pcb-v1-rc4`** (Claude Code, 2026-10-30), con renders aprobados por el usuario:
  - **Logo Volnyx** (`docs/reference/logos/volnyx_wordmark.png`, no el ícono) en B.Silkscreen: huella `INCLI-VA:Logo_Volnyx_Wordmark` de 17.0 × 4.48 mm (`lib/INCLI-VA.pretty`), LOGO1 en (160.0, 121.5), arriba de «INCLI-VA Rev A» (que no se movió). Es solo de placa (F8 no la borra), está fuera del BOM y de la posición y no tiene referencia visible. Trazo: el 0.25 % de la tinta queda < 0.15 mm (borde escalonado y puntas de v/y/x); las letras tienen ~0.7 mm. Libre de TP, pads, vías, courtyards y arandelas H1–H5 (≥ 0.3 mm de las vías). Script: `scripts/ruteo/etapa6_logos.py` (`huella` / `placa X Y` / `reserva`).
  - **Ejes de la placa** en F.Silkscreen, origen (143.0, 87.5) (grupo `CLAUDE_ETAPA6_EJES`, `scripts/ruteo/etapa6_ejes.py`): sistema dextrógiro, +X a la derecha, +Y hacia arriba, ⊙Z sale de la cara superior. Flechas de 7 mm con trazo de 0.15 mm, rótulos de 1.0 mm. No pisan pads, vías ni el círculo del imán (Ø17.9 mm alrededor de U503). Transformaciones de U501/U502 en «Requisitos para el firmware».
  - DRC 0 errores / 3 avisos aceptados, 0 sin rutear, paridad 0; ERC 0 / 5 avisos conocidos; `verify_etapa3/5` OK. `fab/proto/` regenerado: cambian las serigrafías (los rellenos tienen áreas idénticas a rc3; en cobre, máscara y taladros solo cambian la fecha y el orden de los polígonos). BOM y CPL sin cambios.
- [x] **Rótulos de J402 (UART0)** (Claude Code, 2026-10-30, después de `pcb-v1-rc4`, sin tag): «TX», «RX» y «GND» (0.8 mm, trazo 0.15 mm) encima de cada pad, desde el punto de vista del ESP32, en F.Silkscreen y B.Silkscreen. Orden verificado con las redes del PCB (paridad 0): pad 1 = /40_mcu/U0TXD (pin 37 TXD0 de U401), pad 2 = /40_mcu/U0RXD (pin 36 RXD0), pad 3 = GND_VEH. «UART0 / 3V3» entre J402 y H4, en las dos caras, para que no le conecten un adaptador de 5 V. La referencia J402 pasa a vertical a la izquierda del pin 1; la L de pin 1 se ve arriba y se copió a B.Silkscreen (abajo también está el pad cuadrado). Nada pisa pads ni otra serigrafía; «TX» está 0.15 mm corrido a la izquierda por una vía GND tapada en (181.0, 143.0). Script: `scripts/ruteo/etapa6_serigrafia_j402.py` (grupo `CLAUDE_ETAPA6_J402`). DRC 0 errores / 3 avisos aceptados, paridad 0, ERC 0 / 5; `fab/proto/` regenerado (solo cambian las serigrafías).
- [x] **Rótulos de los otros conectores y pulsadores** (revisión del 2026-10-30): SW401 «RESET» y SW402 «BOOT» ya tienen rótulo y coinciden con sus redes; J1 (VIN/GND/CANH/CANL/GND_CAN) y J2 (DO1/DO2) tienen rótulos por pin en las dos caras. **J401 (USB-C):** agregado «USB» (0.8 mm, trazo 0.15 mm, F.Silkscreen) en (190.5, 75.4), arriba a la izquierda del conector y fuera del rectángulo SIN BARNIZ, a ≥ 0.25 mm de pads, vías y serigrafía (`scripts/ruteo/etapa6_serigrafia_usb.py`, grupo `CLAUDE_ETAPA6_USB`). DRC 0 errores / 3 avisos aceptados, paridad 0; `fab/proto/` regenerado (solo cambia F.Silkscreen).
- [ ] **Próximo tag `pcb-v1-rc5`:** cuando se agregue el logo de Hunter o antes de hacer el pedido (decisión del usuario).
- [x] **Puntos de prueba de la cara inferior** (Claude Code, 2026-10-30, sin tag; render aprobado por el usuario). Script `scripts/ruteo/etapa6_tp.py` (grupo `CLAUDE_ETAPA6_TP`, idempotente; rellena zonas, 697 teardrops):
  - Nombre de la señal junto a cada TP en B.Silkscreen (0.8 mm, trazo 0.15 mm, en espejo), verificado contra la red de cada pad: +VPROT, VBAT_F, GND, FLT (/PWR_FLT_N), +5V (TP201 y TP301, +5V_VEH), 3V3_D, 3V3_A, PG_3V3D (TP305; la red es PG_3V3D, no PG_3V3), EN (/MCU_RST_N), BOOT, VBUS, CAN_TX, CAN_RX, SCK, MOSI, MISO, INT1 (/IMU_INT1). Los GND (TP103, TP304, TP406, TP505) llevan recuadro. «TPxxx» va al lado; en TP305, TP405, TP501 y TP406 pasó a B.Fab (no entraba o confundía).
  - **TP406** (hoja 40_mcu, (166.5, 131.0), cerca de BOOT/RESET) y **TP505** (hoja 50_sensors, (162.5, 86.5), al norte de SCK): GND_VEH con agujero, `TestPoint_THTPad_D2.5mm_Drill1.2mm`, en la cara inferior, para el caimán del osciloscopio (admite un lazo de alambre o un Keystone 5001 soldado a mano). En el esquemático con su GND_VEH (#PWR490, #PWR590); fuera del BOM y de la posición. Fuera del imán, del área B, del keep-out de la antena y de las arandelas. TP505 se probó primero en (168, 109), pero ahí no entraba el rótulo.
  - Nota «CAN: medir vs GND_CAN (J1-5)» en B.Silkscreen, encima de «CAN AISLADO». **Bring-up:** el bus CAN (CANH/CANL, J1 pines 3–4) está del lado aislado del ADM3055E; medirlo con la masa del osciloscopio en GND_CAN (J1 pin 5), nunca en GND_VEH ni en TP103/TP304/TP406/TP505.
- [x] **LEDs D801/D802 con menos brillo** (Claude Code, 2026-10-30, sin tag): R803 y R804 pasan de 470 Ω a **2.2 kΩ** (un solo valor, una línea de BOM). PROTO: UNI-ROYAL 0603WAF2201T5E (C4190, JLC basic); PROD: Yageo AC0603FR-072K2L (C125931). Con Vf ≈ 1.95 V (verde) y ≈ 1.75 V (rojo) a ~1 mA (Lite-On LTST-C171KGKT rev. F / LTST-C171KRKT rev. E, fig. 2): verde ≈ 0.61 mA, rojo ≈ 0.70 mA desde 3.3 V. Solo cambian el valor y los campos; la huella sigue igual. BOM, CPL, `bom_jlc_lcsc.csv` y `LCSC_BOM_COMPLETO_PROTO.csv` regenerados (siguen 60 líneas en JLC).
- [ ] **Logo Hunter → rc5.** Falta `docs/reference/logos/hunter.svg` (o `.png`; si es a color, pasarlo a blanco y negro con buen contraste). **Zona reservada** en la cara inferior: rectángulo de 16 × 6 mm centrado en (123.5, 106.5), marcado en User.Comments (grupo `CLAUDE_RESERVA_HUNTER`, no se fabrica). Es el único hueco de ese tamaño en la cara inferior: libre de TP, pads, vías, courtyards, serigrafía y arandelas con 0.3 mm de margen, y arriba de BARRERA_CAN. Un logo cuadrado entraría de ~6 × 6 mm. Usar `etapa6_logos.py` y mostrar el render de la cara inferior antes de fijarlo.
- [ ] Pedido: U601 ADM3055EBRIZ-RL tiene solo 55 u en JLC. Para PROD, comprar en DigiKey/Mouser lo de `bom/DIGIKEY_MOUSER.csv` (`Uso` = PROD).
- [ ] **Revisión independiente** con kicad-happy u otro revisor (solo informe). La de 2026-10-30 se hizo con scripts propios porque kicad-happy no estaba instalada.
- [ ] **Comparación con `ruteo-manual`** (trabajo del usuario en `PCB_INCLI_VA_manual`): decidir qué se conserva de cada ruteo. La lista de cambios a replicar está en «Replicar en `ruteo-manual`», abajo.
- [ ] Confirmar en la vista previa de JLC las rotaciones de `cpl_jlc.csv`, en especial las familias sin regla en la tabla (quedan en la rotación de KiCad): LGA-14 (U502), DFL-12 (U501), SOT-563 (U301), diodos SMx/SOD-123, LED 0805 y SW-SMD; y C104 en la cara inferior (ensamblado de dos caras, costo extra).
- [ ] Esquema, hoja 60 (anterior a este turno): `sch_visual_qa` avisa que #PWR032 se superpone con R601 (~3.2 mm²). Solo legibilidad.

**Antes de tocar el PCB:**
1. Leer `AGENTS.md`, `docs/RUTEO_TRASPASO.md` («Cómo retomar» y «Etapa 6 — Cierre») y `git log -5`.
2. KiCad cerrado, sin archivos `~*.lck` (también en `sheets/`). `git status` limpio.
3. No tocar `PCB_INCLI_VA_manual`, la rama `ruteo-manual` ni `PCB_INCLI_VA_bom`. No ejecutar `git worktree remove/prune`.
4. No mover piezas ni editar el esquema, las reglas o las net classes sin preguntar.
5. Antes de cada commit, revisar `git diff INCLI-VA.kicad_pro`. Si solo cambió el orden de las net classes, restaurarlo con `git checkout INCLI-VA.kicad_pro`.
6. **No volver a ejecutar** `etapa1_potencia.py` ni `etapa3_mcu.py`: este último recrearía la rama sur de VBUS que encierra el GND de C404. Son idempotentes y se encadenan así si se cambia cobre: `etapa5_planos.py` → `etapa6_costura_u401.py` → `etapa6_teardrops.py` (rellena zonas) → DRC → `etapa6_fab.py`.
7. Skills: agentic-sourcing solo para consultar (`jlc_lookup.py`) y solo si el usuario lo pide. kicad-happy solo para revisar e informar hallazgos, sin aplicarlos. Avisar antes de usar cualquier otra skill.

**Etapa 6 — lo hecho (Claude Code, 2026-10-30):**
- Retornos de corriente revisados, sin hallazgos nuevos: plano B.Cu bajo U201/L201 al 99.6 % y bajo U301/L301 al 98.6 %; barrera de U601 sin cobre; GND_CAN y GND_VEH, una isla cada una; U101_RTN aislada.
- Teardrops: `etapa6_teardrops.py`, 697 zonas. `verify_etapa5.py` ignora las zonas teardrop en el cálculo de islas.
- **Tramos sin plano debajo: aceptados por el usuario** (registro en `docs/layout/ruteo/etapa5-islas.json`, `ranuras_bajo_senal_mm`): INT2 9.2 mm, INT1 7.4 mm, USB D− 9.1 mm, D+ 6.9 mm, MCU_RST_N 6.4 mm, VS 6.3 mm, DGATE 5.8 mm.
- **Avisos del DRC:**
  - `silk_overlap` Q101 y U801: **corregidos** moviendo solo la referencia (componentes sin mover). Q101: horizontal en (117.62, 95.3), bajo el cuerpo, porque entre las serigrafías de Q101 y Q102 hay 1.12 mm y el texto ocupa 1.46. U801: de (166.0, 134.2) a (166.0, 133.6), separada de la marca de pin 1.
  - **Excepciones aceptadas por el usuario:** 2 `silk_edge_clearance` de U401 (JLC recorta la serigrafía cerca del borde) y `lib_footprint_mismatch` de U401 (recorte intencional de la huella).
- **Ranura del haz B.Cu bajo U401** (DO1/DO2 EN/DIAG, PWR_FLT_N, LED_G/LED_R; detalle en `docs/layout/ruteo/etapa6-ranura-u401.json`, script `verify_ranura_u401.py`):
  - Largo 46.9 mm (y 77.9–124.7, x 173.5–184.1). Ancho 2.3–4.9 mm (mediana 3.7); hasta 9.9 mm en los abanicos de los extremos.
  - Sobre la ranura, GND F.Cu continuo de borde a borde en 268 de 469 filas de 0.1 mm (y 88.2–96.6, 98.9–100.1 y 108.6–121.8, sobre todo).
  - Pistas F.Cu que la cruzan: el par USB D+/D− (diagonal y 80.5–89.7; es el cruce autorizado en la etapa 4, con GND F.Cu al costado en el 76–100 % del cruce), los quiebres F.Cu de las propias redes del haz (DO2_EN, DO2_DIAG, LED_G, LED_R y PWR_FLT_N, en y 79.6–82.8), VAR_ID2 (2.5 mm) y los tramos de pad de la fila de U401 (1.5 mm cada uno).
  - Costura: 13 vías GND nuevas (grupo `CLAUDE_ETAPA6_COSTURA`, `etapa6_costura_u401.py`). Paso máximo: 3.3 mm al este; 6.0 mm al oeste solo en y 95–101, donde F.Cu no tiene GND (meandro de USB D+ y USB D−). Ahí no va vía, por el criterio del usuario («donde haya cobre GND en F.Cu»).
  - Pad central de U401: 12 vías a B.Cu, que llegan al plano principal (7099 mm²).
- Fabricación de prueba (`etapa6_fab.py` → `fab/proto/`, regenerada tras la costura): gerbers y drill PTH/NPTH con mapa, `stencil/`, `bom_proto.csv`, `pos_kicad.csv` y, desde la revisión independiente, `bom_jlc.csv`/`cpl_jlc.csv` (abajo). BOM: 70 líneas, 133 piezas (145 − 12 DNP). `INCLI-VA_gerbers.zip` no se versiona (`.gitignore`: `fab/**/*.zip`; en el commit anterior había entrado por error).
- Renders finales: `docs/layout/ruteo/etapa6-top.png` y `etapa6-bottom.png`.

**Revisión independiente (Claude Code, 2026-10-30, solo scripts propios: kicad-happy no disponible) — lo resuelto:**
- **1. Stencil sin DNP:** `etapa6_fab.py` plotea F.Paste/B.Paste (en `gerbers/` y en `stencil/`) desde una copia temporal del PCB, fuera del proyecto, sin pasta en los pads de las 12 piezas DNP (C105, D601, D703, D753, R708–R710, R758–R760, R801, R807). Verificado: 0 pads DNP con apertura. Cobre, máscara y taladros: idénticos a los del commit anterior.
- **5. Notes de C602:** corregido en el esquema (hoja 60) y en el PCB: en cadena detrás de C601, a ~6 mm del pin VIO, ubicación aceptada. ERC de la hoja 60: 0.
- **10. Marca de cátodo:** «K» de 0.8 / 0.15 mm en F.Silkscreen junto al pad 1 de D101, D102, D103, D701 y D751, fuera del cuerpo, sin pisar pads ni otra serigrafía (`etapa6_serigrafia_catodo.py`, grupo `CLAUDE_ETAPA6_SILK`, idempotente). Texto de placa, no de huella: no agrega `lib_footprint_mismatch`. DRC sin avisos nuevos.
- **7. Teardrops bajo U601: registrado como verificado.** La regla `ISO_sin_relleno_bajo_U601` no ve los teardrops, y ampliarla marcaría como error los 29 teardrops legítimos de los extremos exteriores de los pads. `verify_etapa5.py` comprueba ahora `U601_teardrops_entre_filas`: 0 teardrops en la franja entre filas (7.25 mm entre bordes interiores de pads).
- **CPL (JLC ensambla parte):** `cpl_jlc.csv` y `bom_jlc.csv` (65 líneas, 128 piezas) sin los THT (J1, J2, J401, J402) ni U401, que se sueldan a mano; `bom_proto.csv` sigue siendo la BOM completa de compra (70 líneas, 133 piezas). `cpl_proto.csv` desaparece. Rotación corregida por familia (JLCKicadTools `cpl_rotations_db.csv`): SOT-23/-5/-6 −90°, SOIC 270°, TSSOP 270°, CP_Elec_10x10 180°, y VQFN-24 de U101 270° (regla propia, por analogía con QFN). Ángulos llevados a 0–359°. Posición = centro de los pads (Q101 y Q102 se corren 0.84 mm; el resto coincide con el origen).
- **Aceptados por el usuario:**
  - **6.** H5 con tornillo o inserto de inoxidable A2/A4, latón o nylon, nunca acero (está a 9.77 mm del eje del imán). En «Requisitos para la caja».
  - **8.** Par CAN asimétrico: CAN_H salta 3.8 mm por B.Cu (2 vías), CAN_L todo en F.Cu. Sin efecto a la velocidad de CAN clásico.
  - **9.** C104 (cara inferior) a ~1.6 mm del borde izquierdo, con el courtyard sobre el borde. En «Requisitos para la caja»; el pedido a JLC va **sin V-cut** (fresado).

**Revisión independiente — hallazgos 2 y 4 (decisiones del usuario, 2026-10-30):**
- **2. Imán:** va **arriba** (F.Cu). U501, C503 y TP502 no se mueven. El cuerpo de U501 (8.8 × 8.2 mm medido en su serigrafía; la huella easyeda no tiene F.Fab) queda a 4.88 mm del eje, no 7.54 como decía el primer informe. Restricciones del portaimán en «Requisitos para la caja».
- **4. Courtyards:** de los 6 movimientos aprobados, probados uno por uno con el DRC real (copia aislada, zonas rellenas), **solo C401 se aplicó**: (189.2, 100.6) → (189.2, 99.8), `etapa6_mover_pasivos.py`, tramos de reconexión en el grupo `CLAUDE_ETAPA6_MOV`. C401–C402 pasa de 0.23 a 1.03 mm y C403–C401 de 0.51 a 0.73 mm. DRC 0 errores.
  - **C402 no se movió:** para 0.5 mm de courtyard con U401 habría que alejarlo 0.22 mm, y la pista al pin 3V3 pasaría de 1.98 a ~2.2 mm, por encima del límite de ≤ 2 mm del usuario. C402–U401 (courtyard 0.28 mm, pads a 0.78 mm) queda como **excepción**, pendiente de confirmación.
  - **C508 movido en lugar de R502** (aprobado por el usuario): (168.7, 90.3) → (167.9, 90.3). R502–C508 pasa de 0.23 a 1.03 mm. R502 no se pudo mover: su pad CS_IMU caía sobre el tronco +3V3_A (x 172.3).
  - **Excepciones aceptadas por el usuario** (no se pueden mover sin rerutear pistas de otras redes):
    - C402–U401: courtyard 0.28 mm, pads a 0.78 mm. Pista al pin 3V3 de 1.98 mm (límite ≤ 2 mm).
    - C404–U402: courtyard 0.09 mm, pads a 0.58 mm. Moverlo choca con USB D±. Pista a VBUS de U402: 1.68 mm.
    - C507–U503: courtyard 0.13 mm, pads a 0.63 mm. Moverlo choca con el tronco +3V3_A (x 144.3).
    - C505–C506 (courtyard 0.26 mm, pads a 0.76 mm) y U502–C506. Moverlos choca con IMU_INT1/INT2 y +3V3_A. **U502–C506: los 0.23 mm son entre courtyards; entre pads y entre aperturas de pasta hay 1.17 mm**, así que no hace falta ajustar el stencil de C506.
    - Los 16 pares con ≥ 0.86 mm entre pads (incluido el grupo de desacoples CAN C601–C605).

**Pendientes fuera del ruteo:**
- Verificar los MPN marcados «a verificar» antes de la BOM final. Confirmar el stock de C105 PROD (EEE-FK1H102AV).
- SCL3300 (DFL-12): revisar la huella para producción; los pads son 0.32 mm más largos que el land pattern.
- C104 va en B.Cu: la caja necesita separadores de ≥ 12 mm y adhesivo.
- Firmware: U503 está girado 180°, lo que da un desfase fijo de 180° (compensar con ZPOS). La velocidad CAN se define en firmware. El modo SPI de cada sensor está en «Requisitos para el firmware».
- Imán de ROT arriba (F.Cu), con portaimán de Ø ≤ 8.7 mm o cara a ≥ 3.8 mm de la placa (ver «Requisitos para la caja»).

**Replicar en `ruteo-manual`** (lo hace el usuario; detalle en `RUTEO_TRASPASO.md`):
- Movimientos de las etapas 1–4 (sección 3, «Cambios de ubicación»).
- Etapa 6: teardrops, costura `CLAUDE_ETAPA6_COSTURA` junto al haz bajo U401 y referencias de Q101/U801 movidas.
- Revisión independiente: C401 de (189.2, 100.6) a (189.2, 99.8) y C508 de (168.7, 90.3) a (167.9, 90.3), con sus tramos de reconexión (grupos `CLAUDE_ETAPA6_MOV`), y las «K» de cátodo de D101–D103, D701 y D751 (grupo `CLAUDE_ETAPA6_SILK`).
- C404 nuevo.
- Desvío de RESET.
- Giro de U503 y movimientos de los pasivos de sensores.
- Cambio de VBUS/C404 de la etapa 5.
- Zonas `E5_*` y las reglas `Planos_*` del `.kicad_dru`, si se quieren los mismos planos.

**Verificación rápida (sin modificar el PCB):**
```bash
kicad-cli pcb drc --schematic-parity --severity-all --format json -o /tmp/drc.json INCLI-VA.kicad_pcb
kicad-cli sch erc --severity-all --format json -o /tmp/erc.json INCLI-VA.kicad_sch
/usr/bin/python3 -B scripts/ruteo/verify_etapa3.py > /tmp/v3.json
/usr/bin/python3 -B scripts/ruteo/verify_etapa5.py > /tmp/v5.json
```

## Etapa 5 cerrada (planos) — Claude Code, 2026-10-30
- **Cerrado:** zonas GND_VEH (B.Cu en toda la placa, F.Cu donde cabe), GND_CAN (ambas caras, solo dominio aislado) y U101_RTN (isla B.Cu), rellenas y guardadas. 321 vías de costura. DRC 0 errores / 5 avisos conocidos, **0 sin rutear**, 0 `via_dangling`, paridad 0, ERC sin cambios, `verify_etapa3.py` OK. Detalle en «Etapa 5 — cierre: planos» de `RUTEO_TRASPASO.md`.
- **Pendientes de la etapa 4 resueltos:** 17 islas F.Cu de sensores (cosidas o eliminadas), isla B.Cu de ~137 mm² bajo la supervisión (vías junto a C309/R306), retorno de INT1/INT2 bajo el módulo, costura junto a C605.
- **Cambio autorizado:** rama sur de VBUS (etapa 3) reemplazada por un enlace B.Cu entre las vías VBUS de J401, para sacar el GND de C404, que estaba encerrado. No volver a ejecutar `etapa3_mcu.py`.
- **Reglas nuevas en `INCLI-VA.kicad_dru`:** `Planos_conexion_solida` y `Planos_un_rayo` (seis pads GND con un solo rayo térmico).
- **Para la etapa 6:** revisar las ranuras listadas (INT1/INT2 bajo la fila de pads del módulo, USB en el cruce del bus, MCU_RST_N); teardrops; fabricación de prueba.
- **Replicar en ruteo-manual:** cambio VBUS/C404 y, si se quieren los mismos planos, zonas `E5_*` y reglas nuevas.

## Etapa 4 cerrada (sensores) — Claude Code, 2026-10-30
- **Cerrado:** sensores con la opción C aprobada (GPIO actuales sin cambios, esquema intacto). U503 girado 180°, C501/C502 girados, C505/C506/C508/R502/R501/R503/C507 y TP501–TP504 reubicados (tabla en «Cambios de ubicación» de `RUTEO_TRASPASO.md`); referencias de serigrafía reubicadas. 12 cruces B.Cu numerados, con costura GND. DRC 0 errores (sin avisos nuevos de serigrafía), paridad 0, ERC 0 errores / 5 avisos conocidos, `verify_etapa3.py` OK. Quedan 132 conexiones, todas de masa (etapa 5).
- **Excepciones aceptadas por el usuario:** cruce 12 (+3V3_A → TP303) de 3.6 mm; tres vías GND dentro del círculo del imán, tapadas en ambas caras; tronco +5V a 7.6 mm del cuerpo de U503 (cifra corregida, antes 9.8 mm).
- **Firmware:** U503 girado 180° → desfase fijo de 180° en el ángulo, sin inversión del sentido de giro; se compensa con el registro ZPOS o en la calibración del cero (ver «Requisitos para el firmware»).
- **Para la etapa 5:** eliminar o coser las 17 islas F.Cu del grupo de sensores y la isla B.Cu de ~137 mm² bajo la supervisión (vías GND junto a R306/R308/C309/C310).
- **Replicar en ruteo-manual:** giro de U503 y movimientos de pasivos/TP de sensores, además del desvío de RESET.
- La reasignación de GPIO del SPI (pendiente anterior) queda **descartada**: el usuario eligió la opción C.

## Etapa 4 parcial — Claude Code, 2026-10-30 (histórico)
- **Cerrado:** periféricos de U101, desvío de RESET bajo el módulo (autorizado), bus DO/PWR_FLT/LED bajo el módulo con un único cruce del par USB (autorizado), DO1/DO2, +5V a las salidas, LED, VAR_ID, WDI, VMON, R305/R307 y PG_3V3D. DRC 0 errores, paridad 0, ERC sin cambios, `verify_etapa3.py` OK. Detalle en «Etapa 4 — avance parcial» de `RUTEO_TRASPASO.md`.
- **A medias (cerrado después):** sensores (39 conexiones: SPI/CS, INT1/INT2, +3V3_A, SCL_AEXTC/DEXTC).
- **Descartado (el usuario eligió la opción C):** reasignar los GPIO del SPI (pines 17–22, IO9–IO14, y quizá INT1/INT2) para que el SPI se rutee todo en F.Cu sin nada en B.Cu debajo. Antes de editar el esquema hay que mostrar al usuario el intercambio exacto y la verificación de ruteo. Requiere ERC y una nota para firmware (algunas señales pasan de IOMUX a la matriz GPIO).
- **Aplicado en el cierre de la etapa 4:** girar 180° C501 y C502; reubicar C505, C506, C508, R502 y TP504 (≤5 mm de U502). Hay que replicarlo en ruteo-manual junto con el desvío de RESET.
- Reglas del usuario para este turno: no usar la skill agentic-sourcing; en etapa 6 usar kicad-happy solo para reportar hallazgos; avisar antes de usar cualquier otra skill.


## Protección del trabajo manual — Codex, 2026-10-29
- Añadida en `AGENTS.md` la regla solicitada por el usuario que reserva `PCB_INCLI_VA_manual` y `ruteo-manual` al usuario y prohíbe intervenir sobre ellas o ejecutar `git worktree remove/prune` salvo pedido explícito. Cambio documental completado, sin nuevos pendientes.

## Etapa 3 — cierre actual (`a881797`)
- Etapa 2 aprobada y auditada. Solo etapa 3 autorizada; no comenzar etapa 4.
- Decisiones del usuario aplicadas: C402 primero junto a 3V3, C401 detrás, R401 junto al RC de EN; posiciones en «Cambios de ubicación» de `RUTEO_TRASPASO.md`.
- **Cambio de esquemático posterior a placement-v1, para replicar en ruteo-manual por el usuario:** añadido **C404**, hoja 40, 100 nF, 0603, X7R, 50 V, `GCM188R71H104KA57D` (Murata), DNP vacío, VBUS–GND_VEH. Símbolo en (365.76,63.5), PCB F.Cu (189.6,81.45) r0. Huella oficial `Capacitor_SMD:C_0603_1608Metric`; campos completos. Incorporado al PCB con el path correcto, **paridad 0; no hace falta F8**. No se tocó la copia manual.
- Ruteados 3V3 al MCU/CAN, desacoples, EN/R401/C403, RESET completo, BOOT, UART, CC1/CC2 y VBUS/C404/TP403. Las cuatro vías USB autorizadas están solo en los ramales B6/B7.
- **Excepción autorizada y aplicada:** cuello D− a 0.15 mm × 1.922754 mm junto a U401, clearance ≥0.2 mm. USB principal completo y sin vías: D−/D+ 45.9509/45.9508 mm, diferencia nominal 0.0001 mm. Las cuatro vías se limitan a ramales B6/B7.
- PCB guardado: **DRC 0 errores /57 avisos** (52 vías de masas +5 conocidos), **paridad 0**, **223 conexiones pendientes**: 108 de etapa 4 y 115 GND de etapa 5. No quedan extremos USB abiertos.
- ERC: **0 errores /5 avisos conocidos**; hoja 40: 0 errores /4 avisos de SW401/SW402. `sch_visual_qa` no está disponible en esta sesión; revisión visual de hoja completa y sector USB/C404 sin solapes nuevos. Evidencia `etapa3-erc.json`, `etapa3-hoja40.png`, `etapa3-c404-esquema.png`.
- Tabla de mediciones y posiciones en `RUTEO_TRASPASO.md`; renders y medidas finales en `docs/layout/ruteo/etapa3-*`. C402 0.775 mm al pin; C404 0.575 mm; R401 4.964 mm a EN (distancias entre bordes de pads).
- Cierre completado: DRC, paridad, ERC, renders y mediciones. **No iniciar etapa 4 sin visto bueno.** Leer «Cómo retomar» al inicio de `RUTEO_TRASPASO.md`; incluye inventario de redes, excepciones, cambios a replicar y comandos. `preview_usb_escape.py` queda como archivo histórico; usar `verify_etapa3.py` para comprobar la placa entregada.
- El detalle que sigue conserva el historial anterior.

## Retoma de ruteo — histórico de etapa 2, Codex, 2026-10-29
- Base: `b46f185`, rama `ruteo-agente`; solo etapa 2 autorizada. Etapas 3–6 esperan nuevos vistos buenos.
- Registrada la línea de continuidad en `AGENTS.md` y las decisiones del usuario en `docs/RUTEO_TRASPASO.md`.
- U503: medir 10 mm desde el borde del cuerpo; excepción del tronco +5V existente a 9.8 mm (corregido 2026-10-30: mínimo 7.6 mm en la esquina (147.3,110.6)).
- TP301: traslado aplicado de (140,134) a (140,131.6), B.Cu, sobre el tronco +5V y fuera del SW; retirada la bajada anterior. Registrado en «Cambios de ubicación».
- ROT: mantener libre Ø17.9 mm en ambas caras. C105 PROD: confirmar stock en BOM, sin bloquear el ruteo.
- R602/R603/C609 montadas en PROTO; PROD según instalación.
- Desacoples U601: ≤2 mm para C601/C604/C607/C610; excepción aceptada C608 = 2.145 mm (≤2.15 mm); C602/C603/C606 en cadena detrás del pequeño, sin derivación independiente y con retorno corto a su masa. Conservar ubicación y valores (C602 es 100 nF). C606/C610 retornan a GNDISO_CAN antes de FB602.
- Usuario confirmó cierre completo de KiCad; comprobada ausencia de bloqueos antes de editar. Esquemáticos intactos. Solo TP301 cambia de ubicación; net classes y reglas conservadas.
- Fuente aislada, desacoples en cadena, CAN_RS y CAN_TX/RX/STBY/SILENT completos hasta U401, con TP404/TP405 y resistencias. El riel +3V3_D desde U301 y los planos siguen en sus etapas previstas.
- **Etapa 2 terminada:** DRC 0 errores / 42 avisos (37 vías de masas pendientes de planos + 5 conocidos), paridad 0, 254 conexiones pendientes para las etapas posteriores. Renders, DRC y medidas finales en `docs/layout/ruteo/etapa2-*`; detalle en `docs/RUTEO_AGENTE.md`.
- **Decisiones resueltas:** C608 aceptado a 2.145 mm. Evaluado giro de D601 a 180°: traslada la inversión al acceso desde J1; se conserva r0 y se aplica el puente CANH autorizado, recto de 3.844 mm en B.Cu, con dos vías. CANL sin vías. Terminación completa.
- **Longitudes principales J1→U601:** H 22.2139 / L 22.2120 mm, diferencia nominal 0.0019 mm incluyendo 1.6 mm por vía (ajuste de altura ya activo en el proyecto). Los ramales a terminación se miden aparte.
- **Etapa 5, C605:** asegurar plano GND_VEH continuo y costura local entre su vía (144.28,121.9), C602/C601 y GND de U601; su camino VIO mide 12.270 mm. Revisar además continuidad GND_CAN alrededor del puente H y plano bajo SW de U301 tras mover TP301.
- Cierre de etapa 2: DRC, paridad, renders de ambas caras, tabla final de desacoples y CAN completados; `.kicad_pro` revisado y conservado. Commit y push del cierre de este turno. **Esperar aprobación antes de etapa 3.**

## Criterio general (decisión del usuario, 2026-10-27)
- **El prototipo es el mismo diseño que irá a producción.** Entre prototipo y producción solo cambia qué se monta.
- Requisitos de producción: vehículos de 12 V y 24 V, chasis con vibración, transitorios ISO 7637-2 / ISO 16750-2 y CAN robusto.
- Lo opcional va con huella en la placa y marcado DNP. La placa funciona igual con o sin esas piezas (0 Ω donde haga falta).
- **Campo `DNP`** en todos los símbolos, para sacar los dos BOM del mismo esquemático:
  - vacío: se monta en prototipo y en producción.
  - `PROTO`: no se monta en el prototipo (sí en producción).
  - `PROD`: no se monta en producción.
  - `PROTO,PROD`: huella reservada; no se monta en ninguno.
  - El atributo nativo `dnp` de KiCad refleja el BOM de prototipo (`dnp yes` si el campo contiene `PROTO`).
  - Las variantes (CAN, OUT, ROT, CABIN) siguen en el campo `Variant`; no se mezclan con `DNP`.

## Decisiones del usuario (2026-10-27)
1. **Load dump:** se diseña para load dump **suprimido** (ISO 16750-2 prueba B; 24 V: ≤ 58 V). Se mantiene el TVS de entrada D102 para ISO 7637 (pulso 1).
   - **Sin TVS de entrada grande** (decisión final del usuario): la entrada ya bloquea 202 V (Q101 250 V, D101 400 V, C101 450 V). Detalle en "Máximos de la entrada".
2. **R109 queda en 1.62 k** (corte por OV a 38.4 V). Decisión final del usuario: con el buck de 80 V ya no hace falta bajarlo.
3. **Opción B, no aislada: aprobada.** Se quitan PS201, U202 (ISO7763) y U201 (TPS7A1650), y entra un buck de +VPROT a 5 V. El aislamiento queda solo en el CAN (ADM3055E).
   - **Buck: TI LMR38010SQDDARQ1** (80 V, 1 A, PFM + spread spectrum, AEC-Q100, HSOIC-8 PowerPAD DDA). El usuario confirma el stock.
   - **Prototipo: LMR38010SDDAR** (LCSC C5219310), equivalente comercial. En el símbolo: `MPN = LMR38010SQDDARQ1` (PROD) y `MPN_PROTO = LMR38010SDDAR` (ver "Equivalencia LMR38010").
   - Si la producción termina en JLCPCB, se revisa la disponibilidad más adelante.
   - Huella: pad expuesto con vías térmicas, soldable con aire caliente.
8. **C105:** DNP en PROTO y montado en PROD (hold-up para load dump y arranque en frío). De acuerdo, con dos condiciones (ver "Hoja 20: diseño listo").
4. **60_can: aprobado y aplicado** (ver "Hecho en este turno").
5. **DO mínima: aprobada y aplicada.** El latch y el diagnóstico quedan como huellas DNP.
6. **J1 y J2:** Phoenix MSTB 2,5 de 5.08 mm con brida roscada (GF). **Aplicado.**
7. **C105:** reemplazada por la decisión 8.

## Decisiones del usuario (2026-10-29)
Cerradas; antes figuraban como abiertas.
- **Serigrafía:** aprobados los rótulos de zona, el pinout de J1/J2 y la línea de barrera CAN. El usuario reubicó parte de la serigrafía en `b2d4f4a` (sin cambios de componentes).
- **Rigidez de los sensores:** se quedan las dos, H5 (opción A, M3 en 156.0, 88.5) y el área B reservada (Ø8 mm en B.Cu).
- **CAN:**
  - R605 = 0 Ω (pendiente completa).
  - La velocidad del bus (250/500 kbit/s) se define en el firmware.
  - Se monta en las variantes con CAN según la tabla VAR_ID; en las demás es DNP (campo `Variant = CAN`).
- **VAR_ID:** 2 bits, (ID1 ID0) = 11 base / 10 CAN / 01 solo DO / 00 CAN + DO, con resistencias de 0 Ω (R805/R806). R807 queda DNP, reservada para CABIN, que **no entra en esta revisión**. El esquemático ya coincide (verificado).
- **LED:** D801 y D802 montados en PROTO y DNP en PROD. La caja es opaca, sin light pipe. El esquemático ya coincide.
- **Fabricación:** 2 capas, JLCPCB. El prototipo se arma en la variante CAN + DO + ROT.
- **ASM330 (LGA):** lo suelda el usuario con aire caliente y stencil. Pedir el stencil a JLCPCB.
- **Conformal coating: sí.** Zonas a enmascarar (J1, J2, J401 y J402) dibujadas en `User.Comments`, con el rótulo "SIN BARNIZ" en F.Silkscreen. Se asume PD1 bajo el barniz; las distancias de la `.kicad_dru` (PD2) quedan con margen.
- **Imán de ROT:** arriba (F.Cu), frente a U503; preferido portaimán de Ø ≤ 8.7 mm; alternativa: mayor, con la cara a ≥ 3.8 mm de la placa (air gap 2.6–3.0 mm). Detalle en «Requisitos para la caja». H5 no magnético (inoxidable A2/A4, latón o nylon).
- **Mecánica:** la caja todavía no está diseñada. Sus requisitos quedan en "Requisitos para la caja".

## Hecho en este turno (2026-10-27)
- **`60_can`** (ADM3055E, datasheet ADI Rev. D, tablas 10 y 12):
  - FB602 estaba en corto (sus dos pines en GND_CAN). Ahora GNDISO (pines 18 y 20) va a GND2 a través de FB602, como pide el datasheet.
  - Desacople corregido según la tabla 10:
    - VISOOUT: C610 de 0.22 µF + C606 de 10 µF a GNDISO.
    - El 10 µF que estaba en VISOIN (C11) pasó a VISOOUT.
    - Se quitó el 10 µF duplicado en VCC (C6).
  - **C601 y C607 (0.01 µF) se mantienen**, aunque se había aprobado quitarlos: el datasheet los exige en VIO y VISOIN ("requires 0.01 µF and 0.1 µF").
  - RS (pin 12) → R605 de 0 Ω a GND2: velocidad completa. Con 47 k pasa a control de pendiente.
  - AUXIN (pin 9) → GND1, porque es una entrada sin uso. AUXOUT (pin 17) sin conexión.
  - STBY: pull-up R604 de 10 k a +3V3_D. STBY y SILENT tienen pull-down interno; con R604 el transceiver arranca en standby.
  - D601 ESD2CAN24-Q1 (SOT-23) en CANH/CANL, DNP en prototipo y en producción. Símbolo genérico `D_TVS_Dual_AAC`, pin 3 = GND.
  - Referencias renumeradas a 6xx. Footprint, MPN, Manufacturer, Datasheet y Notes completos en los 18 componentes.
  - Los símbolos de potencia `power:VCC` y `power:GND` con el Value editado se cambiaron por los de la librería `INCLI-VA`.
  - PWR_FLAG en V_SOIN (alimentado por VISOOUT a través de FB601).
- **`70_output`** (DO1 y DO2), diseñado para load dump suprimido:
  - Q701: FDD7N25LZ (250 V, DPAK) → **DMN10H220LQ-7** (100 V, SOT-23, AEC-Q101).
  - D701: SMCJ188A → **SMAJ58A**. No conduce con 58 V; recorta el pico inductivo a ≤ 93.6 V, por debajo de los 100 V de Q701.
  - **U701 74AHCT1G126** (nuevo): lleva EN de 3.3 V (MCU) a EN_5V, porque el DMN10H220LQ especifica su RDS a 4.5 V. R711 de 100 k es el pull-down de la entrada. C702 desacopla.
  - **D704** (nuevo): zener de 12 V, MMSZ5242B, como protección de gate (VGS máx ±16 V).
  - Latch de sobrecorriente (Q702, Q703, D702, R704–R707, C701): `DNP = PROTO,PROD` hasta validar el disparo (REVISION_CODEX I1). R701 (1 Ω) se monta igual.
  - Diagnóstico (R708–R710, D703): `DNP = PROTO`. D703 pasa a BZX84-C3V3 porque DIAG irá directo a un GPIO del ESP32.
  - **Limitación:** en vehículos sin supresión de load dump, las salidas DO no quedan protegidas. Con 202 V a través de la bobina, D701 tendría que absorber ~8 J.
- **`10_power_input`:**
  - J1 y J2 con huellas MSTB 2,5 de 5.08 mm GF. J2 = 1776508.
  - F101 = Bourns SF-2410FPA200W-2: 2 A, 250 VDC, AEC-Q200, LCSC C3159902.
  - C105 queda con `DNP = PROTO,PROD`. Es un hold-up opcional:
    - Mantiene la lógica durante el corte por OV del LM74930 (load dump de 24 V, ≤ 350 ms) y durante los huecos de arranque en frío de 12 V (4.5–6 V, 15–40 ms).
    - No hace falta para los pulsos ISO 7637.
    - Sin C105, la placa se reinicia en esos eventos (estado funcional C).
  - Se quitó un PWR_FLAG suelto en GND_CAN (#FLG125 + #PWR126), que chocaba con GND2 del ADM3055E.
- **Campo `DNP`** agregado a todos los símbolos del proyecto. D401 (opción de banco) = `PROTO,PROD`.

## Máximos de la entrada (load dump suprimido, 24 V)
Pulsos según ISO 7637-2 (anexo A, 24 V): pulso 1 −600 V / 50 Ω; 2a hasta +112 V / 2 Ω / 50 µs; 3a/3b ±300 V / 50 Ω / 0.15 µs. Load dump suprimido de ISO 16750-2: 58 V durante ≤ 350 ms. Hay que verificar los niveles con la edición de la norma que pida el cliente.

| Componente | Máximo que ve | Valor nominal | Condición |
|---|---|---|---|
| F101, J1, VBAT_F | +58 V / ~+140 V (50 µs) / −55 V | 250 VDC | load dump / pulso 2a sobre 28 V / pulso 1 recortado |
| C101 | ~140 V | 450 V | pulso 2a |
| Q101 (VDS) | ~140 V | 250 V | apagado por OV durante 2a; 58 V en el load dump |
| D101 ES2G (inversa) | ~140 V | 400 V | pulso 2a |
| D102 SMCJ33A | ~11 A, VC ~53 V | Ipp 28 A | pulso 1 |
| R102 10 k (2512) | 0.64 W durante 50 µs; ~0 W en el load dump | — | D103 casi no conduce a 58 V |
| D103 SMAJ51A (VS) | recorta a 57–63 V | VS máx. abs. 70 V | pulso 2a |
| R108, R112 51 k (1206) | ~70 V cada una | 200 V | pulso 2a |
| Q102 (VDS) | ~85 V | 100 V | pulso 1 (VOUT + recorte) |
| +VPROT y lo que cuelga de él | ≤ umbral de OV (38.4 o 34.2 V) | C106 de 50 V | corte del LM74930 |

- Con load dump **sin suprimir** (202 V), la entrada sigue dentro de valores (Q101 250 V, D101 400 V, C101 450 V, R108/R112 ~101 V).
- La única duda abierta con 202 V es la sobrecarga de pulso de R102: 2 W durante 350 ms (REVISION_CODEX I2).

## Limitaciones conocidas
- **Salidas DO1/DO2 con load dump sin suprimir (24 V, 202 V): no quedan protegidas.**
  - La bobina del relé externo queda conectada a la batería. Con Q701 apagado, el drenador sigue a la batería.
  - D701 (SMAJ58A) tendría que absorber ~8 J (≈ 0.34 A × 66 V × 350 ms) y fallaría en corto, lo que deja el relé activado.
  - Para esos vehículos haría falta un MOSFET de ≥ 250 V (otra huella) o supresión en el propio relé.
- Las DO no tienen latch de sobrecorriente (retirado el 2026-10-28): un corto de la carga a +V no está limitado por hardware.

## Equivalencia LMR38010 (prototipo y producción)
Fuentes: TI SNVSC73B (LMR38010, sept. 2023), sección 5 "Device Comparison Table", y TI SNVSC72B (LMR38010-Q1), sección 4.

| Orderable | Datasheet | FPWM | Spread spectrum | Modo en carga liviana |
|---|---|---|---|---|
| LMR38010SDDAR (LCSC C5219310) | SNVSC73B | No | Sí | PFM |
| LMR38010FDDAR (LCSC C5219308) | SNVSC73B | Sí | No | PWM forzado |
| LMR38010FSDDAR (LCSC C5219309) | SNVSC73B | Sí | Sí | PWM forzado |
| **LMR38010SQDDARQ1** | SNVSC72B | No | Sí | PFM |
| LMR38010FSQDDARQ1 | SNVSC72B | Sí | Sí | PWM forzado |

- **F** = FPWM (PWM forzado: frecuencia fija también sin carga, más consumo). Sin F = PFM en carga liviana (IQ 40 µA, "PFM variant only").
- **S** = spread spectrum (±8 %, FSPREAD).
- **Q / Q1** = AEC-Q100.
- **LMR38010SDDAR ≡ LMR38010SQDDARQ1.** Coinciden en:
  - Modo (PFM + spread spectrum).
  - Pinout (1 GND, 2 EN, 3 VIN, 4 RT/SYNC, 5 FB, 6 PG, 7 BOOT, 8 SW, EP).
  - Encapsulado DDA0008B.
  - Parámetros revisados: VREF 1 V ±1.5 %, IHS-LIMIT 1.3/1.6/1.9 A, ILS-LIMIT 0.9/1.2/1.5 A, tON-MIN 80/131 ns, IPEAK-MIN 0.25 A, TJ −40 a 150 °C, RθJA 42.9 °C/W.
  - La única diferencia es la calificación AEC-Q100.
  - El -Q1 especifica FOSC con RT = 64.9 kΩ: 320/400/480 kHz. Es el RT elegido.
- No usar las variantes F en el prototipo: cambian el comportamiento en carga liviana (consumo con solo BLE) y no representan a producción.
- **Campo nuevo `MPN_PROTO`:** se usa solo cuando el prototipo lleva otro número de parte, equivalente al de producción. El BOM de prototipo toma `MPN_PROTO` si existe y, si no, `MPN`.

## Hoja 20 (`20_buck_5v`): aplicada (2026-10-27)
- Opción B aplicada en toda la jerarquía:
  - `sheets/20_isolation.kicad_sch` → `sheets/20_buck_5v.kicad_sch` (`git mv`), sin pines jerárquicos.
  - Se quitaron PS201, U202 (ISO7763), U201 (TPS7A1650) y sus pasivos.
  - U201 nuevo: LMR38010 con los componentes de la tabla de abajo.
  - Todas las hojas: GND_ISO → GND_VEH y +5V_ISO → +5V_VEH.
  - Raíz: DO1_EN, DO2_EN, DO1_DIAG, DO2_DIAG y PWR_FLT_N van directo entre las hojas 40, 70 y 10 (las etiquetas `VEH_*` de esas señales se renombraron).
  - Hoja 10: R111 → +3V3_D, C109 = 100 nF, C105 `DNP = PROTO`.
- **Símbolo U201:** `INCLI-VA_easyeda:LMR38010SDDAR` (easyeda2kicad, LCSC C5219310), registrado en `sym-lib-table`.
  - Coincide pin por pin con la tabla 6-1 del datasheet.
  - Ajustes sobre el import:
    - Tipos de pin: GND/VIN/EP power_in, EN/FB input, RT/BOOT passive, PG open_collector, SW output.
    - Huella → la oficial con vías térmicas.
    - Fabricante → "Texas Instruments".
- **Campos de U201:** `MPN = LMR38010SQDDARQ1`, `MPN_PROTO = LMR38010SDDAR`, `LCSC_PROTO = C5219310`.
- **Se quitó un PWR_FLAG suelto en GND_VEH** (#FLG123 + #PWR124, hoja 10): chocaba con GND1 del ADM3055E, ahora en la misma masa.
- **Textos actualizados** en las hojas 30, 40, 50 y 80 y en la raíz.
  - Hoja 40, J402/USB: ahora dice que no hay aislamiento. **En el vehículo, la PC comparte masa con la placa:** usar un aislador USB/UART o una laptop a batería.
- Los cambios de layout del usuario en `70_output_ch` (hechos en KiCad, 21:24) entran en el mismo commit.

**Huella:** `Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.95x4.9mm_Mask2.71x3.4mm_ThermalVias` (oficial). Comparada con el DDA0008B del datasheet:
- Cobre del EP: 2.95 × 4.9 mm. Máscara: 2.71 × 3.4 mm. Vías: 6 × 0.2 mm, igual que TI.
- Pads: 1.775 × 0.6 mm centrados a ±2.5625 mm; TI pide 1.55 × 0.6 mm a ±2.7 mm. El borde exterior es igual (~3.45 mm); los pads de la huella llegan 0.25 mm más hacia el centro. Sirve para soldar a mano.
- Con aire caliente: estañar el EP y calentar desde abajo; las vías dejan llegar el calor y el estaño.

**Componentes** (TI SNVSC73B, tablas 8-1 y 9-1, sección 9.2): +VPROT (6.5–38.4 V) → 5.02 V / 1 A a 400 kHz.

| Ref. | Valor | MPN | Notas |
|---|---|---|---|
| U201 | LMR38010SQDDARQ1 (PROD) / LMR38010SDDAR (PROTO, LCSC C5219310) | TI | EN y VIN → +VPROT; PG sin uso. Pin a pin con el LMR38020 (2 A) |
| C201 | 4.7 µF 100 V 1210 | CGA6M3X7S2A475K200AB (TDK) | C_IN (TI: ≥ 4.7 µF). A verificar |
| C202 | 100 nF 100 V 0603 | GCM188R72A104KA64D | Bypass de VIN, pegado a los pines 3 y 1 |
| C203 | 100 nF 0603 | GCM188R71H104KA57D | C_BOOT (pines 7 y 8) |
| L201 | 33 µH | XAL6060-333MEC (Coilcraft) | Isat 3.7 A > 1.9 A (límite HS máx.); DCR 105 mΩ; AEC-Q200; huella oficial `L_Coilcraft_XAL6060-XXX` |
| C204–C206 | 3 × 22 µF 10 V 1206 | GCM31CR71A226KE02L | C_OUT (TI: 3 × 22 µF a 5 V / 400 kHz). A verificar |
| R201 / R202 | 100 k / 24.9 k | AC0603FR-07100KL / AC0603FR-0724K9L | VOUT = 1 V × (1 + 100k/24.9k) = 5.02 V |
| R203 | 64.9 k | AC0603FR-0764K9L | RT → 400 kHz. Con D = 0.13 a 38.4 V, el tON es 325 ns > tON-min 131 ns |
| TP201 | +5V_VEH | — | Más un PWR_FLAG en +5V_VEH |

- Pico de carga en +5V_VEH: unos 0.7 A, sumando TPS62A02 (WiFi), ADM3055E (180–260 mA), LP5907 y los buffers.
- Disipación de U201: ~0.4 W, que con θJA de 42.9 °C/W da unos +17 °C.

**Cambios en las demás hojas al aplicar la opción B:**
- **Hoja 20:** se renombra a `20_buck_5v` (archivo y nombre de hoja) y se quitan todos sus pines jerárquicos.
- **Raíz:**
  - Etiquetas `VEH_DO1_EN`, `VEH_DO2_EN`, `VEH_DO1_DIAG`, `VEH_DO2_DIAG` y `VEH_PWR_FLT_N` → `DO1_EN`, `DO2_EN`, `DO1_DIAG`, `DO2_DIAG` y `PWR_FLT_N` (directo entre las hojas 40, 70 y 10).
  - Se quitan los cables y etiquetas de los pines de la hoja 20.
- **Todas las hojas:** GND_ISO → GND_VEH y +5V_ISO → +5V_VEH (símbolos, caché y textos).
- **Hoja 10:**
  - R111 (pull-up de FLT) pasa de +5V_VEH a +3V3_D.
  - **C109 (C_dVdT) pasa de 10 nF a 100 nF** (GCM188R72A104KA64D).
  - C105 queda con `DNP = PROTO`.

**C105 en producción: de acuerdo, con dos condiciones.**
1. **Inrush (obligatorio).** Con C105 montado, la capacidad en VOUT es ~1.07 mF. Con C109 en 10 nF: Iinrush = 1.07 mF × 55 µA / 10 nF ≈ **5.9 A**. El breaker (1 A, TMR ~1 ms con C110 de 68 nF) dispararía en cada arranque y la placa no encendería nunca.
   - Con C109 = 100 nF: 0.59 A con C105 y ~34 mA sin C105. Arranque de ~60 ms. Funciona igual con o sin C105.
2. **Mecánica y MPN.** Un electrolítico radial de 16 mm en un chasis con vibración necesita adhesivo (o un encapsulado con base antivibración) y ser automotriz (105–125 °C, AEC-Q200). El MPN sigue pendiente.
- Hold-up con 1000 µF (de 28 a 6 V): 0.37 J. Alcanza ~0.7 s a 0.5 W (solo BLE), suficiente para los 350 ms del load dump. Con WiFi a 1.5 W alcanza ~0.25 s.
- Arranque en frío de 12 V (de 12 a 6 V): 54 mJ, que dan ~36 ms a 1.5 W o ~108 ms a 0.5 W.

## Reglas de diseño (`INCLI-VA.kicad_dru`) y red del pad 25 (2026-10-27)
- **Fabricante: JLCPCB**, 2 capas, 1.6 mm, 1 oz. Fuente: https://jlcpcb.com/capabilities/pcb-capabilities (consultado el 2026-10-27).

  | Regla | Valor del proyecto | Mínimo de JLCPCB |
  |---|---|---|
  | Pista / espacio | 0.15 / 0.15 mm | 0.10 / 0.10 mm |
  | Vía | hueco 0.3 mm / Ø 0.6 mm | 0.15 mm (preferido 0.2 mm) |
  | Hueco de pad | ≥ 0.2 mm | — |
  | Anillo PTH (hueco > 0.35 mm) | 0.18 mm | 0.18 mm absoluto (0.25 recomendado) |
  | Hueco a hueco | 0.45 mm | 0.45 mm |
  | Hueco a cobre | vías 0.2 mm, PTH 0.28 mm | — |
  | Cobre a borde | 0.5 mm | 0.2 mm |
  | Serigrafía | texto ≥ 1.0 mm, trazo ≥ 0.15 mm | — |

  - El puente de máscara (0.10 mm) va en Board Setup; no se puede expresar en el `.kicad_dru`.
- **Reglas especiales:**
  - **HV de entrada:** VIN_VEH y VBAT_F → 1.25 mm al resto (IPC-2221B tabla 6-1, B2, 171–250 V; pad contra pad excluido).
  - **Salidas DO** (VEH_DO1/2) → 0.6 mm (B2, 51–100 V).
  - **+VPROT, VA, C_ID y VOUT** → 0.6 mm entre conductores (B2, 31–50 V); los pads quedan fuera porque U101 es QFN de 0.5 mm.
  - **Barrera del ADM3055E:** dominio CAN (GND_CAN, BUS_CAN_H/L, V_SOIN, V_SOOUT, GNDISO_CAN, CAN_RS, centro de la terminación) → 2.5 mm al resto.
    - El aislamiento es funcional, no de seguridad. Con J1 (MSTB de 5.08 mm) no se puede llegar a los 8.3 mm del encapsulado (CLR/CRP del datasheet Rev. D).
    - Además, ningún relleno puede cruzar el courtyard de U601.
  - **Anchos (IPC-2152, 1 oz, ΔT 10 °C;** 2 A → 30 mil y 1 A → 10 mil, según la tabla de ejemplo de Altium):
    - Entrada (VIN_VEH … +VPROT): 1.0 mm.
    - DO y SENSE: 0.5 mm.
    - +5V_VEH y BUCK_SW: 0.5 mm.
  - **Antena:** la huella oficial `RF_Module:ESP32-S3-WROOM-1` ya trae un rule area de keep-out de 48 × 21 mm en todas las capas de cobre (15 mm alrededor de la antena), que el DRC nativo hace cumplir.
    - Espressif (Hardware Design Guidelines): antena fuera de la placa o en el borde; si no, recortar la placa debajo y a los costados.
    - El documento oficial **no** da una cifra en mm para la placa base; los 15 mm que cita son para la carcasa.
- **Red del pad 25 de U101: `/10_power_input/U101_RTN`.**
  - En el símbolo (`easyeda2kicad:LM74930QRGERQ1`, librería y caché), el pin 25 (EP) pasó de `no_connect` a `passive`.
  - Con `no_connect`, KiCad le daba a cada pad 25 de la huella su propia red `unconnected-…_N` (7 redes que se superponían).
  - Se agregó la etiqueta `U101_RTN` en la hoja 10 (ERC sigue en 0).
  - En el PCB se renombraron las 7 redes de los pads 25 a `/10_power_input/U101_RTN`. Es la única edición al `.kicad_pcb`; no hubo "Update PCB from Schematic".
  - Reglas:
    - `U101_RTN_aislado`: 0.3 mm a cualquier otra red y `zone_connection none`.
    - `U101_pad25_nunca_GND`: si el pad 25 tiene otra red, es un error.
  - **Probado** en una copia: con un pad 25 en GND_VEH, el DRC marca `items_not_allowed` con esa regla.
- **DRC actual** (PCB viejo, sin actualizar):
  - Las 6 violaciones de `ISO_CAN_barrera` son pads de "U1" sin conectar (RS, AUX_OUT); se resuelven con la actualización (U601, RS a GND2).
  - De antes de este turno:
    - Contorno inválido: dos rectángulos superpuestos en Edge.Cuts.
    - J401 (USB-C): pad a NPTH a 0.194 mm (< 0.25 mm del proyecto; JLCPCB pide NPTH a pista 0.2 mm). Es de la huella.
    - U401: serigrafía recortada por el borde.
    - PS201: huella borrada (sale con la actualización).
    - Los agujeros H2–H4 no coinciden con la librería.
  - **Costo en JLCPCB:** las vías del EP de U101 (hueco 0.2 mm, Ø 0.4 mm) tienen recargo ("0.2mm or 0.25mm hole size with via diameter less than 0.45mm, will cost more"). Para evitarlo hay que subir el Ø a ≥ 0.45 mm en `TI_RGE0024T_..._IsolatedVias`. Pendiente de decisión.

## Hoja 80 y cierre del esquemático (aplicado, 2026-10-27)
- **Hoja 80 aprobada y aplicada.**
  - U801 TPS3828-33QDBVRQ1, C801, R802 (0 Ω en serie con RESET).
  - R801 (1 k de WDI a GND): DNP en PROTO y PROD.
  - MR sin conexión.
- **WD_EN eliminado:** se quitó de las hojas 40 y 80 y de la raíz, e IO18 quedó libre (con marca de no-conexión).
  - El pin que ocupaba en las hojas se reutilizó para **VAR_ID2 (IO8)**.
- **VAR_ID**, tabla del usuario (ID1 ID0): **11 base | 10 CAN | 01 solo DO | 00 CAN + DO**.
  - R805 (IO4): `Variant = CAN`. R806 (IO5): `Variant = OUT`.
  - R807 (IO8, tercer bit, CABIN): `DNP = PROTO,PROD`.
  - La variante **ROT se detecta por SPI**, sin bit de VAR_ID (decisión del usuario).
- **LED:** la caja ABS es opaca. D801 (verde, LTST-C171KGKT), D802 (rojo, LTST-C171KRKT), R803 y R804 (470 Ω): montados en PROTO, `DNP = PROD`. MPN de los LED a verificar.
- **Barrera CAN de 2.5 mm:** aprobada por el usuario (aislamiento funcional).
- **J1 y J2 pasan a verticales**, MSTBV 2,5 GF de 5.08 mm (decisión del usuario: el cable entra por un conector circular de 8 hilos en la caja).
  - J1 = MSTBV 2,5/5-GF-5,08 (1777109).
  - J2 = MSTBV 2,5/2-GF-5,08 (1777073, **verificar** en phoenixcontact.com).
  - Los enchufes STF no cambian.
- **Librería:** se borraron los símbolos `URB2405YMD-10WR3_C5369754` y `TPS7A1650QDGNRQ1` de `lib/INCLI-VA.kicad_sym`.
- **U101:** las vías del EP pasan a Ø 0.45 mm (hueco 0.2 mm), en la huella de `lib/INCLI-VA.pretty` y en la instancia del PCB. Ya no tienen recargo en JLCPCB.
- **ERC del proyecto: 0 errores y 1 aviso.** El aviso es `isolated_pin_label` en `U101_RTN`, y es intencional: la etiqueta sobre un solo pin es la que mantiene unida la red del pad 25.

## PCB (2026-10-27)
- **Contorno:**
  - Los dos rectángulos superpuestos eran la placa (100 × 70 mm, radio 4) y un **recorte para la antena** (x 192–200, y 65–100, bajo el área de antena de U401, que apunta a +x).
  - Se reemplazaron por un solo contorno cerrado (líneas y arcos) con una muesca de 8 × 35 mm (Espressif: recortar la placa bajo la antena y a los costados).
  - `invalid_outline` resuelto.
- **Serigrafía de U401:** se recortaron los dos laterales del módulo en x = 191.8 y se quitó la línea frontal, que caía sobre la muesca.
  - Ahora U401 figura como `lib_footprint_mismatch`. **No usar "Update footprints from library" en U401**: se perdería el recorte.
- **J401 (USB-C):** huella oficial `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`. El pad GND (A1/B12) queda a **0.194 mm** del NPTH de la espiga.
  - Eso es menos que el mínimo de JLCPCB para NPTH a cobre (0.2 mm) y que el `hole_clearance` del proyecto (0.25 mm).
  - Pendiente de decisión del usuario.
- **Update PCB from Schematic:** lo hizo el usuario en KiCad (F8, por UUID, con reemplazo de huellas, sin actualizar desde la librería). Commit `1859b79`.
  - Entraron 39 huellas y salieron PS201, U202, C207, C208, R204 y las referencias viejas U1 y R1.
  - Huellas que cambiaron: J1/J2 → MSTBV, Q701/Q751 → SOT-23, D701/D751 → SMA, U201 → HSOIC-8 con vías, C203–C206.
  - **Se borraron los agujeros de montaje H1–H4**: solo existían en el PCB. Conviene agregarlos al esquemático (`Mechanical:MountingHole`) para que no vuelva a pasar.
- **J401:** se acepta la violación (decisión del usuario). Se implementó como regla `J401_land_pattern_oficial` en `INCLI-VA.kicad_dru`: hole_clearance ≥ 0.19 mm, solo dentro de J401, con la nota.
  - Una exclusión del DRC (`drc_exclusions` en `.kicad_pro`) necesita la posición exacta del marcador, que solo da la interfaz; `kicad-cli` no la exporta y la API de Python no funciona sin la interfaz.
  - Si se prefiere la exclusión nativa: en KiCad, clic derecho en el marcador → Exclude, con la misma nota.
- **DRC después de la actualización** (`kicad-cli`, 2026-10-27):
  - Paridad con el esquemático: 0.
  - Sin rutear: 399 conexiones (todavía no hay pistas).
  - **29 errores de `ISO_CAN_barrera`:** los pasivos nuevos de la hoja 60 quedaron apilados por la actualización, mezclando el lado CAN y el lado de la placa. Se resuelven al ubicar los componentes (pendiente; el usuario pidió no moverlos todavía).
  - 1 aviso `lib_footprint_mismatch` en U401: intencional (serigrafía recortada en la muesca).

## Cierre del esquemático (2026-10-27)
- **El PCB (ubicación y ruteo) lo hace Codex.** Claude Code no toca `INCLI-VA.kicad_pcb`.
- H1–H4 agregados en la raíz: `Mechanical:MountingHole`, huella `MountingHole:MountingHole_3.2mm_M3` (NPTH, sin cobre, courtyard de Ø 6.9 mm), fuera del BOM. La posición la define el layout.
- La revisión final (ERC, campos, huellas, ESP32, DNP, BOM y PENDIENTES) se entregó al usuario como reporte. **Los cambios que propone esperan su aprobación.** Después vienen los BOM de PROTO y PROD, el PDF, `docs/LAYOUT_NOTES.md`, el commit "esquemático congelado para layout" y el tag `schematic-v1`.

## Estado previo al layout — Codex, 2026-10-27
- Turno cedido por el usuario: Claude terminó. Se incorporan sus cambios locales de cierre junto con la sincronización del PCB.
- PCB sincronizado: 186 huellas, H1–H5 añadidos (NPTH, posiciones pendientes), F101 actualizado a `Fuse_Bourns_SF-2410`, D401/JP401 retirados; campos y DNP transferidos. Paridad CLI: **0 diferencias**.
- ERC: **0 errores y 1 aviso** intencional `isolated_pin_label` en U101_RTN. Todas las hojas eléctricas sin errores.
- Revisión visual manual de las diez páginas exportadas: completada. Valores de H1–H5 y TP201 ocultados para evitar solapes; notas de TPS3828, alimentación USB y pull-up de FLT corregidas.
- `sch_visual_qa`: no disponible en el perfil MCP `analysis`; la revisión manual no equivale a ejecutar esa herramienta. Repetir cuando esté disponible.
- DRC previo a ubicación: **29 errores de separación CAN**, **1 aviso de U401** por serigrafía recortada intencional y **396 conexiones sin rutear**. Sin pistas ni zonas.
- U101 pad 25 y vías conservan `/10_power_input/U101_RTN`; contorno, reglas y keep-out de U401 conservados.
- La información histórica anterior describe etapas previas y no sustituye este estado.

## Propuesta visual de tamaño — Codex, 2026-10-27
- Se recomienda **120 × 80 mm** para la revisión de ubicación; 100 × 70 mm queda ajustado (ocupación estimada 82.6 % frente a 59.5 %). No se afirma que 100 × 70 sea imposible de rutear.
- Propuesta separada: `docs/layout/INCLI-VA-120x80.kicad_pcb`; vista `docs/layout/ubicacion-120x80.png`; metodología y límites en `docs/LAYOUT_NOTES.md`.
- Las 186 huellas están ubicadas en la propuesta, con margen geométrico de 1.01 mm entre envolventes, redes/DNP conservados y ningún ruteo. El PCB principal no se cambió.
- DRC de la copia: 0 errores geométricos, 1 aviso conocido de U401, 396 conexiones pendientes. Referencias en F.Fab; falta serigrafía final.
- **Falta confirmar tamaño y revisar bloques**, luego afinar desacoples/retornos y mecánica antes del visto bueno final para rutear.

## Retoma y tamaño objetivo — Codex, 2026-10-28
- El usuario consulta si el diseño puede entrar en **100 × 100 mm como máximo**. Se toma como objetivo para la siguiente revisión de ubicación; todavía no hay una propuesta verificada de ese tamaño.
- Evaluación preliminar: 10000 mm² nominales frente a 9600 mm² de 120 × 80 mm (**4.2 % más**). Con las mismas deducciones geométricas y reserva de huellas del estudio anterior, la ocupación estimada sería **57.0 %**. Es favorable por área, pero no demuestra encaje ni ruteabilidad.
- Estado recuperado: propuesta de 120 × 80 mm con 186 huellas y sin ruteo, guardada en `docs/layout/`; último commit previo `1bb7e6a`. El árbol de trabajo estaba limpio.
- Próximo paso: redistribuir en una copia de 100 × 100 mm y comprobar antena, aislamiento CAN, fijaciones, reserva ROT, acceso para soldar y lazos de alimentación. Mantener las huellas DNP. Presentar ubicación antes de rutear.
- En esta retoma solo se actualizó documentación: no se modificaron esquemáticos ni PCB y no se repitieron ERC/DRC.

## Propuesta de 100 × 100 mm preparada — Codex, 2026-10-28
- Autorización del usuario: preparar el formato cuadrado y reubicar componentes. Hecho en **`docs/layout/INCLI-VA-100x100.kicad_pcb`**, con proyecto y reglas adjuntos; principal y propuesta 120 × 80 conservados.
- **186 huellas ubicadas**, incluyendo DNP. Entrada/CAN a la izquierda, dos DO arriba, bucks abajo, sensores en la zona central, ESP32 en el borde derecho y USB abajo.
- U503 en (50,50) mm locales; H5 en (54,60), próximo a los sensores; cinco fijaciones NPTH. Muesca RF de 8 × 35 mm y esquinas de radio 4 mm.
- **DRC de la propuesta: 0 errores geométricos, 1 aviso intencional de U401 y 396 conexiones sin rutear**. Sin pistas ni zonas. Separación mínima de envolventes: 1.01 mm.
- Verificada igualdad de UUID/referencias, valores, campos, DNP, geometría básica de pads y redes frente al PCB principal. U101 pad 25 conserva su red y reglas; keep-out de U401 conservado.
- Imagen revisada: `docs/layout/ubicacion-100x100.png`; exportación nativa: `placa-100x100.svg`. Reportes en `docs/layout/reports/`; scripts reproducibles en `scripts/`.
- No se editaron esquemáticos; no correspondió repetir ERC ni QA de hojas. Falta ajuste eléctrico de detalle, validación mecánica y visto bueno antes de rutear.

## Revisión: TP en Bottom y cuatro fijaciones — Codex, 2026-10-28
- El usuario prefiere 100 × 100 mm, propone TP en la cara inferior y cuatro agujeros de sujeción. Aplicado en la copia `docs/layout/INCLI-VA-100x100.kicad_pcb`.
- **19 TP en B.Cu**, pads Ø 1.5 mm sin taladro. Catorce cambiaron de cara; TP401–TP405 ya estaban abajo. Referencias legibles desde abajo en B.Silkscreen, 1 mm/0.15 mm, sin colisiones detectadas por DRC.
- **H5 retirado de la propuesta**; quedan H1–H4 NPTH M3. Se conservan las posiciones XY de las otras 185 huellas y todas sus redes/campos/DNP. La rigidez con cuatro apoyos requiere validación mecánica.
- Vistas separadas por cara: `ubicacion-100x100.png` y `ubicacion-100x100-bottom.png`. Corregida la ilustración anterior, que mostraba juntos los pads de ambas caras. Exportaciones SVG nativas actualizadas; revisión visual inferior completada.
- DRC repetido: **0 errores geométricos, 1 aviso conocido de U401, 396 conexiones sin rutear**. U101_RTN y reserva RF conservados.
- **Pendiente H5 en esquemático/PCB base:** hay un archivo de bloqueo del proyecto. Se preguntó si KiCad está cerrado, como exige AGENTS.md; sin respuesta aún al documentar este turno. No se editaron esquemáticos ni PCB principal, ni se repitió ERC/QA de hojas. La comparación de integridad excluye H5 explícitamente; no afirmar paridad completa hasta sincronizar.

## Cierre para revisión del usuario — Codex, 2026-10-28
- El usuario respondió afirmativamente a la consulta pendiente y pidió retirar H5 del esquemático. Se eliminó únicamente su símbolo/instancia en `INCLI-VA.kicad_sch` y se actualizó la nota a cuatro agujeros H1–H4. Las conexiones y hojas eléctricas no cambian.
- ERC repetido, reporte persistente `docs/layout/reports/erc-sin-h5.json`: **0 errores y 1 aviso intencional `isolated_pin_label` en U101_RTN**. El JSON agrupa ese aviso bajo `/`; las hojas eléctricas restantes tienen 0 incidencias.
- Hoja raíz exportada por KiCad y revisada visualmente: H1–H4 y nota correctos, sin solapes nuevos. **`sch_visual_qa` no está disponible** en el catálogo de herramientas ni como ejecutable; esta revisión manual no equivale a ejecutar esa herramienta.
- El usuario solicita commit final y push para revisar en detalle esquemático y PCB. Comparar la raíz con **`docs/layout/INCLI-VA-100x100.kicad_pcb`**, que ya tiene 185 huellas, cuatro fijaciones y TP en Bottom. La placa principal y la propuesta 120 × 80 siguen siendo referencias previas, con H5; no se cambiaron en este cierre del esquemático.

## Reacomodo por bloques — Claude Code, 2026-10-28
- El usuario hizo F8 en KiCad tras retirar el latch: commit aparte `30380cc`, paridad 0.
- **H5 agregado** en el esquemático raíz (M3, sin cobre, UUID a7c615b1…) y en el PCB en (68.2, 53) mm locales. Queda junto a U501/U502 y a 18 mm del eje de ROT.
- **Reubicación por bloques según `docs/reference/`** (UG-230 e INCLIMAX). Detalle, tablas antes/después y límites en `LAYOUT_NOTES.md`; imagen en `docs/layout/reacomodo-antes-despues.png`.
- **Barrera `BARRERA_CAN`** (rule area en las dos caras). Solo la cruza U601. **FB602 no cruza:** sus dos redes (GNDISO_CAN y GND_CAN) son del lado aislado.
- `INCLI-VA.kicad_dru`: el pin 17 de U601 (AUXOUT, sin conexión) cuenta como dominio CAN en `ISO_CAN_barrera`.
- DRC 0 errores / 1 aviso U401 / paridad 0. ERC 0 / 1 aviso conocido. `sch_visual_qa` raíz: PASS.
- **Sin ruteo ni zonas de cobre.**

## PCB principal = propuesta 100 × 100 — Claude Code, 2026-10-28
- Pedido explícito del usuario: pasar la propuesta al layout principal. `docs/layout/INCLI-VA-100x100.kicad_pcb` se copió sobre `INCLI-VA.kicad_pcb`. El principal no tenía cambios desde `17a9676`, así que no se perdió nada.
- Borrada la copia `docs/layout/INCLI-VA-100x100.{kicad_pcb,kicad_pro,kicad_dru,kicad_prl}` y su `fp-lib-table`. `.kicad_dru` y las reglas de `.kicad_pro` eran idénticas a las del principal. Vistas, posiciones y reportes se quedan en `docs/layout/`. Los scripts `layout_100x100.py` y `review_layout_100x100.py` quedan como históricos.
- DRC del principal: 0 errores, 1 aviso conocido de U401 y 396 conexiones sin rutear. **Paridad: 22 diferencias** por el latch retirado. **No se hizo "Update PCB from Schematic"**: espera el pedido del usuario.

## Latch de DO retirado y 120 × 80 borrada — Claude Code, 2026-10-28
Decisiones del usuario en este turno:
- **Aislamiento:** el usuario preguntó por la etapa aislada. Se recordó la decisión 3 (opción B, commit `5030862`); no cambia nada.
- **Salidas DO: se quita el latch de sobrecorriente** (antes `DNP = PROTO,PROD`), en las dos instancias:
  - Borrados: Q702/Q752, Q703/Q753, D702/D752, R704–R707/R754–R757, C701/C751 y sus 3 GND_VEH por canal. Etiquetas TRIG, LATCH y SENSE, y las dos EN_5V del latch.
  - **R701/R751 (1 Ω) también salen:** la fuente de Q701/Q751 va directo a GND_VEH.
  - `PWR_FLT_N` ya no entra en la hoja 70 (solo lo usaba D702): se quitaron el pin jerárquico y sus dos conexiones en la raíz. Sigue entre las hojas 10 y 40.
  - **El diagnóstico se conserva** (R708–R710, D703: DNP en PROTO, montado en PROD).
  - Textos de la hoja, Notes de R702 y README actualizados. **Limitación:** un corto de la carga a +V no queda limitado por hardware.
- ERC: 0 errores / 1 aviso conocido (U101_RTN). `sch_visual_qa`: raíz PASS; hoja 70 con 10 avisos `symbol_overlap` de símbolos que ya estaban y se tocan en un pin compartido (no son solapes visibles).
- **Paridad con `docs/layout/INCLI-VA-100x100.kicad_pcb`: 22 diferencias esperadas** (18 huellas que sobran, red SENSE → GND_VEH en el pad 2 de Q701/Q751 y la Note de R702/R752). Hace falta "Update PCB from Schematic" sobre la propuesta (Codex o el usuario). Se libera el espacio del latch en el bloque DO.
- **Propuesta 120 × 80 borrada** de `docs/layout/` (pcb/pro/dru/prl, posiciones, vistas). Se recupera de `aa0a41b`. `scripts/layout_100x100.py` partía de ella; se anotó en su cabecera.

## Revisión del cierre de Codex — Claude Code, 2026-10-28
Solo verificación; no se editó esquemático ni PCB.
- **Esquemático:** ERC 0 errores / 1 aviso conocido (`isolated_pin_label` U101_RTN). `sch_visual_qa` raíz: PASS (solo INFO: falta "company" en el cajetín). 0 etiquetas globales; KW45 fuera de la jerarquía. Footprint/MPN/Manufacturer/Datasheet completos en los 162 componentes de BOM. Todo pasivo que no es 0603 tiene justificación en Notes. El commit `53115ad` solo quita H5 y cambia la nota.
- **Propuesta 100 × 100:** DRC 0 errores, 1 aviso U401, 396 sin rutear. **Paridad con el esquemático: 0** (probada en una copia con la propuesta como PCB del proyecto). Courtyards ≥ 1 mm en la misma cara. U101 pad 25 = U101_RTN; `.kicad_dru` y reglas de `.kicad_pro` iguales a las del principal.
- **Observaciones de ubicación para la siguiente iteración** (distancia borde de pad a pin):
  - U101: C108 (CAP) 12 mm, C102 (VS) 7 mm, C103 23 mm, C110 (TMR) 20 mm → acercarlos al QFN.
  - U201 LMR38010: C202 a VIN 3.1 mm, C201 4.5 mm, L201 a SW 3.8 mm → cerrar el lazo caliente (C202 pegado a VIN/GND).
  - U601 ADM3055E: C601–C610 entre 1.6 y 7 mm por lado → no cumple el ≤ 2 mm de ADI (ya listado).
  - Sensores U501/U502/U503 en el centro de la luz de 90 mm entre H1–H4 (sin H5): es la zona de mayor flexión bajo vibración. Evaluar rigidez o un apoyo cercano que no choque con el eje ROT.
  - SW402 (pulsador) junto a U502: los golpes al pulsar llegan a la IMU; conviene alejarlo.
  - J401 queda ~1 mm dentro del borde; definir si el USB debe asomar fuera de la caja (pregunta 18).
  - H4 (tornillo M3) junto al keep-out de antena; preferir separador plástico o alejarlo.
  - TP: faltan los CS de SPI y el lado bus del CAN (medible en J1); TP201 y TP301 están ambos en +5V_VEH.
- **Notas desactualizadas:** R708/R709/R758/R759 dicen "el drenador llega a ~250 V" (hoy Q701 de 100 V y recorte ≤ 93.6 V). En "Pendientes de BOM" sigue la línea de 20_isolation y la pregunta 14 menciona PS201.

## placement-v1 — Claude Code, 2026-10-29
Pedido explícito del usuario. Script: `scripts/layout_bloques/placement_v1.py`. Detalle en `LAYOUT_NOTES.md`, sección "placement-v1".
- **U601 (ADM3055E):** ADI Rev. D, "PCB Layout": la pista entre el capacitor y VCC/VIO/VISOIN/VISOOUT no debe pasar de 2 mm.
  - C601 (10 nF VIO) pasa a la fila del pin 4: 1.10 mm de pad a pin (antes ~4.7 mm).
  - C604 (100 nF VCC): 1.10 mm del pin 3.
  - C607 (10 nF VISOIN) y C608 intercambiados: 1.60 / 1.99 mm del pin 16. C610 (VISOOUT): 1.60 mm del pin 19.
  - **Límite físico:** en cada fila entra un solo capacitor a ≤ 2 mm sin tapar la salida de los pines 5–8 hacia el ESP32. Los segundos, C602 (100 nF VIO) y C603 (10 µF VCC), quedan a 4.7 mm, en cadena con el primero. C606 (10 µF VISOOUT) queda a 2.9 mm.
- **Buck:** L201 se movió 0.6 mm hacia U201, así que el nodo SW mide ~2.8 mm de pad a pad (antes 3.4). C203 queda a 1.12 mm del pin BOOT (antes 1.45).
- **C105:** la huella anterior (`CP_Elec_16x17.5`, Vishay 1616) **no coincidía** con el J16 de Panasonic:
  - Pads de 7.8 × 9.6 mm con separación de 4.7 mm, contra el land J16 estándar de 2.5 × 6.9 mm con separación de 6.0 mm.
  - La huella nueva es `INCLI-VA:CP_Elec_Panasonic_J16_VibProof`: land **antivibración** J16 (A 5.8, B 7.0, C 6.2, H 2.8 mm; FK, 01-Sep-25). Su columna central contiene el land estándar.
  - MPN de PROD: **EEE-FK1H102AV** (FK antivibración, AEC-Q200, 50 V, 1000 µF, J16). Alt_MPN: EEE-FK1H102AM. Altura máxima 17.3 mm.
- **Coating:** zonas a enmascarar en `User.Comments` y rótulo "SIN BARNIZ" en F.Silkscreen. La caja completa no entra en serigrafía sin pisar D102, Q701, Q751 y sus pads.
- **Verificación:**
  - DRC: 0 errores; 5 avisos ya conocidos (3 de U401, y las referencias de Q101 y U801 tras `b2d4f4a`). Paridad 0; 358 sin rutear.
  - ERC: 0 errores y 5 avisos, los mismos que en HEAD (4 `pin_to_pin` de SW401/SW402 y la etiqueta U101_RTN de un solo pin).
- Courtyards: los pasivos de U601 quedan a ≥ 0.5 mm entre sí (criterio para pasivos del IC). C105 queda a 0.93 mm de R105–R107 y C109; sus pads están en los extremos, lejos de esos pasivos.

## Fijaciones H1–H5 y serigrafía — Claude Code, 2026-10-29
Pedido explícito del usuario (esquemático raíz, PCB y `.kicad_dru`). Detalle en `LAYOUT_NOTES.md`, sección "Fijaciones H1–H5, apoyo opcional y serigrafía". **Sin ruteo.** No hizo falta F8: H5 se agregó al PCB con la ruta de su símbolo, y la paridad da 0.
- Se conservaron los 5 segmentos de CAN_H/CAN_L en F.Cu que el usuario había borrado sin commit.
- Hecho:
  - H1–H4 cambiados a `MountingHole_3.2mm_M3_Pad`, y H5 nuevo en (56.0, 38.5). Metalizados, con anillo de 6.4 mm (huella oficial) y **sin red**.
  - Reglas `H_anillo_cobre` (≥ 0.5 mm) y `H_zona_arandela` (pistas/vías a ≥ 4 mm del centro).
  - Rule area `APOYO_CAJA_B`: Ø8 mm en B.Cu en (63.5, 49.0); sin pistas, vías, pads ni huellas; relleno permitido.
  - Serigrafía: línea de la barrera CAN y "CAN AISLADO" en las dos caras, pinout de J1/J2 en las dos caras, nombre/Rev/fecha abajo, rótulos ENTRADA, BUCK 5V, SALIDAS DO y SENSORES. Las marcas de polaridad y pin 1 ya estaban todas.
  - C206 a 12.8 mm aceptado: cada C204–C206 con su vía a GND y plano continuo hasta el EP de U201 (anotado para el ruteo).
- Verificación: DRC 0 errores (3 avisos conocidos de U401), paridad 0, 358 sin rutear. ERC 0 errores. `sch_visual_qa` de la raíz: PASS.
- ERC: 4 avisos `pin_to_pin` nuevos en `40_mcu`. Vienen del símbolo de SW401/SW402 que cambió el usuario (pines "Unspecified"). Son inofensivos y quedan para cuando se revise ese símbolo.
- **Decisiones abiertas:**
  - Lado del imán de ROT: sigue sin definir. Se dejan libres las dos caras; H5 y B dejan libre un círculo de Ø17.9 mm alrededor del eje.
  - Visto bueno a la ubicación para empezar el ruteo.

## Correcciones sobre `1ff3419` — Claude Code, 2026-10-29
Pedido explícito del usuario (editar el PCB). Detalle y tablas en `LAYOUT_NOTES.md`, sección "Correcciones aplicadas sobre `1ff3419`". **Sin ruteo.**
- Al empezar seguía abierto el gestor de proyectos de KiCad (`~INCLI-VA.kicad_pro.lck`); el editor de PCB estaba cerrado. No se tocó `.kicad_pro`.
- Hecho:
  - C403 sobre el pin EN (1.3 mm).
  - C202 a 1.06 mm de VIN y de GND de U201; C201 detrás.
  - C204–C206 en columna junto a C203: 6.0 / 9.4 / 12.8 mm al EP (antes 11.6–13.9).
  - J401 −0.4 mm: sin errores de borde.
- Referencias: todas en 0.8 / 0.8 / 0.15 mm, a 0°/90°. Regla `JLC_serigrafia` → 0.8 / 0.15 mm. Ocho quedan solo en F.Fab: U101, R106, R202, C607, C610, R602, R303 y Q701.
- Courtyards: un solo par por debajo de su criterio, C403–C402 (0.7 mm). El resto queda en ≥ 0.5 mm por ser pasivos del IC.
- DRC: 0 errores y los 3 avisos conocidos de U401. Paridad 0; 356 sin rutear.
- **Decisiones abiertas:**
  - Rigidez de los sensores: opción A, agujero M3 en (56.0, 38.5); u opción B, apoyo inferior de Ø8 mm en (63.5, 49.0).
  - Aprobar los rótulos de zona, el pinout de J1/J2 y la línea de barrera CAN en serigrafía.
  - Visto bueno a la ubicación para empezar el ruteo.

## Revisión de la ubicación del usuario (`1ff3419`) — Claude Code, 2026-10-28
Solo verificación y documentación; no se tocó el PCB (KiCad estaba abierto). Detalle en `LAYOUT_NOTES.md`, sección "Revisión de la ubicación del usuario".
- DRC: paridad 0; 2 errores de borde en J401 (ranuras SH a 0.3 mm); 92 referencias en 0.7 / 0.12 mm (regla de 1.0 / 0.15); 37 pares de courtyards a menos de 1 mm.
- A corregir antes de rutear: C403 vuelve al pin EN de U401; C202/C201 pegados a VIN/GND de U201; GND de C204–C206 cerca del EP; J401 0.3–0.5 mm hacia adentro.
- Propuestos: rótulos de zona, pinout de J1/J2, línea de barrera CAN en serigrafía y flechas de ejes en los sensores. Se colocan cuando el usuario lo apruebe, con KiCad cerrado.
- Decisión abierta: apoyo de los sensores sin H5 (zona de máxima flexión).

## Falta
- [x] Sincronizar `INCLI-VA.kicad_pcb` con el esquemático (F8 del usuario, `30380cc`); paridad 0 también tras agregar H5.
- [x] Retirar H5 y actualizar la nota de fijaciones en la raíz; repetir ERC y revisión visual manual.
- [x] Ejecutar `sch_visual_qa` de la raíz: PASS (Claude Code, 2026-10-28).
- [x] Propuesta 100 × 100 adoptada como PCB principal (2026-10-28). Falta la paridad completa (ver el ítem siguiente).
- [x] Preparar y presentar distribución preliminar de **100 × 100 mm máximo** con todos los componentes y H1–H5, separación CAN y acceso de soldadura comprobados geométricamente. Ver `LAYOUT_NOTES.md`.
- [x] Desacoples y lazos: C601 a 1.1 mm del pin 4, L201/C203 acercados (placement-v1). Ubicación aprobada por el usuario: tag `placement-v1`.
- [x] Ruteo por etapas, terminado e integrado en `main` (`pcb-v1-rc1`; ver "Ruteo por etapas"). El usuario rutea aparte una copia en `PCB_INCLI_VA_manual` (rama `ruteo-manual`): **no tocarla**.
- [x] C105: huella J16 verificada contra Panasonic y reemplazada por el land antivibración, que acepta EEE-FK1H102AV y EEE-FK1H102AM.
- [ ] Verificación térmica en dos capas y ensayos eléctricos/EMC; ERC no certifica transitorios ni disipación.
- [ ] Validar H1–H5 y el apoyo B contra la caja cuando se diseñe (ver "Requisitos para la caja"), y hacer el ensayo de vibración.
- [ ] Ruteo del buck: vía a GND junto al pad de C204, C205 y C206, y plano continuo hasta las vías del EP de U201.
- [x] Supervisión con TPS3828 aplicada. WD_EN/TPS3431 quedaron obsoletos.
- [x] F101: nueva huella documentada en librería e incorporada al PCB; sustituye la importación antigua.
- [x] Regla e isla lógica U101_RTN implementadas; las vías del EP comparten una sola red.
- [x] Opción de banco D401/JP401 eliminada del esquemático y del PCB.

## Decisiones del usuario aún abiertas
- Lado del imán de ROT. Mientras no se defina, quedan libres las dos caras alrededor del eje de U503.
- Disponibilidad de EEE-FK1H102AV (C105 PROD) y del resto de los MPN marcados "a verificar".

## Requisitos para la caja (la caja aún no está diseñada)
Coordenadas de KiCad en mm; la placa ocupa (100, 50)–(200, 150), 100 × 100 mm, 1.6 mm.
- **Fijaciones:**
  - H1 (105, 55), H2 (195, 55), H3 (105, 145), H4 (195, 145) y H5 (156, 88.5).
  - M3, PTH de 3.2 mm, anillo de 6.4 mm sin red. Arandela de Ø ≤ 8 mm.
  - Tornillo o inserto de H5 de inoxidable A2/A4, latón o nylon; **nunca acero** (H5 a 9.77 mm del eje del imán de ROT; aceptado por el usuario, 2026-10-30).
- **Apoyo B:** columna de la caja contra B.Cu en (163.5, 99.0), Ø8 mm. Esa zona no tiene cobre expuesto.
- **Aberturas:**
  - J1: MSTBV de 5 pines, borde izquierdo, y ~96–132.
  - J2: MSTBV de 2 pines, borde superior, x ~165–186.
  - J401: USB-C, borde derecho, y ~75–86.
  - J402 (UART0) es interno: no necesita abertura.
- **Altura:**
  - Cara superior: C105 hasta 17.3 mm (solo en PROD) y J1/J2 con la brida.
  - Cara inferior: **C104 (47 µF, CP 10 × 10 mm) de 10.5 mm** en (106.85, 71.0); el resto son TP. **Separadores de ≥ 12 mm** entre la placa y el fondo de la caja.
  - **C104 a ~1.6 mm del borde izquierdo** (cuerpo; el courtyard llega al borde): sin nervios ni paredes de la caja en x < 102 frente a C104. Placa **fresada, sin V-cut** (aceptado por el usuario, 2026-10-30).
- **Adhesivo:** C104 (cara inferior, vibración) y C105 si se monta la versión sin terminales de soporte.
- **Antena del ESP32-S3:** keep-out de la huella oficial (48 × 21 mm alrededor de la antena, borde derecho). Sin metal de la caja ni tornillería sobre la antena ni a menos de 15 mm.
- **ROT (decisión del usuario, 2026-10-30): imán arriba, en la cara F.Cu, frente a U503.**
  - Eje sobre U503 (150, 100). Imán Ø8 × 2.5 mm diametral. Air gap 0.5–3 mm a U503.
  - **Preferido:** imán pegado en la punta del eje o en un portaimán no ferromagnético de **Ø ≤ 8.7 mm** centrado en el eje.
  - El círculo de Ø17.9 mm **no** está libre en F.Cu: U501 (SCL3300, ~3.3 mm de alto) tiene el cuerpo a 4.88 mm del eje y C503 (0603, ~0.9 mm) a 7.24 mm. No se mueven (decisión del usuario).
  - Holgura radial con portaimán de Ø8.7 mm: 0.53 mm a U501 y 2.89 mm a C503.
  - **Alternativa, portaimán mayor que Ø8.7 mm:** solo con air gap de **2.6–3.0 mm**. Su cara inferior debe quedar por encima de U501. Con 0.5 mm de margen: cara a **≥ 3.8 mm** sobre la placa, es decir air gap **≥ 2.6 mm** sobre U503 (TSSOP-14, 1.2 mm máx.), dentro del rango 0.5–3 mm solo entre 2.6 y 3.0 mm. Distancia radial del borde del portaimán: a U501 = 4.88 − Ø/2 mm y a C503 = 7.24 − Ø/2 mm (negativo = el portaimán pasa por encima). Ejemplo Ø16 mm: −3.12 mm (U501) y −0.76 mm (C503), ambos por encima.
  - Cara inferior: TP502 (courtyard a 8.08 mm del eje) se queda; no afecta con el imán arriba.
  - Tornillo e inserto de H5 no magnéticos (inoxidable A2/A4, latón o nylon).
- **Coating:** enmascarar J1, J2, J401 y J402 (zonas en `User.Comments`).

## Ruteo por etapas (rama `ruteo-agente`, desde `placement-v1`) — histórico
Terminado: integrado en `main` (88860c5, tag `pcb-v1-rc1`); la rama se eliminó.
No se mueven ni rotan componentes respecto de `placement-v1`; si hace falta, se anota en `docs/RUTEO_AGENTE.md`. Al final de cada etapa: DRC, render de las dos caras, commit, `git push origin ruteo-agente` y esperar el visto bueno del usuario.
- [x] 0. Reglas: net classes, pares diferenciales, vía 0.3/0.6 mm y teardrops (aprobada, 36bf77f).
- [x] 1. Potencia: cerrada (Claude Code). Cambios de ubicación: C104 a B.Cu, U301 girado 180°, C302 junto a VIN y TP101 a (127.6, 61.5).
- **Las etapas 2 a 6 las sigue Codex en `ruteo-agente`.** Plan, reglas y restricciones en `docs/RUTEO_TRASPASO.md`.
- [x] 2. CAN: terminada y aprobada por el usuario; continuidad B.Cu auditada. Puente H autorizado, C608 aceptado, DRC 0 errores / paridad 0.
- [x] 3. USB/MCU: cierre con cuello D− autorizado; siguiente etapa espera visto bueno.
- [x] 4. Sensores y señales: cerrada (Claude Code); opción C, U503 girado 180°. La etapa 5 espera visto bueno.
- [x] 5. Planos: cerrada (Claude Code); 0 sin rutear. La etapa 6 espera visto bueno.
- [ ] 6. Cierre: DRC y paridad en 0, retornos, fabricación de prueba para JLCPCB en `fab/`.

## Requisitos para el firmware (SPI de 50_sensors)
Bus SPI compartido (SPI2/FSPI: SCK IO12, MOSI IO11, MISO IO13). Un `spi_device` por sensor, cada uno con su modo y su frecuencia:

| Sensor | CS | Modo SPI | f máx. | Fuente |
|---|---|---|---|---|
| U501 SCL3300-D01 | CS_INC → IO10 | 0 (CPOL=0, CPHA=0) | 8 MHz (recomendado 2–4 MHz) | Murata Doc. 4921 Rev. 4 |
| U502 ASM330LHH | CS_IMU → IO9 | 3 (CPOL=1, CPHA=1) | 10 MHz | ST DocID031239 Rev 4, tabla 6 |
| U503 AS5147U (solo ROT) | CS_ROT → IO14 | 1 (CPOL=0, CPHA=1) | 10 MHz | ams DS000639 v1-04 |

- ASM330LHH: configurar `I2C_disable = 1` (CTRL4_C) y `DEVICE_CONF = 1` (CTRL9_XL); INT1/INT2 en push-pull (IO40/IO41).
- Variante estándar: U503 no está montado; no inicializarlo (leer VAR_ID antes de tocar CS_ROT).
- **U503 girado 180° en el PCB (etapa 4):** desfase fijo de 180° en el ángulo, sin inversión del sentido de giro. Compensarlo con el registro ZPOS o en la calibración del cero.

**LEDs de estado D801 (verde, IO6) y D802 (rojo, IO7):** con R803 = R804 = 2.2 kΩ circulan ≈ 0.61 mA (verde) y ≈ 0.70 mA (rojo). Por datasheet, el rojo da más mcd por mA (54 contra 35 mcd típicos a 20 mA), así que a corriente parecida se ve algo más brillante, y el bin de intensidad (18–71 mcd) puede variar hasta 4 veces entre piezas. **Igualar y ajustar el brillo por PWM** (LEDC): como punto de partida, verde al 100 % y rojo al ~55 % (I_rojo ≈ 0.65 × I_verde para la misma mcd); ajustar a ojo en el prototipo.

**Ejes de la placa (rc4, serigrafía en F.Silkscreen junto a H5):** sistema dextrógiro. Mirando la cara superior, +X va a la derecha, +Y hacia arriba y +Z sale de la cara superior. Los dos sensores están en F.Cu a 0°.
- **U502 ASM330LHH** (ST DocID031239 Rev 4, fig. 1: pin 1 arriba a la izquierda en la vista superior; +X derecha, +Y arriba, +Z sale): **X_placa = X_U502, Y_placa = Y_U502, Z_placa = Z_U502** (identidad, para aceleración y giro).
- **U501 SCL3300-D01** (Murata Doc. 4921 Rev. 2, fig. 8, tabla 9 y fig. 10: +X_U501 de la fila de pines 1–6 hacia la 7–12, es decir arriba; +Y_U501 del pin 1 al 6, es decir a la derecha; +Z_U501 sale, z = +1 g apoyada normalmente): **X_placa = Y_U501, Y_placa = X_U501, Z_placa = Z_U501**, con todos los signos +. Tal como lo dibuja Murata, el triedro de U501 es levógiro; el intercambio de X e Y lo lleva al sistema dextrógiro de la placa. Ángulos: ANG_X/ANG_Y de U501 se intercambian igual.
- **Validar en el primer prototipo con la prueba de 6 posiciones** (±1 g por eje): placa con +X, −X, +Y, −Y, +Z y −Z hacia arriba (contra la gravedad). En cada posición, el eje de la placa que apunta hacia arriba debe leer +1 g en los dos sensores, una vez aplicada la transformación, y los otros dos ≈ 0 g. Si algún signo no coincide, corregir la tabla de arriba antes de calibrar.

## Conectores J1 y J2 (confirmado por el usuario, 2026-10-27)
Phoenix Contact COMBICON **MSTBV 2,5**, **vertical**, paso **5.08 mm** y **brida roscada (GF)**.
- Se eligió vertical porque el cable externo entra por un conector circular de 8 hilos en la caja. J1 y J2 son conexiones internas; quedan 7 hilos de 8 en uso.
- Confirmado en phoenixcontact.com (fichas "PCB header"; el sitio bloquea el acceso automático, así que se leyeron indexadas):
  - **1777109** = MSTBV 2,5/ 5-GF-5,08: 5 polos, 12 A / 320 V (III/2), brida roscada, soldadura por ola, Sn.
  - **1777073** = MSTBV 2,5/ 2-GF-5,08: 2 polos, 12 A / 320 V (III/2), brida roscada, agujero de 1.4 mm, Sn.

| Ref. | Función | Header en placa (MPN) | Enchufe del arnés (no va en la placa) |
|---|---|---|---|
| J1 | 1 V+, 2 GND_VEH, 3 CAN_H, 4 CAN_L, 5 CAN_GND | MSTBV 2,5/5-GF-5,08 (**1777109**) | MSTB 2,5/5-STF-5,08 (**1778014**), tornillo |
| J2 | 1 DO1, 2 DO2 | MSTBV 2,5/2-GF-5,08 (**1777073**) | MSTB 2,5/2-STF-5,08 (**1777989**), tornillo |

- Los enchufes STF se atornillan a la brida del header, lo que sirve contra la vibración. Son de 12 A / 320 V, para cable de 0.2–2.5 mm².
- Phoenix también lista como compatibles con estos headers otras familias STF de 5.08 mm: FKC 2,5 (push-in), QC 1 (desplazamiento de aislante) y TMSTBP 2,5. Sirven si se prefiere otra forma de cablear el arnés.
- Huellas oficiales: `Connector_Phoenix_MSTB:PhoenixContact_MSTBV_2,5_{5,2}-GF-5,08_..._Vertical_ThreadedFlange`. Ya están en el PCB.
- **BOM del arnés:** los enchufes no salen del BOM de la placa. Si se quiere, se pueden agregar como ítems mecánicos.

## Pendientes de BOM
- [~] **C105 (PROD):** elegido **EEE-FK1H102AV**: Panasonic FK antivibración, AEC-Q200, 50 V, 1000 µF, 105 °C, J16. Huella `INCLI-VA:CP_Elec_Panasonic_J16_VibProof` con los pads de las terminales de soporte.
  - Falta confirmar la disponibilidad.
  - El inrush con C109 = 100 nF ya está calculado (0.59 A).
- [ ] **R102** (pedido del usuario, 2026-10-27): resistencia **anti-pulso en el mismo encapsulado 2512**, si aguanta el pulso del load dump sin suprimir.
  - Pulso: ~2 W durante 350 ms (0.68–0.74 J rectangular) con 85 °C de temperatura inicial (REVISION_CODEX I2).
  - Comparar con la curva de pulso único del fabricante, por ejemplo series anti-surge 2512.
  - Si ninguna 2512 alcanza, proponer otra opción antes de cambiar la huella.
- [ ] **Compra de sensores:**
  - SCL3300-D01 y AS5147U-HTSM: sin stock en LCSC → comprar en DigiKey o Mouser.
  - ASM330LHHTR: con stock en LCSC (C459826).
- [ ] **MPN marcados "a verificar" en Notes** (disponibilidad y especificación, antes de congelar el BOM):
  - 10_power_input:
    - Q101 STD18NF25
    - L101 SRN6045TA-100M
    - C101 CGA5L4X7T2W104K160AA
    - C102 y C103 CGA5L2X7R2A105K160AA
    - C106 GCM32ER71H106KA12L
    - C107 GCM188R72A104KA64D
    - C110 GCM188R71H683KA57D
    - D101 ES2G-E3/52T
  - 20_isolation: se rehace con la opción B (no aislada); sus MPN dejan de aplicar.
  - 30_regulation:
    - C301 GCM21BR71A106KE22L
    - C304 GRM21BZ71A226ME15L
    - FB301 BLM18PG221SN1D
    - U302 LP5907QMFX-3.3Q1 (confirmar el código de pedido exacto)
  - 40_mcu_esp32s3:
    - C401 GRM21BZ71A226ME15L
    - C403 GCM188R71C105KA64D
    - D401 eliminado junto con JP401; ya no aplica.
  - 50_sensors:
    - C508 GCM21BR71A106KE22L

## Notas para el próximo turno
- **pcbnew en scripts:** `LoadBoard()` de un PCB fuera de la carpeta del proyecto, seguido de `Save()` dentro del proyecto, sobrescribe `INCLI-VA.kicad_pro` con valores por defecto (se pierden las net classes). Cargar siempre el archivo del proyecto. Verificar `git diff INCLI-VA.kicad_pro` antes de cada commit.
- **Reglas DRC:** una regla de clearance sin condición anula las net classes. La propiedad para la net class es `A.NetClass`.
- Variante ROT: U503, C507 y R503 tienen `dnp yes` y el campo `Variant = ROT`. En la variante ROT la placa va centrada sobre el eje del pivote.
- Huella del SCL3300 (easyeda2kicad DFL-12): pads 0.32 mm más largos que el land pattern de Murata, para soldar a mano; en producción volver al de Murata.
- Pines del ESP32-S3: la tabla aprobada y sus criterios están en un texto de la hoja 40. No mover señales críticas a GPIO1–14/17/18 (glitch de encendido) ni a strapping.
- Opción de banco D401/JP401 eliminada. USB no alimenta +5V_VEH; usar la entrada vehicular para energizar la placa.
- Firmware: los requisitos están en `README.md` ("Requisitos para el firmware").
- KiCad: antes de editar archivos `.kicad_sch` a mano o con scripts, confirmar que KiCad está cerrado. Si estaba abierto, recargar las hojas antes de guardar.
