from schemas.findings import Finding
from schemas.report import Report
from prompts.reporter_prompt import REPORTER_PROMPT
from tools.json_extractor import extract_json
import json

class Reporter:
    def __init__(self, client):
        self.client = client

    def run(self, findings: list[Finding]) -> Report:
        print("___Generating Report...___")
        response = self.client.chat.completions.create(
            messages=[{"role":"system", "content":REPORTER_PROMPT},
                      {"role": "user", "content":json.dumps([f.model_dump() for f in findings], separators=(",", ":"))}],
            model = "meta-llama/llama-4-scout-17b-16e-instruct",
            temperature = 0.0,
        )
        content = response.choices[0].message.content
        # print(f"Report {content = }")
        data = extract_json(content)

        report = Report.model_validate(data)
    
        return report