# FITIF Medical RAG 통합 현황 — DB 스키마 단계

## 현재 팀에서 확인한 구현

- `backend/main.py`: `/`, `/health`, `/api/cgm/readings` API. CGM은 현재 `public.cgm_reading_old`를 조회.
- `backend/database.py`: `backend/.env` 환경변수, `psycopg2`, **읽기 전용** `get_connection()`.
- `db/schema.sql`: `public`의 9개 의료기록 테이블 정의. 상단 `DROP TABLE` 주의.
- `llm_app/`, `ingest/`, `ocr_loader/`: 폴더 존재만 확인했고 구현 내용은 확인하지 못함.

## B파트 기존 산출물

- 당뇨병 진료지침 PDF 추출 및 chunking: **994개 최종 청크**.
- `intfloat/multilingual-e5-small` Embedding: **994 x 384**. 512토큰 초과 0건.
- `backend/rag_router.py`: `POST /api/rag/search` 인터페이스 초안. 실제 검색 모듈이 없어 현재 503이 정상.

## 이번 단계 새 파일

- `db/rag_schema.sql`: pgvector 확장 + `rag.document` / `rag.chunk` 테이블 생성 SQL.
- `db/RAG_DB_GUIDE.md`: DB 담당자가 확인할 환경, 권한 및 검증 SQL 안내.

## 기존 팀 코드 변경 여부

- 이번 전달물은 **신규 파일만 추가**하며 `backend/main.py`, `backend/database.py`, `db/schema.sql`을 변경하지 않음.
- 사용자가 기존 `backend/main.py`에 라우터 import와 `app.include_router(rag_router)`를 추가했다고 확인함.

## 파일 배치 점검

- **정상 위치:** `backend/rag_router.py`, `backend/RAG_ROUTER.md`.
- `db/rag_router.py`, `db/RAG_ROUTER.md`가 있다면 파일이 중복 배치된 것으로 보임. 해당 파일을 실제로 참조하는 코드가 없는지 확인 후 중복본만 정리.
- `db/`에는 Python API 라우터가 아니라 `rag_schema.sql`, `RAG_DB_GUIDE.md`를 두는 것을 권장.

## 다음 순서

1. DB 담당자에게 PostgreSQL 16 `team_project` / pgvector 확장 / 쓰기 계정 확인.
2. `db/rag_schema.sql` 실행, `rag.chunk`가 0건인 상태 확인.
3. `medical_rag/load_embeddings.py`로 994개 적재.
4. `medical_rag/search.py` 작성 및 라우터와 실제 검색 통합 검증.
