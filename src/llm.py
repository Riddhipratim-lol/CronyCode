import os
import logging
from typing import Type, TypeVar
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cronycode.llm")

# Try to find and load .env from standard workspace root
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(workspace_root, ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

T = TypeVar("T", bound=BaseModel)

class ModelService:
    """Service layer that executes tasks with a primary model and fails back

    to a secondary model if technical failures occur.
    """
    def __init__(self, primary_model: str, fallback_model: str):
        self.primary_model_name = primary_model
        self.fallback_model_name = fallback_model

    def get_structured_output(
        self, 
        schema: Type[T], 
        system_prompt: str, 
        user_prompt: str
    ) -> T:
        """Invokes Gemini with the given system and user prompts, enforcing a Pydantic schema

        structured output, with automatic fallback logic.
        """
        # Ensure API key is set in current environment
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment or .env file.")

        messages = [
            ("system", system_prompt),
            ("user", user_prompt)
        ]

        try:
            logger.info(f"Invoking primary model: {self.primary_model_name}")
            # Initialize with low temperature to stabilize reasoning and structured generation
            llm = ChatGoogleGenerativeAI(
                model=self.primary_model_name,
                temperature=0.1,
                google_api_key=api_key
            )
            structured_llm = llm.with_structured_output(schema)
            response = structured_llm.invoke(messages)
            logger.info(f"Successfully received response from primary model: {self.primary_model_name}")
            if not isinstance(response, schema):
                raise TypeError(f"Expected structured output of type {schema.__name__}, but got {type(response).__name__}")
            return response

        except Exception as e:
            logger.warning(
                f"Primary model '{self.primary_model_name}' failed with exception: {e}. "
                f"Attempting failover to secondary model: '{self.fallback_model_name}'."
            )
            
            try:
                # Attempt to invoke fallback model
                llm = ChatGoogleGenerativeAI(
                    model=self.fallback_model_name,
                    temperature=0.1,
                    google_api_key=api_key
                )
                structured_llm = llm.with_structured_output(schema)
                response = structured_llm.invoke(messages)
                logger.info(f"Successfully received response from fallback model: {self.fallback_model_name}")
                if not isinstance(response, schema):
                    raise TypeError(f"Expected structured output of type {schema.__name__}, but got {type(response).__name__}")
                return response
            except Exception as fallback_err:
                logger.error(
                    f"Fallback model '{self.fallback_model_name}' also failed. "
                    f"Final exception: {fallback_err}"
                )
                raise fallback_err

# Instantiate standard services defined by the system requirements
# Flash-lite-first (with Flash fallback) for lightweight tasks (Input Classification)
flash_service = ModelService(primary_model="gemini-3.1-flash-lite", fallback_model="gemini-3.5-flash")

# Flash-first (with Flash-lite fallback) for heavy cognitive/reasoning tasks (Understanding, Planning, Architecture)
pro_service = ModelService(primary_model="gemini-3.5-flash", fallback_model="gemini-3.1-flash-lite")
