from abc import ABC, abstractmethod
from typing import Iterator

from anthropic import Anthropic
from ollama import Client

from app.config.settings import Settings


class LLMStrategy(ABC):
    @abstractmethod
    def execute(self, prompt: str) -> Iterator[str]:
        pass


class LLMStrategyFactory:
    @staticmethod
    def get_strategy() -> LLMStrategy:
        llm_type = Settings().LLM_PROVIDER

        if llm_type.lower() == 'anthropic':
            return ClaudeStrategy()
        elif llm_type.lower() == 'ollama':
            return OllamaStrategy()
        else:
            raise ValueError(f'Unsupported LLM type: {llm_type}')


class ClaudeStrategy(LLMStrategy):
    def __init__(self) -> None:
        self.api_key = Settings().ANTHROPIC_API_KEY
        self.model = Settings().ANTHROPIC_MODEL
        self.system_prompt = Settings().LLM_SYSTEM_PROMPT

    def execute(self, prompt: str) -> Iterator[str]:
        client = Anthropic(api_key=self.api_key)

        response = client.messages.create(
            model=self.model,
            messages=[
                {'role': 'assistant', 'content': self.system_prompt},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=1000,
            stream=True,
        )

        for chunk in response:
            if chunk.type == 'content_block_delta':
                yield chunk.delta.text  # type: ignore


class OllamaStrategy(LLMStrategy):
    def __init__(self) -> None:
        self.api_url = Settings().OLLAMA_API_URL
        self.model = Settings().OLLAMA_MODEL
        self.timeout = Settings().OLLAMA_TIMEOUT

    def execute(self, prompt: str) -> Iterator[str]:
        client = Client(host=self.api_url)
        try:
            messages = [
                {'role': 'system', 'content': Settings().LLM_SYSTEM_PROMPT},
                {'role': 'user', 'content': prompt},
            ]
            response = client.chat(
                model=self.model, messages=messages, stream=True
            )
            for chunk in response:
                yield (
                    chunk['message']['content']
                    if 'message' in chunk
                    else chunk.get('content', '')
                )
        except Exception as e:
            yield f'Erro ao conectar com Ollama: {str(e)}'


class LLMService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)

        return cls._instance

    @staticmethod
    def execute(prompt: str) -> Iterator[str]:
        strategy = LLMStrategyFactory.get_strategy()

        return strategy.execute(prompt)
