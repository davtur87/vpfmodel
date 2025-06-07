import streamlit as st
import os
import json
from utils.data_loader import load_crop_data

st.title("🌱 Crop Phenotypical Configuration")

# Detect session state from previous page
default_project = st.session_state.get("selected_project")

# Get available projects
project_folder = "saved_configs"
projects = [f for f in os.listdir(project_folder) if f.endswith("_config.json")]

# Set default to session-selected project
selected_project_file = st.selectbox("Select a project", projects, index=projects.index(default_project) if default_project in projects else 0)

# Load crop data and label mapping
df_crops, crop_lookup, available_crops, code_to_label = load_crop_data()

# Directory where simulation configs are stored
project_folder = "saved_configs"
projects = [f for f in os.listdir(project_folder) if f.endswith("_config.json")]

# Project selector
selected_project_file = st.selectbox("Select a project", projects)
project_path = os.path.join(project_folder, selected_project_file)

# Load project
with open(project_path) as f:
    project_data = json.load(f)

project_name = project_data["vpf_name"]
simulations = project_data["simulations"]

# Define phenotypical variables
pheno_vars = [
    ("Growth Cycle Duration", "Pg"),
    ("Mature Plant Height", "Pm"),
    ("Harvest Index", "Ph"),
    ("HC Water %", "Pw"),
    ("HC Carbohydrate %", "Px"),
    ("HC fat %", "Py"),
    ("HC Protein %", "Pz"),
    ("HC kcal/kg", "Pi"),
    ("Mean optimal temperature", "Pt")
]

# Helper function to get default value from crop_input_data
def get_crop_value(crop_code, var_code):
    row = df_crops[df_crops["crop_code"] == crop_code]
    if not row.empty:
        return row.iloc[0][var_code]
    return None

# Build interface
st.subheader(f"Project: {project_name}")
grouped = {}

# Group simulations by crop
for sim in simulations:
    grouped.setdefault(sim["crop_name"], []).append(sim)

# Store updated values
updated_sims = []

for crop_name, sim_group in grouped.items():
    crop_code = sim_group[0]["crop_code"]
    with st.expander(f"🌾 {crop_name} ({len(sim_group)} sim{'s' if len(sim_group) > 1 else ''})", expanded=True):

        # Global inputs (apply to all)
        st.markdown("##### Apply values to all simulations for this crop:")

        global_updates = {}
        cols = st.columns(len(pheno_vars))
        for i, (label, code) in enumerate(pheno_vars):
            with cols[i]:
                with st.popover("ℹ️", use_container_width=True):
                    st.write(f"More info about **{label}** goes here.")
                global_updates[code] = st.number_input(
                    label,
                    value=get_crop_value(crop_code, code),
                    key=f"{crop_code}_{code}_global"
                )

        # Apply checkbox
        apply_all = st.checkbox(f"Apply these values to all {crop_name} simulations", key=f"{crop_code}_apply_all")

        st.markdown("##### Or edit each simulation individually:")
        for sim in sim_group:
            sim_id = sim["simulation_id"]
            sim_key = f"{sim_id}_section"
            with st.expander(f"🧪 {sim_id}", expanded=False):
                for label, code in pheno_vars:
                    current_val = get_crop_value(sim["crop_code"], code)
                    sim[code] = st.number_input(
                        f"{label} ({code})",
                        value=global_updates[code] if apply_all else current_val,
                        key=f"{sim_id}_{code}"
                    )
                updated_sims.append(sim)

# Save + continue
if st.button("💾 Save & Continue"):
    # Overwrite sim files with updated values
    sim_folder = os.path.join(project_folder, project_name.replace(" ", "_"), "simulations")
    for sim in updated_sims:
        sim_filename = f"{sim['simulation_id']}.json"
        with open(os.path.join(sim_folder, sim_filename), "w") as f:
            json.dump(sim, f, indent=4)
    st.success("Simulations updated successfully.")

    # Placeholder for navigation
    st.info("👉 Continue to next page... (placeholder)")
