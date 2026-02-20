import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="PRO-SUPPLY | Cotação Direta", layout="wide")

# SUBSTISTUA PELO SEU LINK DO GOOGLE PUBLICADO COMO CSV
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/17NvaU9jNOOoQ961HApv9hPF80xizXTjloRCW6hn_dbM/edit?gid=0#gid=0"

def carregar_produtos():
    try:
        # Lê apenas a coluna 'Produto' da planilha
        df = pd.read_csv(URL_PLANILHA)
        return df['Produto'].unique().tolist()
    except:
        return []

# --- 2. ESTADO DO SISTEMA ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'historico' not in st.session_state: 
    st.session_state.historico = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])

st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["📩 PAINEL DO FORNECEDOR", "🔐 CONFIGURAÇÃO (Cliente)", "📊 RELATÓRIO FINAL"])

# --- ABA 1: FORNECEDOR (AGORA É A PRIMEIRA PARA FACILITAR) ---
with aba_f:
    st.subheader("📩 Preencher Cotação")
    lista_produtos = carregar_produtos()
    
    if not lista_produtos:
        st.warning("Aguardando lista de produtos ser atualizada no sistema.")
    else:
        with st.form("form_fornecedor"):
            nome_forn = st.text_input("Sua Empresa / Nome:")
            st.write("Insira seus preços unitários:")
            
            temp_precos = []
            for item in lista_produtos:
                col1, col2 = st.columns([3, 1])
                col1.write(f"📦 **{item}**")
                valor = col2.number_input(f"R$", min_value=0.0, step=0.01, key=f"f_{item}")
                if valor > 0:
                    temp_precos.append({'Fornecedor': nome_forn, 'Produto': item, 'Preço': valor})
            
            if st.form_submit_button("ENVIAR PREÇOS PARA O COMPRADOR"):
                if nome_forn and temp_precos:
                    st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame(temp_precos)], ignore_index=True)
                    st.success("✅ Cotação enviada com sucesso!")
                else:
                    st.error("Preencha seu nome e pelo menos um valor.")

# --- ABA 2: CONFIGURAÇÃO DO CLIENTE ---
with aba_c:
    if not st.session_state.logado:
        senha = st.text_input("Chave de Acesso:", type="password")
        if st.button("Entrar"):
            if senha == "PRO2026":
                st.session_state.logado = True
                st.rerun()
    else:
        st.success("Sincronizado com o Google Sheets")
        st.write("Produtos ativos na cotação atual:")
        st.write(lista_produtos)
        if st.button("Sair do Painel"):
            st.session_state.logado = False
            st.rerun()

# --- ABA 3: RELATÓRIO ---
with aba_r:
    if not st.session_state.logado:
        st.error("Acesso restrito ao comprador.")
    elif st.session_state.historico.empty:
        st.info("Nenhum fornecedor enviou preços ainda.")
    else:
        st.subheader("📊 Resultados da Cotação")
        df_total = st.session_state.historico
        # Pega o menor preço para cada produto
        vencedores = df_total.loc[df_total.groupby('Produto')['Preço'].idxmin()]
        st.dataframe(vencedores, use_container_width=True)
        
        # Exportar
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            vencedores.to_excel(writer, index=False)
        st.download_button("📥 Baixar Pedido Otimizado", output.getvalue(), "pedido_final.xlsx")

