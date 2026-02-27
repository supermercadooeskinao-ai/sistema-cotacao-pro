import streamlit as st
import pandas as pd
import time
import urllib.parse
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PRO-SUPPLY | Smart Analytics", layout="wide", page_icon="⚡")

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #e9ecef; border-radius: 8px 8px 0 0; padding: 10px 20px; color: #495057;
    }
    .stTabs [aria-selected="true"] { background-color: #58a6ff !important; color: white !important; }
    .product-card { 
        background-color: white; padding: 15px; border-radius: 10px; 
        border-left: 5px solid #58a6ff; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

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
st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>🛡️ PRO-SUPPLY <span style='color: #58a6ff;'>SMART ANALYTICS</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>Gestão Inteligente de Cotações e Pedidos</p>", unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["📩 PAINEL DO FORNECEDOR", "🔐 ÁREA DO CLIENTE", "📊 RELATÓRIO FINAL"])

df_google = carregar_dados_google()
itens_ativos = df_google[df_google['Selecionado'].notna()]['Produto'].tolist() if not df_google.empty else []

# --- ABA 1: FORNECEDOR ---
with aba_f:
    st.markdown("### 📋 Enviar Preços de Venda")
    if not itens_ativos:
        st.warning("⚠️ Nenhuma cotação ativa no momento. Aguarde o comprador liberar os itens.")
    else:
        with st.form("form_fornecedor"):
            col_inf1, col_inf2 = st.columns([2,1])
            nome_f = col_inf1.text_input("Nome da sua Empresa:", placeholder="Ex: Distribuidora Brasil")
            st.info(f"Faltam {len(itens_ativos)} itens para você cotar.")
            
            st.markdown("---")
            dados_preenchidos = {}
            
            # Criando uma visualização mais amigável para os itens
            for item in itens_ativos:
                with st.container():
                    st.markdown(f"""<div class='product-card'>📦 <b>{item}</b></div>""", unsafe_allow_html=True)
                    valor = st.number_input(f"Preço para {item}", min_value=0.0, step=0.01, key=f"f_{item}", label_visibility="collapsed")
                    if valor > 0: dados_preenchidos[item] = valor
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("✅ FINALIZAR COTAÇÃO")
            
            if submit:
                if nome_f and dados_preenchidos:
                    msg_wa = f"COTAÇÃO_{nome_f.upper()}\n"
                    for p, v in dados_preenchidos.items():
                        msg_wa += f"{p}: {v}\n"
                    link_final = f"https://wa.me/{TELEFONE_DESTINO}?text={urllib.parse.quote(msg_wa)}"
                    st.success("🎉 Tudo pronto! Clique no botão abaixo para enviar via WhatsApp.")
                    st.link_button("🟢 ENVIAR VIA WHATSAPP", link_final, use_container_width=True)
                else:
                    st.error("Preencha o nome da empresa e pelo menos um preço!")

# --- ABA 2: ÁREA DO CLIENTE ---
with aba_c:
    if not st.session_state.logado:
        c1, c2, c3 = st.columns([1,1,1])
        with c2:
            st.markdown("### 🔐 Acesso Restrito")
            senha = st.text_input("Chave de Licença:", type="password")
            if st.button("DESBLOQUEAR SISTEMA"):
                if senha == "PRO2026":
                    st.session_state.logado = True
                    st.rerun()
                else:
                    st.error("Chave inválida.")
    else:
        st.markdown("### 📥 Processar Respostas do WhatsApp")
        texto_copiado = st.text_area("Cole a mensagem recebida aqui:", height=200, placeholder="COTAÇÃO_EMPRESA...")
        
        col_btn1, col_btn2 = st.columns([1,1])
        if col_btn1.button("📥 ADICIONAR AO RELATÓRIO"):
            if texto_copiado:
                try:
                    linhas = [l for l in texto_copiado.split('\n') if l.strip()]
                    fornecedor = linhas[0].replace("COTAÇÃO_", "").strip()
                    novas_linhas = []
                    for l in linhas[1:]:
                        if ":" in l:
                            p, v = l.split(":")
                            novas_linhas.append({'Fornecedor': fornecedor.upper(), 'Produto': p.strip(), 'Preço': float(v.strip())})
                    st.session_state.base_analise = pd.concat([st.session_state.base_analise, pd.DataFrame(novas_linhas)], ignore_index=True)
                    st.success(f"✅ Fornecedor {fornecedor} adicionado com sucesso!")
                except: st.error("❌ Formato inválido! Verifique o texto copiado.")

# --- ABA 3: RELATÓRIO FINAL ---
with aba_r:
    if not st.session_state.logado:
        st.error("Faça login na aba 'Área do Cliente'.")
    elif st.session_state.base_analise.empty:
        st.info("Aguardando cotações dos fornecedores.")
    else:
        df_total = st.session_state.base_analise
        vencedores = df_total.loc[df_total.groupby('Produto')['Preço'].idxmin()]
        
        st.markdown("### 📊 Inteligência de Compras")
        
        # Filtro de Fornecedor com visual melhorado
        lista_fornecedores = sorted(vencedores['Fornecedor'].unique().tolist())
        selected_f = st.selectbox("🎯 Selecione o Fornecedor para visualizar o pedido:", lista_fornecedores)
        
        pedido_ind = vencedores[vencedores['Fornecedor'] == selected_f]
        
        # Métricas de resumo
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total do Pedido", f"R$ {pedido_ind['Preço'].sum():.2f}")
        with m2:
            st.metric("Itens Ganhos", len(pedido_ind))
        with m3:
            st.metric("Fornecedores Totais", df_total['Fornecedor'].nunique())

        st.markdown(f"#### Detalhes do Pedido: {selected_f}")
        st.dataframe(pedido_ind[['Produto', 'Preço']], use_container_width=True, hide_index=True)
        
        # Ações de exportação
        col_exp1, col_exp2 = st.columns([1,1])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pedido_ind.to_excel(writer, index=False, sheet_name='Pedido')
        
        col_exp1.download_button(
            label=f"📥 BAIXAR PLANILHA ({selected_f})",
            data=output.getvalue(),
            file_name=f"pedido_{selected_f}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        if col_exp2.button("🗑️ RESETAR TODAS AS COTAÇÕES"):
            st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
            st.rerun()

