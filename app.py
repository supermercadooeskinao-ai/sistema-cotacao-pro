import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import base64
import json

st.set_page_config(page_title="PRO-SUPPLY", layout="wide")

def carregar_dados():
    try:
        # 1. Recupera as informações simplificadas dos Secrets
        pk_decodificada = base64.b64decode(st.secrets["pk_base64"]).decode("utf-8")
        
        # 2. Monta o dicionário de credenciais exatamente como o Google exige
        creds = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key": pk_decodificada,
            "client_email": st.secrets["client_email"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        
        # 3. Conecta passando as credenciais como um dicionário único
        return st.connection("gsheets", type=GSheetsConnection, credentials=creds)
    except Exception as e:
        st.error(f"Erro na montagem das chaves: {e}")
        return None

st.title("🛡️ PRO-SUPPLY SMART ANALYTICS")

conn = carregar_dados()

if conn:
    try:
        # spreadsheet_id vem direto dos secrets
        sid = st.secrets["spreadsheet_id"]
        
        # Tenta ler a aba 'Respostas'
        df = conn.read(spreadsheet=sid, worksheet="Respostas", ttl=0)
        st.success("✅ SISTEMA ONLINE!")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.warning("⚠️ Aba 'Respostas' não encontrada ou sem acesso.")
        st.info("Certifique-se de que o e-mail da conta de serviço é EDITOR na planilha.")

# Se quiser testar o envio, adicione um botão simples abaixo
if st.button("Teste de Conexão Rápida"):
    st.write("Tentando acessar a nuvem...")
