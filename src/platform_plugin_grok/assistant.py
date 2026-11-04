"""xAI's Responses API through the contract's client (liminal_lib.assistants.ResponsesAssistant: the
OpenAI-shaped request and answer), as xAI documents it at https://docs.x.ai (verified 2026-11-03):
POST /v1/responses with `input`, `instructions`, `max_output_tokens`, `store`; the answer's
`output[]` message items; `usage` with the vendor's own cost figure (`cost_in_nano_usd`: ten
thousand million to the dollar), which an Evaluation keeps as its cost."""
from __future__ import annotations

from typing import Any, Mapping

from liminal_lib.assistants import ResponsesAssistant
from liminal_lib.errors import NotEntitled, SourceError, Unauthorized

API = "https://api.x.ai"


class GrokAssistant(ResponsesAssistant):
    """Grok: the Responses API at api.x.ai with a bearer key; no user field (xAI's reference lists
    none); errors in xAI's `{code, error}` shape or the OpenAI one."""

    base_url = API
    user_field = ""  # the Responses reference lists no safety identifier or user field: nothing is sent about the account
    limit_prefixes = ("x-ratelimit-",)

    def error(self, status: int, body, message: str) -> SourceError | None:
        mapped = super().error(status, body, message)
        if mapped is not None:
            return mapped
        text = str((body or {}).get("error") or message) if isinstance(body, Mapping) else message
        low = text.lower()
        if status in (402, 403) or (status == 429 and ("credit" in low or "balance" in low or "quota" in low)):
            return NotEntitled(status, f"no credit for it: {text}")
        if status == 401:
            return Unauthorized(401, text)
        return None

    def final(self, status: int, body) -> bool:
        if super().final(status, body):
            return True
        text = str((body or {}).get("error") or "") if isinstance(body, Mapping) else ""
        low = text.lower()
        return status == 429 and ("credit" in low or "balance" in low or "quota" in low)
