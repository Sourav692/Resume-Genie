from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq

from agent.state import AgentState
from agent.prompts import ROUTER_PROMPT
from agent.tools import (
    run_cover_letter,
    run_resume_scorer,
    run_resume_checker,
    run_career_coach,
)

# Tools that require a job description
JD_REQUIRED_TOOLS = {"cover_letter", "resume_scorer"}

# Display names for tool outputs
TOOL_LABELS = {
    "resume_checker": "Resume Evaluation",
    "resume_scorer": "ATS Match Analysis",
    "cover_letter": "Cover Letter",
}


def build_graph(llm: ChatGroq):
    """Build and compile the LangGraph StateGraph for the Resume Genie agent."""

    graph = StateGraph(AgentState)

    # ── Router node ───────────────────────────────────
    def router_node(state: AgentState) -> dict:
        """Classify user intent and decide which tool(s) to run."""
        user_msg = state["messages"][-1].content
        resume_text = state.get("resume_text", "")
        job_description = state.get("job_description")

        resume_status = "uploaded" if resume_text else "NOT uploaded"
        jd_status = "provided" if job_description else "NOT provided"

        decision = llm.invoke(
            ROUTER_PROMPT.format(
                resume_status=resume_status,
                jd_status=jd_status,
                user_message=user_msg,
            )
        ).content.strip().lower()

        if decision.startswith("multi|"):
            tools = [t.strip() for t in decision.split("|")[1].split(",")]
            # Filter out JD-required tools if no JD provided
            if not job_description:
                tools = [t for t in tools if t not in JD_REQUIRED_TOOLS]
            return {"tool_choice": "multi", "tool_chain": tools, "tool_outputs": {}}

        if decision == "need_jd":
            return {
                "tool_choice": "none",
                "messages": [
                    AIMessage(
                        content="I need a job description to do that. "
                        "Please paste one in the sidebar or include it in your message."
                    )
                ],
            }

        return {"tool_choice": decision, "tool_chain": None, "tool_outputs": {}}

    # ── Tool nodes ────────────────────────────────────
    def cover_letter_node(state: AgentState) -> dict:
        result = run_cover_letter(
            llm, state["resume_text"], state["job_description"]
        )
        outputs = dict(state.get("tool_outputs") or {})
        outputs["cover_letter"] = result
        return {"tool_outputs": outputs}

    def resume_scorer_node(state: AgentState) -> dict:
        result = run_resume_scorer(
            llm, state["resume_text"], state["job_description"]
        )
        outputs = dict(state.get("tool_outputs") or {})
        outputs["resume_scorer"] = result
        return {"tool_outputs": outputs}

    def resume_checker_node(state: AgentState) -> dict:
        result = run_resume_checker(llm, state["resume_text"])
        outputs = dict(state.get("tool_outputs") or {})
        outputs["resume_checker"] = result
        return {"tool_outputs": outputs}

    def career_coach_node(state: AgentState) -> dict:
        result = run_career_coach(llm, state["resume_text"], state["messages"])
        return {"messages": [AIMessage(content=result)]}

    # ── Responder node ────────────────────────────────
    def responder_node(state: AgentState) -> dict:
        """Synthesize tool outputs into a final AI message."""
        outputs = state.get("tool_outputs") or {}
        if not outputs:
            return {}

        # Single tool — return its output directly
        if len(outputs) == 1:
            result = next(iter(outputs.values()))
            return {"messages": [AIMessage(content=result)]}

        # Multiple tools — combine with section headers
        sections = []
        for tool_name, result in outputs.items():
            label = TOOL_LABELS.get(tool_name, tool_name)
            sections.append(f"## {label}\n\n{result}")

        combined = "\n\n---\n\n".join(sections)
        return {"messages": [AIMessage(content=combined)]}

    # ── Conditional routing ───────────────────────────
    def route_after_router(state: AgentState) -> str:
        choice = state.get("tool_choice", "none")
        if choice == "multi":
            chain = state.get("tool_chain", [])
            return chain[0] if chain else "career_coach"
        if choice in ("cover_letter", "resume_scorer", "resume_checker", "career_coach"):
            return choice
        return "__end__"

    def route_after_tool(state: AgentState) -> str:
        """After a tool, chain to the next tool or go to responder."""
        if state.get("tool_choice") != "multi":
            return "responder"

        chain = state.get("tool_chain", [])
        executed = set((state.get("tool_outputs") or {}).keys())

        for tool_name in chain:
            if tool_name not in executed:
                return tool_name

        return "responder"

    # ── Wire the graph ────────────────────────────────
    graph.add_node("router", router_node)
    graph.add_node("cover_letter", cover_letter_node)
    graph.add_node("resume_scorer", resume_scorer_node)
    graph.add_node("resume_checker", resume_checker_node)
    graph.add_node("career_coach", career_coach_node)
    graph.add_node("responder", responder_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {
            "cover_letter": "cover_letter",
            "resume_scorer": "resume_scorer",
            "resume_checker": "resume_checker",
            "career_coach": "career_coach",
            "__end__": END,
        },
    )

    # Each tool node routes to next-in-chain or responder
    for tool_node in ["cover_letter", "resume_scorer", "resume_checker"]:
        graph.add_conditional_edges(
            tool_node,
            route_after_tool,
            {
                "cover_letter": "cover_letter",
                "resume_scorer": "resume_scorer",
                "resume_checker": "resume_checker",
                "responder": "responder",
            },
        )

    # Career coach goes directly to END (adds its own message)
    graph.add_edge("career_coach", END)

    # Responder always ends
    graph.add_edge("responder", END)

    return graph.compile()
