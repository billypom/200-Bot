import random
import string


async def generate_random_name() -> str:
    """Returns a random string of length 9"""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=9))
