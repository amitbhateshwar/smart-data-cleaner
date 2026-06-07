import pandas as pd
import numpy as np

def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    return df, removed

def fix_dtypes(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    changes = []
    for col in df.columns:
        if df[col].dtype == object:
            # Try converting to numeric
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() / max(len(df), 1) > 0.8:
                df[col] = converted
                changes.append(f"`{col}` → numeric")
                continue
            # Try converting to datetime
            try:
                converted_dt = pd.to_datetime(df[col], errors="coerce")
                if converted_dt.notna().sum() / max(len(df), 1) > 0.8:
                    df[col] = converted_dt
                    changes.append(f"`{col}` → datetime")
            except Exception:
                pass
    return df, changes

def handle_missing_values(df: pd.DataFrame, strategy: str = "mean") -> tuple[pd.DataFrame, dict]:
    report = {}
    for col in df.columns:
        missing = df[col].isnull().sum()
        if missing == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            if strategy == "mean":
                fill_val = df[col].mean()
            elif strategy == "median":
                fill_val = df[col].median()
            elif strategy == "zero":
                fill_val = 0
            else:
                fill_val = df[col].mean()
            df[col] = df[col].fillna(fill_val)
            report[col] = f"{missing} missing → filled with {strategy} ({round(fill_val, 2)})"

        else:
            fill_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(fill_val)
            report[col] = f"{missing} missing → filled with mode ('{fill_val}')"

    return df, report

def remove_missing_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    before = len(df)
    df = df.dropna()
    removed = before - len(df)
    return df, removed

def handle_outliers(df: pd.DataFrame, method: str = "clip") -> tuple[pd.DataFrame, dict]:
    report = {}
    numeric_cols = df.select_dtypes(include=np.number).columns

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = ((df[col] < lower) | (df[col] > upper)).sum()

        if outliers == 0:
            continue

        if method == "clip":
            df[col] = df[col].clip(lower=lower, upper=upper)
            report[col] = f"{outliers} outliers clipped to [{round(lower,2)}, {round(upper,2)}]"
        elif method == "remove":
            before = len(df)
            df = df[(df[col] >= lower) & (df[col] <= upper)]
            report[col] = f"{outliers} outlier rows removed"

    return df, report