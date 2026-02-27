import streamlit as st
import pandas as pd
import time
import urllib.parse
import io

# =================================================================
# 1. CONFIGURAÇÕES FIXAS (SUA MATRIZ OFICIAL)
# =================================================================
# Quando vender para um novo cliente, mude APENAS estas duas linhas:
ID_CLIENTE_ATUAL = "Restaurante_A" 
URL_PLANILHA_PRODUTOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

# Seus dados mestres configurados
URL_CONTROLE_MESTRE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSAunSaeCenC0s0AX5aq7DyK8sRlVMDfLQ0TxYLkSZz72uNXf9a-EJ-e4k14Ve6k3Ie4bDqeQte6xhI/pub?output=csv"
TELEFONE_SUPORTE = "5574988391826" 
TELEFONE_DESTINO_COTACAO = "5574988391826" 

# =================================================================
# 2. CONFIGURAÇÃO DA PÁGINA E ESTILO COMERCIAL (CSS)
# =================================================================
st.set_page_config(page_title="COTA FÁCIL | Compra Inteligente", layout="wide", page_icon="🛒")

st.markdown("""
    <style>
    /* Fundo Geral */
    .stApp { background-color: #0e1117; }
    
    /* Efeito de Pulsação no Banner */
    @keyframes pulse {
        0% { box-shadow: 0 0 5px rgba(40, 167, 69, 0.4); border-color: rgba(40, 167, 69, 0.4); }
        50% { box-shadow: 0 0 25px rgba(40, 167, 69, 0.9); border-color: rgba(40, 167, 69, 1); }
        100% { box-shadow: 0 0 5px rgba(40, 167, 69, 0.4); border-color: rgba(40, 167, 69, 0.4); }
    }
    
    .comercial-banner {
        background: linear-gradient(135deg, #1e1e1e 0%, #121212 100%);
        padding: 30px;
        border-radius: 15px;
        border: 3px solid #28a745;
        text-align: center;
        margin-bottom: 25px;
        animation: pulse 2s infinite;
    }
    
    .comercial-title {
        color: #28a745 !important;
        font-size: 55px !important;
        font-weight: 900 !important;
        margin: 0 !important;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    .comercial-subtitle {
        color: white !important;
        font-size: 22px !important;
        font-weight: 300 !important;
        margin: 5px 0 0 0 !important;
        opacity: 0.9;
    }

    /* Estilo dos Cards de Produto */
    .product-card { 
        background-color: #ffffff !important; 
        padding: 18px; border-radius: 12px; 
        border-left: 8px solid #28a745; 
        margin-bottom: 8px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    .product-name {
        color: #1c1e21 !important; font-size: 20px !important;
        font-weight: bold !important; display: block;
    }

    /* Tabs e Botões */
    .stTabs [aria-selected="true"] { color: #28a745 !important; font-weight: bold; font-size: 18px; }
    div[data-testid="stMetricValue"] { color: #28a745 !important; }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 3. FUNÇÕES DE DADOS E SEGURANÇA
# =================================================================
def verificar_acesso():
    try:
        # Força atualização do cache para trava imediata
        df_trava = pd.read_csv(f"{URL_CONTROLE_MESTRE}&cache={int(time.time())}")
        status = df_trava.loc[df_trava['Cliente'] == ID_CLIENTE_ATUAL, 'Status'].values[0]
        return status.strip().upper()
    except:
        return "BLOQUEADO"

def carregar_produtos():
    try:
        url = f"{URL_PLANILHA_PRODUTOS}&cache={int(time.time())}"
        df = pd.read_csv(url)
        df.columns = [c.strip().capitalize() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Produto", "Selecionado"])

# --- EXECUÇÃO DA TRAVA ---
if verificar_acesso() == "BLOQUEADO":
    st.markdown(f"""
        <div style="text-align:center; padding:50px; background:#222; border-radius:20px; border:2px solid red;">
            <h1 style="color:red;">⚠️ ACESSO SUSPENSO</h1>
            <p style="color:white; font-size:20px;">A licença de uso do <b>COTA FÁCIL</b> para {ID_CLIENTE_ATUAL} expirou.</p>
            <p style="color:white;">Regularize sua assinatura para continuar economizando.</p>
        </div>
    """, unsafe_allow_html=True)
    st.link_button("📲 FALAR COM SUPORTE FINANCEIRO", f"https://wa.me/{TELEFONE_SUPORTE}", use_container_width=True)
    st.stop()

# =================================================================
# 4. INTERFACE E LOGICA DO APP
# =================================================================
if 'base_analise' not in st.session_state:
    st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
if 'logado' not in st.session_state:
    st.session_state.logado = False

# Banner Principal
st.markdown("""
    <div class="comercial-banner">
        <h1 class="comercial-title">🛒 COTA FÁCIL</h1>
        <p class="comercial-subtitle">Sua Compra Inteligente</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"<p style='text-align:center; color:gray;'>Painel Exclusivo: {ID_CLIENTE_ATUAL.replace('_', ' ')}</p>", unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["💰 ENVIAR PREÇOS (Fornecedor)", "🔐 ÁREA DO CLIENTE", "📊 ECONOMÔMETRO (Resultado)"])

df_google = carregar_produtos()
itens_ativos = df_google[df_google['Selecionado'].notna()]['Produto'].tolist() if not df_google.empty else []

# --- ABA 1: FORNECEDOR (Onde o dinheiro entra) ---
with aba_f:
    st.info("Fornecedor: Preencha os valores abaixo e clique no botão verde para enviar sua cotação.")
    if not itens_ativos:
        st.warning("ℹ️ No momento não há uma lista de compras ativa.")
    else:
        with st.form("form_vendas"):
            nome_f = st.text_input("Nome da sua Empresa:", placeholder="Ex: Atacadão Central")
            st.markdown("---")
            dados_preenchidos = {}
            for item in itens_ativos:
                st.markdown(f'<div class="product-card"><span class="product-name">📦 {item}</span></div>', unsafe_allow_html=True)
                valor = st.number_input(f"Preço {item}", min_value=0.0, step=0.01, key=f"f_{item}", label_visibility="collapsed")
                if valor > 0: dados_preenchidos[item] = valor
            
            if st.form_submit_button("✅ FINALIZAR E ENVIAR PELO WHATSAPP", use_container_width=True):
                if nome_f and dados_preenchidos:
                    msg = f"COTAÇÃO_{nome_f.upper()}\n"
                    for p, v in dados_preenchidos.items(): msg += f"{p}: {v}\n"
                    link = f"https://wa.me/{TELEFONE_DESTINO_COTACAO}?text={urllib.parse.quote(msg)}"
                    st.link_button("🚀 ENVIAR AGORA", link, use_container_width=True)
                else:
                    st.error("Por favor, informe o nome da empresa e pelo menos um preço.")

# --- ABA 2: ÁREA DO CLIENTE (Gestão interna) ---
with aba_c:
    if not st.session_state.logado:
        senha = st.text_input("Chave de Segurança:", type="password")
        if st.button("ACESSAR SISTEMA"):
            if senha == "PRO2026":
                st.session_state.logado = True
                st.rerun()
    else:
        st.success("Acesso Liberado!")
        st.markdown("### 📥 Importar Respostas")
        texto = st.text_area("Cole aqui a mensagem recebida do Fornecedor no WhatsApp:", height=200)
        if st.button("📥 PROCESSAR E COMPARAR"):
            try:
                linhas = [l for l in texto.split('\n') if l.strip()]
                fornecedor = linhas[0].replace("COTAÇÃO_", "").strip()
                novas = []
                for l in linhas[1:]:
                    if ":" in l:
                        p, v = l.split(":")
                        novas.append({'Fornecedor': fornecedor.upper(), 'Produto': p.strip(), 'Preço': float(v.strip())})
                st.session_state.base_analise = pd.concat([st.session_state.base_analise, pd.DataFrame(novas)], ignore_index=True)
                st.balloons()
                st.success(f"Cotação da empresa {fornecedor} adicionada com sucesso!")
            except: 
                st.error("Erro no formato! Certifique-se de copiar a mensagem completa do WhatsApp.")

# --- ABA 3: RELATÓRIO FINAL (Economia) ---
with aba_r:
    if not st.session_state.logado:
        st.error("Acesso restrito ao administrador.")
    elif st.session_state.base_analise.empty:
        st.info("Aguardando o recebimento das primeiras cotações para gerar a economia.")
    else:
        df_total = st.session_state.base_analise
        # Lógica de menor preço
        vencedores = df_total.loc[df_total.groupby('Produto')['Preço'].idxmin()]
        
        forn_list = sorted(vencedores['Fornecedor'].unique().tolist())
        st.markdown("### 🎯 Melhores Preços Encontrados")
        
        selected = st.selectbox("Escolha o Fornecedor para ver o pedido dele:", forn_list)
        pedido = vencedores[vencedores['Fornecedor'] == selected]
        
        col1, col2 = st.columns(2)
        col1.metric("Total do Pedido", f"R$ {pedido['Preço'].sum():.2f}")
        col2.metric("Itens Vencidos", len(pedido))
        
        st.dataframe(pedido[['Produto', 'Preço']], use_container_width=True, hide_index=True)
        
        # Exportação
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pedido.to_excel(writer, index=False, sheet_name='Pedido_CotaFacil')
        st.download_button(f"📥 BAIXAR PEDIDO - {selected}", output.getvalue(), f"pedido_{selected}.xlsx")
        
        st.markdown("---")
        if st.button("🗑️ ZERAR TUDO E COMEÇAR NOVA COMPRA"):
            st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
            st.rerun()
