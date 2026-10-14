# Training del clasificador de áreas (PQRSD)

Modelo ML (TF-IDF + Regresión Logística) entrenado con textos reales de
PQRS etiquetados manualmente. En producción funciona como clasificador
**híbrido**: el modelo decide cuando su confianza ≥ 0.7 y las reglas de
palabras clave (`pqrsd/classifier_rules.py`) actúan de fallback.

## Archivos

| Archivo | Descripción |
|---|---|
| `extraer_datos.py` | Extrae textos del Excel en Drive y los pre-clasifica con reglas |
| `datos_preliminares.csv` | Salida pre-clasificada (sin revisar) |
| `datos.csv` | **Dataset etiquetado y corregido manualmente** (usado para entrenar) |
| `datos_backup_reglas.csv` | Respaldo del dataset clasificado solo por reglas |
| `entrenar.py` | Entrena el pipeline y guarda `pqrsd/modelo_clasificador.pkl` |
| `verificar.py` | Prueba el modelo con 10 casos nuevos y muestra confianza |

## Re-entrenar

1. Editar `datos.csv` (columnas `texto`, `area`; áreas del catálogo oficial).
2. `PYTHONPATH=. python training/entrenar.py`
   - Clases con <5 ejemplos van completas a train (no se pueden estratificar).
   - Las demás: split 80/20 estratificado, `random_state=42`.
   - Imprime accuracy, classification report y matriz de confusión.
3. `PYTHONPATH=. python training/verificar.py`
4. Ejecutar `python -m pytest tests/ -q`.
5. Commit del nuevo `pqrsd/modelo_clasificador.pkl` junto al código.

## Modelo

- `TfidfVectorizer(ngram_range=(1,2), max_features=5000, lowercase=True,
  strip_accents="unicode")`
- `LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)`
- `joblib` para serializar. Está **versionado en git** (`pqrsd/modelo_clasificador.pkl`).

## Métricas de referencia (dataset corregido, 1.353 registros)

- Accuracy (test): 0.751 · weighted F1: 0.775
- SISBEN 0.93 F1 · CATASTRO 0.88 · SECRETARIA DE PLANEACIÓN 0.82
- Áreas sin ejemplos de test (SENA, SOPORTE TIC, SUPERVISION, TICS) se
  resuelven en producción por el fallback de reglas.

## Integración

- `pqrsd/classifier_model.py` — `ModelClassifier.clasificar(texto)` → `(area, confianza)`
- `pqrsd/classifier_rules.py` — `RulesClassifier.clasificar(texto)` → `area`
- `pqrsd/classifier.py` — `AreaClassifier.clasificar(df)` (API sin cambios):
  modelo si `confianza >= Config.CONFIANZA_MINIMA` (0.7), si no las reglas.
- Si `modelo_clasificador.pkl` no existe, todo cae a reglas (degradación segura).
