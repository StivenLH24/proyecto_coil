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
MODELO = "llama3:8b"
TIMEOUT = 120


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

A continuación recibes el código fuente de un motor de nómina colombiano
y una especificación de casos de prueba. Debes generar un archivo de
pruebas Pytest completo y válido.

## Código fuente (engine.py)
```python
{codigo_engine}
```

## Casos de prueba
{casos_prueba}

## Instrucciones
1. Genera SOLO código Python válido con pruebas Pytest.
2. NO incluyas explicaciones ni texto adicional.
3. NO envuelvas el código en bloques markdown.
4. Importa la función `liquidar_nomina` desde `engine`.
5. Cada función de prueba debe tener un assert.
6. Usa `pytest.approx` para comparaciones con decimales.
7. Cubre TODAS las reglas R1 a R5.
8. Incluye al menos un caso feliz y uno de error por regla.

Genera el código de prueba ahora:"""
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
        temperature=0.1,
        num_predict=4096,
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
