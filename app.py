import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import base64

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="PRO-SUPPLY | Portal", layout="wide")

# --- SEGURANÇA (Senha para você, acesso livre para fornecedor via abas) ---
CHAVE_MESTRA = "PRO2026"

# --- FUNÇÃO DE CONEXÃO BLINDADA ---
def conectar():
    try:
        # Pega a chave Base64 dos Secrets e decodifica
        pk_b64 = st.secrets["connections"]["gsheets"]["private_key_base64"]
        pk = base64.b64decode(pk_b64).decode("utf-8")
        
        creds = {
            "type": "service_account",
            "project_id": st.secrets["connections"]["gsheets"]["project_id"],
            "private_key": pk,
            "client_email": st.secrets["connections"]["gsheets"]["client_email"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        return st.connection("gsheets", type=GSheetsConnection, credentials=creds)
    except Exception as e:
        st.error(f"Erro de conexão com a nuvem: {e}")
        return None

# --- INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #00d4ff;'>PRO-SUPPLY SMART SYSTEM</h1>", unsafe_allow_html=True)

aba_fornecedor, aba_gestao = st.tabs(["🚀 PORTAL DO FORNECEDOR", "🛡️ PAINEL DE CONTROLE (ADMIN)"])

# --- ABA 1: ONDE O FORNECEDOR RESPONDE ---
with aba_fornecedor:
    st.subheader("Preenchimento de Cotação")
    
    # Vamos ler os itens que você (Admin) marcou para cotar
    conn = conectar()
    if conn:
        try:
            # Lendo a planilha mestre (Aba 'Produtos')
            df_mestre = conn.read(worksheet="Produtos", ttl=0)
            
            # Filtra apenas o que você marcou com 'x' na coluna 'Cotar'
            itens_liberados = df_mestre[df_mestre['Cotar'].str.lower() == 'x']['Produto'].tolist()
            
            if not itens_liberados:
                st.info("Aguardando liberação de itens pelo administrador.")
            else:
                with st.form("portal_forn"):
                    nome_empresa = st.text_input("Sua Empresa / Fornecedor:")
                    respostas = []
                    
                    st.write("Insira os valores abaixo:")
                    for item in itens_liberados:
                        col1, col2 = st.columns([2, 1])
                        preco = col1.number_input(f"Preço Unitário: {item}", min_value=0.0, format="%.2f", key=f"p_{item}")
                        obs = col2.text_input(f"Obs:", key=f"o_{item}")
                        
                        if preco > 0:
                            respostas.append({
                                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "Fornecedor": nome_empresa,
                                "Produto": item,
                                "Preco": preco,
                                "Observacao": obs
                            })
                    
                    if st.form_submit_button("✅ FINALIZAR E ENVIAR COTAÇÃO"):
                        if not nome_empresa:
                            st.error("Por favor, identifique sua empresa.")
                        elif not respostas:
                            st.warning("Preencha pelo menos um preço.")
                        else:
                            # Salva na aba 'Respostas'
                            try:
                                try:
                                    historico = conn.read(worksheet="Respostas")
                                except:
                                    historico = pd.DataFrame()
                                
                                df_final = pd.concat([historico, pd.DataFrame(respostas)], ignore_index=True)
                                conn.create(worksheet="Respostas", data=df_final)
                                st.balloons()
                                st.success("Cotação enviada com sucesso! Obrigado.")
                            except Exception as e:
                                st.error(f"Erro ao salvar: {e}")
        except:
            st.error("Erro ao ler aba 'Produtos'. Verifique se ela existe no Google Sheets.")

# --- ABA 2: ONDE VOCÊ GERENCIA ---
with aba_gestao:
    senha = st.text_input("Senha Administrativa:", type="password")
    if senha == CHAVE_MESTRA:
        st.success("Acesso Liberado")
        
        conn = conectar()
        if conn:
            # 1. Gerenciar itens para cotar
            st.write("### 1. Selecionar Itens para o Portal")
            try:
                df_prod = conn.read(worksheet="Produtos")
                st.data_editor(df_prod, key="editor_prod", use_container_width=True)
                if st.button("Atualizar Lista no Portal"):
                    conn.create(worksheet="Produtos", data=st.session_state.editor_prod)
                    st.toast("Portal Atualizado!")
            except:
                st.warning("Crie uma aba chamada 'Produtos' com as colunas: Produto, Cotar")

            st.write("---")
            
            # 2. Analisar Resultados
            st.write("### 2. Análise de Preços (Menor Valor)")
            try:
                df_res = conn.read(worksheet="Respostas", ttl=0)
                if not df_res.empty:
                    # Lógica para achar o vencedor
                    venc = df_res.loc[df_res.groupby('Produto')['Preco'].idxmin()]
                    st.dataframe(venc, use_container_width=True)
                else:
                    st.info("Nenhuma resposta recebida ainda.")
            except:
                st.info("Aba 'Respostas' ainda está vazia.")
    elif senha != "":
        st.error("Senha incorreta.")
