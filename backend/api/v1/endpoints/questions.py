from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
import os
from backend.core.question_analyzer import QuestionAnalyzer
from backend.services.neo4j_service import Neo4jService
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import io
import logging 

logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()

# Dependency for services
async def get_analyzer():
    neo4j_service = Neo4jService(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    logger.info(f"instantiate neo4j_service {neo4j_service}")
    analyzer = QuestionAnalyzer(
        api_key=os.getenv("OPENAI_API_KEY"),
        neo4j_service=neo4j_service
    )
    logger.info(f"analyser instantizted {analyzer}")
    try:
        yield analyzer
    finally:
        await neo4j_service.close()

class QuestionAnalysis(BaseModel):
    concepts: list[str]
    prerequisites: list[str]
    techniques: list[str]
    extensions: list[str]

@router.post("/", response_model=QuestionAnalysis)
async def analyze_question(
    text: Optional[str] = None,
    image: Optional[UploadFile] = File(None),
    analyzer: QuestionAnalyzer = Depends(get_analyzer)
):
    logger.info(f"received text {text}")
    try:
        if text is None and image is None:
            raise HTTPException(
                status_code=400,
                detail="Either text or image must be provided"
            )
        
        if image:
            # Process image using OCR
            contents = await image.read()
            img = Image.open(io.BytesIO(contents))
            text = pytesseract.image_to_string(img)
            
            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract text from image"
                )
        logger.info(f"send text to analyzer {text}")
        analysis = await analyzer.analyze_question(text)
        return analysis
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )