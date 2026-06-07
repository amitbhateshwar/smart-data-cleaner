import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def plot_null_heatmap(df: pd.DataFrame):
    null_cols = [col for col in df.columns if df[col].isnull().any()]
    if not null_cols:
        st.info("✅ No missing values found in the dataset.")
        return

    fig, ax = plt.subplots(figsize=(12, max(4, len(null_cols) * 0.5)))
    sns.heatmap(
        df[null_cols].isnull(),
        cbar=False,
        yticklabels=False,
        cmap="viridis",
        ax=ax
    )
    ax.set_title("Missing Value Heatmap (yellow = missing)", fontsize=13)
    ax.set_xlabel("Columns")
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

def plot_distributions(df: pd.DataFrame):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if not numeric_cols:
        st.info("No numeric columns found for distribution plots.")
        return

    cols_per_row = 3
    rows = (len(numeric_cols) + cols_per_row - 1) // cols_per_row
    fig, axes = plt.subplots(rows, cols_per_row, figsize=(15, rows * 4))
    axes = axes.flatten() if rows > 1 else [axes] if len(numeric_cols) == 1 else axes.flatten()

    for i, col in enumerate(numeric_cols):
        axes[i].hist(df[col].dropna(), bins=30, color="#4C9BE8", edgecolor="white", linewidth=0.5)
        axes[i].set_title(col, fontsize=11)
        axes[i].set_xlabel("")
        axes[i].tick_params(labelsize=8)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle("Numeric Column Distributions", fontsize=14, y=1.01)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

def get_column_stats(df: pd.DataFrame) -> pd.DataFrame:
    stats = []
    for col in df.columns:
        col_data = df[col]
        stat = {
            "Column": col,
            "Type": str(col_data.dtype),
            "Missing": int(col_data.isnull().sum()),
            "Missing %": f"{col_data.isnull().mean() * 100:.1f}%",
            "Unique Values": int(col_data.nunique()),
        }
        if pd.api.types.is_numeric_dtype(col_data):
            stat["Min"] = round(col_data.min(), 2)
            stat["Max"] = round(col_data.max(), 2)
            stat["Mean"] = round(col_data.mean(), 2)
            stat["Std Dev"] = round(col_data.std(), 2)
        else:
            stat["Min"] = "-"
            stat["Max"] = "-"
            stat["Mean"] = "-"
            stat["Std Dev"] = "-"
        stats.append(stat)
    return pd.DataFrame(stats)