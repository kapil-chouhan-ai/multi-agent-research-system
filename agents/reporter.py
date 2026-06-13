from schemas.findings import Finding
from schemas.report import Report
from prompts.reporter_prompt import REPORTER_PROMPT
import json

class Reporter:
    def __init__(self, client):
        self.client = client

    def run(self, findings: list[Finding]) -> Report:
        print("___Generating Report...___")
        response = self.client.chat.completions.create(
            messages=[{"role":"system", "content":REPORTER_PROMPT},
                      {"role": "user", "content": str([f.model_dump() for f in findings])}],
            model = "llama-3.3-70b-versatile",
            temperature = 0.3,
        )
        content = response.choices[0].message.content
        content = content.replace("json", "").replace("```",'').strip()
        data = json.loads(content)

        report = Report.model_validate(data)
        
        return report