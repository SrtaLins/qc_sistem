# 1. STEPS
STEPS = {
    "Denoise": ["RotShot", "Stack 2D", "Stack 3D", "Amplitude RMS Map"],
    "Deghost": ["RotShot", "Stack 2D", "Amplitude Spectrum", "Amplitude RMS Map"],
    "RMC": ["CMP 2D", "CMP 3D"]
}

# 2. CHECK ITEMS
CHECK_ITEMS = {
    "RotShot": ["Noise", "SI", "Artifact", "Power Loss", "Frequency", "Missing Data", "Geometry", "OK"],
    "Stack 2D": ["Artifact", "Multiple", "Signal/Noise", "Continuity", "Missing Data", "Frequency", "Acquisition Footprint", "OK"],
    "Stack 3D": ["Artifact", "Multiple", "Signal/Noise", "Continuity", "Missing Data", "Frequency", "Acquisition Footprint", "OK"],
    "CMP 2D": ["Artifact", "Missing Data", "Frequency", "Mute", "Statics", "Velocity", "Signal/Noise", "Multiple", "OK"],
    "CMP 3D": ["Artifact", "Missing Data", "Frequency", "Mute", "Statics", "Velocity", "Signal/Noise", "Multiple", "OK"],
    "Amplitude RMS Map": ["Artifact", "Signal/Noise", "Missing Data", "Acquisition Footprint", "OK"],
    "Amplitude Spectrum": ["Bandwidth", "Frequency Cut", "OK"]
}

# 3. CHARACTERISTICS
CHARACTERISTICS = {
    "Noise": ["Frequency", "Intensity", "Scope"],
    "SI": ["Frequency", "Intensity", "Scope"],
    "Power Loss": ["Scope"],
    "Geometry": ["Scope"],
    "Artifact": ["Intensity", "Scope"],
    "Multiple": ["Intensity", "Scope"],
    "Signal/Noise": ["Quality"],
    "Continuity": ["Quality", "Scope"],
    "Missing Data": ["Scope"],
    "Frequency": ["Frequency", "Scope"],
    "Acquisition Footprint": ["Intensity", "Scope"],
    "Mute": ["Quality"],
    "Statics": ["Quality"],
    "Velocity": ["Quality"],
    "Bandwidth": ["Quality"],
    "Pattern": ["Observation"]
}

# 4. OPTIONS
OPTIONS = {
    "Intensity": ["Low", "Medium", "High"],
    "Scope": ["Spot", "Range", "Full Dataset"],
    "Frequency": ["Low", "Medium", "High", "Specific Frequency"],
    "Quality": ["Poor", "Fair", "Good", "Excellent"]
}
