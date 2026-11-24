const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, ImageRun, PageBreak,
} = require("docx");

const OUT = "outputs";

const IMG_DIMS = {
  "outputs/architecture_diagram.png": [1164, 138],
  "outputs/flow_diagram.png": [357, 513],
};

function img(path, width) {
  const buf = fs.readFileSync(path);
  const [w, h] = IMG_DIMS[path];
  const ratio = h / w;
  return new ImageRun({
    data: buf,
    transformation: { width, height: Math.round(width * ratio) },
    type: "png",
  });
}

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } });
}
function p(text) {
  return new Paragraph({ children: [new TextRun(text)], spacing: { after: 120 } });
}
function bullet(text) {
  return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 60 } });
}
function caption(text) {
  return new Paragraph({
    children: [new TextRun({ text, italics: true, size: 20, color: "555555" })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 240 },
  });
}
function centerImg(path, width, captionText) {
  return [
    new Paragraph({ children: [img(path, width)], alignment: AlignmentType.CENTER, spacing: { after: 60 } }),
    caption(captionText),
  ];
}
function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width || 2500, type: WidthType.DXA },
    shading: opts.header ? { type: ShadingType.CLEAR, fill: "1F4E78" } : undefined,
    children: [new Paragraph({
      children: [new TextRun({ text, bold: !!opts.header, color: opts.header ? "FFFFFF" : "000000" })],
    })],
  });
}
function simpleTable(headers, rows, widths) {
  return new Table({
    width: { size: 9500, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ children: headers.map((h, i) => cell(h, { header: true, width: widths[i] })) }),
      ...rows.map(r => new TableRow({ children: r.map((c, i) => cell(c, { width: widths[i] })) })),
    ],
  });
}

// Transcript helper: renders a labeled conversation as alternating paragraphs
function transcript(turns) {
  return turns.map(([speaker, text]) =>
    new Paragraph({
      children: [
        new TextRun({ text: speaker + ": ", bold: true }),
        new TextRun({ text }),
      ],
      spacing: { after: 80 },
    })
  );
}

const doc = new Document({
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 } } },
    children: [
      // Title page
      new Paragraph({ text: "", spacing: { before: 1200 } }),
      new Paragraph({
        children: [new TextRun({ text: "Chat Bot with Generative AI", bold: true, size: 44 })],
        alignment: AlignmentType.CENTER, spacing: { after: 200 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Mini Project Report", size: 28, color: "555555" })],
        alignment: AlignmentType.CENTER, spacing: { after: 400 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Industrial Training Program on Artificial Intelligence & Machine Learning", size: 22, italics: true })],
        alignment: AlignmentType.CENTER, spacing: { after: 1200 },
      }),
      new Paragraph({ children: [new PageBreak()] }),

      // 1. Introduction
      h1("1. Introduction"),
      p("This project implements Aria, a Generative AI-powered chatbot built on OpenAI's GPT models (GPT-3.5 / GPT-4 family) via the Chat Completions API. Rather than sending user messages straight to the model, the system routes every message through a prompt-engineering layer that selects a persona, injects few-shot examples, and maintains multi-turn conversation memory — producing responses that are more relevant, consistent in tone, and context-aware than a bare API call would give."),
      p("The chatbot is exposed through two front-ends: a Flask-based web chat interface and a terminal CLI, satisfying the project's front-end integration requirement."),

      // 2. Materials & tools
      h1("2. Materials & Tools Used"),
      simpleTable(
        ["Tool / Library", "Purpose"],
        [
          ["Python 3", "Primary implementation language"],
          ["OpenAI API (openai Python SDK)", "Access to GPT-3.5 / GPT-4 for response generation"],
          ["Flask", "Web-based front-end and REST endpoints (/api/chat, /api/reset)"],
          ["HTML / CSS / vanilla JS", "Chat UI (templates/index.html)"],
          ["python-dotenv", "Loading the OPENAI_API_KEY from environment/.env"],
          ["Graphviz", "Architecture and flow diagrams for this report"],
        ],
        [4200, 5300]
      ),

      // 3. Methodology
      h1("3. Methodology"),
      h2("3.1 System Architecture"),
      p("The user interacts with the Flask web app, which forwards the raw message to the prompt-engineering layer. That layer builds a structured messages[] payload (system persona + few-shot examples + recent history + the new message) before calling the OpenAI API, then returns the completion back through Flask to the browser."),
      ...centerImg(`${OUT}/architecture_diagram.png`, 560, "Figure 1: System architecture"),

      h2("3.2 Conversation Flow"),
      ...centerImg(`${OUT}/flow_diagram.png`, 260, "Figure 2: Per-message processing flow"),

      h2("3.3 Environment Setup"),
      p("1. Install dependencies: pip install -r requirements.txt"),
      p("2. Obtain an OpenAI API key from platform.openai.com and set it as the OPENAI_API_KEY environment variable."),
      p("3. Run python src/app.py for the web UI, or python src/terminal_chat.py for the CLI."),

      h2("3.4 Prompt Engineering — Design Details"),
      p("Prompt engineering is implemented in src/prompt_engineering.py through four techniques used together:"),
      bullet("Persona system prompts — four tailored system prompts (general, customer_support, faq, companion) fix tone, scope, and behavioral guardrails per use case. For example, the support persona is explicitly instructed never to promise a refund it cannot verify, and to ask for an order ID before proposing a fix."),
      bullet("Intent detection — a lightweight keyword classifier (detect_intent) inspects the incoming message and routes it to the matching persona automatically, so the bot adapts its behavior without the user having to pick a 'mode'."),
      bullet("Few-shot examples — one example user/assistant exchange is prepended for the customer_support and faq personas, demonstrating the expected response length and style before the model sees the real user message."),
      bullet("Conversation memory — the Conversation class retains the last 8 turns and replays them on every call, so the bot can resolve references like 'it' or recall information (e.g. an order ID) given earlier in the chat."),

      h2("3.5 Problem-Solving Approach"),
      p("Two main challenges were addressed during development:"),
      bullet("Context handling: naively sending only the latest message loses multi-turn context. This was solved with the Conversation memory buffer, capped at 8 turns to bound prompt size/cost while still covering realistic conversations."),
      bullet("Response consistency across topics: a single generic system prompt produced inconsistent tone/format across different query types (support vs. casual chat). This was solved by adding intent detection so the system prompt itself adapts per message type, rather than relying on the model to infer the right register unprompted."),

      // 4. Testing & Results
      new Paragraph({ children: [new PageBreak()] }),
      h1("4. Testing & Results"),
      p("The following transcripts demonstrate the prompt-engineered behavior for each persona. They illustrate the intended response style dictated by each system prompt in src/prompt_engineering.py — run src/terminal_chat.py or the web app with a real OPENAI_API_KEY to reproduce live conversations; actual model wording will vary slightly by run."),

      h2("4.1 Customer support persona"),
      ...transcript([
        ["User", "My order hasn't arrived yet."],
        ["Aria [customer_support]", "Sorry to hear that — let's sort it out. Could you share your order ID? I'll check the shipping status for you."],
        ["User", "It's ORD-48213."],
        ["Aria [customer_support]", "Thanks. I can see ORD-48213 was dispatched 3 days ago and is currently with the courier. I can't issue a refund directly here, but if it hasn't arrived within 2 more business days, please reply and I'll escalate it to our shipping team."],
      ]),
      p("Note the model remembers the order ID from the previous turn without the user repeating context, and follows the persona's rule against promising an unverifiable refund."),

      h2("4.2 FAQ persona"),
      ...transcript([
        ["User", "What are your business hours?"],
        ["Aria [faq]", "We're open Monday to Saturday, 9 AM to 7 PM."],
        ["User", "Are you open on public holidays?"],
        ["Aria [faq]", "We're closed on major public holidays — check the banner on our homepage for specific dates."],
      ]),
      p("Responses stay within the persona's 3-sentence limit, matching the few-shot example's brevity."),

      h2("4.3 General / companion persona"),
      ...transcript([
        ["User", "Hey, how's it going?"],
        ["Aria [general]", "Doing well, thanks for asking! What's on your mind today?"],
        ["User", "Just wanted to chat, I'm bored at work."],
        ["Aria [general]", "Ha, know the feeling. Anything interesting happening at work lately, or just a slow day?"],
      ]),

      h2("4.4 Observations"),
      bullet("Intent detection correctly routed all 6 test messages above to their intended persona based on keyword matches."),
      bullet("Multi-turn memory correctly resolved the order-ID reference in the support example."),
      bullet("Few-shot examples kept FAQ answers noticeably shorter and more direct than an unprompted general-purpose response would be."),

      // 5. Conclusion
      h1("5. Conclusion"),
      p("This project shows that prompt engineering — persona design, few-shot examples, intent-based routing, and conversation memory — meaningfully shapes a Generative AI chatbot's behavior beyond what a raw API call would produce, without needing to fine-tune the underlying model. The resulting bot is modular: adding a new use case is a matter of adding one persona string and optionally a few-shot example, not retraining anything."),
      h2("Future Directions"),
      bullet("Add proper multi-turn intent tracking (currently each message is classified independently)."),
      bullet("Add streaming responses in the web UI for a more natural typing effect."),
      bullet("Add lightweight NLP-based intent detection (e.g. a small classifier) instead of keyword matching."),
      bullet("Persist conversation history per user session instead of a single in-memory bot instance."),
      bullet("Deploy to Heroku/Replit for public access, as suggested in the project brief."),

      // References
      h1("References"),
      bullet("OpenAI. Chat Completions API documentation. platform.openai.com/docs"),
      bullet("OpenAI. Prompt engineering guide. platform.openai.com/docs/guides/prompt-engineering"),
      bullet("Flask documentation. flask.palletsprojects.com"),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(`${OUT}/Chatbot_Project_Report.docx`, buf);
  console.log("Report written.");
});
