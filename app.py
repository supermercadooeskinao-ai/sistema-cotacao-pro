import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="PRO-SUPPLY | Cotação Seletiva", layout="wide")

# SUBSTISTUA PELO SEU LINK DO GOOGLE PUBLICADO COMO CSV
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"

def carregar_dados_google():
    try:
        df = pd.read_csv(URL_PLANILHA)
        # Limpar espaços em branco dos nomes das colunas
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Produto", "Selecionado"])

# --- 2. ESTADO DO SISTEMA ---
if 'logado' not in st.session_state: st.session_state.logado = False
if 'historico' not in st.session_state: 
    st.session_state.historico = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])

st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["📩 PAINEL DO FORNECEDOR", "🔐 ÁREA DO CLIENTE", "📊 RELATÓRIO FINAL"])

# Carregar dados do Google
df_google = carregar_dados_google()

# Filtrar apenas os produtos que o cliente marcou com algo na coluna 'Selecionado'
# O .notna() verifica se a célula não está vazia
itens_para_cotar = []
if not df_google.empty and 'Selecionado' in df_google.columns:
    itens_para_cotar = df_google[df_google['Selecionado'].notna()]['Produto'].tolist()

# --- ABA 1: FORNECEDOR (VÊ APENAS O QUE FOI FILTRADO) ---
with aba_f:
    st.subheader("📩 Preencher Cotação Atual")
    
    if not itens_para_cotar:
        st.warning("⚠️ No momento não há itens liberados para cotação. Aguarde o comprador.")
    else:
        with st.form("form_fornecedor"):
            nome_forn = st.text_input("Nome da sua Empresa:")
            st.write(f"Você tem {len(itens_para_cotar)} itens para cotar hoje:")
            
            temp_precos = []
            for item in itens_para_cotar:
                col1, col2 = st.columns([3, 1])
                col1.write(f"📦 **{item}**")
                valor = col2.number_input(f"Preço R$", min_value=0.0, step=0.01, key=f"f_{item}")
                if valor > 0:
                    temp_precos.append({'Fornecedor': nome_forn, 'Produto': item, 'Preço': valor})
            
            if st.form_submit_button("ENVIAR COTAÇÃO"):
                if nome_forn and temp_precos:
                    st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame(temp_precos)], ignore_index=True)
                    st.success("✅ Enviado com sucesso!")
                else:
                    st.error("Preencha o nome e os preços.")

# --- ABA 2: ÁREA DO CLIENTE ---
with aba_c:
    if not st.session_state.logado:
        senha = st.text_input("Chave de Acesso:", type="password")
        if st.button("Entrar"):
            if senha == "PRO2026":
                st.session_state.logado = True
                st.rerun()
    else:
        st.success("Conectado ao Gerenciador Google")
        st.write("### 📝 Lista Geral de Produtos")
        st.write("Para escolher o que o fornecedor vê, coloque um 'X' na coluna **Selecionado** da sua planilha Google.")
        st.dataframe(df_google, use_container_width=True)
        
        st.write("### 🎯 Itens que o Fornecedor está vendo agora:")
        st.info(itens_para_cotar if itens_para_cotar else "Nenhum item selecionado na planilha.")
        
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

# --- ABA 3: RELATÓRIO ---
with aba_r:
    if not st.session_state.logado:
        st.error("Acesso restrito.")
    elif st.session_state.historico.empty:
        st.info("Aguardando fornecedores...")
    else:
        st.subheader("📊 Menor Preço por Item")
        df_total = st.session_state.historico
        vencedores = df_total.loc[df_total.groupby('Produto')['Preço'].idxmin()]
        st.dataframe(vencedores, use_container_width=True)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            vencedores.to_excel(writer, index=False)
        st.download_button("📥 Baixar Pedido", output.getvalue(), "pedido_final.xlsx")


