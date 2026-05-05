# config_qc.py

# 1. ETAPAS E ITENS
ETAPAS = {
    "Denoise": ["RotShot", "Stack 2D", "Stack 3D", "Mapa RMS de Amplitude"],
    "Deghost": ["RotShot", "Stack 2D", "Espectro de Amplitude", "Mapa RMS de Amplitude"],
    "RMC": ["CMP 2D"]
}

# 2. IDENTIFICAÇÃO (O que você está olhando no item selecionado)
ITENS_CHECK = {
    "RotShot": ["Ruído", "SI", "Artefato", "Falta de energia", "Frequência", "Falta de Dado", "Geometria"],
    
    # Mantendo os outros como base para você expandir depois
    "Stack 2D": ["Continuidade", "Múltiplas", "Sinal/Ruído"],
    "Stack 3D": ["Continuidade", "Ruído", "Sinal/Ruído"],
    "Mapa RMS de Amplitude": ["Amplitude", "Pegada de Aquisição"],
    "Espectro de Amplitude": ["Largura de Banda", "Corte de Frequência"],
    "CMP 2D": ["Mute", "Velocidade", "Estática"]
}

# 3. CARACTERÍSTICAS (O que precisa ser preenchido para cada identificação - exatamente como no seu quadro)
CARACTERISTICAS = {
    # Mapeamento da sua imagem
    "Ruído": ["Frequência", "Intensidade", "Abrangência"],
    "SI": ["Frequência", "Intensidade", "Abrangência"],
    "Artefato": ["Intensidade", "Abrangência"],
    "Falta de energia": ["Abrangência"],
    "Frequência": ["Frequência", "Abrangência"],
    "Falta de Dado": ["Abrangência"],
    "Geometria": ["Abrangência"],
    
    # Extras para os outros itens que mantivemos acima
    "Continuidade": ["Qualidade", "Localização"],
    "Múltiplas": ["Intensidade", "Tipo"],
    "Sinal/Ruído": ["Nível"],
    "Amplitude": ["Variação", "Localização"],
    "Pegada de Aquisição": ["Intensidade", "Direção"],
    "Padrão": ["Observação"] # Usado caso falte alguma configuração
}

# 4. OPÇÕES (As respostas possíveis para cada característica)
OPCOES = {
    # Mapeamento da sua imagem
    "Frequência": ["Baixa", "Média", "Alta", "Frequência específica"],
    "Intensidade": ["Baixa", "Média", "Alta"],
    "Abrangência": ["Pontual", "Faixa", "Dado Todo"],
    
    # Extras para manter a compatibilidade com os outros itens
    "Quantidade": ["Nenhuma", "Pouca", "Muita", "Crítica"],
    "Localização": ["N/A", "Início", "Meio", "Fim", "Espalhado"],
    "Tipo": ["N/A", "Tipo A", "Tipo B", "Desconhecido"],
    "Qualidade": ["Ruim", "Regular", "Boa", "Excelente"]
}
