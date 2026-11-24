"""
terminal_chat.py
-----------------
Simple terminal-based interface for the chatbot (fallback / quick testing,
per the project's "simple front-end integration" deliverable).

Run:
    export OPENAI_API_KEY=sk-...
    python src/terminal_chat.py
"""

from chatbot import ChatBot


def main():
    print("=" * 50)
    print(" Aria — Generative AI Chatbot (terminal mode)")
    print(" Type 'reset' to clear memory, 'exit' to quit.")
    print("=" * 50)

    bot = ChatBot()

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Aria: Goodbye!")
            break
        if user_input.lower() == "reset":
            bot.reset()
            print("Aria: Memory cleared.")
            continue

        try:
            result = bot.reply(user_input)
            print(f"Aria [{result['intent']}]: {result['response']}")
        except Exception as e:
            print(f"[error] {e}")


if __name__ == "__main__":
    main()
