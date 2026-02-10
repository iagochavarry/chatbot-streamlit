"""OpenAI streaming wrapper."""

from collections.abc import Generator

from openai import OpenAI


def stream_completion(
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float = 0.4,
    max_tokens: int = 1024,
) -> Generator[str, None, None]:
    """Yield content deltas from an OpenAI streaming chat completion.

    Raises on connection/auth errors so the caller can handle them.
    """
    client = OpenAI(api_key=api_key)
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    for event in stream:
        if event and event.choices and event.choices[0].delta:
            delta = event.choices[0].delta.content
            if delta:
                yield delta
