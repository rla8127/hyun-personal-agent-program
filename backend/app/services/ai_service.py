"""OpenAI 호출. 데이터 요약을 시스템 프롬프트에 주입한다(컨텍스트 주입)."""
from openai import OpenAI

from app.core.config import settings

_client: OpenAI | None = None

SYSTEM_PROMPT_TEMPLATE = """당신은 사용자의 학습 시간 기록을 분석해 주는 AI 비서입니다.

[사용자 데이터 요약]
- 데이터 기간: {period}
- 총 레코드: {count}개
- 주요 지표(단위: 분): 총 {total}, 평균 {average}, 최대 {max}, 최소 {min}
- 최근 트렌드: {trend}

위 요약 데이터를 근거로 구체적이고 친근하게 한국어로 답변하세요.
요약에 없는 수치는 지어내지 말고, 모르면 모른다고 답하세요.
답변은 3문장 이내로 간결하게 작성하세요."""


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def build_system_prompt(summary: dict) -> str:
    m = summary["metrics"]
    return SYSTEM_PROMPT_TEMPLATE.format(
        period=summary["period"],
        count=summary["count"],
        total=m["total"],
        average=m["average"],
        max=m["max"],
        min=m["min"],
        trend=summary["trend"],
    )


def ask(summary: dict, history: list[dict], user_message: str) -> str:
    """요약 + 직전 대화 맥락 + 새 질문으로 GPT를 호출한다."""
    messages = [{"role": "system", "content": build_system_prompt(summary)}]
    # 토큰 절약을 위해 최근 10턴만 보낸다.
    for m in history[-10:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_message})

    resp = _get_client().chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        # GPT-5 계열은 max_tokens 대신 max_completion_tokens를 쓰고, temperature 변경을 지원하지 않는다.
        max_completion_tokens=settings.OPENAI_MAX_TOKENS,
    )
    content = resp.choices[0].message.content
    if not content:
        raise RuntimeError("AI가 빈 응답을 반환했습니다. OPENAI_MAX_TOKENS 값을 늘려 보세요.")
    return content.strip()
