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
    
    st.divider()
    st.subheader("📊 Exploratory Data Analysis")

    eda_tab1, eda_tab2, eda_tab3 = st.tabs(["Column Stats", "Null Heatmap", "Distributions"])

    with eda_tab1:
        from utils.profiler import get_column_stats
        stats_df = get_column_stats(df)
        st.dataframe(stats_df, use_container_width=True)

    with eda_tab2:
        from utils.profiler import plot_null_heatmap
        plot_null_heatmap(df)

    with eda_tab3:
        from utils.profiler import plot_distributions
        plot_distributions(df)

    st.divider()
    st.subheader("🧹 Cleaning Options")

    with st.form("cleaning_form"):
        col_a, col_b = st.columns(2)

        with col_a:
            remove_dupes = st.checkbox("Remove duplicate rows", value=True)
            fix_types = st.checkbox("Auto-fix data types", value=True)
            handle_missing = st.checkbox("Handle missing values", value=True)
            missing_strategy = st.selectbox(
                "Missing value strategy",
                ["mean", "median", "zero", "drop rows"]
            )

        with col_b:
            handle_out = st.checkbox("Handle outliers", value=True)
            outlier_method = st.selectbox(
                "Outlier method",
                ["clip", "remove"]
            )

        run_cleaning = st.form_submit_button("🚀 Run Cleaning", use_container_width=True)

    if run_cleaning:
        from utils.cleaner import (
            remove_duplicates, fix_dtypes,
            handle_missing_values, remove_missing_rows, handle_outliers
        )

        cleaned_df = df.copy()
        change_log = []

        if remove_dupes:
            cleaned_df, n = remove_duplicates(cleaned_df)
            change_log.append(f"✅ Removed **{n}** duplicate rows")

        if fix_types:
            cleaned_df, type_changes = fix_dtypes(cleaned_df)
            for c in type_changes:
                change_log.append(f"✅ Fixed dtype: {c}")

        if handle_missing:
            if missing_strategy == "drop rows":
                cleaned_df, n = remove_missing_rows(cleaned_df)
                change_log.append(f"✅ Dropped **{n}** rows with missing values")
            else:
                cleaned_df, missing_report = handle_missing_values(cleaned_df, missing_strategy)
                for col, msg in missing_report.items():
                    change_log.append(f"✅ `{col}`: {msg}")

        if handle_out:
            cleaned_df, outlier_report = handle_outliers(cleaned_df, outlier_method)
            for col, msg in outlier_report.items():
                change_log.append(f"✅ `{col}`: {msg}")

        st.session_state["cleaned_df"] = cleaned_df

        st.success("Cleaning complete!")

        st.subheader("📋 Change Log")
        if change_log:
            for log in change_log:
                st.markdown(f"- {log}")
        else:
            st.info("No changes were made.")

        st.divider()
        st.subheader("⚙️ Transform Options")

        with st.form("transform_form"):
            col_t1, col_t2 = st.columns(2)

            with col_t1:
                do_encode = st.checkbox("Encode categorical columns", value=True)
                encode_method = st.selectbox(
                    "Encoding method",
                    ["onehot", "label"],
                    help="One-hot: creates new columns. Label: converts to numbers."
                )

            with col_t2:
                do_normalize = st.checkbox("Normalize numeric columns", value=True)
                norm_method = st.selectbox(
                    "Normalization method",
                    ["minmax", "standard", "log"],
                    help="MinMax: [0,1]. Standard: mean=0 std=1. Log: log1p transform."
                )

            run_transform = st.form_submit_button("⚙️ Run Transforms", use_container_width=True)

        if run_transform:
            from utils.transformer import encode_categoricals, normalize_numerics

            transformed_df = cleaned_df.copy()
            transform_log = []

            if do_encode:
                transformed_df, enc_report = encode_categoricals(transformed_df, encode_method)
                for msg in enc_report:
                    transform_log.append(f"✅ Encode: {msg}")

            if do_normalize:
                transformed_df, norm_report = normalize_numerics(transformed_df, norm_method)
                for msg in norm_report:
                    transform_log.append(f"✅ Normalize: {msg}")

            st.session_state["transformed_df"] = transformed_df

            st.success("Transforms complete!")

            st.subheader("📋 Transform Log")
            if transform_log:
                for log in transform_log:
                    st.markdown(f"- {log}")
            else:
                st.info("No transforms were applied.")

        st.subheader("Cleaned Data Preview")
        st.dataframe(cleaned_df.head(20), use_container_width=True)

        after_col1, after_col2, after_col3 = st.columns(3)
        after_col1.metric("Rows", cleaned_df.shape[0], delta=cleaned_df.shape[0] - df.shape[0])
        after_col2.metric("Columns", cleaned_df.shape[1])
        after_col3.metric("Missing Values", int(cleaned_df.isnull().sum().sum()))
    
    st.session_state["df"] = df