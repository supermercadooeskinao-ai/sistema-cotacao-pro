import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .neon-title { color: #00d4ff; text-shadow: 0 0 10px #00d4ff; text-align: center; padding: 20px; font-weight: bold; }
    .stButton>button { background: linear-gradient(45deg, #00d4ff, #005f73); color: white; border-radius: 8px; width: 100%; }
    div[data-testid="stExpander"] { border: 1px solid #00d4ff; border-radius: 10px; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='neon-title'>PRO-SUPPLY | SMART ANALYTICS</h1>", unsafe_allow_html=True)

# --- LEITURA RÁPIDA (LINK CSV) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

@st.cache_data(ttl=5)
def carregar_dados():
    df = pd.read_csv(URL_CSV)
    df.columns = [str(c).strip().capitalize() for c in df.columns]
    return df

df_prod = carregar_dados()

# --- ABAS ---
aba_f, aba_c = st.tabs(["🚀 PORTAL DO FORNECEDOR", "🛡️ CENTRAL DE ANÁLISE"])

with aba_f:
    st.subheader("📝 Formulário de Cotação")
    
    itens_ativos = []
    if not df_prod.empty and 'Selecionado' in df_prod.columns:
        mask = df_prod['Selecionado'].astype(str).str.lower().str.strip() == 'x'
        itens_ativos = df_prod[mask]['Produto'].tolist()

    if not itens_ativos:
        st.info("💡 Selecione itens com 'x' na coluna B da planilha.")
    else:
        with st.form("form_vendas"):
            c1, c2 = st.columns(2)
            nome_f = c1.text_input("🏢 Nome da Empresa")
            cond = c2.selectbox("💰 Condição", ["Líquido", "Bonificado", "Com ST"])
            
            respostas = []
            for item in itens_ativos:
                with st.expander(f"📦 {item}", expanded=True):
                    col1, col2, col3 = st.columns([1, 1, 2])
                    p_u = col1.number_input(f"Preço Unit.", key=f"u_{item}", min_value=0.0)
                    p_v = col2.number_input(f"Preço Vol.", key=f"v_{item}", min_value=0.0)
                    obs = col3.text_input(f"Obs.", key=f"o_{item}")
                    if p_u > 0:
                        respostas.append({"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Fornecedor": nome_f, "Produto": item, "Preco_Unitario": p_u, "Preco_Volume": p_v, "Condicao": cond, "Observacao": obs})

            if st.form_submit_button("🚀 ENVIAR COTAÇÃO"):
                if not nome_f:
                    st.error("Informe o nome da empresa.")
                elif not respostas:
                    st.warning("Preencha ao menos um preço.")
                else:
                    try:
                        # AJUSTE TÉCNICO DA CHAVE ANTES DE CONECTAR
                        secrets = st.secrets["connections"]["gsheets"]
                        # Remove quebras de linha extras e garante o formato PEM correto
                        pk = secrets["private_key"].replace('\\n', '\n')
                        
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        df_novas = pd.DataFrame(respostas)
                        
                        try:
                            historico = conn.read(worksheet="Respostas")
                            df_final = pd.concat([historico, df_novas], ignore_index=True)
                        except:
                            df_final = df_novas
                        
                        conn.create(worksheet="Respostas", data=df_final)
                        st.balloons()
                        st.success("✅ Cotação enviada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao gravar: {e}")
                        st.info("Dica: Verifique se o e-mail da conta de serviço é EDITOR na planilha.")

with aba_c:
    st.subheader("🛡️ Inteligência de Suprimentos")
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_resp = conn.read(worksheet="Respostas")
        if not df_resp.empty:
            st.write("### 🏆 Ranking de Menores Preços")
            df_resp['Preco_Unitario'] = pd.to_numeric(df_resp['Preco_Unitario'], errors='coerce')
            idx = df_resp.groupby('Produto')['Preco_Unitario'].idxmin()
            st.dataframe(df_resp.loc[idx, ['Produto', 'Fornecedor', 'Preco_Unitario', 'Condicao']], use_container_width=True)
            st.write("### 📂 Todas as Respostas")
            st.dataframe(df_resp, use_container_width=True)
        else:
            st.info("Crie a aba 'Respostas' na planilha para ver a análise.")
    except:
        st.warning("Aba 'Respostas' não detectada ou sem dados.")
