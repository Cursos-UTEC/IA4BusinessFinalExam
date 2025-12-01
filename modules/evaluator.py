import json

def validate_json_structure(data):
    """
    Valida que el JSON tenga las claves requeridas.
    Retorna (bool, list_of_errors).
    """
    required_keys = ["prompt", "guardrails", "hitl_limit"]
    errors = []
    
    if not isinstance(data, dict):
        return False, ["El archivo no contiene un objeto JSON válido."]
        
    for key in required_keys:
        if key not in data:
            errors.append(f"Falta la clave obligatoria: '{key}'")
            
    # Validaciones de tipo
    if "guardrails" in data and not isinstance(data["guardrails"], list):
        errors.append("'guardrails' debe ser una lista de textos.")
        
    if "hitl_limit" in data and not isinstance(data["hitl_limit"], int):
        errors.append("'hitl_limit' debe ser un número entero.")
        
    if "prompt" in data and not isinstance(data["prompt"], str):
        errors.append("'prompt' debe ser un texto.")

    return len(errors) == 0, errors

def evaluate_submission(json_content):
    """
    Ejecuta la rúbrica automática sobre el contenido del JSON.
    Retorna un diccionario con el score y feedback.
    """
    try:
        data = json.loads(json_content)
    except json.JSONDecodeError:
        return {
            "valid": False,
            "score": 0,
            "feedback": ["Error de Sintaxis: El archivo no es un JSON válido."]
        }

    valid_structure, structure_errors = validate_json_structure(data)
    if not valid_structure:
        return {
            "valid": False,
            "score": 0,
            "feedback": structure_errors
        }

    # Rúbrica de Evaluación (Total 14 puntos según RF-03)
    score = 0
    feedback = []
    
    # 1. Test de Seguridad (Guardrails) - 5 Puntos
    # Se espera que el alumno identifique palabras clave de riesgo
    expected_keywords = ["estafa", "robo", "fraude", "clave", "contraseña"]
    found_keywords = [kw for kw in expected_keywords if any(kw in g.lower() for g in data["guardrails"])]
    
    if len(found_keywords) >= 3:
        score += 5
        feedback.append("✅ Seguridad: Guardrails robustos detectados.")
    elif len(found_keywords) > 0:
        score += 2
        feedback.append(f"⚠️ Seguridad: Faltan palabras clave importantes. Encontradas: {found_keywords}")
    else:
        feedback.append("❌ Seguridad: No se detectaron guardrails de seguridad básicos (estafa, robo, etc).")

    # 2. Test de Riesgo (HITL Limit) - 5 Puntos
    # Rango aceptable simulado: 1000 - 2000
    limit = data["hitl_limit"]
    if 1000 <= limit <= 2000:
        score += 5
        feedback.append("✅ Riesgo: Límite HITL dentro del rango operativo correcto.")
    else:
        feedback.append(f"❌ Riesgo: Límite HITL ({limit}) fuera de rango (Esperado: 1000-2000).")

    # 3. Test de Prompting - 4 Puntos
    prompt_len = len(data["prompt"].split())
    if prompt_len > 50:
        score += 4
        feedback.append("✅ Prompting: System Prompt detallado y bien estructurado.")
    elif prompt_len > 20:
        score += 2
        feedback.append("⚠️ Prompting: System Prompt un poco corto, podría ser más específico.")
    else:
        feedback.append("❌ Prompting: System Prompt demasiado breve.")

    return {
        "valid": True,
        "data": data, # Retornamos los datos parseados para usarlos en el bot
        "score": score,
        "max_score": 14,
        "feedback": feedback
    }
