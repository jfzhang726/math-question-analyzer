import pytest
from backend.core.question_analyzer import QuestionAnalyzer
from backend.services.neo4j_service import Neo4jService
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def mock_neo4j_service():
    service = Mock(spec=Neo4jService)
    service.create_question_nodes = AsyncMock()
    return service

@pytest.fixture
def analyzer(mock_neo4j_service):
    return QuestionAnalyzer("fake-api-key", mock_neo4j_service)

@pytest.mark.asyncio
async def test_analyze_question(analyzer):
    # Test data
    question = "Solve the equation: 2x + 5 = 13"
    
    # Analyze question
    result = await analyzer.analyze_question(question)
    
    # Verify structure
    assert isinstance(result, dict)
    assert "concepts" in result
    assert "prerequisites" in result
    assert "techniques" in result
    assert "extensions" in result
    
    # Verify types
    assert all(isinstance(x, str) for x in result["concepts"])
    assert all(isinstance(x, str) for x in result["prerequisites"])
    assert all(isinstance(x, str) for x in result["techniques"])
    assert all(isinstance(x, str) for x in result["extensions"])