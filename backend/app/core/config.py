"""환경 변수 로딩. 키는 절대 코드에 하드코딩하지 않는다."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # 대시보드에 붙여넣을 때 섞이는 공백/줄바꿈/따옴표 제거 (헤더에 들어가면 연결 오류가 난다)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip().strip('"\'')
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    # GPT-5 계열은 추론 토큰도 이 한도에 포함되므로 넉넉히 잡는다.
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

    FIREBASE_SERVICE_ACCOUNT_JSON: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")
    FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH", "./serviceAccountKey.json"
    )

    @property
    def allowed_origins(self) -> list[str]:
        raw = os.getenv("ALLOWED_ORIGINS", "*")
        if raw.strip() == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
