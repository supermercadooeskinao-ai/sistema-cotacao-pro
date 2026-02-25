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

# Inicialização de Estados
if 'historico_local' not in st.session_state:
    st.session_state.historico_local = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Obs'])

st.markdown("<h1 style='text-align: center; color: #58a6ff;'>SISTEMA DE ANÁLISE WHATSAPP</h1>", unsafe_allow_html=True)

aba_c, aba_a = st.tabs(["📦 Preparar Itens", "📊 Analisar Respostas"])

with aba_c:
    st.subheader("1. Carregar Lista de Produtos")
    arquivo = st.file_uploader("Suba seu Excel (Coluna 'Produto')", type=['xlsx'])
    
    if arquivo:
        df_imp = pd.read_excel(arquivo)
        if 'Produto' in df_imp.columns:
            lista_prods = sorted(df_imp['Produto'].dropna().unique().tolist())
            selecionados = st.multiselect("Selecione os itens para enviar ao fornecedor:", lista_prods)
            
            if selecionados:
                st.write("### Texto para copiar e enviar:")
                texto_zap = "Olá, seguem itens para cotação:\n\n"
                for item in selecionados:
                    texto_zap += f"- {item}: R$ \n"
                texto_zap += "\n*Por favor, preencha os valores e me envie de volta.*"
                
                st.text_area("Copie o texto abaixo:", texto_zap, height=200)
                st.info("💡 Envie esse texto para o WhatsApp do fornecedor.")
        else:
            st.error("O Excel precisa ter uma coluna chamada 'Produto'")

with aba_a:
    st.subheader("2. Colar Respostas do Fornecedor")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        forn_nome = st.text_input("Nome do Fornecedor que respondeu:")
        res_texto = st.text_area("Cole aqui a mensagem vinda do WhatsApp:", height=300, placeholder="Ex: - Arroz: R$ 25.00...")
        
        if st.button("Processar e Salvar"):
            if forn_nome and res_texto:
                # Lógica simples de leitura de texto
                linhas = res_texto.split('\n')
                novos_dados = []
                for linha in linhas:
                    if ':' in linha and 'R$' in linha:
                        try:
                            item_parte = linha.split(':')[0].replace('-', '').strip()
                            preco_parte = linha.split('R$')[1].strip().replace(',', '.')
                            novos_dados.append({
                                'Fornecedor': forn_nome,
                                'Produto': item_parte,
                                'Preço': float(preco_parte),
                                'Data': datetime.now().strftime("%d/%m/%Y")
                            })
                        except:
                            continue
                
                if novos_dados:
                    df_novo = pd.DataFrame(novos_dados)
                    st.session_state.historico_local = pd.concat([st.session_state.historico_local, df_novo], ignore_index=True)
                    st.success(f"Dados de {forn_nome} processados!")
                else:
                    st.error("Não consegui identificar preços no texto. Use o formato 'Produto: R$ 0.00'")

    with col2:
        st.write("### Comparativo de Preços")
        if not st.session_state.historico_local.empty:
            df_res = st.session_state.historico_local
            # Mostra o menor preço por produto
            vencedores = df_res.loc[df_res.groupby('Produto')['Preço'].idxmin()]
            st.dataframe(vencedores, use_container_width=True)
            
            # Botão para limpar tudo e começar nova rodada
            if st.button("Limpar Tudo"):
                st.session_state.historico_local = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço', 'Obs'])
                st.rerun()
        else:
            st.info("Aguardando colagem de dados...")

    if not st.session_state.historico_local.empty:
        st.write("---")
        st.subheader("📋 Histórico Geral")
        st.table(st.session_state.historico_local)
