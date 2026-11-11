"""The weekly check (CI's schedule, LIMINAL_VENDOR_PAGES=1): xAI's public models and rate-limit pages
read again, each written-in figure looked for. A figure gone means the table is stale and the
plugin needs a release; the failure names the table. And every address on the plugin's card
(apis.py) asked once. Nothing is read on a push or a pull request."""
from __future__ import annotations

import os

import pytest

from liminal_libs.assistants.verify import check_sources
from plugin_platform_grok import ASSISTANT

pytestmark = pytest.mark.skipif(not os.environ.get("LIMINAL_VENDOR_PAGES"),
                                reason="LIMINAL_VENDOR_PAGES=1 reads the vendor's pages (the weekly CI run)")


def test_the_tables_still_match_xais_pages():
    problems = check_sources(ASSISTANT)
    assert problems == [], "\n".join(problems)


def test_every_address_on_the_card_answers():
    """Each address on the card asked once (sources.apis.dead_links)."""
    from liminal_libs.sources.apis import dead_links
    from plugin_platform_grok.apis import APIS

    assert dead_links(APIS) == []
