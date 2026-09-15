from second_brain_bot.research.models import ResearchContext


def build_research_prompt(context: ResearchContext) -> str:
    knowledge = "\n\n".join(
        f"""
FILE: {match.path}
SCORE: {match.score}

{match.excerpt}
""".strip()
        for match in context.knowledge
    )

    sources = "\n\n".join(
        f"""
TITLE: {source.title}
URL: {source.url}

{source.content}
""".strip()
        for source in context.sources
    )

    return f"""
You are helping maintain a personal knowledge base.

Research topic:
{context.topic}

Category:
{context.category or "none"}

Existing knowledge:
{knowledge or "No related existing knowledge was found."}

Web research:
{sources or "No web sources were found."}

Analyse the topic using the provided evidence.

Your response should:

1. Explain the topic clearly.
2. Identify relationships with existing knowledge.
3. Identify whether existing knowledge already covers the topic.
4. Identify genuinely new information.
5. Point out contradictions or differences.
6. Suggest where the knowledge should belong.
7. Produce a concise research summary.

Do not invent relationships with existing knowledge.
Do not claim that information is from the web unless it appears
in the provided web sources.
""".strip()