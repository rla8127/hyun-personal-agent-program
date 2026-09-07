"""data 컬렉션 CRUD + 요약 통계 계산."""
from app.core.firebase import DATA_COLLECTION, get_db
from app.schemas.data import DataCreate, DataUpdate


def create_data(payload: DataCreate) -> dict:
    ref = get_db().collection(DATA_COLLECTION).document()
    ref.set(payload.model_dump())
    return {"id": ref.id, **payload.model_dump()}


def list_data(limit: int = 500) -> list[dict]:
    docs = (
        get_db()
        .collection(DATA_COLLECTION)
        .order_by("date")
        .limit(limit)
        .stream()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


def get_data(doc_id: str) -> dict | None:
    doc = get_db().collection(DATA_COLLECTION).document(doc_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


def update_data(doc_id: str, payload: DataUpdate) -> dict | None:
    ref = get_db().collection(DATA_COLLECTION).document(doc_id)
    if not ref.get().exists:
        return None
    changes = payload.model_dump(exclude_none=True)
    if changes:
        ref.update(changes)
    doc = ref.get()
    return {"id": doc.id, **doc.to_dict()}


def delete_data(doc_id: str) -> bool:
    ref = get_db().collection(DATA_COLLECTION).document(doc_id)
    if not ref.get().exists:
        return False
    ref.delete()
    return True
