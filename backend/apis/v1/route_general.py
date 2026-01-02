from fastapi import APIRouter, FastAPI

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok"
    }
