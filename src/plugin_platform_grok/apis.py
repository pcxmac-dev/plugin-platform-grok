"""What the plugin attaches to (plugin API 2.2, liminal_libs.sources.apis), as xAI's own pages describe it (read
2026-11-11): the xAI API, every part of its REST reference (the Responses API and the models list the plugin calls
first, then Chat Completions, images, videos, voice, files, batches, the account's calls, collections and the
Management API), how a caller proves who it is, the tiers' limits, the prices, the status page and the console's key
page. The tables the evaluations are costed and planned by stay the plugin's (PLANS, MODELS, SOURCES). The user,
2026-11-11: "each plugin should reflect the the API its attached to, and present links that provide documentation ...
it should also expose more of what the API is about"."""
from __future__ import annotations

from liminal_libs.sources.apis import Api, Area, Call, Link

from .assistant import API, GrokAssistant

DOCS = "https://docs.x.ai/"
DEV = DOCS + "developers/"
REF = DEV + "rest-api-reference/"
VERIFIED = "2026-11-11"  # the day these facts were read from xAI's pages

RESPONSES = "Responses"
MODELS = "Models"
ACCOUNT = "Account"
MANAGEMENT = "Management API"

XAI_API = Api(
    name="xAI API",
    maker="xAI (its docs now say SpaceXSI)",
    about=("xAI's REST API for the Grok models, compatible with OpenAI's. The Responses API takes instructions and input "
           "and returns output items (reasoning, tools such as web and X search, structured outputs, compaction); "
           "beside it are the legacy Chat Completions with their deferred form, images and videos (Imagine), voice "
           "(realtime, text to speech, speech to text), files, batches, the models lists, a token count and the key's "
           "own details; collections to search and the Management API (keys, teams, billing, audit logs) take a "
           "management key on a host of their own. The xAI SDK speaks gRPC to the same models."),
    kind="rest",
    base=API,
    version="v1",
    auth=("an API key as Authorization: Bearer (made on the console's API Keys page); collections management and the "
          "Management API at management-api.x.ai take a management key"),
    limits=("by tier, from cumulative API spend since January 1, 2026, never downgraded: Tier 0 to Tier 4 at $0, $50, "
            "$250, $1,000 and $5,000; for each model, requests a second and tokens a minute: Grok 4.20 and 4.3 37, 50, "
            "75, 125 and 208 a second and 10M, 15M, 25M, 45M and 85M tokens a minute, Grok 4.5 to 4.7 150 to 500 a "
            "second and 50M to 100M; a second's limit is a minute's requests divided by 48 (2 at least); cached tokens "
            "count; 429 beyond"),
    costs=("every token by model, from prepaid credits: per million input and output tokens, Grok 4.20 and 4.3 $1.25 "
           "and $2.50, Grok 4.5 to 4.7 $2 and $6, Grok Build 0.1 $1 and $2, prompts of 200,000 tokens or more twice; "
           "each answer carries its own cost (usage.cost_in_usd_ticks)"),
    links=(
        Link("Get started", DOCS + "overview", "docs"),
        Link("REST API reference", REF + "inference", "reference"),
        Link("Responses", REF + "inference/responses", "reference"),
        Link("Models (reference)", REF + "inference/models", "reference"),
        Link("Generate text", DEV + "model-capabilities/text/generate-text", "guide"),
        Link("Models and pricing", DEV + "models", "pricing"),
        Link("Pricing", DEV + "pricing", "pricing"),
        Link("Rate limits", DEV + "rate-limits", "limits"),
        Link("Debugging errors", DEV + "debugging", "guide"),
        Link("Cost tracking", DEV + "cost-tracking", "guide"),
        Link("Release notes", DEV + "release-notes", "changelog"),
        Link("Status", "https://status.x.ai/", "status"),
        Link("API keys (console)", "https://console.x.ai/team/default/api-keys", "console"),
        Link("Legal", "https://x.ai/legal", "terms"),
    ),
    areas=(
        Area(RESPONSES, "instructions and input in, output items out: reasoning (reasoning.effort), tools, structured "
                        "outputs, stored responses, compaction", REF + "inference/responses",
             covered=("each evaluation's answer, and Connect's probe of a few tokens: instructions, one user input, "
                      "max_output_tokens, store false; the cost xAI counts read from usage. It sends neither "
                      "reasoning.effort nor safety_identifier, which the Responses API now takes")),
        Area("Chat Completions", "the legacy messages-in, message-out interface, and deferred completions",
             REF + "inference/chat-completions"),
        Area(MODELS, "the models, and the language, image and video generation models, with their prices",
             REF + "inference/models", covered="Connect: the key tried, the model chosen looked for, the table's models "
                                              "compared"),
        Area(ACCOUNT, "the key's own details, and a text's token count", REF + "inference/other"),
        Area("Images", "images generated and edited (Imagine)", REF + "inference/images"),
        Area("Videos", "videos generated, edited and extended (Imagine)", REF + "inference/videos"),
        Area("Voice", "realtime voice, text to speech, speech to text, phone numbers", REF + "inference/voice"),
        Area("Files", "files uploaded, listed and downloaded", REF + "files"),
        Area("Batches", "many requests run asynchronously", REF + "inference/batches"),
        Area("Collections", "documents kept to be searched (management key to manage them, API key to search)",
             REF + "collections"),
        Area(MANAGEMENT, "API keys and their access, teams, billing (prepaid credit and usage), audit logs (management "
                         "key, management-api.x.ai)", REF + "management"),
        Area("Legacy and deprecated", "the completions, Anthropic-shaped messages and complete endpoints",
             REF + "inference/legacy"),
    ),
    calls=(
        Call("POST " + GrokAssistant.answers_path, "create a response", RESPONSES,
             used="each evaluation's answer, and Connect's probe", docs=REF + "inference/responses", costs=True),
        Call("GET " + GrokAssistant.models_path, "list the models", MODELS,
             used="Connect: the models the key reaches", docs=REF + "inference/models"),
        Call("GET /v1/responses/{response_id}", "a stored response", RESPONSES, docs=REF + "inference/responses"),
        Call("POST /v1/responses/compact", "compact a conversation", RESPONSES, docs=REF + "inference/responses",
             costs=True),
        Call("GET /v1/language-models", "the language models with their prices", MODELS, docs=REF + "inference/models"),
        Call("GET /v1/api-key", "the key's own details", ACCOUNT, docs=REF + "inference/other"),
        Call("POST /v1/tokenize-text", "a text's tokens", ACCOUNT, docs=REF + "inference/other"),
        Call("POST /v1/chat/completions", "create a chat completion", "Chat Completions",
             docs=REF + "inference/chat-completions", costs=True),
        Call("POST /v1/images/generations", "generate an image", "Images", docs=REF + "inference/images", costs=True),
        Call("POST /v1/batches", "create a batch", "Batches", docs=REF + "inference/batches", writes=True, costs=True),
        Call("POST /v1/files", "upload a file", "Files", docs=REF + "files", writes=True),
    ),
    verified=VERIFIED,
)

APIS = (XAI_API,)
