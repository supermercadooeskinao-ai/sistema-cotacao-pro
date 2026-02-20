import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PRO-SUPPLY Cloud Business", layout="wide", page_icon="🏢")

st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

# 1. CONEXÃO COM O GOOGLE SHEETS
# Esta função gerencia a segurança e a comunicação com a sua planilha
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lendo as duas abas da sua planilha
    df_produtos = conn.read(worksheet="Produtos")
    df_respostas = conn.read(worksheet="Respostas")
    
    # Itens que o cliente marcou com 'X' na coluna Selecionado
    itens_ativos = df_produtos[df_produtos['Selecionado'].notna()]['Produto'].tolist()
except Exception as e:
    st.error("Erro de conexão. Verifique se as abas 'Produtos' e 'Respostas' existem na sua planilha.")
    st.stop()

aba_f, aba_c = st.tabs(["📩 PORTAL DO FORNECEDOR", "🔐 PAINEL ESTRATÉGICO (Cliente)"])

# --- ABA 1: FORNECEDOR (ENVIO DIRETO) ---
with aba_f:
    st.subheader("📩 Envio de Cotação Online")
    if not itens_ativos:
        st.warning("Nenhuma cotação aberta no momento.")
    else:
        with st.form("form_venda"):
            nome_f = st.text_input("Empresa Fornecedora:")
            
            lista_preenchida = []
            for item in itens_ativos:
                c1, c2 = st.columns([3, 1])
                c1.write(f"📦 **{item}**")
                v = c2.number_input(f"R$", min_value=0.0, step=0.01, key=f"v_{item}")
                if v > 0:
                    lista_preenchida.append({"Fornecedor": nome_f, "Produto": item, "Preço": v})
            
            if st.form_submit_button("CONFIRMAR E ENVIAR PREÇOS"):
                if nome_f and lista_preenchida:
                    # O sistema pega o que já tinha na planilha e soma com o novo envio
                    df_final = pd.concat([df_respostas, pd.DataFrame(lista_preenchida)], ignore_index=True)
                    conn.update(worksheet="Respostas", data=df_final)
                    st.success("✅ Cotação enviada direto para o comprador!")
                    st.balloons()

# --- ABA 2: CLIENTE (ANÁLISE E PEDIDOS INDIVIDUAIS) ---
with aba_c:
    st.subheader("📊 Gestão de Compras")
    senha = st.text_input("Acesso Restrito:", type="password")
    
    if senha == "PRO2026":
        if df_respostas.empty:
            st.info("Aguardando o primeiro fornecedor enviar preços.")
        else:
            # Lógica para achar o menor preço de cada produto
            idx_vencedores = df_respostas.groupby('Produto')['Preço'].idxmin()
            vencedores = df_respostas.loc[idx_vencedores]
            
            st.write("### 🏆 Análise de Ganhadores")
            
            # Relatório Individual por Fornecedor
            todos_fornecedores = vencedores['Fornecedor'].unique().tolist()
            selecionado = st.selectbox("Filtrar pedido por fornecedor:", todos_fornecedores)
            
            pedido_forn = vencedores[vencedores['Fornecedor'] == selecionado]
            
            st.markdown(f"**Pedido para: {selecionado}**")
            st.table(pedido_forn[['Produto', 'Preço']])
            
            total = pedido_forn['Preço'].sum()
            st.metric("Valor Total do Pedido", f"R$ {total:.2f}")

            # Botão para baixar a planilha só desse fornecedor
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                pedido_forn.to_excel(writer, index=False)
            st.download_button(f"📥 Baixar Pedido {selecionado}", buffer.getvalue(), f"pedido_{selecionado}.xlsx")
            
            st.divider()
            if st.button("🗑️ Resetar Sistema (Apagar todas as respostas)"):
                conn.update(worksheet="Respostas", data=pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço']))
                st.rerun()
