import json
from typing import List, Dict, Set, Optional
from pydantic import BaseModel
import openai
from neo4j import AsyncGraphDatabase
import logging

logger = logging.getLogger(__name__)

class ConceptMatch(BaseModel):
    input_concept: str
    matched_concept: Optional[str]
    confidence: float
    is_new: bool

class ConceptNormalizerService:
    def __init__(self, neo4j_service, openai_client):
        self.neo4j = neo4j_service
        self.llm = openai_client
        self.concept_cache = {}  # In-memory cache of normalized concepts
        
    async def normalize_concepts(self, new_concepts: List[str]) -> Dict[str, ConceptMatch]:
        """
        Normalize new concepts against existing ones in the knowledge graph.
        Returns mapping of input concepts to their normalized forms.
        """
        # Get existing concepts from Neo4j
        existing_concepts = await self._get_existing_concepts()
        
        # Process each new concept
        normalized_concepts = {}
        for concept in new_concepts:
            if concept.lower() in self.concept_cache:
                normalized_concepts[concept] = self.concept_cache[concept.lower()]
            else:
                match = await self._find_matching_concept(concept, existing_concepts)
                self.concept_cache[concept.lower()] = match
                normalized_concepts[concept] = match
                
        return normalized_concepts

    async def _get_existing_concepts(self) -> Dict[str, Set[str]]:
        """
        Retrieve existing concepts and their alternative forms from Neo4j.
        """
        query = """
        MATCH (c:Concept)
        OPTIONAL MATCH (c)-[:ALTERNATIVE_FORM]->(a:AlternativeForm)
        RETURN c.name as name, collect(a.name) as alternatives
        """
        async with self.neo4j.driver.session() as session:
            result = await session.run(query)
            concepts = {}
            async for record in result:
                name = record["name"]
                alternatives = set(record["alternatives"])
                alternatives.add(name)
                concepts[name] = alternatives
            return concepts

    async def _find_matching_concept(
        self, 
        new_concept: str, 
        existing_concepts: Dict[str, Set[str]]
    ) -> ConceptMatch:
        """
        Find if a new concept matches any existing ones using LLM.
        """
        if not existing_concepts:
            return ConceptMatch(
                input_concept=new_concept,
                matched_concept=None,
                confidence=1.0,
                is_new=True
            )

        # Create prompt for LLM
        concepts_list = "\n".join(f"- {c}" for c in existing_concepts.keys())
        prompt = f"""Given a new mathematical concept and a list of existing concepts,
        determine if the new concept is equivalent to or a variation of any existing concept.
        If it is, return the existing concept name and confidence score (0-1).
        If it's a genuinely new concept, indicate that.
        
        New concept: {new_concept}
        
        Existing concepts:
        {concepts_list}
        
        Return in JSON format:
        {{
            "is_match": boolean,
            "matched_concept": string or null,
            "confidence": float,
            "explanation": string
        }}
        """

        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        
        
        result = json.loads(response.choices[0].message.content)
        # If match found, verify against alternatives
        if result["is_match"] and result["matched_concept"]:
            # Check if it matches any alternative forms
            for concept, alternatives in existing_concepts.items():
                if result["matched_concept"] in alternatives:
                    return ConceptMatch(
                        input_concept=new_concept,
                        matched_concept=concept,  # Use the primary concept name
                        confidence=result["confidence"],
                        is_new=False
                    )
        
        # No match found or confidence too low
        return ConceptMatch(
            input_concept=new_concept,
            matched_concept=None,
            confidence=1.0,
            is_new=True
        )

    async def store_new_concept(self, concept_match: ConceptMatch):
        """
        Store new concept or alternative form in Neo4j.
        """
        if concept_match.is_new:
            query = """
            MERGE (c:Concept {name: $name})
            """
            params = {"name": concept_match.input_concept}
        else:
            query = """
            MATCH (c:Concept {name: $existing_name})
            MERGE (a:AlternativeForm {name: $new_name})
            MERGE (c)-[:ALTERNATIVE_FORM]->(a)
            """
            params = {
                "existing_name": concept_match.matched_concept,
                "new_name": concept_match.input_concept
            }
            
        async with self.neo4j.driver.session() as session:
            await session.run(query, params)