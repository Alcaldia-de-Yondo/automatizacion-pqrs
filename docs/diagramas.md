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
    E --> F["Clasificar area responsable<br/>por palabras clave"]
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
    A["Leer RESUMEN DE ASUNTO"] --> B["Normalizar texto<br/>(mayúsculas, sin caracteres<br/>especiales)"]
    B --> C["Contar palabras clave<br/>por cada área"]
    C --> D{"Hay areas con coincidencias?"}
    D -- Sí --> E["Area con mas coincidencias"]
    D -- No --> K["Area por defecto: SECRETARIA DE PLANEACIÓN"]
    E --> H{"Esta en el catalogo de 11 areas?"}
    H -- Sí --> I["Area asignada"]
    H -- No --> J["ERROR: valor no autorizado"]
    K --> I
    E --> L["En caso de empate: gana el área definida primero"]
    L --> H
```

**Reglas de negocio:**
- Gana el área con más palabras clave coincidentes; en empate prevalece el
  orden del catálogo; sin coincidencia → SECRETARIA DE PLANEACIÓN.

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

