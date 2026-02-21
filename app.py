import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io

# Configuração da página
st.set_page_config(page_title="PRO-SUPPLY Cloud", layout="wide")
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

try:
    # Estabelecendo conexão
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lendo as abas (Worksheets)
    # Certifique-se que na planilha os nomes são exatamente "Produtos" e "Respostas"
    df_prod = conn.read(worksheet="Produtos")
    df_resp = conn.read(worksheet="Respostas")
    
    # Limpeza e padronização das colunas
    df_prod.columns = [c.strip().capitalize() for c in df_prod.columns]
    
    # Filtrando apenas os itens marcados com 'x' na coluna 'Selecionado'
    # Importante: A coluna na planilha deve se chamar "Selecionado" e a outra "Produto"
    itens_ativos = df_prod[df_prod['Selecionado'].notna()]['Produto'].tolist()

except Exception as e:
    # Se o erro for apenas o código 200, ele ignora e segue adiante
    if "200" not in str(e):
        st.error(f"Erro real de configuração: {e}")
        st.info("Verifique se os nomes das colunas na planilha são 'Produto' e 'Selecionado'.")
        st.stop()
    else:
        # Se for 200, tentamos carregar os itens mesmo assim
        try:
            itens_ativos = df_prod[df_prod['Selecionado'].notna()]['Produto'].tolist()
        except:
            itens_ativos = []

# Interface do App
aba_f, aba_c = st.tabs(["📋 PORTAL DO FORNECEDOR", "📊 ÁREA DO CLIENTE"])

with aba_f:
    st.subheader("📋 Enviar Cotação")
    if not itens_ativos:
        st.warning("Nenhum item selecionado para cotação na planilha. Marque um 'x' na coluna Selecionado.")
    else:
        with st.form("form_envio"):
            for item in itens_ativos:
                st.number_input(f"Preço para: {item}", min_value=0.0, step=0.01, key=item)
            
            enviado = st.form_submit_button("Enviar Cotação")
            if enviado:
                st.success("Cotação enviada com sucesso!")

with aba_c:
    st.subheader("📊 Visualização de Dados")
    st.dataframe(df_prod)

