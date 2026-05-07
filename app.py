import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import config_qc as cfg

# --- CONFIGURAÇÕES ---
SHEET_ID = "SEU_ID_AQUI"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIIUSYeDX1XGIruyf1RUYpvOWAtSfjWllBXndWrYtO-qx4suXoqXycnMwLKuxrXdQ/exec"

st.set_page_config(page_title="Seismic QC Tool", layout="wide")

# --- CARREGAMENTO E LIMPEZA ---
@st.cache_data(ttl=60)
def get_master_data():
    df = pd.read_excel("master_sequences.xlsx")
    
    # Limpeza profunda da sequência
    # 1. Converte para numérico, transformando erros em NaN
    df['ACQSEQ'] = pd.to_numeric(df['ACQSEQ'], errors='coerce')
    # 2. Remove linhas onde a sequência é nula ou vazia
    df = df.dropna(subset=['ACQSEQ'])
    # 3. Converte para inteiro (tira o .0) e depois para texto
    df['ACQSEQ'] = df['ACQSEQ'].astype(int).astype(str)
    
    return df

def get_history():
    try:
        df = pd.read_csv(f"{GOOGLE_SHEET_URL}&cache={datetime.now().timestamp()}")
        # Garante que a coluna de comparação seja string
        df['ACQSEQ'] = df['ACQSEQ'].astype(str)
        return df
    except:
        return pd.DataFrame(columns=["Data", "User", "ACQSEQ", "Etapa", "Checks"])

# Carregar dados
df_master = get_master_data()
df_history = get_history()

# --- INTERFACE ---
st.sidebar.header("Identificação")
user = st.sidebar.text_input("Seu Nome")
etapa_ativa = st.sidebar.selectbox("Etapa de QC", list(cfg.ETAPAS.keys()))

if not user:
    st.warning("👈 Digite seu nome na lateral para começar.")
    st.stop()

st.title(f"Monitoramento: {etapa_ativa}")

# Preparar Tabela
hist_etapa = df_history[df_history['Etapa'] == etapa_ativa]
summary_history = hist_etapa.groupby('ACQSEQ')['Checks'].apply(lambda x: " | ".join(x)).reset_index()
summary_history.columns = ['ACQSEQ', 'Itens feitos']

df_display = df_master.copy()
df_display = df_display.merge(summary_history, on='ACQSEQ', how='left')

# Marcar se está em uso (independente da etapa)
em_uso_ids = df_history['ACQSEQ'].unique()
df_display['Em uso'] = df_display['ACQSEQ'].apply(lambda x: "Sim" if x in em_uso_ids else "Não")

# Ajuste de colunas
df_display = df_display.rename(columns={'ACQSEQ': 'Sequência'})
cols_base = ['Sequência', 'Em uso', 'Itens feitos']
extras = st.multiselect("Colunas Adicionais:", [c for c in df_display.columns if c not in cols_base])

df_final = df_display[cols_base + extras].fillna("-")

# --- TABELA COM SELEÇÃO (Requer Streamlit 1.35.0+) ---
st.markdown("### Selecione uma linha para abrir o formulário")

# Captura o evento de seleção
event = st.dataframe(
    df_final,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single_row"
)

# Lógica de seleção
if event.selection.rows:
    idx = event.selection.rows[0]
    st.session_state['current_seq'] = df_final.iloc[idx]['Sequência']

# --- FORMULÁRIO ---
if 'current_seq' in st.session_state:
    seq_id = st.session_state['current_seq']
    st.divider()
    st.subheader(f"📝 Formulário de QC: {seq_id}")
    
    with st.form("form_qc"):
        item_tipo = st.selectbox("Tipo de Dado", cfg.ETAPAS[etapa_ativa])
        sub_itens = st.multiselect("Identificações:", cfg.ITENS_CHECK.get(item_tipo, []))
        
        repostas_form = []
        for sub in sub_itens:
            st.markdown(f"**{sub}**")
            attrs = cfg.CARACTERISTICAS.get(sub, ["Padrão"])
            cols = st.columns(len(attrs))
            
            res_sub = []
            for i, attr in enumerate(attrs):
                opcoes = cfg.OPCOES.get(attr)
                key = f"{seq_id}_{sub}_{attr}"
                val = cols[i].selectbox(attr, opcoes, key=key) if opcoes else cols[i].text_input(attr, key=key)
                res_sub.append(f"{attr}: {val}")
            repostas_form.append(f"[{sub} -> {', '.join(res_sub)}]")

        obs = st.text_area("Notas Gerais")
        
        c1, c2 = st.columns([1, 4])
        if c1.form_submit_button("Salvar"):
            payload = {
                "acqseq": str(seq_id),
                "status": "Done",
                "user": user,
                "checks": f"[{etapa_ativa}] {' | '.join(repostas_form)} | Obs: {obs}"
            }
            requests.post(SCRIPT_URL, json=payload)
            st.success("Salvo!")
            del st.session_state['current_seq']
            st.rerun()
            
        if c2.form_submit_button("Cancelar"):
            del st.session_state['current_seq']
            st.rerun()
