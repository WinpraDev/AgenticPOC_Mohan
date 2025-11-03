"""
LLM Client for Meta-Agent.
Connects to LM Studio with NO FALLBACKS.
System fails explicitly if LM Studio is not available.
"""

from typing import Dict, Any, Optional, List
from loguru import logger
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import settings


class LLMClient:
    """
    Client for LM Studio LLM API.
    
    STRICT MODE: NO FALLBACKS
    - If LM Studio not available → Raise ConnectionError
    - If API call fails → Raise RuntimeError
    - All errors propagate to caller
    """
    
    def __init__(self):
        """
        Initialize LLM client and verify connection.
        
        Raises:
            ConnectionError: If LM Studio is not accessible
            RuntimeError: If model not loaded or configuration invalid
        """
        self.base_url = settings.llm_base_url
        self.model_name = settings.llm_model_name
        self.api_key = settings.llm_api_key
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.context_length = settings.llm_context_length
        
        self.available = False
        self.llm: Optional[ChatOpenAI] = None
        
        logger.debug(f"Initializing LLM client: {self.model_name}")
        logger.debug(f"LM Studio URL: {self.base_url}")
        
        self._initialize()
    
    def _initialize(self) -> None:
        """
        Initialize connection to LM Studio.
        
        Raises:
            ConnectionError: If cannot connect to LM Studio
            RuntimeError: If model not loaded
        """
        # Step 1: Verify LM Studio server is accessible
        try:
            response = httpx.get(
                f"{self.base_url}/models",
                timeout=10.0
            )
            response.raise_for_status()
            models = response.json()
            
            logger.debug(f"✓ LM Studio server accessible")
            logger.debug(f"Available models: {models}")
            
            # Verify our model is loaded
            if models.get("data"):
                loaded_models = [m.get("id") for m in models["data"]]
                if self.model_name not in loaded_models:
                    logger.error(f"Model '{self.model_name}' not loaded in LM Studio")
                    logger.error(f"Loaded models: {loaded_models}")
                    raise RuntimeError(
                        f"Model '{self.model_name}' is not loaded in LM Studio. "
                        f"Please load the model and try again. "
                        f"Loaded models: {loaded_models}"
                    )
            
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to LM Studio at {self.base_url}")
            raise ConnectionError(
                f"Cannot connect to LM Studio at {self.base_url}. "
                f"Please ensure:\n"
                f"1. LM Studio is running\n"
                f"2. Model '{self.model_name}' is loaded\n"
                f"3. Local server is started (port 1234)\n"
                f"4. Server URL is correct: {self.base_url}\n"
                f"\nError: {e}"
            ) from e
        except httpx.HTTPError as e:
            logger.error(f"HTTP error from LM Studio: {e}")
            raise ConnectionError(
                f"LM Studio returned an error: {e}. "
                f"Please check LM Studio is properly configured."
            ) from e
        
        # Step 2: Initialize LangChain client
        try:
            self.llm = ChatOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=180.0,  # 3 minutes - sufficient for 7B model on M4
                max_retries=0  # No retries, fail fast
            )
            
            # Test with simple ping
            test_response = self.llm.invoke([
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Respond with 'OK'")
            ])
            
            if test_response.content:
                self.available = True
                logger.debug(f"✓ LLM client initialized successfully")
                logger.debug(f"  Model: {self.model_name}")
                logger.debug(f"  Temperature: {self.temperature}")
                logger.debug(f"  Max Tokens: {self.max_tokens}")
                logger.debug(f"  Context Length: {self.context_length}")
            else:
                raise RuntimeError("LLM returned empty response")
                
        except Exception as e:
            logger.error(f"Failed to initialize LangChain client: {e}")
            raise RuntimeError(
                f"Failed to initialize LLM client: {e}. "
                f"Please verify LM Studio is running and model is loaded."
            ) from e
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text from LLM.
        
        Args:
            system_prompt: System instruction for the LLM
            user_prompt: User's request/query
            temperature: Override default temperature (optional)
            max_tokens: Override default max tokens (optional)
        
        Returns:
            Generated text response
        
        Raises:
            RuntimeError: If LLM is not available
            RuntimeError: If generation fails
        """
        if not self.available:
            raise RuntimeError(
                "LLM is not available. Cannot generate without LM Studio. "
                "Please ensure LM Studio is running with model loaded."
            )
        
        try:
            # Use override values if provided
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens if max_tokens is not None else self.max_tokens
            
            # Update LLM config if overrides provided
            if temperature is not None or max_tokens is not None:
                self.llm.temperature = temp
                self.llm.max_tokens = tokens
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            logger.debug(f"Generating with temperature={temp}, max_tokens={tokens}")
            logger.debug(f"System prompt length: {len(system_prompt)} chars")
            logger.debug(f"User prompt length: {len(user_prompt)} chars")
            
            response = self.llm.invoke(messages)
            
            if not response.content:
                raise RuntimeError("LLM returned empty response")
            
            logger.debug(f"Response length: {len(response.content)} chars")
            
            return response.content
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise RuntimeError(
                f"LLM generation failed: {e}. "
                f"This may indicate LM Studio crashed or model unloaded."
            ) from e
    
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON response from LLM.
        
        Args:
            system_prompt: System instruction (should request JSON output)
            user_prompt: User's request/query
            temperature: Override default temperature (optional)
            max_tokens: Override default max tokens (optional)
        
        Returns:
            Parsed JSON object
        
        Raises:
            RuntimeError: If LLM is not available or generation fails
            ValueError: If response is not valid JSON
        """
        import json
        
        # Ensure system prompt requests JSON
        if "json" not in system_prompt.lower():
            system_prompt += "\n\nIMPORTANT: Output MUST be valid JSON only, no other text."
        
        response_text = self.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Try to extract JSON if wrapped in markdown code blocks
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove ```
        response_text = response_text.strip()
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            raise ValueError(
                f"LLM did not return valid JSON: {e}. "
                f"Response started with: {response_text[:100]}..."
            ) from e
    
    def verify_health(self) -> bool:
        """
        Verify LLM is healthy and responsive.
        
        Returns:
            True if LLM is healthy
        
        Raises:
            RuntimeError: If health check fails
        """
        if not self.available:
            raise RuntimeError("LLM is not available")
        
        try:
            response = self.generate(
                system_prompt="You are a health check assistant.",
                user_prompt="Respond with 'HEALTHY'",
                max_tokens=10
            )
            
            if "HEALTHY" in response.upper():
                logger.debug("✓ LLM health check passed")
                return True
            else:
                logger.warning(f"Unexpected health check response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise RuntimeError(f"LLM health check failed: {e}") from e

