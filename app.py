import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="PRO-SUPPLY Cloud", layout="wide")

st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

# Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. CARREGAMENTO DE DADOS ---
# Lê a aba 'Produtos' para o fornecedor ver o que cotar
df_produtos = conn.read(worksheet="Produtos")
# Lê a aba 'Respostas' para o cliente ver quem ganhou
df_respostas = conn.read(worksheet="Respostas")

# Filtra itens ativos (coluna Selecionado com 'X')
itens_ativos = df_produtos[df_produtos['Selecionado'].notna()]['Produto'].tolist()

aba_f, aba_c = st.tabs(["📩 PAINEL DO FORNECEDOR", "📊 ÁREA DO CLIENTE (Relatórios)"])

# --- ABA 1: FORNECEDOR (GRAVA DIRETO NO GOOGLE) ---
with aba_f:
    st.subheader("📩 Enviar Cotação")
    if not itens_ativos:
        st.warning("Aguardando liberação de produtos.")
    else:
        with st.form("form_direto"):
            nome_f = st.text_input("Empresa Fornecedora:")
            
            temp_list = []
            for item in itens_ativos:
                c1, c2 = st.columns([3, 1])
                c1.write(f"📦 **{item}**")
                v = c2.number_input(f"Preço R$", min_value=0.0, step=0.01, key=f"f_{item}")
                if v > 0:
                    temp_list.append({"Fornecedor": nome_f, "Produto": item, "Preço": v})
            
            if st.form_submit_button("ENVIAR COTAÇÃO AGORA"):
                if nome_f and temp_list:
                    # Adiciona os novos dados ao que já existe na aba 'Respostas'
                    df_atualizado = pd.concat([df_respostas, pd.DataFrame(temp_list)], ignore_index=True)
                    conn.update(worksheet="Respostas", data=df_atualizado)
                    st.success("✅ Preços enviados e salvos no sistema!")
                    st.balloons()

# --- ABA 2: ÁREA DO CLIENTE (RELATÓRIOS INDIVIDUAIS) ---
with aba_c:
    st.subheader("🔐 Painel de Resultados")
    senha = st.text_input("Senha:", type="password")
    
    if senha == "PRO2026":
        if df_respostas.empty:
            st.info("Nenhuma resposta recebida ainda.")
        else:
            # 1. CÁLCULO DE VENCEDORES
            idx_min = df_respostas.groupby('Produto')['Preço'].idxmin()
            vencedores = df_respostas.loc[idx_min]
            
            st.write("### 🏆 Itens por Fornecedor Ganhador")
            
            # 2. FILTRO E RELATÓRIO INDIVIDUAL
            fornecedores_ganhadores = vencedores['Fornecedor'].unique().tolist()
            forn = st.selectbox("Selecione o Fornecedor para ver o Pedido:", fornecedores_ganhadores)
            
            pedido = vencedores[vencedores['Fornecedor'] == forn]
            st.table(pedido[['Produto', 'Preço']])
            
            st.metric("Total do Pedido", f"R$ {pedido['Preço'].sum():.2f}")
            
            # Exportação
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pedido.to_excel(writer, index=False)
            st.download_button(f"📥 Baixar Pedido: {forn}", output.getvalue(), f"pedido_{forn}.xlsx")
            
            if st.button("🗑️ Resetar Todas as Cotações"):
                conn.update(worksheet="Respostas", data=pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço']))
                st.rerun()
