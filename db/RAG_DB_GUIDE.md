# db 변경 안내 — Medical RAG 스키마 계획

## 현재 상태
- 이번 전달물에는 **DB에 실행할 SQL이 포함되어 있지 않습니다**. DB 구조는 제안 단계입니다.
- 기존 `db/schema.sql`에는 `DROP TABLE` 구문이 있어 기존 데이터가 있다면 **전체 재실행 금지**.
- 팀 DB: PostgreSQL **16**, DB명 `team_project` (제공된 팀 스키마 기준).

## 신규 SQL 계획: `db/rag_schema.sql`
기존 `public.member`, `public.cgm_reading`, `public.source_document` 등을 수정하지 않고 별도의 `rag` 스키마를 사용합니다.

- `rag.document`: 진료지침 문서 제목, 발행기관, 발행연도, 원본 파일.
- `rag.chunk`: 청크 ID, 문서 ID, 본문, PDF 페이지, 검토 플래그, `embedding vector(384)`.
- `CREATE EXTENSION IF NOT EXISTS vector`는 DBA 권한 및 서버에 pgvector 설치가 필요합니다.

## 팀 DBA 확인 사항
1. 팀 DB 서버에 pgvector가 설치·활성화되어 있는지.
2. RAG 스키마 CREATE, INSERT, SELECT를 각각 수행할 계정/권한.
3. 검색 시 사용할 read-only 계정이 `rag` 스키마의 SELECT 권한을 갖는지.
4. 운영 중 기존 `schema.sql`의 DROP/재생성 절차를 금지할지.
5. 서버 PostgreSQL 16과 로컬 PostgreSQL 17 개발 인스턴스가 혼동되지 않도록 접속정보 확인.

## 의료 데이터 구분
- `public.source_document`는 **환자별 OCR 문서**입니다.
- `rag.document`는 **공통 의학적 근거 문서**입니다.
- 둘을 혼합하거나 환자별 데이터에 인용용 진료지침 원문을 저장하지 않습니다.
