REPORTER_PROMPT = """
        Create a research report from the provided findings.

        Rules:

        - Use only the provided findings.
        - Do not use external knowledge.
        - Do not invent facts.
        - Do not infer conclusions.
        - Do not add background information.
        - Preserve specific details, numbers, product names, and organizations.
        - Remove duplicate information.
        - Merge related facts into concise summaries.
        - Include all relevant source URLs for each section.

        Summary:
        - Cover the major findings across all topics.
        - Keep it concise.

        Sections:
        - Create one section per topic.
        - Summarize the findings for that topic.
        - Preserve important facts.
        - Do not repeat the same information multiple times.

        Return ONLY valid JSON.

        IMPORTANT:
        - title must be a single-line string.
        - summary must be a single-line string.
        - section content must be a single-line string.
        - Do not use line breaks inside JSON values.
        - Output must be directly parsable by Python json.loads().

        Schema:

        {
            "title": "...",
            "summary": "...",
            "sections": [
                {
                    "topic": "...",
                    "content": "...",
                    "sources": ["..."]
                }
            ]
        }
"""