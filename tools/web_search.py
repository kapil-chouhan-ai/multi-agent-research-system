import requests

class WebSearchTool:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str) -> list[dict]:
        url = "https://google.serper.dev/search"

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {"q": query}

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        data = response.json()
        results = []

        for item in data.get("organic", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", "")
            })

        return results