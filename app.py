import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da Página
st.set_page_config(page_title="QC Sísmico - Sistema de Gestão", layout="wide")

# Inicialização da base de dados na sessão (Simulação de banco de dados)
if 'qc_history' not in st.session_state:
    st.session_state['qc_history'] = pd.DataFrame(columns=[
        'Data', 'Usuário', 'Etapa', 'Sequência', 'Item', 
        'Intensidade', 'Abrangência', 'Observações'
    ])

# Título da aplicação
st.title("🪨 Sistema de Controle de Qualidade (QC) Sísmico")
st.markdown("---")

# 1. Identificação do Usuário
st.sidebar.header("1. Identificação")
user_name = st.sidebar.text_input("Nome do Analista", placeholder="Digite seu nome completo")

if not user_name:
    st.sidebar.warning("Por favor, digite seu nome para iniciar o QC.")
else:
    st.sidebar.success(f"Usuário identificado: **{user_name}**")
    
    # 2. Seleção da Etapa e Sequência
    st.sidebar.markdown("---")
    st.sidebar.header("2. Seleção de Processo")
    
    etapa = st.sidebar.selectbox("Etapa de Processamento", ["Denoise", "Deghost", "Normal Moveout (NMO)", "Migration"])
    sequencia = st.sidebar.selectbox("Sequência Sísmica", ["SEV-0042", "SEV-0045", "SEV-0050", "SEV-0078"])
    
    st.markdown(f"### Etapa atual: **{etapa}** | Sequência: **{sequencia}**")
    
    # 3. Itens de QC e Checklist Detalhado
    st.subheader("3. Checklist de Itens")
    
    itens_selecionados = st.multiselect(
        "Quais itens você irá checar nesta etapa?",
        ["Stack", "Shot", "Mapa RMS", "Gathers", "Velocidades"]
    )
    
    dados_inseridos = []
    
    for item in itens_selecionados:
        with st.expander(f"🔎 Configurações para: {item}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                intensidade = st.selectbox(f"Intensidade do achado ({item})", ["Baixa", "Média", "Alta"], key=f"int_{item}")
                abrangencia = st.selectbox(f"Abrangência ({item})", ["Dado todo", "Pontos específicos"], key=f"abr_{item}")
            
            with col2:
                obs_item = st.text_area(f"Observações específicas para {item}", key=f"obs_{item}")
                imagem = st.file_uploader(f"Adicionar imagem/print para {item}", type=["png", "jpg", "jpeg"], key=f"img_{item}")
            
            # Armazena os dados do item
            if st.button(f"Salvar item {item}", key=f"btn_{item}"):
                dados_inseridos.append({
                    'Data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'Usuário': user_name,
                    'Etapa': etapa,
                    'Sequência': sequencia,
                    'Item': item,
                    'Intensidade': intensidade,
                    'Abrangência': abrangencia,
                    'Observações': obs_item
                })
                st.success(f"Item {item} registrado com sucesso!")

    # 4. Observações Gerais
    st.markdown("---")
    st.subheader("4. Observações Gerais da Sequência")
    obs_geral = st.text_area("Considerações finais sobre o QC desta sequência")
    
    if st.button("Finalizar e Salvar QC da Sequência"):
        nova_linha = pd.DataFrame({
            'Data': [datetime.now().strftime("%d/%m/%Y %H:%M")],
            'Usuário': [user_name],
            'Etapa': [etapa],
            'Sequência': [sequencia],
            'Item': ["Geral"],
            'Intensidade': ["N/A"],
            'Abrangência': ["N/A"],
            'Observações': [obs_geral]
        })
        st.session_state['qc_history'] = pd.concat([st.session_state['qc_history'], nova_linha], ignore_index=True)
        st.balloons()
        st.success(f"QC da sequência {sequencia} salvo com sucesso no sistema!")

    # 5. Histórico da Sequência
    st.markdown("---")
    st.subheader("📊 Histórico de QCs Anteriores")
    
    filtro_historico = st.session_state['qc_history'][st.session_state['qc_history']['Sequência'] == sequencia]
    
    if not filtro_historico.empty:
        st.dataframe(filtro_historico)
    else:
        st.info("Nenhum registro de QC anterior encontrado para esta sequência.")
