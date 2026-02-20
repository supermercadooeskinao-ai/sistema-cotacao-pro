import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io

# Configuração da Página
st.set_page_config(page_title="PRO-SUPPLY Cloud", layout="wide")

st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

# Conectar ao Google Sheets usando os Secrets configurados
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Lendo as abas da planilha
    df_prod = conn.read(worksheet="Produtos")
    df_resp = conn.read(worksheet="Respostas")
    
    # Padronizar colunas para evitar erros
    df_prod.columns = [c.strip().capitalize() for c in df_prod.columns]
    
    itens_ativos = df_prod[df_prod['Selecionado'].notna()]['Produto'].tolist()
except Exception as e:
    st.error("Erro ao conectar com a planilha. Verifique se as abas 'Produtos' e 'Respostas' existem e se os Secrets estão corretos.")
    st.stop()

aba_f, aba_c = st.tabs(["📩 PORTAL DO FORNECEDOR", "📊 ÁREA DO CLIENTE"])

# --- ABA FORNECEDOR ---
with aba_f:
    st.subheader("📩 Enviar Cotação")
    if not itens_ativos:
        st.warning("Nenhuma cotação aberta no momento.")
    else:
        with st.form("form_envio"):
            nome_f = st.text_input("Empresa Fornecedora:")
            lista_dados = []
            
            for item in itens_ativos:
                c1, c2 = st.columns([3, 1])
                c1.write(f"📦 **{item}**")
                v = c2.number_input(f"Preço R$", min_value=0.0, step=0.01, key=f"f_{item}")
                if v > 0:
                    lista_dados.append({"Fornecedor": nome_f, "Produto": item, "Preço": v})
            
            if st.form_submit_button("ENVIAR PARA O SISTEMA"):
                if nome_f and lista_dados:
                    # Atualiza a planilha do Google Sheets em tempo real
                    df_novo = pd.concat([df_resp, pd.DataFrame(lista_dados)], ignore_index=True)
                    conn.update(worksheet="Respostas", data=df_novo)
                    st.success("✅ Cotação salva com sucesso!")
                    st.balloons()

# --- ABA CLIENTE ---
with aba_c:
    st.subheader("🔐 Gestão de Pedidos")
    senha = st.text_input("Senha de Comprador:", type="password")
    
    if senha == "PRO2026":
        if df_resp.empty:
            st.info("Nenhuma resposta recebida ainda.")
        else:
            # Lógica dos Ganhadores
            idx = df_resp.groupby('Produto')['Preço'].idxmin()
            vencedores = df_resp.loc[idx]
            
            fornecedores = vencedores['Fornecedor'].unique().tolist()
            escolha = st.selectbox("Selecione o Fornecedor para ver o Pedido:", fornecedores)
            
            pedido = vencedores[vencedores['Fornecedor'] == escolha]
            st.table(pedido[['Produto', 'Preço']])
            st.metric("Total", f"R$ {pedido['Preço'].sum():.2f}")
            
            # Download do pedido individual
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                pedido.to_excel(writer, index=False)
            st.download_button(f"📥 Baixar Pedido {escolha}", buf.getvalue(), f"pedido_{escolha}.xlsx")
