import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import config_qc as cfg

# --- CONFIGURATIONS ---
SHEET_ID = "1fVZT7cZ1YYJdketX_zlpuL3L3dIED2nocyPlmRN9Mr0"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/1fVZT7cZ1YYJdketX_zlpuL3L3dIED2nocyPlmRN9Mr0/export?format=csv"
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyIIUSYeDX1XGIruyf1RUYpvOWAtSfjWllBXndWrYtO-qx4suXoqXycnMwLKuxrXdQ/exec"

# Default attribute options if they don't exist in config_qc.py
DEFAULT_OPTIONS = {
    "Intensity": ["Low", "Medium", "High"],
    "Frequency": ["Low", "Medium", "High"],
    "Scope": ["Spot", "Range", "Full Dataset"],
    "Quality": ["Excellent", "Good", "Fair", "Poor"]
}

st.set_page_config(page_title="Seismic QC Tool", layout="wide")

# --- DATA LOADING ---
@st.cache_data(ttl=60)
def get_master_data():
    df = pd.read_excel("master_sequences.xlsx")
    df = df.dropna(subset=['ACQSEQ'])
    df['ACQSEQ'] = pd.to_numeric(df['ACQSEQ']).astype(int).astype(str)
    return df

def get_history():
    try:
        df = pd.read_csv(f"{GOOGLE_SHEET_URL}&cache={datetime.now().timestamp()}")
        df['Sequence'] = df['Sequence'].astype(str)
        return df
    except:
        return pd.DataFrame(columns=["Date_Time", "Analyst", "Sequence", "Step", "Data_Type", "Detected_Item", "Characteristic", "Value"])

df_master = get_master_data()
df_history = get_history()

# --- SIDEBAR INTERFACE ---
st.sidebar.header("Identification")
user = st.sidebar.text_input("Analyst Name", key="user_name")
active_step = st.sidebar.selectbox("QC Step", list(cfg.STEPS.keys()))

if not user:
    st.warning("👈 Please identify yourself in the sidebar to begin.")
    st.stop()

# --- HISTORY PROCESSING FOR TABLE ---
st.title(f"Monitoring - {active_step}")

step_history = df_history[df_history['Step'] == active_step]

if not step_history.empty:
    def format_row(row):
        char, val = row['Characteristic'], row['Value']
        if char == "Status":
            return f"{row['Data_Type']}: {row['Detected_Item']}"
        elif char == "Observation":
            return f"{row['Data_Type']}: {val}"
        else:
            return f"{row['Data_Type']}: {row['Detected_Item']} ({char}={val})"
            
    step_history = step_history.copy()
    step_history['Description'] = step_history.apply(format_row, axis=1)
    summary_history = step_history.groupby('Sequence')['Description'].apply(lambda x: " | ".join(x.unique())).reset_index()
    summary_history.columns = ['Sequence', 'Completed Items']
else:
    summary_history = pd.DataFrame(columns=['Sequence', 'Completed Items'])

df_display = df_master.copy()
df_display = df_display.merge(summary_history, left_on='ACQSEQ', right_on='Sequence', how='left').drop(columns=['Sequence'], errors='ignore')
df_display['In Use'] = df_display['ACQSEQ'].apply(lambda x: "Yes" if x in df_history['Sequence'].unique() else "No")
df_display = df_display.rename(columns={'ACQSEQ': 'Sequence'})

base_cols = ['Sequence', 'In Use', 'Completed Items']
extras = st.multiselect("View extra columns:", [c for c in df_display.columns if c not in base_cols])
final_df = df_display[base_cols + extras].fillna("-")

# Interactive Table
event = st.dataframe(
    final_df, 
    use_container_width=True, 
    hide_index=True, 
    on_select="rerun", 
    selection_mode="single-row"
)

if event.selection.rows:
    st.session_state['current_seq'] = final_df.iloc[event.selection.rows[0]]['Sequence']

# --- DYNAMIC QC FORM ---
if 'current_seq' in st.session_state:
    seq_id = st.session_state['current_seq']
    st.markdown("---")
    st.subheader(f"📝 Sequence QC: {seq_id}")

    available_types = cfg.STEPS[active_step] + ["Observation"]
    selected_type = st.pills("Data Type:", available_types, selection_mode="single", default=available_types[0])

    rows_to_save = []

    if selected_type == "Observation":
        general_obs = st.text_area("General observations for this sequence:", key="general_obs")
        if general_obs:
            rows_to_save.append({
                "analyst": user,
                "sequence": str(seq_id),
                "step": active_step,
                "data_type": "Observation",
                "detected_item": "General",
                "characteristic": "Observation",
                "value": general_obs
            })
    else:
        seen_items = st.multiselect(
            f"What was identified in {selected_type}?", 
            cfg.CHECK_ITEMS.get(selected_type, []),
            key=f"ms_{selected_type}"
        )
        
        st.write("---")
        specific_obs = st.text_input(f"Specific observation for {selected_type}", key="specific_obs")
        
        if specific_obs:
            rows_to_save.append({
                "analyst": user,
                "sequence": str(seq_id),
                "step": active_step,
                "data_type": selected_type,
                "detected_item": "General",
                "characteristic": "Observation",
                "value": specific_obs
            })

        for item in seen_items:
            st.markdown(f"**{item} Settings:**")
            characteristics = cfg.CHARACTERISTICS.get(item, [])
            
            if characteristics:
                cols = st.columns(len(characteristics))
                any_attr_selected = False
                
                for i, attr in enumerate(characteristics):
                    orig_options = getattr(cfg, "OPTIONS", {}).get(attr) or DEFAULT_OPTIONS.get(attr, [])
                    options = ["-"] + orig_options
                    
                    choice = cols[i].selectbox(attr, options, key=f"attr_{seq_id}_{item}_{attr}")
                    if choice != "-":
                        any_attr_selected = True
                        rows_to_save.append({
                            "analyst": user,
                            "sequence": str(seq_id),
                            "step": active_step,
                            "data_type": selected_type,
                            "detected_item": item,
                            "characteristic": attr,
                            "value": choice
                        })
                
                if not any_attr_selected:
                    rows_to_save.append({
                        "analyst": user,
                        "sequence": str(seq_id),
                        "step": active_step,
                        "data_type": selected_type,
                        "detected_item": item,
                        "characteristic": "Status",
                        "value": "Identified"
                    })
            else:
                rows_to_save.append({
                    "analyst": user,
                    "sequence": str(seq_id),
                    "step": active_step,
                    "data_type": selected_type,
                    "detected_item": item,
                    "characteristic": "Status",
                    "value": "Identified"
                })

    col_save, col_cancel = st.columns([1, 5])

    if 'qc_success' in st.session_state:
        st.success(st.session_state['qc_success'])
        del st.session_state['qc_success']
    
    if col_save.button("💾 Save QC"):
        if rows_to_save:
            with st.spinner("Sending data to Google..."):
                try:
                    res = requests.post(SCRIPT_URL, json=rows_to_save, timeout=10)
                    if res.status_code == 200:
                        if "<!DOCTYPE html>" in res.text or "login" in res.text.lower():
                            st.error("❌ Google returned a login page. The script is not public!")
                        elif "Error" in res.text or "error" in res.text.lower():
                            st.error("❌ Execution error in Google Apps Script:")
                            st.code(res.text)
                        else:
                            st.session_state['qc_success'] = f"🚀 QC for Sequence {seq_id} saved successfully!"
                            st.session_state.pop('current_seq', None)
                            st.rerun()
                    else:
                        st.error(f"❌ HTTP Server Error (Status {res.status_code})")
                except Exception as e:
                    st.error(f"❌ Critical connection error: {str(e)}")
        else:
            st.warning("Please select items or write an observation to save.")
