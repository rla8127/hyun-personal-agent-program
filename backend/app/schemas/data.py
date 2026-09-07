"""데이터(학습 시간 기록) 요청/응답 스키마."""
from datetime import date as date_type

from pydantic import BaseModel, Field, field_validator


class DataCreate(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD 형식의 날짜")
    value: float = Field(..., ge=0, le=1440, description="학습 시간(분), 0~1440")
    memo: str = Field(default="", max_length=200, description="과목/메모")

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            date_type.fromisoformat(v)
        except ValueError:
            raise ValueError("date는 YYYY-MM-DD 형식이어야 합니다.")
        return v


class DataUpdate(BaseModel):
    """수정은 부분 업데이트를 허용한다."""
    date: str | None = None
    value: float | None = Field(default=None, ge=0, le=1440)
    memo: str | None = Field(default=None, max_length=200)

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            date_type.fromisoformat(v)
        except ValueError:
            raise ValueError("date는 YYYY-MM-DD 형식이어야 합니다.")
        return v


class DataOut(DataCreate):
    id: str


class SummaryMetrics(BaseModel):
    total: float
    average: float
    max: float
    min: float


class SummaryOut(BaseModel):
    period: str
    count: int
    metrics: SummaryMetrics
    trend: str
