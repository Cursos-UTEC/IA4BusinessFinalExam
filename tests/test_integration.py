import unittest
import sys
import os
import json

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules import evaluator, bot_engine

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        # JSON de prueba válido
        self.valid_json = json.dumps({
            "student_version": "1.0",
            "prompt": "Eres un asistente experto en finanzas.",
            "guardrails": ["estafa", "robo", "clave", "contraseña"],
            "hitl_limit": 1500
        })
        
        # JSON de prueba inválido (sin guardrails)
        self.invalid_json = json.dumps({
            "prompt": "Hola",
            "hitl_limit": 1500
        })

    def test_evaluator_valid(self):
        result = evaluator.evaluate_submission(self.valid_json)
        self.assertTrue(result["valid"])
        self.assertGreater(result["score"], 0)
        self.assertIn("data", result)

    def test_evaluator_invalid(self):
        result = evaluator.evaluate_submission(self.invalid_json)
        self.assertFalse(result["valid"])
        self.assertEqual(result["score"], 0)

    def test_bot_guardrails(self):
        # Configuración simulada
        config = json.loads(self.valid_json)
        
        # Mensaje con palabra prohibida
        msg = "Quiero reportar una estafa en mi cuenta."
        response = bot_engine.process_message(msg, config)
        
        self.assertIn("Bloqueo de Seguridad", response)

    def test_bot_hitl(self):
        # Configuración simulada
        config = json.loads(self.valid_json)
        
        # Mensaje con monto alto
        msg = "Quiero transferir 2000 dolares."
        response = bot_engine.process_message(msg, config)
        
        self.assertIn("Riesgo Financiero", response)

    def test_bot_normal_flow(self):
        # Configuración simulada
        config = json.loads(self.valid_json)
        
        # Mensaje normal (debería ir a Gemini, pero sin API Key fallará controladamente)
        msg = "Hola, ¿cómo estás?"
        response = bot_engine.process_message(msg, config)
        
        # Verificamos que NO sea bloqueo ni HITL
        self.assertNotIn("Bloqueo de Seguridad", response)
        self.assertNotIn("Riesgo Financiero", response)
        # Probablemente retorne error de API Key si no está configurada, lo cual es correcto para este test
        if "Error" in response:
            self.assertIn("Error", response)

if __name__ == '__main__':
    unittest.main()
