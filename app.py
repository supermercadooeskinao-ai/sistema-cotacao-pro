import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="PRO-SUPPLY Cloud", layout="wide")
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

# Inicializamos as variáveis como vazias para não dar NameError
df_prod = pd.DataFrame()
itens_ativos = []

try:
    # Conexão
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lendo a aba de Produtos
    df_prod = conn.read(worksheet="Produtos")
    
    # Limpeza básica de nomes de colunas (tira espaços e põe 1ª letra maiúscula)
    df_prod.columns = [str(c).strip().capitalize() for c in df_prod.columns]
    
    # Tenta criar a lista de itens ativos
    if 'Selecionado' in df_prod.columns and 'Produto' in df_prod.columns:
        itens_ativos = df_prod[df_prod['Selecionado'].notna()]['Produto'].tolist()
    
except Exception as e:
    # Se der erro 200, a gente ignora porque é um bug visual do Streamlit
    if "200" not in str(e):
        st.error(f"Erro na Planilha: {e}")

# Interface
aba_f, aba_c = st.tabs(["📋 PORTAL DO FORNECEDOR", "📊 ÁREA DO CLIENTE"])

with aba_f:
    st.subheader("📋 Enviar Cotação")
    if not itens_ativos:
        st.info("💡 Nenhum item marcado com 'x' na coluna 'Selecionado' da planilha.")
    else:
        with st.form("form_envio"):
            for item in itens_ativos:
                st.number_input(f"Preço para: {item}", min_value=0.0, step=0.01)
            if st.form_submit_button("Enviar Cotação"):
                st.success("Cotação simulada com sucesso!")

with aba_c:
    st.subheader("📊 Visualização de Dados")
    if not df_prod.empty:
        st.dataframe(df_prod)
    else:
        st.warning("Aguardando carregamento dos dados...")

