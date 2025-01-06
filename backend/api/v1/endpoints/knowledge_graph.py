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
        raise HTTPException(status_code=500, detail=str(e))