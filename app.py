import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- SEGURANÇA COMERCIAL ---
CHAVE_ACESSO = "PRO2026"

if 'logado' not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.set_page_config(page_title="Ativação", page_icon="🔐")
    st.markdown("<h2 style='text-align: center;'>🔐 Ativação de Software</h2>", unsafe_allow_html=True)
    senha = st.text_input("Insira sua Chave de Licença:", type="password")
    if st.button("Ativar Sistema"):
        if senha == CHAVE_ACESSO:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Chave inválida.")
    st.stop()

# --- CONFIGURAÇÃO DO APP ---
st.set_page_config(page_title="PRO-SUPPLY | WhatsApp Edition", page_icon="⚡", layout="wide")

# Inicialização de Estados (Memória Temporária)
if 'historico_local' not in st.session_state:
    st.session_state.historico_local = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Data'])

st.markdown("<h1 style='text-align: center; color: #58a6ff;'>SISTEMA DE ANÁLISE WHATSAPP</h1>", unsafe_allow_html=True)

aba_c, aba_a = st.tabs(["📦 Preparar Itens", "📊 Analisar Respostas"])

with aba_c:
    st.subheader("1. Carregar Lista de Produtos")
    arquivo = st.file_uploader("Suba seu Excel (Coluna 'Produto')", type=['xlsx'])
    
    if arquivo:
        try:
            # O motor 'openpyxl' resolve o erro da sua captura de tela
            df_imp = pd.read_excel(arquivo, engine='openpyxl')
            
            if 'Produto' in df_imp.columns:
                lista_prods = sorted(df_imp['Produto'].dropna().unique().tolist())
                selecionados = st.multiselect("Selecione os itens para enviar ao fornecedor:", lista_prods)
                
                if selecionados:
                    st.write("### Texto para copiar e enviar:")
                    texto_zap = "Olá, segue cotação:\n\n"
                    for item in selecionados:
                        texto_zap += f"- {item}: R$ \n"
                    texto_zap += "\n*Por favor, preencha os valores e responda aqui.*"
                    
                    st.text_area("Copie o texto abaixo:", texto_zap, height=250)
                    st.info("💡 Dica: Cole no WhatsApp do fornecedor e aguarde a resposta dele.")
            else:
                st.error("Erro: O Excel precisa ter uma coluna chamada 'Produto'.")
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")

with aba_a:
    st.subheader("2. Colar Respostas e Comparar")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        f_nome = st.text_input("Nome do Fornecedor:")
        res_texto = st.text_area("Cole a mensagem do WhatsApp aqui:", height=300, help="Formato: Produto: R$ 0,00")
        
        if st.button("Processar Resposta"):
            if f_nome and res_texto:
                linhas = res_texto.split('\n')
                novos_dados = []
                for linha in linhas:
                    if ':' in linha and 'R$' in linha:
                        try:
                            item = linha.split(':')[0].replace('-', '').strip()
                            # Limpa o valor para converter em número
                            valor = linha.split('R$')[1].strip().replace('.', '').replace(',', '.')
                            novos_dados.append({
                                'Fornecedor': f_nome,
                                'Produto': item,
                                'Preço': float(valor),
                                'Data': datetime.now().strftime("%d/%m/%Y")
                            })
                        except: continue
                
                if novos_dados:
                    df_n = pd.DataFrame(novos_dados)
                    st.session_state.historico_local = pd.concat([st.session_state.historico_local, df_n], ignore_index=True)
                    st.success(f"Dados de {f_nome} salvos com sucesso!")
                else:
                    st.error("Não encontrei preços no texto. Verifique se tem 'Produto: R$ 00,00'")

    with c2:
        st.write("### 🏆 Melhores Preços Encontrados")
        if not st.session_state.historico_local.empty:
            df_res = st.session_state.historico_local
            # Pega o menor preço para cada produto
            venc = df_res.loc[df_res.groupby('Produto')['Preço'].idxmin()]
            st.dataframe(venc[['Produto', 'Fornecedor', 'Preço']], use_container_width=True)
            
            total_economia = df_res.groupby('Produto')['Preço'].max().sum() - venc['Preço'].sum()
            st.metric("Economia Estimada", f"R$ {total_economia:.2f}")
        else:
            st.info("Cole os dados ao lado para ver a análise.")

if not st.session_state.historico_local.empty:
    st.write("---")
    if st.button("Limpar Histórico e Nova Cotação"):
        st.session_state.historico_local = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Data'])
        st.rerun()
