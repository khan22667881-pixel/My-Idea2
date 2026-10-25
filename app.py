"""Subject Explorer - pick a field and see its scope, importance and more.

Uses Streamlit for the UI and the Gemini Flash model through Google's REST
API (via `requests`), so no Google SDK has to be installed.
"""

import json
import os

import requests
import streamlit as st

DEFAULT_MODEL = "gemini-3.8-flash"
FALLBACK_MODELS = ["gemini-3.7-flash"]  # tried only if the main model returns 404
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

SUBJECTS = [
    "Computer Science",
    "Artificial Intelligence",
    "Data Science",
    "Cybersecurity",
    "Medicine",
    "Nursing",
    "Pharmacy",
    "Psychology",
    "Mechanical Engineering",
    "Electrical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Business Administration",
    "Economics",
    "Accounting & Finance",
    "Law",
    "Physics",
    "Chemistry",
    "Biology",
    "Mathematics",
    "Environmental Science",
    "Education",
    "Journalism & Media",
    "Architecture",
    "Graphic Design",
]

SECTIONS = [
    ("overview", "Overview"),
    ("scope", "Scope"),
    ("key_points", "Key Points"),
    ("importance", "Importance"),
    ("related_subjects", "Relationship With Other Subjects"),
    ("future", "Future Outlook"),
]

PROMPT = """You are an academic and career advisor. Explain the subject "{subject}" to a student.
Return ONLY a JSON object (no markdown, no code fences) with exactly these keys:
- "overview": string, 2-3 sentences describing the subject.
- "scope": list of 5-7 strings, areas, career paths and opportunities.
- "key_points": list of 5-7 strings, core topics or skills studied.
- "importance": list of 4-6 strings, why the subject matters to society and individuals.
- "related_subjects": list of 4-6 objects, each with "subject" and "connection" strings.
- "future": list of 4-6 strings, trends and where the field is heading.
Keep every string concise and factual."""


def get_api_key():
    """Read the key from Streamlit secrets or the environment."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.environ.get("GEMINI_API_KEY", "")


def get_model():
    """Model name from secrets/env (GEMINI_MODEL), else the default."""
    try:
        name = st.secrets.get("GEMINI_MODEL", "")
    except Exception:
        name = ""
    return name or os.environ.get("GEMINI_MODEL", "") or DEFAULT_MODEL


def parse_json(text):
    """Parse model output into a dict, tolerating code fences or extra text."""
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def call_gemini(model, body, api_key):
    """POST one request; return the Response. Raises RuntimeError on network failure."""
    try:
        return requests.post(
            API_URL.format(model=model),
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json=body,
            timeout=60,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Network error while contacting Gemini: {exc}") from exc


def fetch_subject_info(subject, api_key, model=None):
    """Call Gemini and return the parsed dict. Raises RuntimeError on failure."""
    body = {
        "contents": [{"parts": [{"text": PROMPT.format(subject=subject)}]}],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json",
        },
    }
    models = [model or get_model()] + FALLBACK_MODELS
    resp = None
    for name in models:
        resp = call_gemini(name, body, api_key)
        if resp.status_code != 404:  # 404 = model unavailable, try the next one
            break

    if resp.status_code != 200:
        try:
            detail = resp.json().get("error", {}).get("message", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(f"Gemini API error ({resp.status_code}): {detail}")

    try:
        parts = resp.json()["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts)
        return parse_json(text)
    except (KeyError, IndexError, ValueError, TypeError) as exc:
        raise RuntimeError("Could not read the model's response. Please try again.") from exc


def as_list(value):
    if isinstance(value, list):
        return value
    if value:
        return [value]
    return []


def render(subject, data):
    st.header(subject)
    if data.get("overview"):
        st.write(data["overview"])

    for key, title in SECTIONS[1:]:
        items = as_list(data.get(key))
        if not items:
            continue
        st.subheader(title)
        for item in items:
            if isinstance(item, dict):
                name = item.get("subject", "")
                link = item.get("connection", "")
                st.markdown(f"- **{name}**: {link}")
            else:
                st.markdown(f"- {item}")


def main():
    st.set_page_config(page_title="Subject Explorer", page_icon="🎓", layout="centered")
    st.title("🎓 Subject Explorer")
    st.caption("Choose a field to see its scope, importance and future.")

    api_key = get_api_key()
    if not api_key:
        st.error(
            "Gemini API key not found. Add `GEMINI_API_KEY` in Streamlit "
            "Settings > Secrets (or as an environment variable locally)."
        )
        st.stop()

    choice = st.selectbox("Select a subject / field", SUBJECTS + ["Other (type your own)"])
    subject = choice
    if choice.startswith("Other"):
        subject = st.text_input("Enter your subject").strip()

    if st.button("Explore", type="primary"):
        if not subject:
            st.warning("Please enter a subject.")
        else:
            with st.spinner(f"Exploring {subject}..."):
                try:
                    st.session_state["result"] = (subject, fetch_subject_info(subject, api_key))
                except RuntimeError as exc:
                    st.session_state.pop("result", None)
                    st.error(str(exc))

    if "result" in st.session_state:
        render(*st.session_state["result"])


if __name__ == "__main__":
    main()
