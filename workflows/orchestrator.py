from schemas.state import AgentState


class Orchestrator:
    def __init__(self, manager, researcher, reporter, memory=None, human_in_the_loop: bool = False):
        self.manager = manager
        self.researcher = researcher
        self.reporter = reporter
        self.memory = memory
        self.human_in_the_loop = human_in_the_loop

    def run(self, query) -> AgentState:
        if self.memory is not None:
            cached = self.memory.find_similar(query)
            if cached is not None:
                print(f"[memory] Found a similar prior query, reusing report instead of re-researching.\n")
                return cached

        state = AgentState(query=query)

        state.plan = self.manager.run(state.query)

        if self.human_in_the_loop:
            state.plan = self._confirm_plan(state.plan)

        state.findings = self.researcher.run(state.plan)

        state.report = self.reporter.run(state.findings)

        if self.memory is not None:
            self.memory.save(query, state)

        return state

    def _confirm_plan(self, plan):
        print(f"\nProposed research points for '{plan.main_topic}':")
        for i, point in enumerate(plan.research_points, start=1):
            print(f"  {i}. {point}")

        response = input(
            "\nPress Enter to research all of them, or type comma-separated "
            "numbers to keep a subset (e.g. '1,3'): "
        ).strip()

        if response:
            try:
                keep = {int(x.strip()) - 1 for x in response.split(",")}
                plan.research_points = [p for i, p in enumerate(plan.research_points) if i in keep]
            except ValueError:
                print("Could not parse selection -- proceeding with the full plan.")

        return plan
