"""
chatbot.py
----------
Core chatbot logic: wraps the OpenAI Chat Completions API and applies the
prompt-engineering layer from prompt_engineering.py.

Requires an OpenAI API key set as the environment variable OPENAI_API_KEY.
Get one at https://platform.openai.com/api-keys
"""

import os
from openai import OpenAI
from prompt_engineering import Conversation

DEFAULT_MODEL = "gpt-4o-mini"  # swap for "gpt-3.5-turbo" / "gpt-4" as needed


class ChatBot:
    def __init__(self, model: str = DEFAULT_MODEL, temperature: float = 0.7):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable not set. "
                "Get a key from https://platform.openai.com/api-keys and run:\n"
                "  export OPENAI_API_KEY=sk-...   (macOS/Linux)\n"
                "  setx OPENAI_API_KEY sk-...     (Windows)"
            )
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.conversation = Conversation()

    def reply(self, user_message: str, persona: str = None) -> dict:
        """
        Sends the user's message (plus engineered prompt + history) to the
        model and returns {"response": str, "intent": str}.
        """
        messages, intent = self.conversation.build_messages(user_message, persona=persona)

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=300,
        )
        reply_text = completion.choices[0].message.content

        # update memory with the real turn (not the system/few-shot scaffolding)
        self.conversation.add("user", user_message)
        self.conversation.add("assistant", reply_text)

        return {"response": reply_text, "intent": intent}

    def reset(self):
        self.conversation = Conversation()
