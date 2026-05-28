import json
import os
import random
import urllib.error
import urllib.request
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")


class LLMConfigError(Exception):
    """Raised when the backend AI service is not configured."""


class LLMServiceError(Exception):
    """Raised when the configured AI service cannot complete the request."""


RETRYABLE_HTTP_STATUS_CODES = {429, 500, 502, 503, 504}


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
    timeout_seconds: int
    retry_attempts: int


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
        base_url = "https://token-plan-cn.xiaomimimo.com/v1" if api_key.startswith("tp-") else "https://api.mimo-v2.com/v1"
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
        timeout_seconds=_read_int_alias("LLM_TIMEOUT_SECONDS", "AI_TIMEOUT_SECONDS", 120),
        retry_attempts=max(1, _read_int_alias("LLM_RETRY_ATTEMPTS", "AI_RETRY_ATTEMPTS", 2)),
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


def _retry_delay_seconds(attempt: int, headers: Optional[object] = None) -> float:
    retry_after = None
    if headers is not None:
        retry_after = getattr(headers, "get", lambda *_: None)("Retry-After")
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except (TypeError, ValueError):
            pass
    return min((2 ** attempt) + random.random(), 8.0)


def _read_http_error_body(exc: urllib.error.HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="ignore").strip()
    except Exception:
        return ""
    try:
        data = json.loads(body)
        body = str(data.get("error", {}).get("message") or body).strip()
    except (TypeError, json.JSONDecodeError):
        pass
    if "502 Bad Gateway" in body:
        return "上游 AI 服务网关错误：502 Bad Gateway"
    if "<html" in body.lower():
        return "上游 AI 服务返回了网关错误页面"
    return body[:1000]


def _is_retryable_url_error(reason: object) -> bool:
    reason_text = str(reason).lower()
    winerror = getattr(reason, "winerror", None)
    errno = getattr(reason, "errno", None)
    retry_markers = [
        "timed out",
        "timeout",
        "10060",
        "没有正确答复",
        "主机没有反应",
        "连接尝试失败",
        "unexpected_eof",
        "eof occurred",
    ]
    return winerror == 10060 or errno == 10060 or any(marker in reason_text for marker in retry_markers)


def chat_completion(
    messages: List[Dict[str, str]],
    max_tokens: Optional[int] = None,
    timeout_seconds: Optional[int] = None,
    retry_attempts: Optional[int] = None,
) -> Dict[str, str]:
    config = get_llm_config()
    token_limit = max_tokens if max_tokens and max_tokens > 0 else config.max_tokens
    request_timeout = timeout_seconds if timeout_seconds and timeout_seconds > 0 else config.timeout_seconds
    attempt_limit = max(1, retry_attempts if retry_attempts and retry_attempts > 0 else config.retry_attempts)
    payload = {
        "model": config.model,
        "messages": messages,
        "temperature": config.temperature,
    }
    if config.provider.lower() == "mimo":
        payload["max_completion_tokens"] = token_limit
        payload["thinking"] = {"type": "disabled"}
    else:
        payload["max_tokens"] = token_limit

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

    last_error: Optional[LLMServiceError] = None
    for attempt in range(attempt_limit):
        try:
            with urllib.request.urlopen(request, timeout=request_timeout) as response:
                response_data = response.read().decode("utf-8")
            break
        except urllib.error.HTTPError as exc:
            error_body = _read_http_error_body(exc)
            if exc.code in RETRYABLE_HTTP_STATUS_CODES and attempt < attempt_limit - 1:
                time.sleep(_retry_delay_seconds(attempt, exc.headers))
                last_error = LLMServiceError(
                    f"AI 服务临时错误（HTTP {exc.code}）：{error_body or exc.reason}，正在重试"
                )
                continue
            raise LLMServiceError(f"AI 服务调用失败（HTTP {exc.code}）：{error_body or exc.reason}") from exc
        except urllib.error.URLError as exc:
            reason = str(exc.reason)
            if attempt < attempt_limit - 1 and _is_retryable_url_error(exc.reason):
                time.sleep(_retry_delay_seconds(attempt))
                last_error = LLMServiceError(f"AI 服务连接超时：{reason}，正在重试")
                continue
            raise LLMServiceError(f"AI 服务连接失败：{reason}") from exc
        except TimeoutError as exc:
            if attempt < attempt_limit - 1:
                time.sleep(_retry_delay_seconds(attempt))
                last_error = LLMServiceError("AI 服务响应超时，正在重试")
                continue
            raise LLMServiceError("AI 服务响应超时，请稍后重试") from exc
    else:
        if last_error:
            raise last_error
        raise LLMServiceError("AI 服务调用失败，请稍后重试")

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
