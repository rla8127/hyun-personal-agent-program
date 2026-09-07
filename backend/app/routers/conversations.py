"""대화 기록 엔드포인트."""
from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    ConversationCreate,
    ConversationDetail,
    ConversationSummary,
)
from app.services import conversation_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationDetail, status_code=201, summary="대화 저장")
def create(payload: ConversationCreate):
    messages = [m.model_dump() for m in payload.messages]
    created = conversation_service.create_conversation(payload.title, messages)
    return conversation_service.get_conversation(created["id"])


@router.get("", response_model=list[ConversationSummary], summary="대화 목록 조회(messages 미포함)")
def list_all():
    return conversation_service.list_conversations()


@router.get("/{conv_id}", response_model=ConversationDetail, summary="특정 대화 불러오기(messages 포함)")
def get_one(conv_id: str):
    result = conversation_service.get_conversation(conv_id)
    if result is None:
        raise HTTPException(status_code=404, detail="해당 대화를 찾을 수 없습니다.")
    return result


@router.delete("/{conv_id}", summary="대화 삭제")
def delete(conv_id: str):
    if not conversation_service.delete_conversation(conv_id):
        raise HTTPException(status_code=404, detail="해당 대화를 찾을 수 없습니다.")
    return {"deleted": conv_id}
