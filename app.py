import streamlit as st
import pandas as pd
import time
import urllib.parse
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PRO-SUPPLY | Smart Analytics", layout="wide", page_icon="⚡")

# --- CONFIGURAÇÕES DO USUÁRIO ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"
TELEFONE_DESTINO = "5574988391826" 

# --- 2. FUNÇÕES DE DADOS ---
def carregar_dados_google():
    try:
        url_com_cache = f"{URL_PLANILHA}&cache={int(time.time())}"
        df = pd.read_csv(url_com_cache)
        df.columns = [c.strip().capitalize() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Produto", "Selecionado"])

if 'base_analise' not in st.session_state:
    st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- 3. INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["📩 PAINEL DO FORNECEDOR", "🔐 ÁREA DO CLIENTE", "📊 RELATÓRIO FINAL"])

df_google = carregar_dados_google()
itens_ativos = df_google[df_google['Selecionado'].notna()]['Produto'].tolist() if not df_google.empty else []

# --- ABA 1: FORNECEDOR ---
with aba_f:
    st.subheader("📩 Enviar Preços")
    if not itens_ativos:
        st.warning("⚠️ Nenhuma cotação ativa no momento.")
    else:
        with st.form("form_fornecedor"):
            nome_f = st.text_input("Nome da sua Empresa:")
            dados_preenchidos = {}
            for item in itens_ativos:
                col1, col2 = st.columns([3, 1])
                col1.write(f"📦 **{item}**")
                valor = col2.number_input(f"Preço R$", min_value=0.0, step=0.01, key=f"f_{item}")
                if valor > 0: dados_preenchidos[item] = valor
            
            if st.form_submit_button("GERAR COTAÇÃO PARA WHATSAPP"):
                if nome_f and dados_preenchidos:
                    msg_wa = f"COTAÇÃO_{nome_f}\n"
                    for p, v in dados_preenchidos.items():
                        msg_wa += f"{p}: {v}\n"
                    link_final = f"https://wa.me/{TELEFONE_DESTINO}?text={urllib.parse.quote(msg_wa)}"
                    st.success("✅ Cotação preparada!")
                    st.link_button("🟢 ENVIAR VIA WHATSAPP", link_final, use_container_width=True)

# --- ABA 2: ÁREA DO CLIENTE ---
with aba_c:
    if not st.session_state.logado:
        senha = st.text_input("Chave de Acesso:", type="password")
        if st.button("Entrar"):
            if senha == "PRO2026":
                st.session_state.logado = True
                st.rerun()
    else:
        st.subheader("📥 Processar Respostas")
        texto_copiado = st.text_area("Cole a mensagem do WhatsApp aqui:", height=150)
        if st.button("📥 ADICIONAR AO RELATÓRIO"):
            if texto_copiado:
                try:
                    linhas = texto_copiado.split('\n')
                    fornecedor = linhas[0].replace("COTAÇÃO_", "").strip()
                    novas_linhas = []
                    for l in linhas[1:]:
                        if ":" in l:
                            p, v = l.split(":")
                            novas_linhas.append({'Fornecedor': fornecedor, 'Produto': p.strip(), 'Preço': float(v.strip())})
                    st.session_state.base_analise = pd.concat([st.session_state.base_analise, pd.DataFrame(novas_linhas)], ignore_index=True)
                    st.success(f"Dados de '{fornecedor}' adicionados!")
                except: st.error("Erro no formato do texto.")

# --- ABA 3: RELATÓRIO FINAL (AGORA COM FILTRO INDIVIDUAL) ---
with aba_r:
    if not st.session_state.logado:
        st.error("Acesso restrito.")
    elif st.session_state.base_analise.empty:
        st.info("Aguardando cotações...")
    else:
        # 1. CÁLCULO GERAL DOS VENCEDORES
        df_total = st.session_state.base_analise
        vencedores = df_total.loc[df_total.groupby('Produto')['Preço'].idxmin()]
        
        st.subheader("📊 Relatório de Compras por Fornecedor")
        
        # 2. FILTRO INDIVIDUAL
        lista_fornecedores = vencedores['Fornecedor'].unique().tolist()
        forn_selecionado = st.selectbox("🎯 Selecione o Fornecedor para ver o pedido individual:", lista_fornecedores)
        
        # Filtra apenas o que este fornecedor ganhou
        pedido_individual = vencedores[vencedores['Fornecedor'] == forn_selecionado]
        
        st.write(f"### Pedido para: **{forn_selecionado}**")
        st.table(pedido_individual[['Produto', 'Preço']])
        
        total_pedido = pedido_individual['Preço'].sum()
        st.metric("Total do Pedido", f"R$ {total_pedido:.2f}")

        # 3. EXPORTAÇÃO EXCEL INDIVIDUAL
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pedido_individual.to_excel(writer, index=False, sheet_name='Pedido')
        st.download_button(
            label=f"📥 Baixar Planilha para {forn_selecionado}",
            data=output.getvalue(),
            file_name=f"pedido_{forn_selecionado}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.divider()
        if st.button("🗑️ Limpar Tudo"):
            st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
            st.rerun()
