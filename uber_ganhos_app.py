# AVISO: Este script usa Streamlit e Firebase, que devem ser instalados no ambiente local ou no Streamlit Cloud.
# Para rodar localmente, use: pip install streamlit firebase-admin

try:
    import streamlit as st
except ModuleNotFoundError:
    raise ImportError("Streamlit não está instalado. Use 'pip install streamlit' e execute localmente.")

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
        raise KeyError("Chave 'firebase_cred' não encontrada nos segredos do Streamlit. Vá em '⋮ > Edit secrets' e adicione sua credencial.")

db = firestore.client()

st.title("📈 Acompanhamento de Ganhos - Uber")

# Entrada de valor
data = st.date_input("Data da corrida", value=datetime.today())
valor = st.number_input("Valor ganho (R$)", min_value=0.0, step=0.5, format="%.2f")

if st.button("Adicionar ganho"):
    doc_ref = db.collection("ganhos").document()
    doc_ref.set({
        "data": data.strftime("%Y-%m-%d"),
        "valor": valor,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
    st.success("Ganho registrado com sucesso!")

st.subheader("📊 Histórico de Ganhos")

# Recupera dados do Firestore
ganhos_ref = db.collection("ganhos").order_by("timestamp", direction=firestore.Query.DESCENDING)
ganhos = ganhos_ref.stream()

total = 0.0

for g in ganhos:
    item = g.to_dict()
    st.write(f"📅 {item['data']} - 💰 R$ {item['valor']:.2f}")
    total += item['valor']

st.markdown("---")
st.metric(label="Total acumulado", value=f"R$ {total:.2f}")
