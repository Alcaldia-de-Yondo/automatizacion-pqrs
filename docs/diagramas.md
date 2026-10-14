# Diagramas de Flujo — Sistema de Automatización PQRSD

**Entidad:** Alcaldía de Yondó, Antioquia
**Formato:** [Mermaid](https://mermaid.js.org/) — visible en GitHub, GitLab, VS Code (con extensión) y Typora.

---

## 1. Diagrama general del flujo

```mermaid
flowchart TD
    A["Descargar archivo de recepción<br/>(Google Drive / Excel local)"] --> B["Cargar y validar registros"]
    B --> C["Preparar y normalizar datos"]
    C --> D["Identificar competencia de Planeación<br/>y filtrar por fecha de corte"]
    D --> E["Calcular estado<br/>(ABIERTO / CERRADO)"]
    E --> F["Clasificar área responsable<br/>(modelo ML con fallback<br/>por palabras clave)"]
    F --> G["Calcular fecha límite legal<br/>(10 / 15 / 30 días hábiles)"]
    G --> H["Preparar salida y detectar<br/>pendientes"]
    H --> I["Agregar al Sheets de Planeación"]
    I --> J["Notificar correo inmediato al área<br/>+ informes periódicos"]
    J --> K["Guardar Excel de salida<br/>y resumen final"]
```

---

## 2. Diagrama del algoritmo de clasificación

Cómo se decide el área de una PQRSD a partir del *RESUMEN DE ASUNTO*:

```mermaid
flowchart TD
    A["Leer RESUMEN DE ASUNTO"] --> B["Normalizar texto<br/>(mayúsculas, sin tildes)"]
    B --> C{"Modelo ML disponible?"}
    C -- No --> G["Clasificar por palabras clave"]
    C -- Sí --> D["Predicción del modelo<br/>+ confianza 0-1"]
    D --> E{"Confianza >=<br/>umbral 0.7?"}
    E -- Sí --> I["Área asignada por el modelo"]
    E -- No --> G
    G --> H{"Hay áreas con<br/>coincidencias?"}
    H -- Sí --> J["Área con más coincidencias<br/>(en empate, la primera del orden)"]
    H -- No --> K["Área por defecto: SECRETARIA DE PLANEACIÓN"]
    J --> L{"Está en el catálogo de 12 áreas?"}
    I --> L
    K --> L
    L -- Sí --> M["Área asignada"]
    L -- No --> N["ERROR: valor no autorizado"]
```

**Reglas de negocio:**
- El modelo ML (TF-IDF + Regresión Logística, entrenado con PQRS reales)
  decide cuando su confianza es ≥ 0.7; si no, gobierna el clasificador por
  palabras clave: gana el área con más coincidencias, en empate prevalece
  el orden del catálogo, y sin coincidencia → SECRETARIA DE PLANEACIÓN.

---

## 3. Diagrama del cálculo de fecha límite

```mermaid
flowchart TD
    A["Fecha de recepción"] --> B["Determinar término: consulta 30 / informacion 10 / general 15"]
    B --> C["Cargar dias feriados de hoja DÍAS FERIADOS"]
    C --> D["Desde el día siguiente, avanzar día a día"]
    D --> E{"¿Es hábil?"}
    E -- No --> D
    E -- Sí --> F["Contar 1 día hábil"]
    F --> G{"¿Ya conté N dias?"}
    G -- No --> D
    G -- Sí --> H["Fecha límite = ese día hábil<br/>se escribe en FECHA LÍMITE"]
```

---

## 4. Diagrama del flujo de correos

Notificación inmediata vs. informe periódico:

```mermaid
flowchart TD
    A["PQRSD nuevos detectados"] --> B{"para cada PQRSD nuevo"}
    B --> C{"¿Tiene radicado?"}
    C -- No --> D["Omitir y registrar advertencia"]
    C -- Sí --> E{"¿Ya fue notificado?"}
    E -- Sí --> F["Saltar: no duplicar"]
    E -- No --> G["Identificar correo del area seguro tabla interna de rutas"]
    G --> H["Enviar al area con copia al correo general"]
    H --> I{"¿Exito?"}
    I -- No --> E2["Registrar error y reintentar en la siguiente ejecución"]
    I -- Sí --> K2["Registrar envio inmediato en bitacora"]
    A --> L{"¿Han pasado N dias desde el último informe?"}
    L -- No --> M["No enviar informe"]
    L -- Sí --> N["Generar informes por area y general"]
    N --> O["Enviar informes periódicos"]
    O --> P["Registrar envío periódico en bitacora"]
```

---

## 5. Diagrama de estados de una PQRSD

```mermaid
stateDiagram-v2
    [*] --> ABIERTO : PQRSD registrada sin fecha de respuesta
    ABIERTO --> ABIERTO : Informe periódico
    ABIERTO --> CERRADO : Área registra fecha de respuesta
    CERRADO --> [*]
```

