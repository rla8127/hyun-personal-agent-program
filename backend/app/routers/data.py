"""데이터 CRUD + 요약 엔드포인트."""
from fastapi import APIRouter, HTTPException

from app.schemas.data import DataCreate, DataOut, DataUpdate, SummaryOut
from app.services import analysis_service, data_service

router = APIRouter(prefix="/api/data", tags=["data"])


# 주의: /summary 가 /{item_id} 보다 먼저 선언되어야 경로가 가로채이지 않는다.
@router.get("/summary", response_model=SummaryOut, summary="데이터 요약(프롬프트 주입용)")
def get_summary():
    return analysis_service.build_summary()


@router.post("", response_model=DataOut, status_code=201, summary="새 데이터 추가")
def create(payload: DataCreate):
    return data_service.create_data(payload)


@router.get("", response_model=list[DataOut], summary="데이터 목록 조회")
def list_all():
    return data_service.list_data()


@router.put("/{item_id}", response_model=DataOut, summary="데이터 수정")
def update(item_id: str, payload: DataUpdate):
    result = data_service.update_data(item_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    return result


@router.delete("/{item_id}", summary="데이터 삭제")
def delete(item_id: str):
    if not data_service.delete_data(item_id):
        raise HTTPException(status_code=404, detail="해당 데이터를 찾을 수 없습니다.")
    return {"deleted": item_id}
