from prompts.manager_prompt import MANAGER_PROMPT
from schemas.plan import Plan
import json

class Manager:
    def __init__(self, client):
        # self.researcher = Researcher
        # self.reporter = Reporter
        self.client = client            # no tight coupling wth a single client 

    def run(self, query: str):
        print(f"____Planning..._____")
        response = self.client.chat.completions.create(
            messages=[{"role":"system", "content":MANAGER_PROMPT},
                      {"role": "user", "content": query}],
            model = "llama-3.3-70b-versatile",
            temperature = 0.3,
        )

        content = response.choices[0].message.content
        print("__Planning Done__\n")
        try:
            content = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            plan = Plan.model_validate(data)
            return plan

        except Exception as e:
            print("--------RAW Output:-------")
            print(response)
            raise e
            