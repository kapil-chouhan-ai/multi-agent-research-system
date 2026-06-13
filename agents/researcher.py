from schemas.corpus import ResearchCorpus

class Researcher:
    def __init__(self,url_discovery,page_reader,chunker,retriever, finding_generator):
        self.url_discovery = url_discovery
        self.page_reader = page_reader
        self.chunker = chunker
        self.retriever = retriever
        self.finding_generator = finding_generator

    def run(self, plan):
        print("____Collecting Resources..._____")
        sources = self.url_discovery.run(plan)

        page_result = self.page_reader.run(sources)

        chunks = self.chunker.run(page_result.pages)

        corpus = ResearchCorpus(chunks=chunks)

        self.retriever.build(corpus)
        findings = []

        for topic in plan.research_points:
            retrieval_result = self.retriever.retrieve(topic=f"{plan.main_topic} {topic}")

            finding = self.finding_generator.run(retrieval_result)
            findings.append(finding)

        print("_____Research Done___\n")
        return findings