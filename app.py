"""Subject Explorer - pick a field and get its scope, key points, importance,
relationships with other subjects, and future outlook, powered by Gemini Flash."""

import json
import os
import re

import streamlit as st
from google import genai
from google.genai import types

DEFAULT_MODEL = "gemini-2.5-flash"

SUBJECTS = {
    "Sciences": ["Physics", "Chemistry", "Biology", "Mathematics", "Astronomy",
                 "Environmental Science", "Neuroscience"],
    "Technology & Engineering": ["Computer Science", "Artificial Intelligence",
                                 "Data Science", "Cybersecurity", "Electrical Engineering",
                                 "Mechanical Engineering", "Civil Engineering",
                                 "Robotics"],
    "Health & Medicine": ["Medicine", "Pharmacy", "Nursing", "Public Health",
                          "Psychology", "Nutrition"],
    "Business & Social Sciences": ["Economics", "Business Administration", "Finance",
                                   "Marketing", "Law", "Political Science",
                                   "Sociology", "Education"],
    "Arts & Humanities": ["History", "Philosophy", "Literature", "Linguistics",
                          "Architecture", "Music", "Graphic Design"],
}
OTHER_OPTION = "Other (type your own)"

SECTION_KEYS = ["scope", "key_points", "importance", "relationships", "future"]


# --------------------------------------------------------------------------- #
# Helpers (no Streamlit calls so they are easy to test)
# --------------------------------------------------------------------------- #
def build_prompt(subject: str) -> str:
    return f"""You are an academic advisor. Explain the subject "{subject}" to a curious student.

Return ONLY a JSON object (no markdown fences, no extra text) with exactly these keys:
{{
  "overview": "2-3 sentence plain-language definition of the subject",
  "scope": ["5-7 short strings: major branches, areas of study, and career/application areas"],
  "key_points": [{{"title": "core concept or topic", "explanation": "1-2 sentence explanation"}}],
  "importance": ["4-6 short strings: why this subject matters to society, industry and individuals"],
  "relationships": [{{"subject": "related subject name", "connection": "1-2 sentences on how they connect"}}],
  "future": ["4-6 short strings: emerging trends, opportunities and challenges ahead"]
}}

Rules: give 5-8 items in key_points and 4-7 items in relationships. Be accurate,
specific and concise. Do not invent statistics."""


def parse_json_response(text: str) -> dict:
    """Parse model output into a dict, tolerating markdown fences or extra prose."""
    if not text or not text.strip():
        raise ValueError("The model returned an empty response.")
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end <= start:
            raise ValueError("Could not find JSON in the model response.")
        data = json.loads(cleaned[start:end + 1])
    if not isinstance(data, dict):
        raise ValueError("Model response was not a JSON object.")
    return data


def as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def get_api_key() -> str:
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:  # no secrets file locally
        key = ""
    return key or os.environ.get("GEMINI_API_KEY", "")


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_subject_info(subject: str, api_key: str, model: str) -> dict:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=build_prompt(subject),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4,
        ),
    )
    return parse_json_response(response.text)


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #
def render_results(subject: str, data: dict) -> None:
    st.header(subject)
    if data.get("overview"):
        st.info(data["overview"])

    tabs = st.tabs(["Scope", "Key Points", "Importance", "Related Subjects", "Future"])

    with tabs[0]:
        for item in as_list(data.get("scope")):
            st.markdown(f"- {item}")

    with tabs[1]:
        for item in as_list(data.get("key_points")):
            if isinstance(item, dict):
                with st.expander(str(item.get("title", "Topic")), expanded=False):
                    st.write(item.get("explanation", ""))
            else:
                st.markdown(f"- {item}")

    with tabs[2]:
        for item in as_list(data.get("importance")):
            st.markdown(f"- {item}")

    with tabs[3]:
        for item in as_list(data.get("relationships")):
            if isinstance(item, dict):
                st.markdown(f"**{item.get('subject', 'Subject')}** - {item.get('connection', '')}")
            else:
                st.markdown(f"- {item}")

    with tabs[4]:
        for item in as_list(data.get("future")):
            st.markdown(f"- {item}")


def main() -> None:
    st.set_page_config(page_title="Subject Explorer", page_icon="🎓", layout="wide")
    st.title("🎓 Subject Explorer")
    st.caption("Pick a field and discover its scope, key points, importance, "
               "connections to other subjects, and future.")

    api_key = get_api_key()
    with st.sidebar:
        st.header("Settings")
        if not api_key:
            api_key = st.text_input("Gemini API key", type="password",
                                    help="Get a free key at https://aistudio.google.com/apikey")
        model = st.text_input("Gemini model", value=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL))
        st.markdown("---")
        st.caption("AI-generated content can contain mistakes. Verify important details.")

    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category", list(SUBJECTS.keys()) + [OTHER_OPTION])
    with col2:
        if category == OTHER_OPTION:
            subject = st.text_input("Type a subject / field", max_chars=80).strip()
        else:
            subject = st.selectbox("Subject", SUBJECTS[category])

    if st.button("Explore", type="primary", disabled=not subject):
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar.")
            return
        with st.spinner(f"Exploring {subject}..."):
            try:
                st.session_state["result"] = (subject, fetch_subject_info(subject, api_key, model.strip() or DEFAULT_MODEL))
            except Exception as exc:  # show a friendly message instead of a traceback
                st.session_state.pop("result", None)
                st.error(f"Something went wrong: {exc}")

    if "result" in st.session_state:
        render_results(*st.session_state["result"])


if __name__ == "__main__":
    main()
