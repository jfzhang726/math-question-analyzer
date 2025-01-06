from typing import Dict, List
import openai
from backend.services.neo4j_service import Neo4jService
import json
import traceback
import logging 
logger = logging.getLogger(__name__)

class QuestionAnalyzer:
    def __init__(self, api_key: str, neo4j_service: Neo4jService):
        self.client = openai.OpenAI(api_key=api_key)
        logger.info(f"openai client: {self.client}")
        self.neo4j_service = neo4j_service

    async def analyze_question(self, question_text: str) -> Dict[str, List[str]]:
        logger.info(f"start analyze_question, question_text {question_text}")
        prompt = """
        Analyze the following math question and provide a JSON response with these elements:
        - concepts: Main mathematical concepts being tested
        - prerequisites: Knowledge required to solve this
        - techniques: Problem-solving techniques that could be used
        - extensions: More advanced concepts this leads to

        Math Question: {question}

        Provide the response in this exact JSON format:
        {{
            "concepts": ["concept1", "concept2"],
            "prerequisites": ["prereq1", "prereq2"],
            "techniques": ["technique1", "technique2"],
            "extensions": ["extension1", "extension2"]
        }}
        """

        try:
            logger.info(f"invoke open ai")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt.format(question=question_text)}
                ],
                response_format={ "type": "json_object" }
            )
            logger.info(f"response from openai {response}")
            analysis = json.loads(response.choices[0].message.content)
            logger.info(f"analysis result: {analysis}")
            # Store in knowledge graph
            logger.info(f"store analysis result to neo4j")
            await self.store_analysis(question_text, analysis)
            logger.info(f"finished storing to neo4j")
            return analysis
        except Exception as e:
            logger.error(traceback.format_exc())
            raise Exception(f"Error analyzing question: {str(e)}")
        

    async def store_analysis(self, question_text: str, analysis: Dict[str, List[str]]):
        await self.neo4j_service.create_question_nodes(question_text, analysis)
