import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import config_qc as cfg

# --- CONFIGURAÇÕES ---
SHEET_ID = "1fVZT7cZ1YYJdketX_zlpuL3L3dIED2nocyPlmRN9Mr0"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/1fVZT7cZ1YYJdketX_zlpuL3L3dIED2nocyPlmRN9Mr0/export?format=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIIUSYeDX1XGIruyf1RUYpvOWAtSfjWllBXndWrYtO-qx4suXoqXycnMwLKuxrXdQ/exec"

st.set_page_config(page_title="Seismic QC Tool", layout="wide")

# --- CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=60)
def get_master_data():
    return pd.read_csv("20260320_pdb.xlsx - PandDaXlsx.csv")

def get_history():
    try:
        return pd.read_csv(f"{GOOGLE_SHEET_URL}&cache={datetime.now().timestamp()}")
    except:
        return pd.DataFrame(columns=["Data", "User", "ACQSEQ", "Etapa", "Checks"])

df_master = get_master_data()
df_history = get_history()

# --- INTERFACE ---
st.sidebar.header("Usuário")
user = st.sidebar.text_input("Identifique-se")

if not user:
    st.warning("Por favor, digite seu nome na lateral.")
    st.stop()

etapa_ativa = st.sidebar.selectbox("Etapa de QC", list(cfg.ETAPAS.keys()))

# Dashboard
st.subheader(f"Sequências - {etapa_ativa}")
projeto = st.sidebar.selectbox("Projeto", df_master['PROJECT'].unique())
df_view = df_master[df_master['PROJECT'] == projeto]

for _, row in df_view.iterrows():
    seq = row['ACQSEQ']
    cols = st.columns([1, 2, 1])
    cols[0].write(f"**{seq}**")
    
    # Verifica se já existe QC para esta sequência E etapa
    has_qc = not df_history[(df_history['ACQSEQ'] == str(seq)) & (df_history['Etapa'] == etapa_ativa)].empty
    cols[1].write("✅ Concluído" if has_qc else "⚪ Pendente")
    
    if cols[2].button("Abrir", key=f"btn_{seq}"):
        st.session_state['current_seq'] = seq
        st.rerun()

# --- FORMULÁRIO DINÂMICO ---
if 'current_seq' in st.session_state:
    seq_id = st.session_state['current_seq']
    st.markdown("---")
    st.header(f"Inserindo QC: {seq_id} ({etapa_ativa})")
    
    with st.form("form_qc"):
        item_tipo = st.selectbox("Tipo de Dado", cfg.ETAPAS[etapa_ativa])
        sub_itens = st.multiselect("O que foi identificado?", cfg.ITENS_CHECK.get(item_tipo, []))
        
        resultados = []
        
        # Loop dinâmico: para cada sub-item selecionado, cria os inputs do config
        for sub in sub_itens:
            st.markdown(f"**Detalhes de: {sub}**")
            attrs = cfg.CARACTERISTICAS.get(sub, ["Padrão"])
            c = st.columns(len(attrs))
            
            res_sub = []
            for i, attr in enumerate(attrs):
                # Busca as opções no dicionário OPCOES, se não houver usa campo de texto
                opcoes = cfg.OPCOES.get(attr)
                if opcoes:
                    val = c[i].selectbox(attr, opcoes, key=f"{seq_id}_{sub}_{attr}")
                else:
                    val = c[i].text_input(attr, key=f"{seq_id}_{sub}_{attr}")
                res_sub.append(f"{attr}: {val}")
            
            resultados.append(f"[{sub} -> {', '.join(res_sub)}]")

        obs = st.text_area("Observações Gerais")
        
        if st.form_submit_button("Salvar na Planilha"):
            final_checks = " | ".join(resultados) + f" | Obs: {obs}"
            payload = {
                "acqseq": str(seq_id),
                "status": "Done",
                "user": user,
                "checks": f"[{etapa_ativa}] {final_checks}"
            }
            requests.post(SCRIPT_URL, json=payload)
            st.success("QC Registrado!")
            del st.session_state['current_seq']
            st.rerun()
