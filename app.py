import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PRO-SUPPLY | Smart Analytics", page_icon="⚡", layout="wide")

# --- 2. INICIALIZAÇÃO DE MEMÓRIA (Persistência de Dados) ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'itens_para_cotar' not in st.session_state: st.session_state.itens_para_cotar = []
if 'historico_cotacoes' not in st.session_state: st.session_state.historico_cotacoes = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Tipo', 'Obs'])

# --- 3. ESTILO VISUAL ---
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

# --- 4. CRIAÇÃO DAS ABAS ---
aba_c, aba_f, aba_r = st.tabs(["🎯 ÁREA DO CLIENTE", "📩 PAINEL DO FORNECEDOR", "📊 RELATÓRIO FINAL"])

# --- ABA 1: ÁREA DO CLIENTE (COM SENHA) ---
with aba_c:
    if not st.session_state.logado:
        st.subheader("🔐 Acesso Restrito")
        senha = st.text_input("Insira sua Chave de Licença:", type="password", key="login_cli")
        if st.button("Validar Acesso"):
            if senha == "PRO2026":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Chave inválida!")
    else:
        st.success("Bem-vindo! Configure sua cotação abaixo.")
        arquivo = st.file_uploader("📂 Importar Planilha de Produtos (Excel)", type=['xlsx'])
        if arquivo:
            df_imp = pd.read_excel(arquivo)
            # Simplificando a lógica de seleção para evitar erros de memória
            todos_produtos = df_imp['Produto'].unique().tolist()
            escolhidos = st.multiselect("Selecione os Produtos para Cotação:", todos_produtos)
            if st.button("LIBERAR PARA FORNECEDORES"):
                st.session_state.itens_para_cotar = escolhidos
                st.success("Lista liberada com sucesso!")

# --- ABA 2: PAINEL DO FORNECEDOR (ACESSO LIVRE) ---
with aba_f:
    st.subheader("📩 Espaço do Fornecedor")
    if not st.session_state.itens_para_cotar:
        st.warning("⚠️ Nenhuma cotação ativa. Aguarde o comprador liberar a lista.")
    else:
        with st.form("form_fornecedor"):
            nome_f = st.text_input("Sua Empresa:")
            st.write("Insira os preços abaixo:")
            temp_dados = []
            for item in st.session_state.itens_para_cotar:
                col1, col2 = st.columns([2, 1])
                col1.write(f"**{item}**")
                valor = col2.number_input(f"Preço R$", min_value=0.0, step=0.01, key=f"f_{item}")
                if valor > 0:
                    temp_dados.append({'Fornecedor': nome_f, 'Produto': item, 'Preço': valor})
            
            if st.form_submit_button("ENVIAR PREÇOS"):
                if nome_f:
                    novos_dados = pd.DataFrame(temp_dados)
                    st.session_state.historico_cotacoes = pd.concat([st.session_state.historico_cotacoes, novos_dados], ignore_index=True)
                    st.success("Preços enviados!")
                else:
                    st.error("Identifique sua empresa.")

# --- ABA 3: RELATÓRIO FINAL (COM SENHA) ---
with aba_r:
    if not st.session_state.logado:
        st.error("🔐 Acesso bloqueado. Use a aba 'Área do Cliente' para logar.")
    elif st.session_state.historico_cotacoes.empty:
        st.info("Aguardando preenchimento dos fornecedores.")
    else:
        st.subheader("📊 Comparativo de Menor Preço")
        df = st.session_state.historico_cotacoes
        # Pega o menor preço por produto
        vencedores = df.loc[df.groupby('Produto')['Preço'].idxmin()]
        st.dataframe(vencedores, use_container_width=True)
        
        # Botão de Exportação
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            vencedores.to_excel(writer, index=False)
        st.download_button("📥 Baixar Relatório de Compras", output.getvalue(), "relatorio_cotacao.xlsx")
