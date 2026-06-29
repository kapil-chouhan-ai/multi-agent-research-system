import json

from schemas.findings import Finding
from schemas.reflection import Reflection

REFLECT_PROMPT = """
You are judging whether research findings are sufficient to stop searching.

Rules:
- sufficient = true only if there are at least 3 facts AND they are specific
  (contain numbers, dates, named entities, or measurements rather than
  generic statements).
- If not sufficient, propose a refined_query: a short, more specific search
  query targeting what is missing (e.g. a sub-aspect, a missing metric, a
  missing date range). Do not repeat the original topic verbatim.
- If sufficient, refined_query must be null.

Return ONLY valid JSON matching this schema:
{
    "sufficient": true | false,
    "reason": "<one short sentence>",
    "refined_query": "<string or null>"
}
"""


class ReflectNode:
    def __init__(self, client, model: str = "llama-3.1-8b-instant"):
        self.client = client
        self.model = model

    def run(self, topic: str, finding: Finding) -> Reflection:
        facts_text = "\n".join(f"- {f.statement}" for f in finding.facts)
        user_content = f"Topic: {topic}\n\nCurrent facts:\n{facts_text or '(none)'}"

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": REFLECT_PROMPT},
                {"role": "user", "content": user_content},
            ],
            model=self.model,
            temperature=0.0,
        )

        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(content)
            return Reflection.model_validate(data)
        except Exception:
            # Fail safe: if the judge call itself breaks, don't block the
            # pipeline on it -- treat current facts as sufficient.
            return Reflection(sufficient=True, reason="reflect_parse_failed", refined_query=None)
