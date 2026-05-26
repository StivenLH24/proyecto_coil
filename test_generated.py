import pytest
from engine import liquidar_nomina

def test_tc01_salario_minimo_legal_vigente():
    with pytest.raises(ValueError):
        liquidar_nomina(1_000_000, 0, 0, 5_416.67)

def test_tc02_salario_base_negativo():
    with pytest.raises(ValueError):
        liquidar_nomina(-1, 0, 0, 5_416.67)

def test_tc03_horas_extras_diurnas_negativas():
    with pytest.raises(ValueError):
        liquidar_nomina(2_000_000, -5, 0, 8_333.33)

def test_tc04_horas_extras_nocturnas_negativas():
    with pytest.raises(ValueError):
        liquidar_nomina(2_000_000, 0, -3, 8_333.33)

def test_tc05_vlr_hora_negativo():
    with pytest.raises(ValueError):
        liquidar_nomina(2_000_000, 0, 0, -1)

def test_tc06_recargo_diurno():
    resultado = liquidar_nomina(2_000_000, 10, 0, 8_333.33)
    assert resultado["subtotal_recargos"] == pytest.approx(20_833.33, abs=0.02)

def test_tc07_recargo_nocturno():
    resultado = liquidar_nomina(2_000_000, 0, 5, 8_333.33)
    assert resultado["subtotal_recargos"] == pytest.approx(31_250.00, abs=0.02)

def test_tc08_recargos_mixtos():
    resultado = liquidar_nomina(2_000_000, 10, 5, 8_333.33)
    assert resultado["subtotal_recargos"] == pytest.approx(52_083.33, abs=0.02)

def test_tc09_deducciones_seguridad_social():
    resultado = liquidar_nomina(2_000_000, 0, 0, 8_333.33)
    assert resultado["descuento_salud"] == pytest.approx(80_000.00, abs=0.02)
    assert resultado["descuento_pension"] == pytest.approx(80_000.00, abs=0.02)

def test_tc10_auxilio_transporte():
    resultado = liquidar_nomina(1_500_000, 0, 0, 10_833.33)
    assert resultado["auxilio_transporte"] == 162_000

def test_tc11_limite_exacto_auxilio_transporte():
    resultado = liquidar_nomina(2_600_000, 0, 0, 10_833.33)
    assert resultado["auxilio_transporte"] == 162_000
    assert resultado["neto_pagar"] == pytest.approx(2_554_000, abs=0.02)

def test_tc12_caso_mixto_completo():
    resultado = liquidar_nomina(2_300_000, 4, 3, 9_583.33)
    assert resultado["subtotal_recargos"] == pytest.approx(31_145.82, abs=0.02)
    assert resultado["total_devengado"] == pytest.approx(2_331_145.82, abs=0.02)
    assert resultado["descuento_salud"] == pytest.approx(93_245.83, abs=0.02)
    assert resultado["descuento_pension"] == pytest.approx(93_245.83, abs=0.02)
    assert resultado["auxilio_transporte"] == 162_000
    assert resultado["neto_pagar"] == pytest.approx(2_306_654.16, abs=0.02)

def test_tc13_salario_alto_sin_auxilio_transporte():
    resultado = liquidar_nomina(4_000_000, 8, 2, 16_666.67)
    assert resultado["subtotal_recargos"] == pytest.approx(58_333.34, abs=0.02)
    assert resultado["total_devengado"] == pytest.approx(4_058_333.35, abs=0.02)
    assert resultado["descuento_salud"] == pytest.approx(162_333.33, abs=0.02)
    assert resultado["descuento_pension"] == pytest.approx(162_333.33, abs=0.02)
    assert resultado["auxilio_transporte"] == 0
    assert resultado["neto_pagar"] == pytest.approx(3_733_666.68, abs=0.02)