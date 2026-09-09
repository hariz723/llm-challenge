import os
from typing import Optional
from langfuse import Langfuse
from .config import settings
from .logging import logger

_langfuse_instance: Optional[Langfuse] = None
_is_initialized: bool = False


def _configure_environment():
    """Sets standard Langfuse environment variables from application settings."""
    pub_key = settings.LANGFUSE_CLEAN_PUBLIC_KEY
    sec_key = settings.LANGFUSE_CLEAN_SECRET_KEY
    host_url = settings.LANGFUSE_HOST_URL

    if pub_key:
        os.environ["LANGFUSE_PUBLIC_KEY"] = pub_key
    if sec_key:
        os.environ["LANGFUSE_SECRET_KEY"] = sec_key
    if host_url:
        os.environ["LANGFUSE_BASE_URL"] = host_url
        os.environ["LANGFUSE_HOST"] = host_url

    if not settings.LANGFUSE_TRACING_ENABLED:
        os.environ["LANGFUSE_TRACING_ENABLED"] = "False"


def init_langfuse() -> Optional[Langfuse]:
    """Initializes and returns the singleton Langfuse client."""
    global _langfuse_instance, _is_initialized
    if _is_initialized:
        return _langfuse_instance

    _is_initialized = True
    _configure_environment()

    pub_key = settings.LANGFUSE_CLEAN_PUBLIC_KEY
    sec_key = settings.LANGFUSE_CLEAN_SECRET_KEY
    host_url = settings.LANGFUSE_HOST_URL

    if not pub_key or not sec_key:
        logger.info("Langfuse credentials not configured; LLM tracing is disabled.")
        return None

    try:
        _langfuse_instance = Langfuse(
            public_key=pub_key,
            secret_key=sec_key,
            host=host_url,
        )
        logger.info("Langfuse observability client initialized successfully.")
        return _langfuse_instance
    except Exception as e:
        logger.warning(f"Failed to initialize Langfuse client: {e}")
        return None


def get_langfuse() -> Optional[Langfuse]:
    """Gets the active Langfuse client instance or initializes it if not ready."""
    global _langfuse_instance, _is_initialized
    if not _is_initialized:
        return init_langfuse()
    return _langfuse_instance


def is_langfuse_enabled() -> bool:
    """Returns True if Langfuse is configured and enabled."""
    return bool(
        settings.LANGFUSE_TRACING_ENABLED
        and settings.LANGFUSE_CLEAN_PUBLIC_KEY
        and settings.LANGFUSE_CLEAN_SECRET_KEY
    )


def flush_langfuse():
    """Flushes queued events to Langfuse backend."""
    client = get_langfuse()
    if client:
        try:
            client.flush()
        except Exception as e:
            logger.warning(f"Error flushing Langfuse events: {e}")


def shutdown_langfuse():
    """Flushes and shuts down the Langfuse client."""
    client = get_langfuse()
    if client:
        try:
            client.flush()
            client.shutdown()
            logger.info("Langfuse client cleanly shutdown.")
        except Exception as e:
            logger.warning(f"Error during Langfuse shutdown: {e}")
