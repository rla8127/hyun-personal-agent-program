"""conversations 컬렉션 CRUD."""
from datetime import datetime, timezone

from app.core.firebase import CONVERSATIONS_COLLECTION, get_db


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _summary(doc_id: str, data: dict) -> dict:
    messages = data.get("messages", [])
    return {
        "id": doc_id,
        "title": data.get("title", "새 대화"),
        "created_at": data.get("created_at", ""),
        "updated_at": data.get("updated_at", ""),
        "message_count": len(messages),
    }


def create_conversation(title: str, messages: list[dict]) -> dict:
    now = _now()
    body = {
        "title": title or "새 대화",
        "messages": messages,
        "created_at": now,
        "updated_at": now,
    }
    ref = get_db().collection(CONVERSATIONS_COLLECTION).document()
    ref.set(body)
    return {"id": ref.id, **body}


def list_conversations(limit: int = 50) -> list[dict]:
    """목록 조회. messages는 제외하고 요약 정보만 반환한다."""
    docs = (
        get_db()
        .collection(CONVERSATIONS_COLLECTION)
        .order_by("updated_at", direction="DESCENDING")
        .limit(limit)
        .stream()
    )
    return [_summary(d.id, d.to_dict()) for d in docs]


def get_conversation(doc_id: str) -> dict | None:
    """단건 조회. messages를 포함한다."""
    doc = get_db().collection(CONVERSATIONS_COLLECTION).document(doc_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    return {**_summary(doc.id, data), "messages": data.get("messages", [])}


def append_messages(doc_id: str, new_messages: list[dict]) -> dict | None:
    """기존 대화에 메시지를 이어 붙인다."""
    ref = get_db().collection(CONVERSATIONS_COLLECTION).document(doc_id)
    doc = ref.get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    messages = data.get("messages", []) + new_messages
    ref.update({"messages": messages, "updated_at": _now()})
    return {"id": doc_id, **data, "messages": messages}


def delete_conversation(doc_id: str) -> bool:
    ref = get_db().collection(CONVERSATIONS_COLLECTION).document(doc_id)
    if not ref.get().exists:
        return False
    ref.delete()
    return True
