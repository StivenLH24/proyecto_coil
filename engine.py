# engine.py
# Requiere Python 3.11+

from __future__ import annotations

SALARIO_MINIMO_LEGAL_VIGENTE: float = 1_300_000.0
SALARIO_MAXIMO_AUXILIO_TRANSPORTE: float = 2_600_000.0
AUXILIO_TRANSPORTE: float = 162_000.0
HORAS_MENSUALES: float = 240.0
RECARGO_DIURNO: float = 0.25
RECARGO_NOCTURNO: float = 0.75
DEDICCION_SEGURIDAD_SOCIAL: float = 0.04


def liquidar_nomina(
    salario_base: float,
    horas_extras_diurnas: int,
    horas_extras_nocturnas: int,
) -> dict[str, float]:
    """Liquidar nómina mensual con recargos de horas extras y deducciones legales.

    Esta función calcula la liquidación de nómina para un empleado en Colombia y devuelve
    los valores intermedios necesarios para auditoría.

    Args:
        salario_base (float): Salario base mensual del empleado en pesos colombianos.
        horas_extras_diurnas (int): Número de horas extras diurnas trabajadas.
        horas_extras_nocturnas (int): Número de horas extras nocturnas trabajadas.

    Returns:
        dict[str, float]: Un diccionario con los montos calculados de la nómina.
            - subtotal_recargos: valor total de los recargos por horas extras.
            - total_devengado: salario base más recargos por horas extras.
            - descuento_salud: deducción de salud (4% del total devengado).
            - descuento_pension: deducción de pensión (4% del total devengado).
            - neto_pagar_antes_auxilio: neto a pagar antes de auxilio de transporte.
            - auxilio_transporte: valor del subsidio de transporte si aplica.
            - neto_pagar: neto a pagar final incluyendo auxilio de transporte.

    Raises:
        ValueError: Si el salario base está por debajo del salario mínimo legal vigente.
        ValueError: Si alguno de los valores de entrada es negativo.
    """
    # R1: Validar salario mínimo legal vigente.
    if salario_base < SALARIO_MINIMO_LEGAL_VIGENTE:
        raise ValueError(
            "El salario_base no puede ser inferior al salario mínimo legal vigente de $1.300.000."
        )

    # R2: Validar que no se acepten valores negativos para salario u horas extras.
    if salario_base < 0:
        raise ValueError("El salario_base no puede ser negativo.")
    if horas_extras_diurnas < 0:
        raise ValueError("Las horas_extras_diurnas no pueden ser negativas.")
    if horas_extras_nocturnas < 0:
        raise ValueError("Las horas_extras_nocturnas no pueden ser negativas.")

    # R3: Calcular el valor de la hora ordinaria con base en una jornada de 240 horas al mes.
    valor_hora_ordinaria: float = salario_base / HORAS_MENSUALES

    # R4: Aplicar recargos de 25% para horas extras diurnas y 75% para horas extras nocturnas.
    valor_recargo_diurno: float = valor_hora_ordinaria * RECARGO_DIURNO
    valor_recargo_nocturno: float = valor_hora_ordinaria * RECARGO_NOCTURNO

    subtotal_recargos: float = (
        horas_extras_diurnas * valor_recargo_diurno
        + horas_extras_nocturnas * valor_recargo_nocturno
    )

    total_devengado: float = salario_base + subtotal_recargos

    # R6: Calcular deducciones de seguridad social sobre el total devengado.
    descuento_salud: float = total_devengado * DEDICCION_SEGURIDAD_SOCIAL
    descuento_pension: float = total_devengado * DEDICCION_SEGURIDAD_SOCIAL
    neto_pagar_antes_auxilio: float = (
        total_devengado - descuento_salud - descuento_pension
    )

    # R6: Aplicar auxilio de transporte solo si el salario base es menor o igual a 2 SMLV.
    # El auxilio de transporte no se incluye para el cálculo de las deducciones.
    auxilio_transporte: float = (
        AUXILIO_TRANSPORTE
        if salario_base <= SALARIO_MAXIMO_AUXILIO_TRANSPORTE
        else 0.0
    )
    neto_pagar: float = neto_pagar_antes_auxilio + auxilio_transporte

    return {
        "subtotal_recargos": subtotal_recargos,
        "total_devengado": total_devengado,
        "descuento_salud": descuento_salud,
        "descuento_pension": descuento_pension,
        "neto_pagar_antes_auxilio": neto_pagar_antes_auxilio,
        "auxilio_transporte": auxilio_transporte,
        "neto_pagar": neto_pagar,
    }
