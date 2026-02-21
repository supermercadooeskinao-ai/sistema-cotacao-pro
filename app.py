import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="PRO-SUPPLY Cloud", layout="wide")
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

# URL da sua planilha publicada como CSV (Substitua pelo link que você copiou no passo 1)
# O link deve terminar em output=csv
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/17NvaU9jN0OoQ961HApv9hPF80xizXTj1oRCW6hn_dbM/pub?output=csv"

@st.cache_data(ttl=10) # Atualiza a cada 10 segundos
def carregar_dados():
    return pd.read_csv(URL_PLANILHA)

try:
    df = carregar_dados()
    
    # Padronização de colunas
    df.columns = [str(c).strip().capitalize() for c in df.columns]
    
    # Filtro de itens
    itens_ativos = []
    if 'Selecionado' in df.columns and 'Produto' in df.columns:
        itens_ativos = df[df['Selecionado'].astype(str).str.lower() == 'x']['Produto'].tolist()

    # Interface
    aba_f, aba_c = st.tabs(["📋 PORTAL DO FORNECEDOR", "📊 ÁREA DO CLIENTE"])

    with aba_f:
        st.subheader("📋 Enviar Cotação")
        if not itens_ativos:
            st.info("💡 Nenhum item com 'x' na coluna 'Selecionado'.")
        else:
            with st.form("meu_form"):
                for item in itens_ativos:
                    st.number_input(f"Preço: {item}", min_value=0.0)
                st.form_submit_button("Enviar")

    with aba_c:
        st.subheader("📊 Visualização")
        st.dataframe(df)

except Exception as e:
    st.error(f"Erro ao ler planilha: {e}")
    st.info("Certifique-se de que a planilha está 'Publicada na Web' como CSV.")
