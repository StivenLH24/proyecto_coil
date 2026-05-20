# engine.py
# Requiere Python 3.11+

from __future__ import annotations


def liquidar_nomina(
    salario_base: float,
    horas_extras_diurnas: int,
    horas_extras_nocturnas: int,
) -> dict[str, float]:
    """Calcular la nómina de un empleado.

    Args:
        salario_base (float): Salario base mensual del empleado.
        horas_extras_diurnas (int): Cantidad de horas extras diurnas trabajadas.
        horas_extras_nocturnas (int): Cantidad de horas extras nocturnas trabajadas.

    Returns:
        dict[str, float]: Resultado de la liquidación de nómina con subtotal de recargos de horas extras.
    """
    horas_ordinarias_valor: float = salario_base / 240.0
    recargo_diurno: float = horas_ordinarias_valor * 0.25
    recargo_nocturno: float = horas_ordinarias_valor * 0.75

    subtotal_recargos: float = (
        horas_extras_diurnas * recargo_diurno
        + horas_extras_nocturnas * recargo_nocturno
    )

    return {
        "subtotal_recargos": subtotal_recargos,
    }
