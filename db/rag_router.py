"""FITIF Medical RAG 검색 API 라우터

기존 backend.main / backend.database.py의 CGM 조회 동작을 변경하지 않습니다.

엔드포인트
    POST /api/rag/search

의존성
    향후 구현할 medical_rag.search.search_guidelines(query, top_k).
    해당 모듈이 아직 없으면 API는 503으로 응답하며 서버 자체는 실행됩니다.

주의
    이 API는 의료지침 검색 후보와 출처를 반환하며, 진단·처방이나
    개별 약물 용량 변경을 결정하지 않습니다.
"""

import logging
from typing import Any

import psycopg2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["Medical RAG"])


class RagSearchRequest(BaseModel):
    """사용자 질문 및 검색 결과 개수."""

    query: str = Field(
        ...,
        min_length=2,
        max_length=1000,
        description="진료지침에서 근거를 찾을 질문 (2~1000자)",
        examples=["제2형 당뇨병 환자의 저혈당 대처 방법은?"],
    )
    top_k: int = Field(default=5, ge=1, le=10, description="반환할 청크 수 (1~10)")


class RagSearchItem(BaseModel):
    chunk_id: str
    text: str
    pdf_page: int | None = None
    document_title: str | None = None
    publisher: str | None = None
    score: float = Field(description="코사인 유사도 (1 - cosine distance)")
    requires_review: bool = False
    review_flags: list[str] = Field(default_factory=list)


class RagSearchResponse(BaseModel):
    query: str
    count: int
    results: list[RagSearchItem]
    notice: str = (
        "검색 결과는 의료지침의 근거 후보입니다. PDF 원문 및 임상적 타당성 검토가 필요합니다."
    )


@router.post(
    "/search",
    response_model=RagSearchResponse,
    summary="당뇨병 진료지침 근거 검색",
    description="질문을 벡터화해 pgvector에서 유사한 의료지침 청크와 PDF 페이지를 반환합니다.",
)
def search_rag(request: RagSearchRequest) -> RagSearchResponse:
    """검색 로직과 API 계층을 분리합니다.

    medical_rag.search.search_guidelines 의 계약:
        입력: query: str, top_k: int
        반환: dict 목록 (RagSearchItem 필드 포함)
    """
    query = request.query.strip()
    if len(query) < 2:
        raise HTTPException(status_code=422, detail="query must contain at least 2 non-space characters")

    try:
        # 아직 구현되지 않은 검색 모듈 때문에 기존 FastAPI 서버가
        # 시작조차 못하는 일을 막기 위해 요청 시점에 불러옵니다.
        from medical_rag.search import search_guidelines
    except ImportError as exc:
        logger.warning("Medical RAG search module unavailable: %s", type(exc).__name__)
        raise HTTPException(
            status_code=503,
            detail="Medical RAG search component is not installed yet",
        ) from exc

    try:
        raw_results: list[dict[str, Any]] = search_guidelines(
            query=query, top_k=request.top_k
        )
    except (psycopg2.Error, ConnectionError, TimeoutError, RuntimeError) as exc:
        # DB 접속정보, SQL, 개인정보, 검색어 등의 내부 정보는 응답하지 않습니다.
        logger.error("Medical RAG backend temporarily unavailable (%s)", type(exc).__name__)
        raise HTTPException(
            status_code=503,
            detail="Medical RAG search temporarily unavailable",
        ) from exc
    except ValueError as exc:
        # 향후 search_guidelines가 토큰 제한 초과를 ValueError로 전달하도록 계약합니다.
        raise HTTPException(status_code=422, detail="Query cannot be embedded; shorten the question") from exc
    except Exception as exc:
        logger.exception("Unexpected Medical RAG search error")
        raise HTTPException(status_code=500, detail="Medical RAG search failed") from exc

    # 검색 함수의 결과 형식을 확인하고 잘못된 데이터가 외부로 반환되지 않게 합니다.
    try:
        results = [RagSearchItem.model_validate(item) for item in raw_results]
    except (TypeError, ValueError) as exc:
        logger.error("Invalid Medical RAG search result format")
        raise HTTPException(status_code=500, detail="Medical RAG result format error") from exc

    return RagSearchResponse(query=query, count=len(results), results=results)
