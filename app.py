import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="PRO-SUPPLY Cloud", layout="wide")
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

df_prod = pd.DataFrame()
itens_ativos = []

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Lendo a aba Produtos e forçando a atualização dos dados (ttl=0)
    df_prod = conn.read(worksheet="Produtos", ttl=0)
    
    # Vamos simplificar a busca pelas colunas para evitar erros
    # Transformamos todos os nomes de colunas em minúsculo e sem espaços
    df_prod.columns = [str(c).strip().lower() for c in df_prod.columns]
    
    # Agora procuramos as colunas 'produto' e 'selecionado' (em minúsculo)
    if 'selecionado' in df_prod.columns and 'produto' in df_prod.columns:
        # Filtra quem tem 'x' ou qualquer coisa escrita na coluna selecionado
        mask = df_prod['selecionado'].notna() & (df_prod['selecionado'].astype(str).str.strip() != "")
        itens_ativos = df_prod[mask]['produto'].tolist()

except Exception as e:
    if "200" not in str(e):
        st.error(f"Erro na Planilha: {e}")

aba_f, aba_c = st.tabs(["📋 PORTAL DO FORNECEDOR", "📊 ÁREA DO CLIENTE"])

with aba_f:
    st.subheader("📋 Enviar Cotação")
    if not itens_ativos:
        st.info("💡 Nenhum item com 'x' detectado. Verifique se a coluna B se chama 'Selecionado'.")
        # Mostra as colunas que o Python está vendo para ajudar a gente a debugar
        if not df_prod.empty:
            st.write("Colunas detectadas:", list(df_prod.columns))
    else:
        with st.form("form_envio"):
            for item in itens_ativos:
                st.number_input(f"Preço para: {item}", min_value=0.0, step=0.01)
            if st.form_submit_button("Enviar Cotação"):
                st.success("Cotação enviada!")

with aba_c:
    st.subheader("📊 Visualização de Dados")
    if not df_prod.empty:
        st.dataframe(df_prod)


