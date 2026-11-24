"""
prompt_engineering.py
----------------------
Prompt-engineering layer for the chatbot. Instead of sending the user's raw
message straight to the model, this module builds a structured prompt:

  1. A SYSTEM prompt that fixes the bot's persona, tone, and behavioral rules.
  2. Optional FEW-SHOT examples that demonstrate the desired response style.
  3. Lightweight INTENT detection so the system prompt can be specialised
     per use case (customer support / FAQ / general companion chat).
  4. Conversation MEMORY (recent turns) so multi-turn context is preserved.

This is the "prompt engineering" deliverable required by the project brief.
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# 1. Persona / system prompts per use case
# ---------------------------------------------------------------------------

PERSONAS = {
    "general": (
        "You are Aria, a friendly and knowledgeable AI assistant. "
        "You answer clearly and concisely, admit when you don't know "
        "something, and keep a warm, approachable tone. Avoid making up "
        "facts you are not confident about."
    ),
    "customer_support": (
        "You are Aria, a customer support assistant for an online store. "
        "You are polite, patient, and solution-oriented. When a user "
        "reports a problem, first acknowledge it, then ask for any missing "
        "details (order ID, product name) before proposing a fix. Never "
        "promise refunds or actions you cannot verify — instead explain "
        "the next step the user should take."
    ),
    "faq": (
        "You are Aria, an FAQ assistant. Answer the user's question as "
        "directly and briefly as possible using at most 3 sentences. If "
        "the question is ambiguous, ask ONE clarifying question instead "
        "of guessing."
    ),
    "companion": (
        "You are Aria, a warm, upbeat conversational companion. You chat "
        "casually, show genuine curiosity about what the user shares, and "
        "keep responses conversational (1-3 sentences) rather than "
        "lecture-like."
    ),
}

# ---------------------------------------------------------------------------
# 2. Few-shot examples — shown to the model so it mimics the style/format
# ---------------------------------------------------------------------------

FEW_SHOT_EXAMPLES = {
    "customer_support": [
        {"role": "user", "content": "My order hasn't arrived yet."},
        {"role": "assistant", "content": (
            "Sorry to hear that — let's sort it out. Could you share your "
            "order ID? I'll check the shipping status for you."
        )},
    ],
    "faq": [
        {"role": "user", "content": "What are your business hours?"},
        {"role": "assistant", "content": "We're open Monday to Saturday, 9 AM to 7 PM."},
    ],
}

# ---------------------------------------------------------------------------
# 3. Very lightweight keyword-based intent detection
#    (a real system could swap this for a small classifier or the model's
#    own function-calling / classification output)
# ---------------------------------------------------------------------------

INTENT_KEYWORDS = {
    "customer_support": ["order", "refund", "delivery", "shipping", "broken", "cancel", "return"],
    "faq": ["hours", "location", "price", "policy", "how do i", "what is your"],
}


def detect_intent(message: str) -> str:
    lowered = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return intent
    return "general"


# ---------------------------------------------------------------------------
# 4. Conversation state + prompt assembly
# ---------------------------------------------------------------------------

@dataclass
class Conversation:
    history: list = field(default_factory=list)  # list of {"role", "content"}
    max_turns_remembered: int = 8  # keep prompt size bounded

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # keep only the most recent N turns (user+assistant pairs)
        max_messages = self.max_turns_remembered * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

    def build_messages(self, user_message: str, persona: str = None, use_few_shot: bool = True):
        """
        Builds the full `messages` list to send to the OpenAI chat completion
        endpoint: system prompt -> few-shot examples -> recent history -> new
        user message.
        """
        intent = persona or detect_intent(user_message)
        system_prompt = PERSONAS.get(intent, PERSONAS["general"])

        messages = [{"role": "system", "content": system_prompt}]

        if use_few_shot and intent in FEW_SHOT_EXAMPLES:
            messages.extend(FEW_SHOT_EXAMPLES[intent])

        messages.extend(self.history)
        messages.append({"role": "user", "content": user_message})
        return messages, intent
