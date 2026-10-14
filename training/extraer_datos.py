"""FASE 1: extrae los PQRSD del Excel de origen y los pre-clasifica con las
reglas actuales para generar training/datos_preliminares.csv.

El CSV resultante es un punto de partida: las etiquetas deben revisarse y
corregirse manualmente antes de entrenar (FASE 2 usa training/datos.csv).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from pqrsd.classifier import AreaClassifier
from pqrsd.config import Config
from pqrsd.loader import ExcelLoader
from pqrsd.utils import separador


def extraer() -> pd.DataFrame:
    """Extrae y pre-clasifica los resúmenes de asunto del Excel de origen."""
    config = Config()

    # 1. Leer el Excel configurado (local o Google Drive según Config).
    loader = ExcelLoader(config)
    df = loader.cargar_datos()

    # 2. Quedarse solo con la columna RESUMEN DE ASUNTO, sin vacíos.
    resumenes = df[config.COL_RESUMEN_ASUNTO].dropna().astype(str).str.strip()
    resumenes = resumenes[resumenes != ""]
    # Eliminar duplicados: mismo texto no aporta dos veces al entrenamiento.
    resumenes = resumenes.drop_duplicates()

    # 3. Pre-clasificar con las reglas actuales (etiqueta preliminar).
    df_textos = pd.DataFrame({config.COL_RESUMEN_ASUNTO: resumenes})
    clasificado = AreaClassifier(config).clasificar(df_textos)

    datos = pd.DataFrame(
        {
            "texto": clasificado[config.COL_RESUMEN_ASUNTO],
            "area": clasificado[config.COL_AREA],
        }
    )
    return datos


def main() -> None:
    separador("FASE 1: EXTRACCION DE DATOS DE ENTRENAMIENTO")
    datos = extraer()

    salida = Path(__file__).resolve().parent / "datos_preliminares.csv"
    datos.to_csv(salida, index=False, encoding="utf-8-sig")

    print(f"\nTotal de PQRSD extraidos: {len(datos)}")
    print(f"Archivo generado: {salida}")

    print("\nDistribucion por area:")
    print(datos["area"].value_counts().to_string())

    print("\nPrimeras 10 filas:")
    print(datos.head(10).to_string(index=False))

    print(
        "\nSIGUIENTE PASO: revisar y corregir las etiquetas manualmente y "
        "guardar como training/datos.csv"
    )


if __name__ == "__main__":
    main()
