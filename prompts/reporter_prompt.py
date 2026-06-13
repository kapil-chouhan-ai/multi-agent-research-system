REPORTER_PROMPT = """
        Create a research report from the provided findings.

        Rules:
        - Use all findings.
        - summary should touch all the sections and be a atmost 8 - 10 lines
        - Expand findings into coherent paragraphs.
        - Each section should contain detailed 12 - 16 lines.
        - Preserve factual accuracy.
        - Do not invent information.
        - Include relevant sources.
        - Do not infer future outcomes.
        - Do not add conclusions not explicitly supported by findings.

        Return ONLY valid JSON.

        Schema:

        {
            "title": "<report title>",
            "summary": "<executive summary>",
            "sections": [
                {
                    "topic": "<research topic>",
                    "content": "<topic summary>"
                    "sources": [
                        "<source_1>",
                        "<source_2>"..
                    ]
                }
            ]
        }
"""