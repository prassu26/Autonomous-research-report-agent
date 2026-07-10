"""
main.py
Run this file in VS Code (Run > Run Without Debugging, or `python main.py`)
to try the autonomous research agent end to end.
"""

import os
from dotenv import load_dotenv
from agent import run_agent

load_dotenv()  # loads ANTHROPIC_API_KEY from .env


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY in a .env file (see .env.example).")
        return

    topic = input("Enter a research topic: ").strip()
    if not topic:
        topic = "Impact of agentic AI on software engineering"
        print(f"No topic entered, using default: '{topic}'")

    print("\n Agent is planning, researching, and writing... this may take a minute.\n")
    result = run_agent(topic)

    print("\n===== SUB-QUESTIONS RESEARCHED =====")
    for q in result["subquestions"]:
        print("-", q)

    print("\n===== FINAL REPORT =====\n")
    print(result["report"])

    out_path = "report_output.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Research Report: {topic}\n\n{result['report']}")
    print(f"\n(Saved to {out_path})")


if __name__ == "__main__":
    main()
