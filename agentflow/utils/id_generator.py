"""ID generation utilities."""

import uuid


def generate_id() -> str:
    """Generate a unique ID.

    Returns:
        A unique UUID string
    """
    return str(uuid.uuid4())
