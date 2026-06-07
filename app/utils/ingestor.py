import pandas as pd
import requests
import io
import os

SUPPORTED_EXTENSIONS = [".csv", ".json", ".xlsx", ".xls"]

def load_from_upload(uploaded_file) -> pd.DataFrame:
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".csv":
        return pd.read_csv(uploaded_file)
    elif ext == ".json":
        return pd.read_json(uploaded_file)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def load_from_url(url: str) -> pd.DataFrame:
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise ConnectionError(f"Failed to fetch URL. Status code: {response.status_code}")

    content_type = response.headers.get("Content-Type", "")
    url_lower = url.lower()

    if ".csv" in url_lower or "text/csv" in content_type:
        return pd.read_csv(io.StringIO(response.text))
    elif ".json" in url_lower or "application/json" in content_type:
        return pd.read_json(io.StringIO(response.text))
    elif ".xlsx" in url_lower or ".xls" in url_lower:
        return pd.read_excel(io.BytesIO(response.content))
    else:
        try:
            return pd.read_csv(io.StringIO(response.text))
        except Exception:
            raise ValueError("Could not parse the URL content. Make sure it points to a CSV, JSON, or Excel file.")

def get_basic_info(df: pd.DataFrame) -> dict:
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }