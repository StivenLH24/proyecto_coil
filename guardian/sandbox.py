"""
sandbox.py — Guardian Agent: Ejecutor aislado de pruebas en Docker.

Construye la imagen Docker, lanza un contenedor con --rm que monta
el directorio actual, ejecuta pytest con pytest-json-report y emite
un veredicto auditable (APROBADO / RECHAZADO).
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

IMAGEN = "guardian-sandbox"
CONTENEDOR = "guardian-sandbox"
DOCKERFILE = "guardian/Dockerfile"
REPORTE = ".report.json"
TIMEOUT_SEG = 60


def construir_imagen() -> None:
    """Construye la imagen Docker del sandbox."""
    log.info("Construyendo imagen Docker '%s'...", IMAGEN)
    try:
        subprocess.run(
            ["docker", "build", "-t", IMAGEN, "-f", DOCKERFILE, "."],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        log.info("Imagen Docker construida exitosamente.")
    except subprocess.CalledProcessError as exc:
        log.error("Error al construir la imagen Docker:\n%s", exc.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        log.error("Tiempo de espera agotado al construir la imagen Docker.")
        sys.exit(1)


def obtener_ruta_montaje() -> str:
    """Retorna la ruta absoluta del directorio actual para montar en Docker."""
    ruta = Path.cwd().resolve()
    if sys.platform == "win32":
        ruta_str = str(ruta).replace("\\", "/")
        if ruta_str[1] == ":":
            ruta_str = f"/{ruta_str[0].lower()}{ruta_str[2:]}"
        return ruta_str
    return str(ruta)


def ejecutar_pruebas() -> None:
    """Ejecuta pytest dentro del contenedor Docker."""
    ruta_montaje = obtener_ruta_montaje()

    comando = [
        "docker", "run", "--rm",
        "--name", CONTENEDOR,
        "-v", f"{ruta_montaje}:/app",
        "-w", "/app",
        IMAGEN,
        "test_generated.py",
        "--json-report", "--json-report-file=.report.json",
    ]

    log.info("Ejecutando contenedor Docker...")
    log.debug("Comando: %s", " ".join(comando))

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SEG,
        )
        log.info("Código de salida: %d", resultado.returncode)
        if resultado.stdout:
            log.info("stdout:\n%s", resultado.stdout)
        if resultado.stderr:
            log.warning("stderr:\n%s", resultado.stderr)
    except subprocess.TimeoutExpired:
        log.error("Contenedor excedió el tiempo máximo (%d s).", TIMEOUT_SEG)
        # Crear reporte de timeout para que leer_reporte() lo procese
        Path(REPORTE).write_text(
            json.dumps({"summary": {"passed": 0, "failed": 1, "total": 1}}),
            encoding="utf-8",
        )


def leer_reporte() -> dict:
    """Lee el archivo .report.json generado por pytest-json-report."""
    ruta_reporte = Path(REPORTE)
    if not ruta_reporte.exists():
        log.warning("No se encontró %s. Se asume error de ejecución.", REPORTE)
        return {"passed": 0, "failed": 1, "tests": []}

    with ruta_reporte.open(encoding="utf-8") as f:
        reporte = json.load(f)

    log.info(
        "Reporte: %d passed, %d failed, %d total",
        reporte.get("summary", {}).get("passed", 0),
        reporte.get("summary", {}).get("failed", 0),
        reporte.get("summary", {}).get("total", 0),
    )
    return reporte


def emitir_veredicto(reporte: dict) -> dict:
    """Evalúa el reporte y emite un veredicto estructurado.

    Returns:
        dict con claves: passed, failed, bugs_detectados, veredicto
    """
    summary = reporte.get("summary", {})
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)

    if failed == 0:
        veredicto = "APROBADO"
        bugs = 0
    else:
        veredicto = "RECHAZADO"
        bugs = failed

    resultado = {
        "passed": passed,
        "failed": failed,
        "bugs_detectados": bugs,
        "veredicto": veredicto,
    }
    return resultado


def main() -> None:
    """Punto de entrada principal del sandbox."""
    log.info("=== Guardian Agent — Sandbox de Pruebas ===")

    construir_imagen()

    ejecutar_pruebas()

    reporte = leer_reporte()
    veredicto = emitir_veredicto(reporte)

    log.info("=== Veredicto ===")
    log.info("Passed: %d", veredicto["passed"])
    log.info("Failed: %d", veredicto["failed"])
    log.info("Bugs detectados: %d", veredicto["bugs_detectados"])
    log.info("Veredicto: %s", veredicto["veredicto"])

    salida_json = json.dumps(veredicto, indent=2, ensure_ascii=False)
    print(f"\n{'-' * 40}")
    print("RESULTADO FINAL:")
    print(salida_json)


if __name__ == "__main__":
    main()
