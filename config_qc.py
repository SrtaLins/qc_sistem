# config_qc.py

ETAPAS = {
    "Denoise": ["RotShot", "Stack 2D", "Stack 3D", "Mapa RMS de Amplitude"],
    "Deghost": ["RotShot", "Stack 2D", "Espectro de Amplitude", "Mapa RMS de Amplitude"],
    "RMC": ["CMP 2D"]
}

ITENS_CHECK = {
    "RotShot": ["Ruído", "Canais Mortos", "Shot Morto", "si", "Artefato"],
    "Stack 2D": ["Continuidade", "Múltiplas", "Sinal/Ruído"],
    "Stack 3D": ["Continuidade", "Ruído", "Sinal/Ruído"],
    "Mapa RMS de Amplitude": ["Amplitude", "Pegada de Aquisição"],
    "Espectro de Amplitude": ["Largura de Banda", "Corte de Frequência"],
    "CMP 2D": ["Mute", "Velocidade", "Estática"]
}

# Aqui as características são específicas para cada "coisa vista" (sub-item)
CARACTERISTICAS = {
    "Ruído": ["Intensidade", "Frequência", "Abrangência"],
    "Canais Mortos": ["Quantidade", "Localização"],
    "Shot Morto": ["Quantidade", "Sequência"],
    "si": ["Intensidade", "Abrangência"],
    "Artefato": ["Tipo", "Intensidade"],
    "Continuidade": ["Qualidade", "Localização"],
    "Múltiplas": ["Intensidade", "Tipo"],
    "Sinal/Ruído": ["Nível"],
    "Amplitude": ["Variação", "Localização"],
    "Pegada de Aquisição": ["Intensidade", "Direção"],
    "Padrão": ["Observação"] # Fallback para itens não mapeados
}

# Opções de preenchimento para as características comuns
OPCOES = {
    "Intensidade": ["N/A", "Baixa", "Média", "Alta"],
    "Abrangência": ["N/A", "Dado todo", "Pontos específicos"],
    "Frequência": ["N/A", "Baixa", "Média", "Alta"],
    "Quantidade": ["Nenhuma", "Pouca", "Muita", "Crítica"],
    "Localização": ["N/A", "Início", "Meio", "Fim", "Espalhado"],
    "Tipo": ["N/A", "Tipo A", "Tipo B", "Desconhecido"],
    "Qualidade": ["Ruim", "Regular", "Boa", "Excelente"]
}
