import os

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

# Load environment variables from a .env file
load_dotenv()


def get_chat_model() -> BaseChatModel:
    """
    Factory function to get an instance of the chat model.
    This approach allows for easy swapping of models in the future.
    """
    # Ensure the API key is set
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable not set.")

    # Using the standard ChatOpenAI class with OpenRouter's configuration
    # This is the recommended approach for OpenAI-compatible APIs.
    model = ChatOpenAI(
        model="deepseek/deepseek-chat:free",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7,
        # max_tokens=2048, # Increased token limit for complex JSON output
    )

    # To switch to a different model (e.g., local one with Ollama):
    # model = ChatOpenAI(
    #     model="llama3",
    #     api_key="ollama", # The key can be anything for Ollama
    #     base_url="http://localhost:11434/v1",
    #     temperature=0.7
    # )

    return model
