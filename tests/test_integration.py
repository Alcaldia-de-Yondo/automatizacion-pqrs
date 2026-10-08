import pandas as pd

from pqrsd.config import Config
from pqrsd.main import OrquestadorPrincipal


def test_integration_full_flow(tmp_path):
    """Integration test: run the full pipeline with a small fabricated dataset."""
    # 1. Prepare temporary input Excel file
    input_file = tmp_path / "input.xlsx"

    # Define column names as per config
    COL_FECHA = "FECHA"
    COL_AREA_RESPONSABLE = "AREA RESPONSABLE"
    COL_SECRETARIA = "SECRETARIA"
    COL_RESUMEN_ASUNTO = "RESUMEN DE ASUNTO"
    COL_TIPO = "TIPO"
    COL_FECHA_RESPUESTA = "FECHA DE RESPUESTA"
    COL_FECHA_ENTREGA_RESPUESTA = "FECHA DE ENTREGA DE RESPUESTA"
    COL_RESPONSABLE = "RESPONSABLE"
    COL_OBSERVACION = "OBSERVACION"
    COL_ESTADO = "ESTADO"

    # Create rows as described in the plan
    data = [
        {
            COL_FECHA: "2026-01-01",
            COL_AREA_RESPONSABLE: "PLANEACION",
            COL_SECRETARIA: "OTRO",
            COL_RESUMEN_ASUNTO: "CONSULTA",
            COL_TIPO: "",
            COL_FECHA_RESPUESTA: None,
            COL_FECHA_ENTREGA_RESPUESTA: None,
            COL_RESPONSABLE: "",
            COL_OBSERVACION: "",
        },
        {
            COL_FECHA: "2026-07-01",
            COL_AREA_RESPONSABLE: "OTRO",
            COL_SECRETARIA: "PLANEACION",
            COL_RESUMEN_ASUNTO: "SOLICITUD DE INFORMACION",
            COL_TIPO: "",
            COL_FECHA_RESPUESTA: "2026-07-02",
            COL_FECHA_ENTREGA_RESPUESTA: None,
            COL_RESPONSABLE: "",
            COL_OBSERVACION: "",
        },
        {
            COL_FECHA: "2026-05-01",
            COL_AREA_RESPONSABLE: "OTRO",
            COL_SECRETARIA: "OTRO",
            COL_RESUMEN_ASUNTO: "OTRO",
            COL_TIPO: "",
            COL_FECHA_RESPUESTA: None,
            COL_FECHA_ENTREGA_RESPUESTA: None,
            COL_RESPONSABLE: "",
            COL_OBSERVACION: "",
        },
        {
            COL_FECHA: "2026-08-01",
            COL_AREA_RESPONSABLE: "SECRETARIA DE PLANEACIÓN",
            COL_SECRETARIA: "OTRO",
            COL_RESUMEN_ASUNTO: "PAGINA WEB",
            COL_TIPO: "",
            COL_FECHA_RESPUESTA: "2026-08-02",
            COL_FECHA_ENTREGA_RESPUESTA: None,
            COL_RESPONSABLE: "",
            COL_OBSERVACION: "",
        },
        {
            COL_FECHA: "2026-06-24",
            COL_AREA_RESPONSABLE: "OTRO",
            COL_SECRETARIA: "OTRO",
            COL_RESUMEN_ASUNTO: "SISBEN",
            COL_TIPO: "",
            COL_FECHA_RESPUESTA: None,
            COL_FECHA_ENTREGA_RESPUESTA: None,
            COL_RESPONSABLE: "",
            COL_OBSERVACION: "",
        },
    ]
    df_input = pd.DataFrame(data)

    # Write to Excel with header row (so loader can read column names)
    with pd.ExcelWriter(input_file, engine="openpyxl") as writer:
        df_input.to_excel(
            writer, sheet_name="PQRSD 2026", index=False
        )  # default header=True

    # 2. Create a Config instance and override necessary settings
    config = Config()
    config.USE_GOOGLE_DRIVE = False  # avoid actual Drive calls
    config.ARCHIVO_ORIGEN = input_file
    # Ensure output directory exists
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    config.ARCHIVO_SALIDA = output_dir / "output.xlsx"
    # Keep other config values as defaults (they point to a specific file, but we override ARCHIVO_ORIGEN)
    # The config also defines HOJA_SALIDA, etc.

    # 3. Instantiate orchestrator and run
    orquestador = OrquestadorPrincipal(config)
    orquestador.ejecutar()

    # 4. Verify outputs
    # Output file should exist
    assert (
        config.ARCHIVO_SALIDA.exists()
    ), f"Output file not created at {config.ARCHIVO_SALIDA}"

    # Load the output file to inspect sheets
    from openpyxl import load_workbook

    wb = load_workbook(config.ARCHIVO_SALIDA)
    sheet_names = wb.sheetnames
    wb.close()

    expected_sheets = [config.HOJA_SALIDA, "PENDIENTES", "RESUMEN2"]
    for sheet in expected_sheets:
        assert (
            sheet in sheet_names
        ), f"Expected sheet '{sheet}' not found. Sheets: {sheet_names}"

    # Read the main output sheet
    df_output = pd.read_excel(config.ARCHIVO_SALIDA, sheet_name=config.HOJA_SALIDA)
    # According to our expectation, only rows 2 and 4 (indices 1 and 3) should pass the filter.
    # Let's verify that we have exactly 2 rows.
    assert len(df_output) == 2, f"Expected 2 rows in output, got {len(df_output)}"

    # Verify that the STATE column is correctly set
    # Row corresponding to input row 2 (FECHA 2026-07-01) had FECHA DE RESPUESTA set -> CERRADO
    # Row corresponding to input row 4 (FECHA 2026-08-01) had FECHA DE RESPUESTA set -> CERRADO
    # So both should be CERRADO.
    # However, note that the state calculation uses FECHA DE RESPUESTA; if it's not null -> CERRADO.
    # Both have dates, so both CERRADO.
    assert (
        df_output[COL_ESTADO] == "CERRADO"
    ).all(), f"Expected all rows CERRADO, got {df_output[COL_ESTADO].tolist()}"

    # Verify that AREA column contains valid values (from AREAS_PERMITIDAS)
    valid_areas = set(config.AREAS_PERMITIDAS)
    output_area_col = config.COL_AREA_SALIDA
    assert set(df_output[output_area_col].dropna().unique()).issubset(
        valid_areas
    ), f"Invalid area values found: {set(df_output[output_area_col].dropna().unique()) - valid_areas}"

    # 5. Additionally, verify that the input file was not modified (should remain as is)
    assert input_file.exists()
