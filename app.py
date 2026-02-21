import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL FUTURISTA ---
st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #00d4ff; text-shadow: 0 0 10px #00d4ff; text-align: center; font-family: 'Orbitron', sans-serif; }
    .stButton>button { 
        background: linear-gradient(45deg, #00d4ff, #005f73); 
        color: white; border: none; border-radius: 10px; width: 100%;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
    }
    div[data-testid="stExpander"] { border: 1px solid #00d4ff; border-radius: 10px; background-color: #161b22; }
    .metric-card { background: #1f2937; padding: 15px; border-radius: 10px; border-left: 5px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>PRO-SUPPLY | SMART ANALYTICS</h1>", unsafe_allow_html=True)

# --- LINKS E CONEXÕES ---
# Leitura via CSV (Rápida)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

@st.cache_data(ttl=5)
def carregar_dados():
    df = pd.read_csv(URL_CSV)
    df.columns = [str(c).strip().capitalize() for c in df.columns]
    return df

try:
    df_prod = carregar_dados()
    itens_ativos = []
    if 'Selecionado' in df_prod.columns and 'Produto' in df_prod.columns:
        mask = df_prod['Selecionado'].astype(str).str.lower().str.strip() == 'x'
        itens_ativos = df_prod[mask]['Produto'].tolist()

    # --- NAVEGAÇÃO ---
    aba_f, aba_c = st.tabs(["🚀 PORTAL DO FORNECEDOR", "🛡️ CENTRAL DE ANÁLISE"])

    with aba_f:
        st.subheader("📝 Formulário de Cotação Inteligente")
        
        with st.form("form_fornecedor"):
            c1, c2 = st.columns(2)
            with c1:
                nome_fornecedor = st.text_input("🏢 Nome da Empresa", placeholder="Sua marca aqui")
            with c2:
                tipo_preco = st.selectbox("💰 Condição do Preço", ["Líquido", "Bonificado", "Com ST"])
            
            st.divider()
            
            dados_cotacao = []
            for item in itens_ativos:
                with st.expander(f"📦 {item}", expanded=True):
                    col_p1, col_p2, col_obs = st.columns([1, 1, 2])
                    p_uni = col_p1.number_input(f"Preço Unit.", key=f"u_{item}", min_value=0.0)
                    p_vol = col_p2.number_input(f"Preço Vol.", key=f"v_{item}", min_value=0.0)
                    obs_item = col_obs.text_input(f"Obs.", key=f"o_{item}")
                    
                    if p_uni > 0:
                        dados_cotacao.append({
                            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Fornecedor": nome_fornecedor,
                            "Produto": item,
                            "Preco_Unitario": p_uni,
                            "Preco_Volume": p_vol,
                            "Condicao": tipo_preco,
                            "Observacao": obs_item
                        })

            btn_enviar = st.form_submit_button("Sincronizar Dados com a Central")

            if btn_enviar:
                if not nome_fornecedor:
                    st.error("❌ Identifique o Fornecedor antes de enviar.")
                elif not dados_cotacao:
                    st.warning("⚠️ Preencha pelo menos um preço.")
                else:
                    try:
                        # CONEXÃO PARA ESCRITA (Usa os Secrets)
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        df_respostas = pd.DataFrame(dados_cotacao)
                        
                        # Lê o que já existe para anexar
                        try:
                            existente = conn.read(worksheet="Respostas")
                            final = pd.concat([existente, df_respostas], ignore_index=True)
                        except:
                            final = df_respostas
                        
                        conn.create(worksheet="Respostas", data=final)
                        st.balloons()
                        st.success("🚀 Sucesso! Sua cotação foi blindada e enviada para análise.")
                    except Exception as e:
                        st.error(f"Erro ao gravar na nuvem: {e}")

    with aba_c:
        st.subheader("🛡️ Painel de Inteligência de Compras")
        
        # Simulação de análise de menor preço
        if not df_prod.empty:
            st.markdown("### 📊 Status Atual da Planilha")
            st.dataframe(df_prod, use_container_width=True)
            
            # Aqui você pode carregar a aba 'Respostas' para comparar
            st.info("💡 Quando os fornecedores enviarem dados, use esta aba para ver o ranking de preços.")

except Exception as e:
    st.error(f"Erro na Matriz: {e}")
