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
