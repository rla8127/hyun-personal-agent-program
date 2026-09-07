"""FastAPI 진입점: uvicorn main:app --reload"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import chat, conversations, data

app = FastAPI(
    title="나만의 학습 시간 AI 비서 API",
    description="학습 시간 시계열 데이터를 분석하고, 그 요약을 시스템 프롬프트에 주입해 답변하는 AI 비서.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/", tags=["health"], summary="헬스 체크 / 콜드스타트 워밍업")
def health():
    return {"status": "ok", "docs": "/docs"}
