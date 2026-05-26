"""
agent.py — Guardian Agent: Generador automático de pruebas Pytest.

Lee engine.py y casos_prueba.md, usa LangChain + Ollama (llama3:8b)
para generar un archivo test_generated.py con pruebas Pytest válidas.
"""

import logging
import re
import sys
from pathlib import Path

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

RUTA_ENGINE = Path("engine.py")
RUTA_CASOS = Path("casos_prueba.md")
RUTA_SALIDA = Path("test_generated.py")
MODELO = "llama3:latest"
TIMEOUT = 180


def leer_archivo(ruta: Path) -> str:
    """Lee un archivo y retorna su contenido como string."""
    if not ruta.exists():
        log.error("Archivo no encontrado: %s", ruta)
        sys.exit(1)
    contenido = ruta.read_text(encoding="utf-8")
    log.info("Leído %s (%d caracteres)", ruta.name, len(contenido))
    return contenido


def construir_prompt(codigo_engine: str, casos_prueba: str) -> str:
    """Construye el prompt para el LLM."""
    template = PromptTemplate.from_template(
        """Eres un ingeniero de calidad experto en Python y Pytest.

A continuacion recibes el codigo fuente de un motor de nomina colombiano
y una especificacion de escenarios de validacion. Debes generar un archivo
de pruebas Pytest completo, valido y CORRECTO numericamente.

## Codigo fuente (engine.py)
```python
{codigo_engine}
```

## Escenarios de validacion
{casos_prueba}

## INSTRUCCIONES ESTRICTAS (SIGUE CADA UNA)

### Reglas de formato
1. Genera SOLO codigo Python valido con pruebas Pytest.
2. NO incluyas explicaciones ni texto adicional fuera del codigo.
3. NO envuelvas el codigo en bloques markdown.
4. Importa la funcion `liquidar_nomina` desde `engine`.
5. Usa `pytest.approx(valor, abs=0.02)` para toda comparacion numerica.

### Estructura de las pruebas (OBLIGATORIO)
- Crea UNA funcion de prueba POR cada escenario (NO uses parametrize).
- Las funciones de prueba deben llamarse `test_tcXX_descripcion()`.
- Cada funcion de prueba debe tener exactamente UN assert por campo validado.

### Pruebas de error (ValueError)
Para escenarios que deben lanzar ValueError, usa EXACTAMENTE este patron:
```python
def test_tcXX_descripcion():
    with pytest.raises(ValueError):
        liquidar_nomina(...)
```
NO uses el parametro `match` en pytest.raises.

### Pruebas de valores correctos
La funcion `liquidar_nomina` retorna un diccionario con estas claves:
- "subtotal_recargos" (float)
- "total_devengado" (float)
- "descuento_salud" (float)
- "descuento_pension" (float)
- "neto_pagar_antes_auxilio" (float)
- "auxilio_transporte" (float)
- "neto_pagar" (float)

Para validar, usa EXACTAMENTE este patron:
```python
def test_tcXX_descripcion():
    resultado = liquidar_nomina(salario_base, horas_extras_diurnas, horas_extras_nocturnas, vlr_hora)
    assert resultado["clave"] == pytest.approx(valor_esperado, abs=0.02)
```

### Reglas de calculo (MUY IMPORTANTE - USA ESTAS FORMULAS)
- Recargo diurno por hora = vlr_hora * RECARGO_DIURNO (donde RECARGO_DIURNO = 0.25)
- Recargo nocturno por hora = vlr_hora * RECARGO_NOCTURNO (donde RECARGO_NOCTURNO = 0.75)
- subtotal_recargos = (horas_extras_diurnas * recargo_diurno_por_hora) + (horas_extras_nocturnas * recargo_nocturno_por_hora)
- total_devengado = salario_base + subtotal_recargos
- descuento_salud = total_devengado * DEDICCION_SEGURIDAD_SOCIAL (donde DEDICCION_SEGURIDAD_SOCIAL = 0.04)
- descuento_pension = total_devengado * DEDICCION_SEGURIDAD_SOCIAL (donde DEDICCION_SEGURIDAD_SOCIAL = 0.04)
- auxilio_transporte = 162000 si salario_base <= 2600000, sino 0
- neto_pagar = total_devengado - descuento_salud - descuento_pension + auxilio_transporte

### Validacion numerica
CALCULA LOS VALORES ESPERADOS TU MISMO usando las formulas exactas.
- Para vlr_hora = 8333.33 y 10 horas diurnas: recargo = 10 * 8333.33 * 0.25 = 20833.32
- Para vlr_hora = 8333.33 y 5 horas nocturnas: recargo = 5 * 8333.33 * 0.75 = 31249.99
- NO confundas subtotal_recargos con total_devengado.
- Verifica que los decimales sean correctos.

Genera el codigo de prueba AHORA:"""
    )
    return template.format(
        codigo_engine=codigo_engine, casos_prueba=casos_prueba
    )


def limpiar_codigo(respuesta: str) -> str:
    """Extrae el código Python de la respuesta del LLM."""
    patron = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)
    coincidencias = patron.findall(respuesta)
    if coincidencias:
        return coincidencias[0].strip()
    return respuesta.strip()


def generar_pruebas() -> str:
    """Genera test_generated.py usando LangChain + Ollama."""
    codigo_engine = leer_archivo(RUTA_ENGINE)
    casos_prueba = leer_archivo(RUTA_CASOS)
    prompt = construir_prompt(codigo_engine, casos_prueba)

    log.info("Conectando a Ollama con modelo %s...", MODELO)

    llm = OllamaLLM(
        model=MODELO,
        temperature=0.0,
        num_predict=8192,
        timeout=TIMEOUT,
    )

    log.info("Enviando prompt al modelo...")
    respuesta = llm.invoke(prompt)
    log.info("Respuesta recibida (%d caracteres)", len(respuesta))

    codigo_generado = limpiar_codigo(respuesta)

    if not codigo_generado:
        log.error("El modelo no generó código válido.")
        sys.exit(1)

    return codigo_generado


def guardar_pruebas(codigo: str) -> None:
    """Guarda el código generado en test_generated.py."""
    RUTA_SALIDA.write_text(codigo, encoding="utf-8")
    lineas = codigo.strip().count("\n") + 1
    log.info("Guardado %s (%d líneas)", RUTA_SALIDA.name, lineas)


def validar_pruebas_generadas() -> bool:
    """Valida que el archivo generado contenga elementos esenciales."""
    codigo = RUTA_SALIDA.read_text(encoding="utf-8")
    check_list = {
        "import": "from engine import" in codigo or "import engine" in codigo,
        "funcion_test": "def test_" in codigo,
        "assert": "assert" in codigo,
        "liquidar_nomina": "liquidar_nomina" in codigo,
    }
    for name, ok in check_list.items():
        if not ok:
            log.warning("Validación fallida: falta '%s' en el código generado", name)
            return False
    log.info("Validación del código generado: OK")
    return True


def main() -> None:
    """Punto de entrada principal."""
    log.info("=== Guardian Agent — Generación de Pruebas ===")
    codigo = generar_pruebas()
    guardar_pruebas(codigo)
    if not validar_pruebas_generadas():
        log.warning("El código generado podría estar incompleto.")
    log.info("Proceso completado. Revisa 'test_generated.py'.")


if __name__ == "__main__":
    main()
