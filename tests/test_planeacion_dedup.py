"""Pruebas del filtrado de registros nuevos en Planeación (dedup por radicado)."""

from unittest.mock import MagicMock

import pandas as pd

from pqrsd.planeacion_sheets import PlaneacionSheetsAppender


def _appender():
    config = MagicMock()
    config.COL_FECHA = "FECHA"
    config.COLUMNAS_SALIDA = ["FECHA", "RADICADO"]
    return PlaneacionSheetsAppender(config)


def _df(filas):
    return pd.DataFrame(filas)


def test_incluye_radicado_nuevo_con_fecha_igual_a_la_ultima():
    app = _appender()
    df = _df([{"FECHA": "2026-01-10", "RADICADO": "R-002"}])
    ultima_fecha = pd.Timestamp("2026-01-10")
    nuevos = app._filtrar_registros_nuevos(df, ultima_fecha, {"R-001"})
    assert list(nuevos["RADICADO"]) == ["R-002"]


def test_excluye_radicado_ya_presente_aunque_la_fecha_sea_posterior():
    app = _appender()
    df = _df([{"FECHA": "2026-01-20", "RADICADO": "R-001"}])
    ultima_fecha = pd.Timestamp("2026-01-10")
    nuevos = app._filtrar_registros_nuevos(df, ultima_fecha, {"R-001"})
    assert nuevos.empty


def test_fila_sin_radicado_se_filtra_solo_por_fecha():
    app = _appender()
    df = _df(
        [
            {"FECHA": "2026-01-20", "RADICADO": None},
            {"FECHA": "2026-01-05", "RADICADO": None},
        ]
    )
    ultima_fecha = pd.Timestamp("2026-01-10")
    nuevos = app._filtrar_registros_nuevos(df, ultima_fecha, set())
    assert len(nuevos) == 1
    assert pd.Timestamp(nuevos.iloc[0]["FECHA"]) == pd.Timestamp("2026-01-20")


def test_no_duplica_radicados_repetidos_dentro_del_mismo_lote():
    app = _appender()
    df = _df(
        [
            {"FECHA": "2026-01-10", "RADICADO": "R-002"},
            {"FECHA": "2026-01-10", "RADICADO": "R-002"},
        ]
    )
    ultima_fecha = pd.Timestamp("2026-01-10")
    nuevos = app._filtrar_registros_nuevos(df, ultima_fecha, set())
    assert list(nuevos["RADICADO"]) == ["R-002"]
