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
| 0. Reglas | en curso | |
| 1. Potencia | | |
| 2. CAN | | |
| 3. USB/MCU | | |
| 4. Sensores y señales | | |
| 5. Planos | | |
| 6. Cierre y fabricación de prueba | | |
