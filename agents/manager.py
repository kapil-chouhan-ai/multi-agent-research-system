from prompts.manager_prompt import MANAGER_PROMPT
from schemas.plan import Plan
from tools.json_extractor import extract_json

class Manager:
    def __init__(self, client):
        self.client = client            # no tight coupling wth a single client 

    def run(self, query: str):
        print(f"____Planning..._____")
        response = self.client.chat.completions.create(
            messages=[{"role":"system", "content":MANAGER_PROMPT},
                      {"role": "user", "content": query}],
            model = "openai/gpt-oss-20b",
            temperature = 0.0,
        )

        content = response.choices[0].message.content
        print("__Planning Done__\n")
        try:
            data = extract_json(content)
            plan = Plan.model_validate(data)
            return plan

        except Exception as e:
            print("--------RAW Output:-------")
            print(response)
            raise e
            