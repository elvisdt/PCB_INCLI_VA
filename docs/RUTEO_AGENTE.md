# Ruteo del agente (rama `ruteo-agente`)

Parte del tag `placement-v1`. El usuario rutea en paralelo una copia en `PCB_INCLI_VA_manual` (rama `ruteo-manual`): no tocarla.

## Reglas de trabajo
- No mover ni rotar componentes respecto de `placement-v1`. Si alguno lo necesita, se anota abajo y se espera la decisión del usuario.
- Al final de cada etapa: DRC, render de las dos caras, commit, `git push origin ruteo-agente`, y esperar el visto bueno del usuario.

## Cambios de ubicación pedidos (no aplicados)
_(ninguno por ahora)_

## Etapas
| Etapa | Estado | Commit |
|---|---|---|
| 0. Reglas | lista, espera visto bueno | (este commit) |
| 1. Potencia | | |
| 2. CAN | | |
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

### Para decidir (usuario)
1. **HV en VOUT/+VPROT:** se usa 1.25 mm entre pistas, vías y rellenos, y 0.6 mm cuando hay un pad de por medio. Con 1.25 mm literal no se pueden conectar el pin VIN de U201 (GND a 0.67 mm), C202/C107 (0603) ni la ubicación aprobada (C202.2 a 1.15 mm de U201.2). VIN_VEH/VBAT_F (202 V) mantienen 1.25 mm en todo, salvo entre pads de un mismo encapsulado.
2. **Par CAN:** KiCad reconoce pares solo por el sufijo (`+`/`-` o `P`/`N`), así que `BUS_CAN_H/L` no se detecta. La clase CAN fija ancho y gap, y el agente las rutea acopladas por script. Si quieres el router interactivo de pares en tu copia manual, habría que renombrar las redes en el esquemático (por ejemplo `BUS_CAN_P/N`). No se hizo.
3. **USB:** 0.3/0.2 mm cabe en el paso de 0.5 mm de J401. En 2 capas de 1.6 mm la impedancia no queda en 90 Ω, pero para Full-Speed (12 Mbit/s) con menos de 30 mm de pista alcanza.

### Verificación
- DRC: 0 errores; 5 avisos conocidos (3 de U401, y las referencias de Q101 y U801). Paridad 0; 358 sin rutear.
