import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL DARK/FUTURISTA ---
st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .neon-title {
        color: #00d4ff;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff;
        text-align: center;
        padding: 20px;
        font-weight: bold;
    }
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #005f73);
        color: white; border: none; padding: 12px;
        border-radius: 8px; font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); background: linear-gradient(45deg, #005f73, #00d4ff); }
    div[data-testid="stExpander"] {
        border: 1px solid #00d4ff;
        border-radius: 10px;
        background-color: #161b22;
    }
    [data-testid="stMetricValue"] { color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='neon-title'>PRO-SUPPLY | SMART ANALYTICS</h1>", unsafe_allow_html=True)

# --- 2. CONEXÕES E LEITURA ---
# Usamos o link CSV para leitura pública e rápida
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

@st.cache_data(ttl=5)
def carregar_estoque():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao acessar nuvem: {e}")
        return pd.DataFrame()

df_prod = carregar_estoque()

# --- 3. LÓGICA DE NAVEGAÇÃO ---
aba_f, aba_c = st.tabs(["🚀 PORTAL DO FORNECEDOR", "🛡️ CENTRAL DE ANÁLISE"])

with aba_f:
    st.subheader("📝 Formulário de Cotação")
    
    # Identifica itens marcados com 'x'
    itens_ativos = []
    if not df_prod.empty and 'Selecionado' in df_prod.columns:
        mask = df_prod['Selecionado'].astype(str).str.lower().str.strip() == 'x'
        itens_ativos = df_prod[mask]['Produto'].tolist()

    if not itens_ativos:
        st.info("💡 Aguardando seleção de itens na planilha mestre...")
    else:
        with st.form("form_vendas"):
            c1, c2 = st.columns(2)
            with c1:
                nome_fornecedor = st.text_input("🏢 Nome da Empresa", placeholder="Ex: Distribuidora XYZ")
            with c2:
                condicao = st.selectbox("💰 Condição Comercial", ["Líquido", "Bonificado", "Com ST"])
            
            respostas_lista = []
            for item in itens_ativos:
                with st.expander(f"📦 ITEM: {item}", expanded=True):
                    col1, col2, col3 = st.columns([1, 1, 2])
                    p_uni = col1.number_input(f"Preço Unit. (R$)", key=f"u_{item}", min_value=0.0, format="%.2f")
                    p_vol = col2.number_input(f"Preço Vol. (R$)", key=f"v_{item}", min_value=0.0, format="%.2f")
                    obs = col3.text_input(f"Observação", key=f"o_{item}")
                    
                    if p_uni > 0:
                        respostas_lista.append({
                            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Fornecedor": nome_fornecedor,
                            "Produto": item,
                            "Preco_Unitario": p_uni,
                            "Preco_Volume": p_vol,
                            "Condicao": condicao,
                            "Observacao": obs
                        })

            btn_enviar = st.form_submit_button("🚀 SINCRONIZAR COTAÇÃO")

            if btn_enviar:
                if not nome_fornecedor:
                    st.error("⚠️ Identifique sua empresa antes de enviar.")
                elif not respostas_lista:
                    st.warning("⚠️ Preencha pelo menos um preço válido.")
                else:
                    try:
                        # Conexão GSheets para escrita (Usa Secrets)
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        df_novas = pd.DataFrame(respostas_lista)
                        
                        try:
                            historico = conn.read(worksheet="Respostas")
                            df_final = pd.concat([historico, df_novas], ignore_index=True)
                        except:
                            df_final = df_novas
                        
                        conn.create(worksheet="Respostas", data=df_final)
                        st.balloons()
                        st.success("🛰️ TRANSMISSÃO CONCLUÍDA! Dados enviados para a central.")
                    except Exception as e:
                        st.error("❌ Falha na conexão de escrita. Verifique se a Private Key nos Secrets está correta.")

with aba_c:
    st.subheader("🛡️ Inteligência de Suprimentos")
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_resp = conn.read(worksheet="Respostas")
        
        if not df_resp.empty:
            # Tratamento: Menor Preço por Produto
            df_resp['Preco_Unitario'] = pd.to_numeric(df_resp['Preco_Unitario'], errors='coerce')
            idx_menor = df_resp.groupby('Produto')['Preco_Unitario'].idxmin()
            df_ganhadores = df_resp.loc[idx_menor, ['Produto', 'Fornecedor', 'Preco_Unitario', 'Condicao']]
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Propostas Recebidas", len(df_resp))
            m2.metric("Itens Cotados", len(df_ganhadores))
            m3.metric("Melhor Condição", df_ganhadores['Condicao'].mode()[0])

            st.write("### 🏆 Ranking de Menores Preços (Ganhadores)")
            st.dataframe(df_ganhadores.sort_values('Preco_Unitario'), use_container_width=True)
            
            with st.expander("📂 Ver Histórico Completo"):
                st.dataframe(df_resp)
        else:
            st.info("Aguardando o recebimento da primeira cotação para análise.")
    except:
        st.warning("Crie uma aba chamada 'Respostas' na sua planilha para ativar a análise.")
