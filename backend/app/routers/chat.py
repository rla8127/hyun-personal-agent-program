"""AI 챗봇 엔드포인트 (컨텍스트 주입 + 대화 자동 저장)."""
import logging

import openai
from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services import ai_service, analysis_service, conversation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, summary="AI 대화 (데이터 요약을 시스템 프롬프트에 주입)")
def chat(payload: ChatRequest):
    # 1) 데이터 요약 조회
    summary = analysis_service.build_summary()

    # 2) 이어하기라면 기존 대화 맥락을 불러온다
    history: list[dict] = []
    conversation = None
    if payload.conversation_id:
        conversation = conversation_service.get_conversation(payload.conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="해당 대화를 찾을 수 없습니다.")
        history = conversation["messages"]

    # 3) 요약을 시스템 프롬프트에 넣어 GPT 호출
    try:
        reply = ai_service.ask(summary, history, payload.message)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except openai.APIStatusError as e:
        # 401(키 오류), 429(쿼터/크레딧 부족), 404(모델 권한 없음) 등 OpenAI가 돌려준 에러
        logger.exception("OpenAI API 오류")
        raise HTTPException(status_code=502, detail=f"OpenAI 오류 ({e.status_code}): {e.message}")
    except Exception as e:
        logger.exception("AI 응답 생성 실패")
        raise HTTPException(status_code=502, detail=f"AI 응답 생성에 실패했습니다: {type(e).__name__}: {e}")

    # 4) 대화 자동 저장
    new_messages = [
        {"role": "user", "content": payload.message},
        {"role": "assistant", "content": reply},
    ]
    if conversation is None:
        title = payload.message[:30]
        created = conversation_service.create_conversation(title, new_messages)
        conversation_id = created["id"]
    else:
        conversation_service.append_messages(payload.conversation_id, new_messages)
        conversation_id = payload.conversation_id

    return {"conversation_id": conversation_id, "reply": reply}
