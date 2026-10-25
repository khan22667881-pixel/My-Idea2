# My-Idea2
# 🎓 Subject Explorer

A Streamlit app where you pick a field (subject) and Gemini Flash explains:

- **Scope** – branches, areas of study, career and application areas
- **Key points** – the core concepts you should know
- **Importance** – why the subject matters
- **Inter-relationships** – how it connects to other subjects
- **Future** – trends, opportunities and challenges

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Get a free API key from https://aistudio.google.com/apikey, then either:

```bash
export GEMINI_API_KEY="your-key"     # Windows PowerShell: $env:GEMINI_API_KEY="your-key"
streamlit run app.py
```

or run it and paste the key into the sidebar.

Optional: set `GEMINI_MODEL` (default `gemini-2.5-flash`) or change the model in the sidebar.

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub (`app.py`, `requirements.txt`, `README.md` at the repo root).
2. Go to https://share.streamlit.io and click **Create app**.
3. Choose your repo, branch `main`, and main file `app.py`.
4. Open **Advanced settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your-key"
   ```
5. Click **Deploy**.

Never commit your API key to GitHub.

## Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI and Gemini call |
| `requirements.txt` | Dependencies (`streamlit`, `google-genai`) |
| `README.md` | This file |
