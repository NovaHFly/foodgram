import random

from .const import TOKEN_SYMBOLS


def generate_token(token_length: int = 6) -> str:
    """Generate random string of specified length.

    Args:
        token_length (int): Token length.

    Returns:
        str: Token.
    """
    return ''.join(random.choices(TOKEN_SYMBOLS, k=token_length))
