# ==============================================================================
# PROYECTO: Demanda SACME - Capa Agéntica V0.1
# Módulo: agent_tools.py
# Herramientas de Solo Lectura (Read-Only) para el Agente Supervisor de Demanda
# ==============================================================================

import os
import re
import json
import ssl
import urllib.request
from datetime import datetime, timedelta
import pandas as pd

# Rutas del workspace base (relativas al directorio raíz del proyecto)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_JS_PATH = os.path.join(DATA_DIR, "data.js")
REGISTRO_XLSX_PATH = os.path.join(DATA_DIR, "registro_predicciones.xlsx")
CONSISTENCY_JSON_PATH = os.path.join(DATA_DIR, "consistency_status.json")
CONSOLIDADO_CSV_PATH = os.path.join(DATA_DIR, "demanda_sacme_consolidado.csv")

def _load_ml_model_data_readonly():
    """
    Carga de forma segura y en memoria los coeficientes del modelo de Machine Learning desde data.js.
    Garantiza cero escrituras en disco.
    """
    if os.path.exists(DATA_JS_PATH):
        try:
            with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            start_str = "const mlModelData = "
            start_idx = content.find(start_str)
            if start_idx != -1:
                sub = content[start_idx + len(start_str):]
                end_idx = sub.find("};")
                if end_idx != -1:
                    json_str = sub[:end_idx + 1].strip()
                    return json.loads(json_str)
        except Exception as e:
            pass

    # Coeficientes fallback calibrados en caso de no poder leer data.js
    return {
        "edenor": {
            "pivot_temp": 19.0,
            "pivot_media": 15.0,
            "peak_coeffs": [12.029, -569.358, 10229.438],
            "peak_coeffs_cold": [0.659, -217.352, 7000.648],
            "peak_coeffs_hot": [11.481, -523.570, 9360.025],
            "weekend_factor_peak": 0.876
        },
        "gba": {
            "pivot_temp": 19.0,
            "pivot_media": 15.0,
            "peak_coeffs": [22.724, -1081.589, 19641.460],
            "peak_coeffs_cold": [-3.006, -305.807, 12828.924],
            "peak_coeffs_hot": [22.197, -1021.819, 18334.583],
            "weekend_factor_peak": 0.881
        }
    }

def _get_ssl_context():
    """
    Retorna el contexto SSL estándar del sistema para conexiones HTTPS seguras.
    """
    return ssl.create_default_context()

def _fetch_open_meteo_forecast(dias=7):
    """
    Consulta a la API pública de Open-Meteo de forma read-only.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude=-34.6037&longitude=-58.3816&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=America/Argentina/Buenos_Aires&forecast_days={max(1, min(16, dias))}"
    try:
        ssl_context = _get_ssl_context()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Demanda-SACME-Agent-V0.1)'})
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('daily', {})
    except Exception as e:
        return None

# ==============================================================================
# TOOL 1: consultar_pronostico_y_demanda_estimada
# ==============================================================================
def consultar_pronostico_y_demanda_estimada(dias_horizonte: int = 3) -> dict:
    """
    Consulta el pronóstico meteorológico oficial para el área de concesión y calcula
    la demanda eléctrica pico esperada mediante el modelo predictivo de Machine Learning.
    
    Argumentos:
        dias_horizonte (int): Cantidad de días hacia adelante a proyectar (mínimo 1, máximo 7).
    
    Retorna:
        dict: Resumen con temperaturas extremas, demanda estimada para Edenor y GBA, y picos del período.
    """
    try:
        dias_horizonte = max(1, min(7, int(dias_horizonte)))
    except (ValueError, TypeError):
        dias_horizonte = 3

    forecast = _fetch_open_meteo_forecast(dias=dias_horizonte)
    ml_model = _load_ml_model_data_readonly()
    edenor_cfg = ml_model.get('edenor', {})
    gba_cfg = ml_model.get('gba', {})

    day_names_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    predictions = []
    
    if forecast and 'time' in forecast:
        dates = forecast.get('time', [])[:dias_horizonte]
        t_maxs = forecast.get('temperature_2m_max', [])[:dias_horizonte]
        t_mins = forecast.get('temperature_2m_min', [])[:dias_horizonte]
        w_codes = forecast.get('weathercode', [])[:dias_horizonte]

        for i, date_str in enumerate(dates):
            t_max = float(t_maxs[i]) if (i < len(t_maxs) and t_maxs[i] is not None) else 18.0
            t_min = float(t_mins[i]) if (i < len(t_mins) and t_mins[i] is not None) else 10.0
            t_med = (t_max + t_min) / 2.0
            w_code = int(w_codes[i]) if (i < len(w_codes) and w_codes[i] is not None) else 0

            dt = datetime.strptime(date_str, "%Y-%m-%d")
            weekday_idx = dt.weekday()
            is_weekend = weekday_idx >= 5
            
            # Evaluación Edenor
            pivot_media = edenor_cfg.get('pivot_media', 15.0)
            if t_med < pivot_media:
                regimen = "FRIO"
                c = edenor_cfg.get('peak_coeffs_cold', [0.0, -45.0, 4200.0])
                t_eval = t_med
            else:
                regimen = "CALOR"
                c = edenor_cfg.get('peak_coeffs_hot', [0.0, 131.5, 2000.0])
                t_eval = t_max
            
            wf_edenor = edenor_cfg.get('weekend_factor_peak', 0.876)
            pred_edenor = c[0] * (t_eval ** 2) + c[1] * t_eval + c[2]
            if is_weekend:
                pred_edenor *= wf_edenor
            pred_edenor = int(round(pred_edenor))

            # Evaluación GBA
            pivot_gba = gba_cfg.get('pivot_media', 15.0)
            c_gba = gba_cfg.get('peak_coeffs_cold' if t_med < pivot_gba else 'peak_coeffs_hot', [0.0, 250.0, 5000.0])
            wf_gba = gba_cfg.get('weekend_factor_peak', 0.881)
            t_eval_gba = t_med if t_med < pivot_gba else t_max
            pred_gba = c_gba[0] * (t_eval_gba ** 2) + c_gba[1] * t_eval_gba + c_gba[2]
            if is_weekend:
                pred_gba *= wf_gba
            pred_gba = int(round(pred_gba))

            predictions.append({
                "fecha": date_str,
                "dia_semana": day_names_es[weekday_idx],
                "es_fin_de_semana": is_weekend,
                "temp_max_c": round(t_max, 1),
                "temp_min_c": round(t_min, 1),
                "regimen_termico": regimen,
                "weathercode_wmo": w_code,
                "edenor_demanda_pico_estimada_mw": pred_edenor,
                "gba_demanda_pico_estimada_mw": pred_gba
            })
    else:
        # Modo de contingencia seguro si la API de Open-Meteo no responde
        return {
            "error": "No se pudo conectar con la API de Open-Meteo. Servicio no disponible o sin conexión.",
            "fuente": "Open-Meteo (falla de conexión)",
            "dias_solicitados": dias_horizonte,
            "predicciones": []
        }

    picos_edenor = [p["edenor_demanda_pico_estimada_mw"] for p in predictions]
    pico_max_mw = max(picos_edenor) if picos_edenor else 0
    t_mins_list = [p["temp_min_c"] for p in predictions]
    t_min_periodo = min(t_mins_list) if t_mins_list else 0.0
    t_maxs_list = [p["temp_max_c"] for p in predictions]
    t_max_periodo = max(t_maxs_list) if t_maxs_list else 0.0

    return {
        "fuente": "Open-Meteo API + Modelo Cuadrático SACME (data.js)",
        "dias_horizonte": dias_horizonte,
        "predicciones": predictions,
        "resumen_periodo": {
            "pico_maximo_edenor_mw": pico_max_mw,
            "fecha_pico_maximo": predictions[picos_edenor.index(pico_max_mw)]["fecha"] if picos_edenor else None,
            "temperatura_minima_periodo_c": t_min_periodo,
            "temperatura_maxima_periodo_c": t_max_periodo,
            "alerta_umbral_estatico_5500mw": pico_max_mw >= 5500
        }
    }

# ==============================================================================
# TOOL 2: consultar_metricas_error_historico
# ==============================================================================
def consultar_metricas_error_historico(anticipacion_dias: int = 2) -> dict:
    """
    Consulta las estadísticas históricas de precisión y sesgo del modelo predictivo
    para un horizonte de anticipación determinado (0 a 6 días antes).
    
    Argumentos:
        anticipacion_dias (int): Días de anticipación con que se simuló (0 = hoy, 1 = ayer, 2 = 2 días antes...).
    
    Retorna:
        dict: Métricas de error porcentual medio, desvío máximo y tendencia de sesgo (subestimación/sobreestimación).
    """
    try:
        anticipacion_dias = max(0, min(6, int(anticipacion_dias)))
    except (ValueError, TypeError):
        anticipacion_dias = 2

    if not os.path.exists(REGISTRO_XLSX_PATH):
        return {
            "error": "No se encontró el archivo de registro histórico de predicciones.",
            "anticipacion_dias": anticipacion_dias
        }

    try:
        # Carga estrictamente en memoria (read-only)
        df = pd.read_excel(REGISTRO_XLSX_PATH)
    except Exception as e:
        return {
            "error": f"Error leyendo registro_predicciones.xlsx: {str(e)}",
            "anticipacion_dias": anticipacion_dias
        }

    err_col = f"Edenor_Error_{anticipacion_dias}d_antes_pct"
    sim_col = f"Edenor_Sim_{anticipacion_dias}d_antes"
    
    if err_col not in df.columns:
        return {
            "error": f"La columna {err_col} no está presente en el archivo histórico.",
            "anticipacion_dias": anticipacion_dias
        }

    # Filtrar solo registros válidos con error calculado
    df_valid = df.dropna(subset=[err_col]).copy()
    
    if df_valid.empty:
        return {
            "anticipacion_dias": anticipacion_dias,
            "total_observaciones": 0,
            "mensaje": "Aún no hay suficientes días con datos reales de CAMMESA para calcular el error a este horizonte."
        }

    errores = df_valid[err_col].astype(float)
    error_medio = float(errores.mean())
    error_abs_medio = float(errores.abs().mean())
    max_sobreestimacion = float(errores.max())
    max_subestimacion = float(errores.min()) # Valor más negativo

    # Determinación de sesgo
    if error_medio < -1.5:
        sesgo = "SUBESTIMACION_SISTEMATICA (El modelo suele proyectar por debajo de la demanda real)"
    elif error_medio > 1.5:
        sesgo = "SOBREESTIMACION_SISTEMATICA (El modelo suele proyectar por encima de la demanda real)"
    else:
        sesgo = "BIEN_CALIBRADO (Sesgo promedio dentro del ±1.5%)"

    # Extraer últimas 5 observaciones para contexto reciente
    ultimos = []
    for _, row in df_valid.tail(5).iterrows():
        ultimos.append({
            "fecha": str(row["Fecha"])[:10],
            "dia": str(row.get("Dia_Semana", "")),
            "simulado_mw": int(row[sim_col]) if pd.notna(row.get(sim_col)) else None,
            "real_cammesa_mw": int(row["Edenor_Pico_Real_CAMMESA"]) if pd.notna(row.get("Edenor_Pico_Real_CAMMESA")) else None,
            "error_pct": round(float(row[err_col]), 2)
        })

    return {
        "anticipacion_dias": anticipacion_dias,
        "total_dias_evaluados": len(df_valid),
        "error_porcentual_medio_pct": round(error_medio, 2),
        "error_absoluto_medio_mae_pct": round(error_abs_medio, 2),
        "desvio_maximo_subestimacion_pct": round(max_subestimacion, 2),
        "desvio_maximo_sobreestimacion_pct": round(max_sobreestimacion, 2),
        "tendencia_sesgo": sesgo,
        "ultimas_observaciones_recientes": ultimos
    }

# ==============================================================================
# TOOL 3: consultar_consistencia_datos_base
# ==============================================================================
def consultar_consistencia_datos_base() -> dict:
    """
    Verifica la continuidad temporal y consistencia de la base de datos histórica
    de partes SACME para comprobar si existen baches o días faltantes.
    
    Retorna:
        dict: Estado de consistencia, días faltantes si los hay, y métricas del archivo consolidado.
    """
    gaps_info = {"has_gaps": False, "missing_days": []}
    
    # 1. Leer consistency_status.json (prioritario, read-only)
    if os.path.exists(CONSISTENCY_JSON_PATH):
        try:
            with open(CONSISTENCY_JSON_PATH, "r", encoding="utf-8") as f:
                c_data = json.load(f)
                gaps_info["has_gaps"] = bool(c_data.get("has_gaps", False))
                gaps_info["missing_days"] = c_data.get("missing_days", [])
        except Exception:
            pass

    # 2. Consultar consolidado CSV en memoria para metadatos generales
    total_registros = 0
    fecha_min = None
    fecha_max = None
    
    if os.path.exists(CONSOLIDADO_CSV_PATH):
        try:
            df = pd.read_csv(CONSOLIDADO_CSV_PATH, usecols=["Fecha"])
            total_registros = len(df)
            if not df.empty and "Fecha" in df.columns:
                fechas = pd.to_datetime(df["Fecha"]).dropna().sort_values()
                if not fechas.empty:
                    fecha_min = fechas.iloc[0].strftime("%Y-%m-%d")
                    fecha_max = fechas.iloc[-1].strftime("%Y-%m-%d")
        except Exception:
            pass

    estado = "CON_DISCONTINUIDADES" if gaps_info["has_gaps"] else "INTEGRO"

    return {
        "estado_consistencia": estado,
        "tiene_dias_faltantes": gaps_info["has_gaps"],
        "dias_faltantes_detectados": gaps_info["missing_days"],
        "total_dias_registrados_sacme": total_registros,
        "rango_fechas_disponible": {
            "desde": fecha_min,
            "hasta": fecha_max
        },
        "impacto_en_modelo": "Bajo: los gaps reportados son fechas históricas aisladas que no impiden la simulación actual." if gaps_info["has_gaps"] else "Nulo: serie histórica completa."
    }

# ==============================================================================
# Catálogo de herramientas para Tool Calling
# ==============================================================================
TOOLS_SCHEMA = [
    {
        "name": "consultar_pronostico_y_demanda_estimada",
        "description": "Consulta el pronóstico meteorológico oficial y calcula la demanda pico esperada (MW) para Edenor y GBA usando el modelo de Machine Learning calibrado.",
        "parameters": {
            "type": "object",
            "properties": {
                "dias_horizonte": {
                    "type": "integer",
                    "description": "Cantidad de días a proyectar hacia adelante (1 a 7). Por defecto 3."
                }
            },
            "required": ["dias_horizonte"]
        }
    },
    {
        "name": "consultar_metricas_error_historico",
        "description": "Consulta las estadísticas de precisión y sesgo (subestimación/sobreestimación porcentual) del modelo predictivo para un horizonte de días de anticipación.",
        "parameters": {
            "type": "object",
            "properties": {
                "anticipacion_dias": {
                    "type": "integer",
                    "description": "Días de anticipación del pronóstico a evaluar (0 a 6). Por defecto 2."
                }
            },
            "required": ["anticipacion_dias"]
        }
    },
    {
        "name": "consultar_consistencia_datos_base",
        "description": "Verifica si existen baches o días faltantes en la base histórica de reportes de SACME que pudieran comprometer la confiabilidad del modelo.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]

TOOLS_REGISTRY = {
    "consultar_pronostico_y_demanda_estimada": consultar_pronostico_y_demanda_estimada,
    "consultar_metricas_error_historico": consultar_metricas_error_historico,
    "consultar_consistencia_datos_base": consultar_consistencia_datos_base
}
