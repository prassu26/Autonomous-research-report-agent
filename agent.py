"""
agent.py
The agentic pipeline: Plan -> Research -> Critique -> Write.
Built with LangGraph so the control flow (including the critic's loop-back)
is an explicit, inspectable graph -- a good talking point for a viva/demo.
"""

import os
from typing import TypedDict, List
from anthropic import Anthropic
from langgraph.graph import StateGraph, END

from tools import web_search

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"


def ask_llm(prompt: str) -> str:
    """Single-call helper around the Anthropic API."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


class AgentState(TypedDict):
    topic: str
    subquestions: List[str]
    findings: List[str]
    critique: str
    revisions: int
    report: str


# ---------- Graph nodes ----------

def plan_node(state: AgentState) -> AgentState:
    prompt = (
        f"Break the research topic '{state['topic']}' into exactly 4 clear, "
        f"specific sub-questions that together would let someone write a "
        f"thorough report. Return ONLY the 4 questions, one per line, no numbering."
    )
    raw = ask_llm(prompt)
    state["subquestions"] = [q.strip("- ").strip() for q in raw.split("\n") if q.strip()]
    state["revisions"] = 0
    return state


def research_node(state: AgentState) -> AgentState:
    findings = []
    for q in state["subquestions"]:
        search_results = web_search(q)
        summary_prompt = (
            f"Question: {q}\n\nRaw search results:\n{search_results}\n\n"
            f"Summarize the answer to the question in 3-4 sentences, "
            f"using only the information above."
        )
        answer = ask_llm(summary_prompt)
        findings.append(f"Q: {q}\nA: {answer}")
    state["findings"] = findings
    return state


def critic_node(state: AgentState) -> AgentState:
    combined = "\n\n".join(state["findings"])
    prompt = (
        f"Topic: {state['topic']}\n\nResearch findings so far:\n{combined}\n\n"
        f"Are these findings sufficient and specific enough to write a solid "
        f"report on the topic? Reply with 'SUFFICIENT' if yes, or if not, "
        f"reply with 'INSUFFICIENT:' followed by one missing sub-question to research."
    )
    state["critique"] = ask_llm(prompt)
    return state


def route_after_critic(state: AgentState) -> str:
    if state["critique"].startswith("SUFFICIENT") or state["revisions"] >= 2:
        return "write"
    return "revise"


def revise_node(state: AgentState) -> AgentState:
    missing_q = state["critique"].split(":", 1)[-1].strip()
    state["subquestions"] = [missing_q]
    state["revisions"] += 1
    return state


def write_node(state: AgentState) -> AgentState:
    combined = "\n\n".join(state["findings"])
    prompt = (
        f"Write a well-structured report (with headings) on '{state['topic']}' "
        f"using the following research findings as source material:\n\n{combined}\n\n"
        f"Include: Introduction, 2-3 body sections, and a Conclusion."
    )
    state["report"] = ask_llm(prompt)
    return state


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan_node)
    graph.add_node("research", research_node)
    graph.add_node("critic", critic_node)
    graph.add_node("revise", revise_node)
    graph.add_node("write", write_node)

    graph.set_entry_point("plan")
    graph.add_edge("plan", "research")
    graph.add_edge("research", "critic")
    graph.add_conditional_edges("critic", route_after_critic, {
        "write": "write",
        "revise": "revise",
    })
    graph.add_edge("revise", "research")
    graph.add_edge("write", END)

    return graph.compile()


def run_agent(topic: str) -> dict:
    app = build_graph()
    final_state = app.invoke({"topic": topic})
    return final_state
