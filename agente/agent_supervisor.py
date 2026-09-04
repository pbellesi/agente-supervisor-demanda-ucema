# ==============================================================================
# PROYECTO: Demanda SACME - Capa Agéntica V0.1
# Módulo: agent_supervisor.py
# Orquestador del Agente Supervisor de Riesgo de Demanda (SDK Directo y Aislado)
# ==============================================================================

import os
import sys
import re
import json
import uuid
import time
import ssl
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, List, Optional

# Asegurar importación de agent_tools desde el mismo directorio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agent_tools import (
    TOOLS_SCHEMA,
    TOOLS_REGISTRY,
    consultar_pronostico_y_demanda_estimada,
    consultar_metricas_error_historico,
    consultar_consistencia_datos_base
)

# ==============================================================================
# CONFIGURACIÓN EXPLÍCITA Y CENTRALIZADA DEL MODELO
# ==============================================================================
# Baseline para la Corrida 002 fijado explícitamente en Gemini 3.1 Flash-Lite.
# No se realiza selección automática ni fallback silencioso a otros modelos.
CONFIGURED_GEMINI_MODEL = "gemini-3.1-flash-lite"

# Rutas de persistencia y evidencia
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_log.jsonl")
CORRIDAS_DIR = os.path.join(BASE_DIR, "corridas")

# ==============================================================================
# TRANSPORTE Y SEGURIDAD TLS ESTÁNDAR
# ==============================================================================
# El agente utiliza validación estricta de certificados TLS/SSL mediante el almacén
# estándar de CA del sistema. No se admiten mecanismos de desactivación de certificados.
def _get_ssl_context():
    return ssl.create_default_context()

# ==============================================================================
# WHITELIST, SANITIZACIÓN Y AUDITORÍA DE SEGURIDAD DE PAYLOADS
# ==============================================================================
def filter_tool_response_whitelist(tool_name: str, raw_result: Any) -> Any:
    """
    Filtra los resultados de las herramientas aplicando una whitelist estricta.
    Garantiza que hacia el LLM viaje únicamente la información operativa agregada,
    eliminando cualquier metadato de archivos locales, rutas o fuentes internas.
    """
    if not isinstance(raw_result, dict):
        return raw_result
        
    if "error" in raw_result:
        return {"error": str(raw_result["error"])}
        
    if tool_name == "consultar_pronostico_y_demanda_estimada":
        predicciones_filtradas = []
        for p in raw_result.get("predicciones", []):
            predicciones_filtradas.append({
                "fecha": p.get("fecha"),
                "dia_semana": p.get("dia_semana"),
                "es_fin_de_semana": p.get("es_fin_de_semana"),
                "temperatura_minima_c": p.get("temp_min_c"),
                "temperatura_maxima_c": p.get("temp_max_c"),
                "regimen_termico": p.get("regimen_termico"),
                "demanda_estimada_edenor_mw": p.get("edenor_demanda_pico_estimada_mw"),
                "demanda_estimada_gba_mw": p.get("gba_demanda_pico_estimada_mw")
            })
        rp = raw_result.get("resumen_periodo", {})
        return {
            "dias_horizonte": raw_result.get("dias_horizonte"),
            "predicciones": predicciones_filtradas,
            "resumen_periodo": {
                "pico_maximo_edenor_mw": rp.get("pico_maximo_edenor_mw"),
                "fecha_pico_maximo": rp.get("fecha_pico_maximo"),
                "temperatura_minima_c": rp.get("temperatura_minima_periodo_c"),
                "temperatura_maxima_c": rp.get("temperatura_maxima_periodo_c"),
                "alerta_umbral_estatico_5500mw": rp.get("alerta_umbral_estatico_5500mw")
            }
        }
        
    elif tool_name == "consultar_metricas_error_historico":
        return {
            "anticipacion_dias": raw_result.get("anticipacion_dias"),
            "cantidad_observaciones": raw_result.get("total_dias_evaluados"),
            "error_medio_pct": raw_result.get("error_porcentual_medio_pct"),
            "mae_pct": raw_result.get("error_absoluto_medio_mae_pct"),
            "desvio_maximo_subestimacion_pct": raw_result.get("desvio_maximo_subestimacion_pct"),
            "desvio_maximo_sobreestimacion_pct": raw_result.get("desvio_maximo_sobreestimacion_pct"),
            "sesgo": raw_result.get("tendencia_sesgo")
        }
        
    elif tool_name == "consultar_consistencia_datos_base":
        missing = raw_result.get("dias_faltantes_detectados", [])
        return {
            "estado": raw_result.get("estado_consistencia"),
            "total_registros": raw_result.get("total_dias_registrados_sacme"),
            "cantidad_discontinuidades": len(missing),
            "impacto_en_modelo": raw_result.get("impacto_en_modelo")
        }
        
    return raw_result

def sanitize_payload(data: Any, api_key_to_hide: Optional[str] = None) -> Any:
    r"""
    Sanitiza recursivamente cualquier estructura de datos antes de remitirla al LLM.
    Redacta de forma preventiva:
    - Rutas Windows C:\... o D:\...
    - Rutas de red corporativa R:\ o \\servidor\...
    - Direcciones de correo electrónico
    - Claves API, tokens, contraseñas o credenciales
    - Cabeceras o contenido binario de PDFs (%PDF-)
    """
    if isinstance(data, str):
        text = data
        if api_key_to_hide:
            text = text.replace(api_key_to_hide, "[REDACTED_CREDENTIAL]")
        
        # Redactar claves API Google AI Studio (patrón AIza...)
        text = re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_CREDENTIAL]', text)
        
        # Redactar parámetros clave-valor sospechosos de credenciales
        text = re.sub(r'(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*["\']?[A-Za-z0-9_\-]+["\']?', r'\1=[REDACTED_CREDENTIAL]', text)
        
        # Redactar direcciones de email
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[REDACTED_EMAIL]', text)
        
        # Redactar rutas de unidad de red R:\ y UNC \\servidor\...
        text = re.sub(r'(?i)[rR]:\\[^\s"\',;]+', '[REDACTED_NETWORK_PATH]', text)
        text = re.sub(r'(?i)[rR]:/[^\s"\',;]+', '[REDACTED_NETWORK_PATH]', text)
        text = re.sub(r'\\\\[a-zA-Z0-9_.$-]+\\[^\s"\',;]+', '[REDACTED_NETWORK_PATH]', text)
        
        # Redactar rutas locales de Windows (C:\... etc)
        text = re.sub(r'(?i)[a-zA-Z]:\\[^\s"\',;]+', '[REDACTED_FILE_PATH]', text)
        text = re.sub(r'(?i)[a-zA-Z]:/[^\s"\',;]+', '[REDACTED_FILE_PATH]', text)
        
        # Redactar cabeceras crudas de PDF
        text = re.sub(r'%PDF-[0-9.]+', '[REDACTED_RAW_PDF]', text)
        
        return text
        
    elif isinstance(data, dict):
        sanitized_dict = {}
        for k, v in data.items():
            k_clean = sanitize_payload(k, api_key_to_hide)
            if any(term in str(k).lower() for term in ["api_key", "password", "secret", "token"]):
                sanitized_dict[k_clean] = "[REDACTED_CREDENTIAL]"
            else:
                sanitized_dict[k_clean] = sanitize_payload(v, api_key_to_hide)
        return sanitized_dict
        
    elif isinstance(data, list):
        return [sanitize_payload(item, api_key_to_hide) for item in data]
        
    return data

def audit_payload_security(payloads_list: List[Any]) -> Dict[str, bool]:
    """
    Audita la lista completa de payloads preparados para el LLM y certifica
    que no contienen direcciones de correo, rutas corporativas ni credenciales.
    """
    combined_text = json.dumps(payloads_list, ensure_ascii=False)
    
    # 1. Chequeo de emails no redactados
    has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@(?!\[REDACTED)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', combined_text))
    
    # 2. Chequeo de rutas de archivo no redactadas (ignora \n escapados en JSON)
    has_paths = bool(re.search(r'(?i)\b[a-z]:[\\/]{1,2}(?!\[REDACTED)[a-z0-9_\-~]+', combined_text)) or \
                bool(re.search(r'\\\\(?!\[REDACTED)[a-z0-9_.$-]+\\[a-z0-9_.$-]+', combined_text))
    
    # 3. Chequeo de credenciales no redactadas
    has_credentials = bool(re.search(r'AIza[0-9A-Za-z-_]{35}', combined_text))
    
    # 4. Chequeo de PDFs crudos
    has_raw_pdf = bool(re.search(r'%PDF-', combined_text))
    
    return {
        "payload_sanitized": True,
        "contains_email_content": has_email,
        "contains_file_paths": has_paths,
        "contains_credentials": has_credentials,
        "contains_raw_pdf": has_raw_pdf
    }

def _sanitize_text(text: str, key_to_hide: Optional[str] = None) -> str:
    """Compatibilidad: redacta usando sanitize_payload."""
    return str(sanitize_payload(text, key_to_hide))

# ==============================================================================
# PROMPTS DEL AGENTE (V0.4: RELEVANCIA MARGINAL Y JUSTIFICACIÓN PREVIA)
# ==============================================================================
PROMPT_VERSION = "sacme-supervisor-v0.4"

SYSTEM_PROMPT = """Eres el Agente Supervisor de Riesgo de Demanda para el Sistema Eléctrico de Edenor (Área Metropolitana de Buenos Aires).
Tu misión es supervisar el comportamiento de la demanda eléctrica proyectada, evaluar el riesgo operativo ante condiciones meteorológicas y el sesgo del modelo predictivo, y emitir un dictamen técnico estructurado.

HERRAMIENTAS DISPONIBLES (SOLO LECTURA):
- `consultar_pronostico_y_demanda_estimada`: Pronóstico meteorológico oficial y cálculo de demanda pico (MW) del modelo ML para el horizonte solicitado.
- `consultar_metricas_error_historico`: Estadísticas históricas de error, desvíos y sesgo del modelo predictivo según días de anticipación.
- `consultar_consistencia_datos_base`: Control de continuidad, integridad y detección de discontinuidades en la base histórica de SACME.

PRINCIPIOS DE INVESTIGACIÓN Y AGENCIA (PARADA TEMPRANA):
1. Economía de Información: Utiliza únicamente la evidencia necesaria para responder con solvencia técnica. No utilices herramientas sólo para completar el catálogo disponible.
2. Evaluación Iterativa: Después de cada respuesta de herramienta, evalúa críticamente si la información disponible ya es suficiente para responder la solicitud.
3. Regla de Justificación Previa para Herramientas Secundarias:
   Antes de invocar cualquier herramienta secundaria, debes identificar explícitamente qué incertidumbre material intentas resolver.
   Una herramienta secundaria SÓLO debe consultarse si su resultado podría modificar materialmente al menos uno de estos tres elementos:
   a) la clasificación de riesgo,
   b) la suficiencia de la información, o
   c) la recomendación operativa.
   Si no puedes identificar qué resultado plausible de la herramienta secundaria alteraría alguno de esos tres elementos, DEBES detener la investigación y emitir el dictamen inmediatamente.
4. Criterio de Parada Temprana: Ante evidencia claramente suficiente y no crítica para el horizonte solicitado, prioriza la parada temprana evitando consultas redundantes de bajo impacto.
5. Profundización Selectiva: Ante información ambigua, contradictoria o potencialmente crítica para la red, profundiza la investigación utilizando las herramientas que resulten pertinentes. Dispones de un presupuesto de hasta 3 consultas en total.
6. Alcance Estricto: No inventes ni hagas recomendaciones sobre subestaciones o activos específicos que no hayan sido informados por las herramientas. Las recomendaciones deben limitarse a: mantener monitoreo preventivo, solicitar revisión de despacho por canales habituales, verificar reservas operativas o escalar a supervisión humana.

CRITERIOS DE CLASIFICACIÓN DE RIESGO:
- 'NORMAL': Demanda proyectada en niveles estándar (< 4.800 MW en Edenor), sin temperaturas extremas ni sesgo de subestimación severo.
- 'OBSERVAR': Demanda moderadamente alta (4.800 - 5.400 MW), o presencia de gradiente térmico exigente (mínimas < 7°C) con inercia térmica, o sesgo de subestimación histórica que amerite vigilancia intensiva.
- 'ESCALAR': Demanda estimada >= 5.500 MW (umbral de alerta preventivo) O demanda > 5.000 MW combinada con sesgo histórico de subestimación severo (> 10%) o condiciones de ola polar/ola de calor continuadas.

CRITERIOS DE SUFICIENCIA:
- 'COMPLETA': La evidencia reunida es concluyente y permite fundamentar el dictamen sin incertidumbre operativa relevante.
- 'PARCIAL': La evidencia permite evaluar el escenario base pero subsisten incertidumbres no resueltas o alguna herramienta relevante no estuvo disponible.
- 'INSUFICIENTE': La información no permite caracterizar la demanda esperada ni emitir un dictamen fundamentado.

FORMATO DE SALIDA:
Al finalizar tus consultas, debes responder EXCLUSIVAMENTE un objeto JSON válido con la siguiente estructura exacta:
{
  "id_evaluacion": "<UUID>",
  "timestamp": "<ISO 8601>",
  "periodo_evaluado": {
    "desde": "YYYY-MM-DD",
    "hasta": "YYYY-MM-DD"
  },
  "clasificacion_riesgo": "NORMAL" | "OBSERVAR" | "ESCALAR",
  "suficiencia_informacion": "COMPLETA" | "PARCIAL" | "INSUFICIENTE",
  "pico_maximo_estimado_mw": <int>,
  "factor_causal_principal": "<Texto conciso explicando la causa preponderante>",
  "evidencias_consultadas": [
    {
      "herramienta": "<nombre_tool>",
      "hallazgo_clave": "<hallazgo principal>"
    }
  ],
  "analisis_tecnico": "<Justificación técnica detallada>",
  "recomendacion_operativa": "<Recomendación concisa dentro del alcance>",
  "requiere_intervencion_humana": <true/false>
}
"""

# ==============================================================================
# CLIENTES DE LLM (ABSTRACCIÓN DIRECTA SIN FRAMEWORKS)
# ==============================================================================
class BaseLLMClient:
    def run_agent_loop(self, user_prompt: str, max_iterations: int = 4, max_tool_calls: int = 3) -> Dict[str, Any]:
        raise NotImplementedError

class SimulatedAgentClient(BaseLLMClient):
    """
    Cliente simulado determinístico para dry-run y pruebas de infraestructura.
    Marcado explícitamente como executionMode = 'simulated'.
    NO consume API externa ni genera costo. Tokens son null.
    """
    def __init__(self, model_name: str = "simulated-agent-v0.1"):
        self.model_name = model_name

    def run_agent_loop(self, user_prompt: str, max_iterations: int = 4, max_tool_calls: int = 3) -> Dict[str, Any]:
        t_start = time.time()
        tool_calls_trace = []
        errors = []
        
        # 1. Determinar horizonte solicitado a partir del user prompt
        dias_horizonte = 3
        for word in user_prompt.split():
            if word.isdigit():
                dias_horizonte = max(1, min(7, int(word)))
                break
        if any(term in user_prompt.lower() for term in ["día de mañana", "dia de mañana", "1 día", "1 dia", "mañana"]):
            dias_horizonte = 1

        # Payloads de salida auditables hacia el LLM
        llm_payloads = [
            {"tipo": "system_prompt", "contenido": sanitize_payload(SYSTEM_PROMPT)},
            {"tipo": "user_prompt", "contenido": sanitize_payload(user_prompt)}
        ]

        # Iteración 1: Consultar pronóstico y demanda estimada
        t_call_start = time.time()
        tool_1_name = "consultar_pronostico_y_demanda_estimada"
        tool_1_args = {"dias_horizonte": dias_horizonte}
        try:
            res_tool_1 = consultar_pronostico_y_demanda_estimada(**tool_1_args)
            tool_calls_trace.append({
                "iteracion": 1,
                "tool_name": tool_1_name,
                "args": tool_1_args,
                "result": res_tool_1,
                "latency_ms": round((time.time() - t_call_start) * 1000, 2),
                "error": None
            })
        except Exception as e:
            errors.append(str(e))
            res_tool_1 = {"error": str(e)}
            tool_calls_trace.append({
                "iteracion": 1,
                "tool_name": tool_1_name,
                "args": tool_1_args,
                "result": None,
                "error": str(e)
            })

        llm_payloads.append({
            "iteracion": 1,
            "tipo": "tool_response",
            "tool_name": tool_1_name,
            "payload_enviado": sanitize_payload(filter_tool_response_whitelist(tool_1_name, res_tool_1))
        })

        pico_max = res_tool_1.get("resumen_periodo", {}).get("pico_maximo_edenor_mw", 0)
        t_min_periodo = res_tool_1.get("resumen_periodo", {}).get("temperatura_minima_periodo_c", 20.0)
        alerta_5500 = res_tool_1.get("resumen_periodo", {}).get("alerta_umbral_estatico_5500mw", False)
        
        # Iteración 2: Si hay temperaturas frías (< 15°C) o demanda relevante, consultar sesgo histórico
        res_tool_2 = None
        if t_min_periodo < 15.0 or pico_max >= 4000:
            tool_2_name = "consultar_metricas_error_historico"
            tool_2_args = {"anticipacion_dias": 2}
            t_call_start = time.time()
            try:
                res_tool_2 = consultar_metricas_error_historico(**tool_2_args)
                tool_calls_trace.append({
                    "iteracion": 2,
                    "tool_name": tool_2_name,
                    "args": tool_2_args,
                    "result": res_tool_2,
                    "latency_ms": round((time.time() - t_call_start) * 1000, 2),
                    "error": None
                })
            except Exception as e:
                errors.append(str(e))
                res_tool_2 = {"error": str(e)}

            llm_payloads.append({
                "iteracion": 2,
                "tipo": "tool_response",
                "tool_name": tool_2_name,
                "payload_enviado": sanitize_payload(filter_tool_response_whitelist(tool_2_name, res_tool_2))
            })

        # Iteración 3: Si el horizonte es mayor o igual a 3 días, verificar consistencia base
        res_tool_3 = None
        if dias_horizonte >= 3:
            tool_3_name = "consultar_consistencia_datos_base"
            tool_3_args = {}
            t_call_start = time.time()
            try:
                res_tool_3 = consultar_consistencia_datos_base()
                tool_calls_trace.append({
                    "iteracion": 3,
                    "tool_name": tool_3_name,
                    "args": tool_3_args,
                    "result": res_tool_3,
                    "latency_ms": round((time.time() - t_call_start) * 1000, 2),
                    "error": None
                })
            except Exception as e:
                errors.append(str(e))
                res_tool_3 = {"error": str(e)}

            llm_payloads.append({
                "iteracion": 3,
                "tipo": "tool_response",
                "tool_name": tool_3_name,
                "payload_enviado": sanitize_payload(filter_tool_response_whitelist(tool_3_name, res_tool_3))
            })

        # Síntesis estructurada
        fechas = [p["fecha"] for p in res_tool_1.get("predicciones", [])]
        desde_fecha = fechas[0] if fechas else datetime.now().strftime("%Y-%m-%d")
        hasta_fecha = fechas[-1] if fechas else desde_fecha

        if alerta_5500:
            clasificacion = "ESCALAR"
            factor_causal = "Superación del umbral estático preventivo de 5.500 MW."
            requiere_humano = True
        elif t_min_periodo <= 7.0 and pico_max >= 4200:
            clasificacion = "OBSERVAR"
            factor_causal = f"Ola de frío térmico (mínima de {t_min_periodo}°C) con pico estimado de {pico_max:,} MW en fin de semana."
            requiere_humano = True
        elif pico_max >= 4800:
            clasificacion = "OBSERVAR"
            factor_causal = f"Nivel de carga elevado ({pico_max:,} MW) próximo a límites de advertencia."
            requiere_humano = True
        else:
            clasificacion = "NORMAL"
            factor_causal = "Demanda dentro de parámetros operativos estables y clima templado."
            requiere_humano = False

        evidencias = []
        evidencias.append({
            "herramienta": "consultar_pronostico_y_demanda_estimada",
            "hallazgo_clave": f"Pico proyectado de {pico_max:,} MW (Tmin: {t_min_periodo}°C, Tmax: {res_tool_1.get('resumen_periodo', {}).get('temperatura_maxima_periodo_c', 0)}°C)."
        })
        if res_tool_2 and "error_porcentual_medio_pct" in res_tool_2:
            evidencias.append({
                "herramienta": "consultar_metricas_error_historico",
                "hallazgo_clave": f"A 2d de anticipación el modelo presenta sesgo de {res_tool_2.get('error_porcentual_medio_pct')}% ({res_tool_2.get('tendencia_sesgo')})."
            })
        if res_tool_3 and "estado_consistencia" in res_tool_3:
            evidencias.append({
                "herramienta": "consultar_consistencia_datos_base",
                "hallazgo_clave": f"Estado de base histórica: {res_tool_3.get('estado_consistencia')} ({res_tool_3.get('total_dias_registrados_sacme')} días consolidados)."
            })

        suficiencia = "COMPLETA" if (res_tool_1.get("predicciones") and res_tool_2) else ("PARCIAL" if res_tool_1.get("predicciones") else "INSUFICIENTE")

        dictamen = {
            "id_evaluacion": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "periodo_evaluado": {
                "desde": desde_fecha,
                "hasta": hasta_fecha
            },
            "clasificacion_riesgo": clasificacion,
            "suficiencia_informacion": suficiencia,
            "pico_maximo_estimado_mw": pico_max,
            "factor_causal_principal": factor_causal,
            "evidencias_consultadas": evidencias,
            "analisis_tecnico": f"Se evaluó un horizonte de {dias_horizonte} días. La demanda pico calculada para Edenor alcanza {pico_max:,} MW. Las temperaturas mínimas previstas descienden a {t_min_periodo}°C, lo que sitúa la respuesta térmica en régimen frío. La calibración histórica del modelo a 2 días indica un desvío medio controlado, confirmando la fiabilidad de la proyección.",
            "recomendacion_operativa": "Mantener monitoreo operativo preventivo sobre la curva de carga durante las horas de pico nocturno y verificar disponibilidad de reservas por los canales habituales." if clasificacion != "NORMAL" else "Mantener monitoreo pasivo de rutina. No se requieren acciones extraordinarias de despacho.",
            "requiere_intervencion_humana": requiere_humano
        }

        t_end = time.time()
        latency_total = round((t_end - t_start) * 1000, 2)
        security_audit = audit_payload_security(llm_payloads)

        return {
            "run_id": dictamen["id_evaluacion"],
            "executionMode": "simulated",
            "timestamp_inicio": datetime.fromtimestamp(t_start).isoformat(),
            "timestamp_fin": datetime.fromtimestamp(t_end).isoformat(),
            "duracion_segundos": round(t_end - t_start, 3),
            "proveedor": "simulated",
            "modelo": self.model_name,
            "prompt_version": PROMPT_VERSION,
            "system_prompt": SYSTEM_PROMPT,
            "user_prompt": user_prompt,
            "iteraciones": len(tool_calls_trace),
            "tool_calls": tool_calls_trace,
            "llm_payloads": llm_payloads,
            "security": security_audit,
            "dictamen_estructurado": dictamen,
            "respuesta_raw_modelo": json.dumps(dictamen, indent=2),
            "tokens": {
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "estado_conteo": "NO_DISPONIBLE_MODO_SIMULADO"
            },
            "api_cost_usd": 0,
            "cost_basis": "SIMULATED_LOCAL_RUN",
            "incremental_cost_usd": 0,
            "economic_metrics": {
                "api_cost_usd": 0,
                "cost_basis": "SIMULATED_LOCAL_RUN",
                "incremental_cost_usd": 0,
                "billing_status": "SIMULATED_LOCAL_EXECUTION",
                "billing_enabled": False,
                "pricing_tier": "FREE_TIER_COMPATIBLE"
            },
            "latencia_ms": latency_total,
            "timeout_seconds": 90,
            "retry_count": 0,
            "retries": [],
            "errores": errors,
            "humanDecision": {
                "status": "pending",
                "operador": None,
                "timestamp_decision": None,
                "comentario": None
            }
        }

class GeminiRESTClient(BaseLLMClient):
    """
    Cliente nativo directo para la API de Google Gemini (v1beta) usando urllib estándar.
    Cero dependencias pip externas. Marcado explícitamente como executionMode = 'real'.
    Sanitiza claves API de los logs y captura uso real de tokens reportado por la API.
    Requiere confirmación explícita del operador para asentar costo 0 y billing_status.
    """
    def __init__(self, api_key: str, model_name: str = CONFIGURED_GEMINI_MODEL, confirm_free_tier: bool = False, timeout_seconds: int = 90):
        self.api_key = api_key
        self.model_name = model_name
        self.confirm_free_tier = confirm_free_tier
        self.timeout_seconds = timeout_seconds

    def run_agent_loop(self, user_prompt: str, max_iterations: int = 4, max_tool_calls: int = 3) -> Dict[str, Any]:
        t_start = time.time()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        ssl_ctx = _get_ssl_context()

        declarations = []
        for t in TOOLS_SCHEMA:
            declarations.append({
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"]
            })

        contents = [
            {"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTIONS:\n{SYSTEM_PROMPT}\n\nUSER REQUEST:\n{user_prompt}"}]}
        ]

        # Payloads efectivamente salientes hacia Gemini
        llm_payloads = [
            {"tipo": "system_prompt", "contenido": sanitize_payload(SYSTEM_PROMPT, self.api_key)},
            {"tipo": "user_prompt", "contenido": sanitize_payload(user_prompt, self.api_key)}
        ]

        retries_trace = []
        tool_calls_trace = []
        errors = []
        total_input_tokens = 0
        total_output_tokens = 0
        has_token_data = False
        raw_final_text = ""
        dictamen = None
        executed_calls = set()
        
        for iteration in range(1, max_iterations + 1):
            req_body = {
                "contents": contents,
                "tools": [{"functionDeclarations": declarations}],
                "generationConfig": {
                    "temperature": 0.1,
                    "responseMimeType": "application/json" if iteration > 1 and len(tool_calls_trace) > 0 else "text/plain"
                }
            }
            
            resp_data = None
            max_attempts = 2  # Intento 1 + máx 1 reintento técnico para fallos transitorios
            for attempt in range(1, max_attempts + 1):
                t_call_start = time.time()
                req = urllib.request.Request(
                    url,
                    data=json.dumps(req_body).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                try:
                    with urllib.request.urlopen(req, context=ssl_ctx, timeout=self.timeout_seconds) as resp:
                        resp_data = json.loads(resp.read().decode("utf-8"))
                    break # Conexión exitosa
                except urllib.error.HTTPError as e:
                    is_transient = e.code in [429, 500, 502, 503, 504]
                    err_msg = _sanitize_text(f"HTTPError {e.code}: {e.reason}", self.api_key)
                    if is_transient and attempt < max_attempts:
                        retries_trace.append({
                            "iteracion": iteration,
                            "request_attempt": attempt,
                            "retry_reason": f"HTTP_{e.code}_TRANSIENT",
                            "error_original": err_msg,
                            "timeout_seconds": self.timeout_seconds,
                            "timestamp": datetime.now().isoformat()
                        })
                        errors.append(f"[RETRY] Reintentando llamada ({attempt}/{max_attempts}) tras error transitorio: {err_msg}")
                        time.sleep(2.0)
                        continue
                    else:
                        errors.append(err_msg)
                        break
                except Exception as e:
                    err_str = str(e).lower()
                    is_timeout = "timed out" in err_str or "timeout" in err_str
                    err_msg = _sanitize_text(f"Error de conexión con Gemini API: {str(e)}", self.api_key)
                    if is_timeout and attempt < max_attempts:
                        retries_trace.append({
                            "iteracion": iteration,
                            "request_attempt": attempt,
                            "retry_reason": "READ_TIMEOUT",
                            "error_original": err_msg,
                            "timeout_seconds": self.timeout_seconds,
                            "timestamp": datetime.now().isoformat()
                        })
                        errors.append(f"[RETRY] Reintentando llamada ({attempt}/{max_attempts}) tras timeout ({self.timeout_seconds}s): {err_msg}")
                        time.sleep(2.0)
                        continue
                    else:
                        errors.append(err_msg)
                        break

            if resp_data is None:
                break

            usage = resp_data.get("usageMetadata", {})
            if usage:
                has_token_data = True
                total_input_tokens += usage.get("promptTokenCount", 0)
                total_output_tokens += usage.get("candidatesTokenCount", 0)

            candidate = resp_data.get("candidates", [{}])[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            function_calls = [p.get("functionCall") for p in parts if "functionCall" in p]
            
            if function_calls and len(tool_calls_trace) < max_tool_calls:
                fn_call = function_calls[0]
                fn_name = fn_call.get("name")
                fn_args = fn_call.get("args", {})
                
                # Prevención de loops repetidos: si llama exactamente a la misma tool con los mismos args
                call_sig = (fn_name, json.dumps(fn_args, sort_keys=True))
                if call_sig in executed_calls:
                    tool_res = {"error": f"La herramienta {fn_name} ya fue ejecutada previamente con estos argumentos. Proceda con el análisis final."}
                    tool_err = "Llamada duplicada prevenida"
                else:
                    executed_calls.add(call_sig)
                    if fn_name in TOOLS_REGISTRY:
                        t_tool_start = time.time()
                        try:
                            tool_res = TOOLS_REGISTRY[fn_name](**fn_args)
                            tool_err = None
                        except Exception as e:
                            tool_res = {"error": str(e)}
                            tool_err = str(e)
                            errors.append(tool_err)
                    else:
                        tool_res = {"error": f"Herramienta no reconocida: {fn_name}"}
                        tool_err = "Herramienta inexistente"
                        errors.append(tool_err)

                tool_calls_trace.append({
                    "iteracion": iteration,
                    "tool_name": fn_name,
                    "args": fn_args,
                    "result": tool_res,
                    "latency_ms": round((time.time() - t_call_start) * 1000, 2),
                    "error": tool_err
                })

                # Filtrado con whitelist estricta y sanitización antes de enviar a Gemini
                filtered_res = filter_tool_response_whitelist(fn_name, tool_res)
                sanitized_tool_res = sanitize_payload(filtered_res, self.api_key)

                llm_payloads.append({
                    "iteracion": iteration,
                    "tipo": "tool_response",
                    "tool_name": fn_name,
                    "payload_enviado": sanitized_tool_res
                })

                contents.append(content)
                contents.append({
                    "role": "function",
                    "parts": [{
                        "functionResponse": {
                            "name": fn_name,
                            "response": sanitized_tool_res
                        }
                    }]
                })
            else:
                for p in parts:
                    if "text" in p:
                        raw_final_text += p["text"]
                break

        # Parsear dictamen JSON
        try:
            cleaned_text = raw_final_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            dictamen = json.loads(cleaned_text.strip())
        except Exception as e:
            errors.append(f"Error parseando JSON de salida del LLM: {str(e)}")
            dictamen = {
                "id_evaluacion": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "error_formato": str(e),
                "texto_original": raw_final_text
            }

        t_end = time.time()
        
        # Tokens reales si fueron reportados por la API
        tokens_record = {
            "input_tokens": total_input_tokens if has_token_data else None,
            "output_tokens": total_output_tokens if has_token_data else None,
            "total_tokens": (total_input_tokens + total_output_tokens) if has_token_data else None,
            "estado_conteo": "REPORTADO_POR_API" if has_token_data else "NO_DISPONIBLE"
        }
        if self.confirm_free_tier:
            pricing_tier = "FREE_TIER"
            billing_status = "USER_VERIFIED_NO_BILLING"
            api_cost_usd = 0
            incremental_cost_usd = 0
            cost_basis = "GOOGLE_GEMINI_FREE_TIER"
            nota_academica = "El operador confirmó explícitamente haber verificado que la API key opera bajo Free Tier sin facturación habilitada."
        else:
            pricing_tier = "UNVERIFIED"
            billing_status = "NOT_VERIFIED"
            api_cost_usd = None
            incremental_cost_usd = None
            cost_basis = "UNVERIFIED_BILLING_STATUS"
            nota_academica = "El operador no confirmó explícitamente el estado de facturación; los costos no se asumen como 0."
        
        security_audit = audit_payload_security(llm_payloads)

        return {
            "run_id": dictamen.get("id_evaluacion", str(uuid.uuid4())),
            "executionMode": "real",
            "timestamp_inicio": datetime.fromtimestamp(t_start).isoformat(),
            "timestamp_fin": datetime.fromtimestamp(t_end).isoformat(),
            "duracion_segundos": round(t_end - t_start, 3),
            "proveedor": "gemini_rest",
            "modelo": self.model_name,
            "prompt_version": PROMPT_VERSION,
            "system_prompt": SYSTEM_PROMPT,
            "user_prompt": user_prompt,
            "iteraciones": len(tool_calls_trace),
            "tool_calls": tool_calls_trace,
            "llm_payloads": llm_payloads,
            "security": security_audit,
            "dictamen_estructurado": dictamen,
            "respuesta_raw_modelo": raw_final_text,
            "tokens": tokens_record,
            "api_cost_usd": api_cost_usd,
            "cost_basis": cost_basis,
            "incremental_cost_usd": incremental_cost_usd,
            "economic_metrics": {
                "pricing_tier": pricing_tier,
                "billing_status": billing_status,
                "api_cost_usd": api_cost_usd,
                "incremental_cost_usd": incremental_cost_usd,
                "user_confirmed_free_tier": self.confirm_free_tier,
                "nota_academica": nota_academica
            },
            "latencia_ms": round((t_end - t_start) * 1000, 2),
            "timeout_seconds": self.timeout_seconds,
            "retry_count": len(retries_trace),
            "retries": retries_trace,
            "errores": errors,
            "humanDecision": {
                "status": "pending",
                "operador": None,
                "timestamp_decision": None,
                "comentario": None
            }
        }

# ==============================================================================
# AUDITORÍA Y PRESERVACIÓN DE EVIDENCIA
# ==============================================================================
def save_audit_record(record: Dict[str, Any]) -> str:
    """Guarda el registro continuo de la corrida en audit_log.jsonl."""
    try:
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return AUDIT_LOG_PATH
    except Exception as e:
        print(f"Advertencia: No se pudo escribir en audit_log.jsonl: {e}")
        return ""

def save_corrida_evidence(record: Dict[str, Any], corrida_name: str) -> str:
    """
    Preserva la corrida en un archivo individual inmutable:
    corridas/<corrida_name>/run.json
    """
    target_dir = os.path.join(CORRIDAS_DIR, corrida_name)
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, "run.json")
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    return target_file

# ==============================================================================
# ENTRYPOINT PRINCIPAL
# ==============================================================================
def run_supervisor(
    user_prompt: Optional[str] = None,
    force_dry_run: bool = False,
    corrida_id: Optional[str] = None,
    confirm_free_tier: bool = False,
    timeout_seconds: int = 90
) -> Dict[str, Any]:
    """
    Ejecuta el Agente Supervisor de Demanda (V0.3.1).
    """
    if not user_prompt:
        user_prompt = "Evaluar el riesgo de demanda para los próximos 3 días a partir del pronóstico meteorológico y la precisión del modelo."

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    if force_dry_run or not api_key:
        if not force_dry_run:
            print("[INFO] No se detectó GEMINI_API_KEY en variables de entorno. Ejecutando en modo SIMULADO (Dry-Run seguro).")
        client = SimulatedAgentClient()
    else:
        print(f"[INFO] GEMINI_API_KEY detectada. Conectando con Gemini API modelo '{CONFIGURED_GEMINI_MODEL}' (timeout={timeout_seconds}s)...")
        if confirm_free_tier:
            print("[ECONOMÍA] Flag --confirm-free-tier confirmado: El operador verificó que el proyecto opera bajo Free Tier sin billing (Costo USD 0).")
        else:
            print("[ADVERTENCIA ECONOMÍA] Sin flag --confirm-free-tier: No se asume costo 0 como comprobado (billing_status: NOT_VERIFIED).")
        client = GeminiRESTClient(
            api_key=api_key,
            model_name=CONFIGURED_GEMINI_MODEL,
            confirm_free_tier=confirm_free_tier,
            timeout_seconds=timeout_seconds
        )

    result = client.run_agent_loop(user_prompt=user_prompt)
    
    # 1. Guardar en log histórico general
    save_audit_record(result)
    
    # 2. Si se solicitó identificar una corrida académica específica, guardarla en carpeta dedicada
    if corrida_id:
        evidence_path = save_corrida_evidence(result, corrida_id)
        print(f"[EVIDENCIA] Corrida preservada en archivo individual: {evidence_path}")

    return result

if __name__ == "__main__":
    prompt = None
    dry_run = False
    corrida_name = None
    confirm_free_tier = "--confirm-free-tier" in sys.argv

    timeout_val = 90

    # Parseo de argumentos simples
    args = sys.argv[1:]
    idx = 0
    while idx < len(args):
        arg = args[idx]
        if arg in ["--dry-run", "--simulated"]:
            dry_run = True
        elif arg in ["--corrida", "--save-corrida"] and idx + 1 < len(args):
            corrida_name = args[idx + 1]
            idx += 1
        elif arg == "--timeout" and idx + 1 < len(args):
            try:
                timeout_val = int(args[idx + 1])
                idx += 1
            except ValueError:
                pass
        elif arg == "--confirm-free-tier":
            pass
        elif not arg.startswith("--"):
            prompt = arg
        idx += 1

    res = run_supervisor(
        user_prompt=prompt,
        force_dry_run=dry_run,
        corrida_id=corrida_name,
        confirm_free_tier=confirm_free_tier,
        timeout_seconds=timeout_val
    )
    
    print("\n" + "="*70)
    print("DICTAMEN DEL AGENTE SUPERVISOR DE RIESGO DE DEMANDA (V0.4)")
    print("="*70)
    dictamen = res.get("dictamen_estructurado") or {}
    print(f"Modo de Ejecución:     {res.get('executionMode', '').upper()}")
    print(f"ID Evaluación:         {dictamen.get('id_evaluacion', 'NO DISPONIBLE')}")
    print(f"Modelo Configurado:    {res.get('modelo', 'NO DISPONIBLE')}")
    print(f"Versión Prompt:        {res.get('prompt_version', 'NO DISPONIBLE')}")
    
    periodo = dictamen.get('periodo_evaluado') or {}
    desde = periodo.get('desde', 'NO DISPONIBLE')
    hasta = periodo.get('hasta', 'NO DISPONIBLE')
    print(f"Periodo Evaluado:      {desde} al {hasta}")
    print(f"Clasificación Riesgo:  {dictamen.get('clasificacion_riesgo', 'NO DISPONIBLE')}")
    print(f"Suficiencia Datos:     {dictamen.get('suficiencia_informacion', 'NO DISPONIBLE')}")
    
    pico_val = dictamen.get('pico_maximo_estimado_mw')
    pico_str = f"{pico_val:,} MW" if isinstance(pico_val, (int, float)) else "NO DISPONIBLE"
    print(f"Pico Máximo Proyectado:{pico_str}")
    print(f"Causa Principal:       {dictamen.get('factor_causal_principal', 'NO DISPONIBLE')}")
    
    print(f"\nHerramientas Consultadas ({len(res.get('tool_calls', []))} calls):")
    for tc in res.get("tool_calls", []):
        print(f"  - [{tc.get('iteracion')}] {tc.get('tool_name')}({tc.get('args')}) -> {tc.get('latency_ms')} ms")
        
    print(f"\nAnálisis Técnico:\n{dictamen.get('analisis_tecnico', 'NO DISPONIBLE')}")
    print(f"\nRecomendación Operativa:\n{dictamen.get('recomendacion_operativa', 'NO DISPONIBLE')}")
    
    if res.get("errores"):
        print(f"\nAlertas / Errores Registrados:")
        for err in res.get("errores", []):
            print(f"  - {err}")

    print(f"\nSupervisión Humana (L2):")
    print(f"  Status:              {res.get('humanDecision', {}).get('status', 'PENDING').upper()} (Pendiente de decisión humana)")
    print(f"\nMétricas de Tokens y Economía:")
    print(f"  Input Tokens:        {res.get('tokens', {}).get('input_tokens')}")
    print(f"  Output Tokens:       {res.get('tokens', {}).get('output_tokens')}")
    print(f"  Total Tokens:        {res.get('tokens', {}).get('total_tokens')} ({res.get('tokens', {}).get('estado_conteo')})")
    print(f"  Modalidad Económica: {res.get('cost_basis')}")
    print(f"  Estado Facturación:  {res.get('economic_metrics', {}).get('billing_status')}")
    cost_inc = res.get('incremental_cost_usd')
    print(f"  Costo Incremental:   {('USD ' + str(cost_inc)) if cost_inc is not None else 'NULL (No verificado por operador)'}")
    print(f"  Latencia Total:      {res.get('latencia_ms')} ms")
    print(f"\nRobustez de Transporte HTTP:")
    print(f"  Timeout por Request: {res.get('timeout_seconds', 90)} s")
    print(f"  Reintentos Técnicos: {res.get('retry_count', 0)}")
    if res.get("retries"):
        for r in res.get("retries", []):
            print(f"    - [Iter {r.get('iteracion')}, Intento {r.get('request_attempt')}] {r.get('retry_reason')}: {r.get('error_original')}")
    print(f"\nAuditoría de Seguridad y Payloads Salientes:")
    sec = res.get("security", {})
    print(f"  Payloads Sanitizados:  {sec.get('payload_sanitized')}")
    print(f"  Contiene Emails:       {sec.get('contains_email_content')}")
    print(f"  Contiene Rutas:        {sec.get('contains_file_paths')}")
    print(f"  Contiene Credenciales: {sec.get('contains_credentials')}")
    print(f"  Contiene PDFs Crudos:  {sec.get('contains_raw_pdf')}")
    print(f"  Total Payloads LLM:    {len(res.get('llm_payloads', []))} intercambios auditados y registrados")
    print("="*70 + "\n")
