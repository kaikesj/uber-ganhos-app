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

st.title("💼 Ganhos Algarve")

# Obtem valor total atual
ganhos_ref = db.collection("ganhos")
ganhos = ganhos_ref.stream()
total = sum([g.to_dict()["valor"] for g in ganhos])

st.header(f"💰 {total:.2f} €")

if is_admin:
    st.markdown("### Inserir novo valor")

    # Interface tipo calculadora
    col1, col2, col3 = st.columns(3)
    with col1:
        n1 = st.button("1")
        n4 = st.button("4")
        n7 = st.button("7")
    with col2:
        n2 = st.button("2")
        n5 = st.button("5")
        n8 = st.button("8")
    with col3:
        n3 = st.button("3")
        n6 = st.button("6")
        n9 = st.button("9")

    valor_manual = st.text_input("Valor a adicionar", "")

    if st.button("➕ Somar valor") and valor_manual.strip():
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
    st.info("Essa visualização é somente leitura para visitantes.")
