from LLM.client_groq import get_client
from agents.manager import Manager
from agents.researcher import Researcher
from tools.web_search import WebSearchTool
from agents.reporter import Reporter
from schemas.state import AgentState
from workflows.orchestrator import Orchestrator

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("SERPER_API_KEY")
web_tool = WebSearchTool(api_key)

client = get_client()

state = AgentState()
manager = Manager(client)
researcher = Researcher(client, web_tool)
reporter = Reporter(client)
orchestrator = Orchestrator(manager, researcher, reporter)

query = "Research about NVIDIA: about LLMs, GPUs, Ai chips"

state = orchestrator.run(query)
print(f"Query : {query}\n")
print(f"Research Topics : {state.plan.research_points}\n")
print(f"Report Summary: {state.report}")