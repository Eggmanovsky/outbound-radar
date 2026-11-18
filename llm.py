# -*- coding: utf-8 -*-
"""OpenAI 兼容的轻量封装：单次调用、强制 JSON、失败可回落。

设计要点：
- 只读环境变量，不把 key 写进代码；
- 一次调用只拿一个 JSON 对象，前端负责渲染，避免自由文本不可控；
- 任何异常都不抛给界面，返回 {"_error": ...}，由调用方决定是否用离线兜底。
"""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
FALLBACK_MODEL = "qwen3.8-flash"
TIMEOUT_SECONDS = 60

FREE_MODELS_FILE = Path(__file__).with_name("free_models.json")


def api_key() -> str | None:
    return os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY") or None


def model_name() -> str:
    """优先级：环境变量 LLM_MODEL > free_models.json 的 default_model > 兜底常量。"""
    return os.getenv("LLM_MODEL") or _catalog().get("default_model") or FALLBACK_MODEL


def base_url() -> str:
    return os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL)


def enabled() -> bool:
    return bool(api_key())


def status() -> dict[str, Any]:
    return {"enabled": enabled(), "model": model_name(), "base_url": base_url()}


@lru_cache(maxsize=1)
def _catalog() -> dict:
    """读取免费模型名单；文件缺失或损坏时返回空目录（等于「全部不免费」）。"""
    try:
        return json.loads(FREE_MODELS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"models": []}


def _free_models() -> dict[str, dict]:
    return {m["id"]: m for m in _catalog().get("models", []) if m.get("id")}


def model_kind(name: str | None = None) -> str:
    entry = _free_models().get(name or model_name())
    return (entry or {}).get("kind", "chat")


def model_is_free(name: str | None = None) -> bool:
    entry = _free_models().get(name or model_name())
    return bool(entry and entry.get("free"))


def model_warning(name: str | None = None) -> str | None:
    """当前模型不适合直接调用时返回警告文案；安全则返回 None。"""
    target = name or model_name()
    entry = _free_models().get(target)
    if entry is None:
        return f"模型「{target}」不在 free_models.json 名单里，调用可能产生费用。"
    if entry.get("kind") == "image":
        return f"模型「{target}」是图像模型，不能用于文本生成，调用会失败。"
    if not entry.get("free"):
        quota = entry.get("free_quota", "未知")
        return f"模型「{target}」没有免费额度（{quota}），每次生成都会产生费用。"
    if entry.get("expires"):
        return f"模型「{target}」的免费额度将于 {entry['expires']} 到期。"
    return None


def _strip_fence(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _extract_json(text: str) -> dict:
    candidate = _strip_fence(text)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    start, end = candidate.find("{"), candidate.rfind("}")
    if start != -1 and end > start:
        return json.loads(candidate[start : end + 1])
    raise ValueError("模型未返回合法 JSON")


def chat_json(system: str, user: str, temperature: float = 0.6) -> dict | None:
    """没有 key 返回 None；调用失败返回 {"_error": "..."}。"""
    if not enabled():
        return None

    from openai import OpenAI  # 延迟导入，离线模式下不需要

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    try:
        client = OpenAI(api_key=api_key(), base_url=base_url(), timeout=TIMEOUT_SECONDS)
        try:
            resp = client.chat.completions.create(
                model=model_name(),
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
        except Exception as exc:  # 部分第三方模型不支持 json_object，退回普通调用
            text = str(exc).lower()
            if "response_format" not in text and "json_object" not in text:
                raise
            resp = client.chat.completions.create(
                model=model_name(),
                messages=messages,
                temperature=temperature,
            )
        content = resp.choices[0].message.content or ""
        return _extract_json(content)
    except Exception as exc:  # noqa: BLE001 - 演示场景下统一兜底
        return {"_error": f"{type(exc).__name__}: {exc}"}
