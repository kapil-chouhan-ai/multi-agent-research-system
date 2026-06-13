from schemas.retrieval import RetrievalResult
from schemas.findings import Finding
from prompts.research_findingnode_prompt import FINDING_GENERATOR_PROMPT
import json

class FindingGeneratorNode:
    def __init__(self, client):
        self.client = client

    def run(self, retrieval_result: RetrievalResult) -> Finding:
        evidence = ""
        findings = []
        for chunk in retrieval_result.retrieved_chunks:
            evidence += f"""
                        Source: {chunk.url}

                        Content:
                        {chunk.content}

                        ------------------------
                        """
            print(chunk.url)
            print(chunk.content[:600])
            
        prompt = f"""
        Research Topic:
        {retrieval_result.topic}

        Evidence:
        {evidence}
        """

        prompt = prompt + (FINDING_GENERATOR_PROMPT)

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content":prompt}],
            model = "llama-3.3-70b-versatile",
            temperature = 0.0,
        )

        content = response.choices[0].message.content
        content = content.replace("json", "").replace("```",'').strip()
        data = json.loads(content)
        return Finding.model_validate(data)