import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL DARK/FUTURISTA ---
st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

st.markdown("""
    <style>
    /* Fundo e Texto Geral */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Título Neon */
    .neon-title {
        color: #00d4ff;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 20px;
    }
    
    /* Botões Estilizados */
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #005f73);
        color: white;
        border: none;
        padding: 15px 32px;
        border-radius: 8px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        width: 100%;
    }
    
    /* Cards de itens */
    div[data-testid="stExpander"] {
        border: 1px solid #00d4ff;
        border-radius: 10px;
        background-color: #161b22;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='neon-title'>PRO-SUPPLY | SMART ANALYTICS</h1>", unsafe_allow_html=True)

# --- CONEXÕES ---
# Usamos o CSV para leitura ultra-rápida (seu link público)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

@st.cache_data(ttl=5)
def carregar_dados():
    df = pd.read_csv(URL_CSV)
    df.columns = [str(c).strip().capitalize() for c in df.columns]
    return df

try:
    df_prod = carregar_dados()
    
    # Identifica produtos com 'x'
    itens_ativos = []
    if 'Selecionado' in df_prod.columns and 'Produto' in df_prod.columns:
        mask = df_prod['Selecionado'].astype(str).str.lower().str.strip() == 'x'
        itens_ativos = df_prod[mask]['Produto'].tolist()

    # --- MENU DE NAVEGAÇÃO ---
    aba_f, aba_c = st.tabs(["🚀 PORTAL DO FORNECEDOR", "🛡️ CENTRAL DE ANÁLISE"])

    with aba_f:
        st.subheader("📝 Formulário de Cotação")
        
        with st.form("form_vendas"):
            c1, c2 = st.columns(2)
            with c1:
                nome_fornecedor = st.text_input("🏢 Nome do Fornecedor / Empresa", placeholder="Digite sua identificação")
            with c2:
                condicao = st.selectbox("💰 Tipo de Preço", ["Líquido (Faturado)", "Bonificado", "Com ST incluso"])
            
            st.write("---")
            
            # Lista de Itens
            respostas_lista = []
            for item in itens_ativos:
                with st.expander(f"📦 ITEM: {item}", expanded=True):
                    col1, col2, col3 = st.columns([1, 1, 2])
                    p_uni = col1.number_input(f"Preço Unit. (R$)", key=f"u_{item}", min_value=0.0, format="%.2f")
                    p_vol = col2.number_input(f"Preço Vol. (R$)", key=f"v_{item}", min_value=0.0, format="%.2f")
                    obs = col3.text_input(f"Observação", key=f"o_{item}", placeholder="Ex: Validade para 60 dias")
                    
                    if p_uni > 0: # Só registra se houver preço
                        respostas_lista.append({
                            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Fornecedor": nome_fornecedor,
                            "Produto": item,
                            "Preco_Unitario": p_uni,
                            "Preco_Volume": p_vol,
                            "Condicao": condicao,
                            "Observacao": obs
                        })

            st.write("---")
            btn_enviar = st.form_submit_button("🚀 ENVIAR COTAÇÃO AGORA")

            if btn_enviar:
                if not nome_fornecedor:
                    st.error("⚠️ Erro: Informe o nome do Fornecedor.")
                elif not respostas_lista:
                    st.warning("⚠️ Erro: Preencha o preço de pelo menos um produto.")
                else:
                    try:
                        # Conexão GSheets para ESCRITA
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        df_novas_resp = pd.DataFrame(respostas_lista)
                        
                        # Tenta ler histórico para não apagar dados antigos
                        try:
                            historico = conn.read(worksheet="Respostas")
                            df_final = pd.concat([historico, df_novas_resp], ignore_index=True)
                        except:
                            df_final = df_novas_resp
                        
                        # Grava na planilha
                        conn.create(worksheet="Respostas", data=df_final)
                        
                        st.balloons()
                        st.success(f"✅ Sincronizado! Obrigado {nome_fornecedor}, recebemos seus dados.")
                    except Exception as e:
                        st.error(f"❌ Falha ao gravar dados: {e}")

    with aba_c:
        st.subheader("🛡️ Painel de Decisão (Cliente)")
        
        # Aqui simulamos a análise de menor preço
        if not df_prod.empty:
            st.info("📊 Aba em desenvolvimento: Aqui você verá o ranking dos fornecedores.")
            st.dataframe(df_prod, use_container_width=True)

except Exception as e:
    st.error(f"Erro no sistema: {e}")
