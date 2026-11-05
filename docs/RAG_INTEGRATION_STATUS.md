# FITIF Medical RAG 통합 현황 — 팀 공유용

## 목적
개발자 B의 2025 당뇨병 진료지침 기반 Medical RAG를 팀의 PostgreSQL 16 (`team_project`) 및 FastAPI 백엔드에 연결합니다. 기존 CGM API와 환자 데이터 스키마를 보호합니다.

## 신규 전달 파일 / 경로별 작업

| 경로 | 파일 | 상태 | 담당/조치 |
|---|---|---|---|
| `backend/` | `rag_router.py` | **작성 완료** | B: 검색 API 라우터 |
| `backend/` | `RAG_ROUTER.md` | **작성 완료** | A/B: `main.py` 등록법 및 API 계약 |
| `db/` | `RAG_DB_GUIDE.md` | **작성 완료** | DB 담당: 스키마/권한 검토 |
| `db/` | `rag_schema.sql` | **미작성** | B+DB 담당: 별도 스키마 작성 |
| `medical_rag/` | `README.md` | **작성 완료** | B/C: 검색·적재 인터페이스 |
| `medical_rag/` | `search.py` | **미작성** | B: E5 질의 임베딩 및 pgvector 검색 |
| `medical_rag/` | `load_embeddings.py` | **미작성** | B: 994개 벡터 저장 |
| `docs/` | `RAG_INTEGRATION_STATUS.md` | **작성 완료** | 팀 공유용 통합 변경 로그 |

## 기존 코드 변경 요청 (직접 수정하지 않았음)
`backend/main.py`에 다음 두 줄만 추가합니다.

```python
from .rag_router import router as rag_router
# app = FastAPI(...) 선언 후
app.include_router(rag_router)
```

- 기존 `backend/database.py`, `backend/main.py`, `db/schema.sql` 원본은 이번 배포본에 포함하지 않았으며 **덮어쓰지 않습니다**.
- `/api/cgm/readings`는 현재 `public.cgm_reading_old`를 사용하며 신규 `public.cgm_reading`과 다른 테이블입니다. 해당 이관은 A파트 소관입니다.
- 신규 API는 `POST /api/rag/search`이며, 검색 구현 전 요청 시 HTTP 503을 반환합니다.

## 단계별 완료 조건
1. FastAPI 실행 시 기존 API가 동일하게 동작하고 `/docs`에 RAG 엔드포인트가 표시됨.
2. 팀 DB에 pgvector 설치 및 `rag` 스키마 생성.
3. 로컬의 994개 청크와 384차원 벡터 적재 후 행 수·순서·원문/출처 검증.
4. `search_guidelines` 완성 후 단순 검색 결과 및 PDF 페이지 검토.
5. Gemma 답변 생성은 C파트에서 근거 인용을 검증한 뒤 통합.

## 정책 및 품질 주의
- 공개된 진료지침은 출처 표기를 유지하고 재배포/저장 정책을 검토합니다.
- 기존 PDF 표와 임상 수치의 OCR/추출 정확도는 검토되지 않은 항목이 있습니다.
- RAG 결과는 의료 근거 후보이며 진단, 처방, 용량 변경의 자동 결정을 의미하지 않습니다.
- 현재 인증 없는 API는 외부에 공개하지 않습니다.
