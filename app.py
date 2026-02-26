import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="COTA FACIL | Smart Analytics", page_icon="⚡", layout="wide")

# --- ESTILO CSS PERSONALIZADO (UI/UX) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .metric-container {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #58a6ff; }
    .metric-label { font-size: 14px; color: #8b949e; text-transform: uppercase; }
    .stButton>button {
        background: linear-gradient(90deg, #1f6feb 0%, #1158c7 100%);
        color: white; border: none; border-radius: 5px; font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22; border-radius: 5px 5px 0 0; color: #8b949e;
    }
    .stTabs [aria-selected="true"] { background-color: #1f6feb !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SEGURANÇA COMERCIAL ---
CHAVE_ACESSO = "PRO2026"

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div style='text-align: center;'><h2>🔐 Ativação de Sistema</h2><p style='color: #8b949e;'>Insira sua licença PRO-SUPPLY</p></div>", unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="Chave de Acesso")
        if st.button("ATIVAR LICENÇA"):
            if senha == CHAVE_ACESSO:
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Chave inválida. Verifique com o suporte.")
    st.stop()

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'historico_local' not in st.session_state:
    st.session_state.historico_local = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Data'])

# --- TÍTULO ---
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>🛡️ PRO-SUPPLY <span style='color: white;'>SMART</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Inteligência em Compras e Cotações via WhatsApp</p>", unsafe_allow_html=True)

aba_c, aba_a = st.tabs(["📦 1. PREPARAR COTAÇÃO", "📊 2. ANALISAR E GERAR PEDIDO"])

with aba_c:
    st.subheader("Configuração de Itens")
    with st.sidebar:
        st.markdown("### 📂 Importação")
        arquivo = st.file_uploader("Upload da Lista Mestra (Excel)", type=['xlsx'])
    
    if arquivo:
        try:
            df_imp = pd.read_excel(arquivo, engine='openpyxl')
            if 'Produto' in df_imp.columns:
                lista_prods = sorted(df_imp['Produto'].dropna().unique().tolist())
                st.info(f"✨ {len(lista_prods)} produtos identificados na base.")
                
                selecionados = st.multiselect("Selecione os itens para cotar agora:", lista_prods)
                
                if selecionados:
                    st.write("---")
                    st.markdown("### 💬 Mensagem para WhatsApp")
                    texto_zap = "Olá, segue cotação:\n\n"
                    for item in selecionados:
                        texto_zap += f"- {item}: R$ \n"
                    texto_zap += "\n*Por favor, preencha os valores e responda esta mensagem.*"
                    st.text_area("", texto_zap, height=200, help="Copie e envie para seus fornecedores.")
            else:
                st.error("Coluna 'Produto' não encontrada.")
        except Exception as e:
            st.error(f"Erro: {e}")

with aba_a:
    st.subheader("Processamento de Respostas")
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        with st.expander("📥 Registrar Nova Resposta", expanded=True):
            f_nome = st.text_input("Nome do Fornecedor:")
            res_texto = st.text_area("Cole a mensagem recebida:", height=200, placeholder="Ex: - Item: R$ 10,00")
            
            if st.button("PROCESSAR E COMPARAR"):
                if f_nome and res_texto:
                    linhas = res_texto.split('\n')
                    novos_dados = []
                    for linha in linhas:
                        if ':' in linha and 'R$' in linha:
                            try:
                                item = linha.split(':')[0].replace('-', '').strip()
                                valor = linha.split('R$')[1].strip().replace('.', '').replace(',', '.')
                                novos_dados.append({
                                    'Fornecedor': f_nome.upper(), 
                                    'Produto': item.upper(), 
                                    'Preço': float(valor), 
                                    'Data': datetime.now().strftime("%d/%m/%Y")
                                })
                            except: continue
                    
                    if novos_dados:
                        st.session_state.historico_local = pd.concat([st.session_state.historico_local, pd.DataFrame(novos_dados)], ignore_index=True)
                        st.toast(f"✅ Sucesso: {f_nome}")
                    else:
                        st.error("Formato de texto não reconhecido.")

    with col2:
        if not st.session_state.historico_local.empty:
            df_res = st.session_state.historico_local
            venc = df_res.loc[df_res.groupby('Produto')['Preço'].idxmin()]
            
            # Métricas em Cards
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f"""<div class='metric-container'><div class='metric-label'>Investimento Total</div><div class='metric-value'>R$ {venc['Preço'].sum():,.2f}</div></div>""", unsafe_allow_html=True)
            with m2:
                economia = df_res.groupby('Produto')['Preço'].max().sum() - venc['Preço'].sum()
                st.markdown(f"""<div class='metric-container'><div class='metric-label'>Economia Gerada</div><div class='metric-value' style='color: #3fb950;'>R$ {economia:,.2f}</div></div>""", unsafe_allow_html=True)
            
            st.write("### 🏆 Itens Selecionados (Melhor Preço)")
            st.dataframe(venc[['Produto', 'Fornecedor', 'Preço']], use_container_width=True)

            # Exportação
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                venc.to_excel(writer, index=False, sheet_name='Pedido_Sugerido')
            
            st.download_button(
                label="📥 BAIXAR PEDIDO OTIMIZADO (EXCEL)",
                data=output.getvalue(),
                file_name=f"pedido_pro_supply_{datetime.now().strftime('%d%m%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            if st.button("🗑️ LIMPAR TODOS OS DADOS"):
                st.session_state.historico_local = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Data'])
                st.rerun()
        else:
            st.info("Aguardando inserção de dados para análise.")
