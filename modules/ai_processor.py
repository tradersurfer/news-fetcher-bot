"""
AI Content Processor Module

Uses Claude (Anthropic) to transform raw news stories into
polished, on-brand X posts for @AdrianJordan_io.

Built on the Bitcoin Archive style guide:
- Impact first, short words, no hashtags
- Join the dots (explain why it matters for Bitcoin)
- Credit independent journalists
"""

import json
import os
from typing import Optional, List
from dataclasses import dataclass, field

from anthropic import Anthropic

from core.config import (
    ANTHROPIC_API_KEY, log, RawStory, DraftPost
)

# ─────────────────────────────────────────────
# SYSTEM PROMPT — @AdrianJordan_io Voice
# ─────────────────────────────────────────────

ADRIAN_JORDAN_SYSTEM_PROMPT = """
You are the Lead Content Strategist for @AdrianJordan_io on X (Twitter).
Your job is to rewrite raw news headlines into engaging, accurate X posts.

━━━ BRAND VOICE ════════════════════════
- Tone: Direct, authoritative, knowledgeable. Talking to fellow Bitcoiners.
- Style: Headline-style posts. NO preamble, NO waffle, NO greetings.
- Length: Under 280 characters (X limit). Aim for punchy.
- Hashtags: NEVER use hashtags. Zero. They cause algorithm drag.
- Impact: Stack the most important fact/number/entity at the very start.
- Accuracy: Never invent facts, never sensationalize.
- Context: Briefly explain WHY this matters for Bitcoin.
- Credit: For journalists, add "🫡 @handle". For corporate, "- Publication".
- Cash tags: $BTC is fine at the end of a sentence only.

━━━ BANNED PHRASES ════════════════════
Never use: "supply shock", "what a time to be alive", "it's happening",
"official" (for old news), or vague source attributions.

━━━ OUTPUT FORMAT ══════════════════════
Return ONLY a valid JSON object — no markdown, no code fences, no prose.

{
  "option_1": "Sharpest headline with biggest impact first",
  "option_2": "Analytical — connects the dots for Bitcoin relevance",
  "option_3": "Clean factual fallback — neutral and accurate",
  "credit_line": "- Publication Name OR 🫡 @handle OR ''"
}
"""


class AIContentProcessor:
    """Processes raw stories into polished X post drafts using Claude."""

    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.system_prompt = ADRIAN_JORDAN_SYSTEM_PROMPT

    def generate_drafts(self, story: RawStory) -> Optional[DraftPost]:
        """
        Generate three draft X post options from a raw story.

        Args:
            story: RawStory object with title, url, source info

        Returns:
            DraftPost with 3 options, or None on failure
        """
        if not ANTHROPIC_API_KEY:
            log.error("AIContentProcessor: ANTHROPIC_API_KEY not set")
            return None

        user_message = self._build_user_message(story)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=600,
                system=self.system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            raw_text = response.content[0].text.strip()

            # Strip markdown code blocks if present
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()

            parsed = json.loads(raw_text)

            draft = DraftPost(
                story_id=story.id,
                raw_title=story.title,
                source=story.source,
                source_type=story.source_type,
                option_1=parsed.get("option_1", ""),
                option_2=parsed.get("option_2", ""),
                option_3=parsed.get("option_3", ""),
                credit_line=parsed.get("credit_line", ""),
            )

            log.info(f"AIProcessor: Generated drafts for '{story.title[:55]}...'")
            return draft

        except json.JSONDecodeError as exc:
            log.error(f"AIProcessor: Claude returned non-JSON: {exc}\nRaw: {raw_text[:300]}")
            return None
        except Exception as exc:
            log.error(f"AIProcessor: API error: {exc}")
            return None

    def generate_drafts_batch(self, stories: List[RawStory]) -> List[DraftPost]:
        """Process multiple stories at once."""
        drafts = []
        for story in stories:
            draft = self.generate_drafts(story)
            if draft:
                drafts.append(draft)
        log.info(f"AIProcessor: Generated {len(drafts)} drafts from {len(stories)} stories")
        return drafts

    def _build_user_message(self, story: RawStory) -> str:
        """Construct the user message for Claude."""
        source_type_label = {
            "twitter": "X Profile",
            "google": "Google Search",
            "sec": "SEC Filing",
            "rss": "RSS Feed",
        }.get(story.source_type, story.source_type)

        source_name = story.source
        posted_info = f"\nPosted: {story.posted_at}" if story.posted_at else ""

        return (
            f"SOURCE TYPE: {source_type_label}\n"
            f"SOURCE NAME: {source_name}{posted_info}\n"
            f"TITLE/CONTENT: {story.title}\n"
            f"URL: {story.url}\n"
            f"\nRewrite this into three @AdrianJordan_io draft posts "
            f"following the Brand Voice and Hard Rules above."
        )

    def select_best_draft(self, draft: DraftPost, prefer_urgency: bool = False) -> str:
        """
        Pick the best draft option.

        Args:
            draft: DraftPost with 3 options
            prefer_urgency: If True, prefer option_1 (most impactful)

        Returns:
            The selected draft text
        """
        if prefer_urgency:
            return draft.option_1
        # For non-urgent, use option_2 (analytical) or option_1 as fallback
        if draft.option_2 and len(draft.option_2) > 10:
            return draft.option_2
        return draft.option_1

    def format_for_posting(self, draft_text: str, credit_line: str = "") -> str:
        """Final formatting for X posting."""
        # Ensure we have a credit line
        if credit_line and credit_line.strip():
            if not draft_text.endswith("\n"):
                draft_text += "\n\n"
            draft_text += credit_line.strip()

        # Truncate if too long (280 char X limit)
        if len(draft_text) > 280:
            draft_text = draft_text[:277] + "..."

        return draft_text
