import copy
from concurrent.futures import ThreadPoolExecutor

from schemas.corpus import ResearchCorpus
from schemas.findings import Finding
from nodes.hybrid_retriever import HybridRetrieverNode


class Researcher:
    """
    Pipeline per call to run(plan):
      1. Sequential, once: discover URLs for the whole plan, read pages,
         chunk into a base corpus. (Shared web I/O -- no reason to repeat
         it per topic.)
      2. Parallel, once per research point: each topic gets its own
         HybridRetrieverNode seeded from a *copy* of the base corpus, then
         runs a retrieve -> rerank -> generate -> reflect loop (ReAct-style:
         reflect decides whether to stop or issue a real follow-up web
         search and retry).

    Per-topic retrievers are intentionally NOT shared across threads: each
    HybridRetrieverNode.build() mutates its own FAISS/BM25 index, and one
    topic's ReAct follow-up search must not leak extra chunks into another
    topic's corpus. The embedding_model and reranker model are shared
    (inference-only forward passes); this trades a small amount of
    thread-contention overhead for not duplicating model weights per thread.
    """

    def __init__(
        self,
        url_discovery,
        page_reader,
        chunker,
        embedding_model,
        finding_generator,
        reflect_node,
        reranker=None,
        top_k: int = 5,
        pool_size: int = 20,
        rerank_top_n: int = 5,
        max_react_iters: int = 2,
        max_workers: int = 4,
    ):
        self.url_discovery = url_discovery
        self.page_reader = page_reader
        self.chunker = chunker
        self.embedding_model = embedding_model
        self.finding_generator = finding_generator
        self.reflect_node = reflect_node
        self.reranker = reranker

        self.top_k = top_k
        self.pool_size = pool_size
        self.rerank_top_n = rerank_top_n
        self.max_react_iters = max_react_iters
        self.max_workers = max_workers

    def run(self, plan):
        print("____Collecting Resources..._____")
        sources = self.url_discovery.run(plan)
        page_result = self.page_reader.run(sources)
        base_chunks = self.chunker.run(page_result.pages)
        print("_____Base corpus built, researching topics in parallel___\n")

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            findings = list(
                pool.map(
                    lambda topic: self._research_topic(plan.main_topic, topic, base_chunks),
                    plan.research_points,
                )
            )

        print("_____Research Done___\n")
        return findings

    def _research_topic(self, main_topic: str, topic: str, base_chunks: list) -> Finding:
        local_chunks = list(base_chunks)  # per-topic copy; never mutate base_chunks

        hybrid = HybridRetrieverNode(
            embedding_model=self.embedding_model,
            top_k=self.top_k,
            pool_size=self.pool_size,
        )
        hybrid.build(ResearchCorpus(chunks=local_chunks))

        query = f"{main_topic} {topic}"
        finding = None

        for iteration in range(self.max_react_iters):
            retrieval = hybrid.retrieve(query)
            if self.reranker is not None:
                retrieval = self.reranker.rerank(retrieval, top_n=self.rerank_top_n)

            finding = self.finding_generator.run(retrieval)
            finding.topic = topic  # keep the original plan label, not the expanded query

            is_last_iter = iteration == self.max_react_iters - 1
            if is_last_iter:
                break

            reflection = self.reflect_node.run(topic, finding)
            if reflection.sufficient:
                break

            print(f"[ReAct] '{topic}' insufficient ({reflection.reason}); searching again: {reflection.refined_query}")
            follow_up_query = reflection.refined_query or topic
            new_sources = self.url_discovery.run_single(f"{main_topic} {follow_up_query}", top_k=3)
            new_pages = self.page_reader.run(new_sources)
            new_chunks = self.chunker.run(new_pages.pages)

            if not new_chunks:
                break  # nothing new found, stop instead of looping on the same result

            local_chunks = local_chunks + new_chunks
            hybrid.build(ResearchCorpus(chunks=local_chunks))
            query = f"{main_topic} {follow_up_query}"

        return finding
