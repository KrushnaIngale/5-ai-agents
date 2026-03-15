from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from multi_agent_chatbot.config import Settings
from multi_agent_chatbot.providers import ProviderClients


@dataclass
class AgentResult:
    name: str
    role: str
    provider: str
    output: str


def _prompt_analyzer(clients: ProviderClients, user_prompt: str) -> AgentResult:
    provider, output = clients.generate(
        "Analyze this user request and explain what is needed.\n"
        f"User request:\n{user_prompt}",
        preferred_providers=("gemini", "groq"),
    )
    return AgentResult("Agent 1", "Prompt Analyzer", provider, output)


def _research_agent(clients: ProviderClients, analyzer_output: str) -> AgentResult:
    provider, output = clients.generate(
        "Provide useful knowledge, relevant concepts, tools, and implementation guidance for this task.\n"
        f"Input:\n{analyzer_output}",
        preferred_providers=("gemini", "groq"),
    )
    return AgentResult("Agent 2", "Research Agent", provider, output)


def _reasoning_agent(clients: ProviderClients, research_output: str) -> AgentResult:
    provider, output = clients.generate(
        "Think logically about this task, identify the best structure, and improve the solution plan.\n"
        f"Input:\n{research_output}",
        preferred_providers=("groq", "gemini"),
    )
    return AgentResult("Agent 3", "Logic / Reasoning Agent", provider, output)


def _content_generator(clients: ProviderClients, reasoning_output: str) -> AgentResult:
    provider, output = clients.generate(
        "Write a detailed answer or solution draft based on this reasoning.\n"
        f"Input:\n{reasoning_output}",
        preferred_providers=("gemini", "groq"),
    )
    return AgentResult("Agent 4", "Content Generator", provider, output)


def _output_formatter(clients: ProviderClients, content_output: str) -> AgentResult:
    provider, output = clients.generate(
        "Format the following into a clean, polished final answer with sections when helpful.\n"
        f"Input:\n{content_output}",
        preferred_providers=("groq", "gemini"),
    )
    return AgentResult("Agent 5", "Output Formatter", provider, output)


def run_pipeline(user_prompt: str, settings: Settings) -> dict:
    clients = ProviderClients(settings)

    analyzer = _prompt_analyzer(clients, user_prompt)
    researcher = _research_agent(clients, analyzer.output)
    reasoner = _reasoning_agent(clients, researcher.output)
    generator = _content_generator(clients, reasoner.output)
    formatter = _output_formatter(clients, generator.output)

    agents = [analyzer, researcher, reasoner, generator, formatter]

    return {
        "final_answer": formatter.output,
        "agents": agents,
        "mock_mode": settings.mock_mode,
    }


def build_langgraph_app(settings: Settings):
    try:
        from langgraph.graph import END, StateGraph
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("LangGraph is not installed. Install requirements first.") from exc

    clients = ProviderClients(settings)

    class PipelineState(TypedDict, total=False):
        text: str
        agent_1: AgentResult
        agent_2: AgentResult
        agent_3: AgentResult
        agent_4: AgentResult
        agent_5: AgentResult

    def current_text(state: PipelineState) -> str:
        value = state.get("text", "")
        if not isinstance(value, str):
            raise RuntimeError("LangGraph state is missing the expected 'text' string.")
        return value

    def analyze_node(state: PipelineState):
        result = _prompt_analyzer(clients, current_text(state))
        return {"text": result.output, "agent_1": result}

    def research_node(state: PipelineState):
        result = _research_agent(clients, current_text(state))
        return {"text": result.output, "agent_2": result}

    def reasoning_node(state: PipelineState):
        result = _reasoning_agent(clients, current_text(state))
        return {"text": result.output, "agent_3": result}

    def generate_node(state: PipelineState):
        result = _content_generator(clients, current_text(state))
        return {"text": result.output, "agent_4": result}

    def format_node(state: PipelineState):
        result = _output_formatter(clients, current_text(state))
        return {"text": result.output, "agent_5": result}

    builder = StateGraph(PipelineState)
    builder.add_node("analyze", analyze_node)
    builder.add_node("research", research_node)
    builder.add_node("reason", reasoning_node)
    builder.add_node("generate", generate_node)
    builder.add_node("format", format_node)
    builder.set_entry_point("analyze")
    builder.add_edge("analyze", "research")
    builder.add_edge("research", "reason")
    builder.add_edge("reason", "generate")
    builder.add_edge("generate", "format")
    builder.add_edge("format", END)
    return builder.compile()
