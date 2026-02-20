import streamlit as st
import pandas as pd
import io

# --- SEGURANÇA COMERCIAL ---
CHAVE_ACESSO = "PRO2026" # Mudei para facilitar para você

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.set_page_config(page_title="Ativação de Licença", page_icon="🔐")
    st.markdown("<h2 style='text-align: center;'>🔐 Ativação de Software</h2>", unsafe_allow_html=True)
    senha = st.text_input("Insira sua Chave de Licença para acessar:", type="password")
    if st.button("Ativar Sistema"):
        if senha == CHAVE_ACESSO:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Chave inválida. Entre em contato com o suporte.")
    st.stop()

# --- CONFIGURAÇÃO DO APP ---
st.set_page_config(page_title="PRO-SUPPLY | Smart Analytics", page_icon="⚡", layout="wide")

# Estilo Futurista CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #0d47a1 0%, #1976d2 100%);
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicialização de Estados
if 'dados_industrias' not in st.session_state: st.session_state.dados_industrias = {}
if 'itens_para_cotar' not in st.session_state: st.session_state.itens_para_cotar = []
if 'historico_cotacoes' not in st.session_state: st.session_state.historico_cotacoes = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Tipo', 'Obs'])

# Título Principal
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>SISTEMA INTELIGENTE DE COTAÇÕES</h1>", unsafe_allow_html=True)

# Abas
aba_c, aba_f, aba_r = st.tabs(["🎯 Seleção Estratégica", "📩 Painel Fornecedor", "📊 Relatório Final"])

with aba_c:
    st.subheader("Configurar Cotação")
    with st.sidebar:
        arquivo = st.file_uploader("📂 Importar Base Excel", type=['xlsx'])
        if arquivo:
            df_imp = pd.read_excel(arquivo)
            for _, linha in df_imp.iterrows():
                ind = str(linha['Indústria']).strip()
                prod = str(linha['Produto']).strip()
                if ind not in st.session_state.dados_industrias: st.session_state.dados_industrias[ind] = []
                if prod not in st.session_state.dados_industrias[ind]: st.session_state.dados_industrias[ind].append(prod)
            st.success("Base Carregada!")

    if st.session_state.dados_industrias:
        ind_sel = st.selectbox("Escolha a Indústria", sorted(st.session_state.dados_industrias.keys()))
        escolhidos = st.multiselect("Produtos:", st.session_state.dados_industrias[ind_sel])
        if st.button("CONFIRMAR LISTA"):
            st.session_state.itens_para_cotar = escolhidos
            st.toast("Lista atualizada!")

with aba_f:
    if not st.session_state.itens_para_cotar:
        st.warning("Selecione os itens na primeira aba.")
    else:
        with st.form("form_f"):
            f_nome = st.text_input("Fornecedor")
            f_tipo = st.selectbox("Condição", ["NF", "Líquido", "Bonificado"])
            dados_temp = []
            for item in st.session_state.itens_para_cotar:
                c1, c2 = st.columns([1, 2])
                p = c1.number_input(f"Preço {item}", min_value=0.0, format="%.2f", key=f"p_{item}")
                o = c2.text_input(f"Obs {item}", key=f"o_{item}")
                if p > 0: dados_temp.append({'Fornecedor': f_nome, 'Produto': item, 'Preço': p, 'Tipo': f_tipo, 'Obs': o})
            if st.form_submit_button("SALVAR COTAÇÃO"):
                st.session_state.historico_cotacoes = pd.concat([st.session_state.historico_cotacoes, pd.DataFrame(dados_temp)], ignore_index=True)
                st.success("Dados Salvos!")

with aba_r:
    if st.session_state.historico_cotacoes.empty:
        st.info("Aguardando dados.")
    else:
        venc = st.session_state.historico_cotacoes.loc[st.session_state.historico_cotacoes.groupby('Produto')['Preço'].idxmin()]
        
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><b>SKUs</b><br><h2>{len(st.session_state.itens_para_cotar)}</h2></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><b>Empresas</b><br><h2>{venc["Fornecedor"].nunique()}</h2></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><b>Total</b><br><h2>R$ {venc["Preço"].sum():.2f}</h2></div>', unsafe_allow_html=True)

        st.subheader("📦 Separar por Fornecedor")
        forn_sel = st.selectbox("Ver ganhos de:", sorted(venc['Fornecedor'].unique()))
        pedido = venc[venc['Fornecedor'] == forn_sel]
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pedido.to_excel(writer, index=False)
        st.download_button(f"📥 Baixar Pedido: {forn_sel}", output.getvalue(), f"pedido_{forn_sel}.xlsx")
        st.table(venc)