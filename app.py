import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PRO-SUPPLY | Smart System", layout="wide")

# --- FUNÇÃO DE CONEXÃO ---
def obter_conexao():
    try:
        # Aqui o Streamlit já lê a private_key dos secrets automaticamente
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"Erro de Conexão com a Nuvem: {e}")
        return None

# --- INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #00d4ff;'>PRO-SUPPLY SMART SYSTEM</h1>", unsafe_allow_html=True)

aba_fornecedor, aba_gestao = st.tabs(["🚀 PORTAL DO FORNECEDOR", "🛡️ PAINEL DE CONTROLE (ADMIN)"])

# --- ABA 1: PORTAL DO FORNECEDOR ---
with aba_fornecedor:
    st.subheader("📝 Preenchimento de Cotação")
    conn = obter_conexao()
    if conn:
        try:
            # Tenta ler a aba 'Produtos'
            df_mestre = conn.read(worksheet="Produtos", ttl=0)
            
            # Filtra itens para cotar
            itens_liberados = df_mestre[df_mestre['Cotar'].str.lower() == 'x']['Produto'].tolist()
            
            if not itens_liberados:
                st.info("Aguardando lista de produtos ser liberada pelo administrador.")
            else:
                with st.form("portal_forn"):
                    nome_forn = st.text_input("Sua Empresa / Fornecedor:")
                    respostas = []
                    
                    st.write("---")
                    for item in itens_liberados:
                        c1, c2 = st.columns([2, 1])
                        p = c1.number_input(f"Preço Unitário: {item}", min_value=0.0, format="%.2f", key=f"p_{item}")
                        o = c2.text_input(f"Observação:", key=f"o_{item}")
                        if p > 0:
                            respostas.append({
                                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "Fornecedor": nome_forn,
                                "Produto": item,
                                "Preco": p,
                                "Obs": o
                            })
                    
                    if st.form_submit_button("✅ ENVIAR COTAÇÃO"):
                        if not nome_forn:
                            st.error("Identifique a sua empresa.")
                        elif not respostas:
                            st.warning("Insira pelo menos um preço.")
                        else:
                            # Tenta ler o que já existe em 'Respostas'
                            try: 
                                hist = conn.read(worksheet="Respostas", ttl=0)
                            except: 
                                hist = pd.DataFrame()
                            
                            df_final = pd.concat([hist, pd.DataFrame(respostas)], ignore_index=True)
                            conn.create(worksheet="Respostas", data=df_final)
                            st.balloons()
                            st.success("Cotação enviada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao acessar aba 'Produtos': {e}. Verifique se ela existe no Google Sheets.")

# --- ABA 2: GESTÃO (ADMIN) ---
with aba_gestao:
    senha = st.text_input("Senha de Acesso:", type="password")
    if senha == "PRO2026":
        st.subheader("🛡️ Gestão de Compras")
        conn = obter_conexao()
        if conn:
            # 1. Analisar Respostas
            st.write("### 📊 Comparativo de Preços")
            try:
                df_res = conn.read(worksheet="Respostas", ttl=0)
                if not df_res.empty:
                    venc = df_res.loc[df_res.groupby('Produto')['Preco'].idxmin()]
                    st.dataframe(venc, use_container_width=True)
                else:
                    st.info("Nenhuma resposta recebida ainda.")
            except:
                st.info("Aba 'Respostas' sem dados.")
            
            # 2. Gerir Produtos
            st.write("---")
            st.write("### 📦 Lista de Itens (Coloque 'x' para mostrar ao fornecedor)")
            try:
                df_prod = conn.read(worksheet="Produtos", ttl=0)
                edicao = st.data_editor(df_prod, use_container_width=True)
                if st.button("Atualizar Portal"):
                    conn.create(worksheet="Produtos", data=edicao)
                    st.success("Portal atualizado!")
            except:
                st.warning("Certifique-se que a aba 'Produtos' existe com as colunas: Produto, Cotar")
    elif senha != "":
        st.error("Senha incorreta.")
