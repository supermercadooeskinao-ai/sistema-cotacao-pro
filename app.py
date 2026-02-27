import streamlit as st
import pandas as pd
import time
import urllib.parse
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PRO-SUPPLY | Smart Analytics", layout="wide", page_icon="⚡")

# --- URL DA PLANILHA (Mantenha o seu link CSV aqui) ---
URL_PLANILHA_PRODUTOS = "COLE_AQUI_O_LINK_DA_ABA_PRODUTOS_CSV"
URL_PLANILHA_CONFIG = "COLE_AQUI_O_LINK_DA_ABA_CONFIG_CSV" # Nova aba de trava

# --- FUNÇÃO DE VERIFICAÇÃO DE ASSINATURA ---
def verificar_assinatura():
    try:
        # Tenta ler o status na aba Config
        df_config = pd.read_csv(f"{URL_PLANILHA_CONFIG}&cache={int(time.time())}")
        status = df_config.iloc[0, 0].strip().upper() # Lê a célula A2
        return status
    except:
        return "ATIVO" # Por segurança, se der erro na leitura, ele libera

# --- VALIDAÇÃO DE ACESSO ---
status_cliente = verificar_assinatura()

if status_cliente == "BLOQUEADO":
    st.error("### ⚠️ ACESSO SUSPENSO")
    st.info("Identificamos que sua assinatura expirou ou há uma pendência financeira.")
    st.warning("Para reativar seu acesso e não perder seus dados, entre em contato com o suporte agora.")
    st.link_button("📲 FALAR COM SUPORTE (FINANCEIRO)", "https://wa.me/SEU_TELEFONE_AQUI")
    st.stop() # PARA O CÓDIGO AQUI E NÃO MOSTRA MAIS NADA

# ----------------------------------------------------------------
# DAQUI PARA BAIXO SEGUE O SEU CÓDIGO NORMAL (INTERFACE E ABAS)
# ----------------------------------------------------------------

if 'base_analise' not in st.session_state:
    st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
if 'logado' not in st.session_state:
    st.session_state.logado = False

# ... (Restante do código que já ajustamos antes)

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="COTA FACIL | Smart Analytics", layout="wide", page_icon="⚡")

# --- ESTILIZAÇÃO CUSTOMIZADA (Correção de Contraste) ---
st.markdown("""
    <style>
    /* Fundo geral do app */
    .stApp { background-color: #0e1117; }
    
    /* Estilo dos Cards de Produto */
    .product-card { 
        background-color: #ffffff !important; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 6px solid #58a6ff; 
        margin-bottom: 5px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* COR DO TEXTO DENTRO DO CARD (Forçando ser Visível) */
    .product-name {
        color: #1c1e21 !important; 
        font-size: 18px !important;
        font-weight: bold !important;
        display: block;
        margin-bottom: 5px;
    }

    /* Ajuste de métricas e abas */
    div[data-testid="stMetricValue"] { color: #58a6ff !important; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; }
    .stTabs [aria-selected="true"] { color: white !important; font-weight: bold; }
    
    /* Botões */
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DO USUÁRIO ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"
TELEFONE_DESTINO = "5574988391826" 

# --- 2. FUNÇÕES DE DADOS ---
def carregar_dados_google():
    try:
        url_com_cache = f"{URL_PLANILHA}&cache={int(time.time())}"
        df = pd.read_csv(url_com_cache)
        df.columns = [c.strip().capitalize() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Produto", "Selecionado"])

if 'base_analise' not in st.session_state:
    st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- 3. INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>🛡️ COTA FACIL <span style='color: white;'>SMART</span></h1>", unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["📩 PAINEL DO FORNECEDOR", "🔐 ÁREA DO CLIENTE", "📊 RELATÓRIO FINAL"])

df_google = carregar_dados_google()
itens_ativos = df_google[df_google['Selecionado'].notna()]['Produto'].tolist() if not df_google.empty else []

# --- ABA 1: FORNECEDOR ---
with aba_f:
    if not itens_ativos:
        st.warning("⚠️ Nenhuma cotação ativa. Aguarde a liberação dos itens.")
    else:
        with st.form("form_fornecedor"):
            nome_f = st.text_input("Sua Empresa:", placeholder="Nome Fantasia")
            st.markdown("<br>", unsafe_allow_html=True)
            
            dados_preenchidos = {}
            for item in itens_ativos:
                # O Segredo está aqui: usamos uma div com a classe 'product-name'
                st.markdown(f"""
                    <div class="product-card">
                        <span class="product-name">📦 {item}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                valor = st.number_input(f"Preço para {item}", min_value=0.0, step=0.01, key=f"f_{item}", label_visibility="collapsed")
                if valor > 0: dados_preenchidos[item] = valor
                st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)
            
            if st.form_submit_button("✅ GERAR E ENVIAR COTAÇÃO"):
                if nome_f and dados_preenchidos:
                    msg_wa = f"COTAÇÃO_{nome_f.upper()}\n"
                    for p, v in dados_preenchidos.items():
                        msg_wa += f"{p}: {v}\n"
                    link_final = f"https://wa.me/{TELEFONE_DESTINO}?text={urllib.parse.quote(msg_wa)}"
                    st.link_button("🟢 ABRIR WHATSAPP PARA ENVIAR", link_final, use_container_width=True)

# --- ABA 2: ÁREA DO CLIENTE ---
with aba_c:
    if not st.session_state.logado:
        senha = st.text_input("Chave:", type="password")
        if st.button("Entrar"):
            if senha == "PRO2026":
                st.session_state.logado = True
                st.rerun()
    else:
        st.subheader("📥 Receber Cotações")
        texto_copiado = st.text_area("Cole a mensagem do WhatsApp:", height=200)
        if st.button("📥 ADICIONAR AO RELATÓRIO"):
            if texto_copiado:
                try:
                    linhas = [l for l in texto_copiado.split('\n') if l.strip()]
                    fornecedor = linhas[0].replace("COTAÇÃO_", "").strip()
                    novas = []
                    for l in linhas[1:]:
                        if ":" in l:
                            p, v = l.split(":")
                            novas.append({'Fornecedor': fornecedor.upper(), 'Produto': p.strip(), 'Preço': float(v.strip())})
                    st.session_state.base_analise = pd.concat([st.session_state.base_analise, pd.DataFrame(novas)], ignore_index=True)
                    st.success(f"Fornecedor {fornecedor} salvo!")
                except: st.error("Erro no formato!")

# --- ABA 3: RELATÓRIO FINAL ---
with aba_r:
    if not st.session_state.logado:
        st.error("Faça login na aba anterior.")
    elif st.session_state.base_analise.empty:
        st.info("Sem dados.")
    else:
        df_total = st.session_state.base_analise
        vencedores = df_total.loc[df_total.groupby('Produto')['Preço'].idxmin()]
        
        forn_list = sorted(vencedores['Fornecedor'].unique().tolist())
        selected = st.selectbox("🎯 Ver Pedido do Fornecedor:", forn_list)
        pedido = vencedores[vencedores['Fornecedor'] == selected]
        
        c1, c2 = st.columns(2)
        c1.metric("Total do Pedido", f"R$ {pedido['Preço'].sum():.2f}")
        c2.metric("Total de Itens", len(pedido))
        
        st.dataframe(pedido[['Produto', 'Preço']], use_container_width=True, hide_index=True)
        
        if st.button("🗑️ RESETAR SISTEMA"):
            st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
            st.rerun()


