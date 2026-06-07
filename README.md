# 🧹 Smart Data Cleaner

An ML-ready data cleaning pipeline built with Python and Streamlit.
Upload a CSV, JSON, or Excel file (or paste a URL) and get back a
clean, processed dataset in seconds.

## Features

- **Data Ingestion** — CSV, JSON, Excel upload or direct URL
- **EDA Profiling** — column stats, null heatmap, distributions
- **Cleaning** — missing value imputation, duplicate removal, dtype fixing, outlier handling
- **Transforms** — categorical encoding (one-hot / label), numeric normalization (MinMax / Standard / Log)
- **Download** — cleaned CSV + full change report

## Getting Started

### 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/smart-data-cleaner.git
cd smart-data-cleaner

### 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate.bat   # Windows
source venv/bin/activate    # Mac/Linux

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run the app
streamlit run app/main.py

## Project Structure

smart-data-cleaner/
├── app/
│   ├── main.py              # Streamlit UI
│   ├── style.css            # Custom styling
│   └── utils/
│       ├── ingestor.py      # File & URL loading
│       ├── cleaner.py       # Cleaning engine
│       ├── profiler.py      # EDA & visualizations
│       └── transformer.py   # Encoding & normalization
├── requirements.txt
└── README.md

## Tech Stack

- Python 3.11
- Streamlit
- Pandas
- Scikit-learn
- Matplotlib / Seaborn

## Author

Made with ❤️ by **Amit Bhateshwar**

- GitHub: [github.com/amitbhateshwar](https://github.com/amitbhateshwar)