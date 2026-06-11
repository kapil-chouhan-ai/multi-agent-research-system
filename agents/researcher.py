from tools.web_search import WebSearchTool

from prompts.researcher_prompt import RESEARCHER_PROMPT
from schemas.findings import Finding
from schemas.plan import Plan
import json

class Researcher:
    def __init__(self, client, web_tool):
        self.client = client
        self.web_tool = web_tool

    def run(self, plan : Plan) -> list[Finding]:
        findings = []
        for point in plan.research_points:
            search_result = self.web_tool.search(f"{point} related to {plan.user_query}")
            response = self.client.chat.completions.create(
                messages=[{"role":"system", "content":RESEARCHER_PROMPT},
                        {
                            "role": "user", 
                            "content":f"Research Topic : {point}\nSearch Result:{search_result}"
                        }],
                model = "llama-3.3-70b-versatile",
                temperature = 0.3,
            )

            content = response.choices[0].message.content
            content = content.replace("json", "").replace("```",'').strip()
            data = json.loads(content)
            data = Finding.model_validate(data)
            findings.append(data)
        
        return findings