# Escenarios de Validacion Academica — Engine de Nomina (TC-01 a TC-13)

## TC-01: Validacion de salario minimo legal vigente
- Dado un `salario_base` menor a $1.300.000, la funcion debe lanzar `ValueError`.
- Ejemplo: `liquidar_nomina(1_000_000, 0, 0, 5_416.67)` → `ValueError`.

## TC-02: Validacion de salario base negativo
- Dado un `salario_base` negativo, la funcion debe lanzar `ValueError`.
- Ejemplo: `liquidar_nomina(-1, 0, 0, 5_416.67)` → `ValueError`.

## TC-03: Validacion de horas extras diurnas negativas
- Dado `horas_extras_diurnas` negativo, la funcion debe lanzar `ValueError`.
- Ejemplo: `liquidar_nomina(2_000_000, -5, 0, 8_333.33)` → `ValueError`.

## TC-04: Validacion de horas extras nocturnas negativas
- Dado `horas_extras_nocturnas` negativo, la funcion debe lanzar `ValueError`.
- Ejemplo: `liquidar_nomina(2_000_000, 0, -3, 8_333.33)` → `ValueError`.

## TC-05: Validacion de vlr_hora negativo
- Dado `vlr_hora` negativo, la funcion debe lanzar `ValueError`.
- Ejemplo: `liquidar_nomina(2_000_000, 0, 0, -1)` → `ValueError`.

## TC-06: Recargo por horas extras diurnas (25%)
- Dado `salario_base = 2_000_000`, `vlr_hora = 8_333.33` y `horas_extras_diurnas = 10`, el recargo diurno debe ser `10 * 8_333.33 * 0.25 = 20_833.33`.

## TC-07: Recargo por horas extras nocturnas (75%)
- Dado `salario_base = 2_000_000`, `vlr_hora = 8_333.33` y `horas_extras_nocturnas = 5`, el recargo nocturno debe ser `5 * 8_333.33 * 0.75 = 31_250.00`.

## TC-08: Recargos mixtos (diurnas + nocturnas)
- Con 10 diurnas y 5 nocturnas, `subtotal_recargos = 20_833.33 + 31_250.00 = 52_083.33`.

## TC-09: Deducciones de seguridad social (salud + pension)
- Dado `total_devengado = salario_base + subtotal_recargos`:
  - `descuento_salud = total_devengado * 0.04`
  - `descuento_pension = total_devengado * 0.04`
- Ejemplo: `salario_base = 2_000_000`, sin horas extras → `descuento_salud = 80_000`, `descuento_pension = 80_000`.

## TC-10: Auxilio de transporte
- Si `salario_base <= 2_600_000`, se suma `auxilio_transporte = 162_000`.
- Si `salario_base > 2_600_000`, `auxilio_transporte = 0`.
- Ejemplos:
  - `salario_base = 1_500_000` → `auxilio_transporte = 162_000`
  - `salario_base = 3_000_000` → `auxilio_transporte = 0`

## TC-11: Limite exacto del auxilio de transporte
- Dado `salario_base = 2_600_000` (exactamente 2 SMLV), `vlr_hora = 10_833.33` y sin horas extras, el auxilio de transporte debe ser `162_000` porque el salario es menor o igual al limite.
- Ejemplo: `liquidar_nomina(2_600_000, 0, 0, 10_833.33)` → `auxilio_transporte = 162_000`, `neto_pagar = 2_600_000 - 104_000 - 104_000 + 162_000 = 2_554_000`.

## TC-12: Caso mixto completo con validacion de todos los campos
- Dado `salario_base = 2_300_000`, `vlr_hora = 9_583.33`, `horas_extras_diurnas = 4` y `horas_extras_nocturnas = 3`, se deben validar todos los campos del diccionario retornado (usar `pytest.approx` con tolerancia de 0.02 por precision de punto flotante):
  - `subtotal_recargos ≈ 31_145.82` = 4 * (9_583.33 * 0.25) + 3 * (9_583.33 * 0.75)
  - `total_devengado ≈ 2_331_145.82`
  - `descuento_salud ≈ 93_245.83`
  - `descuento_pension ≈ 93_245.83`
  - `auxilio_transporte = 162_000` (salario <= 2.600.000)
  - `neto_pagar ≈ 2_306_654.16`

## TC-13: Salario alto sin auxilio de transporte con horas extras
- Dado `salario_base = 4_000_000`, `vlr_hora = 16_666.67`, `horas_extras_diurnas = 8` y `horas_extras_nocturnas = 2`, el sistema NO debe otorgar auxilio de transporte porque el salario supera los 2 SMLV. (usar `pytest.approx` con tolerancia de 0.02 por precision de punto flotante)
  - `subtotal_recargos ≈ 58_333.34`
  - `total_devengado ≈ 4_058_333.35`
  - `descuento_salud ≈ 162_333.33`
  - `descuento_pension ≈ 162_333.33`
  - `auxilio_transporte = 0`
  - `neto_pagar ≈ 3_733_666.68`
