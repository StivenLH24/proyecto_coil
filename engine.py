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
        dict[str, float]: Resultado de la liquidación de nómina con subtotal de recargos de horas extras y deducciones.
    """
    horas_ordinarias_valor: float = salario_base / 240.0
    recargo_diurno: float = horas_ordinarias_valor * 0.25
    recargo_nocturno: float = horas_ordinarias_valor * 0.75

    subtotal_recargos: float = (
        horas_extras_diurnas * recargo_diurno
        + horas_extras_nocturnas * recargo_nocturno
    )

    total_devengado: float = salario_base + subtotal_recargos
    descuento_salud: float = total_devengado * 0.04
    descuento_pension: float = total_devengado * 0.04
    neto_pagar: float = total_devengado - descuento_salud - descuento_pension

    auxilio_transporte: float = 162_000.0 if salario_base <= 2_600_000.0 else 0.0
    neto_pagar_final: float = neto_pagar + auxilio_transporte

    return {
        "subtotal_recargos": subtotal_recargos,
        "total_devengado": total_devengado,
        "descuento_salud": descuento_salud,
        "descuento_pension": descuento_pension,
        "neto_pagar": neto_pagar_final,
        "auxilio_transporte": auxilio_transporte,
        "neto_pagar_antes_auxilio": neto_pagar,
    }
