"""FASE 3: verifica el modelo entrenado con casos nuevos.

Imprime para cada caso: texto, área predicha, confianza (0-1) y, si se
conoce, el área esperada.
"""

from __future__ import annotations

from pathlib import Path

import joblib

from pqrsd.utils import normalizar_texto, separador

MODELO_PATH = (
    Path(__file__).resolve().parent.parent / "pqrsd" / "modelo_clasificador.pkl"
)

# Casos NUEVOS (no están en training/datos.csv).
CASOS = [
    ("SOLICITUD DE NUEVA ENCUESTA SISBEN PARA CAMBIO DE PUNTAJE", "SISBEN"),
    (
        "PODA DE ARBOLES QUE ESTAN TOCANDO LAS REDES ELECTRICAS DEL BARRIO",
        "ORDENAMIENTO TERRITORIAL",
    ),
    (
        "PERMISO SINDICAL PARA ASAMBLEA GENERAL DE SINTRAEMSDES",
        "SECRETARIA DE PLANEACIÓN",
    ),
    ("ACCION DE TUTELA POR VULNERACION DEL DERECHO A LA SALUD", "ABOGADA(O)"),
    ("SOLICITUD DE CERTIFICADO DE AVALUO CATASTRAL DE MI PREDIO", "CATASTRO"),
    (
        "DENUNCIA POR PRESENCIA DE ROEDORES Y MALAS CONDICIONES DE HIGIENE",
        "GESTION DE RIESGOS",
    ),
    ("PUBLICACION DEL PROGRAMA INSTITUCIONAL EN LA EMISORA LOCAL", "COMUNICACIONES"),
    ("FORMULACION DE PROYECTO PRODUCTIVO CON REGISTRO BPIN", "BANCO DE PROYECTOS"),
    ("FALLA DEL COMPUTADOR DE LA OFICINA DE PLANEACION", "SOPORTE TIC"),
    ("SOLICITUD DE INFORMACION SOBRE UN TRAMITE GENERAL", "SECRETARIA DE PLANEACIÓN"),
]


def main() -> None:
    separador("FASE 3: VERIFICACION DEL MODELO")
    if not MODELO_PATH.exists():
        raise FileNotFoundError(
            f"No existe {MODELO_PATH}. Ejecuta primero training/entrenar.py"
        )
    modelo = joblib.load(MODELO_PATH)

    aciertos = 0
    for texto, esperada in CASOS:
        entrada = normalizar_texto(texto)
        area = modelo.predict([entrada])[0]
        confianza = float(modelo.predict_proba([entrada]).max())
        ok = "OK " if area == esperada else "XX "
        aciertos += area == esperada
        print(
            f"{ok}{area:26} conf={confianza:.2f} (esperada: {esperada:26}) {texto[:60]}"
        )
    print(f"\nAciertos: {aciertos}/{len(CASOS)}")


if __name__ == "__main__":
    main()
