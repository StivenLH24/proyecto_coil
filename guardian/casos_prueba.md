# Casos de Prueba — Engine de Nómina (R1 a R5)

## R1: Validación de salario mínimo legal vigente
- Dado un `salario_base` menor a $1.300.000, la función debe lanzar `ValueError`.
- Ejemplo: `liquidar_nomina(1_000_000, 0, 0, 5_416.67)` → `ValueError`.

## R2: Validación de valores negativos
- Dado un `salario_base`, `horas_extras_diurnas`, `horas_extras_nocturnas` o `vlr_hora` negativo, la función debe lanzar `ValueError`.
- Ejemplos:
  - `liquidar_nomina(-1, 0, 0, 5_416.67)` → `ValueError`
  - `liquidar_nomina(2_000_000, -5, 0, 8_333.33)` → `ValueError`
  - `liquidar_nomina(2_000_000, 0, -3, 8_333.33)` → `ValueError`
  - `liquidar_nomina(2_000_000, 0, 0, -1)` → `ValueError`

## R3: Recargos por horas extras
- **Diurnas (25%)**: Dado `salario_base = 2_000_000`, `vlr_hora = 8_333.33` y `horas_extras_diurnas = 10`, el recargo diurno debe ser `10 * 8_333.33 * 0.25 = 20_833.33`.
- **Nocturnas (75%)**: Dado `salario_base = 2_000_000`, `vlr_hora = 8_333.33` y `horas_extras_nocturnas = 5`, el recargo nocturno debe ser `5 * 8_333.33 * 0.75 = 31_250.00`.
- **Mixto**: Con 10 diurnas y 5 nocturnas, `subtotal_recargos = 20_833.33 + 31_250.00 = 52_083.33`.

## R4: Deducciones de seguridad social (salud + pensión)
- Dado `total_devengado = salario_base + subtotal_recargos`:
  - `descuento_salud = total_devengado * 0.04`
  - `descuento_pension = total_devengado * 0.04`
- Ejemplo: `salario_base = 2_000_000`, sin horas extras → `descuento_salud = 80_000`, `descuento_pension = 80_000`.

## R5: Auxilio de transporte
- Si `salario_base <= 2_600_000`, se suma `auxilio_transporte = 162_000`.
- Si `salario_base > 2_600_000`, `auxilio_transporte = 0`.
- Ejemplos:
  - `salario_base = 1_500_000` → `auxilio_transporte = 162_000`
  - `salario_base = 3_000_000` → `auxilio_transporte = 0`
