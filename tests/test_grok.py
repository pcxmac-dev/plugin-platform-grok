"""The Grok plugin on fake answers: it loads as an assistant plugin, its tables hold together, its
requests are the Responses API's with the key and nothing about the account, xAI's own cost figure
is kept, its errors are mapped, Connect checks the models and the prices, the free plan sends nothing."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

import pytest

from liminal_lib.assistants import Answer, Question, Usage, evaluate
from liminal_lib.errors import NotEntitled, RateLimited, SourceError, Unauthorized

import platform_plugin_grok as grok
from platform_plugin_grok import ASSISTANT, MODELS, PLANS, SOURCES, GrokPlugin

from conftest import FakeResponse, FakeSession

NOW = datetime(2026, 11, 3, 15, 0, tzinfo=timezone.utc)
KEY, EMAIL = "xai-test-key-000", "me@example.com"


def answer(text, model="grok-4.20-0309-non-reasoning", in_=120, out=30, cached=20, reasoning=0, status="completed",
           reason=None, nano_usd=None, headers=None):
    body = {"id": "resp_1", "model": model, "status": status,
            "output": [{"type": "reasoning", "status": "completed", "encrypted_content": "..."},
                       {"type": "message", "role": "assistant", "status": "completed",
                        "content": [{"type": "output_text", "text": text, "annotations": []}]}],
            "usage": {"input_tokens": in_, "output_tokens": out, "total_tokens": in_ + out,
                      "input_tokens_details": {"cached_tokens": cached}, "output_tokens_details": {"reasoning_tokens": reasoning}}}
    if reason:
        body["incomplete_details"] = {"reason": reason}
    if nano_usd is not None:
        body["usage"]["cost_in_nano_usd"] = nano_usd
    return FakeResponse(200, body, headers or {"x-request-id": "req_x"})


def models(*ids):
    return FakeResponse(200, {"object": "list", "data": [{"id": i, "object": "model", "owned_by": "xai"} for i in ids]})


def test_it_loads_as_an_assistant_plugin(installed):
    found = installed(ASSISTANT)
    p = found["grok"]
    assert isinstance(p, GrokPlugin) and p.KIND == "assistant" and p.SYSTEM == "platform" and p.api == "2.0" and p.vendor == "xAI"
    assert [k.name for k in p.keys] == ["GROK_API_KEY", "GROK_ACCOUNT"] and p.keys[0].aliases == ("XAI_API_KEY",)
    assert p.options == ("GROK_MAX_OUTPUT_TOKENS",) and p.has_scan and p.has_settings  # no effort option
    from liminal_lib.sources import registry

    assert registry.errors() == [] and set(registry.variables()) >= {"GROK_API_KEY", "XAI_API_KEY", "GROK_PLAN", "GROK_MODEL"}


def test_the_tables_hold_together():
    assert PLANS[0].name == "free" and not PLANS[0].api_access and "prepaid" in PLANS[0].note
    assert [p.name for p in PLANS] == ["free", "tier0", "tier1", "tier2", "tier3", "tier4", "enterprise"]
    assert all(m.input_usd > 0 and m.output_usd > 0 for m in MODELS) and all(ASSISTANT.plan_of(n) for m in MODELS for n in m.plans)
    assert MODELS[0].id == ASSISTANT.default_model == "grok-4.20-0309-non-reasoning" and not MODELS[0].reasoning
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", grok.VERIFIED) and all(s.url.startswith("https://docs.x.ai/") for s in SOURCES)
    assert ASSISTANT.cost("grok-4.7", Usage(1_000_000, 1_000_000, 0, 0)) == 8.0
    assert sorted(p.rpm for p in PLANS if p.rpm) == [1776, 2400, 3600, 6000, 9984]


def test_the_request_is_the_responses_apis_without_an_account_field(installed, settings_for):
    installed(ASSISTANT)
    settings = settings_for(XAI_API_KEY=KEY, GROK_ACCOUNT=EMAIL, GROK_PLAN="tier0")
    session = FakeSession(answer("Closed.\nVerdict: no", nano_usd=160_000))
    q = Question("Is the market open?", answer=Answer("verdict", scale=("yes", "no")))
    ev = evaluate(q, settings, assistant="grok", session=session, now=lambda: NOW)
    method, url, _, body, headers = session.calls[0]
    assert method == "POST" and url == "https://api.x.ai/v1/responses" and headers["Authorization"] == f"Bearer {KEY}"
    assert body["model"] == "grok-4.20-0309-non-reasoning" and body["max_output_tokens"] == 1024 and body["store"] is False
    assert body["input"] == [{"role": "user", "content": "Question: Is the market open?"}] and body["instructions"].startswith("You are")
    assert "safety_identifier" not in body and "user" not in body and "reasoning" not in body and EMAIL not in json.dumps(body)
    assert ev.verdict == "no" and ev.usage == Usage(120, 30, 20, 0) and ev.request_id == "resp_1" and ev.provider == "xAI"
    assert ev.cost_usd == pytest.approx(0.00016)  # xAI's own figure, not the table's
    table = evaluate(q, settings, assistant="grok", session=FakeSession(answer("Verdict: yes")), now=lambda: NOW)
    assert table.cost_usd == pytest.approx(MODELS[0].cost(Usage(120, 30, 20, 0)))  # no figure sent: the table's prices
    cut = evaluate(q, settings, assistant="grok", session=FakeSession(answer("Verdict: yes", status="incomplete", reason="max_output_tokens")),
                   now=lambda: NOW)
    assert cut.stop == "length"


def test_the_free_plan_sends_nothing(installed, settings_for):
    installed(ASSISTANT)
    settings = settings_for(GROK_API_KEY=KEY)
    assert settings.plugin("grok").plan == "free" and not ASSISTANT.served(settings) and "prepaid credits" in ASSISTANT.free_note(settings)
    session = FakeSession()
    with pytest.raises(NotEntitled, match="Free plan has no API access"):
        evaluate(Question("x"), settings, assistant="grok", session=session)
    assert session.calls == []


def test_xais_errors_are_mapped_in_both_shapes(installed, settings_for):
    installed(ASSISTANT)
    settings = settings_for(GROK_API_KEY=KEY, GROK_PLAN="tier0")

    def run(*responses):
        session = FakeSession(*responses)
        a = ASSISTANT.build(settings, session=session, now=lambda: NOW)
        a.client._sleep = lambda s: None
        try:
            a.evaluate(Question("x"))
        except SourceError as e:
            return type(e), e.message, len(session.calls)
        return None, "", len(session.calls)

    kind, msg, n = run(FakeResponse(401, {"code": "unauthorized", "error": f"Invalid API key {KEY}"}))
    assert kind is Unauthorized and KEY not in msg and n == 1
    kind, msg, n = run(FakeResponse(429, {"code": "insufficient_funds", "error": "Your credit balance is too low"}))
    assert kind is NotEntitled and "no credit" in msg and n == 1  # final: not tried again
    kind, msg, n = run(FakeResponse(404, {"error": {"message": "The model grok-9 does not exist", "code": "model_not_found"}}))
    assert kind is NotEntitled and "Connect's list" in msg
    limited = FakeResponse(429, {"code": "rate_limit", "error": "Too many requests"}, {"Retry-After": "1"})
    kind, msg, n = run(limited, limited, limited, limited, limited)
    assert kind is RateLimited and n == 5


def test_connect_checks_the_models_and_the_prices(installed, settings_for):
    installed(ASSISTANT)
    settings = settings_for(GROK_API_KEY=KEY, GROK_PLAN="tier0")
    probe = answer("OK", in_=10, out=2, cached=0, nano_usd=900_000)  # xAI's figure far from the table's 17,500 nano-dollars
    session = FakeSession(models("grok-4.7", "grok-4.20-0309-non-reasoning", "grok-5-preview"), probe)
    scanned = ASSISTANT.run_scan(ASSISTANT.build(settings, session=session, now=lambda: NOW))
    rows = {w: (ok, d) for w, ok, d in scanned.results}
    assert rows["the key"][0] and rows["the model grok-4.20-0309-non-reasoning"][0]
    assert not rows["the table's models"][0] and "grok-4.3" in rows["the table's models"][1]
    assert rows["models not in the table"] == (True, "grok-5-preview")
    assert rows["an answer"][0] and "by the vendor's count" in rows["an answer"][1]
    assert not rows["the table's prices"][0] and "the table is stale" in rows["the table's prices"][1]
    assert "its plan" not in rows and scanned.plan == {}  # xAI sends no rate-limit headers: the plan stays yours
