import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="PRO-SUPPLY Diagnóstico", layout="wide")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 1. TESTE DE CONEXÃO PURA
    st.write("### 🧪 Teste de Diagnóstico")
    
    # Vamos tentar ler a aba "Produtos" especificamente de novo
    # Se falhar, tentamos ler sem aba
    try:
        df_prod = conn.read(worksheet="Produtos", ttl=0)
        st.success("✅ Aba 'Produtos' encontrada e lida!")
    except:
        df_prod = conn.read(ttl=0)
        st.warning("⚠️ Aba 'Produtos' não achada. Lendo a primeira aba disponível.")

    # 2. MOSTRAR O QUE FOI LIDO
    if df_prod.empty:
        st.error("❌ A planilha foi lida, mas retornou VAZIA (0 linhas e 0 colunas).")
        st.info(f"Verifique se o ID nos Secrets é este mesmo: `{st.secrets['connections']['gsheets']['spreadsheet']}`")
    else:
        st.write("📊 **Dados encontrados:**")
        st.dataframe(df_prod)
        
        # Tenta achar os itens com 'x'
        df_prod.columns = [str(c).strip().lower() for c in df_prod.columns]
        col_p = [c for c in df_prod.columns if 'produto' in c]
        col_s = [c for c in df_prod.columns if 'selecionado' in c]
        
        if col_p and col_s:
            itens = df_prod[df_prod[col_s[0]].astype(str).str.lower().str.strip() == 'x'][col_p[0]].tolist()
            st.write(f"✅ Itens com 'x' identificados: {itens}")

except Exception as e:
    st.error(f"Erro crítico: {e}")

