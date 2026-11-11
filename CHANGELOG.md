# Changelog

## 0.3.0 (2026-11-11)

Its API on its page (plugin API 2.2, liminal-libs 1.49.0; the user: "each plugin should reflect the the API its attached to, and present links that provide documentation, the plugin interface should more or less contain what it already has, BUT, it should also expose more of what the API is about"). `GrokPlugin.apis` (apis.py) is the xAI API's card, from xAI's pages (its docs now at docs.x.ai/developers, the company named SpaceXSI there), verified 2026-11-11: what it is, its base and version, how a key is sent (a bearer key; a management key for collections and the Management API), the tiers' requests a second and tokens a minute, the prices, and xAI's pages (getting started, the REST reference, Responses, Models, generating text, models and pricing, rate limits, debugging, cost tracking, release notes, the status page, the console's API keys, the legal terms). Every part of the reference is named: the Responses API and the models list it uses (Connect and every evaluation), then Chat Completions, the account's calls (the key's details, token counts), images, videos, voice, files, batches, collections, the Management API and the legacy endpoints; and its calls: `POST /v1/responses` and `GET /v1/models`, and the others worth knowing. The card says what the plugin does not send that the Responses API now takes: `reasoning.effort` and `safety_identifier` (xAI's release notes, 2026-09 and later); what it sends is unchanged. The plans, models and sources tables stay as they were. The instance keeps nothing of a run, so `api_facts()` says nothing. Needs liminal-libs>=1.49.0. A test checks that the card names the requests Connect really sends; the weekly page check asks each address on it too.

## 0.2.1 (2026-11-08)

Its icon is Grok's mark, drawn in the library's line (liminal-libs 1.33.0's `grok`; the user: "for the AI icons, lets use the respective mascot/icon from the business, logo, etc.."). Needs liminal-libs>=1.33.0.

## 0.2.0 (2026-11-03)

Renamed `plugin-platform-grok` (the package `plugin_platform_grok`; it was `platform-plugin-grok`) on 2026-11-03: the naming by system (plugins are `plugin-<app>-<name>`), on liminal-libs 1.4.0 (`liminal_libs`, the library renamed with it).

The first release: `GrokPlugin` (an `AssistantPlugin`, plugin API 2.0, liminal-libs 1.3.0) and
`GrokAssistant` on xAI's Responses API. The plans (free: no API access, xAI publishing no free
credits; Tier 0 to Tier 4 by cumulative spend, Enterprise), the models (Grok 4.20 non-reasoning by
default, the 4.20 reasoning model, 4.3, Build 0.1, 4.5, 4.6, 4.7, the multi-agent model, with their
prices per million tokens) and the pages they were written from, verified 2026-11-03; every answer's
cost is xAI's own figure, compared with the table at Connect; the weekly CI run reads the pages
again. Every error scrubbed of the key and the account; a credit refusal is final, not retried.
