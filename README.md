# plugin-platform-grok

Grok for [Liminal](https://github.com/pcxmac-dev/liminal-charts): an AI assistant plugin (plugin API
2.2, `liminal_libs.assistants`, a platform plugin) that evaluates standardized arguments (a question
over headlines, an assessment, a report; a judge over earlier answers) through xAI's Responses API
on your own API key, with xAI's tiers, models and prices written in.

- `grok` on the Plugins view (the AI assistants group): Setup takes `GROK_API_KEY` (read as
  `XAI_API_KEY` too) and `GROK_ACCOUNT`, the email or account name the key belongs to, shown with
  its evaluations and sent to no one (xAI's API takes no account field).
- Plan: `GROK_PLAN` is `free` by default, which has no API access (xAI publishes no free credits;
  the API runs on prepaid credits bought at console.x.ai), so nothing is sent until the plan your
  key is on is chosen: `tier0` (until $50 has been spent), `tier1` to `tier4`, `enterprise`.
- Model: `GROK_MODEL`, Grok 4.20 non-reasoning by default (the cheapest general model); the 4.20
  reasoning model, 4.3, Build 0.1, 4.5, 4.6, 4.7 and the multi-agent model are in the table.
- Caps on this machine, every database together: `GROK_REQUESTS_PER_DAY` (50),
  `GROK_TOKENS_PER_DAY` (200,000), `GROK_MAX_OUTPUT_TOKENS` (1,024); raised on the Plugins view.
- Every answer carries xAI's own cost figure, which is what an evaluation records; Connect compares
  it with the table's prices and names a stale table. The tables were verified on the date the
  plugin says (`VERIFIED`); the weekly CI run reads xAI's pages again and fails when a figure is
  gone, which is a new release of this plugin.

Nothing is sent from an offline copy of the app (`LIMINAL_OFFLINE`).

## Its API

The [xAI API](https://docs.x.ai/developers/rest-api-reference/inference) at `https://api.x.ai`:
[`POST /v1/responses`](https://docs.x.ai/developers/rest-api-reference/inference/responses) for every evaluation and
Connect's probe, [`GET /v1/models`](https://docs.x.ai/developers/rest-api-reference/inference/models) for Connect's
models list, with the key as a bearer token (made on the console's
[API keys](https://console.x.ai/team/default/api-keys) page). Its limits are the
[tiers'](https://docs.x.ai/developers/rate-limits) requests a second and tokens a minute, by cumulative spend; its
prices are per token ([models and pricing](https://docs.x.ai/developers/models)), each answer carrying its own cost;
its status is at [status.x.ai](https://status.x.ai/). The Responses API now also takes `reasoning.effort` and
`safety_identifier`, which this plugin does not send.

`GrokPlugin.apis` (`apis.py`, plugin API 2.2) says this on the plugin's page, with every other part of the API's
reference (Chat Completions, images, videos, voice, files, batches, collections, the Management API ...) and its notable
calls, as read on 2026-11-11.

## Install

Into the app's environment, from the app's folder:

```powershell
.venv\Scripts\python.exe -m pip install "plugin-platform-grok @ git+https://github.com/pcxmac-dev/plugin-platform-grok@release/0.2.0"
```

or with the app's plugins (`pip install -e ".[plugins]"` in liminal-charts). The app loads it on its next
start. Save the key with the app's `tools/set-key.ps1` or on the Plugins view (it is read from your
user environment variables only, never written to a file).

## Tests

`python -m pytest -q`: fake answers, nothing sent. `LIMINAL_VENDOR_PAGES=1` adds the page check.
