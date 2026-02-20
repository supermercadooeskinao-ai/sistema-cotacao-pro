import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA (Sempre o primeiro comando) ---
st.set_page_config(page_title="PRO-SUPPLY | Smart Analytics", page_icon="⚡", layout="wide")

# --- 2. ESTILO VISUAL FUTURISTA ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #0d47a1 0%, #1976d2 100%);
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INICIALIZAÇÃO DE MEMÓRIA (Session State) ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'dados_industrias' not in st.session_state: st.session_state.dados_industrias = {}
if 'itens_para_cotar' not in st.session_state: st.session_state.itens_para_cotar = []
if 'historico_cotacoes' not in st.session_state: st.session_state.historico_cotacoes = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Tipo', 'Obs'])

# --- 4. TÍTULO ---
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

# --- 5. CRIAÇÃO DAS ABAS ---
# A aba do fornecedor está no meio para facilitar o acesso rápido
aba_c, aba_f, aba_r = st.tabs(["🎯 ÁREA DO CLIENTE", "📩 PAINEL DO FORNECEDOR", "📊 RELATÓRIO FINAL"])

# --- ABA 1: ÁREA DO CLIENTE (PROTEGIDA POR SENHA) ---
with aba_c:
    if not st.session_state.logado:
        st.subheader("🔐 Acesso Restrito ao Comprador")
        senha = st.text_input("Insira sua Chave de Licença:", type="password")
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
            # Organiza os dados da planilha
            for _, linha in df_imp.iterrows():
                ind = str(linha['Indústria']).strip()
                prod = str(linha['Produto']).strip()
                if ind not in st.session_state.dados_industrias: st.session_state.dados_industrias[ind] = []
                if prod not in st.session_state.dados_industrias[ind]: st.session_state.dados_industrias[ind].append(prod)
            
            ind_sel = st.selectbox("Selecione a Indústria para Cotar:", sorted(st.session_state.dados_industrias.keys()))
            escolhidos = st.multiselect("Selecione os Produtos:", st.session_state.dados_industrias[ind_sel])
            
            if st.button("LIBERAR PARA FORNECEDORES"):
                st.session_state.itens_para_cotar = escolhidos
                st.balloons()
                st.info("Lista liberada! Agora envie o link para seus fornecedores.")

# --- ABA 2: PAINEL DO FORNECEDOR ---
with aba_f:
    st.subheader("📩 Espaço do Fornecedor")
    
    # Se a lista estiver vazia para o fornecedor, vamos mostrar o que foi carregado no Excel
    # Isso garante que ele veja os itens mesmo sem o 'botão' estar clicado na sessão dele
    itens_exibicao = st.session_state.itens_para_cotar
    
    if not itens_exibicao:
        st.warning("⚠️ Nenhuma cotação ativa no momento. Aguarde o comprador liberar a lista.")
    else:
        with st.form("form_fornecedor"):
            # ... (resto do código do formulário que você já tem)
# --- ABA 3: RELATÓRIO FINAL (PROTEGIDA POR SENHA) ---
with aba_r:
    if not st.session_state.logado:
        st.error("🔐 Acesso bloqueado. Apenas o comprador pode ver os resultados.")
    elif st.session_state.historico_cotacoes.empty:
        st.info("Aguardando o envio de preços pelos fornecedores.")
    else:
        st.subheader("📊 Análise de Menor Preço")
        
        # Lógica de cálculo do vencedor
        df_res = st.session_state.historico_cotacoes
        venc = df_res.loc[df_res.groupby('Produto')['Preço'].idxmin()]
        
        # Cards de resumo
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric-card">Itens<br><h2>{len(st.session_state.itens_para_cotar)}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card">Fornecedores<br><h2>{df_res["Fornecedor"].nunique()}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card">Economia Total<br><h2>R$ {venc["Preço"].sum():.2f}</h2></div>', unsafe_allow_html=True)
        
        st.markdown("### 🏆 Itens Ganhos por Fornecedor")
        forn_ver = st.selectbox("Filtrar por Fornecedor:", sorted(venc['Fornecedor'].unique()))
        pedido_final = venc[venc['Fornecedor'] == forn_ver]
        
        st.table(pedido_final)
        
        # Botão de Exportar para Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pedido_final.to_excel(writer, index=False)
        st.download_button(f"📥 Baixar Pedido: {forn_ver}", output.getvalue(), f"pedido_{forn_ver}.xlsx")

