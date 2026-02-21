import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import io

st.set_page_config(page_title="PRO-SUPPLY Cloud", layout="wide")
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_prod = conn.read(worksheet="Produtos")
    df_resp = conn.read(worksheet="Respostas")
except Exception as e:
    st.error("Erro ao carregar os dados da planilha. Verifique os Secrets.")
    st.stop()

aba_f, aba_c = st.tabs(["📩 PORTAL DO FORNECEDOR", "📊 ÁREA DO CLIENTe"])

with aba_f:
    st.subheader("📩 Enviar Cotação")
    if not itens_ativos:
        st.warning("Nenhum item selecionado para cotação na planilha.")
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
                    df_novo = pd.concat([df_resp, pd.DataFrame(lista_dados)], ignore_index=True)
                    conn.update(worksheet="Respostas", data=df_novo)
                    st.success("✅ Cotação salva com sucesso!")
                    st.balloons()

with aba_c:
    st.subheader("🔐 Gestão de Pedidos")
    senha = st.text_input("Senha:", type="password")
    if senha == "PRO2026":
        if df_resp.empty:
            st.info("Aguardando respostas.")
        else:
            idx = df_resp.groupby('Produto')['Preço'].idxmin()
            vencedores = df_resp.loc[idx]
            fornecedores = vencedores['Fornecedor'].unique().tolist()
            escolha = st.selectbox("Fornecedor:", fornecedores)
            pedido = vencedores[vencedores['Fornecedor'] == escolha]
            st.table(pedido[['Produto', 'Preço']])
            st.metric("Total", f"R$ {pedido['Preço'].sum():.2f}")
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                pedido.to_excel(writer, index=False)
            st.download_button(f"📥 Baixar Pedido {escolha}", buf.getvalue(), f"pedido_{escolha}.xlsx")


