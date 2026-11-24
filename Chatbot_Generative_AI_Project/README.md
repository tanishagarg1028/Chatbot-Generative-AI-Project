# Aria — Generative AI Chatbot

Mini project: a prompt-engineered chatbot built on the OpenAI GPT API, with
both a web UI (Flask) and a terminal interface.

## Project structure

```
chatbot_ai/
├── src/
│   ├── prompt_engineering.py   # personas, few-shot examples, intent detection, memory
│   ├── chatbot.py               # OpenAI API wrapper using the engineered prompts
│   ├── app.py                    # Flask web app (routes: /, /api/chat, /api/reset)
│   └── terminal_chat.py          # simple CLI chat interface
├── templates/
│   └── index.html                 # chat UI
├── diagrams/                      # scripts that generate the report diagrams
├── outputs/                       # architecture + flow diagrams
└── requirements.txt
```

## 1. Get an OpenAI API key

Sign up at https://platform.openai.com, then create a key at
https://platform.openai.com/api-keys.

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Set your API key

```bash
export OPENAI_API_KEY=sk-...        # macOS/Linux
setx OPENAI_API_KEY sk-...          # Windows (new terminal after)
```

## 4. Run it

**Web app:**
```bash
python src/app.py
```
Then open http://localhost:5000 in your browser.

**Terminal chat:**
```bash
python src/terminal_chat.py
```

## How the prompt engineering works

See `src/prompt_engineering.py`. Every user message goes through:

1. **Intent detection** — a lightweight keyword classifier tags the message
   as `customer_support`, `faq`, or `general` (falls back to a `companion`
   persona if you pass `persona="companion"` explicitly).
2. **Persona injection** — each intent maps to a tailored system prompt
   that fixes tone, scope, and behavioral rules (e.g. the support persona
   is told never to promise a refund it can't verify).
3. **Few-shot examples** — for `customer_support` and `faq`, one example
   exchange is prepended so the model mirrors the expected response style
   and length.
4. **Conversation memory** — the last 8 turns are kept and replayed on every
   call so the bot handles multi-turn context (e.g. remembering an order ID
   given two messages ago).

## Testing

`src/prompt_engineering.py` has no external dependencies and can be
exercised without an API key:

```bash
python -c "
from src.prompt_engineering import detect_intent
print(detect_intent('My order hasn't arrived yet'))  # -> customer_support
"
```

For full conversation testing, run `terminal_chat.py` or the web app with a
real `OPENAI_API_KEY` set. See the project report for example transcripts.
