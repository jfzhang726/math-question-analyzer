from neo4j import GraphDatabase
from typing import Dict, List

class Neo4jService:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_question_node(self, question_text: str, analysis: Dict[str, List[str]]):
        with self.driver.session() as session:
            session.execute_write(self._create_question_node, question_text, analysis)
    
    @staticmethod
    def _create_question_node(tx, question_text: str, analysis: Dict[str, List[str]]):
        # Create question node
        query = """
        CREATE (q:Question {text: $text})
        """
        tx.run(query, text=question_text)
        
        # TODO: Create concept nodes and relationships