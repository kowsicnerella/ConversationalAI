"""
LangChain LLM Configuration Manager
Pluggable LLM and embedding providers loaded from llm_providers.yaml.
Supports automatic fallback chains (e.g., vLLM -> Gemini -> OpenAI).

Replaces: app/services/llm_config.py (for chat module only)
"""

import os
import re
import logging
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from langchain_core.language_models import BaseChatModel
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)

# Load .env from project root
_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)


class LangChainConfig:
    """
    Manages LangChain LLM and Embedding instances from YAML config.
    Supports fallback chains: providers are tried in priority order.

    Usage:
        LangChainConfig.initialize()  # Call once in create_app()
        llm = LangChainConfig.get_llm_with_fallback()
        embeddings = LangChainConfig.get_embeddings()
    """

    _llm_instances: Dict[str, BaseChatModel] = {}
    _embedding_instances: Dict[str, Embeddings] = {}
    _llm_priority: List[str] = []
    _embedding_priority: List[str] = []
    _config: Dict[str, Any] = {}
    _initialized: bool = False

    @classmethod
    def initialize(cls, config_path: str = None) -> None:
        """
        Load YAML config, resolve env vars, instantiate all providers.
        Called once during Flask app factory.

        Args:
            config_path: Path to llm_providers.yaml (defaults to project root)
        """
        if cls._initialized:
            return

        if not config_path:
            config_path = str(Path(__file__).resolve().parents[2] / "llm_providers.yaml")

        try:
            with open(config_path, "r") as f:
                cls._config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            cls._config = {}
            cls._initialized = True
            return
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML config: {e}")
            cls._config = {}
            cls._initialized = True
            return

        # Initialize LLM providers
        llm_configs = cls._config.get("llm_providers", {})
        providers_with_priority = []
        for name, provider_cfg in llm_configs.items():
            resolved_cfg = cls._resolve_config(provider_cfg)
            priority = resolved_cfg.get("priority", 99)
            providers_with_priority.append((priority, name, resolved_cfg))

        providers_with_priority.sort(key=lambda x: x[0])

        for priority, name, resolved_cfg in providers_with_priority:
            try:
                llm = cls._create_llm(resolved_cfg)
                if llm:
                    cls._llm_instances[name] = llm
                    cls._llm_priority.append(name)
                    logger.info(f"LLM provider '{name}' initialized (priority {priority})")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM provider '{name}': {e}")

        # Initialize embedding providers
        emb_configs = cls._config.get("embedding_providers", {})
        emb_with_priority = []
        for name, provider_cfg in emb_configs.items():
            resolved_cfg = cls._resolve_config(provider_cfg)
            priority = resolved_cfg.get("priority", 99)
            emb_with_priority.append((priority, name, resolved_cfg))

        emb_with_priority.sort(key=lambda x: x[0])

        for priority, name, resolved_cfg in emb_with_priority:
            try:
                emb = cls._create_embeddings(resolved_cfg)
                if emb:
                    cls._embedding_instances[name] = emb
                    cls._embedding_priority.append(name)
                    logger.info(f"Embedding provider '{name}' initialized (priority {priority})")
            except Exception as e:
                logger.warning(f"Failed to initialize embedding provider '{name}': {e}")

        cls._initialized = True
        logger.info(
            f"LangChainConfig initialized: {len(cls._llm_instances)} LLM(s), "
            f"{len(cls._embedding_instances)} embedding(s)"
        )

    @classmethod
    def get_llm(cls, provider_name: str = None) -> BaseChatModel:
        """
        Get an LLM instance by name, or the highest-priority available one.

        Args:
            provider_name: Optional specific provider name (e.g., 'vllm_primary')

        Returns:
            BaseChatModel instance

        Raises:
            RuntimeError: If no providers are available
        """
        cls._ensure_initialized()

        if provider_name:
            if provider_name in cls._llm_instances:
                return cls._llm_instances[provider_name]
            raise RuntimeError(f"LLM provider '{provider_name}' not found")

        if cls._llm_priority:
            return cls._llm_instances[cls._llm_priority[0]]

        raise RuntimeError("No LLM providers available. Check llm_providers.yaml and .env")

    @classmethod
    def get_llm_with_fallback(cls) -> BaseChatModel:
        """
        Returns an LLM with fallback chain configured.
        Tries each provider in priority order. On failure, falls to next.

        Uses LangChain's with_fallbacks() for automatic failover.

        Returns:
            BaseChatModel with fallback chain
        """
        cls._ensure_initialized()

        if not cls._llm_priority:
            raise RuntimeError("No LLM providers available. Check llm_providers.yaml and .env")

        primary = cls._llm_instances[cls._llm_priority[0]]

        if len(cls._llm_priority) <= 1:
            return primary

        fallbacks = [cls._llm_instances[name] for name in cls._llm_priority[1:]]
        return primary.with_fallbacks(fallbacks)

    @classmethod
    def get_embeddings(cls, provider_name: str = None) -> Embeddings:
        """
        Get an Embeddings instance by name, or highest-priority available.

        Returns:
            Embeddings instance
        """
        cls._ensure_initialized()

        if provider_name:
            if provider_name in cls._embedding_instances:
                return cls._embedding_instances[provider_name]
            raise RuntimeError(f"Embedding provider '{provider_name}' not found")

        if cls._embedding_priority:
            return cls._embedding_instances[cls._embedding_priority[0]]

        raise RuntimeError(
            "No embedding providers available. Check llm_providers.yaml and .env"
        )

    @classmethod
    def get_weaviate_config(cls) -> Dict[str, str]:
        """
        Returns Weaviate connection details from config.

        Returns:
            dict with cluster_url, api_key, collection_name, text_key
        """
        cls._ensure_initialized()

        weaviate_cfg = cls._config.get("weaviate", {})
        return {
            "cluster_url": cls._resolve_env_var(
                weaviate_cfg.get("cluster_url", "")
            ),
            "api_key": cls._resolve_env_var(
                weaviate_cfg.get("api_key", "")
            ),
            "collection_name": weaviate_cfg.get("collection_name", "convai_langchain"),
            "text_key": weaviate_cfg.get("text_key", "content"),
        }

    @classmethod
    def get_available_providers(cls) -> Dict[str, List[str]]:
        """List all available (successfully initialized) providers."""
        cls._ensure_initialized()
        return {
            "llm_providers": list(cls._llm_instances.keys()),
            "embedding_providers": list(cls._embedding_instances.keys()),
            "llm_priority_order": cls._llm_priority,
            "embedding_priority_order": cls._embedding_priority,
        }

    # ─── Private Helpers ───

    @classmethod
    def _ensure_initialized(cls):
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def _resolve_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve all ${ENV_VAR} patterns in a config dict."""
        resolved = {}
        for key, value in config.items():
            if isinstance(value, str):
                resolved[key] = cls._resolve_env_var(value)
            elif isinstance(value, dict):
                resolved[key] = cls._resolve_config(value)
            else:
                resolved[key] = value
        return resolved

    @staticmethod
    def _resolve_env_var(value: str) -> str:
        """Replace ${VAR_NAME} patterns with os.getenv(VAR_NAME)."""
        if not isinstance(value, str):
            return value

        def _replace(match):
            var_name = match.group(1)
            env_val = os.getenv(var_name, "")
            # Strip surrounding quotes from .env values
            if env_val and env_val.startswith('"') and env_val.endswith('"'):
                env_val = env_val[1:-1]
            return env_val

        return re.sub(r"\$\{(\w+)\}", _replace, value)

    @staticmethod
    def _create_llm(config: Dict[str, Any]) -> Optional[BaseChatModel]:
        """
        Factory method: create an LLM from config dict.

        Supported types:
          - 'openai_compatible' -> ChatOpenAI(base_url=...)
          - 'openai'            -> ChatOpenAI
          - 'google_genai'      -> ChatGoogleGenerativeAI
        """
        provider_type = config.get("type", "")
        model = config.get("model", "")
        api_key = config.get("api_key", "not-needed")
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 2000)
        timeout = config.get("timeout", 120)

        if not model:
            return None

        if provider_type in ("openai_compatible", "openai"):
            from langchain_openai import ChatOpenAI

            kwargs = {
                "model": model,
                "api_key": api_key,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "request_timeout": timeout,
            }

            if provider_type == "openai_compatible":
                base_url = config.get("base_url", "")
                if not base_url or "None" in base_url:
                    logger.warning(
                        f"Skipping openai_compatible provider: base_url not configured"
                    )
                    return None
                # ChatOpenAI appends /chat/completions internally,
                # so strip it if the user provided the full endpoint URL.
                base_url = base_url.rstrip("/")
                if base_url.endswith("/chat/completions"):
                    base_url = base_url[: -len("/chat/completions")]
                kwargs["base_url"] = base_url

            return ChatOpenAI(**kwargs)

        elif provider_type == "google_genai":
            from langchain_google_genai import ChatGoogleGenerativeAI

            if not api_key or api_key == "not-needed":
                return None

            return ChatGoogleGenerativeAI(
                model=model,
                google_api_key=api_key,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

        else:
            logger.warning(f"Unknown LLM provider type: {provider_type}")
            return None

    @classmethod
    def get_embeddings_with_fallback(cls) -> Embeddings:
        """
        Returns the highest-priority embedding provider available.
        Tries providers in priority order; skips any that failed to initialize.

        vLLM (priority 1) -> Gemini (priority 2) -> ...

        Returns:
            Embeddings instance from the first available provider

        Raises:
            RuntimeError: If no embedding providers are available
        """
        cls._ensure_initialized()

        if not cls._embedding_priority:
            raise RuntimeError(
                "No embedding providers available. Check llm_providers.yaml and .env"
            )

        # Return the highest-priority successfully initialized provider.
        # Providers that failed during initialize() are never added to
        # _embedding_instances, so the first entry is the best available.
        return cls._embedding_instances[cls._embedding_priority[0]]

    @staticmethod
    def _create_embeddings(config: Dict[str, Any]) -> Optional[Embeddings]:
        """
        Factory method: create Embeddings from config dict.

        Supported types:
          - 'openai_compatible' -> OpenAIEmbeddings(base_url=...) for vLLM/Ollama
          - 'openai'            -> OpenAIEmbeddings
          - 'google_genai'      -> GoogleGenerativeAIEmbeddings
          - 'huggingface'       -> HuggingFaceEmbeddings
        """
        provider_type = config.get("type", "")
        model = config.get("model", "")
        api_key = config.get("api_key", "")

        if not model:
            return None

        if provider_type in ("openai_compatible", "openai"):
            from langchain_openai import OpenAIEmbeddings

            kwargs: Dict[str, Any] = {
                "model": model,
                "api_key": api_key or "not-needed",
            }

            if provider_type == "openai_compatible":
                base_url = config.get("base_url", "")
                if not base_url or "None" in base_url:
                    logger.warning(
                        "Skipping openai_compatible embedding provider: "
                        "base_url not configured (check VLLM_ENDPOINT in .env)"
                    )
                    return None
                # OpenAIEmbeddings appends /embeddings internally,
                # so strip it if the user provided the full endpoint URL.
                base_url = base_url.rstrip("/")
                if base_url.endswith("/embeddings"):
                    base_url = base_url[: -len("/embeddings")]
                kwargs["base_url"] = base_url

            return OpenAIEmbeddings(**kwargs)

        elif provider_type == "google_genai":
            from langchain_google_genai import GoogleGenerativeAIEmbeddings

            if not api_key:
                return None

            return GoogleGenerativeAIEmbeddings(
                model=model,
                google_api_key=api_key,
            )

        elif provider_type == "huggingface":
            from langchain_huggingface import HuggingFaceEmbeddings

            return HuggingFaceEmbeddings(model_name=model)

        else:
            logger.warning(f"Unknown embedding provider type: {provider_type}")
            return None
