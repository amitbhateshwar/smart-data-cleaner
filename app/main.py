import streamlit as st
import pandas as pd
from utils.ingestor import load_from_upload, load_from_url, get_basic_info

st.set_page_config(
    page_title="Smart Data Cleaner",
    page_icon="🧹",
    layout="wide"
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
def load_css():
    import os
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
    <div style="display:flex; align-items:center; gap:16px; padding:1.5rem 0 0.5rem 0;">
        <div style="
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            border-radius: 14px;
            width: 52px; height: 52px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.6rem;">🧹</div>
        <div>
            <h1 style="margin:0; font-size:1.9rem; font-weight:700;
                       color:#f1f5f9; letter-spacing:-0.5px;">
                Smart Data Cleaner
            </h1>
            <p style="margin:0; color:#64748b; font-size:0.9rem;">
                Upload a dataset or paste a URL — get back a clean, ML-ready file.
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)
st.divider()

# ── Init step ─────────────────────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state["step"] = 1

# ── Progress bar ──────────────────────────────────────────────────────────────
steps = ["📂 Load", "📊 EDA", "🧹 Clean", "⚙️ Transform", "📥 Download"]
current = st.session_state["step"]

progress_html = '<div style="display:flex; gap:8px; margin-bottom:1.5rem;">'
for i, label in enumerate(steps, start=1):
    if i == current:
        progress_html += f"""
            <div style="flex:1; background:#2563eb; color:#fff;
                        border-radius:8px; padding:8px 4px;
                        text-align:center; font-size:0.8rem; font-weight:600;">
                {label}
            </div>"""
    elif i < current:
        progress_html += f"""
            <div style="flex:1; background:#052e16; color:#4ade80;
                        border-radius:8px; padding:8px 4px;
                        text-align:center; font-size:0.8rem; font-weight:500;">
                ✓ {label}
            </div>"""
    else:
        progress_html += f"""
            <div style="flex:1; background:#111111; color:#475569;
                        border-radius:8px; padding:8px 4px;
                        text-align:center; font-size:0.8rem;">
                {label}
            </div>"""
progress_html += '</div>'
st.markdown(progress_html, unsafe_allow_html=True)

# ── STEP 1: LOAD ──────────────────────────────────────────────────────────────
if st.session_state["step"] == 1:
    input_method = st.radio("How do you want to load your data?",
                            ["Upload a file", "Paste a URL"], horizontal=True)

    if input_method == "Upload a file":
        uploaded_file = st.file_uploader("Upload CSV, JSON, or Excel",
                                         type=["csv", "json", "xlsx", "xls"])
        if uploaded_file:
            try:
                st.session_state["df"] = load_from_upload(uploaded_file)
                st.success(f"✅ File loaded: `{uploaded_file.name}`")
                if st.button("Continue to EDA →", use_container_width=True):
                    st.session_state["step"] = 2
                    st.rerun()
            except Exception as e:
                st.error(f"Error loading file: {e}")
    else:
        url = st.text_input("Enter the direct URL to a CSV, JSON, or Excel file")
        if url:
            with st.spinner("Fetching data..."):
                try:
                    st.session_state["df"] = load_from_url(url)
                    st.success("✅ Data loaded from URL")
                    if st.button("Continue to EDA →", use_container_width=True):
                        st.session_state["step"] = 2
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# ── STEP 2: EDA ───────────────────────────────────────────────────────────────
elif st.session_state["step"] == 2:
    df = st.session_state["df"]
    info = get_basic_info(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", info["rows"])
    col2.metric("Columns", info["columns"])
    col3.metric("Missing Values", info["missing_values"])
    col4.metric("Duplicate Rows", info["duplicate_rows"])

    st.subheader("Data Preview")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("📊 Exploratory Data Analysis")
    eda_tab1, eda_tab2, eda_tab3 = st.tabs(["Column Stats", "Null Heatmap", "Distributions"])

    with eda_tab1:
        from utils.profiler import get_column_stats
        st.dataframe(get_column_stats(df), use_container_width=True)
    with eda_tab2:
        from utils.profiler import plot_null_heatmap
        plot_null_heatmap(df)
    with eda_tab3:
        from utils.profiler import plot_distributions
        plot_distributions(df)

    col_back, col_next = st.columns(2)
    if col_back.button("← Back", use_container_width=True):
        st.session_state["step"] = 1
        st.rerun()
    if col_next.button("Continue to Cleaning →", use_container_width=True):
        st.session_state["step"] = 3
        st.rerun()

# ── STEP 3: CLEAN ─────────────────────────────────────────────────────────────
elif st.session_state["step"] == 3:
    df = st.session_state["df"]
    st.subheader("🧹 Cleaning Options")

    with st.form("cleaning_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            remove_dupes     = st.checkbox("Remove duplicate rows", value=True)
            fix_types        = st.checkbox("Auto-fix data types", value=True)
            handle_missing   = st.checkbox("Handle missing values", value=True)
            missing_strategy = st.selectbox("Missing value strategy",
                                            ["mean", "median", "zero", "drop rows"])
        with col_b:
            handle_out     = st.checkbox("Handle outliers", value=True)
            outlier_method = st.selectbox("Outlier method", ["clip", "remove"])

        run_cleaning = st.form_submit_button("🚀 Run Cleaning", use_container_width=True)

    if run_cleaning:
        from utils.cleaner import (remove_duplicates, fix_dtypes,
                                   handle_missing_values, remove_missing_rows,
                                   handle_outliers)
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
        st.session_state["change_log"] = change_log

    if "cleaned_df" in st.session_state:
        cleaned_df = st.session_state["cleaned_df"]
        change_log = st.session_state.get("change_log", [])

        st.success("Cleaning complete!")
        st.subheader("📋 Change Log")
        for log in change_log:
            st.markdown(f"- {log}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Rows",           cleaned_df.shape[0], delta=cleaned_df.shape[0] - df.shape[0])
        c2.metric("Columns",        cleaned_df.shape[1])
        c3.metric("Missing Values", int(cleaned_df.isnull().sum().sum()))

        st.subheader("Cleaned Data Preview")
        st.dataframe(cleaned_df.head(20), use_container_width=True)

        col_back, col_next = st.columns(2)
        if col_back.button("← Back to EDA", use_container_width=True):
            st.session_state["step"] = 2
            st.rerun()
        if col_next.button("Continue to Transform →", use_container_width=True):
            st.session_state["step"] = 4
            st.rerun()

# ── STEP 4: TRANSFORM ─────────────────────────────────────────────────────────
elif st.session_state["step"] == 4:
    cleaned_df = st.session_state["cleaned_df"]
    st.subheader("⚙️ Transform Options")

    with st.form("transform_form"):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            do_encode     = st.checkbox("Encode categorical columns", value=True)
            encode_method = st.selectbox("Encoding method", ["onehot", "label"])
        with col_t2:
            do_normalize = st.checkbox("Normalize numeric columns", value=True)
            norm_method  = st.selectbox("Normalization method", ["minmax", "standard", "log"])

        run_transform = st.form_submit_button("⚙️ Run Transforms", use_container_width=True)

    if run_transform:
        from utils.transformer import encode_categoricals, normalize_numerics
        transformed_df = cleaned_df.copy()
        transform_log  = []

        if do_encode:
            transformed_df, enc_report = encode_categoricals(transformed_df, encode_method)
            for msg in enc_report:
                transform_log.append(f"✅ Encode: {msg}")
        if do_normalize:
            transformed_df, norm_report = normalize_numerics(transformed_df, norm_method)
            for msg in norm_report:
                transform_log.append(f"✅ Normalize: {msg}")

        st.session_state["transformed_df"] = transformed_df
        st.session_state["transform_log"]  = transform_log

    if "transformed_df" in st.session_state:
        transformed_df = st.session_state["transformed_df"]
        transform_log  = st.session_state.get("transform_log", [])

        st.success("Transforms complete!")
        st.subheader("📋 Transform Log")
        for log in transform_log:
            st.markdown(f"- {log}")

        st.subheader("Transformed Data Preview")
        st.dataframe(transformed_df.head(20), use_container_width=True)

        col_back, col_next = st.columns(2)
        if col_back.button("← Back to Cleaning", use_container_width=True):
            st.session_state["step"] = 3
            st.rerun()
        if col_next.button("Continue to Download →", use_container_width=True):
            st.session_state["step"] = 5
            st.rerun()

# ── STEP 5: DOWNLOAD ──────────────────────────────────────────────────────────
elif st.session_state["step"] == 5:
    st.subheader("📥 Download Your Clean Dataset")

    final_df = st.session_state.get("transformed_df",
               st.session_state.get("cleaned_df"))

    if final_df is not None:
        change_log    = st.session_state.get("change_log", [])
        transform_log = st.session_state.get("transform_log", [])
        original_df   = st.session_state["df"]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Original Rows",    original_df.shape[0])
        col2.metric("Final Rows",        final_df.shape[0],
                    delta=final_df.shape[0] - original_df.shape[0])
        col3.metric("Final Columns",     final_df.shape[1])
        col4.metric("Missing Values",    int(final_df.isnull().sum().sum()))

        st.subheader("Final Data Preview")
        st.dataframe(final_df.head(20), use_container_width=True)

        st.subheader("📋 Full Change Report")
        all_logs = change_log + transform_log
        if all_logs:
            for log in all_logs:
                st.markdown(f"- {log}")
        else:
            st.info("No changes were logged.")

        st.divider()
        csv = final_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=csv,
            file_name="cleaned_dataset.csv",
            mime="text/csv",
            use_container_width=True
        )

        if st.button("← Back to Transform", use_container_width=True):
            st.session_state["step"] = 4
            st.rerun()

        if st.button("🔄 Start Over", use_container_width=True):
            for key in ["df", "cleaned_df", "transformed_df",
                        "change_log", "transform_log", "step"]:
                st.session_state.pop(key, None)
            st.rerun()
