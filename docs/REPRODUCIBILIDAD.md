# Guía de Reproducibilidad Paso a Paso

**Trabajo Final Individual — MBA UCEMA: Programación de y con Agentes de IA**

Este repositorio está diseñado para que cualquier evaluador académico (humano o agente evaluador) pueda reproducir y verificar el sistema en menos de 3 minutos.

---

## 1. Requisitos Previos
- Python 3.10 o superior instalado.
- Conexión a Internet (para descargar pronóstico de Open-Meteo y opcionalmente consultar Gemini).

---

## 2. Instalación

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd agente-supervisor-demanda-ucema

# 2. Instalar dependencias mínimas (pandas, openpyxl)
pip install -r requirements.txt
```

---

## 3. Ejecución de la Suite de Tests (Modo Simulado / USD 0)

Para verificar la integridad del código, el funcionamiento de las 3 herramientas y la preservación inmutable de las 7 corridas sin consumir tokens:

```bash
python tests/test_agent.py
```

*Resultado esperado:* **7/7 tests pasando exitosamente** con reporte de verificación de hashes.

---

## 4. Ejecución del Agente en Modo Simulado (Dry-Run)

Permite observar el comportamiento agéntico completo sin necesidad de configurar una API key:

```bash
python agente/agent_supervisor.py --dry-run "Evaluar el riesgo de demanda para los próximos 3 días."
```

---

## 5. Ejecución del Agente en Modo Real (Google Gemini Free Tier)

1. Obtener una clave gratuita en [Google AI Studio](https://aistudio.google.com/).
2. Configurar la variable de entorno:
   ```bash
   # En Windows PowerShell:
   $env:GEMINI_API_KEY="tu_api_key_aqui"
   
   # En Linux / macOS:
   export GEMINI_API_KEY="tu_api_key_aqui"
   ```
3. Ejecutar el agente indicando el identificador de corrida y confirmando Free Tier:
   ```bash
   python agente/agent_supervisor.py --corrida corrida_evaluacion --confirm-free-tier "Evaluar el riesgo de demanda para los próximos 3 días."
   ```
4. El dictamen se imprimirá en consola y se guardará la evidencia auditable en `corridas/corrida_evaluacion/run.json`.

---

## 6. Consideraciones de Red y Certificados TLS

El agente utiliza **validación estricta de certificados TLS** (`ssl.create_default_context()`) para todas sus conexiones externas HTTPS (Open-Meteo y Gemini API).

Si el sistema se ejecuta dentro de una red empresarial con proxies de inspección SSL profunda (ej. Zscaler, Fortinet, BlueCoat):
* La estación debe tener instalado el certificado de CA corporativo en el almacén de confianza del sistema operativo.
* Alternativamente, se puede apuntar la variable de entorno estándar de OpenSSL al bundle de certificados empresariales:
  ```bash
  # En PowerShell:
  $env:SSL_CERT_FILE = "C:\ruta\al\certificado_corporativo_ca.pem"
  
  # En Linux / macOS:
  export SSL_CERT_FILE="/ruta/al/certificado_corporativo_ca.pem"
  ```
* El sistema **no incluye ni admite mecanismos de desactivación de certificados**, cumpliendo con los estándares de seguridad de software para entornos públicos.

---

## 7. Naturaleza Estocástica del LLM y Trazabilidad

* **Reproducibilidad del Circuito y Contratos:** El flujo agéntico, la secuencia de herramientas, la sanitización de seguridad y las reglas de clasificación son completamente reproducibles.
* **Varianza de Texto del LLM:** Debido a la naturaleza estocástica del modelo generativo (temperatura de inferencia por defecto en la API de Google), el texto exacto generado en el análisis técnico puede presentar variaciones estilísticas menores entre distintas ejecuciones reales.
* **Evidencia Histórica Exacta:** Los archivos `run.json` preservados en `corridas/` constituyen la evidencia exacta, inmutable y auditable de lo producido en cada corrida real experimental.

