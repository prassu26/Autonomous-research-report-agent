# Autonomous Research & Report Agent

A final-year mini project demonstrating **agentic AI**: an agent that plans
its own research steps, uses a web search tool, critiques its own findings,
loops back if needed, and writes a final structured report — with no human
in the loop after the topic is given.

## How it works (the agent loop)

```
   ┌──────┐    ┌────────────┐    ┌────────┐
   │ Plan │───▶│  Research  │───▶│ Critic │
   └──────┘    └────────────┘    └───┬────┘
                     ▲               │
                     │        sufficient? ──yes──▶ Write ──▶ Done
                     │               │
                     └────Revise◀────┘ no (loop, up to 2x)
```

1. **Plan** – LLM breaks the topic into 4 sub-questions.
2. **Research** – for each sub-question, the agent calls a real web search
   tool (DuckDuckGo, free, no API key) and summarizes the results.
3. **Critic** – the LLM judges whether the findings are good enough. If not,
   it names what's missing and the agent loops back to research it.
4. **Write** – once findings are sufficient, the LLM writes a structured
   report (Intro / body / conclusion), saved to `report_output.md`.

This is what separates it from a plain chatbot: the LLM is making decisions
about *what to do next* (which questions to research, whether to stop),
not just answering one prompt.

## Setup (VS Code)

1. Open this folder in VS Code.
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
5. Run it:
   ```
   python main.py
   ```
   Or press "Run" (▶) on `main.py` in VS Code.

## Files

| File | Purpose |
|---|---|
| `main.py` | Entry point — takes topic input, runs agent, prints/saves report |
| `agent.py` | Core agent logic: the LangGraph state machine (plan/research/critic/write) |
| `tools.py` | The search tool the agent calls |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for your API key |

## Ideas to extend (for extra marks)

- Add a **vector store** (e.g. Chroma) so the agent remembers past reports (RAG).
- Add a **Streamlit UI** so it's a live web app instead of a terminal script.
- Add more tools (Wikipedia API, arXiv API) and let the planner choose which
  tool fits each sub-question.
- Export the final report straight to a `.docx` or `.pdf` file.
- Add unit tests for each node using `pytest`.

## Notes

- Swap `MODEL` in `agent.py` if you want to use a different Claude model.
- If you don't have an Anthropic key, this can be adapted to OpenAI's API
  with minimal changes (swap the `Anthropic` client calls in `agent.py`).
