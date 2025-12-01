import streamlit as st
from modules import auth, evaluator, bot_engine
import pandas as pd
import json

# Configuración de página
st.set_page_config(
    page_title="AI Product Manager Platform",
    page_icon="🚀",
    layout="wide"
)

# ==========================================
# VISTA ESTUDIANTE
# ==========================================
def student_view(user_email):
    st.title(f"🎓 Panel de Estudiante: {user_email}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1. Carga de Configuración")
        uploaded_file = st.file_uploader("Sube tu archivo solucion_final.json", type="json")
        
        if uploaded_file:
            content = uploaded_file.getvalue().decode("utf-8")
            result = evaluator.evaluate_submission(content)
            
            if result["valid"]:
                st.success(f"✅ JSON Válido. Nota Preliminar: {result['score']}/{result['max_score']}")
                with st.expander("Ver Feedback Detallado"):
                    for item in result["feedback"]:
                        st.write(item)
                
                # Guardar configuración válida en sesión para el chat
                st.session_state['bot_config'] = result["data"]
            else:
                st.error("❌ JSON Inválido")
                st.write(result["feedback"])
                st.session_state['bot_config'] = None

    with col2:
        st.subheader("2. Prueba tu Chatbot")
        
        if st.session_state.get('bot_config'):
            config = st.session_state['bot_config']
            st.info(f"Bot activo: {config.get('prompt')[:50]}...")
            
            # Chat Interface
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Escribe un mensaje de prueba..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Procesar mensaje con el motor
                response = bot_engine.process_message(prompt, config)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)
        else:
            st.warning("⚠️ Sube un archivo JSON válido para activar el chat.")

# ==========================================
# VISTA PROFESOR
# ==========================================
def professor_view(user_email):
    st.title(f"👨‍🏫 Panel de Control: {user_email}")
    st.metric(label="Estado del Sistema", value="Operativo", delta="OK")
    
    st.subheader("Monitoreo de Entregas")
    # Aquí se podría implementar una lectura de logs o base de datos de entregas
    st.info("Funcionalidad de Dashboard Global en construcción.")
    
    st.markdown("### Herramientas de Debug")
    if st.button("Limpiar Cache"):
        st.cache_data.clear()
        st.success("Cache limpiada.")

# ==========================================
# MAIN ROUTER
# ==========================================
def main():
    # Sidebar con info de usuario y logout
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
        st.markdown("### AI Product Manager")
        if st.session_state.get('authenticated'):
            st.write(f"Usuario: {st.session_state['user_email']}")
            if st.button("Cerrar Sesión"):
                auth.logout()
    
    # Autenticación
    role = auth.require_auth()
    
    # Router de Vistas
    if role == "Student":
        student_view(st.session_state['user_email'])
    elif role == "Admin" or role == "Profesor":
        professor_view(st.session_state['user_email'])
    else:
        st.error("Rol no reconocido.")

if __name__ == "__main__":
    main()
