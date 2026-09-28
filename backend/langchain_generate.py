from functools import partial
from typing import TypedDict
from langgraph.graph import END, START, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend.observability import get_langfuse_callback, observation


myLLM = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    vertexai=True,
    project="gd-gcp-gridu-genai",
)


class GenState(TypedDict):
    response: str


class GenWorkflow:
    """Run the input through one LLM block per supplied system prompt, in order."""
    def __init__(self, *prompts, name="gen-workflow"):
        if not prompts:
            raise ValueError("GenWorkflow requires at least one system prompt")
        self.name = name
        self.prompts = tuple(p1 for p1, _ in prompts)
        self.tools = tuple(p2 for _, p2 in prompts)
        graph = StateGraph(GenState)
        node_names = [f"block_{index}" for index in range(len(self.prompts))]
        for index, (node_name, system_prompt, tool) in enumerate(zip(node_names, self.prompts, self.tools)):
            graph.add_node(
                node_name,
                partial(self._llm_response, system_prompt=system_prompt, tool=tool),
            )
            graph.add_edge(START if index == 0 else node_names[index - 1], node_name)
        graph.add_edge(node_names[-1], END)
        self.gen_graph_flow = graph.compile()

    @staticmethod
    def _llm_response(state: GenState, system_prompt: str, tool) -> GenState:
        response = myLLM.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=state["response"]),
            ]
        )
        content = response.content
        if isinstance(content, str):
            output = content.strip()
        else:
            output = str(content).strip()
        if tool:
            print(f"Executing {output} in TOOL {tool}")
            tool_name = getattr(tool, "__qualname__", tool.__class__.__name__)
            with observation(
                name=f"tool:{tool_name}",
                as_type="tool",
                input={"input": output},
            ) as tool_observation:
                try:
                    output = tool(output)
                    if tool_observation is not None:
                        tool_observation.update(output={"result": output})
                except Exception as error:
                    if tool_observation is not None:
                        tool_observation.update(level="ERROR", status_message=str(error))
                    raise
        return {"response": output}

    def workflow_response(self, prompt: str) -> str:
        """Pass prompt through all configured blocks and return the final output."""
        callback = get_langfuse_callback()
        config = {"callbacks": [callback]} if callback is not None else None
        with observation(
            name=self.name,
            input={"prompt": prompt},
            metadata={"block_count": len(self.prompts)},
        ) as trace:
            try:
                final_state = self.gen_graph_flow.invoke(
                    {"response": prompt},
                    config=config,
                )
                result = final_state["response"]
                if trace is not None:
                    trace.update(output={"response": result})
                return result
            except Exception as error:
                if trace is not None:
                    trace.update(level="ERROR", status_message=str(error))
                raise
