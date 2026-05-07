import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import config_qc as cfg

# --- CONFIGURAÇÕES ---
SHEET_ID = "SEU_ID_DA_PLANILHA_AQUI"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIIUSYeDX1XGIruyf1RUYpvOWAtSfjWllBXndWrYtO-qx4suXoqXycnMwLKuxrXdQ/exec"

st.set_page_config(page_title="Seismic QC Tool", layout="wide")

# --- CARREGAMENTO E LIMPEZA DE DADOS ---
@st.cache_data(ttl=60)
def get_master_data():
    # Lê o Excel
    df = pd.read_excel("master_sequences.xlsx")
    
    # 1. Remove linhas onde a sequência está vazia
    df = df.dropna(subset=['ACQSEQ'])
    
    # 2. Converte para número inteiro (remove o .0) e depois para string
    df['ACQSEQ'] = df['ACQSEQ'].astype(int).astype(str)
    
    return df

def get_history():
    try:
        df = pd.read_csv(f"{GOOGLE_SHEET_URL}&cache={datetime.now().timestamp()}")
        df['ACQSEQ'] = df['ACQSEQ'].astype(str)
        return df
    except:
        return pd.DataFrame(columns=["Data", "User", "ACQSEQ", "Etapa", "Checks"])

# Tentar carregar os dados
try:
    df_master = get_master_data()
except Exception as e:
    st.error(f"Erro ao carregar master_sequences.xlsx: {e}")
    st.stop()

df_history = get_history()

# --- INTERFACE LATERAL ---
st.sidebar.header("Configurações")
user = st.sidebar.text_input("Identifique-se", placeholder="Nome do Analista")
etapa_ativa = st.sidebar.selectbox("Etapa de QC", list(cfg.ETAPAS.keys()))

if not user:
    st.warning("Por favor, identifique-se na lateral para continuar.")
    st.stop()

# --- MONITORAMENTO DE SEQUÊNCIAS ---
st.title(f"Monitoramento de Sequências - {etapa_ativa}")

# Preparar dados para a tabela
hist_etapa = df_history[df_history['Etapa'] == etapa_ativa]
summary_history = hist_etapa.groupby('ACQSEQ')['Checks'].apply(lambda x: " | ".join(x)).reset_index()
summary_history.columns = ['ACQSEQ', 'Itens feitos nesta etapa']

df_display = df_master.copy()
df_display = df_display.merge(summary_history, on='ACQSEQ', how='left')

em_uso_ids = df_history['ACQSEQ'].unique()
df_display['Em uso'] = df_display['ACQSEQ'].apply(lambda x: "Sim" if x in em_uso_ids else "Não")
df_display = df_display.rename(columns={'ACQSEQ': 'Sequência'})

# Configuração de Colunas
cols_obrigatorias = ['Sequência', 'Em uso', 'Itens feitos nesta etapa']
colunas_adicionais = [c for c in df_display.columns if c not in cols_obrigatorias]

with st.expander("⚙️ Configurar Colunas Extras"):
    colunas_escolhidas = st.multiselect("Adicionar dados técnicos:", options=colunas_adicionais)

colunas_finais = cols_obrigatorias + colunas_escolhidas
df_final = df_display[colunas_finais].fillna("-")

# --- TABELA COM SELEÇÃO DE LINHA ---
st.info("Clique em uma linha para selecionar a sequência e abrir o formulário de QC.")

# O parâmetro on_select="rerun" e selection_mode="single_row" permite capturar o clique
event = st.dataframe(
    df_final,
    use_container_width=True,
    hide_index=True,
    selection_mode="single_row",
    on_select="rerun"
)

# Verifica se o usuário selecionou alguma linha
if len(event.selection.rows) > 0:
    selected_index = event.selection.rows[0]
    # Busca o valor da 'Sequência' na linha clicada
    st.session_state['current_seq'] = df_final.iloc[selected_index]['Sequência']

# --- FORMULÁRIO DE QC ---
if 'current_seq' in st.session_state:
    seq_id = st.session_state['current_seq']
    st.markdown("---")
    st.header(f"📝 Formulário de QC: Sequência {seq_id}")
    st.subheader(f"Etapa: {etapa_ativa}")

    with st.form("form_qc"):
        item_tipo = st.selectbox("Tipo de Dado", cfg.ETAPAS[etapa_ativa])
        sub_itens = st.multiselect("Identificações encontradas:", cfg.ITENS_CHECK.get(item_tipo, []))
        
        resultados = []
        for sub in sub_itens:
            st.write(f"---")
            st.markdown(f"**Detalhes de: {sub}**")
            attrs = cfg.CARACTERISTICAS.get(sub, ["Padrão"])
            cols = st.columns(len(attrs))
            
            res_sub = []
            for i, attr in enumerate(attrs):
                opcoes = cfg.OPCOES.get(attr)
                if opcoes:
                    val = cols[i].selectbox(attr, opcoes, key=f"form_{seq_id}_{sub}_{attr}")
                else:
                    val = cols[i].text_input(attr, key=f"form_{seq_id}_{sub}_{attr}")
                res_sub.append(f"{attr}: {val}")
            resultados.append(f"[{sub}: {', '.join(res_sub)}]")

        st.write("---")
        obs = st.text_area("Observações Gerais / Justificativas")
        
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            submit = st.form_submit_button("💾 Salvar QC")
        with col_btn2:
            if st.form_submit_button("❌ Cancelar"):
                del st.session_state['current_seq']
                st.rerun()

        if submit:
            final_checks = " | ".join(resultados) + (f" | Obs: {obs}" if obs else "")
            payload = {
                "acqseq": str(seq_id),
                "status": "Done",
                "user": user,
                "checks": f"[{etapa_ativa}] {final_checks}"
            }
            try:
                requests.post(SCRIPT_URL, json=payload)
                st.success(f"QC da Sequência {seq_id} salvo com sucesso!")
                del st.session_state['current_seq']
                st.rerun()
            except:
                st.error("Erro ao enviar dados para a planilha. Verifique sua conexão.")
