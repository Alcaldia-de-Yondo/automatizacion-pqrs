import pandas as pd

from pqrsd import emails


def construir_df():
    return pd.DataFrame(
        {
            "FECHA": ["2026-10-01", "2026-10-02"],
            "TIPO": ["PQRSD", "TUTELA"],
            "RADICADO": ["100", "101"],
            "RESUMEN DE ASUNTO": ["Página web", "Predial"],
            "AREA U OFICINA ENCARGADA": ["TICS", "CATASTRO"],
            "FECHA DE RESPUESTA": [None, "2026-10-03"],
            "FECHA LÍMITE DE RESPUESTA (Jurídica)": [
                "2026-10-20",
                "2026-10-21",
            ],
        }
    )


def test_preparar_distribuir_y_resumenes():
    df = emails.preparar_datos(construir_df())

    assert emails.asignar_informe("TICS") == "Planeación"
    assert (
        emails.obtener_correo_informe("Catastro") == "catastro@yondo-antioquia.gov.co"
    )

    informes = emails.distribuir_por_area(df)
    assert set(informes) == {"Planeación", "Catastro"}
    assert [item["RADICADO"] for item in informes["Planeación"]] == ["100"]

    general = emails.generar_informe_general(df)
    assert len(general) == 2

    resumen = emails.crear_resumen_excel(df)
    assert resumen.loc[resumen["INDICADOR"] == "Abiertas", "CANTIDAD"].iloc[0] == 1

    estado_area = emails.preparar_estado_area_excel(df)
    assert set(estado_area["AREA U OFICINA ENCARGADA"]) == {
        "TICS",
        "CATASTRO",
    }


def test_contenido_y_mensaje_pqrsd_nuevo():
    registro = construir_df().iloc[0].to_dict()
    texto, html = emails._generar_contenido_pqrsd_nuevo(registro)

    assert "Se ha registrado una nueva PQRSD" in texto
    assert "RADICADO" not in html
    assert "NÚMERO DE RADICADO" in html.upper()
    assert "DÍAS RESTANTES" in html.upper()
    assert "Sebastián Fonseca Cifuentes" in html
    assert "Andrés Felipe Echavarría Ramos" in html

    mensaje = emails.crear_mensaje(
        "destinatario@example.com",
        "Asunto",
        texto,
        html,
        None,
        {},
    )
    assert mensaje["To"] == "destinatario@example.com"
    assert mensaje["Subject"] == "Asunto"
    assert mensaje.is_multipart()
