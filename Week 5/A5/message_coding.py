"""
Rule-based chat message coding for sentiment labels and short summaries.

Used by collect_vod_chat.py and collect_chat.py so CSV outputs stay consistent.
Designed for esports / live-chat style text (short bursts, slang, emojis).
"""

from __future__ import annotations

import re


def code_message_text(message_text: str) -> tuple[str, str]:
    """
    Assign a coarse sentiment/category label and a very short summary string.

    Returns:
        (message_sentiment, message_summary)
    """
    text = (message_text or "").strip()
    if not text:
        return "unclear", "empty message"

    text_lower = text.lower()
    words = _token_words(text_lower)

    if re.fullmatch(r"\?+", text):
        return "questioning_confusion", "question marks only"
    if re.fullmatch(r"!+", text):
        return "excitement", "exclamation only"

    if "http://" in text_lower or "https://" in text_lower or "www." in text_lower:
        return "link_reference", "contains link"

    if _is_emoji_heavy(text):
        mood = _emoji_sentiment_bucket(text)
        return mood, "emoji-heavy message"

    if "?" in text:
        return "questioning", "question"

    # Strong affect / stance (order: frustration first so "lol int" still reads negative)
    if _contains_any(text_lower, _CRITICISM):
        return "frustration_criticism", "negative or critical"
    if _contains_any(text_lower, _HUMOR):
        return "humor_positive", "laughing or meme tone"
    if _contains_any(text_lower, _PRAISE):
        return "praise_sportsmanship", "praise or gg"
    if _contains_any(text_lower, _TENSION):
        return "tension_anticipation", "stress or clutch moment"
    if _contains_any(text_lower, _SURPRISE):
        return "surprise_awe", "shock or amazement"
    if _contains_any(text_lower, _HYPE):
        return "hype_celebration", "hype or hype slang"
    if _contains_any(text_lower, _AGREEMENT):
        return "agreement_ack", "agrees or pushes back briefly"

    if text.isupper() and len(text) >= 4 and re.search(r"[A-Z]", text):
        return "emphasis_caps", "all caps emphasis"

    if not words:
        if re.fullmatch(r"[ao]+\}?|h+m+", text_lower):
            return "vocal_reaction", "stretched sound"
        return "symbols_only", "symbols or punctuation only"

    if len(words) == 1 and words[0] in _SINGLE_WORD_SENTIMENT:
        return _SINGLE_WORD_SENTIMENT[words[0]]

    if len(words) <= 4 and _tokens_intersect(words, _TEAM_OR_TAG_WORDS):
        return "fandom_reference", "team or tag mention"

    score_like = re.search(r"\b\d\s*[-:]\s*\d\b", text)
    if score_like:
        return "score_or_stat", "numeric score pattern"

    if _is_stretched_token(words):
        return "emphasis_stretched", "stretched letters"

    if len(words) <= 2:
        return "brief_remark", _summary_from_words(words)

    return "general_chat", _summary_from_words(words)


def _contains_any(haystack: str | Iterable[str], needles: Iterable[str]) -> bool:
    if isinstance(haystack, str):
        return any(n in haystack for n in needles)
    hay = frozenset(haystack)
    return not hay.isdisjoint(needles)


def _token_words(text_lower: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text_lower)


def _summary_from_words(words: list[str]) -> str:
    if not words:
        return "no text tokens"
    return " ".join(words[:4])


# --- Keyword buckets (lowercased) ---

_CRITICISM = frozenset({
    "wtf", "int", "inting", "inters", "trash", "garbage", "dog", "troll",
    "grief", "griefing", "boosted", "diff", "gap", "bad", "terrible", "awful",
    "horrible", "disastrous", "embarrassing", "lose", "lost", "rip", "unlucky",
})

_HUMOR = frozenset({
    "lol", "lmao", "lmfao", "rofl", "haha", "hehe", "kek", "kekw", "lul", "omegalul",
})

_PRAISE = frozenset({
    "gg", "ggs", "wp", "ggwp", "nice", "clean", "clapped", "respect", "well",
    "deserved", "earned", "glhf", "hf", "gl",
})

_TENSION = frozenset({
    "clutch", "please", "stress", "scary", "close", "sweating", "choke",
})

_SURPRISE = frozenset({
    "omg", "omfg", "woah", "wow", "holy", "damn", "insane", "crazy", "what",
})

_HYPE = frozenset({
    "pog", "poggers", "pogchamp", "hyped", "letsgo", "goated", "cracked", "nailed",
})

_AGREEMENT = frozenset({
    "yes", "yep", "yeah", "yup", "no", "nope", "nah", "ok", "okay", "same",
    "true", "fair", "real", "facts", "cap", "literally", "this", "agree", "disagree",
})

_TEAM_OR_TAG_WORDS = frozenset({
    # LEC / general esports chat tokens (expand as needed)
    "fnc", "g2", "vit", "bds", "sk", "mad", "koi", "xl", "rog", "ast",
    "lec", "msi", "worlds", "lck", "lcs", "lpl",
})


_SINGLE_WORD_SENTIMENT: dict[str, tuple[str, str]] = {
    "gg": ("praise_sportsmanship", "gg"),
    "wp": ("praise_sportsmanship", "wp"),
    "pog": ("hype_celebration", "pog"),
    "oof": ("frustration_criticism", "oof"),
    "rip": ("frustration_criticism", "rip"),
    "yes": ("agreement_ack", "yes"),
    "no": ("agreement_ack", "no"),
    "nice": ("praise_sportsmanship", "nice"),
    "wtf": ("frustration_criticism", "wtf"),
}


# Heart / romance emoji block (not exhaustive but covers common chat hearts)
_EMOJI_HEART_RANGE = re.compile(r"[\U0001F493-\U0001F49F\U00002764\U00002763\U0000FE0F]")
_EMOJI_EMOTICONS = re.compile(r"[\U0001F600-\U0001F64F]")


def _is_emoji_heavy(text: str) -> bool:
    e = _count_emoji_chars(text)
    if e == 0:
        return False
    letters = len(re.findall(r"[A-Za-z]", text))
    if letters == 0:
        return True  # emoji-only (or emoji + spaces/punctuation)
    # Mostly emoji compared to letters — typical sticker-style chat
    return e >= max(3, letters)


def _count_emoji_chars(text: str) -> int:
    # Broad emoji + symbols pick-up (good enough for chat without extra deps)
    return len(re.findall(
        r"[\U00002600-\U000027BF\U0001F300-\U0001FAFF\U0000FE00-\U0000FE0F]",
        text,
    ))


def _emoji_sentiment_bucket(text: str) -> str:
    if _EMOJI_HEART_RANGE.search(text):
        return "affection_support"
    if "\U0001F525" in text or "\U0001F4AF" in text:
        return "hype_celebration"
    if _EMOJI_EMOTICONS.search(text):
        return "humor_positive"
    return "emoji_reaction"


def _is_stretched_token(words: list[str]) -> bool:
    if len(words) != 1:
        return False
    w = words[0]
    if len(w) < 4:
        return False
    # e.g. yesss, noooo, goooo
    return bool(re.match(r"^(.)\1{2,}", w))


def _tokens_intersect(words: list[str], bag: frozenset[str]) -> bool:
    return not frozenset(words).isdisjoint(bag)
