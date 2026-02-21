import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- 1. CONFIGURAÇÃO VISUAL DARK/FUTURISTA ---
st.set_page_config(page_title="PRO-SUPPLY SMART ANALYTICS", layout="wide")

st.markdown("""
    <style>
    /* Estilização Geral Dark Mode */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Título Neon Impactante */
    .neon-title {
        color: #00d4ff;
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff;
        text-align: center;
        padding: 20px;
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-weight: 800;
        letter-spacing: 2px;
    }
    
    /* Customização dos Botões */
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #005f73);
        color: white; border: none; padding: 12px;
        border-radius: 8px; font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover { 
        transform: scale(1.02); 
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.6);
    }
    
    /* Cards de Itens (Expander) */
    div[data-testid="stExpander"] {
        border: 1px solid #00d4ff;
        border-radius: 10px;
        background-color: #161b22;
        margin-bottom: 10px;
    }
    
    /* Estilo das Métricas */
    [data-testid="stMetricValue"] { color: #00d4ff; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='neon-title'>PRO-SUPPLY | SMART ANALYTICS</h1>", unsafe_allow_html=True)

# --- 2. CONEXÃO E LEITURA DE DADOS ---
# Usamos o link CSV para leitura pública ultra-rápida (não depende de chaves)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

@st.cache_data(ttl=5)
def carregar_estoque():
    try:
        df = pd.read_csv(URL_CSV)
        # Limpa nomes de colunas
        df.columns = [str(c).strip().capitalize() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro na conexão de rede: {e}")
        return pd.DataFrame()

df_prod = carregar_estoque()

# --- 3. NAVEGAÇÃO POR ABAS ---
aba_f, aba_c = st.tabs(["🚀 PORTAL DO FORNECEDOR", "🛡️ CENTRAL DE ANÁLISE"])

with aba_f:
    st.subheader("📝 Formulário de Proposta Comercial")
    
    # Identifica itens ativos (marcados com 'x' na coluna Selecionado)
    itens_ativos = []
    if not df_prod.empty and 'Selecionado' in df_prod.columns:
        # Garante que 'Selecionado' seja string e remove espaços
        mask = df_prod['Selecionado'].astype(str).str.lower().str.strip() == 'x'
        itens_ativos = df_prod[mask]['Produto'].tolist()

    if not itens_ativos:
        st.info("💡 No momento, não há itens pendentes para cotação. Verifique a planilha mestre.")
    else:
        with st.form("form_vendas_profissional"):
            col_id1, col_id2 = st.columns(2)
            with col_id1:
                nome_fornecedor = st.text_input("🏢 Identificação da Empresa", placeholder="Nome Fantasia / Razão Social")
            with col_id2:
                condicao = st.selectbox("💰 Condição de Preço", ["Líquido", "Bonificado", "FOB", "CIF", "Com ST"])
            
            st.write("### Itens Selecionados para Cotação")
            
            respostas_lista = []
            for item in itens_ativos:
                with st.expander(f"📦 {item}", expanded=True):
                    c1, c2, c3 = st.columns([1, 1, 2])
                    p_uni = c1.number_input(f"Preço Unitário (R$)", key=f"u_{item}", min_value=0.0, format="%.2f")
                    p_vol = c2.number_input(f"Preço p/ Volume (R$)", key=f"v_{item}", min_value=0.0, format="%.2f")
                    obs_item = c3.text_input(f"Observação específica para {item}", key=f"o_{item}", placeholder="Ex: Lote mín. 50 un.")
                    
                    if p_uni > 0: # Apenas adiciona se houver valor preenchido
                        respostas_lista.append({
                            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Fornecedor": nome_fornecedor,
                            "Produto": item,
                            "Preco_Unitario": p_uni,
                            "Preco_Volume": p_vol,
                            "Condicao": condicao,
                            "Observacao": obs_item
                        })

            st.write("---")
            btn_enviar = st.form_submit_button("🚀 ENVIAR PROPOSTA PARA A NUVEM")

            if btn_enviar:
                if not nome_fornecedor:
                    st.error("⚠️ Identifique sua empresa antes de realizar o envio.")
                elif not respostas_lista:
                    st.warning("⚠️ Preencha os valores dos itens que deseja cotar.")
                else:
                    try:
                        # Conexão GSheets para escrita (Utiliza as credenciais dos Secrets)
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        df_novas = pd.DataFrame(respostas_lista)
                        
                        # Tenta anexar ao histórico existente na aba 'Respostas'
                        try:
                            historico = conn.read(worksheet="Respostas", ttl=0)
                            # Remove colunas totalmente vazias do histórico
                            historico = historico.dropna(how='all', axis=1)
                            df_final = pd.concat([historico, df_novas], ignore_index=True)
                        except:
                            df_final = df_novas
                        
                        # Escreve na planilha
                        conn.create(worksheet="Respostas", data=df_final)
                        st.balloons()
                        st.success(f"🛰️ TRANSMISSÃO CONCLUÍDA! Obrigado, {nome_fornecedor}. Seus dados foram blindados e enviados.")
                    except Exception as e:
                        if "PEM" in str(e) or "InvalidByte" in str(e):
                            st.error("❌ ERRO DE SEGURANÇA: A 'private_key' nos Secrets está incorreta. Verifique as aspas triplas.")
                        else:
                            st.error(f"❌ FALHA NA CENTRAL: Verifique se a aba 'Respostas' existe na planilha. Erro: {e}")

with aba_c:
    st.subheader("🛡️ Inteligência de Suprimentos")
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_analise = conn.read(worksheet="Respostas", ttl=5)
        
        if not df_analise.empty:
            # Tratamento: Forçar números para comparação
            df_analise['Preco_Unitario'] = pd.to_numeric(df_analise['Preco_Unitario'], errors='coerce')
            
            # Cálculo de Menor Preço (Ganhadores)
            idx_ganhadores = df_analise.groupby('Produto')['Preco_Unitario'].idxmin()
            df_winners = df_analise.loc[idx_ganhadores, ['Produto', 'Fornecedor', 'Preco_Unitario', 'Condicao']]
            
            # Dashboard Superior
            m1, m2, m3 = st.columns(3)
            m1.metric("Propostas Recebidas", len(df_analise))
            m2.metric("Itens com Oferta", len(df_winners))
            m3.metric("Status da Nuvem", "ATIVO", delta="Sincronizado")

            st.write("### 🏆 Ranking de Menores Preços por Item")
            st.dataframe(df_winners.sort_values(by='Preco_Unitario'), use_container_width=True)
            
            with st.expander("📂 Ver Todas as Respostas Recebidas"):
                st.dataframe(df_analise, use_container_width=True)
        else:
            st.info("Aguardando o recebimento da primeira proposta comercial para processar análise.")
    except:
        st.warning("A aba de análise será ativada assim que a primeira cotação for enviada com sucesso.")
