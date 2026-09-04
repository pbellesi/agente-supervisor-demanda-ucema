# Contrato del Agente: User Prompts Evaluados

El Agente Supervisor de Riesgo de Demanda interactúa mediante consignas en lenguaje natural orientadas a evaluar escenarios temporales específicos.

## 1. User Prompts Principales (Evaluación Académica)

### A. Escenario Estándar (3 días)
* **Prompt:** `"Evaluar el riesgo de demanda para los próximos 3 días."`
* **Corridas asociadas:**
  * `corrida_002` (Baseline V0.2, clasificación `NORMAL`, 7.649 tokens)
  * `corrida_006` (Baseline V0.4, clasificación `NORMAL`, 2 retries HTTP 503 recuperados, 8.069 tokens)
* **Propósito:** Evaluar el comportamiento rutinario del agente en un horizonte de planificación operativa semanal de corto plazo.

### B. Escenario Extendido y de Estrés Térmico (5 días)
* **Prompt:** `"Evaluar el riesgo de demanda para los próximos 5 días."`
* **Corrida asociada:**
  * `corrida_007` (Baseline V0.4, clasificación `OBSERVAR`, pico 5.006 MW, Tmin 1.9°C, 8.756 tokens)
* **Propósito:** Poner a prueba la capacidad de discriminación agéntica ante la incursión de una ola de frío e inercia térmica que empuja la demanda por encima de los 5.000 MW.

## 2. User Prompt de Iteración Experimental (1 día)

* **Prompt:** `"Evaluar el riesgo de demanda únicamente para el día de mañana."`
* **Corridas asociadas:**
  * `corrida_003` (Fallo de socket read timeout a los 30s)
  * `corrida_004` (Fallo HTTP 503 transitorio; consumo de 3/3 tools)
  * `corrida_005` (Fallo HTTP 503 transitorio; consumo de 3/3 tools)
* **Propósito:** Estudiar si el modelo era capaz de inducir una parada temprana autónoma ante un requerimiento mínimo de información. La evidencia demostró que el modelo prioriza la exhaustividad probatoria.
