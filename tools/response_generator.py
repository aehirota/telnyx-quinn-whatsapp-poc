"""Generate Quinn's WhatsApp reply in English based on the qualification result.

Implementation: LangChain (ChatAnthropic + ChatPromptTemplate). Plain string
output — no Pydantic schema needed.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

load_dotenv(Path(__file__).parent.parent / ".env")
DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")

SYSTEM_PROMPT = """You are Quinn, Telnyx's AI SDR, replying to a WhatsApp inbound.

CRITICAL: Reply in ENGLISH ONLY, even when the inbound message is in Portuguese, Spanish, or any other language. Telnyx's LATAM SDRs handle the Portuguese/Spanish conversation after Quinn hands off — Quinn's job is qualification + handoff in English. Never reply in Portuguese or Spanish.

HARD LIMIT: under 280 characters. Native to WhatsApp, not corporate email. No emojis, no "hope this finds you well," no marketing fluff.

Routing dictates shape:
- sdr_followup: acknowledge use case, ONE clarifying question, promise human SDR within 4 business hours.
- marketing_nurture: brief acknowledgement, point to https://telnyx.com/docs, invite reply.
- deflect: note it's outside Telnyx's scope, redirect to right place (e.g. their carrier, https://support.telnyx.com).

Return ONLY the English reply text. Count characters before responding."""


_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Original inbound message:\n{message_text}\n\nSender: {sender_name}\nQualification: {qualification}\n\nWrite Quinn's reply now."),
])
_llm = ChatAnthropic(model=DEFAULT_MODEL, max_tokens=120)
_chain = _prompt | _llm


def generate_reply(message_text: str, qualification: dict, sender_name: str | None = None) -> str:
    """Generate Quinn's reply via LangChain. Returns the reply text in English."""
    result = _chain.invoke({
        "message_text": message_text,
        "sender_name": sender_name or "unknown",
        "qualification": qualification,
    })
    return result.content.strip()


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    qual = {
        "icp_fit": "high",
        "intent": "high",
        "company_guess": "Conta Simples",
        "use_case": "Replacing Twilio for support team voice",
        "routing": "sdr_followup",
        "reasoning": "Mid-market fintech, named vendor, has a deadline.",
    }
    print(generate_reply("Oi, sou da Conta Simples, queremos trocar a Twilio.", qual, "Mariana Costa"))
