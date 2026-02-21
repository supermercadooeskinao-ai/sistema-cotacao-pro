import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import base64

st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

def obter_conexao():
    try:
        # 1. Recupera a chave base64 e decodifica
        pk_b64 = st.secrets["connections"]["gsheets"]["private_key_base64"]
        pk_limpa = base64.b64decode(pk_b64).decode("utf-8")
        
        # 2. Cria o dicionário de credenciais SEM a chave 'type' para evitar o erro de duplicata
        # Pegamos tudo dos secrets e apenas atualizamos a private_key
        conf = dict(st.secrets["connections"]["gsheets"])
        conf["private_key"] = pk_limpa
        
        # Removemos a chave base64 para não confundir o Google
        if "private_key_base64" in conf: del conf["private_key_base64"]
        
        # 3. Conecta passando apenas os argumentos necessários
        return st.connection("gsheets", type=GSheetsConnection, **conf)
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return None

# --- Interface ---
st.title("🛡️ PRO-SUPPLY SMART ANALYTICS")

# Carregamento da lista (Public CSV para ser rápido)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"
df_itens = pd.read_csv(URL_CSV)

aba1, aba2 = st.tabs(["🚀 PORTAL FORNECEDOR", "📊 ANÁLISE"])

with aba1:
    with st.form("form_cotacao"):
        fornecedor = st.text_input("Sua Empresa")
        # Filtra itens com 'x'
        itens = df_itens[df_itens['Selecionado'].str.lower() == 'x']['Produto'].tolist()
        
        respostas = []
        for i in itens:
            p = st.number_input(f"Preço: {i}", min_value=0.0, step=0.01)
            if p > 0:
                respostas.append({"Data": datetime.now().strftime("%d/%m/%Y"), "Fornecedor": fornecedor, "Produto": i, "Preco": p})
        
        if st.form_submit_button("SINCRONIZAR"):
            conn = obter_conexao()
            if conn and respostas:
                df_new = pd.DataFrame(respostas)
                try:
                    # Tenta ler histórico
                    try:
                        old = conn.read(worksheet="Respostas")
                        df_final = pd.concat([old, df_new], ignore_index=True)
                    except: df_final = df_new
                    
                    conn.create(worksheet="Respostas", data=df_final)
                    st.success("✅ Sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

with aba2:
    conn = obter_conexao()
    if conn:
        try:
            dados = conn.read(worksheet="Respostas")
            st.dataframe(dados, use_container_width=True)
        except:
            st.info("Aba 'Respostas' não encontrada. Ela será criada no primeiro envio.")
