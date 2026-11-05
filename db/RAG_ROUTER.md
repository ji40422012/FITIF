# backend 변경 안내(B파트) — Medical RAG API

## 신규 파일
- `backend/rag_router.py`: `POST /api/rag/search`를 정의한 FastAPI `APIRouter`.
- 기존 `backend/database.py`, CGM 조회 로직, `GET /health` 등은 수정하지 않습니다.

## 팀원이 적용할 변경 사항 (`backend/main.py`)
`FastAPI` 인스턴스 생성 전에 import 추가:

```python
from .rag_router import router as rag_router
```

`app = FastAPI(...)` 선언 직후에 라우터 등록:

```python
app.include_router(rag_router)
```

이 두 줄은 기존 코드를 교체하지 않고 **추가**합니다. FastAPI 서버 실행은 기존 방법(예: 프로젝트 루트에서 `uvicorn backend.main:app --reload`)을 따릅니다.

## API 요청 예시

```http
POST /api/rag/search
Content-Type: application/json

{"query":"제2형 당뇨병 환자의 저혈당 대처 방법은?", "top_k":5}
```

정상 연결 시 응답 형식:

```json
{
  "query": "제2형 당뇨병 환자의 저혈당 대처 방법은?",
  "count": 1,
  "results": [{
    "chunk_id": "example_only",
    "text": "검색으로 반환할 원문 (예시; 실제 진료지침 인용 아님)",
    "pdf_page": 1,
    "document_title": "2025 당뇨병 진료지침 제9판",
    "publisher": "대한당뇨병학회",
    "score": 0.78,
    "requires_review": false,
    "review_flags": []
  }],
  "notice": "검색 결과는 의료지침의 근거 후보입니다. PDF 원문 및 임상적 타당성 검토가 필요합니다."
}
```

> 위 JSON은 응답 형식 예시일 뿐 실제 검색·검증 결과가 아닙니다.

## 현재 단계와 제한
- **구현 완료:** FastAPI 요청 형식 검증, 응답 모델, 라우팅, DB 오류 시 정보 비노출 처리.
- **미구현:** `medical_rag/search.py` 및 `search_guidelines(query, top_k)` 함수, RAG DB 스키마 적용, 벡터 994건 적재.
- 검색 모듈이 아직 없으면 서버 실행은 가능하고 `/api/rag/search`는 **HTTP 503**을 반환합니다. 완료된 검색 기능으로 표시하지 마세요.
- 잘못된 `top_k`, 빈 질문은 HTTP 422입니다.
- `backend/database.py`의 읽기 전용 `get_connection()`은 검색(SELECT)에만 사용합니다. 벡터 INSERT에는 별도 쓰기 계정을 사용합니다.
- 서버에 사용자 인증이 없으므로 외부 네트워크에 공개하지 않습니다.
- Pydantic v2 사용을 전제로 합니다(FastAPI의 설치 버전 확인 필요).

## 완료 점검
1. `python -m compileall backend/rag_router.py`
2. `backend/main.py`에 두 줄 추가 후 서버 시작.
3. `/docs` 페이지에서 `POST /api/rag/search` 경로 확인.
4. `medical_rag.search` 구현 전 호출 결과 503 확인.
5. 향후 검색 모듈 구현 후 실제 검색 결과 및 출처 검증.
