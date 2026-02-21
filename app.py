import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import base64

st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

# Estilo Futurista
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .neon { color: #00d4ff; text-shadow: 0 0 10px #00d4ff; text-align: center; font-weight: bold; }
    .stButton>button { background: linear-gradient(45deg, #00d4ff, #005f73); color: white; border-radius: 8px; font-weight: bold; width: 100%; }
    div[data-testid="stExpander"] { border: 1px solid #00d4ff; border-radius: 10px; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='neon'>PRO-SUPPLY | SMART ANALYTICS</h1>", unsafe_allow_html=True)

# Função para conectar usando a chave decodificada
def conectar_gsheets():
    try:
        # Pega a chave codificada dos secrets
        pk_b64 = st.secrets["connections"]["gsheets"]["private_key_base64"]
        # Decodifica
        pk_limpa = base64.b64decode(pk_b64).decode("utf-8")
        
        # Monta as credenciais
        creds = dict(st.secrets["connections"]["gsheets"])
        creds["private_key"] = pk_limpa
        
        return st.connection("gsheets", type=GSheetsConnection, **creds)
    except Exception as e:
        st.error(f"Erro na chave de segurança: {e}")
        return None

# Leitura rápida via CSV
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

@st.cache_data(ttl=2)
def ler_itens():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except: return pd.DataFrame()

df_prod = ler_itens()
aba_f, aba_c = st.tabs(["🚀 PORTAL FORNECEDOR", "🛡️ CENTRAL DE ANÁLISE"])

with aba_f:
    st.subheader("📝 Formulário de Cotação")
    if not df_prod.empty and 'Selecionado' in df_prod.columns:
        itens = df_prod[df_prod['Selecionado'].astype(str).str.lower().str.strip() == 'x']['Produto'].tolist()
        
        if not itens:
            st.info("Nenhum item selecionado na planilha.")
        else:
            with st.form("form_vendas"):
                fornecedor = st.text_input("Nome da sua Empresa")
                lista_respostas = []
                for item in itens:
                    with st.expander(f"📦 {item}", expanded=True):
                        c1, c2 = st.columns(2)
                        p_u = c1.number_input(f"Preço Unitário", key=f"u_{item}", min_value=0.0)
                        obs = c2.text_input(f"Observações", key=f"o_{item}")
                        if p_u > 0:
                            lista_respostas.append({
                                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "Fornecedor": fornecedor,
                                "Produto": item,
                                "Preco_Unitario": p_u,
                                "Observacao": obs
                            })
                
                if st.form_submit_button("🚀 ENVIAR PARA CENTRAL"):
                    conn = conectar_gsheets()
                    if conn and fornecedor and lista_respostas:
                        try:
                            df_novas = pd.DataFrame(lista_respostas)
                            try:
                                historico = conn.read(worksheet="Respostas", ttl=0)
                                df_final = pd.concat([historico, df_novas], ignore_index=True)
                            except: df_final = df_novas
                            
                            conn.create(worksheet="Respostas", data=df_final)
                            st.balloons()
                            st.success("✅ Cotação sincronizada!")
                        except Exception as e:
                            st.error(f"Erro ao gravar na planilha: {e}")
                    else:
                        st.warning("Preencha o nome da empresa e pelo menos um preço.")

with aba_c:
    st.subheader("🛡️ Análise de Preços")
    conn = conectar_gsheets()
    if conn:
        try:
            df_res = conn.read(worksheet="Respostas", ttl=5)
            if not df_res.empty:
                df_res['Preco_Unitario'] = pd.to_numeric(df_res['Preco_Unitario'], errors='coerce')
                idx = df_res.groupby('Produto')['Preco_Unitario'].idxmin()
                st.write("### 🏆 Melhores Ofertas Atuais")
                st.dataframe(df_res.loc[idx, ['Produto', 'Fornecedor', 'Preco_Unitario']], use_container_width=True)
                st.write("### 📜 Histórico de Envio")
                st.dataframe(df_res, use_container_width=True)
            else: st.info("Aguardando cotações...")
        except: st.warning("Aba 'Respostas' não encontrada na planilha.")
