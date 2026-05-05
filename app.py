import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Seismic QC Dashboard", layout="wide")

# --- CONEXÃO COM O BANCO DE DADOS (Google Sheets) ---
# Nota: Você precisará configurar o link da planilha no Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl="5s") # Atualiza a cada 5 segundos

df_master = load_data()

# --- SIDEBAR: IDENTIFICAÇÃO E FILTROS ---
st.sidebar.header("1. Identificação")
user_name = st.sidebar.text_input("Nome do Analista")

st.sidebar.markdown("---")
st.sidebar.header("2. Filtros do Dashboard")
etapa_filtro = st.sidebar.selectbox("Filtrar por Etapa", df_master['Etapa'].unique())
status_filtro = st.sidebar.multiselect("Filtrar por Status", df_master['Status'].unique(), default=df_master['Status'].unique())

# Aplicar Filtros
df_filtered = df_master[(df_master['Etapa'] == etapa_filtro) & (df_master['Status'].isin(status_filtro))]

# --- MAIN PAGE: DASHBOARD ---
st.title(f"Painel de QC - {etapa_filtro}")

if not user_name:
    st.warning("👈 Digite seu nome na barra lateral para interagir com as sequências.")
    st.dataframe(df_filtered, use_container_width=True)
else:
    # Mostra a tabela interativa (estilo a sua imagem)
    st.write("Selecione uma sequência para iniciar ou ver detalhes:")
    
    # Criamos colunas para o cabeçalho da lista
    cols = st.columns([1, 2, 2, 2, 1])
    cols[0].bold("ACQSEQ")
    cols[1].bold("Status / Usuário")
    cols[2].bold("Itens Checados")
    cols[3].bold("Metadados")
    cols[4].bold("Ação")

    for i, row in df_filtered.iterrows():
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 2, 1])
            
            c1.write(row['ACQSEQ'])
            
            # Lógica de sinalização de "In Use"
            if row['Status'] == 'In Use':
                c2.error(f"🔴 Em uso por: {row['User']}")
            elif row['Status'] == 'Done':
                c2.success("🟢 Finalizado")
            else:
                c2.info("⚪ Disponível")

            c3.write(row['Checks_Done'])
            c4.write(f"{row['Info_1']} | {row['Info_2']}")
            
            # Botão para entrar na sequência
            if c5.button("Abrir", key=f"btn_{row['ACQSEQ']}"):
                st.session_state['selected_seq'] = row['ACQSEQ']
                # Aqui você dispararia a função de "Lock" no banco de dados
                st.info(f"Abrindo sequência {row['ACQSEQ']}...")

    # --- ÁREA DE EDIÇÃO (Aparece após clicar em Abrir) ---
    if 'selected_seq' in st.session_state:
        st.markdown("---")
        st.subheader(f"Editando Sequência: {st.session_state['selected_seq']}")
        
        # Aqui entra o formulário de checklist que criamos no prompt anterior
        # Ao salvar, o app deve dar um "UPDATE" na linha da planilha via conn.update()
        
        with st.form("qc_form"):
            st.write("Marque os itens vistos:")
            stack = st.checkbox("Stack")
            rms = st.checkbox("Mapa RMS")
            
            if st.form_submit_button("Salvar Alterações"):
                # Lógica para atualizar a planilha
                st.success("Dados enviados para o banco central!")
