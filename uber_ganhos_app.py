# AVISO: Este script usa Streamlit e Firebase, que devem estar instalados.
# Para rodar localmente, use: pip install streamlit firebase-admin

try:
    import streamlit as st
except ModuleNotFoundError:
    raise ImportError("Streamlit não está instalado. Use 'pip install streamlit'.")

from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import json
import tempfile
import os

# Lê a chave do Firebase dos segredos do Streamlit
if not firebase_admin._apps:
    try:
        firebase_json = st.secrets["firebase_cred"]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp.write(firebase_json.encode("utf-8"))
            tmp_path = tmp.name
        cred = credentials.Certificate(tmp_path)
        firebase_admin.initialize_app(cred)
        os.unlink(tmp_path)
    except KeyError:
        raise KeyError("Chave 'firebase_cred' não encontrada nos segredos do Streamlit.")

db = firestore.client()

# Determina se é administrador
is_admin = st.secrets.get("admin", False)

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
        .keypad button {
            width: 80px;
            height: 80px;
            font-size: 24px;
            margin: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

    # Simula botões numéricos
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("1")
        st.button("4")
        st.button("7")
    with col2:
        st.button("2")
        st.button("5")
        st.button("8")
    with col3:
        st.button("3")
        st.button("6")
        st.button("9")

    col_empty, col_plus = st.columns([2, 1])
    with col_plus:
        st.button("+")

    st.markdown("</div>", unsafe_allow_html=True)

    valor_manual = st.text_input("", "", label_visibility="collapsed", placeholder="Digite o valor...")

    if st.button("Somar valor") and valor_manual.strip():
        try:
            valor_float = float(valor_manual.replace(",", "."))
            db.collection("ganhos").add({
                "valor": valor_float,
                "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            st.success("Valor adicionado com sucesso!")
            st.experimental_rerun()
        except ValueError:
            st.error("Digite um valor numérico válido.")
else:
    st.markdown("""
        <p style='text-align: center; font-size: 16px; margin-top: 20px;'>
            Essa visualização é somente leitura para visitantes.
        </p>
    """, unsafe_allow_html=True)
