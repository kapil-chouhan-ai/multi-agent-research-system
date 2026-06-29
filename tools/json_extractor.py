import re
import json

def extract_json(text):
    # remove think blocks
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    )

    text = text.strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        print("No JSON found")
        print(text)
        

    return json.loads(text[start:end+1])