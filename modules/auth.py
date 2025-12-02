import pandas as pd
import streamlit as st
import os

USERS_FILE = os.path.join("data", "usuarios.csv")

def load_users():
    """Carga los usuarios desde el CSV."""
    try:
        # Asumiendo que el CSV tiene columnas: email, token, role
        return pd.read_csv(USERS_FILE)
    except FileNotFoundError:
        st.error(f"No se encontró el archivo de usuarios en {USERS_FILE}")
        return pd.DataFrame()

def authenticate(email, token):
    """
    Valida las credenciales del usuario.
    Retorna el objeto usuario (Series) si es válido, None si no.
    """
    df = load_users()
    if df.empty:
        return None
    
    # Normalizar inputs
    email = email.strip().lower()
    token = token.strip()
    
    # Buscar usuario
    user = df[(df['email'] == email) & (df['token'] == token)]
    
    if not user.empty:
        return user.iloc[0]
    return None

def login_form():
    """Muestra el formulario de login y gestiona la sesión."""
    st.title("🔐 AI Product Manager - Login")
    
    with st.form("login_form"):
        email = st.text_input("Correo Institucional")
        token = st.text_input("Token de Acceso", type="password")
        submitted = st.form_submit_button("Ingresar")
        
        if submitted:
            user = authenticate(email, token)
            if user is not None:
                st.session_state['authenticated'] = True
                st.session_state['user_email'] = user['email']
                st.session_state['user_role'] = user['role']
                st.success(f"Bienvenido, {user['email']} ({user['role']})")
                st.rerun()
            else:
                st.error("Credenciales inválidas. Verifica tu correo y token.")

def logout():
    """Cierra la sesión actual."""
    st.session_state['authenticated'] = False
    st.session_state['user_email'] = None
    st.session_state['user_role'] = None
    st.rerun()

def require_auth():
    """
    Decorador o función helper para proteger vistas.
    Si no está autenticado, muestra login y detiene la ejecución.
    """
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
        
    if not st.session_state['authenticated']:
        login_form()
        st.stop() # Detiene el resto de la app hasta que se loguee
        
    return st.session_state['user_role']
