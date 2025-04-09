from data.config import AI_MODEL_TYPE
from services.ai.gemini_ai_service import GeminiAIService


def create_ai_service():

    if AI_MODEL_TYPE == "gemini":
        return GeminiAIService()

    # elif AI_MODEL_TYPE == "openai":
    #     return OpenAIService()
    # elif AI_MODEL_TYPE == "claude":
    #     return ClaudeService()

    # By DeFault Gemini
    return GeminiAIService()