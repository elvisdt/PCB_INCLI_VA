# Validación previa a la ubicación — 2026-10-27, Codex

El usuario confirmó que Claude terminó y autorizó completar la sincronización antes del layout. La ubicación debe presentarse para visto bueno antes de rutear. Se incorporan los cambios locales de cierre de Claude sin revertirlos.

## Cambios aplicados

- PCB sincronizado con los 186 componentes del netlist: H1–H5 añadidos como NPTH, F101 reemplazado por la nueva huella Bourns, D401/JP401 retirados.
- Campos, valores, exclusiones de BOM y DNP transferidos. Las posiciones de las huellas existentes se mantienen; H1–H5 quedan temporalmente fuera del contorno hasta su ubicación mecánica.
- Se conserva el contorno, el keep-out y la serigrafía recortada de U401, así como la red exclusiva de todos los pads 25 de U101.
- Notas de la hoja MCU actualizadas a TPS3828, sin la opción USB retirada. Pull-up de FLT corregido en el texto de la hoja 10 a +3V3_D.
- Valores gráficos de H1–H5 y TP201 ocultados para evitar solapes. Valores eléctricos intactos.
- PENDIENTES actualizado con el estado vigente y advertencias sobre sus antecedentes históricos.

## Verificación

| Comprobación | Resultado |
|---|---|
| ERC KiCad 10.0.7, todas las severidades | 0 errores; 1 aviso intencional `isolated_pin_label` en U101_RTN |
| Campos Footprint, MPN, Manufacturer, Datasheet, DNP | Presentes en los 186 componentes; DNP vacío permitido; N/A explícito en elementos mecánicos y test points |
| DNP nativo del esquemático | Coherente con pertenencia de PROTO al campo DNP |
| Paridad de esquemático y PCB, DRC CLI | 0 diferencias |
| DRC geométrico antes de ubicar | 29 violaciones de separación CAN por componentes todavía en staging; 1 aviso de huella U401 con serigrafía modificada intencionalmente |
| Conectividad física | 396 conexiones pendientes; 0 pistas y 0 zonas de placa |
| Revisión visual manual | Diez páginas inspeccionadas; páginas corregidas reexportadas e inspeccionadas |
| `sch_visual_qa` | No ejecutado: no disponible en el perfil MCP analysis. La revisión manual no es una ejecución equivalente |

Por hoja: raíz, 20 y 40 con ajustes de texto/legibilidad verificados; hoja 10 con anotación de alimentación corregida; 30, 50, 60, DO1, DO2 y 80 sin defectos visuales bloqueantes detectados. El único aviso ERC pertenece a la etiqueta U101_RTN de la hoja 10, aunque el JSON CLI lo agrupa en la raíz. Las exclusiones/configuración de ERC del proyecto se mantuvieron.

## Límites y siguiente paso

La sincronización y ERC no certifican márgenes de transitorios, disipación, fabricación ni inmunidad EMC. Sigue pendiente el land pattern definitivo de C105 y el cierre de mecánica ROT/fijaciones.

Se exploró una distribución de componentes en copias temporales. No se incorporó al PCB porque todavía presentaba separaciones inferiores a 1 mm entre courtyards y proximidad de desacoples insuficiente. Esto no demuestra que la placa no pueda alojar el diseño: indica que esa propuesta no cumple aún los criterios del proyecto.

Próxima fase: completar ubicación por bloques y desacoples, comprobar separaciones y presentar vista de revisión. **No rutear hasta el visto bueno del usuario.** Los reportes temporales de esta sesión se encuentran en `/tmp/incli-layout-validation`; este documento conserva el resumen reproducible con `kicad-cli sch erc` y `kicad-cli pcb drc --schematic-parity`.
