from constants import BANNED_CHARACTERS


async def check_if_banned_characters(message: str) -> bool:
    """Checks input against list of disallowed character combinations

    Returns true if message contains bad input
    false if OK"""
    for value in BANNED_CHARACTERS:
        if value in message.lower():
            return True
    return False
