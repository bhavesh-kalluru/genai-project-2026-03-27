# 🧠 GenAI Text Summarizer

A simple portfolio-ready Generative AI application that summarizes long text using an LLM through the OpenAI Python SDK and a Streamlit interface.

## Features

- Paste articles, notes, documentation, or other text
- Choose a target summary length
- Generate concise summaries with an LLM
- Simple Streamlit web interface
- API key loaded from environment variables
- No secrets committed to GitHub
- Easy to run locally

## Project Structure

```text
genai_text_summarizer/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Tech Stack

- Python
- Streamlit
- OpenAI Python SDK
- python-dotenv
- Generative AI / LLMs

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

Copy `.env.example` to `.env` and add your API key:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Never commit your real `.env` file or API key.

### 4. Run the app

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## How It Works

1. The user enters text in the Streamlit interface.
2. The app builds a focused summarization prompt.
3. The prompt is sent to the configured generative AI model.
4. The model returns a concise summary.
5. Streamlit displays the generated result.

## Example Use Cases

- Summarizing meeting notes
- Quickly understanding long articles
- Condensing technical documentation
- Creating executive summaries
- Preparing study notes

## Security Notes

API credentials are read from environment variables. The `.gitignore` file prevents `.env` from being committed accidentally.

## Future Improvements

- PDF and DOCX upload support
- URL/article summarization
- Multiple summary styles
- Streaming model responses
- Summary history
- Token/cost tracking
- RAG-based document summarization

## License

MIT
