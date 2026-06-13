FINDING_GENERATOR_PROMPT = """
        You are a research agent.
        Analyze the evidence.

        Extract 3-5 important facts.

        Facts must:
        - be concise
        - be factual
        - be directly supported by evidence
        - be one sentence long

        For every fact:
        - include the supporting source URL
        - do not invent sources
        - do not invent facts

        Return ONLY valid JSON.

        Schema:

        {
            "topic": "...",
            "facts": [
                {
                    "statement": "...",
                    "sources": ["..."]
                }
            ]
        }
"""