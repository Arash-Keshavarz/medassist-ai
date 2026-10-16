"""The minimal provider-independent text generation contract."""

from typing import Protocol


class LLMProvider(Protocol):
    """Structural interface for future adapters and deterministic test doubles.

    Adapters will receive model, credentials, and timeout at construction time.
    Implementations must propagate failures rather than return fabricated answers.
    This contract alone does not enforce grounding or validate citations.
    """

    async def generate(self, *, prompt: str, max_output_tokens: int) -> str:
        """Generate text asynchronously within the requested output token budget."""
        ...
