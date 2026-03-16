# ESP Design App

## Setup & Run (Standard Python venv)

1.  **Environment Setup** (Run once):
    ```powershell
    python -m venv venv
    .\venv\Scripts\pip install -r requirements.txt
    ```

2.  **Run Application**:
    ```powershell
    .\venv\Scripts\python -m streamlit run app.py
    ```

    *Using the full path `.\venv\Scripts\python` ensures you use the checks inside the virtual environment without needing to activate it manually.*

## Features
- **Sidebar**: Well & Reservoir inputs.
- **Interactive Charts**: Plotly integration for Pump Curves.
- **Workflow**: 8-step design process.
