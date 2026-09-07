"""더미 학습 기록 120건을 Firestore에 넣는다.

사용법:  cd backend && python scripts/seed_data.py
"""
import os
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.firebase import DATA_COLLECTION, get_db  # noqa: E402

SUBJECTS = ["파이썬", "알고리즘", "영어", "데이터베이스", "웹개발", "머신러닝"]
DAYS = 120


def main() -> None:
    db = get_db()
    start = date.today() - timedelta(days=DAYS - 1)
    random.seed(42)

    batch = db.batch()
    for i in range(DAYS):
        d = start + timedelta(days=i)
        # 뒤로 갈수록 조금씩 늘어나는 상승 추세를 만든다.
        base = 60 + i * 0.7
        value = max(0, round(random.gauss(base, 25)))
        doc = db.collection(DATA_COLLECTION).document()
        batch.set(doc, {
            "date": d.isoformat(),
            "value": float(value),
            "memo": random.choice(SUBJECTS),
        })
        # Firestore 배치는 최대 500건
        if (i + 1) % 400 == 0:
            batch.commit()
            batch = db.batch()
    batch.commit()
    print(f"{DAYS}건의 학습 기록을 추가했습니다.")


if __name__ == "__main__":
    main()
