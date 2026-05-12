import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import config_qc as cfg
    
# --- CONFIGURAÇÕES ---
SHEET_ID = "1fVZT7cZ1YYJdketX_zlpuL3L3dIED2nocyPlmRN9Mr0"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/1fVZT7cZ1YYJdketX_zlpuL3L3dIED2nocyPlmRN9Mr0/export?format=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIIUSYeDX1XGIruyf1RUYpvOWAtSfjWllBXndWrYtO-qx4suXoqXycnMwLKuxrXdQ/exec"

# Opções de atributos padrão caso não existam no config_qc.py
OPCOES_PADRAO = {
    "Intensidade": ["Baixa", "Média", "Alta"],
    "Frequência": ["Baixa", "Média", "Alta"],
    "Abrangência": ["Pontual", "Localizada", "Espalhada", "Dado Todo"],
    "Qualidade": ["Excelente", "Boa", "Regular", "Ruim"]
}

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
        df['Sequencia'] = df['Sequencia'].astype(str)
        return df
    except:
        return pd.DataFrame(columns=["Data_Hora", "Analista", "Sequencia", "Etapa", "Tipo_Dado", "Item_Detectado", "Caracteristica", "Valor"])

df_master = get_master_data()
df_history = get_history()

# --- INTERFACE LATERAL ---
st.sidebar.header("Identificação")
user = st.sidebar.text_input("Nome do Analista", key="user_name")
etapa_ativa = st.sidebar.selectbox("Etapa de QC", list(cfg.ETAPAS.keys()))

if not user:
    st.warning("👈 Identifique-se na lateral para começar.")
    st.stop()

# --- PROCESSAMENTO DO HISTÓRICO PARA A TABELA ---
st.title(f"Monitoramento - {etapa_ativa}")

hist_etapa = df_history[df_history['Etapa'] == etapa_ativa]

if not hist_etapa.empty:
    # Reconstrói uma string amigável para mostrar na tabela o que já foi feito
    def format_row(row):
        carac, val = row['Caracteristica'], row['Valor']
        if carac == "Status":
            return f"{row['Tipo_Dado']}: {row['Item_Detectado']}"
        elif carac == "Observação":
            return f"{row['Tipo_Dado']}: {val}"
        else:
            return f"{row['Tipo_Dado']}: {row['Item_Detectado']} ({carac}={val})"
            
    hist_etapa = hist_etapa.copy()
    hist_etapa['Descritivo'] = hist_etapa.apply(format_row, axis=1)
    summary_history = hist_etapa.groupby('Sequencia')['Descritivo'].apply(lambda x: " | ".join(x.unique())).reset_index()
    summary_history.columns = ['Sequencia', 'Itens feitos']
else:
    summary_history = pd.DataFrame(columns=['Sequencia', 'Itens feitos'])

df_display = df_master.copy()
df_display = df_display.merge(summary_history, left_on='ACQSEQ', right_on='Sequencia', how='left').drop(columns=['Sequencia'], errors='ignore')
df_display['Em uso'] = df_display['ACQSEQ'].apply(lambda x: "Sim" if x in df_history['Sequencia'].unique() else "Não")
df_display = df_display.rename(columns={'ACQSEQ': 'Sequência'})

cols_base = ['Sequência', 'Em uso', 'Itens feitos']
extras = st.multiselect("Ver colunas extras:", [c for c in df_display.columns if c not in cols_base])
df_final = df_display[cols_base + extras].fillna("-")

# Tabela Interativa
event = st.dataframe(
    df_final, 
    use_container_width=True, 
    hide_index=True, 
    on_select="rerun", 
    selection_mode="single-row"
)

if event.selection.rows:
    st.session_state['current_seq'] = df_final.iloc[event.selection.rows[0]]['Sequência']

# --- FORMULÁRIO DE QC DINÂMICO E REATIVO ---
if 'current_seq' in st.session_state:
    seq_id = st.session_state['current_seq']
    st.markdown("---")
    st.subheader(f"📝 QC da Sequência: {seq_id}")

    # 1. Seleção do Tipo (PILLS)
    tipos_disponiveis = cfg.ETAPAS[etapa_ativa] + ["Observação"]
    tipo_selecionado = st.pills("Tipo de Dado:", tipos_disponiveis, selection_mode="single", default=tipos_disponiveis[0])

    # Lista onde guardaremos cada linha que vai para a planilha
    linhas_para_salvar = []

    if tipo_selecionado == "Observação":
        obs_geral = st.text_area("Escreva aqui as observações gerais da sequência:", key="obs_geral")
        if obs_geral:
            linhas_para_salvar.append({
                "analista": user,
                "sequencia": str(seq_id),
                "etapa": etapa_ativa,
                "tipo_dado": "Observação",
                "item_detectado": "Geral",
                "caracteristica": "Observação",
                "valor": obs_geral
            })
    else:
        # Multiselect Reativo
        itens_vistos = st.multiselect(
            f"O que foi visto em {tipo_selecionado}?", 
            cfg.ITENS_CHECK.get(tipo_selecionado, []),
            key=f"ms_{tipo_selecionado}"
        )
        
        st.write("---")
        obs_tipo = st.text_input(f"Observação específica para {tipo_selecionado}", key="obs_especifica")
        
        # Se houver observação do tipo, cria uma linha para ela
        if obs_tipo:
            linhas_para_salvar.append({
                "analista": user,
                "sequencia": str(seq_id),
                "etapa": etapa_ativa,
                "tipo_dado": tipo_selecionado,
                "item_detectado": "Geral",
                "caracteristica": "Observação",
                "valor": obs_tipo
            })

        # Processar as características de cada item dinamicamente
        for item in itens_vistos:
            st.markdown(f"**Configuração de {item}:**")
            caracteristicas = cfg.CARACTERISTICAS.get(item, [])
            
            if caracteristicas:
                cols = st.columns(len(caracteristicas))
                algum_atributo_selecionado = False
                
                for i, attr in enumerate(caracteristicas):
                    # Procura as opções no config ou usa o padrão
                    opcoes_originais = getattr(cfg, "OPCOES", {}).get(attr) or OPCOES_PADRAO.get(attr, [])
                    opcoes = ["-"] + opcoes_originais
                    
                    escolha = cols[i].selectbox(attr, opcoes, key=f"attr_{seq_id}_{item}_{attr}")
                    if escolha != "-":
                        algum_atributo_selecionado = True
                        linhas_para_salvar.append({
                            "analista": user,
                            "sequencia": str(seq_id),
                            "etapa": etapa_ativa,
                            "tipo_dado": tipo_selecionado,
                            "item_detectado": item,
                            "caracteristica": attr,
                            "valor": escolha
                        })
                
                # Se marcou o item mas não detalhou características, salva apenas a presença
                if not algum_atributo_selecionado:
                    linhas_para_salvar.append({
                        "analista": user,
                        "sequencia": str(seq_id),
                        "etapa": etapa_ativa,
                        "tipo_dado": tipo_selecionado,
                        "item_detectado": item,
                        "caracteristica": "Status",
                        "valor": "Identificado"
                    })
            else:
                # Se o item não tiver características cadastradas (ex: Shot Morto)
                linhas_para_salvar.append({
                    "analista": user,
                    "sequencia": str(seq_id),
                    "etapa": etapa_ativa,
                    "tipo_dado": tipo_selecionado,
                    "item_detectado": item,
                    "caracteristica": "Status",
                    "valor": "Identificado"
                })

    # Botões de Ação
    col_save, col_cancel = st.columns([1, 5])

    # --- EXIBIÇÃO DE FEEDBACK APÓS RERUN ---
    if 'sucesso_qc' in st.session_state:
        st.success(st.session_state['sucesso_qc'])
        del st.session_state['sucesso_qc']
    
    if col_save.button("💾 Salvar QC"):
            if linhas_para_salvar:
                with st.spinner("Enviando dados para o Google..."):
                    try:
                        res = requests.post(SCRIPT_URL, json=linhas_para_salvar, timeout=10)
                        
                        if res.status_code == 200:
                            # Verifica se o Google retornou uma página de login oculta em HTML
                            if "<!DOCTYPE html>" in res.text or "login" in res.text.lower():
                                st.error("❌ O Google retornou uma página de login/bloqueio. O Script não está público!")
                                st.info("Abra o Apps Script, clique em Implantar > Gerenciar Implantações e garanta que 'Quem tem acesso' esteja como 'Qualquer pessoa' (Anyone).")
                                with st.expander("Ver detalhes do retorno do Google"):
                                    st.code(res.text[:1000], language="html")
                            
                            # Verifica se o Script rodou mas acusou erro interno de código
                            elif "Erro" in res.text or "error" in res.text.lower():
                                st.error("❌ Erro de execução dentro do Google Apps Script:")
                                st.code(res.text)
                            
                            # Se passou nos testes, salvou com sucesso!
                            else:
                                st.session_state['sucesso_qc'] = f"🚀 QC da Sequência {seq_id} salvo com sucesso! Retorno: {res.text}"
                                st.session_state.pop('current_seq', None)
                                st.rerun()
                        else:
                            st.error(f"❌ Erro de servidor HTTP no Google (Status {res.status_code})")
                            st.text(res.text)
                    except Exception as e:
                        st.error(f"❌ Erro crítico de conexão: {str(e)}")
            else:
                st.warning("Selecione itens ou escreva uma observação para salvar.")
