# FITIF Medical RAG DB 변경 안내 (B파트)

## 이번 추가 사항

- `db/rag_schema.sql` 신규: `team_project` DB의 **별도 `rag` 스키마**에 `rag.document`, `rag.chunk` 두 테이블을 만듭니다.
- `rag.chunk.embedding`은 `VECTOR(384)`이며 `intfloat/multilingual-e5-small`과 맞춥니다.
- `chunk_id`와 PDF 페이지, 원문, 검토 상태를 벡터와 함께 저장합니다.
- 기존 `public.member`, `public.encounter`, `public.cgm_reading` 등 **팀 테이블을 삭제하거나 변경하지 않습니다**.
- `public.source_document`는 환자 OCR 문서용으로 유지합니다. 공용 의료지침은 `rag.document`에 저장합니다.

## 실행 전 확인 (DB 담당자와 협의)

1. 연결 대상 DB가 **PostgreSQL 16의 `team_project`**인지 확인합니다. 개인 PC의 `medical_rag` DB 또는 PG17 컨테이너와 구분합니다.
2. `SELECT version();` 및 `SELECT extversion FROM pg_extension WHERE extname='vector';` 확인.
3. pgvector가 설치되지 않았으면 **서버 환경에 extension 파일 설치**가 선행돼야 합니다. `CREATE EXTENSION`만으로 설치 파일이 생기지는 않습니다.
4. 역할에 `CREATE EXTENSION`, `CREATE SCHEMA`, 테이블 생성 권한이 있는지 DB 담당자가 확인합니다.
5. **기존 `db/schema.sql`에는 DROP TABLE이 있으므로 재실행하지 않습니다.**

## 적용

팀 DB에 접속된 SQL Query Tool에서 `db/rag_schema.sql`만 실행합니다.

검증 SQL:

```sql
SELECT extversion FROM pg_extension WHERE extname='vector';
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema='rag' ORDER BY table_name;
SELECT COUNT(*) FROM rag.chunk;
```

처음 생성했다면 `rag.chunk`의 행 수는 `0`입니다. 이후 `medical_rag/load_embeddings.py`에서 **최종 994개 Embedding**을 적재할 계획입니다.

## 보안/운영

- `backend/database.py`의 읽기 전용 `get_connection()`은 검색용입니다. **INSERT에는 사용하지 않습니다**.
- 적재는 별도 쓰기 권한 연결을 사용하고, 실제 비밀번호는 `backend/.env` 등 비공개 환경변수로 관리합니다.
- `CREATE TABLE IF NOT EXISTS`는 기존 테이블의 컬럼 구조가 맞는지 검증하지 않습니다. 이름이 같은 다른 구조가 있다면 적용을 멈추고 DBA에게 확인하세요.
- `rag.chunk`는 우선 정확한 코사인 거리 검색(`ORDER BY embedding <=> query_vector`)을 사용합니다. 994건 규모에서 ANN 인덱스는 필수가 아닙니다.
- 임상 검토 플래그는 원문 정확성을 보증하지 않습니다. 표/약물 용량 등은 원본 대조가 별도로 필요합니다.

## 미완료

- `medical_rag/load_embeddings.py` — 994개 Embedding 적재 및 건수 검증
- `medical_rag/search.py` — 질문 `query:` Embedding 및 벡터 검색
- `backend/rag_router.py` 통합 테스트 — 이미 작성된 라우터는 검색 모듈 구현 후 동작
