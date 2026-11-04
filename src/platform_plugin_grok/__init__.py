"""Grok (xAI) for Liminal: an AI assistant plugin (liminal_lib.assistants, plugin API 2.0) that
evaluates standardized arguments through xAI's Responses API on your own API key, with the tiers,
models and prices written in, dated, and checked against xAI's pages.

A Liminal plugin released on its own, registered under the entry point group `liminal.providers` as
`grok`: the plugin `GrokPlugin` (ASSISTANT below), its assistant `GrokAssistant` (assistant.py). It
relies on plugin API 2.0 and nothing of the apps.

What the user sets (the Plugins view's Setup, or the app's key script): `GROK_API_KEY` (read as
`XAI_API_KEY` too), `GROK_ACCOUNT` (the email or account name the key belongs to: shown with its
evaluations, sent to no one: xAI's API takes no account field); its plan `GROK_PLAN` (free: no API
access; tier0 to tier4 by cumulative spend, enterprise), its model `GROK_MODEL` (Grok 4.20
non-reasoning by default: the cheapest general model), its caps on this machine
`GROK_REQUESTS_PER_DAY` (50), `GROK_TOKENS_PER_DAY` (200,000), `GROK_MAX_OUTPUT_TOKENS` (1,024).

The user, 2026-11-03: "the ai plugins should support free, and if that means they have no API access,
then so be it": xAI publishes no free API credits (checked 2026-11-03), so the free plan sends
nothing; with credits bought, Tier 0 is the plan until $50 has been spent. "every time any of the
three vendors changes their plans/rates there will have to be a way to query through the plugin to
update itself, or worst case, just version up every time w/ CI catching the disparity between code
and latest rates through unit testing": every answer carries xAI's own cost figure, which Connect
compares with the table's prices (a disagreement names the stale table); the weekly CI run reads
the models and rate-limit pages (SOURCES) and fails when a written-in figure is gone.
"""
from __future__ import annotations

from liminal_lib.assistants import AssistantPlugin, Caps, Model, Plan, Source

from .assistant import API, GrokAssistant

__all__ = ["ASSISTANT", "GrokPlugin", "GrokAssistant", "PLANS", "MODELS", "SOURCES", "VERIFIED", "API"]

VERIFIED = "2026-11-03"  # the day the tables below were checked against SOURCES

# xAI's tiers (docs.x.ai/docs/key-information/consumption-and-rate-limits, 2026-11-03): by cumulative API
# spend since 2026-01-01, never downgraded; each model's limits are requests a second and tokens a minute
# (the page: a second's limit is a minute's divided by 48). The figures here are the Grok 4.20 and 4.3
# models' (grok-4.5 to 4.7: 150 to 500 a second, 50M to 100M tokens a minute).
PLANS = (
    Plan("free", "Free", api_access=False, price="nothing bought",
         note="xAI publishes no free API credits (2026-11-03): the API runs on prepaid credits bought at console.x.ai; "
              "with credits, choose Tier 0 (the plan until $50 has been spent)"),
    Plan("tier0", "Tier 0", rpm=1_776, tpm=10_000_000, price="credits bought; under $50 spent",
         note="37 requests a second (1,776 a minute), 10,000,000 tokens a minute on the 4.20 and 4.3 models"),
    Plan("tier1", "Tier 1", rpm=2_400, tpm=15_000_000, price="$50 spent", note="50 requests a second, 15,000,000 tokens a minute"),
    Plan("tier2", "Tier 2", rpm=3_600, tpm=25_000_000, price="$250 spent", note="75 requests a second, 25,000,000 tokens a minute"),
    Plan("tier3", "Tier 3", rpm=6_000, tpm=45_000_000, price="$1,000 spent", note="125 requests a second, 45,000,000 tokens a minute"),
    Plan("tier4", "Tier 4", rpm=9_984, tpm=85_000_000, price="$5,000 spent", note="208 requests a second, 85,000,000 tokens a minute"),
    Plan("enterprise", "Enterprise", price="on request (sales@x.ai)", note="limits arranged with xAI"),
)

# The current text models (docs.x.ai/docs/models, 2026-11-03): prices per million tokens (input, output, a
# cached input token), the context window; the cheapest general model first.
MODELS = (
    Model("grok-4.20-0309-non-reasoning", "Grok 4.20 (non-reasoning)", 1.25, 2.50, 0.20, 1_000_000,
          note="answers without thinking: the cheapest; prompts over 200,000 tokens cost twice"),
    Model("grok-4.20-0309-reasoning", "Grok 4.20 (reasoning)", 1.25, 2.50, 0.20, 1_000_000, reasoning=True,
          note="prompts over 200,000 tokens cost twice"),
    Model("grok-4.3", "Grok 4.3", 1.25, 2.50, 0.20, 1_000_000, reasoning=True, note="prompts over 200,000 tokens cost twice"),
    Model("grok-build-0.1", "Grok Build 0.1", 1.00, 2.00, 0.20, 256_000, note="for building: code"),
    Model("grok-4.5", "Grok 4.5", 2.00, 6.00, 0.30, 500_000, reasoning=True, note="prompts over 200,000 tokens cost twice"),
    Model("grok-4.6", "Grok 4.6", 2.00, 6.00, 0.50, 500_000, reasoning=True, note="prompts over 200,000 tokens cost twice"),
    Model("grok-4.7", "Grok 4.7", 2.00, 6.00, 0.50, 500_000, reasoning=True, note="the newest; prompts over 200,000 tokens cost twice"),
    Model("grok-4.20-multi-agent-0309", "Grok 4.20 multi-agent", 1.25, 2.50, 0.20, 1_000_000, reasoning=True,
          note="several agents on one prompt; lower rate limits"),
)

# Where the tables come from, with what each page must still show (verify.check_sources, weekly in CI).
SOURCES = (
    Source("https://docs.x.ai/docs/models", "the models' prices", "Your choice depends on your use case",
           ("grok-4.7", "grok-4.20-0309-non-reasoning", "grok-build-0.1", "1.25", "2.50", "2.00", "6.00")),
    Source("https://docs.x.ai/docs/key-information/consumption-and-rate-limits", "the tiers and their limits",
           "tiers never downgrade", ("Tier 1", "$50", "Tier 2", "$250", "Tier 3", "$1,000", "Tier 4", "$5,000")),
)


class GrokPlugin(AssistantPlugin):
    """Grok: the plugin (see the module's docstring)."""

    name = "grok"
    title = "Grok"
    about = "xAI's Grok through the Responses API: evaluations of standardized arguments on your key"
    vendor = "xAI"
    signup = "https://console.x.ai/"
    order = 501
    api = "2.0"
    assistant = GrokAssistant
    plans = PLANS
    models = MODELS
    default_model = "grok-4.20-0309-non-reasoning"
    verified = VERIFIED
    sources = SOURCES
    caps = Caps()  # 50 requests and 200,000 tokens a day on this machine, 1,024 output tokens an answer
    efforts = ()  # xAI's Responses API takes no effort level
    key_aliases = ("XAI_API_KEY",)
    account_hint = "the email or account name the key belongs to: shown with its evaluations, sent to no one (xAI's API takes no account field)"


ASSISTANT = GrokPlugin()
