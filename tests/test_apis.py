"""What the plugin attaches to (plugin API 2.2, apis.py): the xAI API's card is sound, says how a key is sent, the
limits, the prices, the status page and the key page, names the requests Connect and an evaluation really send (read
from a fake session's record) among the API's others, and every address on it is xAI's own. The page check is the
weekly one (tests/test_vendor_pages.py, LIMINAL_VENDOR_PAGES=1); nothing is sent here. The user, 2026-11-11: "each
plugin should reflect the the API its attached to, and present links that provide documentation"."""
from __future__ import annotations

from datetime import date, datetime, timezone
from urllib.parse import urlsplit

from liminal_libs.sources.apis import problems, urls

import plugin_platform_grok as grok
from plugin_platform_grok import ASSISTANT
from plugin_platform_grok.apis import APIS, XAI_API

from conftest import FakeResponse, FakeSession

NOW = datetime(2026, 11, 11, 15, 0, tzinfo=timezone.utc)
KEY = "xai-test-key-000"


def test_the_card_is_sound_and_is_the_plugins():
    assert problems(APIS, today=date(2026, 11, 11)) == []
    assert ASSISTANT.apis == APIS and grok.GrokPlugin.apis is APIS and grok.APIS is APIS
    assert XAI_API.base == grok.API and XAI_API.verified == "2026-11-11"
    assert XAI_API.link("console") == "https://console.x.ai/team/default/api-keys"
    assert all(XAI_API.link(k) for k in ("docs", "reference", "limits", "pricing", "status", "changelog", "terms"))
    assert "Bearer" in XAI_API.auth and "Tier 0" in XAI_API.limits and "$1.25" in XAI_API.costs
    assert ASSISTANT.interface()["apis"] == ["xAI API"]
    assert ASSISTANT.api_facts() == {}  # the instance keeps nothing of a run: each Connect builds its own Assistant


def test_the_card_names_the_requests_the_plugin_really_sends(installed, settings_for):
    """A full Connect (the models list, then one answer of a few tokens) sends exactly the calls the card says it
    uses, as method and path on the card's base; an evaluation's answer is the same POST."""
    installed(ASSISTANT)
    settings = settings_for(GROK_API_KEY=KEY, GROK_PLAN="tier0")
    session = FakeSession(
        FakeResponse(200, {"object": "list", "data": [{"id": "grok-4.20-0309-non-reasoning", "object": "model"}]}),
        FakeResponse(200, {"id": "resp_1", "object": "response", "status": "completed",
                           "model": "grok-4.20-0309-non-reasoning",
                           "output": [{"type": "message", "content": [{"type": "output_text", "text": "OK"}]}],
                           "usage": {"input_tokens": 12, "output_tokens": 1, "cost_in_usd_ticks": 37756}},
                     {"x-request-id": "req_1"}))
    ASSISTANT.run_scan(ASSISTANT.build(settings, session=session, now=lambda: NOW))
    sent = {f"{method} {url.removeprefix(XAI_API.base)}" for method, url, *_ in session.calls}
    assert sent == {c.name for c in XAI_API.used} == {"POST /v1/responses", "GET /v1/models"}
    used = {c.name: c for c in XAI_API.used}
    assert used["POST /v1/responses"].costs and not used["GET /v1/models"].costs  # an answer is billed, the list is not
    assert {a.name for a in XAI_API.covered} == {"Responses", "Models"}
    assert all(c.area in {a.name for a in XAI_API.areas} for c in XAI_API.calls)
    assert len(XAI_API.areas) > 2 * len(XAI_API.covered) and len(XAI_API.calls) > 2 * len(XAI_API.used)
    # what the Responses API now takes that the plugin does not send is said where it is used
    body = session.calls[1][3]
    assert "reasoning" not in body and "safety_identifier" not in body
    assert "reasoning.effort" in XAI_API.areas[0].covered and "safety_identifier" in XAI_API.areas[0].covered


def test_every_address_is_xais_own():
    hosts = {urlsplit(u).hostname for u in urls(APIS)}
    assert hosts == {"docs.x.ai", "status.x.ai", "console.x.ai", "x.ai"}
