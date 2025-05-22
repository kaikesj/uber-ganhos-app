# AVISO: Este script usa Streamlit e Firebase, que devem estar instalados.
# Para rodar localmente, use: pip install streamlit firebase-admin

try:
    import streamlit as st
except ModuleNotFoundError:
    raise ImportError("Streamlit não está instalado. Use 'pip install streamlit'.")

from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa o Firebase diretamente a partir do arquivo credenciais.json
if not firebase_admin._apps:
    cred = credentials.Certificate("credenciais.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Determina se é administrador manualmente (mude para True se necessário)
is_admin = True  # Altere para False para modo visitante

st.markdown("""
    <h1 style='text-align: center;'>Ganhos Algarve</h1>
""", unsafe_allow_html=True)

# Obtem valor total atual
ganhos_ref = db.collection("ganhos")
ganhos = ganhos_ref.stream()
total = sum([g.to_dict()["valor"] for g in ganhos])

st.markdown(f"""
    <h2 style='text-align: center; font-size: 60px; margin-bottom: 30px;'>
        {total:.0f}
    </h2>
""", unsafe_allow_html=True)

if is_admin:
    st.markdown("""
        <style>
        div[data-testid="column"] button {
            width: 100%;
            height: 70px;
            font-size: 24px;
        }
        </style>
    """, unsafe_allow_html=True)

    if "valor_str" not in st.session_state:
        st.session_state.valor_str = ""

    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("1"): st.session_state.valor_str += "1"
        if st.button("4"): st.session_state.valor_str += "4"
        if st.button("7"): st.session_state.valor_str += "7"
    with col2:
        if st.button("2"): st.session_state.valor_str += "2"
        if st.button("5"): st.session_state.valor_str += "5"
        if st.button("8"): st.session_state.valor_str += "8"
    with col3:
        if st.button("3"): st.session_state.valor_str += "3"
        if st.button("6"): st.session_state.valor_str += "6"
        if st.button("9"): st.session_state.valor_str += "9"

    col0, col_clear, col_sum = st.columns([1, 1, 1])
    with col0:
        if st.button("0"): st.session_state.valor_str += "0"
    with col_clear:
        if st.button("C"): st.session_state.valor_str = ""
    with col_sum:
        if st.button("Somar"):
            try:
                valor_float = float(st.session_state.valor_str)
                db.collection("ganhos").add({
                    "valor": valor_float,
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
                st.success("Valor adicionado com sucesso!")
                st.session_state.valor_str = ""
                st.experimental_rerun()
            except ValueError:
                st.error("Valor inválido")

    st.markdown(f"<p style='text-align: center; font-size: 28px;'>{st.session_state.valor_str}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("""
        <p style='text-align: center; font-size: 16px; margin-top: 20px;'>
            Essa visualização é somente leitura para visitantes.
        </p>
    """, unsafe_allow_html=True)
