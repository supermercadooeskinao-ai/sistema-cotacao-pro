# =================================================================
# 4. INTERFACE PRINCIPAL - BANNER COMERCIAL DE ALTO IMPACTO
# =================================================================
if 'base_analise' not in st.session_state:
    st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- CSS PARA O EFEITO DE PULSAÇÃO (GLOW) ---
st.markdown("""
    <style>
    @keyframes pulse {
        0% { box-shadow: 0 0 5px rgba(40, 167, 69, 0.4); }
        50% { box-shadow: 0 0 25px rgba(40, 167, 69, 0.9); }
        100% { box-shadow: 0 0 5px rgba(40, 167, 69, 0.4); }
    }
    .comercial-banner {
        background: linear-gradient(135deg, #1e1e1e 0%, #121212 100%);
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #28a745;
        text-align: center;
        margin-bottom: 20px;
        animation: pulse 2s infinite; /* Efeito de pulsação ativo */
    }
    .comercial-title {
        color: #28a745 !important;
        font-size: 50px !important; /* Texto MUITO maior */
        font-weight: 900 !important;
        margin: 0 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .comercial-subtitle {
        color: white !important;
        font-size: 20px !important;
        font-weight: 300 !important;
        margin: 5px 0 0 0 !important;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# --- RENDERIZAÇÃO DO BANNER COMERCIAL ---
st.markdown("""
    <div class="comercial-banner">
        <h1 class="comercial-title">🛒 COTA FÁCIL</h1>
        <p class="comercial-subtitle">Sua Compra Inteligente</p>
    </div>
""", unsafe_allow_html=True)

# Subtítulo com o nome do cliente (Mantemos este para identificação)
st.markdown(f"<h3 style='text-align:center; color:white; opacity: 0.7;'>Cliente: {ID_CLIENTE_ATUAL.replace('_', ' ')}</h3>", unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["📩 PAINEL DO FORNECEDOR", "🔐 ÁREA DO CLIENTE", "📊 RELATÓRIO FINAL"])

# ----------------------------------------------------------------
# O RESTANTE DO CÓDIGO (LÓGICA DAS ABAS) SEGUE IGUAL...
# ----------------------------------------------------------------



