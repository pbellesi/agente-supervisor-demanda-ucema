# Gobierno del Sistema, Permisos y Gestión de Riesgos

**Trabajo Final Individual — MBA UCEMA: Programación de y con Agentes de IA**

---

## 1. Matriz de Autonomía y Supervisión Humana (L0–L4)

| Nivel | Definición | Estado en este Sistema | Justificación Técnica |
| :---: | :--- | :---: | :--- |
| **L0** | Sin IA / Proceso manual o script rígido. | Superado | El sistema delega la investigación y el razonamiento en un LLM. |
| **L1** | IA como copiloto pasivo (el humano pide paso a paso). | Superado | El agente decide autónomamente qué herramientas consultar. |
| **L2** | **Agente Autónomo Asistido con Aprobación Humana.** | **IMPLEMENTADO (OFICIAL)** | **El agente investiga y emite dictamen estructurado; la decisión operativa queda formalmente en estado `pending` hasta firma humana.** |
| **L3** | Agente Autónomo con supervisión por excepción (actúa y avisa). | Descartado | Riesgo inaceptable en infraestructura eléctrica crítica (despacho/red). |
| **L4** | Agente totalmente autónomo sin intervención humana. | Prohibido | Violación de normativas regulatorias y de seguridad operativa de red. |

---

---

## 2. Alcance Estricto de Facultades del Agente

### Lo que el Agente SÍ puede hacer:
* Consultar autónomamente las herramientas de **solo lectura (read-only)** declaradas en su catálogo.
* Razonar iterativamente ponderando clima, desvíos y sesgos de Machine Learning.
* Emitir un dictamen técnico estructurado con recomendación operativa.

### Lo que el Agente NO puede hacer (Límites Infranqueables):
* **NO puede despachar potencia ni operar equipos de red.**
* **NO puede escribir en sistemas productivos, SCADA ni bases de datos.**
* **NO puede enviar correos electrónicos ni alertas automáticas externas.**
* **NO puede alterar estados de alarma en sistemas corporativos.**
* **NO puede publicar ni ejecutar decisiones operativas.**

El campo `humanDecision.status` en el JSON de salida permanece invariablemente en **`"pending"`** hasta que un operador humano intervenga formalmente.

---

## 3. Protocolo de Revisión y Firma Humana

* **¿Quién revisa?:** El Ingeniero de Guardia del Centro de Control de Operaciones o el Programador de la Operación de la distribuidora del AMBA.
* **¿Qué revisa?:**
  1. Coherencia del pico de demanda proyectado frente al pronóstico del Servicio Meteorológico Nacional.
  2. Justificación técnica de la clasificación (`NORMAL`, `OBSERVAR` o `ESCALAR`).
  3. Comportamiento del sesgo del modelo (si actúa como amortiguador o factor de riesgo).
* **¿Quién firma/acepta?:** El responsable de guardia firma en la bitácora operativa la aceptación o desestimación del dictamen.

---

## 4. Comportamiento ante Fallas y Contingencias Operativas

| Escenario de Falla | Comportamiento del Sistema | Acción del Operador Humano |
| :--- | :--- | :--- |
| **Tool no disponible (ej. Open-Meteo caído)** | La herramienta retorna un diccionario de error read-only; el agente evalúa con la evidencia remanente y clasifica la suficiencia de información como `PARCIAL` o `INSUFICIENTE`. | El operador recurre a la planilla manual de contingencia o al portal alternativo del SMN. |
| **LLM no disponible (error de red o API caída)** | Se agotan los reintentos transitorios (máx 1 retry); el sistema aborta limpiamente sin colgar el proceso y persiste el error detallado en `run.json`. | El operador asume el monitoreo visual tradicional en los dashboards existentes. |
| **Output inválido o schema corrupto** | El cliente REST detecta el fallo de parseo JSON (`JSONDecodeError`); no inventa datos ni fuerza una clasificación y registra `error_formato` en el output. | El dictamen se marca como no estructurado y se descarta automáticamente para uso operativo. |

---

## 5. Matriz de Modos de Falla Técnicos y Mitigaciones Implementadas

| Modo de Falla | Causa Raíz | Impacto | Mitigación Implementada | Evidencia |
| :--- | :--- | :--- | :--- | :--- |
| **Obsolescencia de Modelo** | Deprecación o bloqueo de endpoint comercial. | Imposibilidad de inferencia (`HTTP 404`). | Registro auditable del fallo; conmutación explícita y centralizada a modelo vigente (DEC-001). Cero fallback silencioso. | `corrida_001` |
| **Latencia / Jitter de Red** | Interposición de proxies corporativos con inspección TLS. | Socket Read Timeout a los 30s. | Desacople de capa de transporte; elevación de timeout a 90 segundos (DEC-003). | `corrida_003` |
| **Caída Transitoria de API** | Indisponibilidad de servidores en la nube (`HTTP 503`). | Interrupción del ciclo agéntico. | Política de 1 reintento técnico transparente tras 2s, acotado a códigos transitorios (429/5xx). | `corrida_004`, `005`, `006` |
| **Sobre-Consulta de Tools** | Inercia completista del LLM. | Consumo innecesario de tokens. | Regla de justificación previa de relevancia marginal en System Prompt V0.4 y tope técnico de 3 llamadas. | `corrida_005`, `006`, `007` |

---

## 6. Transparencia de Deuda Histórica TLS y Alcance de Auditoría

### 6.1 Tres Tiempos en la Gestión de Transporte TLS
1. **A) Entorno Histórico de Pruebas:** Durante ciertas corridas históricas (001 a 007), existió temporalmente un bypass de validación TLS en el código local de desarrollo para poder operar a través del proxy corporativo de inspección profunda de certificados (Zscaler).
2. **B) Remediación en Copia Académica:** Dicho mecanismo fue catalogado como un bloqueante de publicación y removido íntegramente al conformar la copia académica para su publicación abierta.
3. **C) Código Público Actual:** El repositorio público utiliza exclusivamente validación estándar y estricta mediante `ssl.create_default_context()` y no contiene ningún mecanismo ni parámetro para desactivar la verificación de certificados TLS.

### 6.2 Alcance del Registro "security: PASS" / "payload_sanitized: true"
El valor `"security: PASS"` o `"payload_sanitized": true` preservado en las evidencias históricas `run.json`:
* Refiere **únicamente a la sanitización técnica de los payloads salientes hacia el LLM** (confirmando la redacción de emails, rutas locales de archivos y claves API).
* **No constituye bajo ninguna circunstancia una certificación integral de ciberseguridad**, infraestructura ni perímetro del entorno en el que se originaron las llamadas.
