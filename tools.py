"""
tools.py
Simple tool the agent can call: free web search via DuckDuckGo.
No API key required for this one.
"""

from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 4) -> str:
    """
    Runs a web search and returns a compact, formatted string of results
    that can be fed straight into an LLM prompt.
    """
    formatted = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return f"No results found for query: {query}"
        for i, r in enumerate(results, start=1):
            title = r.get("title", "")
            body = r.get("body", "")
            href = r.get("href", "")
            formatted.append(f"[{i}] {title}\n{body}\nSource: {href}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Search failed for '{query}': {e}"
