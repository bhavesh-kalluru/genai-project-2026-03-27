import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

st.set_page_config(page_title="GenAI Text Summarizer", page_icon="🧠", layout="centered")

st.title("🧠 GenAI Text Summarizer")
st.caption("A simple generative-AI app that turns long text into a concise summary.")

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

with st.sidebar:
    st.header("Settings")
    max_words = st.slider("Target summary length", 30, 250, 100, 10)
    st.info("Set OPENAI_API_KEY in a .env file before running the app.")

text = st.text_area(
    "Paste your text",
    height=320,
    placeholder="Paste an article, meeting notes, documentation, or any other text here...",
)

if st.button("Generate Summary", type="primary", use_container_width=True):
    if not text.strip():
        st.warning("Please enter some text first.")
    elif not api_key:
        st.error("OPENAI_API_KEY is not configured. Copy .env.example to .env and add your key.")
    else:
        client = OpenAI(api_key=api_key)
        prompt = f"""Summarize the text below in about {max_words} words.\n\nRules:\n- Keep the main ideas and important facts.\n- Use clear, professional language.\n- Do not invent information.\n- Return only the summary.\n\nTEXT:\n{text}"""

        with st.spinner("Generating summary..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful text summarization assistant.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )
                summary = response.choices[0].message.content.strip()
                st.subheader("Summary")
                st.write(summary)
            except Exception as exc:
                st.error(f"Unable to generate the summary: {exc}")

st.divider()
st.caption("Built with Python, Streamlit, and an OpenAI-compatible generative AI model.")
