from config import BANNED_CHARACTERS
# Input: str
# Output: Boolean
async def check_if_banned_characters(message):
    for value in BANNED_CHARACTERS:
        if value in message:
            return True
    return False