# config_qc.py

# 1. ETAPAS (Onde o analista está)
ETAPAS = {
    "Denoise": ["RotShot", "Stack 2D", "Stack 3D", "Mapa RMS de Amplitude"],
    "Deghost": ["RotShot", "Stack 2D", "Espectro de Amplitude", "Mapa RMS de Amplitude"],
    "RMC": ["CMP 2D", "CMP 3D"] # Adicionado CMP 3D aqui para refletir o quadro
}

# 2. IDENTIFICAÇÃO (O que ele seleciona para analisar, dependendo da etapa)
ITENS_CHECK = {
    # Itens do Primeiro Quadro (RotShot)
    "RotShot": ["Ruído", "SI", "Artefato", "Falta de energia", "Frequência", "Falta de dado", "Geometria", "OK"],
    
    # Itens do Segundo Quadro (Stacks)
    "Stack 2D": ["Artefato", "Múltipla", "Sinal/Ruído", "Continuidade", "Falta de dado", "Frequência", "Pegada de aquisição", "OK"],
    "Stack 3D": ["Artefato", "Múltipla", "Sinal/Ruído", "Continuidade", "Falta de dado", "Frequência", "Pegada de aquisição", "OK"],
    
    # Itens do Terceiro Quadro (CMP 2D / 3D)
    "CMP 2D": ["Artefato", "Falta de dado", "Frequência", "Mute", "Estática", "Velocidade", "Sinal/Ruído", "Múltipla", "OK"],
    "CMP 3D": ["Artefato", "Falta de dado", "Frequência", "Mute", "Estática", "Velocidade", "Sinal/Ruído", "Múltipla", "OK"],

    # Extrapolações mantidas
    "Mapa RMS de Amplitude": ["Artefato", "Sinal/Ruído", "Falta de dado", "Pegada de aquisição", "OK"],
    "Espectro de Amplitude": ["Largura de Banda", "Corte de Frequência", "OK"]
}

# 3. CARACTERÍSTICAS (Os inputs que aparecem na tela para cada item selecionado)
CARACTERISTICAS = {
    # --- Comuns a RotShot ---
    "Ruído": ["Frequência", "Intensidade", "Abrangência"],
    "SI": ["Frequência", "Intensidade", "Abrangência"],
    "Falta de energia": ["Abrangência"],
    "Geometria": ["Abrangência"],
    
    # --- Comuns a Stack e CMP ---
    "Artefato": ["Intensidade", "Abrangência"],
    "Múltipla": ["Intensidade", "Abrangência"],
    "Sinal/Ruído": ["Qualidade"],
    "Continuidade": ["Qualidade", "Abrangência"],
    "Falta de dado": ["Abrangência"],
    "Frequência": ["Frequência", "Abrangência"],
    "Pegada de aquisição": ["Intensidade", "Abrangência"],

    # --- Específicos de CMP (Terceiro Quadro) ---
    "Mute": ["Qualidade"],
    "Estática": ["Qualidade"],
    "Velocidade": ["Qualidade"],
    
    # --- Padrões extras para evitar erros ---
    "Largura de Banda": ["Qualidade"],
    "Padrão": ["Observação"]
}

# 4. OPÇÕES (O que aparece dentro das caixinhas de seleção)
OPCOES = {
    "Intensidade": ["Baixa", "Média", "Alta"],
    "Abrangência": ["Pontual", "Faixa", "Dado Todo"],
    "Frequência": ["Baixa", "Média", "Alta", "Frequência específica"],
    "Qualidade": ["Ruim", "Regular", "Boa", "Excelente"]
}
