"""Registro persistente de correos e informes PQRSD enviados."""

import json
import logging
from datetime import datetime
from typing import Any

from .config import Config

logger = logging.getLogger(__name__)

ENVIOS_LOG_PATH = Config.ENVIOS_LOG_PATH

ESTRUCTURA_INICIAL: dict[str, Any] = {
    "ultimo_envio_periodico": None,
    "radicados_notificados": [],
    "historial_envios": [],
}


def _estructura_inicial() -> dict[str, Any]:
    """Devuelve una copia limpia de la estructura inicial del registro."""
    return json.loads(json.dumps(ESTRUCTURA_INICIAL))


def _crear_directorio() -> None:
    """Crea el directorio del archivo de registro si no existe."""
    ENVIOS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _normalizar_log(datos: dict) -> dict[str, Any]:
    """Garantiza que el archivo tenga las claves y tipos esperados."""
    datos_normalizados = _estructura_inicial()
    datos_normalizados.update(datos)

    radicados = datos_normalizados.get("radicados_notificados")
    if not isinstance(radicados, list):
        datos_normalizados["radicados_notificados"] = []
    else:
        datos_normalizados["radicados_notificados"] = [
            str(radicado) for radicado in radicados
        ]

    historial = datos_normalizados.get("historial_envios")
    if not isinstance(historial, list):
        datos_normalizados["historial_envios"] = []

    return datos_normalizados


def leer_log() -> dict[str, Any]:
    """Lee el registro de envíos, creándolo con valores iniciales si no existe."""
    _crear_directorio()

    if not ENVIOS_LOG_PATH.exists():
        datos = _estructura_inicial()
        guardar_log(datos)
        logger.info("Registro de envíos creado: %s", ENVIOS_LOG_PATH)
        return datos

    try:
        datos = json.loads(ENVIOS_LOG_PATH.read_text(encoding="utf-8"))
        if not isinstance(datos, dict):
            raise ValueError("La raíz de envios.json debe ser un objeto JSON")
    except (OSError, json.JSONDecodeError, ValueError):
        logger.exception("No se pudo leer el registro de envíos; se reiniciará")
        datos = _estructura_inicial()

    datos = _normalizar_log(datos)
    guardar_log(datos)
    return datos


def guardar_log(datos: dict) -> None:
    """Guarda el registro de envíos de forma atómica con codificación UTF-8."""
    datos = _normalizar_log(datos)
    _crear_directorio()
    ruta_temporal = ENVIOS_LOG_PATH.with_name(ENVIOS_LOG_PATH.name + ".tmp")
    ruta_temporal.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    ruta_temporal.replace(ENVIOS_LOG_PATH)


def registrar_envio_periodico() -> None:
    """Registra la fecha actual como último envío periódico realizado."""
    datos = leer_log()
    fecha = datetime.now().isoformat(timespec="seconds")
    datos["ultimo_envio_periodico"] = fecha
    datos["historial_envios"].append(
        {
            "fecha": fecha,
            "tipo": "periodico",
            "destinatarios": [Config.CORREO_GENERAL],
        }
    )
    guardar_log(datos)
    logger.info("Envío periódico registrado: %s", fecha)


def registrar_envio_inmediato(radicado: str) -> None:
    """Registra una notificación inmediata para un radicado."""
    radicado = str(radicado).strip()
    if not radicado:
        raise ValueError("El radicado no puede estar vacío")

    datos = leer_log()
    fecha = datetime.now().isoformat(timespec="seconds")

    if radicado not in datos["radicados_notificados"]:
        datos["radicados_notificados"].append(radicado)

    datos["historial_envios"].append(
        {
            "fecha": fecha,
            "tipo": "inmediato",
            "radicados": [radicado],
        }
    )
    guardar_log(datos)
    logger.info("Envío inmediato registrado para radicado %s", radicado)


def ya_se_notifico(radicado: str) -> bool:
    """Indica si el radicado ya tiene una notificación inmediata registrada."""
    radicado = str(radicado).strip()
    datos = leer_log()
    return radicado in datos["radicados_notificados"]


def dias_desde_periodico() -> int:
    """Devuelve los días desde el último envío periódico.

    Si no existe un envío anterior o tiene formato inválido, devuelve un
    número muy grande para que el proceso periódico pueda ejecutarse.
    """
    datos = leer_log()
    ultimo_envio = datos.get("ultimo_envio_periodico")

    if not ultimo_envio:
        return 1_000_000

    try:
        ultima_fecha = datetime.fromisoformat(str(ultimo_envio))
    except ValueError:
        logger.warning("Fecha de último envío periódico inválida: %s", ultimo_envio)
        return 1_000_000

    return (datetime.now() - ultima_fecha).days
