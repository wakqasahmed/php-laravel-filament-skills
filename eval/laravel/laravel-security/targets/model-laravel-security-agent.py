#!/usr/bin/env python3
"""Model-invoking target agent for the laravel-security outcome evaluation."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path


def extract_json(raw_text: str) -> dict:
    text = raw_text.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


def invoke_provider(model: str, system_prompt: str, user_prompt: str) -> str:
    url = (
        os.environ.get("HARNESS_MODEL_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("OPENROUTER_BASE_URL")
        or "https://openrouter.ai/api/v1/chat/completions"
    )
    api_key = (
        os.environ.get("OPENROUTER_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("HARNESS_API_KEY", "")
    )

    if not api_key and "127.0.0.1" not in url and "localhost" not in url:
        raise SystemExit(
            f"No model provider credentials configured for '{model}'. "
            "Set OPENROUTER_API_KEY, OPENAI_API_KEY, or HARNESS_MODEL_URL."
        )

    if os.environ.get("HARNESS_LOG_INVOCATIONS") == "1":
        sys.stderr.write(
            f"[model-agent] provider={url} model={model} prompt_len={len(user_prompt)}\n"
        )
        sys.stderr.flush()

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.0,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0]["message"]["content"]
    if "content" in data and isinstance(data["content"], list):
        return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
    raise SystemExit(f"Unexpected provider response structure: {data}")


def main() -> int:
    payload = json.loads(sys.stdin.read())
    prompt = payload["prompt"]
    model = payload.get("model", "default-model")
    outcome_path = Path(payload["outcome_path"])
    skill_path = payload.get("skill_path")

    format_instruction = (
        "Return ONLY a valid JSON object with exact keys: 'decision', 'chosen_pattern', 'primary_reason'."
    )

    if skill_path and Path(skill_path).is_file():
        skill_text = Path(skill_path).read_text(encoding="utf-8")
        system_prompt = (
            "You are an expert security engineer evaluating Laravel security practices. "
            "Follow these skill guidelines strictly:\n\n"
            f"{skill_text}\n\n"
            f"{format_instruction}"
        )
    else:
        system_prompt = (
            "You are a helpful software engineering assistant evaluating Laravel security. "
            f"{format_instruction}"
        )

    raw_response = invoke_provider(model, system_prompt, prompt)
    artifact = extract_json(raw_response)
    artifact["model"] = model
    artifact["is_canned"] = False

    outcome_path.write_text(json.dumps(artifact, indent=2))
    print(raw_response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
