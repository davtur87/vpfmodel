df_crops, crop_lookup, available_crops, variable_meta = load_crop_data()

st.title("🧪 VPF Simulation Configurator")

# 1. Project Name
vpf_name = st.text_input("📘 Name of Vertical Plant Farm Project")

# 2. Simulation Type
sim_type = st.selectbox(
    "🔧 Type of simulation",
    options=[
        "1 crop system, multiple simulations",
        "multiple crop systems, 1 simulation per crop",
        "multiple simulations for multiple crops"
    ],
    index=0,
    format_func=lambda x: {
        "1 crop system, multiple simulations": "Single Crop, Multiple Simulations",
        "multiple crop systems, 1 simulation per crop": "Multiple Crops, One Sim Each",
        "multiple simulations for multiple crops": "Multiple Crops, Multiple Sims"
    }[x]
)

# Map internal simopt code
simopt = {
    "1 crop system, multiple simulations": "simopt1",
    "multiple crop systems, 1 simulation per crop": "simopt2",
    "multiple simulations for multiple crops": "simopt3"
}[sim_type]

# 3. Crop selection
if sim_type == "simopt1":
    crop_sel_so1 = st.selectbox("🌿 Select crop", options=available_crops)
    crop_list = [crop_sel_so1]
else:
    crop_sel_so2 = st.multiselect("🌱 Select crops", options=available_crops + ["All Crops"])
    if "All Crops" in crop_sel_so2:
        crop_list = available_crops
    else:
        crop_list = crop_sel_so2

st.write("Selected crops:", crop_list)

# 4. Number of simulations
if simopt == "simopt2":
    sim_number = 1
    st.number_input("🧮 Number of simulations per crop", value=1, disabled=True)
else:
    sim_number = st.number_input("🧮 Number of simulations per crop", min_value=1, value=3, step=1)

# 5. Auto-calculated total
total_sims = len(crop_list) * sim_number if crop_list else 0
st.markdown(f"### 📊 Total Simulations: {total_sims}")

# 6. Save project + simulations
if st.button("💾 Save Project Configuration"):
    if not vpf_name:
        st.error("Please enter a project name before saving.")
    elif not crop_list:
        st.error("Please select at least one crop.")
    else:
        simulations = []
        for crop_name in crop_list:
            crop_code = crop_lookup[crop_name]
            for sim in range(1, sim_number + 1):
                sim_id = f"{crop_name.lower()}_sim_{sim}"
                simulations.append({
                    "simulation_id": sim_id,
                    "crop_name": crop_name,
                    "crop_code": crop_code,
                    "simulation_number": sim,
                    "project_name": vpf_name
                })

        # Save project config
        project_config = {
            "vpf_name": vpf_name,
            "simulation_type": simopt,
            "selected_crops": crop_list,
            "simulations_per_crop": sim_number,
            "total_simulations": total_sims,
            "simulations": simulations
        }

        # Create save folder
        os.makedirs("saved_configs", exist_ok=True)

        # Save project-level file
        project_filepath = f"saved_configs/{vpf_name.replace(' ', '_')}_config.json"
        with open(project_filepath, "w") as f:
            json.dump(project_config, f, indent=4)

        # Optionally save individual simulations separately
        os.makedirs(f"saved_configs/{vpf_name.replace(' ', '_')}/simulations", exist_ok=True)
        for sim in simulations:
            sim_filename = sim["simulation_id"] + ".json"
            with open(f"saved_configs/{vpf_name.replace(' ', '_')}/simulations/{sim_filename}", "w") as f:
                json.dump(sim, f, indent=4)

        st.success(f"✅ Project and {len(simulations)} simulations saved.")
        st.json(project_config)

        # Set session state to remember project
        st.session_state.selected_project = f"{vpf_name.replace(' ', '_')}_config.json"

        # Option to continue
        if st.button("➡️ Continue to Crop Configuration"):
            st.switch_page("pages/2_crop_pheno_config.py")
