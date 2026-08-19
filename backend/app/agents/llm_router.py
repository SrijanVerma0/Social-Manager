"""
1. Implements multi-tier LLM routing via OpenRouter to optimize cost, latency, and reasoning capability.
2. Routes extraction and scraping tasks to fast/economic models (DeepSeek-V3, Claude 3.5 Haiku).
3. Routes high-stakes architectural analysis and senior tone crafting to flagship models (Claude 3.5 Sonnet, GPT-4o).
"""

from enum import Enum
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel
import litellm

from backend.app.core.config import settings


class ModelTier(str, Enum):
    """
    Tier-based model categorization for cost & latency optimization.
    """
    FAST = "fast"            # Cheap & fast for extraction & scraping (DeepSeek-V3)
    REASONING = "reasoning"  # High reasoning for code & fact verification (DeepSeek-V3 / R1)
    WRITER = "writer"        # High nuance & tone for LinkedIn/Twitter/Video scripts (Gemini / GPT-4o)


class LLMRouter:
    """
    Unified async LLM dispatcher supporting OpenRouter multi-tier routing with automatic fallbacks.
    """
    def __init__(self):
        litellm.drop_params = True  # Drops unsupported provider params automatically

    def get_model_name(self, tier: ModelTier) -> str:
        """Returns the configured model string based on requested tier."""
        if tier == ModelTier.FAST:
            return settings.FAST_LLM_MODEL
        elif tier == ModelTier.REASONING:
            return settings.REASONING_LLM_MODEL
        elif tier == ModelTier.WRITER:
            return settings.WRITER_LLM_MODEL
        return settings.FAST_LLM_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tier: ModelTier = ModelTier.FAST,
        temperature: float = 0.7,
        max_tokens: int = 2500,
        response_model: Optional[Type[BaseModel]] = None,
    ) -> str:
        """
        Async completion caller with automatic fallback on rate limits.
        """
        model_name = self.get_model_name(tier)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        extra_headers = {
            "HTTP-Referer": "https://github.com/SrijanVerma0/Social-Manager",
            "X-Title": settings.PROJECT_NAME,
        }

        # Models to try (Primary -> Writer fallback -> Default)
        models_to_try = [model_name, settings.WRITER_LLM_MODEL, "openrouter/deepseek/deepseek-chat"]
        unique_models = list(dict.fromkeys(models_to_try))

        last_error = None
        for current_model in unique_models:
            try:
                if response_model:
                    response = await litellm.acompletion(
                        model=current_model,
                        messages=messages,
                        api_key=settings.OPENROUTER_API_KEY,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_format=response_model,
                        extra_headers=extra_headers,
                    )
                else:
                    response = await litellm.acompletion(
                        model=current_model,
                        messages=messages,
                        api_key=settings.OPENROUTER_API_KEY,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        extra_headers=extra_headers,
                    )

                return response.choices[0].message.content

            except Exception as e:
                last_error = e
                print(f"[LLMRouter Warning]: Model '{current_model}' had issue ({str(e)[:90]}...). Trying fallback...")
                continue

        raise RuntimeError(f"All model fallbacks failed for tier '{tier}': {str(last_error)}")


# Export a global singleton router
llm_router = LLMRouter()
