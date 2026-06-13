from schemas.source import Source
from schemas.plan import Plan

class URLDiscoveryNode:
    def __init__(self, search_tool, top_k: int = 3):
        self.search_tool = search_tool
        self.top_k = top_k

    def run(self, plan: Plan) -> list[Source]:
        discovered_url = set()
        for point in plan.research_points:
            search_result = self.search_tool.search(f"{plan.main_topic} {point}")

            for result in search_result[:self.top_k]:
                discovered_url.add(result['url'])
        return [
            Source(url = url) for url in discovered_url
        ]