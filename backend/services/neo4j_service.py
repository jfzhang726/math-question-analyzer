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