from config import BANNED_CHARACTERS


async def check_if_banned_characters(message: str) -> bool:
    """Checks input against list of disallowed character combinations

    Returns true if input contains bad input
    false if OK"""
    for value in BANNED_CHARACTERS:
        if value in message:
            return True
    return False
