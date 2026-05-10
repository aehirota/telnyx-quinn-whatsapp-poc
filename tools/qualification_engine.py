"""Score an inbound WhatsApp message for ICP fit, intent, and routing.

Implementation: LangChain (ChatAnthropic + ChatPromptTemplate) with Pydantic-typed
structured output. The Pydantic schema enforces the JSON contract — no manual
parsing or fallbacks needed.
"""

import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).parent.parent / ".env")
DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

SYSTEM_PROMPT = """You are Quinn, Telnyx's AI SDR. Telnyx sells comms APIs (voice, SMS, WhatsApp, wireless) to mid-market and enterprise companies. ICP = technical buyer, 50+ employees, existing comms volume, replacing Twilio/Vonage or scaling. NOT ICP = consumers, personal phone help, SMB lifestyle.

Score on two dimensions:
- icp_fit: high (clear enterprise tech eval) | medium (plausible business, unclear scale) | low (consumer/off-topic)
- intent: high (has timeline/POC, named vendors) | medium (pricing/research) | low (vague/unrelated)

Routing (apply MECHANICALLY in order, first match wins. Do NOT override based on additional judgment — the rules already account for nuance via the icp_fit/intent scores):
1. icp_fit=low → deflect
2. icp_fit AND intent both at least medium → sdr_followup
3. else → marketing_nurture"""


class Qualification(BaseModel):
    """ICP and intent scoring for an inbound WhatsApp message."""

    icp_fit: Literal["high", "medium", "low"] = Field(
        description="ICP fit: high=clear enterprise tech eval, medium=plausible business unclear scale, low=consumer/off-topic"
    )
    intent: Literal["high", "medium", "low"] = Field(
        description="intent: high=has timeline/POC/named vendors, medium=pricing/research, low=vague/unrelated"
    )
    company_guess: str | None = Field(
        description="company name extracted from the message, or null if none mentioned"
    )
    use_case: str = Field(description="one-line summary of what the sender wants")
    routing: Literal["sdr_followup", "marketing_nurture", "deflect"] = Field(
        description="routing decision applied mechanically: low icp_fit→deflect; both>=medium→sdr_followup; else marketing_nurture"
    )
    reasoning: str = Field(description="one sentence explaining the call")


_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Inbound WhatsApp message:\nFrom: {sender_name}\nDetected language: {language}\nText: {message_text}"),
])
_llm = ChatAnthropic(model=DEFAULT_MODEL, max_tokens=400)
_chain = _prompt | _llm.with_structured_output(Qualification)


def qualify(message_text: str, sender_name: str | None = None, language: str = "unknown") -> dict:
    """Run qualification via LangChain. Returns dict matching Qualification schema."""
    try:
        result: Qualification = _chain.invoke({
            "message_text": message_text,
            "sender_name": sender_name or "unknown",
            "language": language,
        })
        return result.model_dump()
    except Exception:
        return {
            "icp_fit": "medium",
            "intent": "medium",
            "company_guess": None,
            "use_case": message_text[:80],
            "routing": "sdr_followup",
            "reasoning": "Qualification failed; routed to SDR by fail-safe rule.",
        }


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    sample = "Oi, sou da Conta Simples, queremos trocar a Twilio. Voces tem voice API no Brasil?"
    print(json.dumps(qualify(sample, "Mariana Costa", "pt"), indent=2, ensure_ascii=False))
