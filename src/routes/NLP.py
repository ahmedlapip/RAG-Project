from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from src.controllers.NLPController import NLPController
from pydantic import BaseModel
from typing import Optional


nlp_router = APIRouter(prefix="/api/v1/nlp", tags=["nlp"])
nlp_controller = NLPController()


class VectorizeRequest(BaseModel):
    do_reset: bool = False


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


class AnswerQuestionRequest(BaseModel):
    question: str
    limit: int = 5
    max_output_token: Optional[int] = None
    temperature: Optional[float] = None


@nlp_router.post("/vectorize/{project_id}")
async def vectorize_project(request: Request, project_id: str, body: VectorizeRequest):
    try:
        result = await nlp_controller.vectorize_project(
            request=request, project_id=project_id, do_reset=body.do_reset
        )

        if not result.get("success", False):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)

        return result

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": str(e)},
        )


@nlp_router.get("/vectorization-info/{project_id}")
async def get_vectorization_info(request: Request, project_id: str):
    try:
        result = await nlp_controller.get_vectorization_info(
            request=request, project_id=project_id
        )

        if not result.get("success", False):
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)

        return result

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": str(e)},
        )


@nlp_router.post("/search/{project_id}")
async def get_similar_vectors(request: Request, project_id: str, body: SearchRequest):
    try:
        result = await nlp_controller.get_similar_vectors(
            request=request,
            project_id=project_id,
            query_text=body.query,
            limit=body.limit,
        )

        if not result.get("success", False):
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)

        return result

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": str(e)},
        )


@nlp_router.post("/answer/{project_id}")
async def answer_user_question(
    request: Request, project_id: str, body: AnswerQuestionRequest
):
    try:
        result = await nlp_controller.answer_user_question(
            request=request,
            project_id=project_id,
            question=body.question,
            limit=body.limit,
            max_output_token=body.max_output_token,
            temperature=body.temperature,
        )

        if not result.get("success", False):
            status_code = status.HTTP_404_NOT_FOUND
            if "not found" in result.get("message", "").lower():
                status_code = status.HTTP_404_NOT_FOUND
            elif "vectorize" in result.get("message", "").lower():
                status_code = status.HTTP_400_BAD_REQUEST
            return JSONResponse(status_code=status_code, content=result)

        return result

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": str(e)},
        )
