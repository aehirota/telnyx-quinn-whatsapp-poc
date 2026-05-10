"""Detect the language of an inbound message and flag LATAM leads."""

from langdetect import DetectorFactory, LangDetectException, detect

DetectorFactory.seed = 0  # deterministic detection across runs

LATAM_LANGUAGES = {"pt", "es"}


def detect_language(text: str) -> dict:
    """Return language ISO code and whether the lead is LATAM.

    On detection failure (e.g. very short text), returns language='unknown'
    and is_latam=False — see workflows/whatsapp-qualification.md Step 2.
    """
    try:
        lang = detect(text)
    except LangDetectException:
        return {"language": "unknown", "is_latam": False}

    return {"language": lang, "is_latam": lang in LATAM_LANGUAGES}


if __name__ == "__main__":
    import sys

    sample = sys.argv[1] if len(sys.argv) > 1 else "Oi, tudo bem?"
    print(detect_language(sample))
