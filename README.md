HealthWise Connect 🩺

HealthWise Connect is a community health awareness# HealthWise Connect — AI chatbot fix

1. Upload `App.py` (rename `HealthWise_Connect_AI_Chat_Fixed.py` to `App.py`) and `requirements.txt` to the root of your GitHub repository.
2. Deploy/redeploy in Streamlit Community Cloud with main file path `App.py`.
3. For a secure permanent configuration, add this in Streamlit Cloud → App settings → Secrets:

```toml
OPENAI_API_KEY = "your-real-openai-api-key"
```

Alternatively, the Health Chat page has a session-only key field for testing. The key entered there is not saved to the app database or GitHub and will need to be entered again in a new session. OpenAI API usage may incur charges; a ChatGPT subscription does not automatically include API credits. Never commit an API key to GitHub.

