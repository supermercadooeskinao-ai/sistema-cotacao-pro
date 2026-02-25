import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="PRO-SUPPLY SMART SYSTEM", layout="wide")

# Conexão automática usando os secrets
def conectar():
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return None

st.title("🛡️ PRO-SUPPLY SMART SYSTEM")

aba1, aba2 = st.tabs(["🚀 PORTAL FORNECEDOR", "📊 ANÁLISE"])

conn = conectar()

with aba1:
    if conn:
        try:
            # Lê a aba de produtos
            df_prod = conn.read(worksheet="Produtos", ttl=0)
            lista_itens = df_prod[df_prod['Cotar'].str.lower() == 'x']['Produto'].tolist()
            
            if not lista_itens:
                st.info("Aguardando liberação de produtos...")
            else:
                with st.form("form_forn"):
                    fornecedor = st.text_input("Nome da sua Empresa:")
                    dados_envio = []
                    for item in lista_itens:
                        preco = st.number_input(f"Preço Unitário: {item}", min_value=0.0, format="%.2f")
                        if preco > 0:
                            dados_envio.append({"Data": datetime.now().strftime("%d/%m/%Y"), "Fornecedor": fornecedor, "Produto": item, "Preco": preco})
                    
                    if st.form_submit_button("ENVIAR PREÇOS"):
                        if fornecedor and dados_envio:
                            try:
                                try: existente = conn.read(worksheet="Respostas", ttl=0)
                                except: existente = pd.DataFrame()
                                
                                df_novo = pd.concat([existente, pd.DataFrame(dados_envio)], ignore_index=True)
                                conn.create(worksheet="Respostas", data=df_novo)
                                st.balloons()
                                st.success("Cotação enviada!")
                            except Exception as e: st.error(f"Erro ao salvar: {e}")
        except:
            st.error("Crie a aba 'Produtos' no seu Google Sheets.")

with aba2:
    senha = st.text_input("Senha Admin:", type="password")
    if senha == "PRO2026":
        if conn:
            st.subheader("Menores Preços")
            try:
                df_res = conn.read(worksheet="Respostas", ttl=0)
                if not df_res.empty:
                    vencedores = df_res.loc[df_res.groupby('Produto')['Preco'].idxmin()]
                    st.dataframe(vencedores, use_container_width=True)
                else: st.info("Sem respostas ainda.")
            except: st.info("Aba 'Respostas' vazia.")
