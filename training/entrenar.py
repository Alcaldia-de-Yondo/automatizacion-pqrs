"""FASE 2: entrena el clasificador ML (TF-IDF + Regresión Logística) con
training/datos.csv y guarda pqrsd/modelo_clasificador.pkl.

Decisiones documentadas:
- Las clases con <MIN_EJEMPLOS_SPLIT ejemplos van completas a entrenamiento:
  el split estratificado es imposible/irrelevante para ellas y en producción
  ese tipo de área (SENA, SOPORTE TIC, SUPERVISION) lo cubre bien el fallback
  por reglas. Las métricas de test solo miden las clases con datos suficientes.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from pqrsd.config import Config
from pqrsd.utils import normalizar_texto, separador

RANDOM_STATE = 42
MIN_EJEMPLOS_SPLIT = 5
MODELO_PATH = (
    Path(__file__).resolve().parent.parent / "pqrsd" / "modelo_clasificador.pkl"
)
DATOS_PATH = Path(__file__).resolve().parent / "datos.csv"


def cargar_datos(path: Path = DATOS_PATH) -> pd.DataFrame:
    """Carga el dataset etiquetado: quita vacíos y normaliza el texto."""
    df = pd.read_csv(path)
    df = df.dropna(subset=["texto", "area"])
    df["texto"] = df["texto"].astype(str).map(normalizar_texto)
    df = df[df["texto"] != ""]
    areas_validas = set(Config.AREAS_PERMITIDAS)
    invalidas = set(df["area"]) - areas_validas
    if invalidas:
        raise ValueError(f"Áreas no válidas en el dataset: {invalidas}")
    return df


def crear_pipeline() -> Pipeline:
    """Pipeline TF-IDF (unigramas+bigramas) + Regresión Logística balanceada."""
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_features=5000,
                    lowercase=True,
                    strip_accents="unicode",
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def split_estratificado(df: pd.DataFrame):
    """80/20 estratificado; clases con <MIN_EJEMPLOS_SPLIT van completas a train."""
    conteos = df["area"].value_counts()
    pequenas = conteos[conteos < MIN_EJEMPLOS_SPLIT].index
    df_peq = df[df["area"].isin(pequenas)]
    df_split = df[~df["area"].isin(pequenas)]

    if len(pequenas):
        print(
            f"Clases con <{MIN_EJEMPLOS_SPLIT} ejemplos (van completas a train): "
            f"{sorted(pequenas)}"
        )

    train, test = train_test_split(
        df_split,
        test_size=0.2,
        stratify=df_split["area"],
        random_state=RANDOM_STATE,
    )
    train = pd.concat([train, df_peq])
    return train, test


def main() -> None:
    separador("FASE 2: ENTRENAMIENTO DEL MODELO")
    df = cargar_datos()
    print(f"Ejemplos cargados: {len(df)}")
    print("\nDistribución por área:")
    print(df["area"].value_counts().to_string())

    train, test = split_estratificado(df)
    print(f"\nTrain: {len(train)}  |  Test: {len(test)}")

    pipeline = crear_pipeline()
    pipeline.fit(train["texto"], train["area"])

    predicciones = pipeline.predict(test["texto"])
    accuracy = accuracy_score(test["area"], predicciones)
    print(f"\nAccuracy (test): {accuracy:.3f}")
    print("\nClassification report:")
    print(classification_report(test["area"], predicciones, zero_division=0))
    print("Matriz de confusión:")
    labels = sorted(set(test["area"]))
    print(
        pd.DataFrame(
            confusion_matrix(test["area"], predicciones, labels=labels),
            index=labels,
            columns=labels,
        ).to_string()
    )

    MODELO_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODELO_PATH)
    tamano_mb = MODELO_PATH.stat().st_size / 1e6
    print(f"\nModelo guardado en: {MODELO_PATH} ({tamano_mb:.1f} MB)")


if __name__ == "__main__":
    main()
