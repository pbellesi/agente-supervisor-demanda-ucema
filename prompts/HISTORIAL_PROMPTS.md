# Historial y Evolución de Prompts (MBA UCEMA)

El diseño del contrato de instrucciones del Agente Supervisor evolucionó desde el prototipo inicial (`Pre-V0.3`) a través de las versiones formales V0.2, V0.3 y V0.4, reflejando el proceso de iteración, auditoría y aprendizaje empírico.

---

## 1. Tabla de Evolución de Versiones

| Versión | Denominación en Código | Motivación de Diseño | Decisión que la Origina | Corridas Asociadas | Estado |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **Pre-V0.3** | *Pre-V0.3* (Prototipo Inicial) | Prototipo inicial con heurísticas prescriptivas rígidas por temperatura. | Baseline inicial | **Corrida 001** | Obsoleta (Fallo HTTP 404 en Gemini 2.5) |
| **V0.2** | `sacme-supervisor-v0.2` | Adaptación de function calling nativo para Gemini 3.1 Flash-Lite. | **DEC-001** | **Corrida 002** | Sustituida (Inducía sobre-consulta de tools) |
| **V0.3** | `sacme-supervisor-v0.3` | Reemplazo de heurísticas por principios generales de parada temprana. | **DEC-002** | **Corrida 003**, **Corrida 004** | Sustituida (No resolvió sobre-consulta ante 1d) |
| **V0.4** | `sacme-supervisor-v0.4` | Regla de Justificación Previa de Relevancia Marginal para herramientas secundarias. | **DEC-004** / **DEC-005** | **Corrida 005**, **Corrida 006**, **Corrida 007** | **Congelada (Baseline Oficial Definitivo)** |

---

## 2. Detalle Histórico de Iteraciones

### Prototipo Inicial (Pre-V0.3) — Heurísticas Prescriptivas
* **Modelo:** `gemini-1.5-flash` / `gemini-2.5-flash`
* **Características:**
  * Heurísticas rígidas que inducían la consulta de herramientas en función de rangos de temperatura fijados de antemano.
  * Presupuesto de 3 herramientas no acotado por principios de parsimonia.
* **Resultado / Aprendizaje:** La Corrida 001 real falló por indisponibilidad de endpoint (`HTTPError 404: Not Found` en Gemini 2.5 Flash), forzando el cambio a un modelo vigente (DEC-001).

---

## Versión V0.2 — Convalidación de Gemini 3.1 Flash-Lite
* **Modelo:** `gemini-3.1-flash-lite`
* **Prompt Version:** `sacme-supervisor-v0.2`
* **Características:**
  * Adaptación al esquema de function calling directo de Gemini v1beta.
  * Mantenimiento de las heurísticas iniciales.
* **Resultado / Aprendizaje:** La Corrida 002 fue 100% exitosa (7.649 tokens, dictamen NORMAL). Sin embargo, la auditoría académica detectó que el agente consultó las 3 herramientas aún cuando la demanda era baja y el riesgo nulo. Se diagnosticó que las heurísticas del prompt sobre-inducían el uso de herramientas marginales (DEC-002).

---

## Versión V0.3 — Principios de Investigación y Parada Temprana
* **Modelo:** `gemini-3.1-flash-lite`
* **Prompt Version:** `sacme-supervisor-v0.3`
* **Cambios introducidos:**
  * Eliminación total de heurísticas prescriptivas y árboles condicionales.
  * Introducción de principios de parada temprana y evaluación iterativa: el agente debía evaluar si una consulta adicional difícilmente alteraría el riesgo, la suficiencia o la recomendación.
* **Resultado / Aprendizaje:**
  * Corrida 003: Fallo de timeout a los 30s por latencia de red corporativa (motivando DEC-003: timeout 90s + retry).
  * Corrida 004: Con timeout de 90s, el agente volvió a consultar las 3 herramientas ante un horizonte de 1 solo día, demostrando que los principios generales no eran suficientes para frenar la inercia exhaustiva del LLM (DEC-004).

---

## Versión V0.4 — Relevancia Marginal y Regla de Justificación Previa (Baseline Congelado)
* **Modelo:** `gemini-3.1-flash-lite`
* **Prompt Version:** `sacme-supervisor-v0.4`
* **Cambios introducidos:**
  * Se agregó la **Regla de Justificación Previa para Herramientas Secundarias**:
    * Antes de invocar cualquier herramienta secundaria, el agente debe formular qué incertidumbre material intenta resolver.
    * Una herramienta secundaria sólo debe llamarse si su resultado podría alterar materialmente: (1) clasificación de riesgo, (2) suficiencia de evidencia, o (3) recomendación operativa.
    * Si no se identifica un impacto plausible sobre esos tres elementos, se ordena la detención inmediata.
* **Resultado / Aprendizaje:**
  * Corrida 005: Ante 1 día, el modelo volvió a consumir 3/3 tools. Se decidió **no continuar sobre-endureciendo el prompt** para no convertir la deliberación agéntica en un árbol determinístico simulado (DEC-005).
  * Corrida 006 (3 días, NORMAL) y Corrida 007 (5 días, OBSERVAR): Se ratificó la solidez, consistencia y sensibilidad operativa del prompt V0.4, cerrando el ciclo experimental (DEC-006).
