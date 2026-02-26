import streamlit as st
import pandas as pd
import time
import urllib.parse

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="PRO-SUPPLY | Smart Analytics", layout="wide", page_icon="⚡")

# --- CONFIGURAÇÕES DO USUÁRIO ---
# Cole aqui o link que você gerou em 'Publicar na Web' como CSV
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS3Extm7GnoMba57gboYO9Lb6s-mUUh10pQF0bH_Wu2Xffq6UfKnAf4iAjxROAtC_iAC2vEM0rYLf9p/pub?output=csv"
# Coloque o telefone que vai receber as cotações (DDI + DDD + Numero)
TELEFONE_DESTINO = "5574988391826" 

# --- 2. FUNÇÕES DE DADOS ---
def carregar_dados_google():
    try:
        # Adiciona um timestamp para evitar que o Google entregue uma versão antiga (cache)
        url_com_cache = f"{URL_PLANILHA}&cache={int(time.time())}"
        df = pd.read_csv(url_com_cache)
        
        # Padroniza os nomes das colunas: remove espaços e coloca a primeira letra em maiúsculo
        df.columns = [c.strip().capitalize() for c in df.columns]
        return df
    except Exception as e:
        return pd.DataFrame(columns=["Produto", "Selecionado"])

# Inicializa o banco de dados de análise na sessão do Cliente
if 'base_analise' not in st.session_state:
    st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- 3. INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #58a6ff;'>PRO-SUPPLY SMART ANALYTICS</h1>", unsafe_allow_html=True)

aba_f, aba_c, aba_r = st.tabs(["📩 PAINEL DO FORNECEDOR", "🔐 ÁREA DO CLIENTE", "📊 RELATÓRIO FINAL"])

# Carregamento global dos dados para todas as abas
df_google = carregar_dados_google()

# Filtra itens que possuem qualquer marcação na coluna 'Selecionado'
itens_ativos = []
if not df_google.empty and 'Selecionado' in df_google.columns:
    itens_ativos = df_google[df_google['Selecionado'].notna()]['Produto'].tolist()

# --- ABA 1: FORNECEDOR ---
with aba_f:
    st.subheader("📩 Enviar Preços de Cotação")
    
    if not itens_ativos:
        st.warning("⚠️ Nenhuma cotação ativa no momento. Aguarde o comprador liberar os itens na planilha.")
    else:
        with st.form("form_fornecedor"):
            nome_f = st.text_input("Nome da sua Empresa:")
            st.info(f"Itens liberados para hoje: {len(itens_ativos)}")
            
            dados_preenchidos = {}
            for item in itens_ativos:
                col1, col2 = st.columns([3, 1])
                col1.write(f"📦 **{item}**")
                valor = col2.number_input(f"Preço R$", min_value=0.0, step=0.01, key=f"f_{item}")
                if valor > 0:
                    dados_preenchidos[item] = valor
            
            st.markdown("---")
            if st.form_submit_button("GERAR COTAÇÃO PARA WHATSAPP"):
                if nome_f and dados_preenchidos:
                    # Monta a mensagem formatada para o sistema ler depois
                    msg_wa = f"COTAÇÃO_{nome_f}\n"
                    for p, v in dados_preenchidos.items():
                        msg_wa += f"{p}: {v}\n"
                    
                    # Gera o link do WhatsApp
                    link_final = f"https://wa.me/{TELEFONE_DESTINO}?text={urllib.parse.quote(msg_wa)}"
                    
                    st.success("✅ Cotação preparada com sucesso!")
                    st.link_button("🟢 ENVIAR VIA WHATSAPP", link_final, use_container_width=True)
                else:
                    st.error("Por favor, preencha o nome da empresa e ao menos um preço.")

# --- ABA 2: ÁREA DO CLIENTE ---
with aba_c:
    if not st.session_state.logado:
        senha = st.text_input("Chave de Acesso:", type="password")
        if st.button("Entrar"):
            if senha == "PRO2026":
                st.session_state.logado = True
                st.rerun()
    else:
        st.subheader("📥 Processar Respostas do WhatsApp")
        st.write("Copie a mensagem recebida no WhatsApp e cole abaixo para analisar:")
        
        texto_copiado = st.text_area("Cole aqui o texto da cotação:", height=150, placeholder="COTAÇÃO_Empresa...")
        
        if st.button("📥 ADICIONAR AO RELATÓRIO"):
            if texto_copiado:
                try:
                    linhas = texto_copiado.split('\n')
                    fornecedor = linhas[0].replace("COTAÇÃO_", "").strip()
                    novas_linhas = []
                    for l in linhas[1:]:
                        if ":" in l:
                            prod_nome, preco_val = l.split(":")
                            novas_linhas.append({
                                'Fornecedor': fornecedor, 
                                'Produto': prod_nome.strip(), 
                                'Preço': float(preco_val.strip())
                            })
                    
                    df_temp = pd.DataFrame(novas_linhas)
                    st.session_state.base_analise = pd.concat([st.session_state.base_analise, df_temp], ignore_index=True)
                    st.success(f"Dados de '{fornecedor}' processados!")
                except:
                    st.error("Erro ao ler o texto. Verifique se copiou a mensagem inteira.")

# --- ABA 3: RELATÓRIO FINAL ---
with aba_r:
    if not st.session_state.logado:
        st.error("Acesso restrito.")
    elif st.session_state.base_analise.empty:
        st.info("Aguardando o processamento de cotações na aba anterior.")
    else:
        st.subheader("📊 Comparativo de Menores Preços")
        df_final = st.session_state.base_analise
        
        # Lógica de Menor Preço
        idx_min = df_final.groupby('Produto')['Preço'].idxmin()
        vencedores = df_final.loc[idx_min].sort_values(by='Fornecedor')
        
        st.dataframe(vencedores, use_container_width=True)
        
        if st.button("🗑️ Limpar Tudo e Nova Cotação"):
            st.session_state.base_analise = pd.DataFrame(columns=['Fornecedor', 'Produto', 'Preço'])
            st.rerun()


