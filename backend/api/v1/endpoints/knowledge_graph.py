from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from backend.services.neo4j_service import Neo4jService
from backend.config import settings
import traceback
import logging 

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_neo4j_service():
    service = Neo4jService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    )
    try:
        yield service
    finally:
        await service.close()

@router.get("/concepts")
async def get_all_concepts(neo4j: Neo4jService = Depends(get_neo4j_service)):
    """Get all mathematical concepts in the knowledge graph."""
    try:
        return await neo4j.get_all_concepts()
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/related/{concept}")
async def get_related_concepts(
    concept: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get concepts related to the specified concept."""
    try:
        return await neo4j.get_related_concepts(concept)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prerequisites/{concept}")
async def get_prerequisites(
    concept: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get prerequisites for the specified concept."""
    try:
        return await neo4j.get_prerequisites(concept)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions")
async def get_all_questions(neo4j: Neo4jService = Depends(get_neo4j_service)):
    """Get all mathematical questions in the knowledge graph."""
    try:
        return await neo4j.get_all_questions()
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/related_question/{question}")
async def get_related_questions(
    question: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get questions related to the specified question."""
    try:
        return await neo4j.get_related_questions(question)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prerequisites_question/{question}")
async def get_prerequisites_question(
    question: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get prerequisites for the specified question."""
    try:
        return await neo4j.get_prerequisites_question(question)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/techniques")
async def get_all_techniques(neo4j: Neo4jService = Depends(get_neo4j_service)):
    """Get all mathematical techniques in the knowledge graph."""
    try:
        return await neo4j.get_all_techniques()
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/related_technique/{technique}")
async def get_related_techniques(
    technique: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get techniques related to the specified technique."""
    try:
        return await neo4j.get_related_techniques(technique)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prerequisites_technique/{technique}")
async def get_prerequisites_technique(
    technique: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """Get prerequisites for the specified technique."""
    try:
        return await neo4j.get_prerequisites_technique(technique)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
