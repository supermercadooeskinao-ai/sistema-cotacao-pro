import streamlit as st
import pandas as pd
import time
import urllib.parse
import io

# =================================================================
# 1. CONFIGURAÇÕES FIXAS (SUA MATRIZ OFICIAL)
# =================================================================
ID_CLIENTE_ATUAL = "Restaurante A" 
URL_PLANILHA_PRODUTOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"
URL_CONTROLE_MESTRE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSAunSaeCenC0s0AX5aq7DyK8sRlVMDfLQ0TxYLkSZz72uNXf9a-EJ-e4k14Ve6k3Ie4bDqeQte6xhI/pub?output=csv"
TELEFONE_SUPORTE = "5574988391826" 
TELEFONE_DESTINO_COTACAO = "5574988391826" 

# =================================================================
# 2. ESTILO E INTERFACE
# =================================================================
st.set_page_config(page_title="COTA FÁCIL | Compra Inteligente", layout="wide", page_icon="🛒")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    @keyframes pulse {
        0% { box-shadow: 0 0 5px rgba(40, 167, 69, 0.4); border-color: rgba(40, 167, 69, 0.4); }
        50% { box-shadow: 0 0 25px rgba(40, 167, 69, 0.9); border-color: rgba(40, 167, 69, 1); }
        100% { box-shadow: 0 0 5px rgba(40, 167, 69, 0.4); border-color: rgba(40, 167, 69, 0.4); }
    }
    .comercial-banner {
        background: linear-gradient(135deg, #1e1e1e 0%, #121212 100%);
        padding: 25px; border-radius: 15px; border: 3px solid #28a745;
        text-align: center; margin-bottom: 25px; animation: pulse 2s infinite;
    }
    .comercial-title { color: #28a745 !important; font-size: 50px !important; font-weight: 900 !important; margin: 0; text-transform: uppercase; }
    .product-card { 
        background-color: #ffffff !important; padding: 15px; border-radius: 10px; 
        border-left: 8px solid #28a745; margin-bottom: 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .product-name { color: #1c1e21 !important; font-size: 18px !important; font-weight: bold !important; }
    .qty-badge { background-color: #e9ecef; color: #495057; padding: 2px 8px; border-radius: 5px; font-weight: bold; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def verificar_acesso():
    try:
        df_trava = pd.read_csv(f"{URL_CONTROLE_MESTRE}&cache={int(time.time())}")
        status = df_trava.loc[df_trava['Cliente'] == ID_CLIENTE_ATUAL, 'Status'].values[0]
        return status.strip().upper()
    except: return "BLOQUEADO"

def carregar_produtos():
    try:
        url = f"{URL_PLANILHA_PRODUTOS}&cache={int(time.time())}"
        df = pd.read_csv(url)
        df.columns = [c.strip().capitalize() for c in df.columns]
        # Garante que a coluna Quantidade exista
        if 'Quantidade' not in df.columns: df['Quantidade'] = 1
        return df
    except: return pd.DataFrame(columns=["Produto", "Selecionado", "Quantidade"])

# --- TRAVA ---
if verificar_acesso() == "BLOQUEADO":
    st.error("⚠️ ACESSO SUSPENSO. Entre em contato com o suporte.")
    st.link_button("📲 SUPORTE", f"https://wa.me/{TELEFONE_SUPORTE}")
    st.stop()

# --- SESSÃO ---
if 'base_analise' not in st.session_state:
    st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Quantidade'])
if 'logado' not in st.session_state:
    st.session_state.logado = False

# Banner
st.markdown('<div class="comercial-banner"><h1 class="comercial-title">🛒 COTA FÁCIL</h1><p style="color:white; margin:0;">Sua Compra Inteligente</p></div>', unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["💰 FORNECEDOR", "🔐 ÁREA DO CLIENTE", "📊 ECONOMÔMETRO"])

df_google = carregar_produtos()
# Filtra apenas o que está marcado como selecionado
df_ativos = df_google[df_google['Selecionado'].notna()]

# --- ABA 1: FORNECEDOR ---
with aba_f:
    if df_ativos.empty:
        st.warning("ℹ️ Nenhuma cotação aberta.")
    else:
        with st.form("form_vendas"):
            nome_f = st.text_input("Sua Empresa:", placeholder="Ex: Atacadão")
            dados_preenchidos = []
            for _, row in df_ativos.iterrows():
                item = row['Produto']
                qtd = row['Quantidade']
                st.markdown(f'''<div class="product-card">
                    <span class="product-name">📦 {item}</span>
                    <span class="qty-badge">Pedir: {qtd}</span>
                </div>''', unsafe_allow_html=True)
                valor = st.number_input(f"Preço Unitário {item}", min_value=0.0, step=0.01, key=f"f_{item}", label_visibility="collapsed")
                if valor > 0:
                    dados_preenchidos.append({"p": item, "v": valor, "q": qtd})
            
            if st.form_submit_button("✅ ENVIAR COTAÇÃO", use_container_width=True):
                if nome_f and dados_preenchidos:
                    msg = f"COTAÇÃO_{nome_f.upper()}\n"
                    for d in dados_preenchidos: msg += f"{d['p']}|{d['v']}|{d['q']}\n"
                    link = f"https://wa.me/{TELEFONE_DESTINO_COTACAO}?text={urllib.parse.quote(msg)}"
                    st.link_button("🚀 ENVIAR AGORA", link, use_container_width=True)

# --- ABA 2: CLIENTE ---
with aba_c:
    if not st.session_state.logado:
        senha = st.text_input("Senha:", type="password")
        if st.button("ENTRAR"):
            if senha == "PRO2026": st.session_state.logado = True; st.rerun()
    else:
        texto = st.text_area("Cole a mensagem do WhatsApp aqui:", height=200)
        if st.button("📥 PROCESSAR"):
            try:
                linhas = [l for l in texto.split('\n') if l.strip()]
                forn = linhas[0].replace("COTAÇÃO_", "").strip()
                novas = []
                for l in linhas[1:]:
                    p, v, q = l.split("|")
                    novas.append({'Fornecedor': forn, 'Produto': p, 'Preço': float(v), 'Quantidade': float(q)})
                st.session_state.base_analise = pd.concat([st.session_state.base_analise, pd.DataFrame(novas)], ignore_index=True)
                st.success("Adicionado!")
            except: st.error("Erro no formato.")

# --- ABA 3: RESULTADOS ---
with aba_r:
    if not st.session_state.logado: st.error("Acesso restrito.")
    elif st.session_state.base_analise.empty: st.info("Sem dados.")
    else:
        df = st.session_state.base_analise
        # Calcula o subtotal (Preço * Quantidade)
        df['Total'] = df['Preço'] * df['Quantidade']
        
        # Encontra o fornecedor com menor preço unitário por produto
        vencedores = df.loc[df.groupby('Produto')['Preço'].idxmin()]
        
        forn_list = sorted(vencedores['Fornecedor'].unique().tolist())
        sel_forn = st.selectbox("Fornecedor:", forn_list)
        pedido = vencedores[vencedores['Fornecedor'] == sel_forn]
        
        st.metric("Total do Pedido", f"R$ {pedido['Total'].sum():.2f}")
        st.dataframe(pedido[['Produto', 'Quantidade', 'Preço', 'Total']], use_container_width=True, hide_index=True)
        
        if st.button("🗑️ LIMPAR TUDO"):
            st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Quantidade'])
            st.rerun()

