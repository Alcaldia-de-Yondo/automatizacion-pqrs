# Cumplimiento Normativo - PQRSD

**Última verificación**: 2026-10-08
**Commit**: aaad7c0

## Estado por herramienta

| Herramienta | Estado | Comando |
|-------------|--------|---------|
| **ruff** | ✅ 0 errores | `ruff check pqrsd/ tests/` |
| **black** | ✅ 22 archivos OK | `black --check pqrsd/ tests/` |
| **isort** | ✅ 0 sin ordenar | `isort --check-only pqrsd/ tests/` |
| **mypy** | ✅ 0 errores en 17 archivos | `mypy pqrsd/` |
| **bandit** | ✅ 0 issues de seguridad | `bandit -r pqrsd/ -ll` |
| **pytest** | ✅ 27 passed | `pytest tests/` |
| **coverage** | ✅ 72.68% (>= 50%) | `pytest --cov=pqrsd` |

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
python -m ruff check pqrsd/ tests/
python -m black --check pqrsd/ tests/
python -m isort --check-only pqrsd/ tests/
python -m mypy pqrsd/
python -m bandit -r pqrsd/ -ll
python -m pytest tests/ --cov=pqrsd --cov-report=term-missing