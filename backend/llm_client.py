import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import urljoin

from dotenv import load_dotenv


load_dotenv()


class LLMConfigError(Exception):
    """Raised when the backend AI service is not configured."""


class LLMServiceError(Exception):
    """Raised when the configured AI service cannot complete the request."""


@dataclass
class LLMConfig:
    provider: str
    api_key: str
    base_url: str
    model: str
    chat_path: str
    temperature: float
    max_tokens: int
    api_key_header: str


def _read_float(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value in (None, ""):
        return default
    try:
        return float(raw_value)
    except ValueError as exc:
        raise LLMConfigError(f"{name} 配置不是有效数字") from exc


def _read_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value in (None, ""):
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise LLMConfigError(f"{name} 配置不是有效整数") from exc


def _read_env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return default


def _read_float_alias(primary: str, fallback: str, default: float) -> float:
    raw_value = _read_env(primary, fallback)
    if not raw_value:
        return default
    try:
        return float(raw_value)
    except ValueError as exc:
        raise LLMConfigError(f"{primary}/{fallback} 配置不是有效数字") from exc


def _read_int_alias(primary: str, fallback: str, default: int) -> int:
    raw_value = _read_env(primary, fallback)
    if not raw_value:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise LLMConfigError(f"{primary}/{fallback} 配置不是有效整数") from exc


def get_llm_config() -> LLMConfig:
    provider = _read_env("LLM_PROVIDER", default="mimo") or "mimo"
    api_key = _read_env("LLM_API_KEY", "MIMO_API_KEY")
    base_url = _read_env("LLM_BASE_URL", "MIMO_API_URL", "MIMO_BASE_URL")
    model = _read_env("LLM_MODEL", "MIMO_MODEL")
    if not base_url and provider.lower() == "mimo":
        base_url = "https://token-plan-cn.xiaomimimo.com/v1" if api_key.startswith("tp-") else "https://api.xiaomimimo.com/v1"
    chat_path = _read_env("LLM_CHAT_PATH", "MIMO_CHAT_PATH", default="/chat/completions") or "/chat/completions"
    api_key_header = _read_env("LLM_API_KEY_HEADER", "MIMO_API_KEY_HEADER")
    if not api_key_header:
        api_key_header = "api-key" if provider.lower() == "mimo" else "Authorization"

    if not api_key:
        raise LLMConfigError("AI 服务尚未配置，请在后端 .env 中配置 LLM_API_KEY 或 MIMO_API_KEY")
    if not base_url:
        raise LLMConfigError("AI 服务尚未配置，请在后端 .env 中配置 LLM_BASE_URL、MIMO_API_URL 或 MIMO_BASE_URL")
    if not model:
        raise LLMConfigError("AI 服务尚未配置，请在后端 .env 中配置 LLM_MODEL 或 MIMO_MODEL")

    return LLMConfig(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
        chat_path=chat_path,
        temperature=_read_float_alias("LLM_TEMPERATURE", "AI_TEMPERATURE", 0.4),
        max_tokens=_read_int_alias("LLM_MAX_TOKENS", "AI_MAX_TOKENS", 1200),
        api_key_header=api_key_header,
    )


def get_llm_identity() -> Dict[str, str]:
    return {
        "provider": _read_env("LLM_PROVIDER", default="mimo") or "mimo",
        "model": _read_env("LLM_MODEL", "MIMO_MODEL"),
    }


def _build_chat_url(base_url: str, chat_path: str) -> str:
    clean_base = base_url.rstrip("/") + "/"
    clean_path = chat_path.lstrip("/")
    return urljoin(clean_base, clean_path)


def chat_completion(messages: List[Dict[str, str]]) -> Dict[str, str]:
    config = get_llm_config()
    payload = {
        "model": config.model,
        "messages": messages,
        "temperature": config.temperature,
    }
    if config.provider.lower() == "mimo":
        payload["max_completion_tokens"] = config.max_tokens
    else:
        payload["max_tokens"] = config.max_tokens

    auth_headers = {
        "Content-Type": "application/json",
    }
    if config.api_key_header.lower() == "authorization":
        auth_headers["Authorization"] = f"Bearer {config.api_key}"
    else:
        auth_headers[config.api_key_header] = config.api_key

    request = urllib.request.Request(
        _build_chat_url(config.base_url, config.chat_path),
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=auth_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_data = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise LLMServiceError(f"AI 服务调用失败（HTTP {exc.code}）：{error_body or exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise LLMServiceError(f"AI 服务连接失败：{exc.reason}") from exc
    except TimeoutError as exc:
        raise LLMServiceError("AI 服务响应超时，请稍后重试") from exc

    try:
        data = json.loads(response_data)
        answer = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise LLMServiceError("AI 服务返回格式异常，无法解析回答") from exc

    return {
        "answer": str(answer).strip(),
        "provider": config.provider,
        "model": config.model,
    }
