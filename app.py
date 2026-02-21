import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import base64

st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

# --- FUNÇÃO DE CONEXÃO CORRIGIDA ---
def conectar():
    try:
        # Pega as infos dos secrets
        s = st.secrets["connections"]["gsheets"]
        
        # Decodifica a chave privada
        pk_limpa = base64.b64decode(s["private_key_base64"]).decode("utf-8")
        
        # Monta o dicionário de credenciais EXATAMENTE como o Google quer
        creds = {
            "type": "service_account",
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk_limpa,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        # Cria a conexão passando as credenciais limpas
        return st.connection("gsheets", type=GSheetsConnection, **creds)
    except Exception as e:
        st.error(f"Erro na configuração: {e}")
        return None

# --- CARREGAMENTO DE DADOS (PÚBLICO) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

@st.cache_data(ttl=5)
def carregar_lista():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except: return pd.DataFrame()

df_itens = carregar_lista()

st.title("🛡️ PRO-SUPPLY SMART ANALYTICS")

aba1, aba2 = st.tabs(["🚀 PORTAL FORNECEDOR", "📊 ANÁLISE"])

with aba1:
    if not df_itens.empty and 'Selecionado' in df_itens.columns:
        # Filtra apenas itens marcados com x
        selecionados = df_itens[df_itens['Selecionado'].astype(str).str.lower().str.strip() == 'x']['Produto'].tolist()
        
        if selecionados:
            with st.form("meu_form"):
                fornecedor = st.text_input("Sua Empresa")
                dados_coletados = []
                
                for item in selecionados:
                    with st.expander(f"Item: {item}", expanded=True):
                        p = st.number_input(f"Preço Unitário", key=f"p_{item}", min_value=0.0)
                        o = st.text_input(f"Obs", key=f"o_{item}")
                        if p > 0:
                            dados_coletados.append({
                                "Data": datetime.now().strftime("%d/%m/%Y"),
                                "Fornecedor": fornecedor,
                                "Produto": item,
                                "Preco": p,
                                "Obs": o
                            })
                
                if st.form_submit_button("ENVIAR COTAÇÃO"):
                    conn = conectar()
                    if conn and fornecedor and dados_coletados:
                        df_novos = pd.DataFrame(dados_coletados)
                        try:
                            # Tenta ler o que já existe na aba 'Respostas'
                            try:
                                existente = conn.read(worksheet="Respostas", ttl=0)
                                final = pd.concat([existente, df_novos], ignore_index=True)
                            except: final = df_novos
                            
                            conn.create(worksheet="Respostas", data=final)
                            st.success("✅ Enviado com sucesso!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")
        else:
            st.info("Nenhum item selecionado na planilha mestre.")

with aba2:
    st.subheader("Central de Inteligência")
    conn = conectar()
    if conn:
        try:
            df_res = conn.read(worksheet="Respostas", ttl=0)
            st.dataframe(df_res, use_container_width=True)
        except:
            st.warning("A aba 'Respostas' ainda não foi criada ou está vazia.")
