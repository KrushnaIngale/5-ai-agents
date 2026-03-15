import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def _load_streamlit_secrets() -> None:
    try:
        import streamlit as st
    except Exception:
        return

    try:
        for key in ("DEFAULT_PROVIDER", "GEMINI_KEY", "GEMINI_MODEL", "GROQ_KEY", "GROQ_MODEL"):
            if key in st.secrets:
                os.environ.setdefault(key, str(st.secrets[key]))
    except Exception:
        return


@dataclass
class Settings:
    gemini_key: str
    groq_key: str
    gemini_model: str
    groq_model: str
    default_provider: str
    mock_mode: bool


def get_settings() -> Settings:
    _load_dotenv()
    _load_streamlit_secrets()

    gemini_key = os.getenv("GEMINI_KEY", "")
    groq_key = os.getenv("GROQ_KEY", "")

    return Settings(
        gemini_key=gemini_key,
        groq_key=groq_key,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        default_provider=os.getenv("DEFAULT_PROVIDER", "groq").lower(),
        mock_mode=not any([gemini_key, groq_key]),
    )