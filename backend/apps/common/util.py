import random

from .const import TOKEN_SYMBOLS


def generate_token(token_length: int = 6):
    return ''.join(random.choices(TOKEN_SYMBOLS, k=token_length))