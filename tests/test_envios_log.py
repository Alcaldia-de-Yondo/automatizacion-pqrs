import json
from datetime import datetime, timedelta

from pqrsd import envios_log


def test_envios_log_flujo_completo(tmp_path, monkeypatch):
    ruta = tmp_path / "logs" / "envios.json"
    monkeypatch.setattr(envios_log, "ENVIOS_LOG_PATH", ruta)

    inicial = envios_log.leer_log()

    assert inicial == {
        "ultimo_envio_periodico": None,
        "radicados_notificados": [],
        "historial_envios": [],
    }
    assert ruta.exists()
    assert envios_log.ya_se_notifico("1655") is False
    assert envios_log.dias_desde_periodico() == 1_000_000

    envios_log.registrar_envio_inmediato("1655")
    envios_log.registrar_envio_inmediato("1655")

    assert envios_log.ya_se_notifico("1655") is True
    assert envios_log.ya_se_notifico("9999") is False

    datos = envios_log.leer_log()
    datos["ultimo_envio_periodico"] = (datetime.now() - timedelta(days=3)).isoformat(
        timespec="seconds"
    )
    envios_log.guardar_log(datos)
    assert envios_log.dias_desde_periodico() == 3

    envios_log.registrar_envio_periodico()

    persistido = json.loads(ruta.read_text(encoding="utf-8"))
    assert persistido["ultimo_envio_periodico"] is not None
    assert persistido["radicados_notificados"] == ["1655"]
    assert len(persistido["historial_envios"]) == 3
    assert persistido["historial_envios"][0]["tipo"] == "inmediato"
    assert persistido["historial_envios"][-1]["tipo"] == "periodico"
