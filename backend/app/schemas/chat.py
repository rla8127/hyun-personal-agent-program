"""대화 기록 / 챗봇 스키마."""
from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = Field(
        default=None, description="이어서 대화할 기존 대화 ID. 없으면 새 대화를 만든다."
    )


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str


class ConversationCreate(BaseModel):
    title: str = Field(default="새 대화", max_length=100)
    messages: list[Message] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    """목록 조회용: messages는 포함하지 않는다."""
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


class ConversationDetail(ConversationSummary):
    """단건 조회용: messages를 포함한다."""
    messages: list[Message]
