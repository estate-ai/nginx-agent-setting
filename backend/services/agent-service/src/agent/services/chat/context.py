from __future__ import annotations

from typing import NotRequired, TypedDict

from agent.schemas.chat import ReasoningEffort
from agent.services.chat.approvals.schemas import InterruptOnConfig


class ChatRuntimeContext(TypedDict):
    """한 번의 run 동안 변하지 않는 실행 설정.

    messages 같은 대화 상태는 ChatState에 둔다.
    model, reasoning_effort, allowed_tools, interrupt_on은 runtime context로 받는다.

    LangGraph 0.6+에서는 config["configurable"] 대신 context_schema + Runtime.context를 쓴다.
    참고:
    https://reference.langchain.com/python/langgraph/graph/state/StateGraph
    https://reference.langchain.com/python/langgraph/runtime/Runtime
    """

    model: str
    reasoning_effort: ReasoningEffort
    allowed_tools: NotRequired[list[str]]
    interrupt_on: NotRequired[InterruptOnConfig]
