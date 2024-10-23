import random
import string

TOKEN_SYMBOLS = string.ascii_letters + string.digits


def generate_short_url(token_length: int = 6):
    return ''.join(random.choices(TOKEN_SYMBOLS, k=token_length))
