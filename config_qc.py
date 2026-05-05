# config_qc.py
ETAPAS = {
    "Denoise": ["RotShot", "Stack 2D", "Stack 3D", "Mapa RMS de Amplitude"],
    "Deghost": ["RotShot", "Stack 2D", "Espectro de Amplitude", "Mapa RMS de Amplitude"],
    "RMC": ["CMP 2D"]
}

ITENS_CHECK = {
    "RotShot": ["Ruído Coerente", "Canais Mortos", "Falta de Energia"],
    "Stack 2D": ["Continuidade", "Múltiplas", "Sinal/Ruído"],
    "Mapa RMS de Amplitude": ["Amplitude", "Pegada de Aquisição"]
}

CARACTERISTICAS = {
    "Intensidade": ["Baixa", "Média", "Alta"],
    "Abrangência": ["Dado todo", "Pontos específicos", "N/A"]
}
