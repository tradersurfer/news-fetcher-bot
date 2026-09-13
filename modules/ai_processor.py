"""
AI Content Processor — transforms raw stories into X drafts using Claude.
@AdrianJordan_io brand voice.
"""

import json
from typing import Optional, List
from anthropic import Anthropic
from core.config import ANTHROPIC_API_KEY, log, RawStory, DraftPost

SYSTEM_PROMPT = """
You are the Lead Content Strategist for @AdrianJordan_io on X.
Rewrite raw news into engaging, accurate X posts.

BRAND VOICE:
- Direct, authoritative, knowledgeable. Talking to fellow Bitcoiners.
- Headline-style. NO preamble, NO waffle, NO hashtags.
- Under 280 chars. Impact first.
- Accuracy: never invent facts.
- Context: briefly WHY this matters for Bitcoin.
- Credit: 🫡 @handle for journalists. - Publication for corporate.
- Cash tags: $BTC at end only.

BANNED: "supply shock", "what a time to be alive", "it's happening".

OUTPUT ONLY valid JSON:
{"option_1": "Sharpest headline", "option_2": "Analytical", "option_3": "Clean factual", "credit_line": "- Publication OR 🫡 @handle OR ''"}
"""

class AIContentProcessor:
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate_drafts(self, story: RawStory) -> Optional[DraftPost]:
        if not ANTHROPIC_API_KEY:
            log.error("ANTHROPIC_API_KEY not set")
            return None
        msg = (f"SOURCE: {story.source_type} | {story.source} | {story.posted_at or ''}\n"
               f"TITLE: {story.title}\nURL: {story.url}\n"
               f"Rewrite into three @AdrianJordan_io posts.")
        try:
            resp = self.client.messages.create(
                model="claude-sonnet-4-6", max_tokens=600,
                system=SYSTEM_PROMPT,
                messages=[{"role":"user","content":msg}],
            )
            raw = resp.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"): raw = raw[4:]
                raw = raw.strip()
            parsed = json.loads(raw)
            return DraftPost(
                story_id=story.id, raw_title=story.title, source=story.source,
                source_type=story.source_type,
                option_1=parsed.get("option_1",""), option_2=parsed.get("option_2",""),
                option_3=parsed.get("option_3",""), credit_line=parsed.get("credit_line",""),
            )
        except Exception as exc:
            log.error(f"AIProcessor: {exc}")
            return None

    def generate_drafts_batch(self, stories: List[RawStory]) -> List[DraftPost]:
        drafts = []
        for s in stories:
            d = self.generate_drafts(s)
            if d: drafts.append(d)
        log.info(f"AIProcessor: {len(drafts)} drafts from {len(stories)} stories")
        return drafts
