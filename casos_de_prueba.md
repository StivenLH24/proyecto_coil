# casos_prueba.md

# Matriz de Casos de Prueba – Sistema de Nómina

## Caso de Prueba CP-01
- **Historia de Usuario:** US-NOM02
- **Regla de Negocio:** R1
- **Escenario:** Empleado sin horas extras y con subsidio de transporte.
- **Datos de Entrada:**
  - Salario Base: $2.000.000
  - Horas Extras Diurnas: 0
  - Horas Extras Nocturnas: 0
- **Resultado Esperado:**
  - El sistema calcula correctamente el salario neto.
  - Se aplica subsidio de transporte.
  - Se realiza descuento del 8% correspondiente a salud y pensión.

---

## Caso de Prueba CP-02
- **Historia de Usuario:** US-NOM02
- **Regla de Negocio:** R2
- **Escenario:** Validar salario exactamente igual al límite permitido para subsidio.
- **Datos de Entrada:**
  - Salario Base: $2.600.000
  - Horas Extras Diurnas: 0
  - Horas Extras Nocturnas: 0
- **Resultado Esperado:**
  - El sistema debe otorgar subsidio de transporte.
  - El salario cumple exactamente el umbral permitido.

---

## Caso de Prueba CP-03
- **Historia de Usuario:** US-NOM02
- **Regla de Negocio:** R3
- **Escenario:** Validar cálculo de horas extras diurnas.
- **Datos de Entrada:**
  - Salario Base: $1.800.000
  - Horas Extras Diurnas: 5
  - Horas Extras Nocturnas: 0
- **Resultado Esperado:**
  - El sistema calcula correctamente el valor adicional de las horas extras diurnas.

---

## Caso de Prueba CP-04
- **Historia de Usuario:** US-NOM02
- **Regla de Negocio:** R4
- **Escenario:** Validar cálculo de horas extras nocturnas.
- **Datos de Entrada:**
  - Salario Base: $1.800.000
  - Horas Extras Diurnas: 0
  - Horas Extras Nocturnas: 4
- **Resultado Esperado:**
  - El sistema calcula correctamente el valor adicional de las horas extras nocturnas.

---

## Caso de Prueba CP-05
- **Historia de Usuario:** US-NOM02
- **Regla de Negocio:** R5
- **Escenario:** Validar deducción exacta del 8%.
- **Datos de Entrada:**
  - Salario Base: $2.000.000
  - Horas Extras Diurnas: 0
  - Horas Extras Nocturnas: 0
- **Resultado Esperado:**
  - El sistema realiza una deducción exacta de $160.000.
  - El descuento corresponde al 8% del salario base.

---

## Caso de Prueba CP-06
- **Historia de Usuario:** US-NOM02
- **Regla de Negocio:** R3, R4 y R5
- **Escenario:** Caso mixto con horas extras diurnas y nocturnas.
- **Datos de Entrada:**
  - Salario Base: $2.300.000
  - Horas Extras Diurnas: 3
  - Horas Extras Nocturnas: 2
- **Resultado Esperado:**
  - El sistema suma correctamente ambos tipos de horas extras.
  - El sistema aplica correctamente las deducciones legales.

---

## Caso de Prueba CP-07
- **Historia de Usuario:** US-NOM02
- **Regla de Negocio:** R2, R3, R4 y R5
- **Escenario:** Caso mixto cercano al límite del subsidio.
- **Datos de Entrada:**
  - Salario Base: $2.550.000
  - Horas Extras Diurnas: 2
  - Horas Extras Nocturnas: 3
- **Resultado Esperado:**
  - El sistema mantiene el subsidio de transporte.
  - El sistema calcula correctamente horas extras y deducciones.

---

## Caso de Prueba CP-08
- **Historia de Usuario:** US-NOM02
- **Regla de Negocio:** R1
- **Escenario:** Ingreso de horas extras negativas.
- **Datos de Entrada:**
  - Salario Base: $2.000.000
  - Horas Extras Diurnas: -2
  - Horas Extras Nocturnas: 0
- **Resultado Esperado:**
  - El sistema debe lanzar una excepción o mensaje de error.
  - No se permite registrar horas negativas.

---

## Caso de Prueba CP-09
- **Historia de Usuario:** US-NOM02
- **Regla de Negocio:** R1
- **Escenario:** Ingreso de horas nocturnas negativas.
- **Datos de Entrada:**
  - Salario Base: $2.000.000
  - Horas Extras Diurnas: 0
  - Horas Extras Nocturnas: -5
- **Resultado Esperado:**
  - El sistema debe impedir el cálculo.
  - Debe mostrarse un mensaje de validación de datos inválidos.

---

## Caso de Prueba CP-10
- **Historia de Usuario:** US-NOM02
- **Regla de Negocio:** R2 y R5
- **Escenario:** Empleado que supera el límite del subsidio.
- **Datos de Entrada:**
  - Salario Base: $2.600.001
  - Horas Extras Diurnas: 0
  - Horas Extras Nocturnas: 0
- **Resultado Esperado:**
  - El sistema NO debe otorgar subsidio de transporte.
  - El sistema debe aplicar únicamente las deducciones legales.

---

# Reglas de Negocio

## R1
El sistema debe validar que los valores ingresados sean positivos y válidos.

## R2
El subsidio de transporte se otorga únicamente a salarios menores o iguales a $2.600.000.

## R3
Las horas extras diurnas deben calcularse con el recargo correspondiente definido por la empresa.

## R4
Las horas extras nocturnas deben calcularse con el recargo correspondiente definido por la empresa.

## R5
El sistema debe aplicar una deducción total del 8% correspondiente a salud y pensión.