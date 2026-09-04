# Evidencia Económica y Trazabilidad de Consumo de Tokens (D4)

**Trabajo Final Individual — MBA UCEMA: Programación de y con Agentes de IA**

---

## 1. Declaración de Origen de la Evidencia y Ausencia de Facturación Comercial

> **Declaración Metodológica Explícita:**  
> Los conteos de tokens provienen de la metadata de uso devuelta por Gemini y preservada dentro de cada `run.json`. No se dispone de factura de proveedor porque las ejecuciones documentadas se realizaron bajo Free Tier / sin billing habilitado. Por eso la evidencia económica primaria es la metadata original preservada en las corridas.

En cada interacción HTTP multi-turno contra la API de Google Gemini (`v1beta/models/gemini-3.1-flash-lite:generateContent`), el servidor de Google devuelve en el cuerpo de la respuesta el objeto oficial de telemetría de consumo:

```json
"usageMetadata": {
  "promptTokenCount": 0,
  "candidatesTokenCount": 0,
  "totalTokenCount": 0
}
```

El cliente nativo del agente (`agente/agent_supervisor.py:603-607`) acumula iterativamente estos valores reportados directamente por Google y los asienta en el registro auditable de cada corrida bajo la clave `"tokens"` (`input_tokens`, `output_tokens`, `total_tokens`, con estado `"REPORTADO_POR_API"`).

---

## 2. Tabla Consolidada de Evidencia Económica por Corrida Principal

| Dimensión Auditada | Corrida 002 (Baseline V0.2) | Corrida 006 (Resiliencia V0.4) | Corrida 007 (Discriminación V0.4) |
| :--- | :--- | :--- | :--- |
| **Modelo Utilizado** | `gemini-3.1-flash-lite` | `gemini-3.1-flash-lite` | `gemini-3.1-flash-lite` |
| **Prompt Version** | `sacme-supervisor-v0.2` | `sacme-supervisor-v0.4` | `sacme-supervisor-v0.4` |
| **Input Tokens (promptTokenCount)** | **6.976** | **7.438** | **8.056** |
| **Output Tokens (candidatesTokenCount)**| **673** | **631** | **700** |
| **Tokens Totales Reales** | **7.649** | **8.069** | **8.756** |
| **Estado de Conteo** | `REPORTADO_POR_API` | `REPORTADO_POR_API` | `REPORTADO_POR_API` |
| **Costo API Observado (Proveedor)** | **USD 0** | **USD 0** | **USD 0** |
| **Costo Incremental del Proyecto** | **USD 0** | **USD 0** | **USD 0** |
| **Cost Basis** | `GOOGLE_GEMINI_FREE_TIER` | `GOOGLE_GEMINI_FREE_TIER` | `GOOGLE_GEMINI_FREE_TIER` |
| **Pricing Tier Declarado** | `FREE_TIER` | `FREE_TIER` | `FREE_TIER` |
| **Billing Status** | `USER_VERIFIED_NO_BILLING` | `USER_VERIFIED_NO_BILLING` | `USER_VERIFIED_NO_BILLING` |
| **Confirmación de Operador** | `user_confirmed_free_tier: true` | `user_confirmed_free_tier: true` | `user_confirmed_free_tier: true` |
| **Factura de Proveedor** | No disponible (Free Tier) | No disponible (Free Tier) | No disponible (Free Tier) |
| **Archivo de Evidencia Primaria** | [`corridas/corrida_002/run.json`](../corridas/corrida_002/run.json) | [`corridas/corrida_006/run.json`](../corridas/corrida_006/run.json) | [`corridas/corrida_007/run.json`](../corridas/corrida_007/run.json) |
| **Archivo de Metadata Derivada** | [`corridas/corrida_002/metadata.json`](../corridas/corrida_002/metadata.json) | [`corridas/corrida_006/metadata.json`](../corridas/corrida_006/metadata.json) | [`corridas/corrida_007/metadata.json`](../corridas/corrida_007/metadata.json) |
| **Hash Criptográfico SHA-256 (`run.json`)** | `cd2561ba4acafd92f3be...` | `c282f6416a8f37948dc6...` | `21719d6e2d938dc870ba...` |

---

## 3. Promedios y Proyecciones Operativas

* **Consumo Promedio por Corrida Exitosa:**  
  $$\text{Promedio} = \frac{7.649 + 8.069 + 8.756}{3} = \mathbf{8.158 \text{ tokens/corrida}}$$
  * Input promedio: **7.526 tokens**
  * Output promedio: **632 tokens**

* **Frecuencia Operativa Supuesta:**  
  1 evaluación diaria, programada al inicio de la jornada operativa matutina coincidiendo con la actualización del pronóstico del Servicio Meteorológico Nacional y partes de CAMMESA.

* **Proyección Semanal (7 evaluaciones):**  
  $$7 \times 8.158 \approx \mathbf{57.100 \text{ tokens/semana}}$$  
  * Costo directo observado de API: **USD 0** (dentro de los límites del Free Tier).

* **Proyección Anual (365 evaluaciones):**  
  $$365 \times 8.158 \approx \mathbf{2.980.000 \text{ tokens/año}}$$  
  * Costo directo observado de API: **USD 0** bajo el entorno usado (Free Tier oficial de Google AI Studio sin billing habilitado).

---

## 4. Distinción entre Costo de API y Costos Totales de Proyecto

Para un análisis económico riguroso y transparente:

1. **Costo de API de Proveedor (Medido y Auditado):**  
   * **USD 0** observado e incremental. El proyecto se mantuvo estrictamente en Free Tier.
2. **Costos No Medidos (Excluidos de la Métrica de API):**  
   * Tiempo de ingeniería y desarrollo del agente supervisor.
   * Cómputo local de la estación de trabajo donde se ejecutan los scripts y el preprocesamiento de series temporales.
   * Conectividad a Internet.
3. **Escenario Comercial Hipotético (Paid Tier):**  
   * Cualquier cálculo de costos sobre tiers comerciales pagos se mantiene formalmente bajo el marcador:  
     `PENDIENTE_VERIFICACION_PRECIO_OFICIAL`  
   * No se introducen estimaciones de precios por millón de tokens no respaldadas por contratos vigentes del proveedor.
