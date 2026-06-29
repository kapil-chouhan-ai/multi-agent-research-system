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
from nodes.reranker import RerankerNode
from nodes.reflect import ReflectNode
from nodes.finding_generator import FindingGeneratorNode

from memory.store import ResearchMemoryStore


load_dotenv()

serper_api_key = os.getenv("SERPER_API_KEY")
use_mcp_search = os.getenv("USE_MCP_SEARCH", "false").lower() == "true"
enable_hitl = os.getenv("ENABLE_HITL", "true").lower() == "true"

# -------------------------Clients / Models-------------------------

groq_client = get_client()

# NOTE: was "microsoft/harrier-oss-v1-270m" -- not a real HuggingFace model id
# (same "unrecognized embedding model name" bug pattern seen before in the
# RAG-from-scratch project). Swapped to a real, well-established small
# retrieval embedding model.
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

#------------------------TOOLS------------------------------------

if use_mcp_search:
    from mcp_tools.search_client import MCPWebSearchTool
    web_search_tool = MCPWebSearchTool()
else:
    web_search_tool = WebSearchTool(api_key=serper_api_key)

web_reader = WebReader()

# -------------------------Nodes -------------------------

url_discovery = URLDiscoveryNode(search_tool=web_search_tool, top_k=7)

page_reader = PageReaderNode(reader=web_reader)

chunker = ChunkingNode(chunk_size=500, chunk_overlap=50)

reranker = RerankerNode(top_n=5)

reflect_node = ReflectNode(client=groq_client)

finding_generator = FindingGeneratorNode(client=groq_client)

# -------------------------Agents-------------------------

manager = Manager(client=groq_client)

researcher = Researcher(
    url_discovery=url_discovery,
    page_reader=page_reader,
    chunker=chunker,
    embedding_model=embedding_model,
    finding_generator=finding_generator,
    reflect_node=reflect_node,
    reranker=reranker,
    top_k=5,
    pool_size=20,
    rerank_top_n=5,
    max_react_iters=2,
    max_workers=4,
)

reporter = Reporter(client=groq_client)

memory = ResearchMemoryStore(embedding_model=embedding_model)

# -------------------------Orchestrator-------------------------

orchestrator = Orchestrator(
    manager=manager,
    researcher=researcher,
    reporter=reporter,
    memory=memory,
    human_in_the_loop=enable_hitl,
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
