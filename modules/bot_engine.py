import google.generativeai as genai
import re
import os

# Configuración de API Key (Se espera que esté en st.secrets o variable de entorno)
# Para desarrollo local, intentamos leer de variable de entorno
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def check_guardrails(message, guardrails_list):
    """
    Verifica si el mensaje contiene palabras prohibidas.
    Retorna (blocked: bool, reason: str).
    """
    msg_lower = message.lower()
    for word in guardrails_list:
        if word.lower() in msg_lower:
            return True, f"🛡️ Bloqueo de Seguridad: Se detectó contenido prohibido ('{word}')."
    return False, None

def check_hitl_risk(message, limit):
    """
    Verifica si el mensaje contiene montos que superan el límite.
    Retorna (escalated: bool, reason: str).
    """
    # Regex simple para encontrar números (enteros o decimales)
    # Busca patrones como 1000, 150.50, $2000
    numbers = re.findall(r'\d+(?:[.,]\d+)?', message)
    
    for num_str in numbers:
        try:
            # Limpiar caracteres no numéricos comunes
            clean_num = num_str.replace(',', '')
            val = float(clean_num)
            if val > limit:
                return True, f"⚠️ Riesgo Financiero: Monto detectado ({val}) excede el límite de aprobación ({limit}). Transacción pausada para revisión humana."
        except ValueError:
            continue
            
    return False, None

def generate_response(message, system_prompt):
    """
    Invoca a Gemini para generar la respuesta.
    """
    if not GOOGLE_API_KEY:
        return "Error de Configuración: API Key de Google no encontrada."
        
    try:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_prompt
        )
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        return f"Error del Modelo: {str(e)}"

def process_message(message, config):
    """
    Pipeline principal del Chatbot.
    config: Diccionario con 'guardrails', 'hitl_limit', 'prompt'.
    """
    # 1. Capa de Guardrails
    blocked, reason = check_guardrails(message, config.get('guardrails', []))
    if blocked:
        return reason
        
    # 2. Capa HITL
    escalated, reason = check_hitl_risk(message, config.get('hitl_limit', 999999))
    if escalated:
        return reason
        
    # 3. Capa GenAI
    return generate_response(message, config.get('prompt', 'Eres un asistente útil.'))
