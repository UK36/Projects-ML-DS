import os
from pathlib import Path
import streamlit as st
from supabase import create_client, Client
from src.database.local_db import LocalDatabaseClient

def _load_env_files():
    try:
        from dotenv import load_dotenv
        for candidate in [
            Path.cwd() / ".env",
            Path(__file__).resolve().parents[2] / ".env",
            Path(__file__).resolve().parents[3] / ".env"
        ]:
            if candidate.is_file():
                load_dotenv(dotenv_path=str(candidate), override=True)
    except ImportError:
        pass

_load_env_files()

def get_secret(key: str, default: str = "") -> str:
    """Retrieve secret from environment variable, .env, or streamlit secrets."""
    _load_env_files()

    # 1. Environment variable (from .env or OS)
    val = os.getenv(key)
    if val:
        return val.strip()

    # 2. Streamlit secrets (.streamlit/secrets.toml)
    try:
        if key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass

    # 3. Direct .env file fallback parser
    for candidate in [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[2] / ".env",
        Path(__file__).resolve().parents[3] / ".env"
    ]:
        if candidate.is_file():
            try:
                for line in candidate.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == key:
                            return v.strip().strip('"').strip("'")
            except Exception:
                pass

    return default

def is_supabase_configured() -> bool:
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")
    return bool(url and key and "your-project-id" not in url.lower())

_client = None

def get_supabase_client():
    global _client
    if is_supabase_configured():
        if _client is None or isinstance(_client, LocalDatabaseClient):
            url = get_secret("SUPABASE_URL")
            key = get_secret("SUPABASE_KEY")
            _client = create_client(url, key)
        return _client
    else:
        # Automatic local SQLite database fallback for offline / immediate operation
        if _client is None or not isinstance(_client, LocalDatabaseClient):
            _client = LocalDatabaseClient()
        return _client

class _SupabaseProxy:
    def __getattr__(self, name):
        return getattr(get_supabase_client(), name)

supabase = _SupabaseProxy()
