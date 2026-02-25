import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="PRO-SUPPLY SMART SYSTEM", layout="wide")

# Função simples para conectar
def conectar():
    try:
        # O Streamlit busca automaticamente os dados em [connections.gsheets]
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Erro técnico na conexão: {e}")
        return None

st.markdown("<h1 style='text-align: center;'>PRO-SUPPLY SMART SYSTEM</h1>", unsafe_allow_html=True)

aba_forn, aba_admin = st.tabs(["🚀 PORTAL DO FORNECEDOR", "🛡️ PAINEL DE CONTROLE"])

with aba_forn:
    conn = conectar()
    if conn:
        try:
            # Tenta ler a aba 'Produtos'
            df_mestre = conn.read(worksheet="Produtos", ttl=0)
            itens = df_mestre[df_mestre['Cotar'].str.lower() == 'x']['Produto'].tolist()
            
            if not itens:
                st.info("Aguardando lista de produtos...")
            else:
                with st.form("f_cotacao"):
                    nome = st.text_input("Sua Empresa:")
                    respostas = []
                    for item in itens:
                        p = st.number_input(f"Preço: {item}", min_value=0.0, format="%.2f")
                        if p > 0:
                            respostas.append({"Data": datetime.now().strftime("%d/%m/%Y"), "Fornecedor": nome, "Produto": item, "Preco": p})
                    
                    if st.form_submit_button("ENVIAR"):
                        if nome and respostas:
                            try:
                                try: hist = conn.read(worksheet="Respostas", ttl=0)
                                except: hist = pd.DataFrame()
                                df_final = pd.concat([hist, pd.DataFrame(respostas)], ignore_index=True)
                                conn.create(worksheet="Respostas", data=df_final)
                                st.success("Enviado!")
                            except Exception as e: st.error(f"Erro ao salvar: {e}")
        except:
            st.warning("Certifique-se que a aba 'Produtos' existe no Google Sheets.")

with aba_admin:
    senha = st.text_input("Senha Admin:", type="password")
    if senha == "PRO2026":
        conn = conectar()
        if conn:
            st.write("### Itens para Cotação")
            try:
                df_p = conn.read(worksheet="Produtos", ttl=0)
                novo_df = st.data_editor(df_p)
                if st.button("Salvar Alterações"):
                    conn.create(worksheet="Produtos", data=novo_df)
                    st.success("Lista atualizada!")
            except: st.error("Erro ao carregar aba 'Produtos'")
