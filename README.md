# 📚 학습 시간 AI 비서

내 학습 시간 기록(시계열 데이터)을 분석해, 그 **요약 정보를 시스템 프롬프트에 주입**하여
"내 상황을 아는" 답변을 해 주는 AI 비서 웹 서비스입니다.

일반 ChatGPT는 "이번 주 공부 시간 어때?"에 일반론만 답하지만,
이 서비스는 Firestore에 쌓인 내 실제 기록의 기간·개수·평균·최대/최소·추세를 근거로 답합니다.

## 기술 스택

| 영역 | 사용 기술 |
|------|-----------|
| 백엔드 | Python 3.12, FastAPI, Uvicorn, Pydantic v2 |
| DB | Firebase Firestore (firebase-admin) |
| AI | OpenAI Chat Completions API |
| 프론트엔드 | HTML / CSS / Vanilla JavaScript (프레임워크 미사용) |
| 배포 | 백엔드 Render, 프론트엔드 Vercel |

## 배포 URL

| 구분 | URL |
|------|-----|
| 프론트엔드 | (배포 후 기입) |
| 백엔드 API | (배포 후 기입) |
| Swagger UI | (백엔드 URL)/docs |

> Render 무료 티어는 일정 시간 요청이 없으면 슬립 상태가 됩니다.
> 첫 요청은 최대 1분가량 걸릴 수 있으며, 프론트엔드 화면 상단에 안내 문구가 표시됩니다.

## 프로젝트 구조

```
.
├── backend/
│   ├── main.py                       # FastAPI 진입점, CORS 설정
│   ├── requirements.txt
│   ├── render.yaml                   # Render 배포 설정
│   ├── .env.example
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py             # 환경 변수 로딩
│   │   │   └── firebase.py           # Firestore 클라이언트 초기화
│   │   ├── schemas/                  # Pydantic 요청/응답 모델
│   │   │   ├── data.py
│   │   │   └── chat.py
│   │   ├── services/                 # 비즈니스 로직
│   │   │   ├── data_service.py       # data 컬렉션 CRUD
│   │   │   ├── analysis_service.py   # 시계열 분석 → 요약 생성
│   │   │   ├── conversation_service.py
│   │   │   └── ai_service.py         # 컨텍스트 주입 + GPT 호출
│   │   └── routers/                  # HTTP 엔드포인트
│   │       ├── data.py
│   │       ├── conversations.py
│   │       └── chat.py
│   └── scripts/seed_data.py          # 더미 학습 기록 120건 생성
└── frontend/
    ├── index.html
    ├── vercel.json
    ├── css/style.css
    ├── js/{config.js, api.js, app.js}
    └── scripts/build-config.js       # 빌드 시 API_BASE_URL 주입
```

**계층 분리 기준**: `routers`는 HTTP 요청/응답과 상태 코드만 담당하고,
`services`는 Firestore·OpenAI 접근과 계산 로직을 담당합니다.
`schemas`의 Pydantic 모델이 두 계층 사이의 계약이 되어, 잘못된 입력은 라우터에 닿기 전에 422로 걸러집니다.

## Firestore 컬렉션 구조

```
data/{auto_id}
  ├─ date  : string  "YYYY-MM-DD"
  ├─ value : number  학습 시간(분), 0~1440
  └─ memo  : string  과목/메모

conversations/{auto_id}
  ├─ title      : string
  ├─ messages   : array<{ role: "user"|"assistant", content: string }>
  ├─ created_at : string (ISO8601)
  └─ updated_at : string (ISO8601)
```

## API 명세

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/data` | 새 데이터 추가 |
| GET | `/api/data` | 데이터 목록 조회 |
| PUT | `/api/data/{id}` | 데이터 수정 (부분 업데이트) |
| DELETE | `/api/data/{id}` | 데이터 삭제 |
| GET | `/api/data/summary` | 데이터 요약 (프롬프트 주입용) |
| POST | `/api/conversations` | 대화 저장 |
| GET | `/api/conversations` | 대화 목록 조회 (**messages 미포함**) |
| GET | `/api/conversations/{id}` | 특정 대화 불러오기 (**messages 포함**) |
| DELETE | `/api/conversations/{id}` | 대화 삭제 |
| POST | `/api/chat` | AI 대화 (요약 주입 + 자동 저장) |

목록 조회는 응답 크기를 줄이기 위해 `messages`를 제외하고 `message_count`만 내려주며,
"대화 불러오기"는 `GET /api/conversations/{id}`로 전체 메시지를 가져옵니다. (요구사항 6-A 방식)

### `GET /api/data/summary` 응답 예시

```json
{
  "period": "2025-05-11 ~ 2025-09-07",
  "count": 120,
  "metrics": { "total": 12480.0, "average": 104.0, "max": 178.0, "min": 31.0 },
  "trend": "상승 (최근 평균 +38.2%)"
}
```

### 컨텍스트 주입 흐름 (`POST /api/chat`)

1. `analysis_service.build_summary()`로 데이터 요약 계산
2. 요약을 시스템 프롬프트 템플릿에 삽입
3. 시스템 프롬프트 + 최근 10턴 대화 + 새 질문으로 GPT 호출
4. 질문/답변을 `conversations`에 자동 저장 (기존 대화면 이어붙임, 없으면 새로 생성)

## 로컬 실행 방법

### 1. 백엔드

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # .env 를 열어 실제 값 입력
# Firebase 콘솔 > 프로젝트 설정 > 서비스 계정 > 새 비공개 키 생성
# 내려받은 JSON 을 backend/serviceAccountKey.json 로 저장

python scripts/seed_data.py        # (선택) 더미 학습 기록 120건 생성
uvicorn main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

### 2. 프론트엔드

`file://` 로 열면 CORS에 걸리므로 정적 서버로 실행합니다.

```bash
cd frontend
python3 -m http.server 5500
```

http://127.0.0.1:5500 접속. 백엔드 주소는 `js/config.js`의 기본값을 사용합니다.

## 환경 변수

### 백엔드 (Render)

| 변수 | 필수 | 설명 |
|------|------|------|
| `OPENAI_API_KEY` | ✅ | OpenAI API 키 |
| `OPENAI_MODEL` | | 사용 모델 (기본 `gpt-5.6-luna`) |
| `OPENAI_MAX_TOKENS` | | 응답 최대 토큰 (기본 `500`) |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | ✅(배포) | 서비스 계정 키 JSON 전체를 한 줄 문자열로 |
| `FIREBASE_SERVICE_ACCOUNT_PATH` | ✅(로컬) | 서비스 계정 키 파일 경로 |
| `ALLOWED_ORIGINS` | ✅ | CORS 허용 도메인, 쉼표 구분 (예: Vercel 배포 URL) |

### 프론트엔드 (Vercel)

| 변수 | 필수 | 설명 |
|------|------|------|
| `API_BASE_URL` | ✅ | 백엔드 Render URL (끝에 `/` 없이) |

> 키는 모두 환경 변수로만 관리하며, `.env`와 `serviceAccountKey.json`은 `.gitignore`로 커밋에서 제외됩니다.

## 배포

### 백엔드 (Render)

1. GitHub에 푸시 후 Render → New → Web Service → 저장소 연결
2. Root Directory `backend`, Build `pip install -r requirements.txt`,
   Start `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Environment에 위 백엔드 환경 변수 등록
   (`FIREBASE_SERVICE_ACCOUNT_JSON`은 키 JSON 파일 내용을 통째로 붙여넣기)
4. 배포 후 `https://<서비스명>.onrender.com/docs` 접속 확인

### 프론트엔드 (Vercel)

1. Vercel → New Project → 같은 저장소 연결, Root Directory `frontend`
2. Environment Variables에 `API_BASE_URL` = Render 백엔드 URL 등록
3. 배포 후 Render의 `ALLOWED_ORIGINS`에 Vercel 도메인을 추가하고 재배포

## 제출 스크린샷

| 화면 | 이미지 |
|------|--------|
| 데이터 요약이 보이는 채팅 화면 (질문+답변) | `docs/screenshot-chat.png` |
| 데이터 관리 화면 (CRUD 동작) | `docs/screenshot-data.png` |
| 대화 기록 화면 (불러오기 동작) | `docs/screenshot-conversations.png` |
