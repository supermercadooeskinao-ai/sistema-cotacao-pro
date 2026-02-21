import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import base64

st.set_page_config(page_title="PRO-SUPPLY ANALYTICS", layout="wide")

def conectar_seguro():
    try:
        # Busca os segredos
        s = st.secrets["connections"]["gsheets"]
        # Decodifica a chave
        pk = base64.b64decode(s["private_key_base64"]).decode("utf-8")
        
        # Monta o dicionário de credenciais SEM duplicar o 'type'
        creds = {
            "type": "service_account",
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        # Conexão limpa
        return st.connection("gsheets", type=GSheetsConnection, **creds)
    except Exception as e:
        st.error(f"Erro na configuração: {e}")
        return None

st.title("🛡️ PRO-SUPPLY SMART ANALYTICS")
conn = conectar_seguro()

if conn:
    try:
        # Tenta ler a aba 'Respostas'
        df = conn.read(worksheet="Respostas")
        st.success("Conectado com sucesso!")
        st.dataframe(df)
    except:
        st.warning("Aba 'Respostas' não encontrada na planilha. Verifique o nome da aba no Google Sheets.")
