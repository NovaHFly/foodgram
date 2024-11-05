import re

URL_REGEX = re.compile(r'(https?:\/\/[\w\d\-_.]+)')


def extract_host_with_schema(url: str) -> str:
    """Extract schema and hostname from url."""
    return URL_REGEX.match(url)[0]
