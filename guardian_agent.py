"""
guardian_agent.py — Agente Guardian: Generación y ejecución automática de pruebas.

Requiere Python 3.11+, LangChain, Ollama (qwen2.5-coder:7b) y Docker.

Flujo:
    PASO 1: Leer casos_prueba.md
    PASO 2: Generar tests_generados.py
    PASO 3: Generar Dockerfile.guardian
    PASO 4: Construir entorno Docker de pruebas aislado
    PASO 5: Ejecutar pytest dentro del contenedor
    PASO 6: Guardar veredicto auditable

Uso:
    python3 guardian_agent.py
"""

import json
import logging
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("guardian_agent")

RUTA_ENGINE = Path("engine.py")
RUTA_CASOS = Path("casos_prueba.md")
RUTA_TESTS = Path("tests_generados.py")
RUTA_DOCKERFILE = Path("Dockerfile.guardian")
RUTA_VEREDICTO = Path("veredicto.json")

MODELO = "qwen2.5-coder:7b"
TIMEOUT_LLM = 120
TIMEOUT_DOCKER_BUILD = 120
TIMEOUT_DOCKER_RUN = 60
IMAGEN_DOCKER = "guardian-sandbox"

SYSTEM_PROMPT = """Eres un ingeniero de calidad experto en Python y Pytest.

A continuacion recibes el codigo fuente de un motor de nomina colombiano
y una especificacion de escenarios de validacion academica.
Debes generar un archivo de pruebas Pytest completo y valido.

## Codigo fuente (engine.py)
```python
{codigo_engine}
```

## Escenarios de validacion academica
{casos_prueba}

## Instrucciones
1. Genera SOLO codigo Python valido con pruebas Pytest.
2. NO incluyas explicaciones ni texto adicional.
3. NO envuelvas el codigo en bloques markdown.
4. Importa la funcion `liquidar_nomina` desde `engine`.
5. Cada funcion de prueba debe tener un assert.
6. Usa `pytest.approx` para comparaciones con decimales.
7. Cubre TODOS los escenarios de validacion TC-01 a TC-10 descritos.
8. Incluye al menos un caso feliz y uno de error por cada escenario.

Genera el codigo de prueba ahora:"""


# ──────────────────────────────────────────────
# PASO 1: Leer archivos
# ──────────────────────────────────────────────

def leer_archivo(ruta: Path) -> str:
    """Lee un archivo y retorna su contenido como string."""
    if not ruta.exists():
        log.error("Archivo no encontrado: %s", ruta)
        sys.exit(1)
    contenido = ruta.read_text(encoding="utf-8")
    log.info("PASO 1 — Leido %s (%d caracteres)", ruta.name, len(contenido))
    return contenido


# ──────────────────────────────────────────────
# PASO 2: Generar tests_generados.py via LangChain + Ollama
# ──────────────────────────────────────────────

def construir_prompt(codigo_engine: str, casos_prueba: str) -> str:
    template = PromptTemplate.from_template(SYSTEM_PROMPT)
    return template.format(
        codigo_engine=codigo_engine, casos_prueba=casos_prueba
    )


def limpiar_codigo(respuesta: str) -> str:
    patron = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)
    coincidencias = patron.findall(respuesta)
    if coincidencias:
        return coincidencias[0].strip()
    return respuesta.strip()


def generar_tests() -> str:
    """PASO 2: Genera tests_generados.py usando LangChain + Ollama."""
    codigo_engine = leer_archivo(RUTA_ENGINE)
    casos_prueba = leer_archivo(RUTA_CASOS)
    prompt = construir_prompt(codigo_engine, casos_prueba)

    log.info("PASO 2 — Conectando a Ollama con modelo %s...", MODELO)

    llm = OllamaLLM(
        model=MODELO,
        temperature=0.1,
        num_predict=4096,
        timeout=TIMEOUT_LLM,
    )

    log.info("PASO 2 — Enviando prompt al modelo...")
    respuesta = llm.invoke(prompt)
    log.info("PASO 2 — Respuesta recibida (%d caracteres)", len(respuesta))

    codigo_generado = limpiar_codigo(respuesta)

    if not codigo_generado:
        log.error("El modelo no genero codigo valido.")
        sys.exit(1)

    return codigo_generado


def guardar_tests(codigo: str) -> None:
    RUTA_TESTS.write_text(codigo, encoding="utf-8")
    lineas = codigo.strip().count("\n") + 1
    log.info("PASO 2 — Guardado %s (%d lineas)", RUTA_TESTS.name, lineas)


def validar_tests_generados() -> bool:
    codigo = RUTA_TESTS.read_text(encoding="utf-8")
    check_list = {
        "import": "from engine import" in codigo or "import engine" in codigo,
        "funcion_test": "def test_" in codigo,
        "assert": "assert" in codigo,
        "liquidar_nomina": "liquidar_nomina" in codigo,
    }
    for name, ok in check_list.items():
        if not ok:
            log.warning("Validacion: falta '%s' en el codigo generado", name)
            return False
    log.info("PASO 2 — Validacion del codigo generado: OK")
    return True


# ──────────────────────────────────────────────
# PASO 3: Generar Dockerfile.guardian
# ──────────────────────────────────────────────

CONTENIDO_DOCKERFILE = """FROM python:3.11-slim

WORKDIR /app

COPY engine.py .
COPY tests_generados.py .

RUN pip install pytest pytest-json-report

CMD ["pytest", "tests_generados.py", "--json-report", "--json-report-file=/app/veredicto.json"]
"""


def guardar_dockerfile() -> None:
    """Tool: Genera automaticamente el archivo Dockerfile.guardian."""
    RUTA_DOCKERFILE.write_text(CONTENIDO_DOCKERFILE.strip(), encoding="utf-8")
    log.info("PASO 3 — Generado %s", RUTA_DOCKERFILE.name)


# ──────────────────────────────────────────────
# PASO 4: Construir entorno Docker de pruebas aislado
# ──────────────────────────────────────────────

def obtener_ruta_montaje() -> str:
    ruta = Path.cwd().resolve()
    if sys.platform == "win32":
        ruta_str = str(ruta).replace("\\", "/")
        if ruta_str[1] == ":":
            ruta_str = f"/{ruta_str[0].lower()}{ruta_str[2:]}"
        return ruta_str
    return str(ruta)


def construir_imagen_docker() -> None:
    """PASO 4: Valida archivos y construye la imagen Docker."""
    for archivo in [RUTA_TESTS, RUTA_DOCKERFILE]:
        if not archivo.exists():
            log.error(
                "No se encuentra %s. Ejecute la generacion primero.",
                archivo.name,
            )
            sys.exit(1)

    log.info("PASO 4 — Construyendo imagen Docker '%s'...", IMAGEN_DOCKER)
    try:
        subprocess.run(
            [
                "docker", "build", "-t", IMAGEN_DOCKER,
                "-f", RUTA_DOCKERFILE.name, ".",
            ],
            check=True,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=TIMEOUT_DOCKER_BUILD,
        )
        log.info("PASO 4 — Imagen Docker construida exitosamente.")
    except subprocess.CalledProcessError as exc:
        log.error("Error al construir la imagen Docker:\n%s", exc.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        log.error("Tiempo de espera agotado al construir la imagen Docker.")
        sys.exit(1)


# ──────────────────────────────────────────────
# PASO 5: Ejecutar pytest dentro del contenedor
# ──────────────────────────────────────────────

def ejecutar_pruebas_docker() -> None:
    """PASO 5: Corre pytest dentro del contenedor y genera veredicto.json."""
    ruta_montaje = obtener_ruta_montaje()

    comando = [
        "docker", "run", "--rm",
        "--name", "guardian-sandbox",
        "-v", f"{ruta_montaje}:/app",
        "-w", "/app",
        IMAGEN_DOCKER,
    ]

    log.info("PASO 5 — Ejecutando pytest en contenedor Docker...")
    log.debug("Comando: %s", " ".join(comando))

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=TIMEOUT_DOCKER_RUN,
        )
        log.info("PASO 5 — Codigo de salida: %d", resultado.returncode)
        if resultado.stdout:
            log.info("stdout:\n%s", resultado.stdout)
        if resultado.stderr:
            log.warning("stderr:\n%s", resultado.stderr)
    except subprocess.TimeoutExpired:
        log.error("Contenedor excedio el tiempo maximo (%d s).", TIMEOUT_DOCKER_RUN)
        Path(RUTA_VEREDICTO).write_text(
            json.dumps({"summary": {"passed": 0, "failed": 1, "total": 1}}),
            encoding="utf-8",
        )


# ──────────────────────────────────────────────
# PASO 6: Guardar veredicto auditable
# ──────────────────────────────────────────────

def leer_reporte_pytest() -> dict:
    ruta_reporte = Path("veredicto.json")
    if not ruta_reporte.exists():
        log.warning("No se encontro veredicto.json generado por pytest.")
        return {"summary": {"passed": 0, "failed": 1, "total": 0}}

    with ruta_reporte.open(encoding="utf-8") as f:
        return json.load(f)


def generar_veredicto(reporte_pytest: dict) -> dict:
    """PASO 6: Construye el veredicto estructurado auditable."""
    summary = reporte_pytest.get("summary", {})
    tests_pasados = summary.get("passed", 0)
    tests_fallidos = summary.get("failed", 0)

    if tests_fallidos == 0:
        veredicto = "APROBADO"
    else:
        veredicto = "RECHAZADO"

    resultado = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "modelo_ia": MODELO,
        "tests_generados": RUTA_TESTS.name,
        "dockerfile": RUTA_DOCKERFILE.name,
        "tests_pasados": tests_pasados,
        "tests_fallidos": tests_fallidos,
        "veredicto": veredicto,
    }

    RUTA_VEREDICTO.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    log.info("PASO 6 — Guardado %s", RUTA_VEREDICTO.name)
    return resultado


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main() -> None:
    """Ejecuta el flujo completo del Agente Guardian (PASO 1 a PASO 6)."""
    log.info("=== Guardian Agent — Inicio ===")

    # PASO 1
    leer_archivo(RUTA_CASOS)

    # PASO 2
    codigo_tests = generar_tests()
    guardar_tests(codigo_tests)
    if not validar_tests_generados():
        log.warning("El codigo generado podria estar incompleto.")

    # PASO 3
    guardar_dockerfile()

    # PASO 4
    construir_imagen_docker()

    # PASO 5
    ejecutar_pruebas_docker()

    # PASO 6
    reporte = leer_reporte_pytest()
    veredicto = generar_veredicto(reporte)

    log.info("=== Veredicto Final ===")
    log.info("Modelo IA: %s", veredicto["modelo_ia"])
    log.info("Tests pasados: %d", veredicto["tests_pasados"])
    log.info("Tests fallidos: %d", veredicto["tests_fallidos"])
    log.info("Veredicto: %s", veredicto["veredicto"])

    print(f"\n{'=' * 50}")
    print(json.dumps(veredicto, indent=2, ensure_ascii=False))
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
