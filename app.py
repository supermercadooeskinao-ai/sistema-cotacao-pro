import streamlit as st
import pandas as pd
import time
import urllib.parse
import io

# --- 1. CONFIGURAÇÃO DE IDENTIDADE E SEGURANÇA ---
# Mude o nome para cada cliente (deve ser igual ao que está na sua Planilha Mestra)
ID_CLIENTE_ATUAL = "Restaurante_A" 

# Substitua pelos seus links CSV do Google Sheets
URL_CONTROLE_MESTRE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSAunSaeCenC0s0AX5aq7DyK8sRlVMDfLQ0TxYLkSZz72uNXf9a-EJ-e4k14Ve6k3Ie4bDqeQte6xhI/pub?output=csv"
URL_PLANILHA_PRODUTOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"
TELEFONE_SUPORTE = "5574988391826" # Seu número para quem for bloqueado
TELEFONE_DESTINO_COTACAO = "5574988391826" # Número do cliente que recebe as cotações

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="COTA FÁCIL | Smart Analytics", layout="wide", page_icon="⚡")

# Estilização CSS para garantir legibilidade e visual moderno
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .product-card { 
        background-color: #ffffff !important; 
        padding: 15px; border-radius: 10px; 
        border-left: 6px solid #58a6ff; 
        margin-bottom: 5px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .product-name {
        color: #1c1e21 !important; font-size: 18px !important;
        font-weight: bold !important; display: block; margin-bottom: 5px;
    }
    div[data-testid="stMetricValue"] { color: #58a6ff !important; }
    .stTabs [aria-selected="true"] { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES DE DADOS E VALIDAÇÃO ---
def verificar_acesso():
    try:
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

# --- 4. TRAVA DE ACESSO ---
status_acesso = verificar_acesso()

if status_acesso == "BLOQUEADO":
    st.error(f"### ⚠️ ACESSO SUSPENSO: {ID_CLIENTE_ATUAL.replace('_', ' ')}")
    st.info("Identificamos uma pendência na licença. Entre em contato com o suporte.")
    st.link_button("📲 FALAR COM FINANCEIRO", f"https://wa.me/{TELEFONE_SUPORTE}")
    st.stop()

# --- 5. INICIALIZAÇÃO DE SESSÃO ---
if 'base_analise' not in st.session_state:
    st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- 6. INTERFACE PRINCIPAL ---
st.markdown(f"<h1 style='text-align: center; color: #58a6ff;'>🛡️ COTA FÁCIL <span style='color: white;'>| {ID_CLIENTE_ATUAL.replace('_', ' ')}</span></h1>", unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["📩 PAINEL DO FORNECEDOR", "🔐 ÁREA DO CLIENTE", "📊 RELATÓRIO FINAL"])

df_google = carregar_produtos()
itens_ativos = df_google[df_google['Selecionado'].notna()]['Produto'].tolist() if not df_google.empty else []

# --- ABA 1: FORNECEDOR ---
with aba_f:
    st.markdown("### 📋 Preencher Cotação")
    if not itens_ativos:
        st.warning("⚠️ Nenhuma cotação ativa no momento.")
    else:
        with st.form("form_fornecedor"):
            nome_f = st.text_input("Sua Empresa:", placeholder="Ex: Distribuidora Silva")
            st.markdown("---")
            dados_preenchidos = {}
            for item in itens_ativos:
                st.markdown(f'<div class="product-card"><span class="product-name">📦 {item}</span></div>', unsafe_allow_html=True)
                valor = st.number_input(f"Preço {item}", min_value=0.0, step=0.01, key=f"f_{item}", label_visibility="collapsed")
                if valor > 0: dados_preenchidos[item] = valor
                st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("✅ ENVIAR COTAÇÃO"):
                if nome_f and dados_preenchidos:
                    msg = f"COTAÇÃO_{nome_f.upper()}\n"
                    for p, v in dados_preenchidos.items(): msg += f"{p}: {v}\n"
                    link = f"https://wa.me/{TELEFONE_DESTINO_COTACAO}?text={urllib.parse.quote(msg)}"
                    st.link_button("🟢 ABRIR WHATSAPP", link, use_container_width=True)

# --- ABA 2: ÁREA DO CLIENTE ---
with aba_c:
    if not st.session_state.logado:
        senha = st.text_input("Chave de Acesso:", type="password")
        if st.button("DESBLOQUEAR"):
            if senha == "PRO2026":
                st.session_state.logado = True
                st.rerun()
    else:
        st.markdown("### 📥 Processar Respostas")
        texto = st.text_area("Cole aqui o texto do WhatsApp:", height=200)
        if st.button("📥 ADICIONAR AO RELATÓRIO"):
            try:
                linhas = [l for l in texto.split('\n') if l.strip()]
                fornecedor = linhas[0].replace("COTAÇÃO_", "").strip()
                novas = []
                for l in linhas[1:]:
                    if ":" in l:
                        p, v = l.split(":")
                        novas.append({'Fornecedor': fornecedor.upper(), 'Produto': p.strip(), 'Preço': float(v.strip())})
                st.session_state.base_analise = pd.concat([st.session_state.base_analise, pd.DataFrame(novas)], ignore_index=True)
                st.success(f"Fornecedor {fornecedor} adicionado!")
            except: st.error("Erro no formato!")

# --- ABA 3: RELATÓRIO FINAL ---
with aba_r:
    if not st.session_state.logado:
        st.error("Acesso restrito.")
    elif st.session_state.base_analise.empty:
        st.info("Aguardando dados...")
    else:
        df_total = st.session_state.base_analise
        vencedores = df_total.loc[df_total.groupby('Produto')['Preço'].idxmin()]
        
        forn_list = sorted(vencedores['Fornecedor'].unique().tolist())
        selected = st.selectbox("🎯 Ver Pedido por Fornecedor:", forn_list)
        pedido = vencedores[vencedores['Fornecedor'] == selected]
        
        c1, c2 = st.columns(2)
        c1.metric("Total do Pedido", f"R$ {pedido['Preço'].sum():.2f}")
        c2.metric("Itens Ganhos", len(pedido))
        
        st.dataframe(pedido[['Produto', 'Preço']], use_container_width=True, hide_index=True)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pedido.to_excel(writer, index=False, sheet_name='Pedido')
        st.download_button(f"📥 BAIXAR EXCEL ({selected})", output.getvalue(), f"pedido_{selected}.xlsx")
        
        if st.button("🗑️ RESETAR SISTEMA"):
            st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
            st.rerun()





