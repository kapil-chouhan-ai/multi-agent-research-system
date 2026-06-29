from schemas.source import Source
from schemas.plan import Plan

class URLDiscoveryNode:
    def __init__(self, search_tool, top_k: int = 5):
        self.search_tool = search_tool
        self.top_k = top_k

    def run(self, plan: Plan) -> list[Source]:
        discovered_url = set()
        i = 1
        for point in plan.research_points:
            print(f"url_{i}")
            search_result = self.search_tool.search(f"{point}")

            for result in search_result[:self.top_k]:
                discovered_url.add(result['url'])
                
        print(f"{len(discovered_url) = }\n")
        return [
            Source(url = url) for url in discovered_url
        ]
    
    def run_single(self, query: str, top_k: int | None = None) -> list[Source]:
        """Ad-hoc single-query search, used by the ReAct loop to do a real
        follow-up web search on a refined_query rather than re-querying the
        same fixed corpus.
        """
        k = top_k or self.top_k
        search_result = self.search_tool.search(query)
        return [Source(url=r['url']) for r in search_result[:k]]