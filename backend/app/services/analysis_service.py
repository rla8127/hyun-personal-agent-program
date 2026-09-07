"""시계열 데이터 분석: 프롬프트 주입용 요약 정보를 만든다."""
from app.services.data_service import list_data

_EMPTY = {
    "period": "-",
    "count": 0,
    "metrics": {"total": 0, "average": 0, "max": 0, "min": 0},
    "trend": "데이터 없음",
}


def _trend(values: list[float]) -> str:
    """최근 구간과 이전 구간의 평균을 비교해 추세를 판정한다."""
    if len(values) < 4:
        return "판단하기에 데이터가 부족함"
    half = len(values) // 2
    prev_avg = sum(values[:half]) / half
    recent_avg = sum(values[half:]) / (len(values) - half)
    if prev_avg == 0:
        return "상승" if recent_avg > 0 else "유지"
    change = (recent_avg - prev_avg) / prev_avg * 100
    if change > 5:
        return f"상승 (최근 평균 +{change:.1f}%)"
    if change < -5:
        return f"감소 (최근 평균 {change:.1f}%)"
    return f"유지 (변동 {change:+.1f}%)"


def build_summary() -> dict:
    """요약 정보를 계산한다. 데이터가 없으면 빈 요약을 반환한다."""
    rows = list_data()
    if not rows:
        return _EMPTY

    rows.sort(key=lambda r: r.get("date", ""))
    values = [float(r.get("value", 0)) for r in rows]

    return {
        "period": f"{rows[0]['date']} ~ {rows[-1]['date']}",
        "count": len(rows),
        "metrics": {
            "total": round(sum(values), 2),
            "average": round(sum(values) / len(values), 2),
            "max": max(values),
            "min": min(values),
        },
        "trend": _trend(values),
    }
