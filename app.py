import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import base64
import json

st.set_page_config(page_title="PRO-SUPPLY", layout="wide")

# 1. Função para limpar e montar as credenciais
def carregar_conexao():
    try:
        s = st.secrets["connections"]["gsheets"]
        # Decodifica a chave privada que veio do site Base64
        private_key = base64.b64decode(s["private_key_base64"]).decode("utf-8")
        
        # Monta o dicionário de credenciais padrão do Google
        creds = {
            "type": "service_account",
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": private_key,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        # Conecta usando as credenciais como um dicionário único
        return st.connection("gsheets", type=GSheetsConnection, credentials=creds)
    except Exception as e:
        st.error(f"Erro ao processar chaves: {e}")
        return None

st.title("🛡️ PRO-SUPPLY SMART ANALYTICS")

conn = carregar_conexao()

if conn:
    try:
        # Tenta ler a aba 'Respostas'
        # spreadsheet é o ID que está nos seus secrets
        df = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], worksheet="Respostas")
        st.success("🛰️ SISTEMA ONLINE E CONECTADO!")
        st.dataframe(df)
    except Exception as e:
        st.warning("⚠️ Aba 'Respostas' não encontrada ou planilha sem acesso.")
        st.info("Verifique se o e-mail da conta de serviço é EDITOR na planilha.")
