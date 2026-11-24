import graphviz

dot = graphviz.Digraph("flow", format="png")
dot.attr(rankdir="TB", bgcolor="white", fontname="Helvetica", nodesep="0.35", ranksep="0.4")
dot.attr("node", shape="box", style="rounded,filled", fontname="Helvetica",
         fontsize="12", margin="0.2,0.1")

steps = [
    ("input", "User types a query", "#DCEBFA"),
    ("intent", "Detect intent\n(support / faq / companion / general)", "#FCE8D6"),
    ("build", "Build engineered prompt\n(system persona + few-shot + history)", "#FCE8D6"),
    ("api", "Send to OpenAI Chat\nCompletions API", "#D6F0E4"),
    ("memory", "Append turn to\nconversation memory", "#D6F0E4"),
    ("output", "Display response to user", "#F5DCE3"),
]

for key, label, color in steps:
    dot.node(key, label, fillcolor=color, color="#888888")

keys = [s[0] for s in steps]
for a, b in zip(keys, keys[1:]):
    dot.edge(a, b, color="#666666")

dot.render("/home/claude/chatbot_ai/outputs/flow_diagram", cleanup=True)
print("saved")
