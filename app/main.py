import streamlit as st
import pandas as pd
from utils.ingestor import load_from_upload, load_from_url, get_basic_info

st.set_page_config(
    page_title="Smart Data Cleaner",
    page_icon="🧹",
    layout="wide"
)

st.title("🧹 Smart Data Cleaner")
st.markdown("Upload a dataset or paste a URL — get back a clean, ML-ready file.")

st.divider()

# --- Input Section ---
input_method = st.radio("How do you want to load your data?", ["Upload a file", "Paste a URL"], horizontal=True)

df = None

if input_method == "Upload a file":
    uploaded_file = st.file_uploader(
        "Upload CSV, JSON, or Excel",
        type=["csv", "json", "xlsx", "xls"]
    )
    if uploaded_file:
        try:
            df = load_from_upload(uploaded_file)
            st.success(f"✅ File loaded: `{uploaded_file.name}`")
        except Exception as e:
            st.error(f"Error loading file: {e}")

elif input_method == "Paste a URL":
    url = st.text_input("Enter the direct URL to a CSV, JSON, or Excel file")
    if url:
        with st.spinner("Fetching data from URL..."):
            try:
                df = load_from_url(url)
                st.success("✅ Data loaded from URL")
            except Exception as e:
                st.error(f"Error loading URL: {e}")

# --- Preview Section ---
if df is not None:
    st.divider()
    info = get_basic_info(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", info["rows"])
    col2.metric("Columns", info["columns"])
    col3.metric("Missing Values", info["missing_values"])
    col4.metric("Duplicate Rows", info["duplicate_rows"])

    st.subheader("Data Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("Column Info")
    dtype_df = pd.DataFrame({
        "Column": info["column_names"],
        "Data Type": [info["dtypes"][c] for c in info["column_names"]],
        "Missing": [int(df[c].isnull().sum()) for c in info["column_names"]],
        "Missing %": [f"{df[c].isnull().mean()*100:.1f}%" for c in info["column_names"]],
    })
    st.dataframe(dtype_df, use_container_width=True)

    st.session_state["df"] = df