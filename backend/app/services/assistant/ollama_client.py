"""
ollama_client.py — the only file that talks to the LLM.

CONCEPT — LLM (Large Language Model):
  A model trained on huge amounts of text to predict the next word.
  Given a prompt, it continues writing. Good at language; it does NOT
  know our private data (our transactions or policies). That is why we
  give it data (analytics numbers + RAG passages) inside the prompt.

CONCEPT — Ollama:
  A program that runs open LLMs (like Llama 3.2) on your own machine and
  exposes them through a simple HTTP API at http://localhost:11434.
  So calling an LLM is just an HTTP POST, like calling any REST API.

  A "chat" is a list of messages with roles:
    system    -> the rules/personality ("you are an analyst...")
    user      -> the question
    assistant -> the model's reply
"""

import httpx

from app.config.settings import settings


def chat(messages: list[dict], json_mode: bool = False) -> str:
    """Send messages to Ollama and return the model's reply text."""
    payload = {
        "model": settings.ollama_chat_model,
        "messages": messages,
        "stream": False,                      # wait for the full answer at once
        "options": {"temperature": 0},        # 0 = least random, most repeatable
    }
    if json_mode:
        payload["format"] = "json"            # force the reply to be valid JSON

    # The FIRST call after Ollama starts loads the model into memory (can take
    # 1-2 minutes on a laptop). Later calls take a few seconds. So allow 300 s.
    response = httpx.post(f"{settings.ollama_base_url}/api/chat", json=payload, timeout=300)
    response.raise_for_status()               # turn HTTP 4xx/5xx into a Python error
    return response.json()["message"]["content"]


def is_available() -> bool:
    """Quick check used by /health: is the Ollama server reachable?"""
    try:
        return httpx.get(f"{settings.ollama_base_url}/api/version", timeout=3).is_success
    except httpx.HTTPError:
        return False
