"""Firestore 클라이언트 초기화 (앱 전체에서 1회만)."""
import json

import firebase_admin
from firebase_admin import credentials, firestore

from app.core.config import settings

_db = None


def _build_credentials() -> credentials.Certificate:
    # 배포 환경: JSON 문자열을 환경 변수로 주입
    if settings.FIREBASE_SERVICE_ACCOUNT_JSON.strip():
        info = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
        return credentials.Certificate(info)
    # 로컬 환경: 키 파일 경로
    return credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)


def get_db():
    """Firestore 클라이언트를 반환한다 (lazy singleton)."""
    global _db
    if _db is None:
        if not firebase_admin._apps:
            firebase_admin.initialize_app(_build_credentials())
        _db = firestore.client()
    return _db


DATA_COLLECTION = "data"
CONVERSATIONS_COLLECTION = "conversations"
