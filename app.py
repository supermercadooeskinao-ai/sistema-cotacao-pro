import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="PRO-SUPPLY Cloud", layout="wide")
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

df_prod = pd.DataFrame()
itens_ativos = []

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # MUDANÇA: Lemos a planilha sem especificar a aba para ele pegar a primeira disponível
    # ttl=0 força o Google a entregar os dados MAIS RECENTES agora
    df_prod = conn.read(ttl=0)
    
    if not df_prod.empty:
        # Padroniza nomes de colunas (minúsculo e sem espaços)
        df_prod.columns = [str(c).strip().lower() for c in df_prod.columns]
        
        # Procura colunas que CONTENHAM a palavra 'produto' e 'selecionado'
        col_p = [c for c in df_prod.columns if 'produto' in c]
        col_s = [c for c in df_prod.columns if 'selecionado' in c]
        
        if col_p and col_s:
            # Filtra onde a coluna de seleção tem 'x'
            df_prod[col_s[0]] = df_prod[col_s[0]].astype(str).str.strip().str.lower()
            itens_ativos = df_prod[df_prod[col_s[0]] == 'x'][col_p[0]].tolist()
    else:
        st.warning("Aviso: O Google retornou uma planilha sem dados. Verifique se há conteúdo na primeira aba.")

except Exception as e:
    if "200" not in str(e):
        st.error(f"Erro técnico: {e}")

# Interface
aba_f, aba_c = st.tabs(["📋 PORTAL DO FORNECEDOR", "📊 ÁREA DO CLIENTE"])

with aba_f:
    st.subheader("📋 Enviar Cotação")
    if not itens_ativos:
        st.info("💡 Coloque um 'x' na coluna Selecionado da sua planilha e aguarde alguns segundos.")
    else:
        with st.form("form_envio"):
            for item in itens_ativos:
                st.number_input(f"Preço para: {item}", min_value=0.0, step=0.01)
            st.form_submit_button("Enviar Cotação")

with aba_c:
    st.subheader("📊 Visualização de Dados")
    st.write("Dados detectados na planilha:")
    st.dataframe(df_prod)
