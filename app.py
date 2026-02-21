import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="PRO-SUPPLY Cloud", layout="wide")
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

df_prod = pd.DataFrame()
itens_ativos = []

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # ttl=0 força o Streamlit a buscar dados novos da planilha toda vez
    df_prod = conn.read(worksheet="Produtos", ttl=0)
    
    # MOSTRAR COLUNAS PARA DIAGNÓSTICO (Aparecerá no app para você ver)
    st.write("Colunas lidas na planilha:", list(df_prod.columns))
    
    # Padronização agressiva
    df_prod.columns = [str(c).strip().lower() for c in df_prod.columns]
    
    if 'selecionado' in df_prod.columns and 'produto' in df_prod.columns:
        # Filtra linhas onde a coluna selecionado tem 'x' ou 'X'
        df_prod['selecionado'] = df_prod['selecionado'].astype(str).str.strip().str.lower()
        itens_ativos = df_prod[df_prod['selecionado'] == 'x']['produto'].tolist()

except Exception as e:
    if "200" not in str(e):
        st.error(f"Erro: {e}")

aba_f, aba_c = st.tabs(["📋 PORTAL DO FORNECEDOR", "📊 ÁREA DO CLIENTE"])

with aba_f:
    st.subheader("📋 Enviar Cotação")
    if not itens_ativos:
        st.info("💡 Nenhum 'x' detectado. Verifique se escreveu 'x' na coluna B.")
    else:
        with st.form("form_envio"):
            for item in itens_ativos:
                st.number_input(f"Preço para: {item}", min_value=0.0, step=0.01)
            st.form_submit_button("Enviar Cotação")

with aba_c:
    st.subheader("📊 Visualização de Dados")
    st.dataframe(df_prod)

