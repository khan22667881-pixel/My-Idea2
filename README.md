# 🎓 Subject Explorer

Pick a subject or field and get an AI-generated overview of its **scope**, **key points**, **importance**, **relationship with other subjects** and **future outlook**.

Built with [Streamlit](https://streamlit.io) and the Gemini Flash model (called through the Gemini REST API, so no Google SDK is needed).

## Files

| File | Purpose |
|------|---------|
| `app.py` | The Streamlit app |
| `requirements.txt` | Python dependencies (`streamlit`, `requests`) |
| `README.md` | This file |

## Run locally

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Install and run:

```bash
pip install -r requirements.txt

# macOS / Linux
export GEMINI_API_KEY="your-key"
# Windows PowerShell
$env:GEMINI_API_KEY="your-key"

streamlit run app.py
```

Alternatively create `.streamlit/secrets.toml` (never commit it):

```toml
GEMINI_API_KEY = "your-key"
```

## Push to GitHub

```bash
git init
git add app.py requirements.txt README.md
git commit -m "Subject Explorer app"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Create the empty repo on github.com first. Keep all three files at the **root** of the repo.

## Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **Create app** > **Deploy a public app from GitHub**.
3. Choose your repo, branch `main`, main file path `app.py`.
4. Open **Advanced settings** > **Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your-key"
   ```
5. Click **Deploy**.

## Troubleshooting

- **Key not found**: add `GEMINI_API_KEY` in app Settings > Secrets, then reboot the app.
- **Dependency errors after editing requirements**: in the app menu choose *Manage app* > *Reboot app*.
- **Model not found**: change `MODEL` at the top of `app.py` to another Gemini Flash model name.
