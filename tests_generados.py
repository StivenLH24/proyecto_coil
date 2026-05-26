import pytest
from engine import liquidar_nomina

def test_salario_minimo_legal_vigente():
    with pytest.raises(ValueError):
        liquidar_nomina(1_000_000, 0, 0, 5_416.67)

def test_salario_base_negativo():
    with pytest.raises(ValueError):
        liquidar_nomina(-1, 0, 0, 5_416.67)

def test_horas_extras_diurnas_negativas():
    with pytest.raises(ValueError):
        liquidar_nomina(2_000_000, -5, 0, 8_333.33)

def test_horas_extras_nocturnas_negativas():
    with pytest.raises(ValueError):
        liquidar_nomina(2_000_000, 0, -3, 8_333.33)

def test_vlr_hora_negativo():
    with pytest.raises(ValueError):
        liquidar_nomina(2_000_000, 0, 0, -1)

def test_recargo_diurno():
    result = liquidar_nomina(2_000_000, 10, 0, 8_333.33)
    assert pytest.approx(result["subtotal_recargos"], abs=0.02) == 20_833.33

def test_recargo_nocturno():
    result = liquidar_nomina(2_000_000, 0, 5, 8_333.33)
    assert pytest.approx(result["subtotal_recargos"], abs=0.02) == 31_250.00

def test_recargos_mixtos():
    result = liquidar_nomina(2_000_000, 10, 5, 8_333.33)
    assert pytest.approx(result["subtotal_recargos"], abs=0.02) == 52_083.33

def test_deducciones_seguridad_social():
    result = liquidar_nomina(2_000_000, 0, 0, 8_333.33)
    assert pytest.approx(result["descuento_salud"], abs=0.02) == 80_000
    assert pytest.approx(result["descuento_pension"], abs=0.02) == 80_000

def test_auxilio_transporte():
    result = liquidar_nomina(1_500_000, 0, 0, 10_833.33)
    assert pytest.approx(result["auxilio_transporte"], abs=0.02) == 162_000

def test_auxilio_transporte_exacto_limite():
    result = liquidar_nomina(2_600_000, 0, 0, 10_833.33)
    assert pytest.approx(result["auxilio_transporte"], abs=0.02) == 162_000

def test_caso_mixto_completo():
    result = liquidar_nomina(2_300_000, 4, 3, 9_583.33)
    assert pytest.approx(result["subtotal_recargos"], abs=0.02) == 31_145.82
    assert pytest.approx(result["total_devengado"], abs=0.02) == 2_331_145.82
    assert pytest.approx(result["descuento_salud"], abs=0.02) == 93_245.83
    assert pytest.approx(result["descuento_pension"], abs=0.02) == 93_245.83
    assert pytest.approx(result["auxilio_transporte"], abs=0.02) == 162_000
    assert pytest.approx(result["neto_pagar"], abs=0.02) == 2_306_654.16

def test_salario_alto_sin_auxilio_de_transporte():
    result = liquidar_nomina(4_000_000, 8, 2, 16_666.67)
    assert pytest.approx(result["subtotal_recargos"], abs=0.02) == 58_333.34
    assert pytest.approx(result["total_devengado"], abs=0.02) == 4_058_333.35
    assert pytest.approx(result["descuento_salud"], abs=0.02) == 162_333.33
    assert pytest.approx(result["descuento_pension"], abs=0.02) == 162_333.33
    assert pytest.approx(result["auxilio_transporte"], abs=0.02) == 0
    assert pytest.approx(result["neto_pagar"], abs=0.02) == 3_733_666.68