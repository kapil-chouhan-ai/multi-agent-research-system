from schemas.state import AgentState

class Orchestrator:
    def __init__(self, manager, researcher, reporter):
        self.manager = manager
        self.researcher = researcher
        self.reporter = reporter
    
    def run(self, query) -> AgentState:
        state = AgentState(query = query)
        # print(state.query)

        state.plan = self.manager.run(state.query)
        # print(f"\n{state.plan = }\n")

        state.findings = self.researcher.run(state.plan)
        # print(f"{state.findings = }\n")

        state.report = self.reporter.run(state.findings)
        # print(f"{state.report = }\n")

        return state