import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import config_qc as cfg

# --- CONFIGURAÇÕES ---
SHEET_ID = "SEU_ID_DA_PLANILHA"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIIUSYeDX1XGIruyf1RUYpvOWAtSfjWllBXndWrYtO-qx4suXoqXycnMwLKuxrXdQ/exec"

st.set_page_config(page_title="Seismic QC Tool", layout="wide")

# --- CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=60)
def get_master_data():
    df = pd.read_excel("master_sequences.xlsx")
    df = df.dropna(subset=['ACQSEQ'])
    df['ACQSEQ'] = pd.to_numeric(df['ACQSEQ']).astype(int).astype(str)
    return df

def get_history():
    try:
        df = pd.read_csv(f"{GOOGLE_SHEET_URL}&cache={datetime.now().timestamp()}")
        df['ACQSEQ'] = df['ACQSEQ'].astype(str)
        return df
    except:
        return pd.DataFrame(columns=["Data", "User", "ACQSEQ", "Etapa", "Checks"])

df_master = get_master_data()
df_history = get_history()

# --- INTERFACE LATERAL ---
st.sidebar.header("Identificação")
user = st.sidebar.text_input("Nome do Analista")
etapa_ativa = st.sidebar.selectbox("Etapa de QC", list(cfg.ETAPAS.keys()))

if not user:
    st.warning("Identifique-se na lateral para liberar o sistema.")
    st.stop()

# --- TABELA DE MONITORAMENTO ---
st.title(f"Monitoramento - {etapa_ativa}")

hist_etapa = df_history[df_history['Etapa'] == etapa_ativa]
summary_history = hist_etapa.groupby('ACQSEQ')['Checks'].apply(lambda x: " | ".join(x)).reset_index()
summary_history.columns = ['ACQSEQ', 'Itens feitos']

df_display = df_master.copy()
df_display = df_display.merge(summary_history, on='ACQSEQ', how='left')
df_display['Em uso'] = df_display['ACQSEQ'].apply(lambda x: "Sim" if x in df_history['ACQSEQ'].unique() else "Não")
df_display = df_display.rename(columns={'ACQSEQ': 'Sequência'})

cols_base = ['Sequência', 'Em uso', 'Itens feitos']
extras = st.multiselect("Ver colunas extras:", [c for c in df_display.columns if c not in cols_base])
df_final = df_display[cols_base + extras].fillna("-")

event = st.dataframe(
    df_final, 
    use_container_width=True, 
    hide_index=True, 
    on_select="rerun", 
    selection_mode="single-row"
)

if event.selection.rows:
    st.session_state['current_seq'] = df_final.iloc[event.selection.rows[0]]['Sequência']

# --- FORMULÁRIO DE QC (ESTILO IMAGEM) ---
if 'current_seq' in st.session_state:
    seq_id = st.session_state['current_seq']
    st.markdown("---")
    st.subheader(f"📝 QC da Sequência: {seq_id}")

    # 1. Listagem de Tipos (Usando Pills como na imagem)
    tipos_disponiveis = cfg.ETAPAS[etapa_ativa] + ["Observação"]
    tipo_selecionado = st.pills("Selecione o Tipo de Dado:", tipos_disponiveis, default=tipos_disponiveis[0])

    with st.form("form_qc_detalhes"):
        detalhes_qc = []
        
        # Caso seja um tipo técnico (RotShot, Stack, etc)
        if tipo_selecionado != "Observação":
            itens = st.multiselect(f"O que foi visto em {tipo_selecionado}?", cfg.ITENS_CHECK.get(tipo_selecionado, []))
            
            for item in itens:
                st.markdown(f"**Configuração de {item}:**")
                caracteristicas = cfg.CARACTERISTICAS.get(item, [])
                
                # Criar colunas para os atributos
                if caracteristicas:
                    cols = st.columns(len(caracteristicas))
                    res_item = []
                    for i, (attr) in enumerate(caracteristicas):
                        opcoes = ["-"] + cfg.OPCOES.get(attr, []) # Adiciona "-" para ser opcional
                        escolha = cols[i].selectbox(attr, opcoes, key=f"{seq_id}_{item}_{attr}")
                        if escolha != "-":
                            res_item.append(f"{attr}: {escolha}")
                    
                    if res_item:
                        detalhes_qc.append(f"{item} ({', '.join(res_item)})")
                    else:
                        detalhes_qc.append(item)
                else:
                    detalhes_qc.append(item)
            
            st.write("---")
            obs_tipo = st.text_input(f"Observação específica para {tipo_selecionado}")
            if obs_tipo:
                detalhes_qc.append(f"Obs_{tipo_selecionado}: {obs_tipo}")

        # Caso seja apenas Observação Geral
        else:
            obs_geral = st.text_area("Escreva aqui as observações gerais da sequência:")
            if obs_geral:
                detalhes_qc.append(f"OBS GERAL: {obs_geral}")

        # Botões de ação
        c1, c2 = st.columns([1, 4])
        if c1.form_submit_button("💾 Salvar"):
            if detalhes_qc:
                payload = {
                    "acqseq": str(seq_id),
                    "status": "Done",
                    "user": user,
                    "checks": f"[{etapa_ativa}][{tipo_selecionado}] " + " | ".join(detalhes_qc)
                }
                requests.post(SCRIPT_URL, json=payload)
                st.success("QC salvo com sucesso!")
                del st.session_state['current_seq']
                st.rerun()
            else:
                st.warning("Nenhuma informação selecionada para salvar.")
                
        if c2.form_submit_button("❌ Cancelar"):
            del st.session_state['current_seq']
            st.rerun()
