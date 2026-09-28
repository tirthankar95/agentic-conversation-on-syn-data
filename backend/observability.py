"""Optional Langfuse helpers for tracing the app when credentials are configured."""

from contextlib import contextmanager
import os


def _configured() -> bool:
    enabled = os.getenv("LANGFUSE_TRACING_ENABLED", "true").lower()
    return (
        enabled not in {"0", "false", "no", "off"}
        and bool(os.getenv("LANGFUSE_PUBLIC_KEY"))
        and bool(os.getenv("LANGFUSE_SECRET_KEY"))
    )


def get_langfuse_callback():
    """Return a LangChain callback handler when tracing is configured."""
    if not _configured():
        return None
    from langfuse.langchain import CallbackHandler
    return CallbackHandler()


@contextmanager
def observation(name: str, *, as_type: str = "span", input=None, metadata=None):
    """Create an active Langfuse observation, or a no-op when tracing is disabled."""
    if not _configured():
        yield None
        return
    from langfuse import get_client
    client = get_client()
    options = {"as_type": as_type, "name": name}
    if input is not None:
        options["input"] = input
    if metadata:
        options["metadata"] = metadata
    with client.start_as_current_observation(**options) as current:
        yield current
