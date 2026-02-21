import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="PRO-SUPPLY Final", layout="wide")
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

# 1. Tentar ler os dados de qualquer maneira
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Lendo a aba Produtos (ttl=0 evita cache)
    df_prod = conn.read(worksheet="Produtos", ttl=0)
except Exception as e:
    # Se o erro for o tal '200', a gente tenta ler de novo sem especificar aba
    if "200" in str(e):
        try:
            df_prod = conn.read(ttl=0)
        except:
            st.error("Erro ao processar resposta do Google. Verifique os Secrets.")
            st.stop()
    else:
        st.error(f"Erro Real: {e}")
        st.stop()

# 2. Processamento dos Dados
itens_ativos = []
if not df_prod.empty:
    # Padroniza nomes de colunas
    df_prod.columns = [str(c).strip().capitalize() for c in df_prod.columns]
    
    # Verifica se as colunas necessárias existem
    if 'Selecionado' in df_prod.columns and 'Produto' in df_prod.columns:
        # Filtra quem tem 'x' ou 'X'
        df_prod['Selecionado'] = df_prod['Selecionado'].astype(str).str.lower().str.strip()
        itens_ativos = df_prod[df_prod['Selecionado'] == 'x']['Produto'].tolist()

# 3. Interface de Abas
aba_f, aba_c = st.tabs(["📋 PORTAL DO FORNECEDOR", "📊 ÁREA DO CLIENTE"])

with aba_f:
    st.subheader("📋 Enviar Cotação")
    if not itens_ativos:
        st.info("💡 Coloque um 'x' na coluna Selecionado da planilha e aguarde.")
    else:
        with st.form("form_envio"):
            for item in itens_ativos:
                st.number_input(f"Preço para: {item}", min_value=0.0, step=0.01)
            st.form_submit_button("Enviar Cotação")

with aba_c:
    st.subheader("📊 Visualização de Dados")
    if not df_prod.empty:
        st.dataframe(df_prod, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado na aba 'Produtos'.")
