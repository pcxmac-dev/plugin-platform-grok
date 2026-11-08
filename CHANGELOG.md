# Changelog

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
