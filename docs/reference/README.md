# Placas de referencia

Fotos de placas comerciales usadas como referencia de distribución y arquitectura para el INCLI-VA. Son solo referencia visual, no documentación de fabricación.

| Archivo | Placa | Qué observar |
|---|---|---|
| `ug230_superior.png` | UG-230 (WU-SDW2-22, STM32F401 + radios BLE/433 + RS485 aislado + 2 relés), cara superior | Cada conector en el borde con su circuito pegado. Entrada en una esquina en orden bornera → varistor → fusible/TVS → buck → electrolítico. ADM2582E (RS485 aislado) junto a su conector, montado sobre la barrera. MCU al centro, radios con blindaje en los bordes. Relés junto a su bornera de salida. |
| `ug230_inferior.png` | UG-230, cara inferior | Plano de masa continuo con vías de costura, corte del plano en la zona aislada y puntos de prueba rotulados en la cara inferior. Agujeros de fijación también en posiciones intermedias, no solo en las esquinas. |
| `inclimax_superior.png` | INCLIMAX SENSOR (ESP32-S3), cara superior | Referencia del producto. Buck no aislado (inductor central) + módulo DC-DC aislado (U12) + transceptor ancho junto al conector con keep-out rayado. Arquitectura probable: lógica referida a la masa del vehículo y solo el bus aislado, igual que la opción B (el ADM3055E integra transceptor aislado + isoPower). **Pendiente:** confirmar con continuidad entre el GND de la entrada y el GND de la lógica. Placa mucho más chica que 100 × 100 mm, por lo que es más rígida frente a vibración. |
