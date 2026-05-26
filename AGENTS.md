# proyecto_coil

Colombian payroll (nómina) calculation engine.

## Requirements

- **Python 3.11+** (uses `from __future__ import annotations`)

## Structure

- `engine.py` — single-module library with one public function `liquidar_nomina(salario_base, horas_extras_diurnas, horas_extras_nocturnas, vlr_hora)`. No package layout, no entrypoint script.

## Key constants (Colombian labor law 2025/2026)

| Constant | Value |
|---|---|
| `SALARIO_MINIMO_LEGAL_VIGENTE` | 1,300,000 |
| `AUXILIO_TRANSPORTE` | 162,000 |
| `SALARIO_MAXIMO_AUXILIO_TRANSPORTE` | 2,600,000 (2 SMLV) |
| `RECARGO_DIURNO` | 25% |
| `RECARGO_NOCTURNO` | 75% |
| `DEDICCION_SEGURIDAD_SOCIAL` | 4% (health + pension) |
| `HORAS_MENSUALES` | 240 (declared but unused — hourly rate passed via `vlr_hora`) |

## Quirks

- Currency math uses `float`, not `Decimal` — potential precision issues on large scales.
- Auxilio de transporte is excluded from the deduction base (applied after health/pension).
- No tests, no linting, no formatter config exists yet.
- No `if __name__ == "__main__"` — not a standalone script.

## `guardian_agent.py` — Guardian Agent (autonomous test generation)

A self-contained script that reads `engine.py` and `casos_prueba.md`, uses LangChain + Ollama (`qwen2.5-coder:7b`) to generate Pytest tests, builds a Docker sandbox, runs the tests, and emits a verdict.

### 6-step execution flow (automatic)

| Step | Action |
|---|---|
| PASO 1 | Read `casos_prueba.md` |
| PASO 2 | Generate `tests_generados.py` via LangChain + Ollama |
| PASO 3 | Generate `Dockerfile.guardian` |
| PASO 4 | Build Docker image |
| PASO 5 | Run pytest inside container |
| PASO 6 | Save `veredicto.json` |

### Generated files (output)

| File | Content |
|---|---|
| `tests_generados.py` | Pytest tests covering TC-01 to TC-10 |
| `Dockerfile.guardian` | Docker image definition for the sandbox |
| `veredicto.json` | Auditable verdict with timestamp, model, pass/fail counts |

### Execution
```
pip install -r requirements.txt
ollama pull qwen2.5-coder:7b
python3 guardian_agent.py       # PASOS 1-6, generates all 3 output files
```

### Key details
- `guardian_agent.py` connects to Ollama **locally** (no external APIs).
- Model: `qwen2.5-coder:7b` (not llama3).
- Prompt uses neutral academic terminology to avoid security filters.
- System prompt instructs LLM to output raw Python (no markdown fences). Post-processor strips fences if present.
- `guardar_dockerfile()` tool generates `Dockerfile.guardian` automatically.
- Before building the Docker image, both `tests_generados.py` and `Dockerfile.guardian` must exist (validated).
- Container timeout is 60 s; image build timeout is 120 s.
- Verdict logic: `tests_fallidos == 0` → APROBADO, else RECHAZADO.
- `veredicto.json` format: `{timestamp, modelo_ia, tests_generados, dockerfile, tests_pasados, tests_fallidos, veredicto}`.
- Windows paths are auto-converted to Unix-style for Docker volume mounts.

## `guardian/` (legacy)

The old `guardian/` subdirectory contains the previous split implementation (`agent.py` + `sandbox.py`). The current entry point is `guardian_agent.py` at the root.
