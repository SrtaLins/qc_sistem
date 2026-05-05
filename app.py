import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import config_qc as cfg # Importa suas configurações

# --- CONFIGURAÇÕES ---
# 1. ID da Planilha para LEITURA (Precisa estar pública "Qualquer um com link")
SHEET_ID = "SEU_ID_AQUI"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# 2. URL do Script para ESCRITA (O que você já criou)
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIIUSYeDX1XGIruyf1RUYpvOWAtSfjWllBXndWrYtO-qx4suXoqXycnMwLKuxrXdQ/exec"

st.set_page_config(page_title="Seismic QC Tool", layout="wide")

# --- CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=60)
def get_master_data():
    # Lê o CSV que está na mesma pasta do GitHub
    return pd.read_csv("20260320_pdb.xlsx - PandDaXlsx.csv")

def get_history():
    try:
        return pd.read_csv(f"{GOOGLE_SHEET_URL}&cache={datetime.now().timestamp()}")
    except:
        return pd.DataFrame(columns=["Data", "User", "ACQSEQ", "Etapa", "Item", "Obs"])

df_master = get_master_data()
df_history = get_history()

# --- INTERFACE ---
st.title("🛠 Ferramenta de QC Sísmico")

# Lateral: Usuário e Filtros
st.sidebar.header("Usuário")
user = st.sidebar.text_input("Identifique-se")

if not user:
    st.warning("Por favor, digite seu nome.")
    st.stop()

st.sidebar.header("Filtros")
projeto = st.sidebar.selectbox("Projeto", df_master['PROJECT'].unique())
etapa_ativa = st.sidebar.selectbox("Etapa de QC", list(cfg.ETAPAS.keys()))

# --- DASHBOARD DE SEQUÊNCIAS ---
# Cruzamos o Master com o Histórico para ver o que já foi feito
st.subheader(f"Status das Sequências - {etapa_ativa}")

# Filtrar master por projeto
df_view = df_master[df_master['PROJECT'] == projeto].copy()

cols = st.columns([1, 2, 2, 1])
cols[0].bold("ACQSEQ")
cols[1].bold("Status")
cols[2].bold("Último QC nesta etapa")
cols[3].bold("Ação")

for _, row in df_view.iterrows():
    seq = row['ACQSEQ']
    # Busca no histórico se essa sequência já tem QC nesta etapa
    last_qc = df_history[(df_history['ACQSEQ'] == seq) & (df_history['Etapa'] == etapa_ativa)].last_valid_index()
    
    with st.container():
        c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
        c1.write(seq)
        
        if last_qc is not None:
            c2.success("✅ Concluído")
            c3.write(f"Por: {df_history.loc[last_qc, 'User']}")
        else:
            c2.info("⚪ Pendente")
            c3.write("-")
            
        if c4.button("Abrir QC", key=f"btn_{seq}"):
            st.session_state['current_seq'] = seq
            st.rerun()

# --- FORMULÁRIO DE QC ---
if 'current_seq' in st.session_state:
    seq_id = st.session_state['current_seq']
    st.markdown("---")
    st.header(f"Inserindo QC: Sequência {seq_id}")
    
    # Mostrar histórico prévio da sequência (O que outros viram)
    with st.expander("Ver histórico desta sequência"):
        hist_seq = df_history[df_history['ACQSEQ'] == seq_id]
        st.table(hist_seq[['Data', 'Etapa', 'Item', 'User']])

    with st.form("form_detalhado"):
        item_tipo = st.selectbox("O que você está olhando?", cfg.ETAPAS[etapa_ativa])
        coisa_vista = st.multiselect("O que foi identificado?", cfg.ITENS_CHECK.get(item_tipo, ["Outros"]))
        
        col1, col2 = st.columns(2)
        with col1:
            intns = st.select_slider("Intensidade", cfg.CARACTERISTICAS["Intensidade"])
        with col2:
            abrang = st.radio("Abrangência", cfg.CARACTERISTICAS["Abrangência"])
            
        coment = st.text_area("Observações adicionais")
        
        if st.form_submit_button("Salvar na Planilha"):
            # Lógica para enviar ao Google Sheets (JSON para o seu Script)
            payload = {
                "acqseq": str(seq_id),
                "status": "Done",
                "user": user,
                "checks": f"{item_tipo}: {', '.join(coisa_vista)} | {intns} | {abrang}"
            }
            requests.post(SCRIPT_URL, json=payload)
            st.success("Salvo com sucesso!")
            del st.session_state['current_seq']
            st.rerun()
