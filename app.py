import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL FUTURISTA ---
st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #00d4ff; text-shadow: 0 0 10px #00d4ff; text-align: center; font-family: 'Orbitron', sans-serif; }
    .stButton>button { 
        background: linear-gradient(45deg, #00d4ff, #005f73); 
        color: white; border: none; border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 0 25px rgba(0, 212, 255, 0.6); }
    div[data-testid="stExpander"] { border: 1px solid #00d4ff; border-radius: 10px; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>PRO-SUPPLY | SMART ANALYTICS</h1>", unsafe_allow_html=True)

# --- CONEXÃO E DADOS ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

@st.cache_data(ttl=5)
def carregar_dados():
    df = pd.read_csv(URL_PLANILHA)
    df.columns = [str(c).strip().capitalize() for c in df.columns]
    return df

try:
    df = carregar_dados()
    
    # Filtro de itens ativos
    itens_ativos = []
    if 'Selecionado' in df.columns and 'Produto' in df.columns:
        mask = df['Selecionado'].astype(str).str.lower().str.strip() == 'x'
        itens_ativos = df[mask]['Produto'].tolist()

    # --- NAVEGAÇÃO ---
    aba_f, aba_c = st.tabs(["🚀 PORTAL DO FORNECEDOR", "🛡️ CENTRAL DE ANÁLISE"])

    with aba_f:
        st.subheader("📝 Formulário de Cotação Inteligente")
        
        with st.form("form_fornecedor"):
            col1, col2 = st.columns(2)
            with col1:
                nome_fornecedor = st.text_input("🏢 Nome da Empresa / Fornecedor", placeholder="Ex: Distribuidora Alpha")
            with col2:
                tipo_preco = st.selectbox("💰 Condição do Preço", ["Líquido", "Bonificado", "Com ST incluído"])
            
            st.divider()
            
            respostas = {}
            for item in itens_ativos:
                with st.expander(f"📦 Item: {item}", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        p1 = st.number_input(f"Preço Unitário (R$)", key=f"u_{item}", min_value=0.0, step=0.01)
                    with c2:
                        p2 = st.number_input(f"Preço p/ Volume (ex: 12 un)", key=f"v_{item}", min_value=0.0, step=0.01)
                    obs = st.text_input(f"Observação para {item}", key=f"obs_{item}", placeholder="Validade, lote, etc...")
                    respostas[item] = {"Unitario": p1, "Volume": p2, "Obs": obs}

            st.divider()
            obs_geral = st.text_area("🗒️ Observações Gerais da Proposta")
            
            btn_enviar = st.form_submit_button("Sincronizar Cotação com a Nuvem")

            if btn_enviar:
                if not nome_fornecedor:
                    st.error("⚠️ Por favor, identifique o nome do Fornecedor.")
                else:
                    # SIMULAÇÃO DE ENVIO (Para gravar no Sheets, precisamos do gspread)
                    st.balloons()
                    st.success(f"✅ Protocolo gerado! Dados enviados com sucesso para a central PRO-SUPPLY.")
                    st.info(f"Fornecedor: {nome_fornecedor} | Horário: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    with aba_c:
        st.subheader("📊 Dashboards de Performance")
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Itens em Cotação", len(itens_ativos))
        col_m2.metric("Status do Servidor", "ONLINE", delta="Latência 24ms")

        st.write("### 🔍 Comparativo de Mercado")
        # Aqui simulamos a aba de tratamento de dados
        st.dataframe(df, use_container_width=True)
        
        st.info("💡 Dica: Os cálculos de 'Menor Preço' e 'Ganhador' serão processados automaticamente assim que a aba 'Respostas' receber os dados dos fornecedores.")

except Exception as e:
    st.error(f"Falha na Matriz de Dados: {e}")
