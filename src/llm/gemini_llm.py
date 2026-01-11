"""Gemini LLM wrapper for Google's Generative AI API."""

from typing import List, Dict, Optional
import google.generativeai as genai

from .config import LLMConfig


class GeminiLLM:
    """
    A class to interact with Google's Gemini model through their API.
    """

    def __init__(self, api_key: str):
        """Initialize GeminiLLM with API key.

        Args:
            api_key (str): Google API authentication key
        """
        self.config = LLMConfig()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.config.model)

    def _convert_messages_to_prompt(self, messages: List[Dict]) -> str:
        """Convert messages to a single prompt string.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"{content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(f"User: {content}")

        return "\n\n".join(prompt_parts)

    async def agenerate(
        self,
        messages: List[Dict],
        temperature: Optional[float] = None
    ) -> str:
        """Generate text using Gemini model.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0, default from config)

        Returns:
            str: Generated text response
        """
        prompt = self._convert_messages_to_prompt(messages)

        generation_config = genai.GenerationConfig(
            temperature=temperature or self.config.default_temp,
            max_output_tokens=self.config.max_tokens
        )

        response = await self.model.generate_content_async(
            prompt,
            generation_config=generation_config
        )

        return response.text
