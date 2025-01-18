from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import openai
from backend.services.concept_normalization_service import ConceptNormalizerService
from backend.services.neo4j_service import Neo4jService
import json
import traceback
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalysisResult(BaseModel):
    concepts: List[str]
    prerequisites: List[str]
    techniques: List[str]
    extensions: List[str]
    difficulty_level: float
    solution_steps: List[Dict[Any, Any]]
    domain: str
    timestamp: datetime

class QuestionAnalyzer:
    def __init__(self, api_key: str, neo4j_service: Neo4jService):
        self.client = openai.OpenAI(api_key=api_key)
        self.neo4j_service = neo4j_service
        self.concept_normalizer = ConceptNormalizerService(neo4j_service, self.client)
        
    async def analyze_question(self, question_text: str) -> AnalysisResult:
        """Enhanced question analysis with concept normalization and additional features."""
        logger.info(f"Starting enhanced analysis for question: {question_text}")
        
        try:
            # Get initial analysis from LLM
            raw_analysis = await self._get_llm_analysis(question_text)
            logger.info(f"raw_analysis\n{raw_analysis}")
            # Normalize all concept types
            normalized_concepts = await self.concept_normalizer.normalize_concepts(raw_analysis["concepts"])
            normalized_prereqs = await self.concept_normalizer.normalize_concepts(raw_analysis["prerequisites"])
            normalized_techniques = await self.concept_normalizer.normalize_concepts(raw_analysis["techniques"])
            
            # Store new concepts and relationships
            for matches in [normalized_concepts, normalized_prereqs, normalized_techniques]:
                for match in matches.values():
                    await self.concept_normalizer.store_new_concept(match)
            
            # Create final analysis result
            result = AnalysisResult(
                concepts=[m.matched_concept or m.input_concept for m in normalized_concepts.values()],
                prerequisites=[m.matched_concept or m.input_concept for m in normalized_prereqs.values()],
                techniques=[m.matched_concept or m.input_concept for m in normalized_techniques.values()],
                extensions=raw_analysis["extensions"],
                difficulty_level=raw_analysis["difficulty_level"],
                solution_steps=raw_analysis["solution_steps"],
                domain=raw_analysis["domain"],
                timestamp=datetime.now()
            )
            
            # Store enhanced analysis in graph
            await self._store_enhanced_analysis(question_text, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced analysis: {traceback.format_exc()}")
            raise Exception(f"Error analyzing question: {str(e)}")

    async def _get_llm_analysis(self, question_text: str) -> Dict:
        """Get enhanced analysis from LLM."""
        prompt = """
        Analyze the following math question and provide a detailed JSON response with:
        - concepts: Main mathematical concepts being tested
        - prerequisites: Knowledge required to solve this
        - techniques: Problem-solving techniques that could be used
        - extensions: More advanced concepts this leads to
        - difficulty_level: A score from 0-1 indicating question difficulty
        - solution_steps: Array of step-by-step solution guidance
        - domain: Primary mathematical domain (e.g., Algebra, Geometry, Calculus)

        Math Question: {question}

        Provide the response in this exact JSON format:
        {{
            "concepts": ["concept1", "concept2"],
            "prerequisites": ["prereq1", "prereq2"],
            "techniques": ["technique1", "technique2"],
            "extensions": ["extension1", "extension2"],
            "difficulty_level": 0.7,
            "solution_steps": [
                {{"step": 1, "description": "First, ...", "concepts_used": ["concept1"]}},
                {{"step": 2, "description": "Then, ...", "concepts_used": ["concept2"]}}
            ],
            "domain": "Algebra"
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt.format(question=question_text)}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

    async def _store_enhanced_analysis(self, question_text: str, analysis: AnalysisResult):
        """Store enhanced analysis in Neo4j with new relationship types and properties."""
        query = """
        // Create question node with metadata
        MERGE (q:Question {text: $text})
        SET q.difficulty_level = $difficulty_level,
            q.domain = $domain,
            q.analyzed_at = $timestamp
        
        // Create and link concepts
        WITH q
        UNWIND $concepts AS concept
        MERGE (c:Concept {name: concept})
        MERGE (q)-[r:TESTS_CONCEPT]->(c)
        SET r.strength = 1.0
        
        // Create and link prerequisites with ordering
        WITH q
        UNWIND $prerequisites_with_index AS prereq
        MERGE (p:Concept {name: prereq.name})
        MERGE (q)-[r:REQUIRES_PREREQUISITE]->(p)
        SET r.order = prereq.index
        
        // Create solution steps
        WITH q
        UNWIND $solution_steps AS step
        CREATE (s:SolutionStep {
            step_number: step.step,
            description: step.description
        })
        MERGE (q)-[:HAS_STEP]->(s)
        WITH s, step
        UNWIND step.concepts_used AS concept_used
        MERGE (c:Concept {name: concept_used})
        MERGE (s)-[:USES_CONCEPT]->(c)
        """
        
        # Prepare prerequisites with order information
        prerequisites_with_index = [
            {"name": name, "index": idx}
            for idx, name in enumerate(analysis.prerequisites)
        ]
        
        params = {
            "text": question_text,
            "difficulty_level": analysis.difficulty_level,
            "domain": analysis.domain,
            "timestamp": analysis.timestamp.isoformat(),
            "concepts": analysis.concepts,
            "prerequisites_with_index": prerequisites_with_index,
            "solution_steps": analysis.solution_steps
        }
        
        await self.neo4j_service.execute_query(query, params)