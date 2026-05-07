import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import config_qc as cfg

# --- CONFIGURAÇÕES ---
# Substitua pelo seu ID e URL do Script
SHEET_ID = "SEU_ID_DA_PLANILHA_AQUI"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIIUSYeDX1XGIruyf1RUYpvOWAtSfjWllBXndWrYtO-qx4suXoqXycnMwLKuxrXdQ/exec"

st.set_page_config(page_title="Seismic QC Tool", layout="wide")

# --- CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=60)
def get_master_data():
    # Lendo o arquivo Excel diretamente (certifique-se de ter 'openpyxl' no requirements.txt)
    return pd.read_excel("master_sequences.xlsx")

def get_history():
    try:
        # Puxa o histórico da planilha do Google
        df = pd.read_csv(f"{GOOGLE_SHEET_URL}&cache={datetime.now().timestamp()}")
        # Garante que as colunas de ID sejam strings para comparação
        df['ACQSEQ'] = df['ACQSEQ'].astype(str)
        return df
    except:
        return pd.DataFrame(columns=["Data", "User", "ACQSEQ", "Etapa", "Checks"])

# Carregar dados
try:
    df_master = get_master_data()
    df_master['ACQSEQ'] = df_master['ACQSEQ'].astype(str)
except Exception as e:
    st.error(f"Erro ao carregar master_sequences.xlsx: {e}")
    st.stop()

df_history = get_history()

# --- INTERFACE LATERAL ---
st.sidebar.header("Configurações")
user = st.sidebar.text_input("Identifique-se", placeholder="Nome do Analista")
etapa_ativa = st.sidebar.selectbox("Etapa de QC", list(cfg.ETAPAS.keys()))

if not user:
    st.warning("Aguardando identificação do usuário...")
    st.stop()

# --- PROCESSAMENTO DA TABELA DE SEQUÊNCIAS ---
st.title(f"Monitoramento de Sequências - {etapa_ativa}")

# 1. Preparar informações obrigatórias
# Agrupamos o histórico para ver o que foi feito nesta etapa por sequência
hist_etapa = df_history[df_history['Etapa'] == etapa_ativa]
summary_history = hist_etapa.groupby('ACQSEQ')['Checks'].apply(lambda x: " | ".join(x)).reset_index()
summary_history.columns = ['ACQSEQ', 'Itens feitos nesta etapa']

# Criar DataFrame de exibição
df_display = df_master.copy()
df_display = df_display.merge(summary_history, on='ACQSEQ', how='left')

# Lógica "Em uso" (Exemplo: se houver qualquer registro no histórico geral)
em_uso_ids = df_history['ACQSEQ'].unique()
df_display['Em uso'] = df_display['ACQSEQ'].apply(lambda x: "Sim" if x in em_uso_ids else "Não")

# Renomear coluna obrigatória
df_display = df_display.rename(columns={'ACQSEQ': 'Sequência'})

# 2. Seleção Dinâmica de Colunas
cols_obrigatorias = ['Sequência', 'Em uso', 'Itens feitos nesta etapa']
todas_as_colunas = df_display.columns.tolist()
colunas_adicionais = [c for c in todas_as_colunas if c not in cols_obrigatorias]

with st.expander("⚙️ Configurar Colunas da Tabela"):
    colunas_escolhidas = st.multiselect(
        "Escolha colunas extras para visualizar:",
        options=colunas_adicionais,
        default=[]
    )

# Tabela Final filtrada pelas colunas escolhidas
colunas_finais = cols_obrigatorias + colunas_escolhidas
df_final = df_display[colunas_finais].fillna("-")

# Exibição da Tabela (Filtros nativos habilitados)
st.write("Dica: Use os ícones nas colunas para filtrar ou ordenar.")
st.dataframe(df_final, use_container_width=True, hide_index=True)

# --- SELEÇÃO PARA QC ---
st.markdown("---")
col_sel, _ = st.columns([1, 2])
with col_sel:
    seq_para_editar = st.selectbox(
        "Selecione uma sequência para iniciar o QC:",
        options=df_master['ACQSEQ'].unique(),
        index=None,
        placeholder="Escolha o ID da Sequência"
    )

if seq_para_editar:
    st.session_state['current_seq'] = seq_para_editar

# --- FORMULÁRIO DINÂMICO (Mantido da versão anterior) ---
if 'current_seq' in st.session_state:
    seq_id = st.session_state['current_seq']
    st.header(f"📝 Inserindo QC: {seq_id} ({etapa_ativa})")
    
    with st.form("form_qc"):
        item_tipo = st.selectbox("Tipo de Dado", cfg.ETAPAS[etapa_ativa])
        sub_itens = st.multiselect("O que foi identificado?", cfg.ITENS_CHECK.get(item_tipo, []))
        
        resultados = []
        for sub in sub_itens:
            st.markdown(f"**Detalhes de: {sub}**")
            attrs = cfg.CARACTERISTICAS.get(sub, ["Padrão"])
            c = st.columns(len(attrs))
            res_sub = []
            for i, attr in enumerate(attrs):
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
            try:
                requests.post(SCRIPT_URL, json=payload)
                st.success("QC Registrado com Sucesso!")
                del st.session_state['current_seq']
                st.rerun()
            except:
                st.error("Erro ao conectar com o Google Sheets.")
