from groq import Groq
from app.config.config import settings
from typing import Tuple

class GroqService:    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.temperature = settings.GROQ_TEMPERATURE
        self.max_tokens = settings.GROQ_MAX_TOKENS
    
    def classify_license(self, license_name: str) -> Tuple[str, str]:
        """
        Classify a software license using Groq LLM
        
        Args:
            license_name: Name of the software license
            
        Returns:
            Tuple of (category, explanation)
            
        Raises:
            Exception: If classification fails
        """
        
        prompt = self._build_classification_prompt(license_name)
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            response_text = response.choices[0].message.content.strip()
            category, explanation = self._parse_response(response_text)
            
            explanation = self._truncate_explanation(explanation)
            
            return category, explanation
            
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        return (
            "You are an expert software categorization system. "
            "Classify software licenses into exact categories. "
            "Provide explanations in EXACTLY 140-145 characters to allow for safety margin. "
            "Be concise and precise. Focus on the primary function of the software."
        )
    
    def _build_classification_prompt(self, license_name: str) -> str:
        categories = ", ".join(settings.VALID_CATEGORIES)
        
        return f"""Classify this software license into ONE category from: {categories}

Software License: {license_name}

Rules:
1. Choose the MOST appropriate single category
2. Explanation MUST be 140-145 characters (strictly enforced)
3. Focus on primary software function

Respond EXACTLY in this format:
Category: [category name]
Explanation: [your 140-145 character explanation]

Do not include any other text."""
    
    def _parse_response(self, response_text: str) -> Tuple[str, str]:
        """
        Parse LLM response to extract category and explanation
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Tuple of (category, explanation)
        """
        category = ""
        explanation = ""
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith("Category:"):
                category = line.replace("Category:", "").strip()
            elif line.startswith("Explanation:"):
                explanation = line.replace("Explanation:", "").strip()
        
        if category not in settings.VALID_CATEGORIES:
            for valid_cat in settings.VALID_CATEGORIES:
                if valid_cat.lower() in response_text.lower():
                    category = valid_cat
                    break
            
            if category not in settings.VALID_CATEGORIES:
                category = "Development"
        
        if not explanation:
            explanation = f"Software classified as {category} based on primary functionality."
        
        return category, explanation
    
    def _truncate_explanation(self, explanation: str) -> str:
        """
        Strictly truncate explanation to MAX_EXPLANATION_LENGTH characters
        
        Args:
            explanation: Original explanation
            
        Returns:
            Truncated explanation under 150 characters
        """
        max_len = settings.MAX_EXPLANATION_LENGTH
        
        if len(explanation) <= max_len:
            return explanation
        
        return explanation[:max_len - 3] + "..."

groq_service = GroqService()