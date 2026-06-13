from dotenv import load_dotenv
import os

from sentence_transformers import SentenceTransformer

from LLM.client_groq import get_client

from agents.manager import Manager
from agents.researcher import Researcher
from agents.reporter import Reporter

from workflows.orchestrator import Orchestrator

from tools.web_search import WebSearchTool
from tools.web_reader import WebReader

from nodes.url_discovery import URLDiscoveryNode
from nodes.page_reader import PageReaderNode
from nodes.chunking import ChunkingNode
from nodes.retriever import RetrieverNode
from nodes.finding_generator import FindingGeneratorNode


load_dotenv()

serper_api_key = os.getenv("SERPER_API_KEY")

# -------------------------Clients / Models-------------------------

groq_client = get_client()

embedding_model = SentenceTransformer("microsoft/harrier-oss-v1-270m")

#------------------------TOOLS------------------------------------

web_search_tool = WebSearchTool(api_key=serper_api_key)

web_reader = WebReader()

# -------------------------Nodes -------------------------

url_discovery = URLDiscoveryNode(search_tool=web_search_tool,top_k = 7)

page_reader = PageReaderNode(reader=web_reader)

chunker = ChunkingNode(chunk_size=500,chunk_overlap=50)

retriever = RetrieverNode(embedding_model=embedding_model,top_k = 3)

finding_generator = FindingGeneratorNode(client=groq_client)

# -------------------------Agents------------------------- 

manager = Manager(client=groq_client)

researcher = Researcher(
    url_discovery=url_discovery,
    page_reader=page_reader,
    chunker=chunker,
    retriever=retriever,
    finding_generator=finding_generator,
)

reporter = Reporter(client=groq_client)

# -------------------------Orchestrator-------------------------

orchestrator = Orchestrator(
    manager=manager,
    researcher=researcher,
    reporter=reporter,
)

# -------------------------Run-------------------------

query = "Research NVIDIA: AI chips only"

state = orchestrator.run(query)
for finding in state.findings:
    print(finding.model_dump_json(indent=4))

print("\n================ QUERY =================\n")
print(state.query)

print("\n=============== REPORT ==================\n")

print(f"\nTitle: {state.report.title}\n")

print("Summary:")
print(state.report.summary)

print("\nSections:")
for section in state.report.sections:
    print(f"\n{'='*60}")
    print(section.topic)
    print(f"{'='*60}")
    print(section.content)
    print(f"Sources :{section.sources}")