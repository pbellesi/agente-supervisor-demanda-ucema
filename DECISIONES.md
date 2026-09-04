# Registro de Decisiones de Arquitectura y Evolución Agéntica (MBA UCEMA)

## DEC-001: Cambio de Gemini 2.5 Flash a Gemini 3.1 Flash-Lite (Versión Agéntica V0.2)
* **Fecha:** 2026-09-03
* **Contexto:** En la Corrida 001 académica real ejecutada con el baseline inicial `gemini-2.5-flash`, el endpoint de Google AI Studio (`generativelanguage.googleapis.com/v1beta`) retornó `HTTPError 404: Not Found`. El diagnóstico externo verificó que Google está limitando actualmente el acceso a modelos Gemini 2.5 para proyectos nuevos y recomienda modelos vigentes.
* **Preservación de Evidencia:** Se preservó de forma intacta e inmutable la traza histórica de la Corrida 001 en `corridas/corrida_001/run.json` y `agente/audit_log.jsonl` (reflejando `iteraciones: 0`, `tool_calls: []`, `tokens: NO_DISPONIBLE`, `costo incremental: USD 0`, error HTTP 404 y verificación de sanitización exitosa), sin inventar tokens ni falsear el resultado.
* **Decisión:** Actualizar el punto único de configuración a `CONFIGURED_GEMINI_MODEL = "gemini-3.1-flash-lite"`.
* **Motivo Académico:** Evaluar el modelo vigente más pequeño, veloz y costo-eficiente para tareas agénticas de supervisión técnica de demanda bajo Free Tier (USD 0 incremental). Se mantiene estricta la política de **cero fallback automático**, registrando fielmente los resultados reales de cada corrida.

## DEC-002: Convalidación de Gemini 3.1 Flash-Lite y hallazgo de sobre-consulta
* **Fecha:** 2026-09-03
* **Contexto:** La Corrida 002 real se ejecutó con éxito utilizando `gemini-3.1-flash-lite` bajo Free Tier verificado, completando 3 tool calls dinámicas, 7.649 tokens reales, ~8.66 s de latencia, dictamen estructurado válido y verificación de seguridad PASS (`corridas/corrida_002/run.json`).
* **Decisión:** Ratificar `gemini-3.1-flash-lite` como baseline oficial del agente supervisor.
* **Hallazgo / Aprendizaje:** La auditoría académica de la corrida identificó una tendencia a consultar evidencia marginal (agotando el máximo de 3 herramientas en un escenario operativo normal y no crítico) inducida por heurísticas prescriptivas en el System Prompt. Para la versión V0.3 se decide sustituir las reglas imperativas por principios de investigación y parada temprana fundamentada.

## DEC-003: Robustez de Transporte HTTP (Timeout Extendido y Retry Transitorio)
* **Fecha:** 2026-09-03
* **Contexto:** En la Corrida 003 real ejecutada con el System Prompt V0.3, el request HTTP hacia Gemini API experimentó un socket read timeout a los 30.06 segundos (`The read operation timed out`) producto de la latencia y filtros de la red corporativa. La corrida concluyó sin inferencia ni dictamen, preservando intacta la evidencia en `corridas/corrida_003/run.json` con seguridad PASS y costo incremental USD 0.
* **Decisión:** 
  1. Aumentar el timeout por petición HTTP de 30 a 90 segundos (`timeout_seconds = 90`).
  2. Incorporar una política de transporte con un único reintento técnico (máx 1 retry) confinado estrictamente a fallos transitorios de red (`READ_TIMEOUT`, HTTP 429, HTTP 5xx).
  3. No reintentar bajo ninguna circunstancia errores semánticos, de esquema, tool calling inválido o errores 4xx no transitorios.
  4. Registrar con total transparencia en `run.json` cada intento fallido y reintento (`request_attempt`, `retry_reason`, `retry_count`, `timeout_seconds`).
* **Motivo Académico:** Garantizar robustez operativa frente a la variabilidad de la red sin alterar en modo alguno la lógica agéntica, los prompts, las herramientas, los criterios de riesgo ni las decisiones del modelo. La Corrida 003 queda registrada como evidencia histórica de contingencia de transporte, programándose la siguiente ejecución en `corridas/corrida_004/run.json`.

## DEC-004: Evaluación de Corrida 004 y refuerzo de criterio para herramientas secundarias (V0.4)
* **Fecha:** 2026-09-03
* **Contexto:** La Corrida 004 real (`corridas/corrida_004/run.json`) demostró dos hechos fundamentales:
  1. La política de transporte y reintentos (DEC-003) operó correctamente: detectó un fallo transitorio `HTTPError 503: Service Unavailable`, ejecutó exactamente un reintento técnico transparente a los 2 segundos, y registró la trazabilidad completa (`retry_count: 1`, `retry_reason: HTTP_503_TRANSIENT`).
  2. A nivel agéntico, el System Prompt V0.3 no logró mitigar la sobre-consulta: aun ante una solicitud acotada a un solo día con demanda moderada (3.656 MW, 12.6°C), el modelo volvió a consumir el 100% de las herramientas (3 de 3), consultando la consistencia histórica de 600 días sin una hipótesis de impacto operativo.
* **Decisión:** 
  1. Mantener intacta la infraestructura, el modelo (`gemini-3.1-flash-lite`), el timeout (90 s), la política de transporte y las herramientas.
  2. Actualizar el prompt a la versión V0.4 (`sacme-supervisor-v0.4`) incorporando una **regla de justificación previa de relevancia marginal**: antes de invocar cualquier herramienta secundaria, el agente debe identificar qué incertidumbre intenta resolver y constatar si el resultado podría modificar materialmente:
     a) la clasificación de riesgo,
     b) la suficiencia de evidencia, o
     c) la recomendación operativa.
     Si el agente no puede identificar cómo el resultado cambiaría alguno de esos 3 elementos, debe detener la investigación y emitir el dictamen.
* **Motivo Académico:** Inducir selectividad genuina y parsimonia epistémica mediante razonamiento de valor marginal de la información, sin imponer reglas determinísticas por temperatura ni restringir artificialmente el presupuesto de 3 herramientas.

## DEC-005: Cierre de optimización de parada temprana y congelamiento de V0.4
* **Fecha:** 2026-09-03
* **Contexto:** La Corrida 005 real (`corridas/corrida_005/run.json`), ejecutada con el System Prompt V0.4 ante la consulta acotada a un solo día ("día de mañana"), repitió el comportamiento de invocar 3 de 3 herramientas disponibles, registrando 4.976 tokens y un reintento por fallo transitorio HTTP 503 de la API.
* **Hallazgo / Aprendizaje:** Las iteraciones V0.3 y V0.4 evidenciaron empíricamente que `gemini-3.1-flash-lite` mantiene una estrategia de investigación conservadora y sobre-exhaustiva, orientada a maximizar la completitud de la evidencia antes de dictaminar, con independencia de las reglas de relevancia marginal.
* **Decisión:**
  1. No continuar endureciendo el System Prompt con heurísticas prescriptivas que degraden la autonomía agéntica genuina convirtiéndola en un árbol determinístico.
  2. Congelar formalmente la versión **V0.4 (`sacme-supervisor-v0.4`)** como baseline oficial y definitivo del sistema.
  3. Mantener intactos el modelo (`gemini-3.1-flash-lite`), las 3 herramientas read-only, el límite técnico de 3 llamadas, el timeout de 90 s, el reintento técnico único y la infraestructura de sanitización y seguridad.
* **Enfoque Académico para Próximas Corridas:** Las siguientes corridas evaluarán la consistencia analítica, solidez técnica y adaptabilidad del agente ante escenarios variados de demanda, desistiendo de intervenir artificialmente sobre la cantidad de tool calls.

## DEC-006: Validación final del baseline V0.4 mediante corridas exitosas
* **Fecha:** 2026-09-03
* **Contexto:** Se ejecutaron dos corridas reales adicionales con el baseline congelado V0.4 (`gemini-3.1-flash-lite`, timeout 90 s, máx 1 retry técnico, prompt V0.4):
  * **Corrida 006 (`corridas/corrida_006/run.json`):**
    * Modo: Real (`gemini-3.1-flash-lite`, Prompt V0.4).
    * Objetivo / Horizonte: 3 días.
    * Herramientas: 3 tool calls dinámicas completadas.
    * Clasificación: `NORMAL` (Pico 4.508 MW).
    * Suficiencia: `COMPLETA`.
    * Tokens: 8.069 tokens reportados por API.
    * Resiliencia: 2 reintentos técnicos recuperados exitosamente ante fallos transitorios `HTTP 503: Service Unavailable`.
    * Dictamen: Estructurado, fundado y válido.
    * Seguridad: PASS (sin filtraciones corporativas ni de red).
    * Costo incremental: USD 0 (Free Tier verificado).
  * **Corrida 007 (`corridas/corrida_007/run.json`):**
    * Modo: Real (`gemini-3.1-flash-lite`, Prompt V0.4).
    * Objetivo / Horizonte: 5 días (escenario extendido de mayor exigencia térmica).
    * Herramientas: 3 tool calls dinámicas completadas.
    * Clasificación: `OBSERVAR` (Pico 5.006 MW, Tmin 1.9°C).
    * Suficiencia: `COMPLETA`.
    * Tokens: 8.756 tokens reportados por API.
    * Resiliencia: 0 reintentos (ejecución HTTP limpia en 33.9 s).
    * Dictamen: Estructurado, fundado y válido.
    * Seguridad: PASS (sin filtraciones corporativas ni de red).
    * Costo incremental: USD 0 (Free Tier verificado).
* **Hallazgo Clave:** 
  Con el baseline congelado V0.4 se obtuvieron dos corridas completas, robustas y consistentes.
  La Corrida 007 demostró **sensibilidad y discriminación técnica genuina de clasificación**: el agente no repite automáticamente `NORMAL`, sino que ante una proyección de demanda superior a 5.000 MW y un gradiente térmico severo (mínima de 1.9°C con inercia térmica), conmuta de forma justificada su clasificación a `OBSERVAR`, articulando el impacto del frío y el factor amortiguador del sesgo histórico del modelo.
* **Decisión de Cierre Experimental:** 
  Se declaran como la terna de **Corridas Principales Exitosas** para el Trabajo Final:
  1. **Corrida 002:** Evaluación estándar a 3 días (Baseline V0.2, clasificación `NORMAL`, 7.649 tokens).
  2. **Corrida 006:** Evaluación a 3 días con resiliencia de transporte demostrada (Baseline V0.4, clasificación `NORMAL`, 2 retries HTTP 503 recuperados, 8.069 tokens).
  3. **Corrida 007:** Evaluación extendida a 5 días con sensibilidad operativa (Baseline V0.4, clasificación `OBSERVAR`, pico 5.006 MW, Tmin 1.9°C, 8.756 tokens).
  Las Corridas 001, 003, 004 y 005 se conservan selladas como evidencia histórica obligatoria de iteración, contingencias de API (HTTP 404, Read Timeout, HTTP 503) y gobierno del sistema agéntico.



