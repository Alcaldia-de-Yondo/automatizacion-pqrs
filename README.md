# Automatización PQRS - Planeación

Sistema para automatizar el procesamiento de archivos Excel de PQRS (Peticiones, Quejas, Reclamos y Sugerencias) para la secretaría de Planeación.

## Características

- Carga de archivos Excel desde sistema local o Google Drive
- Validación de columnas obligatorias
- Normalización de datos (fechas, texto, áreas)
- Identificación de registros relacionados con planeación
- Filtrado por fecha de corte
- Cálculo de estados (ABIERTO/CERRADO)
- Clasificación de áreas basada en palabras clave
- Cálculo de fechas límite legales
- Generación de reportes y resúmenes
- Exportación a Excel con formato profesional
- Subida opcional a Google Drive

## Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/automatizacion-pqrs.git
   cd automatizacion-pqrs
   ```

2. Crear un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno (opcional):
   ```bash
   cp .env.example .env
   # Editar .env con sus configuraciones
   ```

## Uso

```bash
python -m pqrsd.main
```

O usando el comando instalado:
```bash
automatizacion-pqrs
```

## Estructura del Proyecto

```
automatizacion-pqrs/
├── pqrsd/                 # Paquete principal
│   ├── __init__.py
│   ├── config.py          # Configuración centralizada
│   ├── drive.py           # Integración con Google Drive
│   ├── loader.py          # Carga de archivos Excel
│   ├── validator.py       # Validación de columnas
│   ├── preparer.py        # Preparación de columnas y normalización de fechas
│   ├── identifiers.py     # Identificación de registros de planeación
│   ├── filters.py         # Filtrado por fecha de corte
│   ├── states.py          # Cálculo de estados
│   ├── classifier.py      # Clasificación de áreas
│   ├── legal.py           # Cálculo de fechas límite legales
│   ├── output.py          # Preparación de salida y extracción de pendientes
│   ├── saver.py           # Guardado y formateo de Excel
│   ├── reports.py         # Generación de reportes y formato de hojas
│   ├── resumen.py         # Resumen final del proceso
│   ├── main.py            # Orquestador principal
│   └── utils.py           # Funciones auxiliares
├── tests/                 # Pruebas unitarias
├── .github/
│   └── workflows/
│       └── ci.yml         # Configuración de CI/CD
├── .pre-commit-config.yaml # Configuración de pre-commit
├── requirements.txt       # Dependencias de producción
├── requirements-dev.txt   # Dependencias de desarrollo
├── pyproject.toml         # Metadatos del proyecto
├── .gitignore             # Archivos a ignorar en Git
├── .env.example           # Ejemplo de variables de entorno
└── README.md              # Este archivo
```

## Configuración de Google Drive (Opcional)

Para usar Google Drive:

1. Obtener credenciales de servicio de Google Cloud Console
2. Compartir el archivo de Excel con la cuenta de servicio
3. Configurar en `.env`:
   ```env
   GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account-key.json
   GOOGLE_DRIVE_FOLDER_ID=ID_de_la_carpeta_de_Google_Drive
   GOOGLE_DRIVE_FILE_NAME=1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx
   USE_GOOGLE_DRIVE=True
   ```

## Pruebas

Ejecutar pruebas unitarias:
```bash
pytest
```

Con reporte de cobertura:
```bash
pytest --cov=pqrsd
```

## Formato de Código

Este proyecto utiliza:
- [Black](https://black.readthedocs.io/) para formato de código
- [isort](https://pycqa.github.io/isort/) para ordenamiento de imports
- [Flake8](https://flake8.pycqa.org/) para linting

Ejecutar formateo:
```bash
black .
isort .
```

Ejecutar linting:
```bash
flake8
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abra un issue primero para discutir qué le gustaría cambiar.

Por favor, asegúrese de actualizar las pruebas según corresponda.

## Contacto

Tu Nombre - tu.email@ejemplo.com

Enlace del Proyecto: https://github.com/tu-usuario/automatizacion-pqrs