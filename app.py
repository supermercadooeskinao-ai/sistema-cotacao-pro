import streamlit as st
import pandas as pd
import io
import base64
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- FUNÇÃO DE CONEXÃO SEGURA ---
def conectar_google():
    try:
        pk = base64.b64decode(st.secrets["google_pk_base64"]).decode("utf-8")
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
if 'lista_geral_produtos' not in st.session_state: st.session_state.lista_geral_produtos = []
if 'itens_para_cotar' not in st.session_state: st.session_state.itens_para_cotar = []

# Título Principal
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>SISTEMA INTELIGENTE DE COTAÇÕES</h1>", unsafe_allow_html=True)

aba_c, aba_f, aba_r = st.tabs(["🎯 Seleção de Itens", "📩 Painel Fornecedor", "📊 Relatório Final"])

with aba_c:
    st.subheader("Configurar Itens para Cotação")
    with st.sidebar:
        st.info("O Excel deve ter uma coluna chamada 'Produto'")
        arquivo = st.file_uploader("📂 Importar Base Excel", type=['xlsx'])
        if arquivo:
            df_imp = pd.read_excel(arquivo)
            if 'Produto' in df_imp.columns:
                # Remove duplicados e valores vazios
                st.session_state.lista_geral_produtos = sorted(df_imp['Produto'].dropna().unique().tolist())
                st.success(f"{len(st.session_state.lista_geral_produtos)} produtos carregados!")
            else:
                st.error("Coluna 'Produto' não encontrada no Excel.")

    if st.session_state.lista_geral_produtos:
        escolhidos = st.multiselect("Selecione os produtos que deseja cotar agora:", st.session_state.lista_geral_produtos)
        if st.button("CONFIRMAR LISTA SELECIONADA"):
            st.session_state.itens_para_cotar = escolhidos
            st.success(f"Lista com {len(escolhidos)} itens pronta para o fornecedor!")
            st.toast("Lista atualizada!")
    else:
        st.info("Importe um arquivo Excel ao lado para começar.")

with aba_f:
    if not st.session_state.itens_para_cotar:
        st.warning("Selecione os itens na primeira aba primeiro.")
    else:
        with st.form("form_f"):
            f_nome = st.text_input("Nome do Fornecedor / Distribuidora")
            f_tipo = st.selectbox("Condição Comercial", ["NF", "Líquido", "Bonificado", "Outros"])
            dados_temp = []
            
            st.write("---")
            for item in st.session_state.itens_para_cotar:
                c1, c2 = st.columns([1, 2])
                p = c1.number_input(f"Preço Unit. ({item})", min_value=0.0, format="%.2f", key=f"p_{item}")
                o = c2.text_input(f"Observação", key=f"o_{item}", placeholder="Ex: Validade, lote...")
                if p > 0:
                    dados_temp.append({
                        'Data': datetime.now().strftime("%d/%m/%Y"),
                        'Fornecedor': f_nome, 
                        'Produto': item, 
                        'Preço': p, 
                        'Tipo': f_tipo, 
                        'Obs': o
                    })
            
            st.write("---")
            if st.form_submit_button("🚀 ENVIAR PREÇOS PARA O GOOGLE SHEETS"):
                if not f_nome:
                    st.error("Por favor, preencha o nome do fornecedor.")
                elif not dados_temp:
                    st.warning("Insira pelo menos um preço antes de enviar.")
                else:
                    conn = conectar_google()
                    if conn:
                        try:
                            # Tenta ler a planilha existente ou cria nova se falhar
                            try:
                                existente = conn.read(spreadsheet=st.secrets["id_planilha"], worksheet="Respostas")
                            except:
                                existente = pd.DataFrame()
                            
                            df_novos = pd.DataFrame(dados_temp)
                            df_final = pd.concat([existente, df_novos], ignore_index=True)
                            
                            conn.create(spreadsheet=st.secrets["id_planilha"], worksheet="Respostas", data=df_final)
                            st.balloons()
                            st.success("✅ Cotação enviada com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")

with aba_r:
    st.subheader("📊 Histórico de Cotações na Nuvem")
    conn = conectar_google()
    if conn:
        try:
            df_nuvem = conn.read(spreadsheet=st.secrets["id_planilha"], worksheet="Respostas", ttl=0)
            if not df_nuvem.empty:
                st.write("Abaixo estão todos os preços registrados até agora:")
                st.dataframe(df_nuvem, use_container_width=True)
                
                # Exportação rápida
                csv = df_nuvem.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Baixar tudo em CSV", csv, "cotacoes_completas.csv", "text/csv")
            else:
                st.info("Nenhum dado registrado na nuvem ainda.")
        except:
            st.warning("Aba 'Respostas' não detectada na planilha Google.")
