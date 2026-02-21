import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import base64

st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

# --- LEITURA RÁPIDA (Public CSV) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

@st.cache_data(ttl=2)
def carregar_dados():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except: return pd.DataFrame()

# --- FUNÇÃO DE CONEXÃO BLINDADA ---
def obter_conexao():
    try:
        # Decodifica a chave Base64 para o formato original
        encoded_key = st.secrets["connections"]["gsheets"]["private_key_base64"]
        decoded_key = base64.b64decode(encoded_key).decode("utf-8")
        
        # Cria um dicionário de credenciais temporário para o Streamlit
        creds = dict(st.secrets["connections"]["gsheets"])
        creds["private_key"] = decoded_key
        
        return st.connection("gsheets", type=GSheetsConnection, **creds)
    except Exception as e:
        st.error(f"Erro na decodificação da chave: {e}")
        return None

df_prod = carregar_dados()
aba_f, aba_c = st.tabs(["🚀 PORTAL FORNECEDOR", "🛡️ CENTRAL DE ANÁLISE"])

with aba_f:
    st.subheader("📝 Formulário de Cotação")
    if not df_prod.empty and 'Selecionado' in df_prod.columns:
        itens = df_prod[df_prod['Selecionado'].astype(str).str.lower().str.strip() == 'x']['Produto'].tolist()
        
        if not itens:
            st.info("💡 Marque itens com 'x' na coluna 'Selecionado' da planilha.")
        else:
            with st.form("form_vendas"):
                fornecedor = st.text_input("Empresa/Fornecedor")
                lista_envio = []
                for item in itens:
                    with st.expander(f"📦 {item}", expanded=True):
                        c1, c2 = st.columns(2)
                        p_u = c1.number_input(f"Preço Unit.", key=f"u_{item}", min_value=0.0)
                        obs = c2.text_input(f"Obs.", key=f"o_{item}")
                        if p_u > 0:
                            lista_envio.append({"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Fornecedor": fornecedor, "Produto": item, "Preco_Unitario": p_u, "Observacao": obs})
                
                if st.form_submit_button("🚀 ENVIAR COTAÇÃO"):
                    conn = obter_conexao()
                    if conn and fornecedor and lista_envio:
                        try:
                            df_novas = pd.DataFrame(lista_envio)
                            try:
                                historico = conn.read(worksheet="Respostas", ttl=0)
                                df_final = pd.concat([historico, df_novas], ignore_index=True)
                            except: df_final = df_novas
                            
                            conn.create(worksheet="Respostas", data=df_final)
                            st.balloons()
                            st.success("✅ Cotação enviada com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao gravar: {e}")
                    else:
                        st.warning("Verifique se preencheu o fornecedor e os preços.")

with aba_c:
    st.subheader("🛡️ Inteligência de Suprimentos")
    conn = obter_conexao()
    if conn:
        try:
            df_res = conn.read(worksheet="Respostas")
            if not df_res.empty:
                df_res['Preco_Unitario'] = pd.to_numeric(df_res['Preco_Unitario'], errors='coerce')
                idx = df_res.groupby('Produto')['Preco_Unitario'].idxmin()
                st.write("### 🏆 Vencedores")
                st.dataframe(df_res.loc[idx, ['Produto', 'Fornecedor', 'Preco_Unitario']], use_container_width=True)
            else: st.info("Aguardando dados...")
        except: st.warning("Aba 'Respostas' não encontrada na planilha.")
