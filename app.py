import streamlit as st
import pandas as pd
import io
import base64
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- FUNÇÃO DE CONEXÃO SEGURA ---
def conectar_google():
    try:
        # Decodifica a chave para evitar erro de PEM/Length
        pk = base64.b64decode(st.secrets["google_pk_base64"]).decode("utf-8")
        
        # Monta credenciais manualmente para evitar erro de 'multiple values for type'
        creds = {
            "type": "service_account",
            "project_id": st.secrets["google_project_id"],
            "private_key": pk,
            "client_email": st.secrets["google_client_email"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        return st.connection("gsheets", type=GSheetsConnection, credentials=creds)
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

# --- SEGURANÇA COMERCIAL ---
CHAVE_ACESSO = "PRO2026"

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.set_page_config(page_title="Ativação de Licença", page_icon="🔐")
    st.markdown("<h2 style='text-align: center;'>🔐 Ativação de Software</h2>", unsafe_allow_html=True)
    senha = st.text_input("Insira sua Chave de Licença:", type="password")
    if st.button("Ativar Sistema"):
        if senha == CHAVE_ACESSO:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Chave inválida.")
    st.stop()

# --- CONFIGURAÇÃO DO APP ---
st.set_page_config(page_title="PRO-SUPPLY | Smart Analytics", page_icon="⚡", layout="wide")

# Inicialização de Estados
if 'dados_industrias' not in st.session_state: st.session_state.dados_industrias = {}
if 'itens_para_cotar' not in st.session_state: st.session_state.itens_para_cotar = []

# Título Principal
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>SISTEMA INTELIGENTE DE COTAÇÕES</h1>", unsafe_allow_html=True)

aba_c, aba_f, aba_r = st.tabs(["🎯 Seleção Estratégica", "📩 Painel Fornecedor", "📊 Relatório Final"])

with aba_c:
    st.subheader("Configurar Cotação")
    with st.sidebar:
        arquivo = st.file_uploader("📂 Importar Base Excel", type=['xlsx'])
        if arquivo:
            df_imp = pd.read_excel(arquivo)
            for _, linha in df_imp.iterrows():
                ind = str(linha['Indústria']).strip()
                prod = str(linha['Produto']).strip()
                if ind not in st.session_state.dados_industrias: st.session_state.dados_industrias[ind] = []
                if prod not in st.session_state.dados_industrias[ind]: st.session_state.dados_industrias[ind].append(prod)
            st.success("Base Carregada!")

    if st.session_state.dados_industrias:
        ind_sel = st.selectbox("Escolha a Indústria", sorted(st.session_state.dados_industrias.keys()))
        escolhidos = st.multiselect("Produtos:", st.session_state.dados_industrias[ind_sel])
        if st.button("CONFIRMAR LISTA"):
            st.session_state.itens_para_cotar = escolhidos
            st.toast("Lista atualizada!")

with aba_f:
    if not st.session_state.itens_para_cotar:
        st.warning("Selecione os itens na primeira aba.")
    else:
        with st.form("form_f"):
            f_nome = st.text_input("Nome do Fornecedor")
            f_tipo = st.selectbox("Condição", ["NF", "Líquido", "Bonificado"])
            dados_temp = []
            
            for item in st.session_state.itens_para_cotar:
                c1, c2 = st.columns([1, 2])
                p = c1.number_input(f"Preço {item}", min_value=0.0, format="%.2f", key=f"p_{item}")
                o = c2.text_input(f"Obs {item}", key=f"o_{item}")
                if p > 0:
                    dados_temp.append({
                        'Data': datetime.now().strftime("%d/%m/%Y"),
                        'Fornecedor': f_nome, 
                        'Produto': item, 
                        'Preço': p, 
                        'Tipo': f_tipo, 
                        'Obs': o
                    })
            
            if st.form_submit_button("🚀 ENVIAR COTAÇÃO PARA NUVEM"):
                if not f_nome:
                    st.error("Identifique o fornecedor!")
                else:
                    conn = conectar_google()
                    if conn:
                        try:
                            # 1. Lê o que já existe
                            try:
                                existente = conn.read(spreadsheet=st.secrets["id_planilha"], worksheet="Respostas")
                            except:
                                existente = pd.DataFrame()
                            
                            # 2. Junta com os novos dados
                            df_novos = pd.DataFrame(dados_temp)
                            df_final = pd.concat([existente, df_novos], ignore_index=True)
                            
                            # 3. Salva de volta
                            conn.create(spreadsheet=st.secrets["id_planilha"], worksheet="Respostas", data=df_final)
                            st.balloons()
                            st.success("✅ Sincronizado com o Google Sheets!")
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")

with aba_r:
    st.subheader("📊 Resultados na Nuvem")
    conn = conectar_google()
    if conn:
        try:
            df_nuvem = conn.read(spreadsheet=st.secrets["id_planilha"], worksheet="Respostas", ttl=0)
            if not df_nuvem.empty:
                st.dataframe(df_nuvem, use_container_width=True)
                
                # Botão para limpar (Opcional)
                if st.button("Limpar Histórico da Nuvem"):
                    conn.create(spreadsheet=st.secrets["id_planilha"], worksheet="Respostas", data=pd.DataFrame(columns=df_nuvem.columns))
                    st.rerun()
            else:
                st.info("Nenhum dado encontrado na aba 'Respostas'.")
        except:
            st.warning("Aba 'Respostas' não encontrada na planilha.")
