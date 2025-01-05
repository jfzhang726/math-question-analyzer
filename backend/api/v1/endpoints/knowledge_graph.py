from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_knowledge_graph():
    return {"message": "Knowledge graph endpoint"}