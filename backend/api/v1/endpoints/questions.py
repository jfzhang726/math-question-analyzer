from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

class QuestionAnalysis(BaseModel):
    concepts: list[str]
    prerequisites: list[str]
    techniques: list[str]
    extensions: list[str]

@router.post("/", response_model=QuestionAnalysis)
async def analyze_question(
    text: Optional[str] = None,
    image: Optional[UploadFile] = File(None)
):
    if text is None and image is None:
        raise HTTPException(status_code=400, detail="Either text or image must be provided")
    
    # Placeholder response
    return QuestionAnalysis(
        concepts=["algebra", "linear_equations"],
        prerequisites=["basic_arithmetic"],
        techniques=["substitution_method"],
        extensions=["systems_of_equations"]
    )
