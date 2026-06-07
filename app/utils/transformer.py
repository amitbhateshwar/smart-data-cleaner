import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder

def encode_categoricals(df: pd.DataFrame, method: str = "onehot") -> tuple[pd.DataFrame, list]:
    report = []
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if not cat_cols:
        return df, ["No categorical columns found"]

    if method == "onehot":
        for col in cat_cols:
            if df[col].nunique() <= 15:
                dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
                report.append(f"`{col}` → one-hot encoded ({df.shape[1]} new columns)")
            else:
                report.append(f"`{col}` → skipped (too many unique values: {df[col].nunique()})")

    elif method == "label":
        le = LabelEncoder()
        for col in cat_cols:
            df[col] = le.fit_transform(df[col].astype(str))
            report.append(f"`{col}` → label encoded")

    return df, report


def normalize_numerics(df: pd.DataFrame, method: str = "minmax") -> tuple[pd.DataFrame, list]:
    report = []
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    if not numeric_cols:
        return df, ["No numeric columns found"]

    if method == "minmax":
        scaler = MinMaxScaler()
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
        report.append(f"Min-Max scaled {len(numeric_cols)} numeric columns → range [0, 1]")

    elif method == "standard":
        scaler = StandardScaler()
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
        report.append(f"Standard scaled {len(numeric_cols)} numeric columns → mean=0, std=1")

    elif method == "log":
        for col in numeric_cols:
            if (df[col] > 0).all():
                df[col] = np.log1p(df[col])
                report.append(f"`{col}` → log transformed")
            else:
                report.append(f"`{col}` → skipped log (contains zero/negative values)")

    return df, report