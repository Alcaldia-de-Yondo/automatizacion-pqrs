import datetime
from functools import lru_cache
from typing import Any

import pandas as pd

from .config import Config
from .utils import normalizar_texto


def _convertir_fecha_scalar(valor, fmt) -> pd.Timestamp | None:
    """Convierte un valor a Timestamp usando el formato dado, o None si falla."""
    try:
        return pd.Timestamp(datetime.datetime.strptime(str(valor).strip(), fmt))
    except (ValueError, TypeError):
        return None


def _parse_fecha_string(valor: str) -> Any:
    """Parse a date string using known formats, returning NaT if parsing fails."""
    if not isinstance(valor, str):
        return pd.NaT

    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
        fecha = _convertir_fecha_scalar(valor, fmt)
        if fecha is not None:
            return fecha

    return pd.NaT


@lru_cache(maxsize=4)
def _cargar_dias_feriados_cached(ruta_archivo: str, hoja: str) -> frozenset:
    """Carga los días feriados, cacheado por ruta+hoja."""
    try:
        df_feriados = pd.read_excel(
            ruta_archivo,
            sheet_name=hoja,
            header=None,
        )
    except ValueError:
        print(
            f"Advertencia: no se encontró la hoja '{hoja}'. "
            "Se excluirán únicamente sábados y domingos."
        )
        return frozenset()

    fechas = []

    for valor in df_feriados.to_numpy().ravel():
        fecha: Any = None
        if isinstance(valor, (int, float)) and not pd.isna(valor):
            # Excel almacena fechas como números seriales.
            if 40000 <= float(valor) <= 60000:
                fecha = pd.Timestamp("1899-12-30") + pd.to_timedelta(
                    float(valor),
                    unit="D",
                )
            else:
                fecha = pd.NaT
        else:
            # Intentar formatos explícitos primero
            fecha = pd.NaT
            if isinstance(valor, str):
                for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
                    try:
                        fecha = pd.Timestamp(
                            datetime.datetime.strptime(valor.strip(), fmt),
                        )
                        break
                    except (ValueError, TypeError):
                        continue
            # Fallback: dejar que pandas intente
            if pd.isna(fecha):
                fecha = pd.to_datetime(valor, errors="coerce", dayfirst=True)

        if pd.notna(fecha):
            fecha = pd.Timestamp(fecha).normalize()

            if 2020 <= fecha.year <= 2035:
                fechas.append(fecha)

    feriados = frozenset(fechas)

    print(f"Días feriados cargados: {len(feriados):,}")
    return feriados


class LegalDateCalculator:
    """Responsable de calcular la fecha límite legal para cada PQRSD."""

    def __init__(self, config: Config):
        self.config = config

    def calcular_fecha_limite(self, df):
        """Calcula la fecha límite legal para cada PQRSD."""
        # Determine effective origin
        archivo_origen = getattr(self.config, "EFFECTIVE_ARCHIVO_ORIGEN", None)
        if archivo_origen is None:
            archivo_origen = self.config.ARCHIVO_ORIGEN
        feriados = _cargar_dias_feriados_cached(
            str(archivo_origen), self.config.HOJA_FERIADOS
        )

        df = df.copy()
        df[self.config.COL_FECHA_LIMITE] = [
            self._sumar_dias_habiles(
                fecha,
                self._obtener_dias_termino(fila),
                feriados,
            )
            for fecha, (_, fila) in zip(
                df[self.config.COL_FECHA],
                df.iterrows(),
            )
        ]

        return df

    def _es_dia_habil(self, fecha, feriados):
        """Determina si una fecha es hábil según calendario colombiano."""
        fecha = pd.Timestamp(fecha).normalize()
        return fecha.weekday() < 5 and fecha not in feriados

    def _sumar_dias_habiles(self, fecha_inicio, dias, feriados):
        """Suma días hábiles contando desde el día siguiente a la recepción."""
        if pd.isna(fecha_inicio):
            return pd.NaT

        fecha = pd.Timestamp(fecha_inicio).normalize()
        dias_contados = 0

        while dias_contados < dias:
            fecha += pd.Timedelta(days=1)

            if self._es_dia_habil(fecha, feriados):
                dias_contados += 1

        return fecha

    def _obtener_dias_termino(self, fila):
        """Determina el término legal según el contenido de TIPO y ASUNTO."""
        tipo = normalizar_texto(fila.get("TIPO", ""))
        asunto = normalizar_texto(fila.get(self.config.COL_RESUMEN_ASUNTO, ""))
        texto = f"{tipo} {asunto}"

        if any(
            termino in texto
            for termino in (
                "CONSULTA",
                "CONSULTAS",
            )
        ):
            return self.config.DIAS_TERMINO_CONSULTA

        if any(
            termino in texto
            for termino in (
                "SOLICITUD DE INFORMACION",
                "SOLICITUD DE INFORMACIÓN",
                "INFORMACION",
                "INFORMACIÓN",
                "DOCUMENTO",
                "DOCUMENTOS",
                "COPIA",
                "COPIAS",
            )
        ):
            return self.config.DIAS_TERMINO_INFORMACION

        return self.config.DIAS_TERMINO_GENERAL
