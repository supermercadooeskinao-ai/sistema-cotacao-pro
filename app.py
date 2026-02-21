import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# CONFIGURAÇÃO VISUAL
st.set_page_config(page_title="PRO-SUPPLY ANALYTICS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .neon-text { color: #00d4ff; text-shadow: 0 0 10px #00d4ff; font-weight: bold; text-align: center; }
    .stButton>button { background: linear-gradient(45deg, #00d4ff, #005f73); color: white; width: 100%; border-radius: 8px; font-weight: bold; }
    div[data-testid="stExpander"] { border: 1px solid #00d4ff; border-radius: 10px; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='neon-text'>PRO-SUPPLY | SMART ANALYTICS</h1>", unsafe_allow_html=True)

# LINK PÚBLICO PARA LEITURA RÁPIDA
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

@st.cache_data(ttl=2)
def carregar_dados():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_prod = carregar_dados()

aba_fornecedor, aba_analise = st.tabs(["🚀 PORTAL FORNECEDOR", "🛡️ CENTRAL DE ANÁLISE"])

with aba_fornecedor:
    if not df_prod.empty and 'Selecionado' in df_prod.columns:
        itens_ativos = df_prod[df_prod['Selecionado'].astype(str).str.lower().str.strip() == 'x']['Produto'].tolist()
        
        if not itens_ativos:
            st.info("Aguardando seleção de itens na planilha...")
        else:
            with st.form("form_vendas"):
                c1, c2 = st.columns(2)
                fornecedor = c1.text_input("Empresa/Fornecedor")
                condicao = c2.selectbox("Condição Comercial", ["Líquido", "Bonificado", "Com ST"])
                
                lista_envio = []
                for item in itens_ativos:
                    with st.expander(f"📦 {item}", expanded=True):
                        col_u, col_v, col_o = st.columns([1, 1, 2])
                        v_u = col_u.number_input(f"Preço Unit.", key=f"u_{item}", min_value=0.0)
                        v_v = col_v.number_input(f"Preço Vol.", key=f"v_{item}", min_value=0.0)
                        v_o = col_o.text_input(f"Obs.", key=f"o_{item}")
                        if v_u > 0:
                            lista_envio.append({"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Fornecedor": fornecedor, "Produto": item, "Preco_Unitario": v_u, "Preco_Volume": v_v, "Condicao": condicao, "Observacao": v_o})

                if st.form_submit_button("🚀 ENVIAR COTAÇÃO"):
                    if not fornecedor:
                        st.error("Nome do fornecedor obrigatório.")
                    elif not lista_envio:
                        st.warning("Preencha ao menos um preço.")
                    else:
                        try:
                            # CONEXÃO COM TRATAMENTO DE CHAVE
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            df_novas = pd.DataFrame(lista_envio)
                            try:
                                historico = conn.read(worksheet="Respostas")
                                df_final = pd.concat([historico, df_novas], ignore_index=True)
                            except:
                                df_final = df_novas
                            
                            conn.create(worksheet="Respostas", data=df_final)
                            st.balloons()
                            st.success("✅ Cotação enviada!")
                        except Exception as e:
                            st.error(f"Erro de conexão: {e}")

with aba_analise:
    st.subheader("🛡️ Central de Inteligência")
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_res = conn.read(worksheet="Respostas")
        if not df_res.empty:
            df_res['Preco_Unitario'] = pd.to_numeric(df_res['Preco_Unitario'], errors='coerce')
            idx = df_res.groupby('Produto')['Preco_Unitario'].idxmin()
            st.write("### 🏆 Vencedores por Item")
            st.dataframe(df_res.loc[idx, ['Produto', 'Fornecedor', 'Preco_Unitario', 'Condicao']], use_container_width=True)
        else:
            st.info("Nenhuma resposta recebida ainda.")
    except:
        st.warning("Aba 'Respostas' não encontrada.")
