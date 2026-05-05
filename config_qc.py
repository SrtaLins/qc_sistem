# config_qc.py

# 1. ETAPAS (Onde o analista está)
ETAPAS = {
    "Denoise": ["RotShot", "Stack 2D", "Stack 3D", "Mapa RMS de Amplitude"],
    "Deghost": ["RotShot", "Stack 2D", "Espectro de Amplitude", "Mapa RMS de Amplitude"],
    "RMC": ["CMP 2D"]
}

# 2. IDENTIFICAÇÃO (O que ele seleciona para analisar, dependendo da etapa)
ITENS_CHECK = {
    # Itens mapeados do primeiro quadro
    "RotShot": ["Ruído", "SI", "Artefato", "Falta de energia", "Frequência", "Falta de dado", "Geometria"],
    
    # Itens mapeados do segundo quadro
    "Stack 2D": ["Artefato", "Múltipla", "Sinal/Ruído", "Continuidade", "Falta de dado", "Frequência", "Pegada de aquisição"],
    "Stack 3D": ["Artefato", "Múltipla", "Sinal/Ruído", "Continuidade", "Falta de dado", "Frequência", "Pegada de aquisição"],
    
    # Extrapolando a lógica para os outros (você pode ajustar depois)
    "Mapa RMS de Amplitude": ["Artefato", "Sinal/Ruído", "Falta de dado", "Pegada de aquisição"],
    "Espectro de Amplitude": ["Largura de Banda", "Corte de Frequência"],
    "CMP 2D": ["Mute", "Velocidade", "Estática"]
}

# 3. CARACTERÍSTICAS (Os inputs que aparecem na tela para cada item selecionado)
CARACTERISTICAS = {
    # --- Do Primeiro Quadro ---
    "Ruído": ["Frequência", "Intensidade", "Abrangência"],
    "SI": ["Frequência", "Intensidade", "Abrangência"],
    "Falta de energia": ["Abrangência"],
    "Geometria": ["Abrangência"],
    
    # --- Do Segundo Quadro ---
    "Artefato": ["Intensidade", "Abrangência"],
    "Múltipla": ["Intensidade", "Abrangência"],
    "Sinal/Ruído": ["Qualidade"],
    "Continuidade": ["Qualidade", "Abrangência"],
    "Falta de dado": ["Abrangência"],
    "Frequência": ["Frequência", "Abrangência"],
    "Pegada de aquisição": ["Intensidade", "Abrangência"],
    
    # --- Padrões extras para evitar erros ---
    "Largura de Banda": ["Qualidade"],
    "Padrão": ["Observação"]
}

# 4. OPÇÕES (O que aparece dentro das caixinhas de seleção)
OPCOES = {
    # Mapeamento exato das duas lousas
    "Intensidade": ["Baixa", "Média", "Alta"],
    "Abrangência": ["Pontual", "Faixa", "Dado Todo"],
    "Frequência": ["Baixa", "Média", "Alta", "Frequência específica"],
    "Qualidade": ["Ruim", "Regular", "Boa", "Excelente"]
}
