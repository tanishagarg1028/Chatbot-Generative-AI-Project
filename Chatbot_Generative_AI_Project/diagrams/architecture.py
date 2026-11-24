import graphviz

dot = graphviz.Digraph("architecture", format="png")
dot.attr(rankdir="LR", bgcolor="white", fontname="Helvetica", nodesep="0.4", ranksep="0.6")
dot.attr("node", shape="box", style="rounded,filled", fontname="Helvetica",
         fontsize="12", margin="0.2,0.12")

nodes = [
    ("user", "User\n(web browser)", "#DCEBFA"),
    ("flask", "Flask Web App\n(app.py)", "#D6F0E4"),
    ("prompt", "Prompt Engineering\n(intent detection,\nsystem prompt, memory)", "#FCE8D6"),
    ("openai", "OpenAI API\n(GPT-3.5 / GPT-4)", "#F5DCE3"),
]

for key, label, color in nodes:
    dot.node(key, label, fillcolor=color, color="#888888")

dot.edge("user", "flask", label="  types message", fontsize="10", fontname="Helvetica")
dot.edge("flask", "prompt", label="  raw text", fontsize="10", fontname="Helvetica")
dot.edge("prompt", "openai", label="  engineered\n  messages[]", fontsize="10", fontname="Helvetica")
dot.edge("openai", "flask", label="  completion", fontsize="10", fontname="Helvetica", style="dashed")
dot.edge("flask", "user", label="  response", fontsize="10", fontname="Helvetica", style="dashed")

dot.render("/home/claude/chatbot_ai/outputs/architecture_diagram", cleanup=True)
print("saved")
