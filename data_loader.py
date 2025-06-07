import streamlit as st
import pandas as pd

@st.cache_data
def load_crop_data():
    # Load all rows so we can access metadata as well
    df_full = pd.read_csv("data/crop_input_data.csv", header=None)

    # Extract metadata
    variable_names = df_full.iloc[0].tolist()   # Row 1
    variable_codes = df_full.iloc[1].tolist()   # Row 2

    # Extract main crop data (rows 3+)
    df_crops = df_full.iloc[2:].copy()
    df_crops.columns = variable_codes  # Use variable codes as column names
    df_crops.reset_index(drop=True, inplace=True)

    # Create lookup dicts
    crop_lookup = dict(zip(df_crops["crop_name"], df_crops["crop_code"]))
    available_crops = list(crop_lookup.keys())

    # Optional: dictionary to map variable codes to full names
    variable_meta = dict(zip(variable_codes, variable_names))

    return df_crops, crop_lookup, available_crops, variable_meta
