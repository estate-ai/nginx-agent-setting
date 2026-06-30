from typing import Any

from agent.core.config import settings
from agent.schemas.chat import ReasoningEffort
from agent.services.chat.model_cards import ChatModelRoute
from agent.services.chat.providers.normalized import ChatOpenRouter


def create_cerebras_chat_model(
    *, route: ChatModelRoute, reasoning_effort: ReasoningEffort
) -> Any:
    kwargs: dict[str, Any] = {
        "model": route.langchain_model,
        "api_key": settings.cerebras_api_key,
        "base_url": settings.cerebras_base_url,
        "streaming": True,
        "use_responses_api": False,
    }
    if reasoning_effort != "none":
        kwargs["reasoning_effort"] = reasoning_effort

    return ChatOpenRouter(**kwargs)
