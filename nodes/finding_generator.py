from schemas.retrieval import RetrievalResult
from schemas.findings import Finding
from prompts.research_findingnode_prompt import FINDING_GENERATOR_PROMPT
from tools.json_extractor import extract_json

class FindingGeneratorNode:
    def __init__(self, client):
        self.client = client

    def run(self, retrieval_result: RetrievalResult) -> Finding:
        evidence = ""
        for chunk in retrieval_result.retrieved_chunks:
            evidence += f"""
                        Source: {chunk.url}

                        Content:
                        {chunk.content}

                        ------------------------
                        """
            

        prompt = f"""
        Research Topic:
        {retrieval_result.topic}

        Evidence:
        {evidence}
        """

        response = self.client.chat.completions.create(
            messages=[
                {"role":"system", "content":FINDING_GENERATOR_PROMPT}
                ,{"role": "user", "content":prompt}],
            model = "openai/gpt-oss-20b",
            temperature = 0.0,
        )

        content = response.choices[0].message.content
        data = extract_json(content)
        return Finding.model_validate(data)