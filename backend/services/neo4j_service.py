from neo4j import AsyncGraphDatabase
from typing import Dict, List
import asyncio

class Neo4jService:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self.driver.close()

    async def create_question_nodes(self, question_text: str, analysis: Dict[str, List[str]]):
        async with self.driver.session() as session:
            await session.execute_write(self._create_question_nodes, question_text, analysis)

    @staticmethod
    async def _create_question_nodes(tx, question_text: str, analysis: Dict[str, List[str]]):
        # Create question node
        query = """
        MERGE (q:Question {text: $text})
        
        WITH q
        UNWIND $concepts AS concept
        MERGE (c:Concept {name: concept})
        MERGE (q)-[:TESTS_CONCEPT]->(c)
        
        WITH q
        UNWIND $prerequisites AS prereq
        MERGE (p:Prerequisite {name: prereq})
        MERGE (q)-[:REQUIRES_PREREQUISITE]->(p)
        
        WITH q
        UNWIND $techniques AS technique
        MERGE (t:Technique {name: technique})
        MERGE (q)-[:SOLVED_BY_TECHNIQUE]->(t)
        
        WITH q
        UNWIND $extensions AS extension
        MERGE (e:Extension {name: extension})
        MERGE (q)-[:EXTENDS_TO]->(e)
        """
        
        await tx.run(query, 
                    text=question_text,
                    concepts=analysis["concepts"],
                    prerequisites=analysis["prerequisites"],
                    techniques=analysis["techniques"],
                    extensions=analysis["extensions"])
        
    async def get_all_concepts(self):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (c:Concept)
                OPTIONAL MATCH (q:Question)-[:TESTS_CONCEPT]->(c)
                RETURN c.name as name, 
                       count(q) as question_count
                ORDER BY question_count DESC
                """
            )
            return [dict(record) for record in await result.data()]

    async def get_all_questions(self):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (q:Question)
                RETURN q.text as text
                """
            )
            return [dict(record) for record in await result.data()]

    async def get_related_questions(self, question: str):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (q1:Question {text: $question})-[r:RELATED_TO]->(q2:Question)
                WHERE q1 <> q2
                RETURN q2.text as text, count(*) as strength
                ORDER BY strength DESC
                """,
                question=question
            )
            return [dict(record) for record in await result.data()]

    async def get_prerequisites_question(self, question: str):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (q:Question {text: $question})-[r:REQUIRES_PREREQUISITE]->(p:Prerequisite)
                RETURN p.name as name, count(*) as count
                ORDER BY count DESC
                """,
                question=question
            )
            return [dict(record) for record in await result.data()]

    async def get_all_techniques(self):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (t:Technique)
                RETURN t.name as name
                """
            )
            return [dict(record) for record in await result.data()]

    async def get_related_techniques(self, technique: str):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (t1:Technique {name: $technique})-[r:RELATED_TO]->(t2:Technique)
                WHERE t1 <> t2
                RETURN t2.name as name, count(*) as strength
                ORDER BY strength DESC
                """,
                technique=technique
            )
            return [dict(record) for record in await result.data()]

    async def get_prerequisites_technique(self, technique: str):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (t:Technique {name: $technique})-[r:REQUIRES_PREREQUISITE]->(p:Prerequisite)
                RETURN p.name as name, count(*) as count
                ORDER BY count DESC
                """,
                technique=technique
            )
            return [dict(record) for record in await result.data()]

    async def get_related_concepts(self, concept: str):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (c1:Concept {name: $concept})<-[:TESTS_CONCEPT]-(q:Question)
                      -[:TESTS_CONCEPT]->(c2:Concept)
                WHERE c1 <> c2
                RETURN c2.name as name, count(*) as strength
                ORDER BY strength DESC
                """,
                concept=concept
            )
            return [dict(record) for record in await result.data()]

    async def get_prerequisites(self, concept: str):
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH (c:Concept {name: $concept})<-[:TESTS_CONCEPT]-(q:Question)
                      -[:REQUIRES_PREREQUISITE]->(p:Prerequisite)
                RETURN p.name as name, count(*) as count
                ORDER BY count DESC
                """,
                concept=concept
            )
            return [dict(record) for record in await result.data()]
        
    async def execute_query(self, query: str, params: Dict = None):
        """Execute a Neo4j query with parameters."""
        async with self.driver.session() as session:
            await session.run(query, params or {})

    async def get_concept_alternatives(self, concept_name: str) -> List[str]:
        """Get all alternative forms of a concept."""
        query = """
        MATCH (c:Concept {name: $name})-[:ALTERNATIVE_FORM]->(a:AlternativeForm)
        RETURN collect(a.name) as alternatives
        """
        async with self.driver.session() as session:
            result = await session.run(query, {"name": concept_name})
            record = await result.single()
            return record["alternatives"] if record else []

    async def get_concept_hierarchy(self, concept_name: str) -> Dict:
        """Get concept hierarchy showing prerequisites and extensions."""
        query = """
        MATCH (c:Concept {name: $name})
        OPTIONAL MATCH (c)<-[r:REQUIRES_PREREQUISITE]-(q:Question)-[:TESTS_CONCEPT]->(c)
        WITH c, collect(DISTINCT r) as prereq_rels
        OPTIONAL MATCH (c)<-[:TESTS_CONCEPT]-(q:Question)-[:EXTENDS_TO]->(e:Extension)
        RETURN {
            name: c.name,
            prerequisites: [(c)<-[:REQUIRES_PREREQUISITE]-(q:Question)-[:TESTS_CONCEPT]->(p:Concept) | p.name],
            extensions: collect(DISTINCT e.name),
            usage_count: size(prereq_rels)
        } as hierarchy
        """
        async with self.driver.session() as session:
            result = await session.run(query, {"name": concept_name})
            record = await result.single()
            return record["hierarchy"] if record else {}

    async def get_domain_concepts(self, domain: str) -> List[Dict]:
        """Get all concepts within a mathematical domain."""
        query = """
        MATCH (q:Question {domain: $domain})-[:TESTS_CONCEPT]->(c:Concept)
        WITH c, count(q) as usage_count
        RETURN {
            name: c.name,
            usage_count: usage_count
        } as concept
        ORDER BY usage_count DESC
        """
        async with self.driver.session() as session:
            result = await session.run(query, {"domain": domain})
            return [record["concept"] async for record in result]

    async def get_concept_difficulty(self, concept_name: str) -> float:
        """Calculate concept difficulty based on questions that test it."""
        query = """
        MATCH (c:Concept {name: $name})<-[:TESTS_CONCEPT]-(q:Question)
        RETURN avg(q.difficulty_level) as avg_difficulty
        """
        async with self.driver.session() as session:
            result = await session.run(query, {"name": concept_name})
            record = await result.single()
            return record["avg_difficulty"] if record else 0.0
