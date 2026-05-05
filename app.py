import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURAÇÕES BÁSICAS ---
# Substitua pelo ID da sua planilha (ex: 1A2B3C4D...)
SHEET_ID = "COLE_AQUI_O_ID_DA_SUA_PLANILHA" 
# Seu link de implantação do Apps Script
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIIUSYeDX1XGIruyf1RUYpvOWAtSfjWllBXndWrYtO-qx4suXoqXycnMwLKuxrXdQ/exec"
CSV_URL = f"https://docs.google.com/spreadsheets/d/1fVZT7cZ1YYJdketX_zlpuL3L3dIED2nocyPlmRN9Mr0/export?format=csv"

st.set_page_config(page_title="QC Sísmico Dashboard", layout="wide")

# --- FUNÇÕES DE DADOS ---
def load_data():
    try:
        # Adicionamos um parâmetro de tempo para evitar cache do navegador
        return pd.read_csv(f"{CSV_URL}&cachebust={datetime.now().timestamp()}")
    except:
        st.error("Erro ao carregar a planilha. Verifique se o ID está correto e se o acesso é público.")
        return pd.DataFrame()

def save_to_google(acqseq, status, user, checks):
    payload = {
        "acqseq": str(acqseq),
        "status": status,
        "user": user,
        "checks": checks
    }
    try:
        response = requests.post(SCRIPT_URL, json=payload)
        return response.status_code == 200
    except:
        return False

# --- INTERFACE ---
st.title("🚜 Controle de Qualidade Sísmico")

# 1. Identificação na Sidebar
st.sidebar.header("Identificação")
user_name = st.sidebar.text_input("Nome do Analista", placeholder="Ex: Amanda")

if not user_name:
    st.info("👈 Por favor, identifique-se na barra lateral para começar.")
    st.stop()

# 2. Carregamento e Filtros
df = load_data()

if not df.empty:
    st.sidebar.markdown("---")
    st.sidebar.header("Filtros")
    etapa_opt = df['Etapa'].unique()
    etapa_sel = st.sidebar.selectbox("Selecionar Etapa", etapa_opt)
    
    # Dashboard Principal
    df_filt = df[df['Etapa'] == etapa_sel]
    
    st.subheader(f"Dashboard: {etapa_sel}")
    
    # Cabeçalho da Tabela
    h1, h2, h3, h4 = st.columns([1, 2, 3, 1])
    h1.bold("ACQSEQ")
    h2.bold("Status / Usuário")
    h3.bold("Itens Checados")
    h4.bold("Ação")
    st.markdown("---")

    for _, row in df_filt.iterrows():
        c1, c2, c3, c4 = st.columns([1, 2, 3, 1])
        
        c1.write(f"**{row['ACQSEQ']}**")
        
        # Lógica de cores para Status
        if row['Status'] == 'In Use':
            c2.error(f"🔴 Em uso por: {row['User']}")
        elif row['Status'] == 'Done':
            c2.success(f"🟢 Finalizado por: {row['User']}")
        else:
            c2.info("⚪ Disponível")
            
        c3.write(row['Checks_Done'] if pd.notna(row['Checks_Done']) else "-")
        
        if c4.button("Abrir", key=f"open_{row['ACQSEQ']}"):
            st.session_state['active_seq'] = row['ACQSEQ']
            # Opcional: Marcar como "In Use" automaticamente ao abrir
            save_to_google(row['ACQSEQ'], "In Use", user_name, row['Checks_Done'])
            st.rerun()

    # --- FORMULÁRIO DE QC (Aparece abaixo ao selecionar uma sequência) ---
    if 'active_seq' in st.session_state:
        seq_id = st.session_state['active_seq']
        st.markdown("---")
        st.header(f"📝 Editando Sequência: {seq_id}")
        
        with st.form("form_qc"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                itens = st.multiselect("Itens para conferência", ["Stack", "Shot", "Mapa RMS", "Gathers", "Velocidades"])
                intensidade = st.select_slider("Intensidade do achado", options=["N/A", "Baixa", "Média", "Alta"])
            
            with col_b:
                abrangencia = st.radio("Abrangência", ["Dado todo", "Pontos específicos", "N/A"], horizontal=True)
                obs = st.text_area("Observações Detalhadas")
                img = st.file_uploader("Upload de print/imagem", type=["png", "jpg"])

            # Botão de submissão do formulário
            if st.form_submit_button("Salvar e Finalizar QC"):
                res_str = f"{' | '.join(itens)} ({intensidade})"
                if save_to_google(seq_id, "Done", user_name, res_str):
                    st.success(f"QC da sequência {seq_id} salvo!")
                    del st.session_state['active_seq']
                    st.rerun()
                else:
                    st.error("Erro ao salvar. Verifique o Script.")

    if st.button("🔄 Atualizar Dashboard"):
        st.rerun()
else:
    st.warning("Aguardando dados da planilha...")
