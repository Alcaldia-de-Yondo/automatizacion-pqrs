# Cumplimiento Normativo - PQRSD

**Última verificación**: 14 de octubre de 2026
**Commit**: cambios sin commitear (clasificador híbrido ML + reglas)

## Estado por herramienta

| Herramienta | Estado | Comando |
|-------------|--------|---------|
| **ruff** | ✅ 0 errores | `ruff check pqrsd/ tests/ training/` |
| **black** | ✅ 36 archivos OK | `black --check pqrsd/ tests/ training/` |
| **isort** | ✅ 0 sin ordenar | `isort --check-only pqrsd/ tests/ training/` |
| **mypy** | ✅ 0 errores en 23 archivos | `mypy pqrsd/` |
| **bandit** | ✅ 0 issues de seguridad | `bandit -r pqrsd/ -ll` |
| **pip-audit** | ✅ 0 vulnerabilidades conocidas | `pip-audit` |
| **pytest** | ✅ 58 passed | `pytest tests/` |
| **coverage** | ✅ 59.03% (>= 50%) | `pytest --cov=pqrsd` |

## Normas cumplidas

- **PEP 8**: ruff (pycodestyle) — 0 errores
- **PEP 257**: docstrings en módulos públicos
- **PEP 484**: type hints en todo el código (mypy 0 errores)
- **Conventional Commits**: usado en el historial
- **SemVer**: versión 1.0.0 en pyproject.toml
- **OWASP**: bandit sin issues
- **DRY/KISS/SOLID**: estructura modular aplicada

## Cómo verificar

```bash
# Instalar entorno de desarrollo
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

# Correr todas las verificaciones
python -m ruff check pqrsd/ tests/ training/
python -m black --check pqrsd/ tests/ training/
python -m isort --check-only pqrsd/ tests/ training/
python -m mypy pqrsd/
python -m bandit -r pqrsd/ -ll
python -m pip-audit
python -m pytest tests/ --cov=pqrsd --cov-report=term-missing