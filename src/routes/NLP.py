from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from src.controllers.NLPController import NLPController
from pydantic import BaseModel


nlp_router = APIRouter(prefix="/api/v1/nlp", tags=["nlp"])
nlp_controller = NLPController()


class VectorizeRequest(BaseModel):
    do_reset: bool = False


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


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
