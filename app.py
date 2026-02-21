import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import base64

st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

def conectar():
    try:
        # 1. Decodifica a chave para garantir que não haja erro de PEM file
        s = st.secrets["connections"]["gsheets"]
        pk = base64.b64decode(s["private_key_base64"]).decode("utf-8")
        
        # 2. Cria a conexão usando o método mais simples possível
        # Passamos a private_key decodificada para sobrepor qualquer erro de formato
        return st.connection("gsheets", type=GSheetsConnection, private_key=pk)
    except Exception as e:
        st.error(f"Erro técnico na conexão: {e}")
        return None

st.title("🛡️ PRO-SUPPLY SMART ANALYTICS")

conn = conectar()

if conn:
    try:
        # Tenta ler a aba 'Respostas'
        df = conn.read(worksheet="Respostas", ttl=0)
        st.success("✅ SISTEMA ONLINE!")
        st.write("### Dados da Planilha")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.warning("⚠️ Aba 'Respostas' não encontrada.")
        st.info("Dica: Verifique se você criou a aba com o nome exato 'Respostas' no Google Sheets.")
