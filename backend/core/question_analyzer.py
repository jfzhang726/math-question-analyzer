from typing import Dict, List
import openai

class QuestionAnalyzer:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    async def analyze_question(self, question_text: str) -> Dict[str, List[str]]:
        prompt = f"""
        Analyze the following math question and identify:
        1. Main mathematical concepts tested
        2. Prerequisites needed to solve it
        3. Problem-solving techniques that could be used
        4. Potential extensions of the concepts

        Question: {question_text}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # TODO: Parse the response and structure the data
        return {
            "concepts": [],
            "prerequisites": [],
            "techniques": [],
            "extensions": []
        }