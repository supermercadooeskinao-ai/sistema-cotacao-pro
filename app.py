import streamlit as st
import pandas as pd
import time
import urllib.parse
import re

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="PRO-SUPPLY | Smart Analytics", layout="wide")

URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"
TELEFONE_DESTINO = "5511999999999" 

def carregar_dados_google():
    try:
        url_dinamica = f"{URL_PLANILHA}?cache={int(time.time())}"
        df = pd.read_csv(url_dinamica)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Produto", "Selecionado"])

# Inicializa o banco de dados temporário para o Relatório
if 'base_analise' not in st.session_state:
    st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])

st.markdown("<h1 style='text-align: center;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["📩 FORNECEDOR", "🔐 ÁREA DO CLIENTE", "📊 RELATÓRIO FINAL"])

df_google = carregar_dados_google()
itens_para_cotar = df_google[df_google['Selecionado'].notna()]['Produto'].tolist() if not df_google.empty else []

# --- ABA 1: FORNECEDOR (Gera o texto formatado) ---
with aba_f:
    st.subheader("📩 Enviar Preços")
    if not itens_para_cotar:
        st.warning("Nenhum item selecionado para cotação.")
    else:
        with st.form("form_wa"):
            nome_f = st.text_input("Empresa Fornecedora:")
            dados = {}
            for item in itens_para_cotar:
                col1, col2 = st.columns([3, 1])
                col1.write(f"📦 {item}")
                v = col2.number_input(f"R$", min_value=0.0, step=0.01, key=f"f_{item}")
                if v > 0: dados[item] = v
            
            if st.form_submit_button("GERAR LINK WHATSAPP"):
                if nome_f and dados:
                    msg = f"COTAÇÃO_{nome_f}\n" # Tag para o sistema reconhecer
                    for p, v in dados.items():
                        msg += f"{p}: {v}\n"
                    link = f"https://wa.me/{TELEFONE_DESTINO}?text={urllib.parse.quote(msg)}"
                    st.success("Clique abaixo:")
                    st.link_button("🟢 ENVIAR VIA WHATSAPP", link)

# --- ABA 2: ÁREA DO CLIENTE (Onde a mágica acontece) ---
with aba_c:
    st.subheader("📥 Receber Cotações")
    st.write("Cole aqui o texto que você recebeu no WhatsApp para analisar:")
    texto_recebido = st.text_area("Cole a mensagem aqui:", height=150)
    
    if st.button("📥 PROCESSAR COTAÇÃO"):
        if texto_recebido:
            try:
                # Lógica para transformar o texto em dados de novo
                linhas = texto_recebido.split('\n')
                forn_nome = linhas[0].replace("COTAÇÃO_", "").strip()
                novos_dados = []
                for l in linhas[1:]:
                    if ":" in l:
                        p, v = l.split(":")
                        novos_dados.append({'Fornecedor': forn_nome, 'Produto': p.strip(), 'Preço': float(v.strip())})
                
                df_novos = pd.DataFrame(novos_dados)
                st.session_state.base_analise = pd.concat([st.session_state.base_analise, df_novos], ignore_index=True)
                st.success(f"Cotação de {forn_nome} adicionada ao relatório!")
            except:
                st.error("Formato de texto inválido. Cole a mensagem exatamente como veio do WhatsApp.")

# --- ABA 3: RELATÓRIO FINAL (Inteligência de Menor Preço) ---
with aba_r:
    st.subheader("📊 Comparativo e Vencedores")
    if st.session_state.base_analise.empty:
        st.info("Aguardando você processar as cotações na aba 'Área do Cliente'.")
    else:
        df_final = st.session_state.base_analise
        # Calcula o vencedor por produto
        vencedores = df_final.loc[df_final.groupby('Produto')['Preço'].idxmin()]
        
        st.write("### 🏆 Melhores Preços Encontrados:")
        st.dataframe(vencedores, use_container_width=True)
        
        if st.button("Limpar Relatório e Começar Novo"):
            st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
            st.rerun()

