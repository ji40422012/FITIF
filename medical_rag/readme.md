# medical_rag — 개발자 B 작업 영역

## 이번 전달물 상태
이 폴더는 이후 구현할 모듈의 **인터페이스와 준비사항을 문서화**한 것입니다. 현재 `search.py`, `load_embeddings.py` 파일은 아직 만들어지지 않았습니다.

## 기존 로컬 작업 산출물
`medical-rag/data/processed/`에서 생성된 다음 파일을 팀 프로젝트에 복사할 계획입니다.

- `guideline_chunks_fixed.jsonl`: 994개 청크, 512토큰 초과 0개.
- `embeddings/guideline_vectors.npy`: 994행 × 384차원.
- `embeddings/guideline_metadata.jsonl`: 원문/출처 메타데이터.
- `embeddings/embedding_manifest.json`: 모델 및 처리 설정.

## 예정 검색 함수의 계약
`medical_rag/search.py`에서 다음 함수를 구현합니다.

```python
def search_guidelines(query: str, top_k: int) -> list[dict]:
    """검색어를 E5-small query 접두어로 임베딩하고 pgvector에서 상위 청크 반환."""
```

반환할 각 dict 필수 키: `chunk_id`, `text`, `score`.
선택 키: `pdf_page`, `document_title`, `publisher`, `requires_review`, `review_flags`.
`score`는 DB cosine distance `<=>`를 활용한 `1 - distance`로 정의합니다.

- 문서 적재 시 `passage:` 접두어, 검색 질문 시 `query:` 접두어 및 **같은 모델** `intfloat/multilingual-e5-small` 사용.
- 질문의 토큰 수를 512 이내로 검사. 초과 시 `ValueError`.
- `backend.database.get_connection()`으로 read-only SELECT 수행.
- 데이터베이스 결과의 청크와 출처를 반환할 뿐 의료적 판단을 생성하지 않습니다.
- PDF 추출 과정의 표/임상 수치 품질 문제는 아직 자동 해결되지 않았습니다.

## 예정 적재 함수
`load_embeddings.py`는 적재용 권한 계정으로 `rag.document`, `rag.chunk`에 994건을 저장합니다. 기존 `backend.database.get_connection()`은 **읽기 전용**이므로 재사용하지 않습니다.

## 주의
실제 환자 데이터와 RAG 문서는 구분하고, 테스트 샘플이라도 가명 ID·환자 검사기록을 로그에 출력하지 않습니다.
